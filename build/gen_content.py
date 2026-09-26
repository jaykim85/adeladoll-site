# booklet_src/content*.js + ui_*.js -> content.json (사이트 원고)
# 사용법: 이 폴더에서  python gen_content.py   (Node.js 필요)  -> 이어서 python build.py
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "booklet_src"))
LANGS = {"ko": ("content.js", "ui_ko.js"), "en": ("content_en.js", "ui_en.js")}

def load_js(name):
    js = f"process.stdout.write(JSON.stringify(require({json.dumps(os.path.join(SRC, name))})))"
    return json.loads(subprocess.check_output(["node", "-e", js]).decode("utf-8"))

out = {}
for lang, (cf, uf) in LANGS.items():
    dolls, ui = load_js(cf), load_js(uf)
    tail = [ui["sources"]["title"], ui["sources"]["lead"]]
    for name, items in ui["sources"]["groups"]:
        tail.append(name); tail.extend(items)
    tail.append(ui["sources"]["noteLabel"] + "  " + ui["sources"]["note"])
    out[lang] = {
        "groups": [{"name": n, "ids": ids} for n, ids in ui["contents"]["groups"]],
        "terms": ui["intro"]["terms"],
        "kinds": [a + "  " + b for a, b in ui["intro"]["types"]],
        "dolls": {str(d["no"]): {"no": d["no"], "title": d["name"], "subtitle": d["cat"], "info": d["specs"],
                                "about": d["about"], "bg": d["background"], "pending": " ".join(d.get("notes") or [])}
                  for d in dolls},
        "tail": tail,
    }
    ids = sorted(i for g in out[lang]["groups"] for i in g["ids"])
    assert ids == list(range(1, 36)), (lang, ids)
    assert len(out[lang]["dolls"]) == 35, lang
json.dump(out, open(os.path.join(HERE, "content.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("content.json written:", {k: (len(v["dolls"]), [(g["name"], len(g["ids"])) for g in v["groups"]]) for k, v in out.items()})
