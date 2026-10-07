# -*- coding: utf-8 -*-
"""Full Chinese patch for Qqsp.exe.

Applied to the pristine backup (Qqsp.exe.bak), so the result is deterministic:

1. window title  "Qt Quest Soft Player"  -> "QSP·小说播放器"   (equal 20-byte
   UTF-8 slot; the length 0x14 baked into `lea edx,[rbx+0x14]` stays valid)
2. the 28 QSP engine error descriptions (UTF-16LE literals, NUL terminated,
   consumed by QString::fromUtf16 -> no baked length, shorter Chinese is safe)
3. four narrow format strings used by the error dialog.  Their length *is*
   baked as `mov edx, imm32` right before `lea rcx, [rip+...]`, so the immediate
   is patched too.  Each replacement fits the literal's aligned slot.
"""
import hashlib
import os
import argparse
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from qpe import b as IMG, off2va, va2off, find_str, xrefs_to, rd_str  # noqa

from qpe import _resolve_exe

# The pristine (unpatched) build to start from.  Default is
# ..\original\Qqsp.exe, i.e. the untouched Qqsp 1.9.0 binary.
SRC = os.environ.get('QQSP_BAK') or _resolve_exe()
DST = os.environ.get('QQSP_OUT') or os.path.join(HERE, os.pardir, 'out', 'Qqsp.exe')

TITLE_OLD = b'Qt Quest Soft Player'
TITLE_NEW = 'QSP·小说播放器'.encode('utf-8')

# ---- QSP engine error descriptions (English -> Chinese) ----
ERRORS = {
    'Division by zero!': '除以零',
    'Type mismatch!': '类型不匹配',
    'Stack overflow!': '堆栈溢出',
    'Too many items in expression!': '表达式中的项过多',
    'File not found!': '文件未找到',
    "Can't load file!": '无法载入文件',
    'Game not loaded!': '游戏未载入',
    'Sign [:] not found!': '缺少符号 [:]',
    "Can't add file!": '无法添加文件',
    "Can't add action!": '无法添加动作',
    'Sign [=] not found!': '缺少符号 [=]',
    'Location not found!': '未找到位置',
    '[end] not found!': '未找到 [end]',
    'Label not found!': '未找到标签',
    "Incorrect variable's name!": '变量名不正确',
    'Quote not found!': '未找到引号',
    'Bracket not found!': '未找到左括号',
    'Brackets not found!': '未找到括号',
    'Syntax error!': '语法错误',
    'Unknown action!': '未知动作',
    "Incorrect arguments' count!": '参数个数不正确',
    "Can't add object!": '无法添加对象',
    "Can't add menu's item!": '无法添加菜单项',
    'Too many variables!': '变量过多',
    "Regular expression's error!": '正则表达式错误',
    'Code not found!': '未找到代码',
    '[to] not found!': '未找到 [to]',
    'Unknown error!': '未知错误',
}

# ---- narrow format strings (ASCII -> Chinese); length immediate is patched ----
FORMATS = [
    ('Location: %1\nArea: %2\nLine: %3\nCode: %4\nDesc: %5',
     '位置: %1\n区域: %2\n行号: %3\n代码: %4\n描述: %5'),
    ('Code: %1\nDesc: %2', '代码: %1\n描述: %2'),
    ('on visit', '访问时'),
    ('on action', '动作时'),
]

report = []


def must(cond, msg):
    if not cond:
        raise SystemExit('FAILED: ' + msg)


def patch_title(data):
    off = data.find(TITLE_OLD)
    must(off > 0, 'title literal not found')
    must(data.find(TITLE_OLD, off + 1) < 0, 'title literal not unique')
    data[off:off + len(TITLE_OLD)] = TITLE_NEW
    report.append('title      @%#x  %r -> %r' % (off2va(off), TITLE_OLD.decode(), TITLE_NEW.decode()))


def patch_errors(data):
    for en, zh in ERRORS.items():
        blob = en.encode('utf-16-le')
        off = data.find(blob)
        must(off > 0, 'wide literal not found: %r' % en)
        must(data.find(blob, off + 2) < 0, 'wide literal not unique: %r' % en)
        new = zh.encode('utf-16-le')
        must(len(new) + 2 <= len(blob), 'chinese too long for %r' % en)
        data[off:off + len(new)] = new
        data[off + len(new):off + len(new) + 2] = b'\x00\x00'   # terminator
        report.append('error      @%#x  %-32s -> %s' % (off2va(off), en, zh))


def patch_formats(data):
    for en, zh in FORMATS:
        blob = en.encode('utf-8')
        # locate by exact bytes (each of these literals occurs once)
        off = data.find(blob)
        must(off > 0, 'format literal not found: %r' % en)
        must(data.find(blob, off + 1) < 0, 'format literal not unique: %r' % en)
        va = off2va(off)
        new = zh.encode('utf-8')
        # how much room until the next literal starts (aligned slot)?
        avail = None
        sites = xrefs_to(va)
        must(sites, 'no xrefs for %r' % en)
        real = []
        for x in sites:
            insn = x - 3
            if data[va2off(insn)] == 0x48 and data[va2off(insn) + 1] == 0x8d:
                real.append(insn)
        must(real, 'no real lea site for %r' % en)
        # slot size: distance to the next non-NUL byte after the string
        p = off + len(blob) + 1
        while data[p] == 0:
            p += 1
        avail = p - off - 1          # usable bytes before the next literal
        must(len(new) <= avail, 'no room for %r (%d > %d)' % (en, len(new), avail))
        data[off:off + len(new)] = new
        data[off + len(new)] = 0
        # patch every baked length immediate
        for insn in real:
            o = va2off(insn)
            must(data[o - 5] == 0xba, 'expected mov edx,imm32 before %#x' % insn)
            old = struct.unpack_from('<I', data, o - 4)[0]
            must(old == len(blob), 'unexpected old length %d at %#x' % (old, insn))
            struct.pack_into('<I', data, o - 4, len(new))
        report.append('format     @%#x  len %2d -> %2d (room %2d, %d site(s))  %r -> %r'
                      % (va, len(blob), len(new), avail, len(real), en, zh))


def main():
    data = bytearray(open(SRC, 'rb').read())
    orig = hashlib.sha256(bytes(data)).hexdigest()
    print('source :', SRC, len(data), 'bytes')
    print('sha256 :', orig)
    patch_title(data)
    patch_errors(data)
    patch_formats(data)
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, 'wb').write(bytes(data))
    print('\n'.join(report))
    print('\nwrote  :', DST, len(data), 'bytes')
    print('sha256 :', hashlib.sha256(bytes(data)).hexdigest())


if __name__ == '__main__':
    main()
