# -*- coding: utf-8 -*-
"""Sweep the exe for user-visible literals that are NOT covered by our .qm."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qm as Q

exe_full = open((os.environ.get('QQSP_BAK') or os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qqsp.exe')), 'rb').read()
# only .rdata (where literals live) - avoids disassembly noise from .text
exe = exe_full[0x46800:0x46800 + 0x51200]
qm = Q.parse(open(os.path.join(HERE, 'out', 'Qqsp.zh_CN.qm'), 'rb').read())
sources = set()
for ctx, src, cmt, tr in qm.messages:
    sources.add(src)
    sources.add(tr)

# --- ASCII literals ---
strs = []
sb = bytearray()
for x in exe:
    if 32 <= x < 127:
        sb.append(x)
    else:
        if len(sb) >= 4:
            strs.append(sb.decode('ascii'))
        sb = bytearray()
# --- UTF-16LE literals ---
u = []
sb = bytearray()
i = 0
while i < len(exe) - 1:
    lo, hi = exe[i], exe[i + 1]
    if hi == 0 and 32 <= lo < 127:
        sb.append(lo)
        i += 2
        continue
    if len(sb) >= 5:
        u.append(sb.decode('ascii'))
    sb = bytearray()
    i += 2

skip_patterns = [
    r'@', r'^[?._]', r'\.dll$', r'^\*', r'^[\W_]+$', r'^\{', r'^static const',
    r'^[A-Za-z0-9_/\\:.\-]+$',                 # single tokens / paths
    r'^[a-z]+[A-Z]',                           # camelCase API names
    r'^(QW|Q)[A-Za-z]+',                       # Qt class / method names
    r'^[A-Za-z_]+\([A-Za-z\*\)]',              # signatures
    r'^(false|true|null|endif|ifdef)', r'xpm\[\]', r'^\d',
    r'<[/!]?(table|tr|td|h2|p|video|br|center|html|body|img|a)\b',
    r'^(background|font|color|text-decoration|QLabel|a \{)',
    r'(LOCALE|LANGID|LANGNAME|_TEXT|CURLOC|SELOBJ|SELACT|MAINTXT|STATTXT|CURACTS|COUNTOBJ|USERCOM|ARRSIZE|ISPLAY|GETOBJ|STRCOMP|STRFIND|STRPOS|MID|ARRPOS|ARRCOMP|INSTR|REPLACE|DYNEVAL|MSECSCOUNT|QSPVER|USRTXT|FUNC|INPUT|RAND|MIN|MAX|IIF|ISNUM|LCASE|UCASE|TRIM|DESC|PLAY|VIEW|WAIT|EXEC|GOTO|GOSUB|JUMP|MENU|CLEAR|CLR|OPEN|SAVE|SHOW|UNSEL|KILL|DEL|ADD|COPY|INCLIB|FREELIB|SETTIMER|STEP|XGOTO|LOCAL|ELSE|ARGS|RESULT|COUNTER|DISABLE|NOSAVE|USEHTML|ONGSAVE|ONGLOAD|QSPGAME|QSPSAVED)',
    r'^(https?|file|mailto|about|data)', r'^\x00',
]
cands = []
for s in strs + u:
    s = s.strip()
    if len(s) < 4:
        continue
    if any(re.search(p, s) for p in skip_patterns):
        continue
    if not re.search(r'[A-Za-z]', s):
        continue
    if ' ' not in s and not s.endswith(('!', '?', '.', ':')):
        continue
    if s in sources or any(s in t for t in sources):
        continue
    if any(s in t for t in ('Qqsp', 'QSP games', 'Sonix')) and s in sources:
        continue
    cands.append(s)

seen = set()
print('--- candidate user-visible literals not found in the .qm ---')
for s in cands:
    if s in seen:
        continue
    seen.add(s)
    print('   %r' % s)
print('total: %d' % len(seen))
