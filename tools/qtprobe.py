# -*- coding: utf-8 -*-
"""Load a .qm with the real Qt5Core.dll and print resolved translations.

Usage: python qtprobe.py <file.qm>
"""
import ctypes
import os
import sys

QT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qt5Core.dll')
qt = ctypes.WinDLL(QT)

c_void_p = ctypes.c_void_p
c_char_p = ctypes.c_char_p
c_int = ctypes.c_int

p_ctor_tr = getattr(qt, '??0QTranslator@@QEAA@PEAVQObject@@@Z')
p_ctor_tr.argtypes = [c_void_p, c_void_p]
p_ctor_tr.restype = c_void_p
p_dtor_tr = getattr(qt, '??1QTranslator@@UEAA@XZ')
p_dtor_tr.argtypes = [c_void_p]
p_load = getattr(qt, '?load@QTranslator@@QEAA_NPEBEHAEBVQString@@@Z')
p_load.argtypes = [c_void_p, c_char_p, c_int, c_void_p]
p_load.restype = ctypes.c_bool
p_ctor_qs = getattr(qt, '??0QString@@QEAA@XZ')
p_ctor_qs.argtypes = [c_void_p]
p_ctor_qs.restype = c_void_p
p_translate = getattr(qt, '?translate@QTranslator@@UEBA?AVQString@@PEBD00H@Z')
# This Qt build passes the hidden QString return slot in RDX and `this` in RCX.
p_translate.argtypes = [c_void_p, c_void_p, c_char_p, c_char_p, c_char_p, c_int]
p_translate.restype = c_void_p
p_utf16 = getattr(qt, '?utf16@QString@@QEBAPEBGXZ')
p_utf16.argtypes = [c_void_p]
p_utf16.restype = c_void_p
p_isempty_tr = getattr(qt, '?isEmpty@QTranslator@@UEBA_NXZ')
p_isempty_tr.argtypes = [c_void_p]
p_isempty_tr.restype = ctypes.c_bool


def main():
    path = sys.argv[1]
    data = open(path, 'rb').read()

    empty_qs = ctypes.create_string_buffer(32)
    p_ctor_qs(empty_qs)

    tr = ctypes.create_string_buffer(64)
    p_ctor_tr(tr, None)

    buf = ctypes.create_string_buffer(data, len(data))
    ok = p_load(tr, ctypes.cast(buf, c_char_p), len(data), ctypes.cast(empty_qs, c_void_p))
    print('load(%s) -> %s   isEmpty=%s' % (os.path.basename(path), ok, p_isempty_tr(tr)))
    if not ok:
        return

    def tr_(ctx, src, n=-1):
        res = ctypes.create_string_buffer(32)
        p_ctor_qs(res)
        p_translate(tr, res, ctx.encode(), src.encode(), None, n)
        p = p_utf16(res)
        if not p:
            return None
        return ctypes.wstring_at(p)

    print('langname   =', tr_('__LANG__', '__LANGNAME__'))
    print('langid     =', tr_('__LANG__', '__LANGID__'))
    for ctx, src in [('MainWindow', '&Quest'), ('MainWindow', 'Open game...'),
                     ('MainWindow', 'Save game...'), ('MainWindow', 'Quick Save'),
                     ('MainWindow', 'Exit'), ('MainWindow', 'About...'),
                     ('MainWindow', 'Window / Fullscreen mode'),
                     ('OptionsDialog', 'Options'), ('OptionsDialog', 'Language'),
                     ('OptionsDialog', 'Cancel'), ('OptionsDialog', 'Ok'),
                     ('QspMsgDlg', 'OK'), ('main', 'Game file to open.'),
                     ('MainWindow', 'Select game file'),
                     ('MainWindow', 'QSP games (*.qsp *.gam)'),
                     ('QFileDialog', 'Look in:'),
                     ('QFileDialog', 'File &name:'),
                     ('QFileDialog', 'Files of type:'),
                     ('QFileDialog', '&Open'),
                     ('QFileSystemModel', 'Name'),
                     ('QPlatformTheme', 'Cancel'),
                     ('QPlatformTheme', '&Yes'),
                     ('QLineEdit', '&Copy'),
                     ('QColorDialog', '&Basic colors'),
                     ('QFontDialog', '&Font'),
                     ('QMessageBox', 'Show Details...')]:
        print('  %-24s %-32s -> %s' % ('[' + ctx + ']', src, tr_(ctx, src)))

    p_dtor_tr(tr)


if __name__ == '__main__':
    main()
