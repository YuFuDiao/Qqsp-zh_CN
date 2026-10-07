# -*- coding: utf-8 -*-
"""Extract every QCoreApplication::translate()/qt_tr call from Qqsp.exe and
diff it against our .qm, so nothing translatable is missed."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qpe
from qpe import b, md, imgbase, va2off, rd_str, iat, funcs
from capstone import CS_OP_MEM, CS_OP_REG
from capstone.x86 import X86_REG_RIP, X86_REG_RDX, X86_REG_R8
import qm as Q

CALLS = set()
for va, name in iat.items():
    if not name:
        continue
    if '?translate@QCoreApplication@@' in name or 'qt_tr' in name or '?tr@QObject@@' in name:
        CALLS.add(va)
print('translate-like import slots:', len(CALLS))

found = {}
for st, en in funcs:
    o = va2off(st)
    if o is None:
        continue
    last = {}
    for ins in md.disasm(b[o:o + (en - st)], st):
        if ins.mnemonic == 'lea' and len(ins.operands) == 2:
            dst, src = ins.operands
            if dst.type == CS_OP_REG and src.type == CS_OP_MEM and src.mem.base == X86_REG_RIP:
                t = ins.address + ins.size + src.mem.disp
                last[dst.reg] = rd_str(t, 300)
        elif ins.mnemonic == 'xor' and ins.op_str.endswith(', edx'):
            last.pop(X86_REG_RDX, None)
            last.pop(X86_REG_R8, None)
        if ins.mnemonic != 'call' or not ins.operands:
            continue
        op = ins.operands[0]
        if op.type != CS_OP_MEM or op.mem.base != X86_REG_RIP:
            continue
        if ins.address + ins.size + op.mem.disp not in CALLS:
            continue
        ctx = last.get(X86_REG_RDX)
        src = last.get(X86_REG_R8)
        if ctx and src and len(ctx) < 60 and len(src) < 300:
            key = (ctx, src)
            found[key] = found.get(key, 0) + 1
        last = {}

print('distinct (context, source) pairs found in code:', len(found))
qm = Q.parse(open(os.path.join(HERE, 'out', 'Qqsp.zh_CN.qm'), 'rb').read())
have = set((c, s) for c, s, cm, t in qm.messages)
missing = [(c, s, n) for (c, s), n in sorted(found.items()) if (c, s) not in have]
print('\n--- translatable but NOT in our .qm ---')
for ctx, src, n in missing:
    print('   [%s] %r  (%d site(s))' % (ctx, src, n))
print('total missing:', len(missing))
extra = [x for x in have if x not in found]
print('\nin .qm but no direct call site found: %d (Qt standard-dialog contexts + ui lookups)' % len(extra))
