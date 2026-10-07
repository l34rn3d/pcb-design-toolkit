#!/usr/bin/env python3
"""Inspect native Gerber-job file inventory and hashes; not geometry or DFM approval."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def inspect(job_path, expected_layers=None):
    job_path = Path(job_path).resolve()
    job = json.loads(job_path.read_text())
    files = job.get('FilesAttributes')
    if not isinstance(files, list) or not files:
        raise ValueError('Missing or empty Gerber-job FilesAttributes')
    layers = job.get('GeneralSpecs', {}).get('LayerNumber')
    if not isinstance(layers, int) or layers < 1:
        raise ValueError('Missing or invalid copper-layer count')
    if expected_layers is not None and layers != expected_layers:
        raise ValueError(f'Expected {expected_layers} layers, found {layers}')
    inventory = {}
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get('Path'), str):
            raise ValueError('Invalid job file entry')
        path = (job_path.parent / entry['Path']).resolve()
        if job_path.parent not in path.parents:
            raise ValueError('Job references a file outside its export directory')
        if entry['Path'] in inventory:
            raise ValueError('Duplicate job file entry')
        data = path.read_bytes()
        if not data.strip().endswith(b'M02*'):
            raise ValueError(f'Missing Gerber end marker: {entry["Path"]}')
        inventory[entry['Path']] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                                    'function': entry.get('FileFunction')}
    return {'status': 'PASS within inventory scope', 'copper_layers': layers, 'files': inventory,
            'limitations': ['Geometry, layer/drill registration, mask/paste and manufacturer DFM not checked',
                            'Drills, BOM, positions and files absent from the job need separate review',
                            'Inspect exports in native Gerber viewer before ordering']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', help='Native .gbrjob path')
    parser.add_argument('--expected-layers', type=int)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.job, args.expected_layers), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'UNKNOWN: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
