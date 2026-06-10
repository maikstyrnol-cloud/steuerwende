#!/usr/bin/env python3
"""SteuerWende – Static Site Builder"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
PUBLISHED = ROOT / "articles" / "published"
OUTPUT = ROOT / "docs"

KATEGORIEN = ["wirtschaft", "politik", "gesellschaft", "klima", "sport", "hintergrund", "meinung"]

def slugify(text):
    text = text.lower()
    for a, b in [("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),(" ","-")]:
        text = text.replace(a, b)
    return re.sub(r'[^a-z0-9-]', '', text)[:60]

def format_date(iso):
    try:
        dt = datetime.fromisoformat(iso)
        m = ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
        return f"{dt.day}. {m[dt.month-1]} {dt.year}"
    except:
        return iso[:10]

def load_articles():
    articles = []
    for f in sorted(PUBLISHED.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            if "_meta" not in data:
                data["_meta"] = {}
            if "slug" not in data["_meta"]:
                data["_meta"]["slug"] = slugify(data.get("titel", f.stem))
            if "erstellt" not in data["_meta"]:
                data["_meta"]["erstellt"] = datetime.now().isoformat()
            articles.append(data)
        except Exception as e:
            print(f"⚠️  {f}: {e}")
    return articles

def nav(root=""):
    return f"""
        <a href="{root}index.html">Startseite</a>
        <a href="{root}kategorie/wirtschaft.html">Wirtschaft</a>
        <a href="{root}kategorie/politik.html">Politik</a>
        <a href="{root}kategorie/gesellschaft.html">Gesellschaft</a>
        <a href="{root}kategorie/klima.html">Klima</a>
        <a href="{root}kategorie/sport.html">Sport</a>
        <a href="{root}kategorie/meinung.html">Meinung</a>"""

def footer_html(root=""):
    year = datetime.now().year
    return f"""
  <footer>
    <div class="footer-inner">
      <div class="footer-brand">
        <div class="logo">Steuer<span>Wende</span></div>
        <p>Unabhängige Recherche- und Analyseplattform für Steuergerechtigkeit.<br/>Keine Werbung. Keine Paywall.</p>
      </div>
      <div class="footer-links">
        <a href="{root}impressum.html">Impressum</a>
        <a href="{root}datenschutz.html">Datenschutz</a>
        <a href="{root}ueber-uns.html">Über uns</a>
      </div>
      <p class="footer-copy">© {year} SteuerWende</p>
    </div>
  </footer>
</body></html>"""

def page_wrap(title, content, root="", description=""):
    today = datetime.now().strftime("%d.%m.%Y")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="description" content="{description}"/>
  <title>{title} – SteuerWende</title>
  <link rel="stylesheet" href="{root}style.css"/>
  <link rel="icon" type="image/svg+xml" href="{root}favicon.svg"/>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet"/>
</head>
<body>
  <div class="topbar">{today} <span class="sep">|</span> <strong>SteuerWende</strong> – Wer zahlt? Wer profitiert? Wer entscheidet?</div>
  <header class="masthead">
    <div class="masthead-inner">
      <a href="{root}index.html" class="site-title">Steuer<span>Wende</span></a>
      <div class="site-tagline">Unabhängige Analyse · Wirtschaft · Politik · Gesellschaft</div>
      <nav class="main-nav">{nav(root)}</nav>
    </div>
  </header>
  <div class="thesis-banner">
    <p>Arbeit wird in Deutschland höher besteuert als fast überall sonst. Vermögen kaum. <strong>Wir fragen, was das für uns alle bedeutet.</strong></p>
  </div>
  {content}
  {footer_html(root)}"""

def article_card(a, root=""):
    slug = a["_meta"]["slug"]
    datum = format_date(a["_meta"].get("erstellt",""))
    kat = a.get("kategorie","")
    kat_slug = slugify(kat)
    untertitel = a.get("untertitel","")[:120]
    svg = a.get("infografik_svg","")
    if svg:
        # SVG verkleinert als Vorschau einbetten
        preview = '<div class="card-img card-svg">' + svg + '</div>'
    else:
        preview = '<div class="card-img cat-' + kat_slug + '"></div>'
    return f"""
    <div class="article-card">
      {preview}
      <div class="card-body">
        <span class="card-kicker">{kat}</span>
        <h3><a href="{root}artikel/{slug}.html">{a.get("titel","")}</a></h3>
        <p>{untertitel}</p>
        <div class="card-meta"><span>{datum}</span><span>{a.get("lesezeit",7)} Min.</span></div>
      </div>
    </div>"""

def build_index(articles, out):
    hero = ""
    if articles:
        a = articles[0]
        slug = a["_meta"]["slug"]
        datum = format_date(a["_meta"].get("erstellt",""))
        kat_slug = slugify(a.get("kategorie",""))
        svg = a.get("infografik_svg","")
        hero_img = '<div class="hero-img hero-svg">' + svg + '</div>' if svg else f'<div class="hero-img cat-{kat_slug}"></div>'
        hero = f"""
    <div class="hero-card">
      {hero_img}
      <div class="hero-content">
        <span class="kicker">{a.get("kategorie","")}</span>
        <h2><a href="artikel/{slug}.html">{a.get("titel","")}</a></h2>
        <p class="deck">{a.get("untertitel","")}</p>
        <div class="meta">{datum} · {a.get("lesezeit",7)} Min. Lesezeit</div>
      </div>
    </div>"""

    cards = "".join(article_card(a) for a in articles[1:13])

    content = f"""
  <section class="hero-section"><div class="container">{hero}</div></section>
  <div class="stat-strip"><div class="container stat-grid">
    <div class="stat-item"><span class="stat-number">47,8%</span><span class="stat-label">Steuer- & Abgabenlast auf Arbeit</span><span class="stat-source">OECD 2024</span></div>
    <div class="stat-item"><span class="stat-number">0%</span><span class="stat-label">Vermögensteuer in Deutschland</span><span class="stat-source">seit 1997</span></div>
    <div class="stat-item"><span class="stat-number">56%</span><span class="stat-label">Privatvermögen beim reichsten Zehntel</span><span class="stat-source">Bundesbank 2021</span></div>
    <div class="stat-item"><span class="stat-number">90 Mrd.</span><span class="stat-label">Potenzial einer 1%-Vermögensteuer/Jahr</span><span class="stat-source">DIW Berlin</span></div>
  </div></div>
  <section class="article-grid-section"><div class="container">
    <div class="section-divider"><div class="line"></div><div class="label">Aktuelle Artikel</div><div class="line thin"></div></div>
    <div class="article-grid">{cards}</div>
  </div></section>"""

    (out / "index.html").write_text(page_wrap("Startseite", content, "", "SteuerWende – Unabhängige Recherche- und Analyseplattform für Steuergerechtigkeit"))
    print("  ✅ index.html")

def build_article_page(article, out):
    slug = article["_meta"]["slug"]
    datum = format_date(article["_meta"].get("erstellt",""))
    dh = article.get("daten_highlight", {})

    dh_html = ""
    if dh:
        dh_html = f"""<div class="daten-highlight container"><div class="dh-inner">
      <span class="dh-zahl">{dh.get("zahl","")}</span>
      <span class="dh-text">{dh.get("beschreibung","")}</span>
      <span class="dh-quelle">Quelle: {dh.get("quelle","")}</span>
    </div></div>"""

    quellen_html = "".join(
        f'<li>{q.get("autor","")}: <em>{q.get("titel","")}</em> ({q.get("jahr","")})</li>'
        for q in article.get("quellen", [])
    )
    tags_html = " ".join(f'<span class="tag">{t}</span>' for t in article.get("tags", []))

    content = f"""
  <article class="article-page">
    <div class="article-header container">
      <span class="kicker">{article.get("kategorie","")}</span>
      <h1>{article.get("titel","")}</h1>
      <p class="deck">{article.get("untertitel","")}</p>
      <div class="article-meta">Von der Redaktion <span class="sep">·</span> {datum} <span class="sep">·</span> {article.get("lesezeit",7)} Min. Lesezeit</div>
    </div>
    {dh_html}
    <div class="article-body container">
      {"<div class='infografik-wrap'>" + article["infografik_svg"] + "</div>" if article.get("infografik_svg") else ""}
      {article.get("inhalt","")}
      <div class="sources-box"><h3>Quellen & Belege</h3><ol>{quellen_html}</ol></div>
    </div>
    <div class="article-footer container">
      <div class="tags">{tags_html}</div>
    </div>
  </article>"""

    path = out / "artikel" / f"{slug}.html"
    path.write_text(page_wrap(article.get("titel",""), content, "../"))
    print(f"  ✅ artikel/{slug}.html")

def build_kategorie_pages(articles, out):
    for kat in KATEGORIEN:
        filtered = [a for a in articles if slugify(a.get("kategorie","")) == kat]
        kat_label = kat.capitalize()
        cards = "".join(article_card(a, "../") for a in filtered) if filtered else "<p style='padding:40px;color:#888'>Noch keine Artikel in dieser Kategorie.</p>"
        content = f"""
  <section class="article-grid-section" style="padding-top:32px"><div class="container">
    <div class="section-divider"><div class="line"></div><div class="label">{kat_label}</div><div class="line thin"></div></div>
    <div class="article-grid">{cards}</div>
  </div></section>"""
        path = out / "kategorie" / f"{kat}.html"
        path.write_text(page_wrap(kat_label, content, "../"))
    print(f"  ✅ {len(KATEGORIEN)} Kategorie-Seiten")

def build_static_pages(out):
    # Impressum
    content = """
  <main class="article-page">
    <div class="article-header container">
      <span class="kicker">Rechtliches</span>
      <h1>Impressum</h1>
      <p class="deck">Angaben gemäß § 5 TMG</p>
    </div>
    <div class="article-body container">
      <h2>Verantwortlich für den Inhalt</h2>
      <p>Maik Styrnol<br/>Blumenstr. 13<br/>79194 Gundelfingen<br/>Deutschland</p>
      <h2>Kontakt</h2>
      <p>E-Mail: <a href="mailto:redaktion@steuerwende.de">redaktion@steuerwende.de</a></p>
      <h2>Redaktionell verantwortlich</h2>
      <p>Maik Styrnol<br/>Blumenstr. 13, 79194 Gundelfingen</p>
      <h2>Redaktionelle Inhalte</h2>
      <p>SteuerWende ist ein unabhängiges, nicht-kommerzielles Informationsangebot.
      Die Plattform verfolgt keine wirtschaftlichen Eigeninteressen und nimmt keine
      Werbung an. Alle Inhalte dienen der sachlichen Information und politischen
      Meinungsbildung im Sinne des demokratischen Diskurses.</p>
      <h2>Haftung für Inhalte</h2>
      <p>Als Diensteanbieter sind wir gemäß § 7 Abs. 1 TMG für eigene Inhalte auf
      diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10
      TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder
      gespeicherte fremde Informationen zu überwachen.</p>
      <h2>Haftung für Links</h2>
      <p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte
      wir keinen Einfluss haben. Für die Inhalte der verlinkten Seiten ist stets der
      jeweilige Anbieter verantwortlich.</p>
      <h2>Urheberrecht</h2>
      <p>Die durch die Seitenbetreiber erstellten Inhalte unterliegen dem deutschen
      Urheberrecht. Downloads sind nur für den privaten, nicht kommerziellen
      Gebrauch gestattet.</p>
    </div>
  </main>"""
    (out / "impressum.html").write_text(page_wrap("Impressum", content))

    # Datenschutz
    content = """
  <main class="article-page">
    <div class="article-header container">
      <span class="kicker">Rechtliches</span>
      <h1>Datenschutzerklärung</h1>
      <p class="deck">SteuerWende verwendet kein Tracking, keine Cookies, keine Werbung.</p>
    </div>
    <div class="article-body container">
      <h2>1. Verantwortlicher</h2>
      <p>Siehe <a href="impressum.html">Impressum</a>.</p>
      <h2>2. Hosting</h2>
      <p>GitHub Pages (GitHub Inc., USA). GitHub kann technische Zugriffsdaten speichern.
      Siehe <a href="https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement" target="_blank">GitHub Privacy Statement</a>.</p>
      <h2>3. Cookies und Tracking</h2>
      <p>SteuerWende verwendet <strong>keine Cookies</strong> und kein Tracking.</p>
      <h2>4. Google Fonts</h2>
      <p>Diese Website lädt Schriftarten von Google Fonts. Dabei wird Ihre IP-Adresse an Google übermittelt.</p>
      <h2>5. Ihre Rechte</h2>
      <p>Auskunft, Berichtigung, Löschung: <a href="mailto:redaktion@steuerwende.de">redaktion@steuerwende.de</a></p>
    </div>
  </main>"""
    (out / "datenschutz.html").write_text(page_wrap("Datenschutz", content))

    # Über uns
    content = """
  <main class="article-page">
    <div class="article-header container">
      <span class="kicker">Über diese Seite</span>
      <h1>Warum es SteuerWende gibt</h1>
      <p class="deck">In Deutschland wird besteuert, wer arbeitet. Wer Vermögen besitzt, kaum.
      Das ist keine Naturgewalt – es ist eine politische Entscheidung.</p>
    </div>
    <div class="article-body container">
      <p>Ein Arbeitnehmer mit mittlerem Einkommen zahlt fast die Hälfte seines Bruttogehalts
      an den Staat. Wer Millionen erbt oder von Kapitalerträgen lebt, zahlt einen Bruchteil davon.</p>
      <p>Das ist das Ergebnis von Jahrzehnten gezielter Steuerpolitik – beeinflusst von
      Lobbyverbänden, verteidigt von Parteien, unsichtbar für die meisten Menschen.</p>
      <blockquote><p>SteuerWende existiert, weil Steuerpolitik zu wichtig ist,
      um sie Ökonomen und Lobbyisten zu überlassen.</p></blockquote>
      <p>Wir schreiben über Wirtschaft, Politik, Klima, Gesellschaft und Sport –
      immer mit demselben Blickwinkel: Wer profitiert? Wer zahlt?</p>
      <p>Alle Artikel stützen sich auf belegbare Daten: OECD, DIW Berlin, Deutsche Bundesbank,
      Statistisches Bundesamt, sowie Forschung von Thomas Piketty und Gabriel Zucman.</p>
      <h2>Unsere Grundsätze</h2>
      <p><strong>Keine Werbung.</strong> Nicht kommerziell, keine Abhängigkeiten.</p>
      <p><strong>Keine Paywall.</strong> Alle Inhalte kostenlos zugänglich.</p>
      <p><strong>Nur belegbare Quellen.</strong> Jede Zahl nachprüfbar belegt.</p>
      <p><strong>Kein Tracking.</strong> Keine Cookies, kein Analytics.</p>
      <p>Kontakt: <a href="mailto:redaktion@steuerwende.de">redaktion@steuerwende.de</a></p>
    </div>
  </main>"""
    (out / "ueber-uns.html").write_text(page_wrap("Über uns", content))
    print("  ✅ impressum.html, datenschutz.html, ueber-uns.html")

def build_site():
    print("🔨 Baue SteuerWende Website...")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "artikel").mkdir(exist_ok=True)
    (OUTPUT / "kategorie").mkdir(exist_ok=True)

    css_src = ROOT / "static" / "css" / "main.css"
    if css_src.exists():
        shutil.copy(css_src, OUTPUT / "style.css")
    favicon_src = ROOT / "static" / "favicon.svg"
    if favicon_src.exists():
        shutil.copy(favicon_src, OUTPUT / "favicon.svg")

    articles = load_articles()
    print(f"  📚 {len(articles)} Artikel")

    for a in articles:
        build_article_page(a, OUTPUT)

    build_index(articles, OUTPUT)
    build_kategorie_pages(articles, OUTPUT)
    build_static_pages(OUTPUT)

    total = len(list(OUTPUT.rglob("*.html")))
    print(f"✅ Fertig: {total} HTML-Seiten")

if __name__ == "__main__":
    build_site()

# CSS-Ergaenzung fuer Infografiken (wird in main.css benoetigt):
# .infografik-wrap {
#   background: white;
#   border: 1px solid #e8e4da;
#   border-left: 4px solid #c8102e;
#   padding: 20px 24px;
#   margin: 24px 0;
# }
