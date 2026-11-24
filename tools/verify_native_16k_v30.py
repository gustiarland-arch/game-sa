#!/usr/bin/env python3
"""Gate for APK native .so ELF load segment alignment (NOT a runtime/Play certification)."""
import struct
import sys
import zipfile
from pathlib import Path

def elf_load_alignments(data):
    if data[:4] != b'\x7fELF' or len(data) < 64:
        raise ValueError('Bukan ELF valid')
    bits, endian = data[4], data[5]
    if bits not in (1, 2) or endian not in (1, 2):
        raise ValueError('Unsupported ELF format')
    order = '<' if endian == 1 else '>'
    if bits == 2:
        phoff, = struct.unpack_from(order + 'Q', data, 32)
        entsize, count = struct.unpack_from(order + 'HH', data, 54)
        align_offset, align_format, size = 48, 'Q', 56
    else:
        phoff, = struct.unpack_from(order + 'I', data, 28)
        entsize, count = struct.unpack_from(order + 'HH', data, 42)
        align_offset, align_format, size = 28, 'I', 32
    if count == 0 or entsize < size or phoff + entsize * count > len(data):
        raise ValueError('ELF header program table tidak valid')
    found = []
    for i in range(count):
        off = phoff + entsize * i
        typ, = struct.unpack_from(order + 'I', data, off)
        if typ == 1:
            align, = struct.unpack_from(order + align_format, data, off + align_offset)
            found.append(align)
    if not found:
        raise ValueError('ELF tanpa PT_LOAD')
    return found

def verify(apk):
    with zipfile.ZipFile(apk) as z:
        libs = [name for name in z.namelist() if name.startswith('lib/') and name.endswith('.so')]
        if not libs:
            raise RuntimeError('Tidak ada native lib di APK; periksa packaging LibGDX')
        failures = []
        for lib in libs:
            aligns = elf_load_alignments(z.read(lib))
            if any(align < 16384 or align % 16384 != 0 for align in aligns):
                failures.append(f'{lib}: PT_LOAD p_align={aligns}')
        if failures:
            raise RuntimeError('Native 16 KB alignment TIDAK lulus:\n' + '\n'.join(failures))
        print(f'Native 16 KB ELF: {len(libs)} .so verified (zipalign and device test still required)')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: verify_native_16k_v30.py PATH_TO_APK', file=sys.stderr)
        sys.exit(2)
    try: verify(Path(sys.argv[1]))
    except (ValueError, RuntimeError, OSError, zipfile.BadZipFile) as error:
        print(f'BLOCK RELEASE: {error}', file=sys.stderr)
        sys.exit(1)
