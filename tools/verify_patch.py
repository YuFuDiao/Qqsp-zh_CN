# -*- coding: utf-8 -*-
"""Verify out/Qqsp.exe against the pristine backup."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qpe
from qpe import imgbase, off2va, va2off
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

ORIG = (os.environ.get('QQSP_BAK') or os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qqsp.exe'))
NEW = os.path.join(HERE, 'out', 'Qqsp.exe')

a = open(ORIG, 'rb').read()
b = open(NEW, 'rb').read()
print('sizes equal:', len(a) == len(b))
assert len(a) == len(b)

diff = [i for i in range(len(a)) if a[i] != b[i]]
# group into runs
runs = []
for i in diff:
    if runs and i == runs[-1][1] + 1:
        runs[-1][1] = i
    else:
        runs.append([i, i])
print('changed bytes: %d in %d runs' % (len(diff), len(runs)))

md = Cs(CS_ARCH_X86, CS_MODE_64)
# the 8 length-immediate sites (lea_addr - 5) found earlier
sites = [0x140009010, 0x140041da5, 0x14000918a, 0x140041f1f,
         0x140008fbd, 0x140041d52, 0x140008fde, 0x140041d73]
print('\nlength immediates after patching:')
for lea in sites:
    o = va2off(lea - 5)
    data = b[o:o + 12]
    txt = []
    for i in md.disasm(data, lea - 5):
        txt.append('%s %s' % (i.mnemonic, i.op_str))
        if len(txt) == 2:
            break
    reg = a[o + 1]
    print('  %#x  %s   (was edx=%d)' % (lea - 5, ' | '.join(txt), a[o + 1] | (a[o + 2] << 8)))

print('\nliteral sanity (new exe):')
for s in ['QSP·小说播放器', '位置: %1', '代码: %1', '访问时', '动作时']:
    enc = s.encode('utf-8')
    i = b.find(enc)
    print('  %-16r at file+%#x  NUL-terminated: %s' % (s, i, b[i + len(enc)] == 0))
for s in ['除以零', '参数个数不正确', '未找到括号']:
    enc = s.encode('utf-16-le')
    i = b.find(enc)
    print('  %-16r at file+%#x  wide-NUL-terminated: %s' % (s, i, b[i + len(enc):i + len(enc) + 2] == b'\x00\x00'))

# unchanged regions check: PE headers and section table untouched
print('\nfirst 0x1000 bytes identical:', a[:0x1000] == b[:0x1000])
