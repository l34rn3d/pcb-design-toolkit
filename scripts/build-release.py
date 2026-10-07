#!/usr/bin/env python3
"""Build source and self-contained skill ZIPs from an explicit source allowlist."""
import hashlib
import importlib.util
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_check', ROOT / 'scripts/check-package.py')
package_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_check)


def archive(path, entries):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as output:
        for source, name in entries:
            output.write(source, name)
    with zipfile.ZipFile(path) as output:
        if output.testzip() is not None:
            raise ValueError('Archive CRC check failed')
        for source, name in entries:
            if output.read(name) != source.read_bytes():
                raise ValueError(f'Archive content mismatch: {name}')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    files = package_check.check()
    dest = ROOT / 'dist'
    dest.mkdir(exist_ok=True)
    skill_parent = ROOT / 'skills'
    toolkit = [(p, 'pcb-design-toolkit/' + str(p.relative_to(ROOT))) for p in files]
    skill = [(p, str(p.relative_to(skill_parent))) for p in files if skill_parent in p.parents]
    hashes = []
    for name, entries in [('pcb-design-toolkit.zip', toolkit), ('pcb-layout-engineer.zip', skill)]:
        digest = archive(dest / name, entries)
        hashes.append(f'{digest}  {name}')
        print(f'Created {name}: {len(entries)} files')
    (dest / 'SHA256SUMS').write_text('\n'.join(hashes) + '\n')


if __name__ == '__main__':
    main()
