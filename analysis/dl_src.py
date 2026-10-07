import urllib.request,os
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(w,"src"),exist_ok=True)
base="https://gitlab.com/Sonnix1/Qqsp/-/raw/master/"
for f in ["main.cpp","optionsdialog.cpp","optionsdialog.h","Qqsp.en.ts","Qqsp.ru.ts","qqsp.qrc","optionsdialog.ui","Qqsp.pro","mainwindow.cpp"]:
    try:
        d=urllib.request.urlopen(urllib.request.Request(base+f,headers={"User-Agent":"dsh"}),timeout=60).read()
        open(os.path.join(w,"src",f),"wb").write(d)
        print(f,len(d))
    except Exception as e:
        print("ERR",f,e)
