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
UNCONF = ("확인 중", "To be confirmed")

T = {
 "ko": dict(prefix="", other="en", other_label="EN", lang_name="한국어",
   nav_collection="컬렉션", nav_about="인형 이야기", nav_visit="방문 / 문의",
   site_desc="Adela Art Doll - 앤틱 비스크 돌과 아티스트 리프로덕션 포슬린 인형 전시관. 독일, 프랑스 앤틱 원본과 복제, 모던 아티스트 돌 35점을 소개합니다.",
   hero_kicker="Porcelain Doll Gallery", hero_title="시간을 건너온<br>포슬린 인형들",
   hero_text="독일과 프랑스의 앤틱 비스크 돌부터 현대 작가의 아티스트 돌까지, 한 점 한 점의 이야기를 담은 35점의 인형을 소개합니다.",
   cta_collection="컬렉션 보기", cta_insta="인스타그램",
   kinds_title="세 종류의 인형", featured_title="컬렉션 하이라이트", see_all="전체 컬렉션 보기",
   collection_title="컬렉션", collection_lead="전시 중인 포슬린 인형 35점입니다. 인형을 누르면 자세한 이야기를 볼 수 있습니다.",
   all="전체", about_doll="이 인형에 대하여", background="배경 이야기", details="기본 정보",
   prev="이전", next="다음", back="컬렉션으로",
   inquire="인스타그램으로 문의", buy_store="네이버 스마트스토어에서 구매", buy_etsy="Etsy에서 구매 (해외)",
   st_exhibit="전시 중", st_available="판매 중", st_reserved="예약 중", st_sold="판매 완료",
   inquiry_note="이 인형에 관한 문의는 인스타그램 메시지로 편하게 남겨 주세요.",
   about_title="인형 이야기", about_lead="포슬린 인형을 처음 보시는 분들을 위한 짧은 안내입니다.",
   terms_title="자주 나오는 용어", sources_title="참고 자료",
   visit_title="방문 / 문의", visit_lead="전시 관람과 인형 구매에 관한 문의를 기다립니다.",
   v_insta="인스타그램", v_insta_text="새 소식과 인형 사진을 가장 먼저 올립니다. 문의는 DM으로 받습니다.",
   v_shop="온라인 구매", v_shop_ko="국내 구매: 네이버 스마트스토어", v_shop_en="해외 구매: Etsy",
   v_soon="준비 중입니다", v_addr="주소", v_hours="관람 시간", v_email="이메일", v_phone="전화", v_map="지도 보기",
   biz="사업자 정보", biz_name="상호", biz_owner="대표", biz_reg="사업자등록번호", biz_mail="통신판매업 신고번호",
   nf_title="페이지를 찾을 수 없습니다", nf_text="주소가 바뀌었거나 없는 페이지입니다.", home="처음으로",
   dolls_count="점"),
 "en": dict(prefix="/en", other="ko", other_label="한국어", lang_name="English",
   nav_collection="Collection", nav_about="About the Dolls", nav_visit="Visit & Contact",
   site_desc="Adela Art Doll - a gallery of antique bisque dolls and artist reproductions in Korea. 35 porcelain dolls: German and French antiques, reproductions and modern artist dolls.",
   hero_kicker="Porcelain Doll Gallery", hero_title="Porcelain dolls<br>across the years",
   hero_text="From German and French antique bisque dolls to the work of today's doll artists: 35 dolls, each with its own story.",
   cta_collection="View the collection", cta_insta="Instagram",
   kinds_title="Three kinds of dolls", featured_title="Highlights", see_all="See the full collection",
   collection_title="Collection", collection_lead="The 35 porcelain dolls on exhibition. Select a doll to read its story.",
   all="All", about_doll="About this doll", background="Background", details="Details",
   prev="Previous", next="Next", back="Back to collection",
   inquire="Ask on Instagram", buy_store="Buy on Naver Smart Store (Korea)", buy_etsy="Buy on Etsy",
   st_exhibit="On exhibition", st_available="Available", st_reserved="Reserved", st_sold="Sold",
   inquiry_note="For questions about this doll, please send us a message on Instagram.",
   about_title="About the Dolls", about_lead="A short guide for anyone new to porcelain dolls.",
   terms_title="Terms you will meet", sources_title="Sources",
   visit_title="Visit & Contact", visit_lead="We welcome questions about the exhibition and about buying a doll.",
   v_insta="Instagram", v_insta_text="New dolls and news appear here first. Send us a DM with any question.",
   v_shop="Buy online", v_shop_ko="In Korea: Naver Smart Store", v_shop_en="International: Etsy",
   v_soon="Coming soon", v_addr="Address", v_hours="Opening hours", v_email="Email", v_phone="Phone", v_map="Open map",
   biz="Business information", biz_name="Business name", biz_owner="Owner", biz_reg="Business registration no.", biz_mail="Mail-order business no.",
   nf_title="Page not found", nf_text="The page may have moved or no longer exists.", home="Home",
   dolls_count=" dolls"),
}
FEATURED = [2, 35, 9, 21, 20, 25]
HERO = [1, 2, 22]
KIND_GROUPS = {0: [0], 1: [2, 3, 4], 2: [5]}  # 원본 여부 확인 중(1), 확인 중(6) 그룹은 제외  # 종류 카드 -> 그룹 인덱스

# ---------- images ----------
def build_images():
    d = os.path.join(OUT, "assets", "img"); os.makedirs(d, exist_ok=True)
    for n in IDS:
        src = [f for f in glob.glob(os.path.join(ROOT, f"{n}.*")) if re.search(r"\.(jpe?g|png)$", f, re.I)][0]
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
        im = ImageOps.exif_transpose(Image.open([f for f in glob.glob(os.path.join(ROOT, f"{n}.*"))][0])).convert("RGB")
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
    t = T[lang]; other = t["other"]
    alt_path = path if alt_path is None else alt_path
    full_title = f"{title} | Adela Art Doll" if title else "Adela Art Doll | " + ("포슬린 인형 전시관" if lang == "ko" else "Porcelain Doll Gallery")
    canon = SITE["domain"] + url(lang, path)
    nav = [("collection/", t["nav_collection"]), ("about/", t["nav_about"]), ("visit/", t["nav_visit"])]
    CUR = ' aria-current="page"'
    navh = "".join(f'<a href="{url(lang,p)}"{CUR if path.startswith(p) else ""}>{e(l)}</a>' for p, l in nav)
    fonts = "family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Noto+Serif+KR:wght@500;600&family=Noto+Sans+KR:wght@400;500;600"
    foot_biz = ""
    bi = [(t["biz_name"], SITE["biz_name"]), (t["biz_owner"], SITE["biz_owner"]), (t["biz_reg"], SITE["biz_reg_no"]), (t["biz_mail"], SITE["mail_order_no"])]
    bi = [x for x in bi if x[1]]
    if bi: foot_biz = '<p class="biz">' + " / ".join(f"{e(k)} {e(v)}" for k, v in bi) + "</p>"
    verify = ""
    if SITE.get("google_site_verification"): verify += f'<meta name="google-site-verification" content="{e(SITE["google_site_verification"])}">\n'
    if SITE.get("naver_site_verification"): verify += f'<meta name="naver-site-verification" content="{e(SITE["naver_site_verification"])}">\n'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="ko" href="{SITE['domain']}{url('ko', alt_path if lang=='en' else path)}">
<link rel="alternate" hreflang="en" href="{SITE['domain']}{url('en', alt_path if lang=='ko' else path)}">
<link rel="alternate" hreflang="x-default" href="{SITE['domain']}{url('ko', alt_path if lang=='en' else path)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Adela Art Doll">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE['domain']}/assets/img/{og_img}">
<meta property="og:locale" content="{'ko_KR' if lang=='ko' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
{verify}<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}
</head>
<body class="lang-{lang}">
<a class="skip" href="#main">{'본문 바로가기' if lang=='ko' else 'Skip to content'}</a>
<header class="site-header">
 <div class="wrap bar">
  <a class="brand" href="{url(lang)}"><span class="mono">A</span><span class="wordmark">ADELA ART DOLL</span></a>
  <nav class="nav" aria-label="main">{navh}<a class="lang" href="{url(other, alt_path)}" hreflang="{other}">{t['other_label']}</a></nav>
 </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
 <div class="wrap foot">
  <div><a class="brand small" href="{url(lang)}"><span class="mono">A</span><span class="wordmark">ADELA ART DOLL</span></a>
  <p class="muted">{'포슬린 인형 전시관' if lang=='ko' else 'Porcelain Doll Gallery'}</p></div>
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
                         "addressRegion": "경기도" if lang == "ko" else "Gyeonggi-do", "addressCountry": "KR"}
    if SITE.get("opening_hours_schema"): ld["openingHours"] = SITE["opening_hours_schema"]
    head = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    return page(lang, "", "", t["site_desc"], body, extra_head=head)

def visit_block(lang, full=False):
    t = T[lang]
    rows = []
    if SITE.get("address_" + lang):
        a = e(SITE["address_" + lang])
        mu = SITE.get("map_url_" + lang) or SITE.get("map_url")
        if mu: a += f' <a class="maplink" href="{e(mu)}" target="_blank" rel="noopener">{e(t["v_map"])}</a>'
        rows.append((t["v_addr"], a))
    if SITE.get("hours_" + lang): rows.append((t["v_hours"], e(SITE["hours_" + lang])))
    if SITE.get("email"): rows.append((t["v_email"], f'<a href="mailto:{e(SITE["email"])}">{e(SITE["email"])}</a>'))
    if SITE.get("phone"): rows.append((t["v_phone"], f'<a href="tel:{e(SITE["phone"])}">{e(SITE["phone"])}</a>'))
    info = "".join(f"<dt>{e(k)}</dt><dd>{v}</dd>" for k, v in rows)
    def shop(label, u):
        return f'<li><span>{e(label)}</span>' + (f'<a class="btn small" href="{e(u)}" target="_blank" rel="noopener">{"바로가기" if lang=="ko" else "Visit"}</a>' if u else f'<em>{e(t["v_soon"])}</em>') + "</li>"
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
    # 참고 자료 (책자 마지막 부분) - 첫 줄 제목 제외, '  '로 시작하는 주석 문단 처리
    tail = L["tail"][2:]
    src = ""
    for line in tail:
        if line.startswith(("공개 자료로 확인되지", "Not confirmed", "Items not")): continue
        if ":" in line or "(" in line and len(line) > 60: src += f"<li>{e(line)}</li>"
        elif len(line) < 40: src += f'</ul><h3 class="h-small">{e(line)}</h3><ul class="sources">'
        else: src += "</ul><p>" + e(line) + '</p><ul class="sources">'
    body = f"""<section class="section page-head"><div class="wrap narrow"><h1 class="sec-title">{e(t['about_title'])}</h1><p class="lead">{e(t['about_lead'])}</p></div></section>
<section class="section"><div class="wrap"><div class="kinds">{kinds}</div></div></section>
<section class="section alt"><div class="wrap narrow"><h2 class="sec-title">{e(t['terms_title'])}</h2><dl class="terms">{terms}</dl></div></section>
<section class="section"><div class="wrap narrow"><h2 class="sec-title">{e(t['sources_title'])}</h2><div class="src"><p>{e(L["tail"][1])}</p><ul class="sources">{src}</ul></div></div></section>"""
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
    for lang in ("ko", "en"):
        pre = T[lang]["prefix"]
        write(pre + "/", home(lang)); write(pre + "/collection/", collection(lang))
        write(pre + "/about/", about(lang)); write(pre + "/visit/", visit(lang))
        for n in IDS: write(pre + f"/dolls/{n:02d}/", detail(lang, n))
        urls += [pre + "/", pre + "/collection/", pre + "/about/", pre + "/visit/"] + [pre + f"/dolls/{n:02d}/" for n in IDS]
    write("/404.html", notfound("ko"))
    write("/en/404.html", notfound("en"))
    today = date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE['domain']}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    write("/sitemap.xml", sm)
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
    write("/CNAME", SITE["domain"].replace("https://", "") + "\n")
    write("/.nojekyll", "")
    print("built", len(urls), "pages ->", OUT)

if __name__ == "__main__": main()
