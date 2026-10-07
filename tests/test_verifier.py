"""Exercise verifier outcomes using a mock CLI; native compatibility is a separate smoke test."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

VERIFIER = Path(__file__).resolve().parents[1] / 'skills/pcb-layout-engineer/scripts/verify-board.sh'
MOCK = r'''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
mode = os.environ['MOCK_MODE']
if args == ['version']:
    print('10.0.6'); sys.exit(0)
if '--help' in args:
    print('--format --severity-all --exit-code-violations --refill-zones --schematic-parity --all-track-errors'); sys.exit(0)
if mode == 'process-failure':
    sys.exit(3)
output = pathlib.Path(args[args.index('--output') + 1])
if mode == 'missing-report':
    sys.exit(0)
if mode == 'malformed':
    output.write_text('invalid'); sys.exit(0)
erc = 'erc' in args
finding = {'severity': 'error', 'description': 'known finding'}
report = {'$schema': 'https://schemas.kicad.org/' + ('erc.v1.json' if erc else 'drc.v1.json'),
          'included_severities': ['error', 'warning', 'exclusion'], 'ignored_checks': []}
if erc:
    report['sheets'] = [{'path': '/child', 'violations': [finding] if mode == 'erc-finding' else []}]
else:
    report.update(violations=[], unconnected_items=[], schematic_parity=[])
    if mode == 'finding': report['violations'] = [finding, {'severity': 'warning'}, {'severity': 'exclusion'}]
    if mode == 'opens': report['unconnected_items'] = [finding]
    if mode == 'parity' and '--schematic-parity' in args: report['schematic_parity'] = [finding]
if mode == 'disabled': report['ignored_checks'] = [{'key': 'disabled'}]
if mode == 'schema': report['$schema'] = 'unknown'
if mode == 'coverage': report['included_severities'] = ['error']
if mode == 'mutate': pathlib.Path(args[-1]).write_text('changed')
output.write_text(json.dumps(report))
sys.exit(5 if mode in ('finding', 'opens', 'parity', 'erc-finding') else 0)
'''


class VerifierTests(unittest.TestCase):
    def run_case(self, mode, expected, *, erc=True, project=True, conflict=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            board = root / 'design.kicad_pcb'
            board.write_text('fixture; parsed only by mock')
            sch = root / 'design.kicad_sch'
            sch.write_text('fixture')
            if project:
                (root / 'design.kicad_pro').write_text('{}')
            cli = root / 'mock-cli'
            cli.write_text(MOCK)
            cli.chmod(0o755)
            command = ['bash', str(VERIFIER), str(board)]
            if erc:
                if conflict:
                    sch = root / 'other.kicad_sch'
                    sch.write_text('fixture')
                command.append(str(sch))
            result = subprocess.run(command, env={**os.environ, 'KICAD_CLI': str(cli), 'MOCK_MODE': mode}, capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            manifest = json.loads(next((root / 'temp').glob('*/manifest.json')).read_text())
            self.assertEqual(manifest['exit_status'], expected)
            if not erc:
                self.assertFalse(manifest['checks']['erc']['in_exit_scope'])
            if mode == 'erc-finding':
                self.assertEqual(manifest['checks']['erc']['counts']['violations'], 1)

    def test_scoped_clear_and_omitted_erc(self):
        self.run_case('clean', 0)
        self.run_case('clean', 0, erc=False)

    def test_findings_and_disabled_checks(self):
        for mode in ('finding', 'opens', 'parity', 'erc-finding', 'disabled'):
            with self.subTest(mode=mode):
                self.run_case(mode, 1)

    def test_failed_unknown_checks(self):
        for mode in ('process-failure', 'missing-report', 'malformed', 'schema', 'coverage', 'mutate'):
            with self.subTest(mode=mode):
                self.run_case(mode, 2)
        self.run_case('clean', 2, project=False)
        self.run_case('clean', 2, conflict=True)
