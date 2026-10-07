import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'skills/pcb-layout-engineer/scripts/verify-exports.py'
spec = importlib.util.spec_from_file_location('exports', PATH)
exports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exports)


class ExportTests(unittest.TestCase):
    def test_inventory_and_rejected_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            job = root / 'design-job.gbrjob'
            gerber = root / 'top.gbr'
            gerber.write_text('%MOMM*%\nM02*\n')
            data = {'GeneralSpecs': {'LayerNumber': 2}, 'FilesAttributes': [{'Path': 'top.gbr', 'FileFunction': 'Copper,L1,Top'}]}
            job.write_text(json.dumps(data))
            self.assertEqual(exports.inspect(job, 2)['files']['top.gbr']['bytes'], gerber.stat().st_size)
            with self.assertRaisesRegex(ValueError, 'Expected 4'):
                exports.inspect(job, 4)
            gerber.write_text('truncated')
            with self.assertRaisesRegex(ValueError, 'end marker'):
                exports.inspect(job)
            data['FilesAttributes'][0]['Path'] = '../outside.gbr'
            job.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'outside'):
                exports.inspect(job)
