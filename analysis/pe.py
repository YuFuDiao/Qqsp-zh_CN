import struct, sys
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qqsp.exe')
b=open(P,'rb').read()
# --- PE parse ---
e_lfanew=struct.unpack_from('<I',b,0x3c)[0]
assert b[e_lfanew:e_lfanew+4]==b'PE\0\0'
coff=e_lfanew+4
nsec=struct.unpack_from('<H',b,coff+2)[0]
optsz=struct.unpack_from('<H',b,coff+16)[0]
opt=coff+20
magic=struct.unpack_from('<H',b,opt)[0]
imgbase=struct.unpack_from('<Q',b,opt+24)[0] if magic==0x20b else struct.unpack_from('<I',b,opt+28)[0]
print('machine',hex(struct.unpack_from('<H',b,coff)[0]),'sections',nsec,'imagebase',hex(imgbase),'optmagic',hex(magic))
secs=[]
so=opt+optsz
for i in range(nsec):
    name=b[so:so+8].rstrip(b'\0').decode()
    vsize,vaddr,rawsize,rawptr=struct.unpack_from('<IIII',b,so+8)
    secs.append((name,vaddr,vsize,rawptr,rawsize))
    print(f'{name:10s} VA={imgbase+vaddr:#x} vsize={vsize:#x} raw={rawptr:#x} rawsize={rawsize:#x}')
    so+=40
def off2va(off):
    for name,va,vs,rp,rs in secs:
        if rp<=off<rp+rs: return imgbase+va+(off-rp)
    return None
def va2off(va):
    r=va-imgbase
    for name,sva,vs,rp,rs in secs:
        if sva<=r<sva+max(vs,rs): return rp+(r-sva)
    return None

# --- find strings ---
targets=[b':/translations/',b'custom.ini',b'application/language',b'qqsp.ini',b'Language']
for t in targets:
    i=0
    while True:
        i=b.find(t,i)
        if i<0: break
        print('str',t,'off',i,'va',hex(off2va(i)) if off2va(i) else None)
        i+=1
