import multiprocessing
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from amem_repro.budget import BudgetStop, PhasePermit, ledger_summary
from amem_repro.config import stage_output_limits


def binding():
    return {'manifest_sha256':'a'*64,'config_sha256':'b'*64,'source_sha256':'c'*64,
            'preflight_sha256':'d'*64,'population':'smoke','condition':'full','repetition':0,
            'model':'deepseek-flash','endpoint':'https://api.deepseek.com/beta/chat/completions',
            'max_output_tokens_by_stage':stage_output_limits()}


def approval(phase='compatibility', cap='2', ident='phase-one', run='run-one'):
    b=binding()
    if phase=='pilot':b['population']='pilot'
    if phase=='baseline':b['population']='full'
    return {'approval_id':ident,'approved':True,'approved_by':'offline-test',
            'approved_at':'2026-11-01T00:00:00+00:00','phase':phase,'run_id':run,
            'binding':b,'limits':{'max_logical_calls':44,'max_attempts':132,'phase_usd':cap},
            'pricing':{'pricing_id':'peak-offline-fixture','input_per_million':'0.30',
                       'output_per_million':'1.20','max_context_tokens':1048576,'max_output_tokens':4000}}


def request():
    return {'model':'deepseek-flash','endpoint':'https://api.deepseek.com/beta/chat/completions',
            'max_tokens':1000,'temperature':0.7,'stream':False,'thinking':'disabled'}


def reserve_from_new_process(path, auth, outcomes):
    """A fresh process has no inherited permit or mutable balance."""
    try:
        permit=PhasePermit(auth,path,auth['binding'])
        permit.reserve_attempt(permit.start_logical('metadata'),request())
        outcomes.put('reserved')
    except BudgetStop:
        outcomes.put('stopped')


class BudgetTests(unittest.TestCase):
    def test_shared_decision_reserves_its_four_thousand_token_bound_and_settles_usage(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'ledger'
            permit=PhasePermit(approval(),path,binding())
            attempt=permit.reserve_attempt(permit.start_logical('shared_decision'),request()|{'max_tokens':4000})
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],319373)
            permit.settle(attempt,{'prompt_tokens':20,'completion_tokens':4000,'total_tokens':4020})
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],4806)
            self.assertEqual(permit.summary()['unknown_attempts'],0)

    def test_nondecision_requests_cannot_use_the_four_thousand_token_cap(self):
        for stage in ('metadata','query_keywords','answer'):
            with self.subTest(stage=stage),tempfile.TemporaryDirectory() as directory:
                permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
                with self.assertRaises(BudgetStop):
                    permit.reserve_attempt(permit.start_logical(stage),request()|{'max_tokens':4000})
                self.assertEqual(permit.summary()['physical_attempts'],0)
                self.assertTrue(permit.summary()['halted'])

    def test_usage_limit_follows_the_attempt_stage_not_the_global_pricing_bound(self):
        for stage,limit,reservation in (('shared_decision',4000,319373),
                                        ('metadata',1000,315773),
                                        ('query_keywords',1000,315773),
                                        ('answer',1000,315773)):
            with self.subTest(stage=stage),tempfile.TemporaryDirectory() as directory:
                permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
                attempt=permit.reserve_attempt(permit.start_logical(stage),request()|{'max_tokens':limit})
                # A later logical stage must not replace this attempt's usage bound.
                permit.start_logical('metadata' if stage=='shared_decision' else 'shared_decision')
                with self.assertRaises(BudgetStop):
                    permit.settle(attempt,{'prompt_tokens':20,'completion_tokens':limit+1})
                self.assertEqual(permit.summary()['charged_or_reserved_microusd'],reservation)
                self.assertEqual(permit.summary()['unknown_attempts'],1)
                self.assertTrue(permit.summary()['halted'])

    def test_shared_decision_retry_reservation_accounts_for_its_full_stage_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(cap='0.638746'),Path(directory)/'ledger',binding())
            logical=permit.start_logical('shared_decision')
            for _ in range(2):
                attempt=permit.reserve_attempt(logical,request()|{'max_tokens':4000})
                permit.settle(attempt,None)
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],638746)
            self.assertEqual(permit.summary()['unknown_attempts'],2)
            with self.assertRaises(BudgetStop):
                permit.reserve_attempt(logical,request()|{'max_tokens':4000})
            self.assertEqual(permit.summary()['physical_attempts'],2)

    def test_stage_output_approval_is_explicit_complete_and_strictly_integer(self):
        cases=[None,{}, {'metadata':1000},
               stage_output_limits()|{'unknown':1000},
               stage_output_limits()|{'shared_decision':1000},
               stage_output_limits()|{'shared_decision':4001},
               stage_output_limits()|{'shared_decision':4000.0},
               stage_output_limits()|{'metadata':4000},
               stage_output_limits()|{'metadata':True},
               stage_output_limits()|{'answer':1000.0}]
        for limits in cases:
            with self.subTest(limits=limits),tempfile.TemporaryDirectory() as directory:
                auth=approval()
                if limits is None:
                    del auth['binding']['max_output_tokens_by_stage']
                else:
                    auth['binding']['max_output_tokens_by_stage']=limits
                path=Path(directory)/'ledger'
                with self.assertRaises(BudgetStop):PhasePermit(auth,path,auth['binding'])
                self.assertFalse(path.exists())

    def test_reserve_before_transmission_then_settle_usage_without_double_charge(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'budget.sqlite3'
            permit=PhasePermit(approval(),path,binding())
            logical=permit.start_logical('metadata')
            token=permit.reserve_attempt(logical,request())
            self.assertEqual(ledger_summary(path)['charged_or_reserved_microusd'],315773)
            permit.settle(token,{'prompt_tokens':20,'completion_tokens':5})
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],12)
            self.assertEqual(permit.summary()['physical_attempts'],1)
            permit.settle(token,{'prompt_tokens':20,'completion_tokens':5})
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],12)

    def test_unknown_attempts_and_restart_retain_reservations(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'budget.sqlite3'
            auth=approval()
            permit=PhasePermit(auth,path,binding())
            first=permit.reserve_attempt(permit.start_logical('metadata'),request())
            permit.settle(first,None)
            permit.reserve_attempt(permit.start_logical('answer'),request())
            with self.assertRaises(BudgetStop):
                PhasePermit(auth,path,binding())
            self.assertEqual(ledger_summary(path)['charged_or_reserved_microusd'],631546)
            self.assertEqual(ledger_summary(path)['unknown_attempts'],2)

    def test_phase_cap_is_durable_and_does_not_transmit_an_extra_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'budget.sqlite3'
            permit=PhasePermit(approval(cap='0.5'),path,binding())
            logical=permit.start_logical('metadata')
            permit.reserve_attempt(logical,request())
            with self.assertRaises(BudgetStop):
                permit.reserve_attempt(logical,request())
            self.assertEqual(permit.summary()['physical_attempts'],1)
            self.assertTrue(permit.summary()['halted'])
            with self.assertRaises(BudgetStop):
                permit.start_logical('answer')

    def test_logical_and_physical_caps_count_attempts_separately(self):
        for limit,first_operation in [('max_logical_calls','logical'),('max_attempts','physical')]:
            with self.subTest(limit=limit),tempfile.TemporaryDirectory() as directory:
                auth=approval()
                auth['limits'][limit]=1
                if limit=='max_logical_calls':auth['limits']['max_attempts']=3
                permit=PhasePermit(auth,Path(directory)/'ledger',binding())
                logical=permit.start_logical('metadata')
                attempt=permit.reserve_attempt(logical,request())
                permit.settle(attempt,{'prompt_tokens':20,'completion_tokens':5})
                with self.assertRaises(BudgetStop):
                    if first_operation=='logical':permit.start_logical('metadata')
                    else:permit.reserve_attempt(logical,request())
                self.assertEqual(permit.summary()['physical_attempts'],1)

    def test_each_logical_call_has_at_most_three_transport_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
            logical=permit.start_logical('metadata')
            for _ in range(3):
                attempt=permit.reserve_attempt(logical,request())
                permit.settle(attempt,{'prompt_tokens':20,'completion_tokens':5})
            with self.assertRaises(BudgetStop):permit.reserve_attempt(logical,request())
            self.assertEqual(permit.summary()['physical_attempts'],3)

    def test_transport_retry_cannot_change_the_logical_request(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
            logical=permit.start_logical('metadata')
            first=request()|{'body_sha256':'a'*64}
            attempt=permit.reserve_attempt(logical,first)
            permit.settle(attempt,None)
            with self.assertRaises(BudgetStop):
                permit.reserve_attempt(logical,request()|{'body_sha256':'b'*64})
            self.assertEqual(permit.summary()['physical_attempts'],1)

    def test_untrusted_usage_never_releases_the_reservation(self):
        values=[{'prompt_tokens':True,'completion_tokens':5},
                {'prompt_tokens':-1,'completion_tokens':5},
                {'prompt_tokens':1048577,'completion_tokens':5},
                {'prompt_tokens':20,'completion_tokens':1001},
                {'prompt_tokens':20.0,'completion_tokens':5},
                {'prompt_tokens':float('nan'),'completion_tokens':5},
                {'prompt_tokens':20,'completion_tokens':float('inf')},
                {'prompt_tokens':20,'completion_tokens':5,'total_tokens':24},
                {'prompt_tokens':20,'completion_tokens':5,'total_tokens':True},
                {'prompt_tokens':20},42]
        for usage in values:
            with self.subTest(usage=usage),tempfile.TemporaryDirectory() as directory:
                permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
                attempt=permit.reserve_attempt(permit.start_logical('metadata'),request())
                with self.assertRaises(BudgetStop):permit.settle(attempt,usage)
                self.assertEqual(permit.summary()['charged_or_reserved_microusd'],315773)
                self.assertTrue(permit.summary()['halted'])

    def test_completion_after_stop_can_record_actual_incurred_usage(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
            attempt=permit.reserve_attempt(permit.start_logical('metadata'),request())
            permit.stop('orchestrator-stop')
            permit.settle(attempt,{'prompt_tokens':20,'completion_tokens':5})
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],12)
            self.assertEqual(permit.summary()['halted'],'orchestrator-stop')
            with self.assertRaises(BudgetStop):permit.start_logical('answer')

    def test_cache_details_are_subsets_and_never_discount_or_add_input_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
            attempt=permit.reserve_attempt(permit.start_logical('metadata'),request())
            permit.settle(attempt,{'prompt_tokens':20,'completion_tokens':5,'total_tokens':25,
                                  'prompt_cache_hit_tokens':15,'prompt_cache_miss_tokens':5,
                                  'prompt_tokens_details':{'cached_tokens':15}})
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],12)

    def test_inconsistent_cache_details_are_untrusted_usage(self):
        for details in ({'prompt_cache_hit_tokens':21},
                        {'prompt_cache_hit_tokens':15,'prompt_cache_miss_tokens':6},
                        {'prompt_tokens_details':{'cached_tokens':True}}):
            with self.subTest(details=details),tempfile.TemporaryDirectory() as directory:
                permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
                attempt=permit.reserve_attempt(permit.start_logical('metadata'),request())
                with self.assertRaises(BudgetStop):
                    permit.settle(attempt,{'prompt_tokens':20,'completion_tokens':5}|details)
                self.assertEqual(permit.summary()['charged_or_reserved_microusd'],315773)

    def test_conflicting_settlement_cannot_revise_incurred_cost(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
            attempt=permit.reserve_attempt(permit.start_logical('metadata'),request())
            permit.settle(attempt,{'prompt_tokens':20,'completion_tokens':5})
            with self.assertRaises(BudgetStop):
                permit.settle(attempt,{'prompt_tokens':0,'completion_tokens':0})
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],12)

    def test_changed_binding_permanently_stops_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
            changed=binding()|{'repetition':1}
            with self.assertRaises(BudgetStop):permit.check_binding(changed)
            self.assertEqual(permit.summary()['logical_calls'],0)
            self.assertTrue(permit.summary()['halted'])
            with self.assertRaises(BudgetStop):permit.check_binding(binding())

    def test_changed_internal_binding_cannot_change_the_approved_request(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
            permit.binding['endpoint']='https://example.invalid/chat/completions'
            with self.assertRaises(BudgetStop):permit.start_logical('metadata')
            self.assertTrue(permit.summary()['halted'])

    def test_concurrent_reservations_cannot_both_spend_remaining_phase_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            permit=PhasePermit(approval(cap='0.5'),Path(directory)/'ledger',binding())
            calls=[permit.start_logical('metadata') for _ in range(2)]
            def reserve(logical):
                try:return permit.reserve_attempt(logical,request())
                except BudgetStop:return 'stopped'
            with ThreadPoolExecutor(max_workers=2) as workers:
                outcomes=list(workers.map(reserve,calls))
            self.assertEqual(outcomes.count('stopped'),1)
            self.assertEqual(permit.summary()['physical_attempts'],1)
            self.assertEqual(permit.summary()['charged_or_reserved_microusd'],315773)

    def test_study_total_includes_old_unknown_attempts_and_reserves_eight_dollars(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'ledger'
            # Historical compatibility/pilot phases predate one-shot main-cell bindings.
            # Four valid USD10 phases retain their unknown maximum reservations.
            for index in range(4):
                first=approval('pilot','10',f'historical-{index}',f'historical-{index}')
                first['pricing']['input_per_million']='9'
                permit=PhasePermit(first,path,first['binding'])
                permit.reserve_attempt(permit.start_logical('metadata'),request())
            second=approval('pilot','10','phase-two','run-two')
            second['pricing']['input_per_million']='9'
            another=PhasePermit(second,path,second['binding'])
            with self.assertRaises(BudgetStop):
                another.reserve_attempt(another.start_logical('metadata'),request())
            self.assertEqual(ledger_summary(path)['charged_or_reserved_microusd'],37753536)
            self.assertEqual(ledger_summary(path)['physical_attempts'],4)

    def test_fresh_processes_share_study_spending_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path=str(Path(directory)/'ledger')
            for index in range(3):
                historical=approval('pilot','10',f'historical-{index}',f'historical-{index}')
                historical['pricing']['input_per_million']='9'
                permit=PhasePermit(historical,path,historical['binding'])
                token=permit.reserve_attempt(permit.start_logical('metadata'),request())
                permit.settle(token,{'prompt_tokens':1000000,'completion_tokens':0})
            context=multiprocessing.get_context('spawn')
            outcomes=context.Queue()
            processes=[]
            for index in range(2):
                auth=approval('pilot','10',f'phase-{index}',f'run-{index}')
                auth['pricing']['input_per_million']='9'
                processes.append(context.Process(target=reserve_from_new_process,args=(path,auth,outcomes)))
            for process in processes:process.start()
            for process in processes:
                process.join(10)
                self.assertEqual(process.exitcode,0)
            self.assertCountEqual([outcomes.get(timeout=2) for _ in processes],['reserved','stopped'])
            self.assertEqual(ledger_summary(path)['physical_attempts'],4)
            self.assertEqual(ledger_summary(path)['charged_or_reserved_microusd'],36438384)

    def test_new_approval_cannot_reset_an_existing_run_handle(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'ledger'
            permit=PhasePermit(approval(),path,binding())
            permit.reserve_attempt(permit.start_logical('metadata'),request())
            with self.assertRaises(BudgetStop):
                PhasePermit(approval(ident='new-approval'),path,binding())
            self.assertEqual(ledger_summary(path)['physical_attempts'],1)

    def test_request_cannot_borrow_another_phase_logical_call(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'ledger'
            permit=PhasePermit(approval(),path,binding())
            logical=permit.start_logical('metadata')
            other=PhasePermit(approval(ident='other-approval',run='other-run'),path,binding())
            with self.assertRaises(BudgetStop):other.reserve_attempt(logical,request())
            self.assertEqual(ledger_summary(path)['physical_attempts'],0)
            self.assertTrue(other.summary()['halted'])

    def test_approval_rejects_unsafe_or_incomplete_configuration_before_creating_ledger(self):
        cases=[('approved',False),('phase','other'),('approved_at','2026-11-01'),
               ('limits.phase_usd','NaN'),('limits.phase_usd','Infinity'),
               ('limits.phase_usd','0'),('limits.phase_usd','2.000001'),
               ('limits.max_attempts',133),('limits.max_attempts',True),
               ('limits.max_logical_calls',45),('limits.max_logical_calls',1.0),
               ('pricing.input_per_million','.29'),('pricing.output_per_million','1.19'),
               ('pricing.max_context_tokens',1048575),('pricing.max_output_tokens',999),
               ('pricing.max_output_tokens',1000),('pricing.max_output_tokens',4001),
               ('pricing.max_output_tokens',4000.0),('pricing.max_output_tokens',True),
               ('binding.preflight_sha256','missing'),('binding.population','full')]
        for key,value in cases:
            with self.subTest(key=key,value=value),tempfile.TemporaryDirectory() as directory:
                auth=approval()
                target=auth
                parts=key.split('.')
                for part in parts[:-1]:target=target[part]
                target[parts[-1]]=value
                path=Path(directory)/'ledger'
                with self.assertRaises(BudgetStop):PhasePermit(auth,path,auth['binding'])
                self.assertFalse(path.exists())

    def test_invalid_physical_contract_halts_before_reservation(self):
        changes=[{'model':'other'},{'endpoint':'https://example.invalid'},
                 {'max_tokens':999},{'stream':True},{'temperature':.5},
                 {'thinking':'enabled'}]
        for change in changes:
            with self.subTest(change=change),tempfile.TemporaryDirectory() as directory:
                permit=PhasePermit(approval(),Path(directory)/'ledger',binding())
                with self.assertRaises(BudgetStop):
                    permit.reserve_attempt(permit.start_logical('metadata'),request()|change)
                self.assertEqual(permit.summary()['physical_attempts'],0)
                self.assertTrue(permit.summary()['halted'])


if __name__=='__main__':unittest.main()
