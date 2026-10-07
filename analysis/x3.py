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
def rd_str(va,maxlen=200):
    o=va2off(va)
    if o is None: return None
    d=b[o:o+maxlen]; z=d.find(b'\0')
    if z>=0: d=d[:z]
    if len(d)<1: return None
    try: return d.decode('utf-8')
    except: return None
ddir=opt+112
imp_rva,imp_sz=struct.unpack_from('<II',b,ddir+8)
iat={}
o=va2off(imgbase+imp_rva)
while True:
    oft,ts,fc,nm,ft=struct.unpack_from('<IIIII',b,o)
    if nm==0 and ft==0 and oft==0: break
    dllname=rd_str(imgbase+nm); thunk=oft or ft
    to=va2off(imgbase+thunk); k=0
    while True:
        v=struct.unpack_from('<Q',b,to+k*8)[0]
        if v==0: break
        name=f'{dllname}.#{v&0xffff}' if (v&(1<<63)) else rd_str(imgbase+v+2)
        iat[imgbase+ft+k*8]=name; k+=1
    o+=20
def nm(va):
    for k in range(4):
        if va-k*8 in iat: return iat[va-k*8]
_,pva,pvs,prp,prs=S['.pdata']
funcs=[]
for p in range(prp,prp+pvs,12):
    st,en,uw=struct.unpack_from('<III',b,p); funcs.append((imgbase+st,imgbase+en))
funcs.sort()
_,tva,tvs,trp,trs=S['.text']
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
def find_str(s):
    t=s.encode(); out=[]
    st=0
    while True:
        i=b.find(t,st)
        if i<0: break
        out.append(off2va(i)); st=i+1
    return out
def xrefs_to(va):
    res=[]
    for p in range(trp,trp+trs-4):
        d=struct.unpack_from('<i',b,p)[0]
        if off2va(p)+4+d==va: res.append(off2va(p))
    return res
def func_of(va):
    for st,en in funcs:
        if st<=va<en: return (st,en)
    return None
for s in ['__LANGNAME__','__LANGID__','application/language']:
    print('#### ',s)
    for va in find_str(s):
        line=rd_str(va,40)
        if line!=s: continue
        xs=xrefs_to(va)
        print('  str at',hex(va),'xrefs:',[hex(x) for x in xs])
        for x in xs:
            f=func_of(x)
            print('     in func',hex(f[0]) if f else None, 'delta',hex(x-f[0]) if f else '')
