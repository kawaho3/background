#!/usr/bin/env python3
"""Restore a local Flower Friends example from a previously supplied archive.

The archive itself is not distributed by this repository. This only extracts
project files from an existing trusted local ZIP that the owner supplies.
"""
import argparse
import hashlib
import zipfile
from pathlib import Path

EXPECTED_SHA256 = '0b814dd830d5e37e2c898dd5283e137504c2b4b0599b6f14cc56b0c5c0adbcbe'
PREFIX = 'Flower_Friends_Project/'


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def restore(archive, target):
    if sha256(archive) != EXPECTED_SHA256:
        raise ValueError('Archive hash does not match the verified historical project zip')
    # Restore only known run assets; do NOT replace repository source code.
    permitted = ('assets/', 'work/')
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            if item.is_dir() or not item.filename.startswith(PREFIX):
                continue
            path = item.filename[len(PREFIX):]
            if not path.startswith(permitted):
                continue
            relative = Path(path)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe archive member path')
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            with z.open(item) as source, output.open('wb') as dest:
                while chunk := source.read(1024 * 1024):
                    dest.write(chunk)
            print('Restored', relative)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('--target', type=Path, default=Path(__file__).resolve().parent)
    args = p.parse_args()
    restore(args.archive, args.target)


if __name__ == '__main__':
    main()