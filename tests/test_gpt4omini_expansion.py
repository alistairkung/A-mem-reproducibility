"""Release boundaries for the final six matched ablations."""
from amem_repro.openrouter import (
    ACCEPTED_ORDER, ABLATION_POLICY, CELL_ORDER, CELL_SERVICE_RESERVE, EXPANSION_CELLS,
    EXPANSION_POLICY, PROGRAM_SERVICE_RESERVE, ablation_policy, cell_parts, predecessor_filename,
)


def test_expansion_begins_after_consumed_terminal_frontier():
    assert CELL_ORDER[:6] == ACCEPTED_ORDER
    assert [cell_parts(key) for key in EXPANSION_CELLS] == [
        ('conv-50','evolution_only'), ('conv-44','evolution_only'),
        ('conv-50','neither'), ('conv-44','neither'),
        ('conv-50','linking_only'), ('conv-44','linking_only')]
    assert predecessor_filename(EXPANSION_CELLS[0]) == 'expansion-frontier.json'
    assert all(ablation_policy(c)==EXPANSION_POLICY for c in EXPANSION_CELLS)
    assert ablation_policy('neither-conv-49') == ABLATION_POLICY


def test_entire_program_fits_even_if_every_reserved_service_unit_is_billed():
    assert CELL_SERVICE_RESERVE == 1_080_000
    assert PROGRAM_SERVICE_RESERVE == 6_680_000
    assert 2_032_817 + 6*(5_000_000-CELL_SERVICE_RESERVE) + PROGRAM_SERVICE_RESERVE < 42_000_000


def test_service_limit_stops_before_opening_another_span():
    from scripts.gpt4omini_service import ServiceUnits
    import pytest
    meter=ServiceUnits(3)
    meter.admit('trace')
    meter.admit('trace')
    with pytest.raises(RuntimeError):meter.admit('another trace')
    assert meter.exhausted and meter.spent == 3
    with pytest.raises(RuntimeError):meter.admit()


def test_failed_gate_consumes_same_claim_for_all_output_names(tmp_path):
    import runpy, shutil, pytest
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    gate=runpy.run_path(str(root/'scripts/gpt4omini-gate.py'))
    prior=root/'artifacts/gpt4omini/verification/six-cell-expansion'
    if not (prior/'first-gate-settlement.json').exists():pytest.skip('Requires completed first cloud proof')
    for name in ('first-gate-settlement.json','six-cell-cloud-9e7d76f/receipt.json'):
        target=tmp_path/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(prior/name,target)
    assert gate['reserve_gate'](tmp_path,tmp_path/'first').limit==1382
    with pytest.raises(FileExistsError):
        gate['reserve_gate'](tmp_path,tmp_path/'second')
