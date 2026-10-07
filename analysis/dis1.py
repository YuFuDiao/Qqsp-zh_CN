import struct,sys,os
if os.path.isdir('pylibs'):
    sys.path.insert(0, 'pylibs')
import capstone
from capstone import *
from capstone.x86 import *
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qqsp.exe')
b=open(P,'rb').read()
e_lfanew=struct.unpack_from('<I',b,0x3c)[0]; coff=e_lfanew+4
nsec=struct.unpack_from('<H',b,coff+2)[0]; optsz=struct.unpack_from('<H',b,coff+16)[0]; opt=coff+20
imgbase=struct.unpack_from('<Q',b,opt+24)[0]
secs=[]; so=opt+optsz
for i in range(nsec):
    name=b[so:so+8].rstrip(b'\0').decode(); vsize,vaddr,rawsize,rawptr=struct.unpack_from('<IIII',b,so+8)
    secs.append((name,vaddr,vsize,rawptr,rawsize)); so+=40
S=dict((s[0],s) for s in secs)
def off2va(off):
    for name,va,vs,rp,rs in secs:
        if rp<=off<rp+rs: return imgbase+va+(off-rp)
def va2off(va):
    r=va-imgbase
    for name,sva,vs,rp,rs in secs:
        if sva<=r<sva+max(vs,rs): return rp+(r-sva)
def rd_str(va,maxlen=120):
    o=va2off(va)
    if o is None: return None
    d=b[o:o+maxlen]; z=d.find(b'\0')
    if z>=0: d=d[:z]
    if len(d)<2: return None
    try: return d.decode('utf-8')
    except: return None
# pdata functions
_,pva,pvs,prp,prs=S['.pdata']
funcs=[]
for p in range(prp,prp+pvs,12):
    st,en,uw=struct.unpack_from('<III',b,p)
    funcs.append((imgbase+st,imgbase+en))
funcs.sort()
print('num funcs',len(funcs))
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
def show(off_before,count=200):
    va=off2va(off_before)
    f=None
    for st,en in funcs:
        if st<=va<en: f=(st,en); break
    print('containing func:',[hex(x) for x in f] if f else None)
    if not f: return
    st,en=f
    o=va2off(st); data=b[o:o+(en-st)]
    for i in md.disasm(data,st):
        note=''
        for op in i.operands:
            if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:
                t=i.address+i.size+op.mem.disp
                s=rd_str(t)
                note=f'   ; "{s}"' if s else f'   ; {t:#x}'
        print(f'{i.address:#010x}  {i.bytes.hex(" "):<26s} {i.mnemonic} {i.op_str}{note}')
print('########## A: :/translations/ (file off 0xdc8) ##########')
show(0xdc8)
