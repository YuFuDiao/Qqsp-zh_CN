import urllib.request,os
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
urls=[
 "https://raw.githubusercontent.com/qt/qttranslations/5.13/translations/qt_zh_CN.ts",
 "https://raw.githubusercontent.com/qt/qttranslations/v5.13.1/translations/qt_zh_CN.ts",
 "https://code.qt.io/cgit/qt/qttranslations.git/plain/translations/qt_zh_CN.ts?h=5.13",
 "https://raw.githubusercontent.com/qt/qttranslations/5.15/translations/qtbase_zh_CN.ts",
]
for u in urls:
    try:
        d=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"dsh"}),timeout=90).read()
        print("OK",u,len(d))
        open(os.path.join(w,"src","qt_zh_CN.ts"),"wb").write(d)
        break
    except Exception as e:
        print("ERR",u,e)
