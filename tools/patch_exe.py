# -*- coding: utf-8 -*-
"""Patch Qqsp.exe in place: the window title is a compile-time constant
(`setWindowTitle(QSP_LOGO)`) that no .qm file can translate.

The literal "Qt Quest Soft Player" sits in .rdata and is turned into a QString
at runtime through QString::fromAscii_helper(ptr, 20) -- the length 20 is baked
into the instruction, so the replacement must be exactly 20 UTF-8 bytes.
"QSP·小说播放器" is exactly 20 bytes.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qqsp.exe')
OUT = os.path.join(HERE, 'out', 'Qqsp.exe')

OLD = b'Qt Quest Soft Player'
NEW = 'QSP·小说播放器'.encode('utf-8')
assert len(OLD) == 20 and len(NEW) == 20, (len(OLD), len(NEW))

data = bytearray(open(EXE, 'rb').read())
off = data.find(OLD)
assert off > 0, 'title literal not found'
assert data.find(OLD, off + 1) < 0, 'title literal is not unique'
print('patching file offset %#x (VA %#x)' % (off, 0x140048000 - 0x46800 + off))
data[off:off + 20] = NEW

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(bytes(data))
print('wrote', OUT, len(data))
print('orig sha256', hashlib.sha256(open(EXE, 'rb').read()).hexdigest())
print('new  sha256', hashlib.sha256(bytes(data)).hexdigest())
