import urllib.request,os
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
for f in ["qspwebbox.cpp","qspwebbox.h"]:
    try:
        d=urllib.request.urlopen(urllib.request.Request("https://gitlab.com/Sonnix1/Qqsp/-/raw/master/"+f,headers={"User-Agent":"dsh"}),timeout=60).read()
        open(os.path.join(w,"src",f),"wb").write(d); print(f,len(d))
    except Exception as e: print("ERR",f,e)
