import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qpe import *

start = int(sys.argv[1], 16)
end = int(sys.argv[2], 16)
if start < imgbase:
    start += imgbase
if end < imgbase:
    end += imgbase
o = va2off(start)
data = b[o:o + (end - start)]
for i in md.disasm(data, start):
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
    print('%#010x  %s %s%s' % (i.address, i.mnemonic, i.op_str, note))
