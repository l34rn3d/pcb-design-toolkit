#!/usr/bin/env python3
"""Validate distributable source and local Markdown links; optional forbidden-text scan."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = ('README.md', 'LICENSE', '.gitignore')
TOP_DIRS = ('skills', 'scripts', 'tests', 'docs', '.github')
ALLOWED_SUFFIXES = {'.md', '.py', '.sh', '.yaml', '.yml'}


def source_files():
    files = [ROOT / name for name in TOP_FILES]
    for directory in TOP_DIRS:
        for p in (ROOT / directory).rglob('*'):
            if '__pycache__' in p.parts or '.cache' in p.parts:
                continue
            if p.is_symlink():
                raise ValueError(f'Symlink is not distributable: {p.relative_to(ROOT)}')
            if p.is_file():
                if p.suffix not in ALLOWED_SUFFIXES and p.name != 'LICENSE':
                    raise ValueError(f'Unexpected package file: {p.relative_to(ROOT)}')
                files.append(p)
    return sorted(files)


def check(forbidden=()):
    files = source_files()
    for p in files:
        text = p.read_text(encoding='utf-8')
        for term in forbidden:
            if term.casefold() in text.casefold() or term.casefold() in str(p.relative_to(ROOT)).casefold():
                raise ValueError(f'Forbidden text in {p.relative_to(ROOT)}')
        if re.search(r'/home/[A-Za-z0-9_.-]+/', text):
            raise ValueError(f'User-specific absolute path in {p.relative_to(ROOT)}')
        if p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                path = target.split('#')[0]
                if path and not (p.parent / path).exists():
                    raise ValueError(f'Broken link in {p.relative_to(ROOT)}: {target}')
    skill = ROOT / 'skills/pcb-layout-engineer/SKILL.md'
    text = skill.read_text()
    if not text.startswith('---\nname: pcb-layout-engineer\ndescription: ') or '\n---\n' not in text[4:]:
        raise ValueError('Invalid skill frontmatter')
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--forbid', action='append', default=[])
    args = parser.parse_args()
    files = check(args.forbid)
    print(f'PASS: {len(files)} distributable files; skill metadata, paths and local links checked')
