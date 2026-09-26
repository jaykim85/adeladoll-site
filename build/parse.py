import re, json
CFG={
 "ko":dict(about="이 인형에 대하여",bg="배경 이야기",pend="확인 중인 정보",end="참고 자료",listhdr="전시 인형 목록",intro_end="자주 나오는 용어"),
 "en":dict(about="About This Doll",bg="Background",pend="Pending confirmation",end=None,listhdr="The Dolls on Exhibition",intro_end="Terms You Will Meet"),
}
def parse(k):
    L=open(f"/tmp/{k}.txt").read().split("\n")
    c=CFG[k]
    # groups from list
    li=L.index(c["listhdr"]); groups=[]; i=li+1
    while True:
        s=L[i]
        m=re.match(r"No\. (\d+)\t",s)
        if m: groups[-1]["ids"].append(int(m.group(1)))
        elif re.match(r"No\. 01$",s) : break
        else: groups.append({"name":s,"ids":[]})
        i+=1
    # terms
    ti=L.index(c["intro_end"]); terms=[]
    j=ti+1
    while L[j].startswith("[T] "):
        a,b=L[j][4:].split(" | ",1); terms.append([a,b]); j+=1
    kinds=[]
    ki=[x for x in range(len(L)) if L[x] in ("세 종류의 인형","Three Kinds of Dolls")][0]
    for x in range(ki+1,ti):
        kinds.append(L[x])
    dolls={}; i=L.index("No. 01",li)
    while i<len(L):
        m=re.match(r"No\. (\d+)$",L[i])
        if not m: break
        n=int(m.group(1)); d={"no":n,"title":L[i+1],"subtitle":L[i+2],"info":[],"about":[],"bg":[],"pending":""}
        i+=3; sec=None
        while i<len(L) and not re.match(r"No\. \d+$",L[i]):
            s=L[i]
            if c["end"] and s==c["end"]: break
            if k=="en" and s in ("References","Sources","Sources and References"): break
            if s.startswith("[T] "):
                parts=s[4:].split(" | ")
                if len(parts)==2 and not d["about"]: d["info"].append(parts)
            elif s==c["about"]: sec="about"
            elif s==c["bg"]: sec="bg"
            elif s.startswith(c["pend"]): d["pending"]=s[len(c["pend"]):].strip()
            elif sec: d[sec].append(s)
            i+=1
        dolls[n]=d
        if i<len(L) and not re.match(r"No\. \d+$",L[i]): break
    rest=L[i:]
    return dict(groups=groups,terms=terms,kinds=kinds,dolls=dolls,tail=rest)
out={k:parse(k) for k in ("ko","en")}
for k in out:
    print(k,len(out[k]["dolls"]),[ (g["name"],len(g["ids"])) for g in out[k]["groups"]], "tail",len(out[k]["tail"]), out[k]["tail"][:2])
    for n,d in out[k]["dolls"].items():
        if not d["about"] or not d["info"]: print("  WARN",k,n,len(d["info"]),len(d["about"]),len(d["bg"]))
json.dump({k:{**v,"dolls":{str(n):d for n,d in v["dolls"].items()}} for k,v in out.items()},open("content.json","w"),ensure_ascii=False,indent=1)
