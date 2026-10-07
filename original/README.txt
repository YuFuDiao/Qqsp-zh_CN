Place the PRISTINE, unpatched Qqsp 1.9.0 executable here, named:

    Qqsp.exe

SHA256 (the build this localization was made against):
    7ad434c3034a1e0284871ad5991c1d747c0cbdd3c22d53201d2cacc539567e38

Size: 666624 bytes

It is consumed by tools/patch_exe2.py as the input to re-derive out/Qqsp.exe.
The copy committed here is the upstream 1.9.0 binary, kept so that the patch can
be reproduced and verified byte for byte. Override the path with the QQSP_EXE /
QQSP_BAK environment variables if you keep your own copy elsewhere.