import struct, sys, io
f=os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qqsp.exe')
b=open(f,'rb').read()
MAGIC=bytes([0x3c,0xb8,0x64,0x18,0xca,0xef,0x9c,0x95,0xcd,0x21,0x1c,0xbf,0x60])
offs=[]
i=0
while True:
    i=b.find(MAGIC,i)
    if i<0: break
    offs.append(i); i+=1
print('magic offsets',offs)
for st in offs:
    d=b[st:st+200000]
    # header
    print('=== blob at',st, 'header bytes:', d[:32].hex())
    vs=d[16]
    print('version byte',hex(vs))
    p=17
    endian='>'
    try:
        secs=[]
        for k in range(5):
            ln=struct.unpack_from('>I',d,p)[0]; of=struct.unpack_from('>I',d,p+4)[0]
            secs.append((ln,of)); p+=8
        print('secs',secs)
        total=max(o+l for l,o in secs)
        print('total size',total)
        # dump messages section
        ln,of=secs[2]
        msgs=d[of:of+ln]
        print('messages section len',ln)
        s=msgs.decode('utf-16-be',errors='replace')
        print('--- msgs head ---')
        print(s[:3000])
    except Exception as e:
        print('parse err',e)
