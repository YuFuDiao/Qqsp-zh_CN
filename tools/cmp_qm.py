import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qm as Q

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'Qqsp.ru.qm')
data = open(p, 'rb').read()
o = 16
blocks = []
while o + 5 <= len(data):
    tag = data[o]
    ln = Q._read32(data, o + 1)
    o += 5
    if tag == 0 or ln == 0:
        break
    blocks.append((tag, ln, data[o:o + ln]))
    o += ln
print('original blocks:')
for t, ln, _ in blocks:
    print('  tag %#x len %d' % (t, ln))
parsed = Q.parse(data)
out = Q.build(parsed)
o = 16
print('rebuilt blocks:')
while o + 5 <= len(out):
    tag = out[o]
    ln = Q._read32(out, o + 1)
    o += 5
    if tag == 0 or ln == 0:
        break
    print('  tag %#x len %d' % (tag, ln))
    o += ln

# compare contexts blocks
def blk(d, want):
    o = 16
    while o + 5 <= len(d):
        tag = d[o]; ln = Q._read32(d, o + 1); o += 5
        if tag == want:
            return d[o:o + ln]
        o += ln
a = blk(data, Q.TAG_CONTEXTS)
b = blk(out, Q.TAG_CONTEXTS)
print('ctx orig len %d rebuilt %d' % (len(a), len(b)))
print('orig ctx hex:', a.hex())
print('new  ctx hex:', b.hex())
# hash blocks
ha = blk(data, Q.TAG_HASHES)
hb = blk(out, Q.TAG_HASHES)
print('hash orig len %d rebuilt %d identical=%s' % (len(ha), len(hb), ha == hb))
for i in range(0, min(len(ha), len(hb)), 8):
    h1, o1 = struct.unpack_from('>II', ha, i)
    h2, o2 = struct.unpack_from('>II', hb, i)
    if (h1, o1) != (h2, o2):
        print('  first hash diff at entry %d: orig %08x/%d new %08x/%d' % (i // 8, h1, o1, h2, o2))
        break
