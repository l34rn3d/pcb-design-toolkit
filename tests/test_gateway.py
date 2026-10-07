"""Offline plumbing checks; these do not establish a working KiCad connection."""
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/pcb-layout-engineer/scripts/kicad"))

import gateway
import install


FAKE_SERVER = r'''
import json, sys, time
for line in sys.stdin:
    msg = json.loads(line)
    if 'id' not in msg:
        continue
    method = msg['method']
    if method == 'initialize':
        result = {'protocolVersion': '2025-06-18', 'capabilities': {'tools': {}}}
    elif method == 'tools/list':
        if msg['params'].get('cursor') == 'page2':
            result = {'tools': [{'name': 'second'}]}
        else:
            print(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/tools/list_changed'}), flush=True)
            result = {'tools': [{'name': 'first'}], 'nextCursor': 'page2'}
    elif method == 'slow':
        time.sleep(5)
        continue
    elif method == 'bad':
        print(json.dumps({'jsonrpc': '2.0', 'id': msg['id'], 'error': {'code': -32602, 'message': 'bad input'}}), flush=True)
        continue
    else:
        result = {'isError': True, 'content': [{'type': 'text', 'text': 'not connected'}]}
    print(json.dumps({'jsonrpc': '2.0', 'id': msg['id'], 'result': result}), flush=True)
'''


class GatewayTests(unittest.TestCase):
    def test_mcp_initialize_notifications_pagination_and_errors(self):
        client = gateway.Client([sys.executable, '-u', '-c', FAKE_SERVER])
        try:
            self.assertEqual(client.initialize()['protocolVersion'], '2025-06-18')
            self.assertEqual([t['name'] for t in client.tools()], ['first', 'second'])
            self.assertTrue(client.request('tools/call', {})['isError'])
            with self.assertRaisesRegex(RuntimeError, 'bad input'):
                client.request('bad', {})
        finally:
            client.close()

    def test_timeout_reaps_child(self):
        client = gateway.Client([sys.executable, '-u', '-c', FAKE_SERVER], timeout=0.1)
        try:
            with self.assertRaises(TimeoutError):
                client.request('slow', {})
        finally:
            client.close()
        self.assertIsNotNone(client.process.poll())

    def test_copy_preserves_project_context_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'original'
            source.mkdir()
            for name in ('design.kicad_pro', 'design.kicad_pcb',
                         'design.kicad_sch', 'fp-lib-table', 'sym-lib-table'):
                (source / name).write_text(name)
            (source / 'Draft.pretty').mkdir()
            (source / 'Draft.pretty/part.kicad_mod').write_text('local footprint')
            before = gateway.hashes(source)
            trial = source / 'temp/pilot'
            gateway.prepare(source / 'design.kicad_pro', trial)
            self.assertEqual((trial / 'Draft.pretty/part.kicad_mod').read_text(), 'local footprint')
            with self.assertRaisesRegex(RuntimeError, 'already exists'):
                gateway.prepare(source / 'design.kicad_pro', trial)
            self.assertEqual(before, gateway.hashes(source))

    def test_copy_rejects_recursive_destination_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'original'
            source.mkdir()
            project = source / 'design.kicad_pro'
            for suffix in ('.kicad_pro', '.kicad_pcb', '.kicad_sch'):
                project.with_suffix(suffix).write_text('fixture')
            with self.assertRaisesRegex(RuntimeError, 'recursive'):
                gateway.prepare(project, source / 'nested/trial')
            (source / 'dependency').symlink_to(project)
            with self.assertRaisesRegex(RuntimeError, 'Symlink'):
                gateway.prepare(project)
            self.assertFalse((source / 'temp/konnect-pilot').exists())

    def test_probe_requires_live_requested_board(self):
        def response(payload):
            return {'isError': False, 'content': [{'type': 'text', 'text': json.dumps(payload)}]}
        self.assertFalse(gateway.probe_access(response({'ipc_available': False, 'requested_open': False})))
        self.assertFalse(gateway.probe_access(response({'ipc_available': True, 'requested_open': False})))
        self.assertTrue(gateway.probe_access(response({'ipc_available': True, 'requested_open': True})))
        self.assertFalse(gateway.probe_access({'content': [{'type': 'text', 'text': 'invalid'}]}))

    def test_archive_copies_only_binary_not_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / 'asset.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                for name, data in (('bin/konnect', b'binary'), ('../../unexpected', b'bad')):
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    tar.addfile(member, io.BytesIO(data))
            dest = Path(directory) / 'konnect'
            install.unpack_binary(archive, dest)
            self.assertEqual(dest.read_bytes(), b'binary')
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ['asset.tar.gz', 'konnect'])

    def test_asset_requires_digest_and_exact_release(self):
        asset = {'name': 'konnect-v0.13.0-x86_64-unknown-linux-gnu.tar.gz',
                 'browser_download_url': 'https://github.com/mixelpixx/Konnect/releases/download/v0.13.0/asset',
                 'digest': 'sha256:' + 'a' * 64}
        release = {'tag_name': 'v0.13.0', 'assets': [asset]}
        self.assertEqual(install.select_asset(release), asset)
        asset.pop('digest')
        with self.assertRaisesRegex(ValueError, 'digest'):
            install.select_asset(release)


if __name__ == '__main__':
    unittest.main()
