"""Operator-only redaction and opt-in read-only auth check, after key rotation.

Never apply redaction to authoritative benchmark/provider records. Raw process
output stays in memory; this helper never prints it or writes audit files.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from urllib.parse import urlsplit

COMMAND = ('npx', '--yes', 'langfuse-cli@1.2.4', 'api', 'projects', 'list', '--json')
LF_KEYS = {'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_BASE_URL', 'LANGFUSE_HOST'}
CLOUD_HOSTS = {'cloud.langfuse.com', 'us.cloud.langfuse.com', 'jp.cloud.langfuse.com', 'hipaa.cloud.langfuse.com'}


def redact_operator_text(text, *, secrets=()):
    """Return a safe operator copy, including masked key previews and auth values."""
    value = str(text)
    for secret in sorted((str(s) for s in secrets if s), key=len, reverse=True):
        value = value.replace(secret, '[redacted]')
    value = re.sub(r'''(?i)\b(?:Bearer|Basic)\s+[^\s"'<>]+''', '[redacted]', value)
    return re.sub(r'''(?i)\b(?:sk|pk)-[^\s"'<>),;\]}]+''', '[redacted]', value)


def check_langfuse_project_auth(env_file, expected_project_id):
    """Run exactly one read-only command; return only allowlisted result fields."""
    result = {'status': 'failed', 'project_match': False, 'error_type': 'ConfigurationError'}
    try:
        values = {}
        for line in Path(env_file).read_text().splitlines():
            match = re.match(r'^\s*(?:export\s+)?([A-Z_]+)\s*=(.*)$', line)
            if match and match[1] in LF_KEYS:
                parts = shlex.split(match[2], comments=True)
                if len(parts) != 1:
                    return result
                values[match[1]] = parts[0]
        host = values.get('LANGFUSE_BASE_URL') or values.get('LANGFUSE_HOST', '')
        parsed = urlsplit(host)
        if (not expected_project_id or not all(values.get(k) for k in ('LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY'))
                or parsed.scheme != 'https' or parsed.netloc not in CLOUD_HOSTS
                or parsed.path not in ('', '/') or parsed.query or parsed.fragment):
            return result
        # Allowlist child variables: never inherit provider keys, auth/debug flags,
        # npm options, NODE_OPTIONS or arbitrary environment-driven command changes.
        child = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR', 'SYSTEMROOT', 'WINDIR') if k in os.environ}
        child.update(values, LANGFUSE_BASE_URL=host, LANGFUSE_HOST=host, npm_config_loglevel='silent')
    except Exception:
        return result
    try:
        response = subprocess.run(list(COMMAND), env=child, capture_output=True, text=True, timeout=30, check=False)
    except Exception:
        return {**result, 'error_type': 'ExecutionError'}
    if type(response.returncode) is not int or response.returncode != 0:
        return {**result, 'error_type': 'CommandFailed'}
    try:
        envelope = json.loads(response.stdout)
        if type(envelope['status']) is not int or envelope['status'] != 200:
            raise ValueError
        projects = envelope['body']['data']
        if not isinstance(projects, list) or any(not isinstance(p, dict) or not isinstance(p.get('id'), str) for p in projects):
            raise ValueError
        matched = any(p['id'] == expected_project_id for p in projects)
    except Exception:
        return {**result, 'error_type': 'InvalidResponse'}
    return {'status': 'ok' if matched else 'failed', 'project_match': matched, 'error_type': None if matched else 'ProjectMismatch'}


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError  # argparse must not echo unknown arguments containing keys.


def main(argv=None):
    parser = SafeParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check-auth', action='store_true', help='Read-only project check; use only after rotating the exposed key.')
    group.add_argument('--redact', action='store_true', help='Redact an operator-only stdin copy.')
    parser.add_argument('--env-file', default='.env')
    parser.add_argument('--expected-project-id')
    try:
        args = parser.parse_args(argv)
        if args.redact:
            print(redact_operator_text(sys.stdin.read()))
            return 0
        result = check_langfuse_project_auth(args.env_file, args.expected_project_id) if args.check_auth else {'status': 'not_run', 'project_match': False, 'error_type': None}
    except Exception:
        result = {'status': 'failed', 'project_match': False, 'error_type': 'ConfigurationError'}
    print(json.dumps(result))
    return int(result['status'] == 'failed')


if __name__ == '__main__':
    raise SystemExit(main())
