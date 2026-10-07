# -*- coding: utf-8 -*-
"""Compile a Qt Linguist .ts file into a .qm (no Qt tooling required).

Usage: python ts2qm.py input.ts [output.qm]
"""
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qm as Q


def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + '.qm'
    root = ET.parse(src).getroot()
    language = root.get('language') or ''
    out = Q.QmFile()
    out.language = language.split('_')[0] if False else language
    n = skipped = 0
    for ctx in root.findall('context'):
        name = ctx.findtext('name') or ''
        for m in ctx.findall('message'):
            t = m.find('translation')
            if t is None or t.find('numerusform') is not None:
                skipped += 1
                continue
            if t.get('type') == 'unfinished':
                skipped += 1
                continue
            out.messages.append((name, m.findtext('source') or '',
                                 m.findtext('comment') or '', t.text or ''))
            n += 1
    data = Q.build(out)
    open(dst, 'wb').write(data)
    print('%s -> %s : %d messages (%d skipped), %d bytes' % (src, dst, n, skipped, len(data)))


if __name__ == '__main__':
    main()
