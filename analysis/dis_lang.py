import struct,sys,os
if os.path.isdir('pylibs'):
    sys.path.insert(0, 'pylibs')
import capstone
from capstone import *
from capstone.x86 import *
exec(open(os.path.join(QSP_ROOT, 'x3.py')).read().split("for s in [")[0])
def dump(va_start,va_end=None,limit=100000):
    f=func_of(va_start)
    st,en=f if f else (va_start,va_start+4000)
    if va_end: en=va_end
    o=va2off(st); data=b[o:o+(en-st)]
    for i in md.disasm(data,st):
        note=''
        if i.mnemonic=='call':
            for op in i.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:
                    t=i.address+i.size+op.mem.disp
                    r=nm(t)
                    note='   ; CALL '+ (r if r else hex(t))
        if not note:
            for op in i.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:
                    t=i.address+i.size+op.mem.disp
                    r=iat.get(t); s=rd_str(t)
                    if r: note=f'   ; {r}'
                    elif s: note=f'   ; "{s}"'
        print(f'{i.address:#010x}  {i.mnemonic} {i.op_str}{note}')
print('#################### func 0x14000fe20 (__LANGNAME__/__LANGID__ scanner) ####################')
dump(0x14000fe20)
