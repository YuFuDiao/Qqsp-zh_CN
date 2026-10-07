# -*- coding: utf-8 -*-
"""Ask the real Qt5Core.dll what QLocale::system().name() returns here."""
import ctypes

qt = ctypes.WinDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'original', 'Qt5Core.dll'))
V = ctypes.c_void_p

p_sys = getattr(qt, '?system@QLocale@@SA?AV1@XZ')          # static QLocale QLocale::system()
p_sys.argtypes = [V]
p_sys.restype = V
p_name = getattr(qt, '?name@QLocale@@QEBA?AVQString@@XZ')  # QString QLocale::name() const
p_name.argtypes = [V, V]
p_name.restype = V
p_ctor_qs = getattr(qt, '??0QString@@QEAA@XZ')
p_ctor_qs.argtypes = [V]
p_ctor_qs.restype = V
p_utf16 = getattr(qt, '?utf16@QString@@QEBAPEBGXZ')
p_utf16.argtypes = [V]
p_utf16.restype = V


def qstr(qs):
    p = p_utf16(qs)
    return ctypes.wstring_at(p) if p else None


locale = ctypes.create_string_buffer(32)
p_sys(locale)
out = ctypes.create_string_buffer(32)
p_ctor_qs(out)
p_name(locale, out)
print('QLocale::system().name() =', repr(qstr(out)))
