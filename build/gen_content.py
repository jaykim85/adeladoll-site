# booklet_src/content*.js + ui_*.js -> content.json (사이트 원고, 모든 언어)
# 사용법: 이 폴더에서  python gen_content.py   (Node.js 필요)  -> 이어서 python build.py
# 언어 추가: booklet_src 에 content_<lang>.js, ui_<lang>.js 를 만들고 아래 LANGS 에 한 줄 추가 (build.py 의 LANGS 와 ui_strings.json 도 함께)
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "booklet_src"))
LANGS = {
    "ko": ("content.js", "ui_ko.js"),
    "en": ("content_en.js", "ui_en.js"),
    "ja": ("content_ja.js", "ui_ja.js"),
    "zh": ("content_zh.js", "ui_zh.js"),           # 간체
    "zh-tw": ("content_zh_tw.js", "ui_zh_tw.js"),  # 번체 (간체에서 OpenCC s2twp 로 변환해 만든 파일)
    "de": ("content_de.js", "ui_de.js"),
    "fr": ("content_fr.js", "ui_fr.js"),
    "es": ("content_es.js", "ui_es.js"),
    "it": ("content_it.js", "ui_it.js"),
}

def load_js(name):
    js = f"process.stdout.write(JSON.stringify(require({json.dumps(os.path.join(SRC, name))})))"
    return json.loads(subprocess.check_output(["node", "-e", js]).decode("utf-8"))

out = {}
for lang, (cf, uf) in LANGS.items():
    dolls, ui = load_js(cf), load_js(uf)
    tail = [ui["sources"]["title"], ui["sources"]["lead"]]     # (구버전 호환용) 참고 자료를 한 줄씩
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
        "sources": {"title": ui["sources"]["title"], "lead": ui["sources"]["lead"], "groups": ui["sources"]["groups"],
                    "note_label": ui["sources"]["noteLabel"], "note": ui["sources"]["note"]},
        "tail": tail,
    }
    ids = sorted(i for g in out[lang]["groups"] for i in g["ids"])
    assert ids == list(range(1, 36)), (lang, ids)
    assert len(out[lang]["dolls"]) == 35, lang
    assert [g["ids"] for g in out[lang]["groups"]] == [g["ids"] for g in out["ko"]["groups"]], (lang, "목록 그룹이 한국어판과 다름")
json.dump(out, open(os.path.join(HERE, "content.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("content.json written:", {k: (len(v["dolls"]), [len(g["ids"]) for g in v["groups"]]) for k, v in out.items()})
