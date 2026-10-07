import urllib.request,re,os
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"dsh"}),timeout=90).read().decode('utf-8','replace')
for u in ["https://code.qt.io/cgit/qt/qtbase.git/plain/src/gui/kernel/qplatformtheme.cpp?h=5.13",
          "https://code.qt.io/cgit/qt/qtbase.git/plain/src/widgets/widgets/qdialogbuttonbox.cpp?h=5.13"]:
    try:
        t=get(u)
        print("=== ",u,len(t))
        for m in re.finditer(r'translate\(\s*"([^"]+)"\s*,\s*"([^"]+)"', t):
            print("   ctx=%-20s src=%s"%(m.group(1),m.group(2)))
        for m in re.finditer(r'tr\(\s*"([^"]+)"',t):
            print("   tr  src=%s"%m.group(1))
    except Exception as e: print("ERR",u,e)
