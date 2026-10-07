import urllib.request,os
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
base="https://gitlab.com/Sonnix1/Qqsp/-/raw/master/"
for f in ["qsp/errors.h","qsp/errors.c"]:
    try:
        d=urllib.request.urlopen(urllib.request.Request(base+f,headers={"User-Agent":"dsh"}),timeout=60).read()
        open(os.path.join(w,"src",os.path.basename(f)),"wb").write(d); print(f,len(d))
    except Exception as e: print("ERR",f,e)
