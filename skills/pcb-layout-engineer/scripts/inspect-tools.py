#!/usr/bin/env python3
"""Report available PCB programs without installing or changing configuration."""
import json
import shutil
import subprocess

PROGRAMS = ('kicad', 'kicad-cli', 'eeschema', 'pcbnew', 'gerbview',
            'pcb_calculator', 'bitmap2component', 'pl_editor', 'ngspice', 'freerouting')
report = {name: {'available': bool(shutil.which(name))} for name in PROGRAMS}
if report['kicad-cli']['available']:
    try:
        result = subprocess.run(['kicad-cli', 'version'], capture_output=True, text=True, timeout=15)
        report['kicad-cli'].update(version=result.stdout.strip(), returncode=result.returncode)
    except (OSError, subprocess.TimeoutExpired) as exc:
        report['kicad-cli']['error'] = str(exc)
report['scope'] = 'PATH discovery only; availability does not establish IPC or simulation functionality'
print(json.dumps(report, indent=2))
