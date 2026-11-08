"""An explicit immutable support reference cannot replace the scientific oracle."""
import hashlib
import subprocess
import sys

import pytest

from amem_repro import replay_baseline as replay
from amem_repro.replay import ReplayMismatch


def sha(value):
    return hashlib.sha256(value).hexdigest()


def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


@pytest.fixture
def repository(tmp_path):
    git(tmp_path,'init','-q')
    git(tmp_path,'config','user.name','Offline replay test')
    git(tmp_path,'config','user.email','offline@example.invalid')
    support=('adapter','artifacts','author','budget','checkpoint','config','measurements','phases','reporting','runner')
    paths=[f'amem_repro/{name}.py' for name in support]
    paths+=['memory_layer.py','amem_repro/contracts.py','amem_repro/scoring.py',
            'amem_repro/unregistered.py','config/assets.json','config/study.json']
    for name in paths:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('archived '+name+'\n')
    git(tmp_path,'add','.');git(tmp_path,'commit','-qm','archived')
    old=git(tmp_path,'rev-parse','HEAD')
    archived={'author_revision':'frozen-author','files':{n:sha((tmp_path/n).read_bytes()) for n in paths}}
    (tmp_path/'amem_repro/adapter.py').write_text('reviewed passive/profile support\n')
    (tmp_path/'amem_repro/new_support.py').write_text('new reviewed offline support\n')
    git(tmp_path,'add','.');git(tmp_path,'commit','-qm','reviewed support')
    reviewed=git(tmp_path,'rev-parse','HEAD')
    def current():
        return {'author_revision':'frozen-author','files':{n:sha((tmp_path/n).read_bytes())
                for n in paths+['amem_repro/new_support.py']}}
    return tmp_path,archived,current,old,reviewed


def test_changed_support_requires_explicit_reference_and_emits_migration_evidence(repository):
    root,archived,current,_,reviewed=repository
    with pytest.raises(ReplayMismatch,match='source amem_repro/adapter.py'):
        replay.verify_replay_sources(root,archived,current())
    receipt=replay.verify_replay_sources(root,archived,current(),support_reference=reviewed)
    assert receipt['reference_commit']==reviewed
    assert list(receipt['changed_existing_files'])==['amem_repro/adapter.py']
    assert receipt['added_files']=={'amem_repro/new_support.py':current()['files']['amem_repro/new_support.py']}
    assert receipt['all_current_sources_match_reference'] is True
    assert receipt['archived_critical_pins_retained'] is True
    assert receipt['run1_output_limits']['shared_decision']==4000


def test_reviewed_replay_can_relocate_only_the_exact_upstream_readme(repository, monkeypatch):
    root, archived, current, _, _ = repository
    (root / 'README.md').write_text('original instructions\n')
    git(root, 'add', 'README.md')
    git(root, 'commit', '-qm', 'Original README')
    upstream = git(root, 'rev-parse', 'HEAD')
    monkeypatch.setattr(replay, 'AUTHOR_REVISION', upstream)
    archived['author_revision'] = upstream
    digest = sha((root / 'README.md').read_bytes())
    archived['files']['README.md'] = digest
    git(root, 'mv', 'README.md', replay.UPSTREAM_README)
    (root / 'README.md').write_text('Coursework guide\n')
    git(root, 'add', 'README.md')
    git(root, 'commit', '-qm', 'Preserve original README')
    reviewed = git(root, 'rev-parse', 'HEAD')
    inventory = current()
    inventory['author_revision'] = upstream
    inventory['files'][replay.UPSTREAM_README] = digest
    with pytest.raises(ReplayMismatch):
        replay.verify_replay_sources(root, archived, inventory)
    receipt = replay.verify_replay_sources(root, archived, inventory, support_reference=reviewed)
    assert receipt['relocated_files'] == {'README.md': replay.UPSTREAM_README}
    assert receipt['archived_source_sha256'] == replay.fingerprint(archived)
    assert receipt['current_source_sha256'] == replay.fingerprint(inventory)
    assert replay.UPSTREAM_README not in receipt['added_files']
    archived['files']['README.md'] = '0' * 64
    inventory['files'][replay.UPSTREAM_README] = '0' * 64
    with pytest.raises(ReplayMismatch, match='archived README'):
        replay.verify_replay_sources(root, archived, inventory, support_reference=reviewed)
    archived['files']['README.md'] = digest
    with pytest.raises(ReplayMismatch, match=replay.UPSTREAM_README):
        replay.verify_replay_sources(root, archived, inventory, support_reference=reviewed)


@pytest.mark.parametrize('reference',['HEAD','main','short','f'*40])
def test_reference_must_be_existing_full_immutable_commit(repository,reference):
    root,archived,current,_,_=repository
    with pytest.raises(ReplayMismatch,match='reference'):
        replay.verify_replay_sources(root,archived,current(),support_reference=reference)


def test_wrong_immutable_reference_does_not_accept_current_support(repository):
    root,archived,current,old,_=repository
    with pytest.raises(ReplayMismatch,match='reference'):
        replay.verify_replay_sources(root,archived,current(),support_reference=old)


@pytest.mark.parametrize('critical',['memory_layer.py','amem_repro/contracts.py','amem_repro/scoring.py',
                                    'amem_repro/unregistered.py','config/assets.json','config/study.json'])
def test_even_reviewed_commit_cannot_replace_archived_critical_source(repository,critical):
    root,archived,current,_,_=repository
    (root/critical).write_text('changed critical oracle\n')
    git(root,'add',critical);git(root,'commit','-qm','forbidden critical change')
    ref=git(root,'rev-parse','HEAD')
    with pytest.raises(ReplayMismatch,match='source '+critical):
        replay.verify_replay_sources(root,archived,current(),support_reference=ref)


def test_unreviewed_allowed_file_edit_and_added_file_edit_both_reject(repository):
    root,archived,current,_,reviewed=repository
    for name in ('amem_repro/adapter.py','amem_repro/new_support.py'):
        p=root/name;original=p.read_bytes();p.write_text('unreviewed edit\n')
        with pytest.raises(ReplayMismatch,match='reference'):
            replay.verify_replay_sources(root,archived,current(),support_reference=reviewed)
        p.write_bytes(original)


def test_reviewed_reference_cannot_remove_archived_support(repository):
    root,archived,current,_,reviewed=repository
    missing=current()
    del missing['files']['amem_repro/adapter.py']
    with pytest.raises(ReplayMismatch,match='source amem_repro/adapter.py'):
        replay.verify_replay_sources(root,archived,missing,support_reference=reviewed)


def test_full_blob_sha_is_not_a_reviewed_commit(repository):
    root,archived,current,_,_=repository
    blob=git(root,'hash-object','amem_repro/adapter.py')
    with pytest.raises(ReplayMismatch,match='reference'):
        replay.verify_replay_sources(root,archived,current(),support_reference=blob)


def test_reference_cannot_change_default_run1_generation_limits(repository,monkeypatch):
    root,archived,current,_,reviewed=repository
    monkeypatch.setattr(replay,'stage_output_limits',lambda:{'metadata':1000,'shared_decision':8192,'query_keywords':1000,'answer':1000})
    with pytest.raises(ReplayMismatch,match='Run1 output limits'):
        replay.verify_replay_sources(root,archived,current(),support_reference=reviewed)


def test_cli_forwards_explicit_reference_without_inferring_head(monkeypatch,capsys):
    received={}
    def capture(assets,output,**kwargs):
        received.update(assets=assets,output=output,**kwargs)
        return {'paid_calls':0}
    monkeypatch.setattr(replay,'replay_baseline',capture)
    monkeypatch.setattr(sys,'argv',['replay_baseline','--assets','local-assets',
                                  '--output','fresh-output','--support-reference','a'*40])
    replay.main()
    assert received['support_reference']=='a'*40
    assert received['factory_builder'] is None
    assert '"paid_calls": 0' in capsys.readouterr().out
