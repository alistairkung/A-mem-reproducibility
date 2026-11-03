"""Operator tooling only; all credentials and process responses are synthetic."""
import json
from types import SimpleNamespace

from scripts import safe_service_audit as audit


def test_operator_redaction_covers_credentials_previews_auth_and_explicit_literals():
    raw = 'sk-provider-123 pk-lf-public123 sk-lf-...ab12 pk-lf-••••cd34 Bearer token123 Basic dXNlcjpwYXNz explicit-private-value'
    redacted = audit.redact_operator_text(raw, secrets=['explicit-private-value'])
    assert redacted == '[redacted] [redacted] [redacted] [redacted] [redacted] [redacted] [redacted]'
    assert raw.endswith('explicit-private-value')  # Input remains authoritative and untouched.
    assert audit.redact_operator_text('Authorization: Bearer abc~privateSuffix') == 'Authorization: [redacted]'
    assert audit.redact_operator_text('{"Authorization":"Basic abc~privateSuffix"}') == '{"Authorization":"[redacted]"}'


def test_explicit_auth_check_uses_only_pinned_read_only_command_and_safe_output(tmp_path, monkeypatch, capsys):
    path = tmp_path / '.env'
    path.write_text('LANGFUSE_PUBLIC_KEY=pk-lf-test\nLANGFUSE_SECRET_KEY=sk-lf-test\nLANGFUSE_HOST=https://cloud.langfuse.com\nDEEPSEEK_API_KEY=sk-provider-file\n')
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-provider-shell')
    monkeypatch.setenv('LANGFUSE_DEBUG', 'true')

    def process(command, **kwargs):
        assert command == ['npx', '--yes', 'langfuse-cli@1.2.4', 'api', 'projects', 'list', '--json']
        child = kwargs['env']
        assert child['LANGFUSE_PUBLIC_KEY'] == 'pk-lf-test'
        assert child['LANGFUSE_SECRET_KEY'] == 'sk-lf-test'
        assert 'OPENAI_API_KEY' not in child and 'DEEPSEEK_API_KEY' not in child and 'LANGFUSE_DEBUG' not in child
        assert child['npm_config_cache'].endswith('/amem-run2-langfuse-cli-cache')
        assert kwargs['capture_output'] is True and kwargs['timeout'] == 30
        return SimpleNamespace(returncode=0, stdout=json.dumps({'status': 200, 'headers': {'authorization': 'Basic synthetic-private-header', 'x-secret': 'sk-lf-private-header'}, 'body': {'data': [{'id': 'expected-project', 'name': 'PRIVATE PROJECT sk-leak'}]}}), stderr='Basic dXNlcjpwYXNz sk-secret-stderr')

    monkeypatch.setattr(audit.subprocess, 'run', process)
    assert audit.main(['--check-auth', '--expected-project-id', 'expected-project', '--env-file', str(path)]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {'status': 'ok', 'project_match': True, 'error_type': None}
    assert captured.err == ''


def test_auth_failures_never_echo_untrusted_process_output(tmp_path, monkeypatch, capsys):
    path = tmp_path / '.env'
    path.write_text('LANGFUSE_PUBLIC_KEY=pk-lf-fake\nLANGFUSE_SECRET_KEY=sk-lf-fake\nLANGFUSE_HOST=https://cloud.langfuse.com\n')
    cases = [
        (SimpleNamespace(returncode=1, stdout='sk-stdout', stderr='Basic bad-secret'), 'CommandFailed'),
        (SimpleNamespace(returncode=0, stdout='Bearer bad-json', stderr='sk-stderr'), 'InvalidResponse'),
        (RuntimeError('Basic exception-private-value'), 'ExecutionError'),
        (SimpleNamespace(returncode=0, stdout=json.dumps({'status': 200, 'headers': {'x-secret': 'sk-private-header'}, 'body': {'data': [{'id': 'different', 'name': 'sk-private-name'}]}}), stderr=''), 'ProjectMismatch'),
        (SimpleNamespace(returncode=0, stdout=json.dumps({'status': 400, 'headers': {'authorization': 'Basic private-header'}, 'body': {'data': [{'id': 'expected'}], 'error': 'sk-private-error'}}), stderr='Bearer private-stderr'), 'InvalidResponse'),
        (SimpleNamespace(returncode=0, stdout=json.dumps({'status': '200 sk-private-status', 'body': {'data': [{'id': 'expected'}]}}), stderr=''), 'InvalidResponse'),
        (SimpleNamespace(returncode=0, stdout=json.dumps({'status': 200.0, 'body': {'data': [{'id': 'expected'}]}}), stderr=''), 'InvalidResponse'),
        (SimpleNamespace(returncode=0, stdout=json.dumps({'status': 200, 'body': 'sk-private-body'}), stderr=''), 'InvalidResponse'),
        (SimpleNamespace(returncode=0, stdout=json.dumps({'status': 200, 'body': {'data': 'Basic private-data'}}), stderr=''), 'InvalidResponse'),
        (SimpleNamespace(returncode=0, stdout=json.dumps({'data': [{'id': 'expected'}]}), stderr=''), 'InvalidResponse'),
    ]
    for response, error_type in cases:
        def process(*args, **kwargs):
            if isinstance(response, Exception):
                raise response
            return response
        monkeypatch.setattr(audit.subprocess, 'run', process)
        assert audit.main(['--check-auth', '--expected-project-id', 'expected', '--env-file', str(path)]) == 1
        captured = capsys.readouterr()
        assert json.loads(captured.out) == {'status': 'failed', 'project_match': False, 'error_type': error_type}
        assert captured.err == ''


def test_default_invalid_arguments_and_untrusted_hosts_cannot_start_a_process(tmp_path, monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError('No command is authorized')
    monkeypatch.setattr(audit.subprocess, 'run', forbidden)
    assert audit.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {'status': 'not_run', 'project_match': False, 'error_type': None}
    assert audit.main(['--unknown=sk-argument-secret']) == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {'status': 'failed', 'project_match': False, 'error_type': 'ConfigurationError'}
    assert captured.err == ''
    path = tmp_path / '.env'
    path.write_text('LANGFUSE_PUBLIC_KEY=pk-lf-fake\nLANGFUSE_SECRET_KEY=sk-lf-fake\nLANGFUSE_HOST=https://cloud.langfuse.com@untrusted.invalid\n')
    assert audit.main(['--check-auth', '--expected-project-id', 'expected', '--env-file', str(path)]) == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)['error_type'] == 'ConfigurationError'
    assert captured.err == ''
