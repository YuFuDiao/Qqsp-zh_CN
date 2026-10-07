# -*- coding: utf-8 -*-
"""Emit an editable Qt Linguist .ts next to the generated .qm."""
import os
import sys
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qm as Q

src = os.path.join(HERE, 'out', 'Qqsp.zh_CN.qm')
dst = os.path.join(HERE, 'out', 'Qqsp.zh_CN.ts')

data = Q.parse(open(src, 'rb').read())
order = []
ctxs = {}
for ctx, s, cmt, tr in data.messages:
    if ctx not in ctxs:
        ctxs[ctx] = []
        order.append(ctx)
    ctxs[ctx].append((s, cmt, tr))

with open(dst, 'w', encoding='utf-8', newline='\n') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n')
    f.write('<TS version="2.1" language="%s">\n' % (data.language or 'zh_CN'))
    for ctx in order:
        f.write('<context>\n    <name>%s</name>\n' % escape(ctx))
        for s, cmt, tr in ctxs[ctx]:
            f.write('    <message>\n')
            if cmt:
                f.write('        <comment>%s</comment>\n' % escape(cmt))
            f.write('        <source>%s</source>\n' % escape(s))
            f.write('        <translation>%s</translation>\n' % escape(tr))
            f.write('    </message>\n')
        f.write('</context>\n')
    f.write('</TS>\n')
print('wrote', dst, '%d contexts, %d messages' % (len(order), len(data.messages)))
