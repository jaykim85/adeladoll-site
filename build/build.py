# Adela Art Doll - static site generator
# 사용법: 이 폴더에서  python build.py   -> ../docs 에 사이트가 생성됩니다.
import json, os, re, glob, shutil, html
from datetime import date
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))      # C:\dev\Doll Works (사진 원본 위치)
OUT = os.path.abspath(os.path.join(HERE, "..", "docs"))     # 배포 폴더
C = json.load(open(os.path.join(HERE, "content.json"), encoding="utf-8"))
SITE = json.load(open(os.path.join(HERE, "site.json"), encoding="utf-8"))
SALES = json.load(open(os.path.join(HERE, "sales.json"), encoding="utf-8"))["dolls"]
e = html.escape
IDS = list(range(1, 36))

# ---------- languages ----------
# 언어 추가 순서: booklet_src 에 content_<lang>.js / ui_<lang>.js 작성 -> gen_content.py 의 LANGS -> 여기 LANGS/HREFLANG/OG_LOCALE/FONTS -> ui_strings.json 에 문구 -> site.json 에 address_/hours_
LANGS = ["ko", "en", "ja", "zh", "zh-tw", "de", "fr", "es", "it"]          # 첫 번째(ko)가 루트, 나머지는 /<lang>/
HREFLANG = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh-Hans", "zh-tw": "zh-Hant", "de": "de", "fr": "fr", "es": "es", "it": "it"}
OG_LOCALE = {"ko": "ko_KR", "en": "en_US", "ja": "ja_JP", "zh": "zh_CN", "zh-tw": "zh_TW", "de": "de_DE", "fr": "fr_FR", "es": "es_ES", "it": "it_IT"}
LATIN_FONTS = "family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500"
FONTS = {"ko": "&family=Noto+Serif+KR:wght@500;600&family=Noto+Sans+KR:wght@400;500;600",
         "ja": "&family=Noto+Serif+JP:wght@500;600&family=Noto+Sans+JP:wght@400;500;600",
         "zh": "&family=Noto+Serif+SC:wght@500;600&family=Noto+Sans+SC:wght@400;500;600",
         "zh-tw": "&family=Noto+Serif+TC:wght@500;600&family=Noto+Sans+TC:wght@400;500;600"}
T = json.load(open(os.path.join(HERE, "ui_strings.json"), encoding="utf-8"))   # 화면 문구 (언어별)
for _l in LANGS:
    assert _l in T and _l in C, f"missing language {_l}"
    T[_l]["prefix"] = "" if _l == LANGS[0] else "/" + _l
UNCONF = tuple(T[l]["tbc"] for l in LANGS)      # '확인 중' 값은 사이트에 표시하지 않음

FEATURED = [2, 35, 9, 21, 20, 25]
HERO = [1, 2, 22]
# 종류 카드 -> 목록 그룹 인덱스: 첫 그룹 = 앤틱 원본, 마지막 그룹 = 모던 아티스트 돌, 그 사이 = 복제 (그룹 수가 바뀌어도 자동)
_NG = len(C["ko"]["groups"])
KIND_GROUPS = {0: [0], 1: list(range(1, _NG - 1)), 2: [_NG - 1]}

# ---------- images ----------
def build_images():
    d = os.path.join(OUT, "assets", "img"); os.makedirs(d, exist_ok=True)
    for n in IDS:
        cands = glob.glob(os.path.join(ROOT, "dolls", f"{n:02d}_*", f"{n}.*")) + glob.glob(os.path.join(ROOT, f"{n}.*"))  # 2026-09-26: 사진은 dolls/NN_이름/ 폴더로 이동
        src = [f for f in cands if re.search(r"\.(jpe?g|png)$", f, re.I)][0]
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        for size, suf, q in ((1600, "l", 84), (720, "m", 80)):
            t = im.copy(); t.thumbnail((size, size), Image.LANCZOS)
            t.save(os.path.join(d, f"doll-{n:02d}-{suf}.jpg"), quality=q, optimize=True, progressive=True)
        # 공유 미리보기용 1200x630
        t = ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(0.5, 0.3))
        t.save(os.path.join(d, f"og-{n:02d}.jpg"), quality=80, optimize=True)
    # 홈 공유 이미지: 3장 가로 배치
    og = Image.new("RGB", (1200, 630), (247, 242, 234))
    for i, n in enumerate(HERO):
        cands = glob.glob(os.path.join(ROOT, "dolls", f"{n:02d}_*", f"{n}.*")) + glob.glob(os.path.join(ROOT, f"{n}.*"))
        im = ImageOps.exif_transpose(Image.open([f for f in cands if re.search(r"\.(jpe?g|png)$", f, re.I)][0])).convert("RGB")
        og.paste(ImageOps.fit(im, (400, 630), Image.LANCZOS, centering=(0.5, 0.3)), (i * 400, 0))
    og.save(os.path.join(d, "og-home.jpg"), quality=80, optimize=True)

def img_size(n, suf):
    with Image.open(os.path.join(OUT, "assets", "img", f"doll-{n:02d}-{suf}.jpg")) as im: return im.size

# ---------- helpers ----------
def dolls(lang): return C[lang]["dolls"]
def dnum(n): return f"No. {n:02d}"
def url(lang, path=""): return f"{T[lang]['prefix']}/{path}"
def group_of(lang):
    m = {}
    for gi, g in enumerate(C[lang]["groups"]):
        for n in g["ids"]: m[n] = gi
    return m
def status(n): return SALES[f"{n:02d}"]
def kind_split(s):
    a, b = s.split("  ", 1); return a, b

def page(lang, path, title, desc, body, og_img="og-home.jpg", alt_path=None, extra_head=""):
    t = T[lang]
    alt_path = path if alt_path is None else alt_path
    full_title = f"{title} | Adela Art Doll" if title else "Adela Art Doll | " + t["tagline"]
    canon = SITE["domain"] + url(lang, path)
    nav = [("collection/", t["nav_collection"]), ("about/", t["nav_about"]), ("visit/", t["nav_visit"])]
    CUR = ' aria-current="page"'
    navh = "".join(f'<a href="{url(lang,p)}"{CUR if path.startswith(p) else ""}>{e(l)}</a>' for p, l in nav)
    fonts = LATIN_FONTS + FONTS.get(lang, "")
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE["domain"]}{url(l, alt_path)}">\n' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE["domain"]}{url(LANGS[0], alt_path)}">'
    # 언어 메뉴: 현재 언어를 제목으로, 나머지를 목록으로 (JS 없이 동작)
    CURL = ' aria-current="true"'
    lang_items = "".join(f'<li><a href="{url(l, alt_path)}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}" data-lang="{l}"{CURL if l == lang else ""}>{e(T[l]["lang_name"])}</a></li>' for l in LANGS)
    lang_menu = f'<details class="lang"><summary aria-label="Language">{e(t["lang_name"])}</summary><ul>{lang_items}</ul></details>'
    # 첫 방문 시 홈(/)에서만 브라우저 언어에 맞는 홈으로 이동. 언어 메뉴에서 고른 언어는 localStorage(adela_lang)에 저장되어 그 뒤로는 그 언어로 이동
    redirect = ""
    if lang == LANGS[0] and path == "":
        redirect = ("<script>(function(){try{if(location.pathname!=='/')return;var L=" + json.dumps(LANGS) + ";var l=localStorage.getItem('adela_lang');"
                    "if(!l){var n=((navigator.languages&&navigator.languages[0])||navigator.language||'').toLowerCase();"
                    "if(n.indexOf('zh')===0){l=/tw|hk|mo|hant/.test(n)?'zh-tw':'zh';}else{l=n.slice(0,2);}if(L.indexOf(l)<0)l='en';}"
                    "if(l!==L[0]&&L.indexOf(l)>=0)location.replace('/'+l+'/'+location.search+location.hash);}catch(e){}})();</script>\n")
    foot_biz = ""
    bi = [(t["biz_name"], SITE["biz_name"]), (t["biz_owner"], SITE["biz_owner"]), (t["biz_reg"], SITE["biz_reg_no"]), (t["biz_mail"], SITE["mail_order_no"])]
    bi = [x for x in bi if x[1]]
    if bi: foot_biz = '<p class="biz">' + " / ".join(f"{e(k)} {e(v)}" for k, v in bi) + "</p>"
    verify = ""
    if SITE.get("google_site_verification"): verify += f'<meta name="google-site-verification" content="{e(SITE["google_site_verification"])}">\n'
    if SITE.get("naver_site_verification"): verify += f'<meta name="naver-site-verification" content="{e(SITE["naver_site_verification"])}">\n'
    return f"""<!doctype html>
<html lang="{HREFLANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
{alts}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Adela Art Doll">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE['domain']}/assets/img/{og_img}">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
<meta name="twitter:card" content="summary_large_image">
{verify}{redirect}<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}
</head>
<body class="lang-{lang}">
<a class="skip" href="#main">{e(t['skip'])}</a>
<header class="site-header">
 <div class="wrap bar">
  <a class="brand" href="{url(lang)}"><span class="mono">A</span><span class="wordmark">ADELA ART DOLL</span></a>
  <nav class="nav" aria-label="main">{navh}{lang_menu}</nav>
 </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
 <div class="wrap foot">
  <div><a class="brand small" href="{url(lang)}"><span class="mono">A</span><span class="wordmark">ADELA ART DOLL</span></a>
  <p class="muted">{e(t['tagline'])}</p></div>
  <div class="foot-links"><a href="https://www.instagram.com/{SITE['instagram']}/" rel="noopener" target="_blank">Instagram @{SITE['instagram']}</a>
  <a href="{url(lang,'visit/')}">{e(t['nav_visit'])}</a></div>
 </div>
 <div class="wrap">{foot_biz}<p class="copy">&copy; {date.today().year} Adela Art Doll</p></div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>"""

def status_badge(lang, n):
    s = status(n)["status"]
    if s == "exhibit": return ""
    return f'<span class="badge st-{s}">{e(T[lang]["st_"+s])}</span>'

def card(lang, n, eager=False):
    d = dolls(lang)[str(n)]; w, h = img_size(n, "m"); gm = group_of(lang)
    return f"""<li class="card" data-group="{gm[n]}"><a href="{url(lang, f'dolls/{n:02d}/')}">
<figure><img src="/assets/img/doll-{n:02d}-m.jpg" width="{w}" height="{h}" alt="{e(d['title'])}" loading="{'eager' if eager else 'lazy'}" decoding="async">{status_badge(lang,n)}</figure>
<div class="card-text"><span class="no">{dnum(n)}</span><h3>{e(d['title'])}</h3><p>{e(d['subtitle'])}</p></div></a></li>"""

# ---------- pages ----------
def home(lang):
    t = T[lang]; L = C[lang]
    PRI, LAZY = 'fetchpriority="high"', 'loading="lazy"'
    hero_imgs = "".join(f'<a class="h{i}" href="{url(lang, f"dolls/{n:02d}/")}"><img src="/assets/img/doll-{n:02d}-{"l" if i==0 else "m"}.jpg" alt="{e(dolls(lang)[str(n)]["title"])}" {PRI if i==0 else LAZY}></a>' for i, n in enumerate(HERO))
    kinds = ""
    for i, k in enumerate(L["kinds"]):
        name, text = kind_split(k)
        cnt = sum(len(L["groups"][g]["ids"]) for g in KIND_GROUPS[i])
        kinds += f'<article class="kind"><span class="kind-no">0{i+1}</span><h3>{e(name)}</h3><p>{e(text)}</p><a class="more" href="{url(lang,"collection/")}#g={",".join(map(str,KIND_GROUPS[i]))}">{cnt}{e(t["dolls_count"])} &rarr;</a></article>'
    feat = "".join(card(lang, n) for n in FEATURED)
    body = f"""
<section class="hero"><div class="wrap hero-grid">
 <div class="hero-text"><p class="kicker">{e(t['hero_kicker'])}</p><h1>{t['hero_title']}</h1><p class="lead">{e(t['hero_text'])}</p>
 <div class="actions"><a class="btn primary" href="{url(lang,'collection/')}">{e(t['cta_collection'])}</a><a class="btn" href="https://www.instagram.com/{SITE['instagram']}/" target="_blank" rel="noopener">{e(t['cta_insta'])}</a></div></div>
 <div class="hero-imgs">{hero_imgs}</div>
</div></section>
<section class="section"><div class="wrap"><h2 class="sec-title">{e(t['kinds_title'])}</h2><div class="kinds">{kinds}</div></div></section>
<section class="section alt"><div class="wrap"><h2 class="sec-title">{e(t['featured_title'])}</h2><ul class="grid">{feat}</ul>
<p class="center"><a class="btn" href="{url(lang,'collection/')}">{e(t['see_all'])}</a></p></div></section>
{visit_block(lang)}"""
    ld = {"@context": "https://schema.org", "@type": "Store", "name": "Adela Art Doll", "url": SITE["domain"] + url(lang),
          "image": SITE["domain"] + "/assets/img/og-home.jpg", "sameAs": [f"https://www.instagram.com/{SITE['instagram']}/"], "description": t["site_desc"]}
    if SITE.get("address_ko"):
        ld["address"] = {"@type": "PostalAddress", "streetAddress": "경의로256번길 52" if lang == "ko" else "52, Gyeongui-ro 256beon-gil",
                         "addressLocality": "고양시 일산동구" if lang == "ko" else "Ilsandong-gu, Goyang-si",
                         "addressRegion": "경기도" if lang == "ko" else "Gyeonggi-do", "addressCountry": "KR"}   # 한국어 외에는 로마자 표기
    if SITE.get("opening_hours_schema"): ld["openingHours"] = SITE["opening_hours_schema"]
    _map = SITE.get("map_url_" + lang) or SITE.get("map_url_en")
    if _map: ld["hasMap"] = _map   # 한국어는 네이버 지도(플레이스), 그 외는 구글 지도
    head = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    return page(lang, "", "", t["site_desc"], body, extra_head=head)

def visit_block(lang, full=False):
    t = T[lang]
    rows = []
    if SITE.get("address_" + lang):
        a = e(SITE["address_" + lang])
        mu = SITE.get("map_url_" + lang) or SITE.get("map_url_en") or SITE.get("map_url")   # 한국어는 네이버 지도, 그 외는 구글 지도
        if mu: a += f' <a class="maplink" href="{e(mu)}" target="_blank" rel="noopener">{e(t["v_map"])}</a>'
        rows.append((t["v_addr"], a))
    if SITE.get("hours_" + lang): rows.append((t["v_hours"], e(SITE["hours_" + lang])))
    if SITE.get("email"): rows.append((t["v_email"], f'<a href="mailto:{e(SITE["email"])}">{e(SITE["email"])}</a>'))
    if SITE.get("phone"): rows.append((t["v_phone"], f'<a href="tel:{e(SITE["phone"])}">{e(SITE["phone"])}</a>'))
    info = "".join(f"<dt>{e(k)}</dt><dd>{v}</dd>" for k, v in rows)
    def shop(label, u):
        return f'<li><span>{e(label)}</span>' + (f'<a class="btn small" href="{e(u)}" target="_blank" rel="noopener">{e(t["visit_btn"])}</a>' if u else f'<em>{e(t["v_soon"])}</em>') + "</li>"
    shops = shop(t["v_shop_ko"], SITE["smartstore_url"]) + shop(t["v_shop_en"], SITE["etsy_url"])
    h = "h1" if full else "h2"
    return f"""<section class="section visit"><div class="wrap visit-grid">
<div><{h} class="sec-title">{e(t['visit_title'])}</{h}><p class="lead">{e(t['visit_lead'])}</p>{f'<dl class="info">{info}</dl>' if info else ''}</div>
<div class="panels">
 <div class="panel"><h3>{e(t['v_insta'])}</h3><p>{e(t['v_insta_text'])}</p><a class="btn primary" href="https://ig.me/m/{SITE['instagram']}" target="_blank" rel="noopener">@{SITE['instagram']}</a></div>
 <div class="panel"><h3>{e(t['v_shop'])}</h3><ul class="shops">{shops}</ul></div>
</div></div></section>"""

def collection(lang):
    t = T[lang]; L = C[lang]
    chips = f'<button type="button" class="chip" data-g="all" aria-pressed="true">{e(t["all"])} <span>35</span></button>'
    for gi, g in enumerate(L["groups"]):
        chips += f'<button type="button" class="chip" data-g="{gi}" aria-pressed="false">{e(g["name"])} <span>{len(g["ids"])}</span></button>'
    items = "".join(card(lang, n, eager=(i < 4)) for i, n in enumerate(IDS))
    body = f"""<section class="section page-head"><div class="wrap"><h1 class="sec-title">{e(t['collection_title'])}</h1><p class="lead">{e(t['collection_lead'])}</p>
<div class="chips" role="group" aria-label="filter">{chips}</div><ul class="grid" id="grid">{items}</ul></div></section>"""
    return page(lang, "collection/", t["collection_title"], t["collection_lead"], body)

def detail(lang, n):
    t = T[lang]; d = dolls(lang)[str(n)]; s = status(n)
    w, h = img_size(n, "l")
    rows = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in d["info"] if v.strip() not in UNCONF)
    about = "".join(f"<p>{e(p)}</p>" for p in d["about"])
    bg = "".join(f"<p>{e(p)}</p>" for p in d["bg"])
    price = ""
    if s["status"] in ("available", "reserved"):
        p = s["price_krw"] if lang == "ko" else s["price_usd"]
        if p: price = f'<p class="price">{"%s원" % format(p, ",") if lang=="ko" else "US$ %s" % format(p, ",")}</p>'
    buttons = []
    if s["status"] == "available":
        if lang == "ko" and (s["smartstore"] or SITE["smartstore_url"]): buttons.append(f'<a class="btn primary" href="{e(s["smartstore"] or SITE["smartstore_url"])}" target="_blank" rel="noopener">{e(t["buy_store"])}</a>')
        if s["etsy"] or (lang == "en" and SITE["etsy_url"]): buttons.append(f'<a class="btn primary" href="{e(s["etsy"] or SITE["etsy_url"])}" target="_blank" rel="noopener">{e(t["buy_etsy"])}</a>')
    buttons.append(f'<a class="btn" href="https://ig.me/m/{SITE["instagram"]}" target="_blank" rel="noopener">{e(t["inquire"])}</a>')
    i = IDS.index(n); pv = IDS[i - 1] if i > 0 else None; nx = IDS[i + 1] if i < len(IDS) - 1 else None
    def pn(m, lab, cls):
        if not m: return "<span></span>"
        return f'<a class="pn {cls}" href="{url(lang, f"dolls/{m:02d}/")}"><small>{e(lab)}</small>{dnum(m)} {e(dolls(lang)[str(m)]["title"])}</a>'
    body = f"""<article class="section detail"><div class="wrap">
<p class="crumb"><a href="{url(lang,'collection/')}">&larr; {e(t['back'])}</a></p>
<div class="detail-grid">
 <figure class="detail-img"><a href="/assets/img/doll-{n:02d}-l.jpg" target="_blank"><img src="/assets/img/doll-{n:02d}-l.jpg" width="{w}" height="{h}" alt="{e(d['title'])}" fetchpriority="high"></a></figure>
 <div class="detail-text">
  <p class="no">{dnum(n)} {status_badge(lang,n)}</p><h1>{e(d['title'])}</h1><p class="sub">{e(d['subtitle'])}</p>
  {price}
  {f'<h2 class="h-small">{e(t["details"])}</h2><dl class="info">{rows}</dl>' if rows else ''}
  <h2 class="h-small">{e(t['about_doll'])}</h2>{about}
  <h2 class="h-small">{e(t['background'])}</h2>{bg}
  <div class="actions">{''.join(buttons)}</div><p class="muted small">{e(t['inquiry_note'])}</p>
 </div>
</div>
<nav class="prevnext">{pn(pv, t['prev'], 'p')}{pn(nx, t['next'], 'n')}</nav>
</div></article>"""
    desc = (d["about"][0] if d["about"] else d["subtitle"])[:150]
    ld = {"@context": "https://schema.org", "@type": "VisualArtwork", "name": d["title"], "artform": "Porcelain doll",
          "image": SITE["domain"] + f"/assets/img/doll-{n:02d}-l.jpg", "description": desc, "url": SITE["domain"] + url(lang, f"dolls/{n:02d}/")}
    head = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    return page(lang, f"dolls/{n:02d}/", f"{dnum(n)} {d['title']}", desc, body, og_img=f"og-{n:02d}.jpg", extra_head=head)

def about(lang):
    t = T[lang]; L = C[lang]
    kinds = "".join(f'<article class="kind"><span class="kind-no">0{i+1}</span><h3>{e(kind_split(k)[0])}</h3><p>{e(kind_split(k)[1])}</p></article>' for i, k in enumerate(L["kinds"]))
    terms = "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in L["terms"])
    # 참고 자료: gen_content.py 가 만든 sources {lead, groups:[[제목,[항목...]]]} (미확인 항목 메모는 사이트에 표시하지 않음)
    S = L["sources"]
    src = "".join(f'</ul><h3 class="h-small">{e(name)}</h3><ul class="sources">' + "".join(f"<li>{e(x)}</li>" for x in items) for name, items in S["groups"])
    body = f"""<section class="section page-head"><div class="wrap narrow"><h1 class="sec-title">{e(t['about_title'])}</h1><p class="lead">{e(t['about_lead'])}</p></div></section>
<section class="section"><div class="wrap"><div class="kinds">{kinds}</div></div></section>
<section class="section alt"><div class="wrap narrow"><h2 class="sec-title">{e(t['terms_title'])}</h2><dl class="terms">{terms}</dl></div></section>
<section class="section"><div class="wrap narrow"><h2 class="sec-title">{e(t['sources_title'])}</h2><div class="src"><p>{e(S["lead"])}</p><ul class="sources">{src}</ul></div></div></section>"""
    return page(lang, "about/", t["about_title"], t["about_lead"], body)

def visit(lang):
    return page(lang, "visit/", T[lang]["visit_title"], T[lang]["visit_lead"], visit_block(lang, full=True))

def notfound(lang):
    t = T[lang]
    body = f'<section class="section page-head"><div class="wrap narrow center"><h1 class="sec-title">{e(t["nf_title"])}</h1><p class="lead">{e(t["nf_text"])}</p><p><a class="btn primary" href="{url(lang)}">{e(t["home"])}</a></p></div></section>'
    return page(lang, "404.html", t["nf_title"], t["nf_text"], body, alt_path="")

def write(path, s):
    p = os.path.join(OUT, path.lstrip("/"))
    if path.endswith("/"): p = os.path.join(p, "index.html")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(s)

def main():
    keep = os.path.join(OUT, "assets", "img")
    if os.path.isdir(OUT) and os.environ.get("CLEAN"):   # CLEAN=1 python build.py 로 실행하면 docs 를 비우고 다시 생성
        for x in os.listdir(OUT):
            if x == "assets": continue
            fp = os.path.join(OUT, x); shutil.rmtree(fp) if os.path.isdir(fp) else os.remove(fp)
    os.makedirs(OUT, exist_ok=True)
    if not os.path.isfile(os.path.join(keep, "doll-35-m.jpg")) or os.environ.get("REBUILD_IMAGES"): build_images()
    for f in ("style.css", "site.js", "favicon.svg"): shutil.copy(os.path.join(HERE, "static", f), os.path.join(OUT, "assets", f))
    urls = []
    for lang in LANGS:
        pre = T[lang]["prefix"]
        write(pre + "/", home(lang)); write(pre + "/collection/", collection(lang))
        write(pre + "/about/", about(lang)); write(pre + "/visit/", visit(lang))
        for n in IDS: write(pre + f"/dolls/{n:02d}/", detail(lang, n))
        urls += [pre + "/", pre + "/collection/", pre + "/about/", pre + "/visit/"] + [pre + f"/dolls/{n:02d}/" for n in IDS]
    for lang in LANGS: write(T[lang]["prefix"] + "/404.html", notfound(lang))   # GitHub Pages 는 루트 /404.html 만 사용
    today = date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE['domain']}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    write("/sitemap.xml", sm)
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
    write("/CNAME", SITE["domain"].replace("https://", "") + "\n")
    write("/.nojekyll", "")
    print("built", len(urls), "pages,", len(LANGS), "languages ->", OUT)

if __name__ == "__main__": main()
