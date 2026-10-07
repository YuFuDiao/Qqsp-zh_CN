import urllib.request,os,re
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
for u in ["https://raw.githubusercontent.com/qt/qttranslations/5.13/translations/qtwebengine_zh_CN.ts",
          "https://raw.githubusercontent.com/qt/qttranslations/5.13/translations/qtwebengine_zh_CN.qm"]:
    try:
        d=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"dsh"}),timeout=120).read()
        print("OK",u,len(d)); open(os.path.join(w,"src",os.path.basename(u)),"wb").write(d)
    except Exception as e: print("ERR",u,e)
