import json,urllib.request,os
QSP_ROOT = os.path.dirname(os.path.abspath(__file__))
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"dsh"}),timeout=60)
    return r.read()
try:
    d=json.loads(get("https://gitlab.com/api/v4/projects/Sonnix1%2FQqsp/repository/tree?recursive=true&per_page=100"))
    for e in d: print(e["type"],e["path"])
except Exception as ex:
    print("ERR",ex)
