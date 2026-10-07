import struct, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
import capstone
from capstone import *
from capstone.x86 import *

# Resolve the player build: $QQSP_EXE, then $QQSP_DIR\Qqsp.exe,
# then ..\original\Qqsp.exe, then a Qqsp.exe next to the scripts.
_HERE = os.path.dirname(os.path.abspath(__file__))


def _resolve_exe():
    if os.environ.get('QQSP_EXE'):
        return os.environ['QQSP_EXE']
    if os.environ.get('QQSP_DIR'):
        return os.path.join(os.environ['QQSP_DIR'], 'Qqsp.exe')
    cand = os.path.join(_HERE, os.pardir, 'original', 'Qqsp.exe')
    if os.path.isfile(cand):
        return os.path.abspath(cand)
    return os.path.join(_HERE, 'Qqsp.exe')


P = _resolve_exe()
b = open(P, 'rb').read()
e_lfanew = struct.unpack_from('<I', b, 0x3c)[0]
coff = e_lfanew + 4
nsec = struct.unpack_from('<H', b, coff + 2)[0]
optsz = struct.unpack_from('<H', b, coff + 16)[0]
opt = coff + 20
imgbase = struct.unpack_from('<Q', b, opt + 24)[0]
secs = []
so = opt + optsz
for i in range(nsec):
    name = b[so:so + 8].rstrip(b'\0').decode()
    vsize, vaddr, rawsize, rawptr = struct.unpack_from('<IIII', b, so + 8)
    secs.append((name, vaddr, vsize, rawptr, rawsize))
    so += 40
S = dict((s[0], s) for s in secs)


def off2va(off):
    for name, va, vs, rp, rs in secs:
        if rp <= off < rp + rs:
            return imgbase + va + (off - rp)


def va2off(va):
    r = va - imgbase
    for name, sva, vs, rp, rs in secs:
        if sva <= r < sva + max(vs, rs):
            return rp + (r - sva)


def rd_str(va, maxlen=200):
    o = va2off(va)
    if o is None:
        return None
    d = b[o:o + maxlen]
    z = d.find(b'\0')
    if z >= 0:
        d = d[:z]
    if len(d) < 1:
        return None
    try:
        return d.decode('utf-8')
    except Exception:
        return None


ddir = opt + 112
imp_rva, imp_sz = struct.unpack_from('<II', b, ddir + 8)
iat = {}
o = va2off(imgbase + imp_rva)
while True:
    oft, ts, fc, nmm, ft = struct.unpack_from('<IIIII', b, o)
    if nmm == 0 and ft == 0 and oft == 0:
        break
    dllname = rd_str(imgbase + nmm)
    thunk = oft or ft
    to = va2off(imgbase + thunk)
    k = 0
    while True:
        v = struct.unpack_from('<Q', b, to + k * 8)[0]
        if v == 0:
            break
        name = '%s.#%d' % (dllname, v & 0xffff) if (v & (1 << 63)) else rd_str(imgbase + v + 2)
        iat[imgbase + ft + k * 8] = name
        k += 1
    o += 20


def nm(va):
    for k in range(4):
        if va - k * 8 in iat:
            return iat[va - k * 8]
    return None


_, pva, pvs, prp, prs = S['.pdata']
funcs = []
for p in range(prp, prp + pvs, 12):
    st, en, uw = struct.unpack_from('<III', b, p)
    funcs.append((imgbase + st, imgbase + en))
funcs.sort()
_, tva, tvs, trp, trs = S['.text']
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True


def func_of(va):
    for st, en in funcs:
        if st <= va < en:
            return (st, en)
    return None


def find_str(s):
    t = s.encode()
    out = []
    st = 0
    while True:
        i = b.find(t, st)
        if i < 0:
            break
        out.append(off2va(i))
        st = i + 1
    return out


def xrefs_to(va):
    res = []
    for p in range(trp, trp + trs - 4):
        d = struct.unpack_from('<i', b, p)[0]
        if off2va(p) + 4 + d == va:
            res.append(off2va(p))
    return res


def dump(va_start, va_end=None, out=sys.stdout):
    f = func_of(va_start)
    st, en = f if f else (va_start, va_start + 4000)
    if va_end:
        en = va_end
    o = va2off(st)
    data = b[o:o + (en - st)]
    for i in md.disasm(data, st):
        note = ''
        if i.mnemonic == 'call':
            for op in i.operands:
                if op.type == CS_OP_MEM and op.mem.base == X86_REG_RIP:
                    t = i.address + i.size + op.mem.disp
                    r = nm(t)
                    note = '   ; CALL ' + (r if r else hex(t))
        if not note:
            for op in i.operands:
                if op.type == CS_OP_MEM and op.mem.base == X86_REG_RIP:
                    t = i.address + i.size + op.mem.disp
                    r = iat.get(t)
                    s = rd_str(t)
                    if r:
                        note = '   ; ' + r
                    elif s:
                        note = '   ; "%s"' % s
        out.write('%#010x  %s %s%s\n' % (i.address, i.mnemonic, i.op_str, note))


if __name__ == '__main__':
    which = int(sys.argv[1], 16)
    if which < imgbase:
        which += imgbase
    dump(which)
