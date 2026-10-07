import json,urllib.request,sys,os,zipfile
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
url="https://pypi.tuna.tsinghua.edu.cn/pypi/capstone/json"
try:
    j=json.load(urllib.request.urlopen(url,timeout=30))
    for f in j["releases"][j["info"]["version"]]:
        if f["filename"].endswith("win_amd64.whl"):
            print(f["url"]); u=f["url"]; break
    dest=os.path.join(w,"capstone.whl")
    urllib.request.urlretrieve(u,dest)
    print("downloaded",os.path.getsize(dest))
    z=zipfile.ZipFile(dest); z.extractall(os.path.join(w,"pylibs")); print("extracted")
except Exception as e:
    print("ERR",e)
