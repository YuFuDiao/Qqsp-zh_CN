import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qm as Q

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'Qqsp.ru.qm')
data = open(p, 'rb').read()
o = 16
while o + 5 <= len(data):
    tag = data[o]; ln = Q._read32(data, o + 1); o += 5
    if tag == Q.TAG_MESSAGES:
        msgs = data[o:o + ln]
        break
    o += ln

print('messages block len', len(msgs))
m = 0
rec = 0
while m < len(msgs) and rec < 6:
    print('--- record %d at %d' % (rec, m))
    while m < len(msgs):
        tag = msgs[m]; m += 1
        if tag == Q.T_END:
            print('   END')
            break
        ln = struct.unpack_from('>I', msgs, m)[0]; m += 4
        payload = msgs[m:m + ln]; m += ln
        kind = {Q.T_CONTEXT: 'CTX', Q.T_SOURCETEXT: 'SRC', Q.T_TRANSLATION: 'TR', Q.T_COMMENT: 'CMT'}.get(tag, 'T%d' % tag)
        try:
            show = payload.decode('utf-16-be') if tag == Q.T_TRANSLATION else payload.decode('utf-8')
        except Exception:
            show = payload.hex()
        print('   tag %#x %s len %d %r  (tail bytes: %s)' % (tag, kind, ln, show[:40], payload[-3:].hex()))
    rec += 1
