"""Minimal Qt .qm (Qt Linguist binary) reader/writer.

Format (Qt 5 / Qt 6):
  16-byte magic
  repeated blocks: u8 tag, u32be length, payload
    tag 0x2f Contexts, 0x42 Hashes, 0x69 Messages, 0x88 NumerusRules,
        0x96 Dependencies, 0xa7 Language
Message block payload: sequence of records, each:
    tag 0x07 Context   : u32be len, bytes
    tag 0x06 SourceText: u32be len, bytes
    tag 0x08 Comment   : u32be len, bytes
    tag 0x03 Translation: u32be len, UTF-16BE bytes
    tag 0x01 End
Hashes block: N * (u32be hash, u32be offset-in-message-block)
Contexts block: u16be hTableSize, hTableSize*u16be bucket offsets (in u16 units
    from start of the string area), then per-context records: u8 len, bytes.
"""
import struct

MAGIC = bytes([0x3c, 0xb8, 0x64, 0x18, 0xca, 0xef, 0x9c, 0x95,
               0xcd, 0x21, 0x1c, 0xbf, 0x60, 0xa1, 0xbd, 0xdd])
TAG_CONTEXTS = 0x2f
TAG_HASHES = 0x42
TAG_MESSAGES = 0x69
TAG_NUMERUS = 0x88
TAG_DEPENDENCIES = 0x96
TAG_LANGUAGE = 0xa7

T_END = 1
T_SOURCETEXT16 = 2
T_TRANSLATION = 3
T_CONTEXT16 = 4
T_OBSOLETE1 = 5
T_SOURCETEXT = 6
T_CONTEXT = 7
T_COMMENT = 8
T_OBSOLETE2 = 9


def elf_hash(name):
    h = 0
    if isinstance(name, str):
        name = name.encode('utf-8')
    for c in name:
        h = (h << 4) + c
        g = h & 0xf0000000
        if g:
            h ^= g >> 24
        h &= ~g & 0xffffffff
    if not h:
        h = 1
    return h


class QmFile:
    def __init__(self):
        self.language = None
        # list of (context, source, comment, translation)
        self.messages = []
        self.numerus = b''
        self.dependencies = []


def _read32(b, o):
    return struct.unpack_from('>I', b, o)[0]


def parse(data):
    if data[:16] != MAGIC:
        raise ValueError('bad qm magic')
    qm = QmFile()
    o = 16
    blocks = {}
    while o + 5 <= len(data):
        tag = data[o]
        ln = _read32(data, o + 1)
        o += 5
        if tag == 0 or ln == 0:
            break
        payload = data[o:o + ln]
        o += ln
        blocks[tag] = payload
    if TAG_LANGUAGE in blocks:
        qm.language = blocks[TAG_LANGUAGE].decode('utf-8')
    msgs = blocks.get(TAG_MESSAGES, b'')
    m = 0
    while m < len(msgs):
        ctx = src = cmt = tr = None
        while m < len(msgs):
            tag = msgs[m]
            m += 1
            if tag == T_END:
                break
            if tag == T_TRANSLATION:
                ln = _read32(msgs, m); m += 4
                if tr is None:
                    tr = msgs[m:m + ln].decode('utf-16-be')
                m += ln
            elif tag in (T_SOURCETEXT, T_CONTEXT, T_COMMENT):
                ln = _read32(msgs, m); m += 4
                v = msgs[m:m + ln].decode('utf-8')
                if v.endswith('\x00'):
                    v = v[:-1]
                if tag == T_SOURCETEXT:
                    src = v
                elif tag == T_CONTEXT:
                    ctx = v
                else:
                    cmt = v
                m += ln
            elif tag == T_OBSOLETE1:
                m += 4
            else:
                raise ValueError('unknown message tag %d' % tag)
        if ctx is not None or src is not None:
            qm.messages.append((ctx or '', src or '', cmt or '', tr if tr is not None else ''))
    return qm


def _pack_bytes(b):
    return struct.pack('>I', len(b)) + b


def build(qm):
    """Serialise a QmFile.  Returns bytes.

    Framing matches Qt's lrelease: per record
      Translation(3), Comment(8, always emitted), SourceText(6), Context(7), End(1)
    with byte lengths and no NUL terminators.  The Contexts block is omitted on
    purpose: QTranslator skips the context hash check when it is absent and
    still verifies the context from each record.
    """
    # ---- messages block ----
    msgs = bytearray()
    offsets = []          # parallel to qm.messages: offset in msgs
    for ctx, src, cmt, tr in qm.messages:
        offsets.append(len(msgs))
        msgs.append(T_TRANSLATION)
        msgs += _pack_bytes(tr.encode('utf-16-be'))
        msgs.append(T_COMMENT)
        msgs += _pack_bytes(cmt.encode('utf-8'))
        msgs.append(T_SOURCETEXT)
        msgs += _pack_bytes(src.encode('utf-8'))
        msgs.append(T_CONTEXT)
        msgs += _pack_bytes(ctx.encode('utf-8'))
        msgs.append(T_END)
    messages_block = bytes(msgs)

    # ---- hashes block: sorted by hash, then keep insertion order stable ----
    entries = []
    for i, (ctx, src, cmt, tr) in enumerate(qm.messages):
        h = 0
        h = elf_hash_add(h, src)
        if cmt:
            h = elf_hash_add(h, cmt)
        h = elf_hash_finish(h)
        entries.append((h, offsets[i], i))
    entries.sort(key=lambda e: (e[0], e[2]))
    hashes_block = b''.join(struct.pack('>II', h, off) for h, off, _ in entries)

    # ---- contexts block ----
    ctx_order = []
    ctx_index = {}
    for ctx, src, cmt, tr in qm.messages:
        if ctx not in ctx_index:
            ctx_index[ctx] = len(ctx_order)
            ctx_order.append(ctx)
    nhash = 1
    while nhash < len(ctx_order) * 2:
        nhash <<= 1
    # bucket -> list of context indices, chains must be contiguous in storage
    buckets = [[] for _ in range(nhash)]
    for i, ctx in enumerate(ctx_order):
        buckets[elf_hash(ctx) % nhash].append(i)
    # storage order: bucket 0's contexts, then bucket 1's, ...
    storage = []
    for b in buckets:
        storage.extend(b)
    pos_in_storage = {}
    strings = bytearray()
    bucket_offset = [0] * nhash
    for bi, b in enumerate(buckets):
        if not b:
            bucket_offset[bi] = 0
            continue
        bucket_offset[bi] = len(strings) // 2
        for ci in b:
            ctx = ctx_order[ci]
            cb = ctx.encode('utf-8')
            strings.append(len(cb))
            strings += cb
        strings.append(0)   # terminator for the chain
    # u16 padding
    if len(strings) % 2:
        strings.append(0)
    hdr = struct.pack('>H', nhash) + b''.join(struct.pack('>H', x) for x in bucket_offset)
    contexts_block = hdr + bytes(strings)

    out = bytearray(MAGIC)
    if qm.language:
        lb = qm.language.encode('utf-8')
        out.append(TAG_LANGUAGE)
        out += struct.pack('>I', len(lb)) + lb
    for tag, payload in ((TAG_HASHES, hashes_block),
                         (TAG_MESSAGES, messages_block)):
        out.append(tag)
        out += struct.pack('>I', len(payload))
        out += payload
    return bytes(out)


def elf_hash_add(h, name):
    if isinstance(name, str):
        name = name.encode('utf-8')
    for c in name:
        h = (h << 4) + c
        g = h & 0xf0000000
        if g:
            h ^= g >> 24
        h &= ~g & 0xffffffff
    return h


def elf_hash_finish(h):
    if not h:
        h = 1
    return h


if __name__ == '__main__':
    import sys
    p = sys.argv[1]
    data = open(p, 'rb').read()
    qm = parse(data)
    print('file %s size %d language=%r messages=%d' % (p, len(data), qm.language, len(qm.messages)))
    for ctx, src, cmt, tr in qm.messages:
        print('  [%s] %r -> %r' % (ctx, src, tr))
    if len(sys.argv) > 2 and sys.argv[2] == 'roundtrip':
        out = build(qm)
        print('rebuilt size %d, identical=%s' % (len(out), out == data))
        if out != data:
            open(p + '.rebuilt', 'wb').write(out)
