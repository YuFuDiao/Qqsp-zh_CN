import struct
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qqsp.exe')
b=open(P,'rb').read()
e_lfanew=struct.unpack_from('<I',b,0x3c)[0]; coff=e_lfanew+4
nsec=struct.unpack_from('<H',b,coff+2)[0]; optsz=struct.unpack_from('<H',b,coff+16)[0]; opt=coff+20
imgbase=struct.unpack_from('<Q',b,opt+24)[0]
secs=[]; so=opt+optsz
for i in range(nsec):
    name=b[so:so+8].rstrip(b'\0').decode(); vsize,vaddr,rawsize,rawptr=struct.unpack_from('<IIII',b,so+8)
    secs.append((name,vaddr,vsize,rawptr,rawsize)); so+=40
def toVA(rva): return imgbase+rva
text=[s for s in secs if s[0]=='.text'][0]
_,tva,tvs,trp,trs=text
tstart,tend=trp,trp+trs
targets={':/translations/':0x14004a530,'custom.ini':0x14004a500,'application/language':0x14004a510,'qqsp.ini':0x14004bf58}
res={k:[] for k in targets}
for p in range(tstart,tend-4):
    d=struct.unpack_from('<i',b,p)[0]
    va=toVA(tva+(p-tstart))+4+d
    for k,t in targets.items():
        if va==t:
            res[k].append(p)
for k,v in res.items():
    print('==',k,[hex(x) for x in v])
    for p in v:
        print('   ctx:',b[p-8:p+4].hex(' '))
