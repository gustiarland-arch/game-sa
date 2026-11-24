#!/usr/bin/env python3
"""Tests ELF header parser on synthetic good/bad native libs; does not test real APK."""
import io
import struct
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from verify_native_16k_v30 import elf_load_alignments, verify

def elf64(align):
    data=bytearray(128); data[:4]=b'\x7fELF'; data[4]=2; data[5]=1
    struct.pack_into('<Q',data,32,64)
    struct.pack_into('<HH',data,54,56,1)
    struct.pack_into('<I',data,64,1)
    struct.pack_into('<Q',data,64+48,align)
    return bytes(data)

assert elf_load_alignments(elf64(16384)) == [16384]
assert elf_load_alignments(elf64(4096)) == [4096]
with TemporaryDirectory() as d:
    path=Path(d)/'valid.apk'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('lib/arm64-v8a/libgdx.so',elf64(16384))
    verify(path)
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('lib/arm64-v8a/libgdx.so',elf64(4096))
    try: verify(path)
    except RuntimeError as e: assert '16 KB' in str(e)
    else: raise AssertionError('4K ELF incorrectly accepted')
print('NATIVE 16 KB GATE: good accepted, 4 KB rejected; synthetic test OK')
