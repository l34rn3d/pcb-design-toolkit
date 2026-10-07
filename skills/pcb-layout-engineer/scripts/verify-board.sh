#!/usr/bin/env bash
# Read-only native checks. Reports under board directory/temp; no board save.
set -euo pipefail
if [[ ${1:-} == --help || ${1:-} == -h ]]; then
  printf '%s\n' 'Usage: bash verify-board.sh BOARD.kicad_pcb [ROOT.kicad_sch]' \
    'Needs Bash, Python 3, kicad-cli on PATH (or KICAD_CLI=/path/to/wrapper).' \
    'Reports: BOARD_DIRECTORY/temp/pcb-verify-<unique>/' \
    'Exit 0: requested native scope clear; 1: findings/disabled checks; 2: required check failed/unknown.' \
    'Omitted ERC and manual engineering/rule reviews are outside exit-code scope.' \
    'No manufacturing outputs; no saved zone fill; not an engineering approval.'
  exit 0
fi
if [[ $# -lt 1 || $# -gt 2 ]]; then
  printf '%s\n' 'Usage: bash verify-board.sh BOARD.kicad_pcb [ROOT.kicad_sch]' >&2
  exit 2
fi
command -v python3 >/dev/null || { printf '%s\n' 'UNKNOWN: Python 3 missing' >&2; exit 2; }
exec python3 - "$@" <<'PY'
import collections
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def exception_handler(kind, value, traceback):
    print('UNKNOWN: verification aborted:', value, file=sys.stderr)
    sys.exit(2)

sys.excepthook = exception_handler


def die(message):
    print('UNKNOWN:', message, file=sys.stderr)
    sys.exit(2)


board = Path(sys.argv[1]).expanduser().resolve()
if not board.is_file() or board.suffix != '.kicad_pcb':
    die('Board must be an existing .kicad_pcb file')
sch = Path(sys.argv[2]).expanduser().resolve() if len(sys.argv) == 3 else None
if sch and (not sch.is_file() or sch.suffix != '.kicad_sch'):
    die('Schematic must be an existing root .kicad_sch file')
cli = shutil.which(os.environ.get('KICAD_CLI', 'kicad-cli'))
if not cli:
    die('Compatible kicad-cli missing; KICAD_CLI accepts one executable, not shell arguments')
try:
    temp = board.parent / 'temp'
    temp.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='pcb-verify-', dir=temp))
except OSError as e:
    die(str(e))
print('Reports:', out)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# Track all source/context files in the project tree, including hierarchical sheets.
# Output temp and common repository/dependency dirs are not project source context.
context = {}
for root, dirs, files in os.walk(board.parent):
    dirs[:] = [d for d in dirs if d not in ('temp', '.git', 'node_modules', '.venv')]
    for name in files:
        p = Path(root) / name
        if p.suffix in ('.kicad_pcb', '.kicad_sch', '.kicad_pro', '.kicad_dru', '.kicad_sym', '.kicad_mod') or name in ('fp-lib-table', 'sym-lib-table'):
            context[str(p)] = digest(p)
for p in (board, sch):
    if p:
        context[str(p)] = digest(p)
manifest = {'board': str(board), 'schematic': str(sch) if sch else None,
            'cli': cli, 'context_sha256_before': context, 'commands': [], 'checks': {}}
exit_status = 0


def run(args, name):
    global exit_status
    try:
        result = subprocess.run([cli, *args], cwd=board.parent, capture_output=True, text=True, timeout=300)
        (out / (name + '.log')).write_text(result.stdout + '\n' + result.stderr)
        manifest['commands'].append({'argv': [cli, *args], 'returncode': result.returncode, 'log': name + '.log'})
        return result
    except (OSError, subprocess.TimeoutExpired) as e:
        exit_status = 2
        manifest['commands'].append({'argv': [cli, *args], 'error': str(e)})
        print('UNKNOWN:', name, str(e))
        return None


def unknown(name, message):
    global exit_status
    exit_status = 2
    manifest['checks'][name] = {'status': 'UNKNOWN', 'reason': message}
    print('UNKNOWN:', name, message)


def check(name, args, required):
    global exit_status
    result = run(args, name)
    # KiCad's --exit-code-violations uses 5 for reported violations.
    if result is None or result.returncode not in (0, 5):
        unknown(name, 'Native check failed; inspect log')
        return
    try:
        data = json.loads((out / (name + '.json')).read_text())
        if not isinstance(data, dict):
            raise ValueError('Report root is not an object')
        schema = 'https://schemas.kicad.org/' + ('erc.v1.json' if name == 'erc' else 'drc.v1.json')
        if data.get('$schema') != schema:
            raise ValueError('Unknown report schema: ' + str(data.get('$schema')))
        if not isinstance(data.get('included_severities'), list) or not {'error', 'warning', 'exclusion'}.issubset(data['included_severities']):
            raise ValueError('Incomplete severity coverage')
        if name == 'erc':
            if not isinstance(data.get('sheets'), list):
                raise ValueError('Missing ERC sheets array')
            arrays = {'violations': []}
            for sheet in data['sheets']:
                if not isinstance(sheet, dict) or not isinstance(sheet.get('violations'), list):
                    raise ValueError('Unknown ERC sheet representation')
                for finding in sheet['violations']:
                    if not isinstance(finding, dict):
                        raise ValueError('Unknown ERC finding representation')
                    arrays['violations'].append(dict(finding, sheet_path=sheet.get('path')))
        else:
            for key in required:
                if not isinstance(data.get(key), list):
                    raise ValueError('Missing/unknown report array: ' + key)
            arrays = {key: data[key] for key in ('violations', 'unconnected_items', 'schematic_parity') if key in data}
            if any(not isinstance(v, list) for v in arrays.values()):
                raise ValueError('Unknown DRC finding representation')
        ignored = data.get('ignored_checks')
        if not isinstance(ignored, list):
            raise ValueError('Missing/unknown disabled-check inventory')
        findings = [item for values in arrays.values() for item in values]
        if any(not isinstance(item, dict) for item in findings):
            raise ValueError('Unknown finding representation')
        severity = collections.Counter(str(item.get('severity', 'unknown')) for item in findings)
        status = 'REVIEW' if findings or ignored or result.returncode == 5 else 'PASS'
        if status == 'REVIEW':
            exit_status = max(exit_status, 1)
        manifest['checks'][name] = {'status': status, 'counts': {k: len(v) for k, v in arrays.items()},
                                   'severity': dict(severity), 'ignored_checks': ignored, 'source': data.get('source'),
                                   'report_schema': schema, 'report': name + '.json'}
        print(status + ':', name, json.dumps(manifest['checks'][name]))
    except (OSError, ValueError, TypeError) as e:
        unknown(name, str(e))


version = run(['version'], 'version')
manifest['kicad_version'] = version.stdout.strip() if version and version.returncode == 0 else None
if not manifest['kicad_version']:
    unknown('version', 'Unable to establish CLI version')
help_drc = run(['pcb', 'drc', '--help'], 'drc-help')
needed = ('--format', '--severity-all', '--exit-code-violations', '--refill-zones')
if not help_drc or help_drc.returncode != 0 or not all(flag in help_drc.stdout for flag in needed):
    unknown('drc', 'Installed CLI lacks required JSON/all-severity/refill/exit-code capabilities')
else:
    args = ['pcb', 'drc', '--format', 'json', '--severity-all', '--exit-code-violations',
            '--refill-zones', '--output', str(out / 'drc.json'), str(board)]
    if '--all-track-errors' in help_drc.stdout:
        args.insert(2, '--all-track-errors')
    check('drc', args, ('violations', 'unconnected_items'))
    if sch and sch != board.with_suffix('.kicad_sch'):
        unknown('parity', 'Supplied root schematic differs from same-stem parity source; establish authority independently')
    elif board.with_suffix('.kicad_sch').is_file() and '--schematic-parity' in help_drc.stdout:
        parity_args = args.copy()
        parity_args[parity_args.index(str(out / 'drc.json'))] = str(out / 'parity.json')
        parity_args.insert(2, '--schematic-parity')
        check('parity', parity_args, ('violations', 'unconnected_items', 'schematic_parity'))
    else:
        unknown('parity', 'No same-stem root schematic or CLI parity support; check correspondence independently')
if sch:
    help_erc = run(['sch', 'erc', '--help'], 'erc-help')
    if not help_erc or help_erc.returncode != 0 or not all(flag in help_erc.stdout for flag in needed[:3]):
        unknown('erc', 'Installed CLI lacks required ERC capabilities')
    else:
        check('erc', ['sch', 'erc', '--format', 'json', '--severity-all', '--exit-code-violations',
                      '--output', str(out / 'erc.json'), str(sch)], ('violations',))
else:
    manifest['checks']['erc'] = {'status': 'UNKNOWN', 'in_exit_scope': False, 'reason': 'Not requested; required if schematic changed'}
    print('UNKNOWN: ERC not requested; required if schematic changed')
# Missing same-stem project rules are always surfaced, not silently accepted.
if not board.with_suffix('.kicad_pro').is_file():
    unknown('project_context', 'No same-stem .kicad_pro; verify rule/project context independently')
else:
    manifest['checks']['project_context'] = {'status': 'REVIEW', 'reason': 'Project file present; effective rules still require inspection'}
changed = [p for p, old in context.items() if not Path(p).is_file() or digest(Path(p)) != old]
manifest['source_files_changed'] = changed
if changed:
    unknown('source_integrity', 'Source/context changed during checks; do not reuse this result')
else:
    manifest['checks']['source_integrity'] = {'status': 'PASS', 'reason': 'Tracked source/context hashes unchanged'}
manifest['limitations'] = ['No engineering/fabrication approval', 'Zone refill is in memory, not saved',
                          'Exit scope: requested native checks, parity, project presence, tracked-file integrity; manual review and omitted ERC are outside exit scope',
                          'Hash inventory covers existing tracked files only; external/symlinked libraries and sheets may be untracked',
                          'Inspect warnings, exclusions and disabled checks individually', 'Validate effective project/custom rules manually',
                          'Dimensions/layers/vias/packages/pinouts/returns/impedance/mechanics/manufacturing not validated']
manifest['exit_status'] = exit_status
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('REVIEW: Engineering checklist still required; no manufacturing outputs generated.')
sys.exit(exit_status)
PY
