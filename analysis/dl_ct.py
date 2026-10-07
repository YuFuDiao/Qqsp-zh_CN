import urllib.request,os
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
d=urllib.request.urlopen(urllib.request.Request("https://gitlab.com/Sonnix1/Qqsp/-/raw/master/comtools.cpp",headers={"User-Agent":"dsh"}),timeout=60).read()
open(os.path.join(w,"src","comtools.cpp"),"wb").write(d); print("comtools.cpp",len(d))
