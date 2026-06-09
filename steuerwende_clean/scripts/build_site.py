#!/usr/bin/env python3
"""
SteuerWende – Static Site Builder
Wandelt alle veröffentlichten JSON-Artikel in HTML-Seiten um
und baut die komplette Website (Index, Artikel, Kategorien).
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
PUBLISHED = ROOT / "articles" / "published"
OUTPUT = ROOT / "docs"  # GitHub Pages liest aus /docs


# ── HTML-Templates ─────────────────────────────────────────────────────────────

BASE_HTML = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="description" content="{meta_description}"/>
  <title>{page_title} – SteuerWende</title>
  <link rel="canonical" href="https://steuerwende.de/{canonical}"/>
  <link rel="stylesheet" href="{css_path}style.css"/>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet"/>
  <!-- Open Graph -->
  <meta property="og:title" content="{page_title}"/>
  <meta property="og:description" content="{meta_description}"/>
  <meta property="og:type" content="{og_type}"/>
  <meta property="og:site_name" content="SteuerWende"/>
</head>
<body>
  <div class="topbar">
    <span class="date">{today}</span>
    <span class="sep">|</span>
    <strong>SteuerWende</strong> – Wer zahlt? Wer profitiert? Wer entscheidet?
  </div>
  <header class="masthead">
    <div class="masthead-inner">
      <a href="{root_path}index.html" class="site-title">Steuer<span>Wende</span></a>
      <div class="site-tagline">Unabhängige Analyse · Wirtschaft · Politik · Gesellschaft</div>
      <nav class="main-nav">
        <a href="{root_path}index.html">Startseite</a>
        <a href="{root_path}kategorie/wirtschaft.html">Wirtschaft</a>
        <a href="{root_path}kategorie/politik.html">Politik</a>
        <a href="{root_path}kategorie/gesellschaft.html">Gesellschaft</a>
        <a href="{root_path}kategorie/klima.html">Klima</a>
        <a href="{root_path}kategorie/sport.html">Sport</a>
        <a href="{root_path}kategorie/meinung.html">Meinung</a>
      </nav>
    </div>
  </header>
  <div class="thesis-banner">
    <p>Arbeit wird in Deutschland höher besteuert als fast überall sonst.
    Vermögen kaum. <strong>Wir fragen, was das für uns alle bedeutet.</strong></p>
  </div>

  {body_content}

  <footer>
    <div class="footer-inner">
      <div class="footer-brand">
        <div class="logo">Steuer<span>Wende</span></div>
        <p>Unabhängiger Journalismus für ein gerechtes Steuersystem.<br/>
        Keine Werbung. Keine Paywall. Nur Haltung.</p>
      </div>
      <div class="footer-links">
        <a href="{root_path}impressum.html">Impressum</a>
        <a href="{root_path}datenschutz.html">Datenschutz</a>
        <a href="{root_path}ueber-uns.html">Über uns</a>
      </div>
      <p class="footer-copy">© {year} SteuerWende</p>
    </div>
  </footer>
</body>
</html>"""


ARTICLE_BODY = """
  <article class="article-page">
    <div class="article-header">
      <div class="container">
        <span class="kicker">{kategorie}</span>
        <h1>{titel}</h1>
        <p class="deck">{untertitel}</p>
        <div class="article-meta">
          <span>Von der Redaktion</span>
          <span class="sep">·</span>
          <span>{datum}</span>
          <span class="sep">·</span>
          <span>{lesezeit} Min. Lesezeit</span>
        </div>
      </div>
    </div>

    {daten_highlight_html}

    <div class="article-body container">
      {inhalt}

      <div class="sources-box">
        <h3>Quellen & Belege</h3>
        <ol>
          {quellen_html}
        </ol>
      </div>
    </div>

    <div class="article-footer container">
      <div class="tags">
        {tags_html}
      </div>
      <div class="share">
        <span>Teilen:</span>
        <a href="https://twitter.com/intent/tweet?text={titel_encoded}&url=https://steuerwende.de/artikel/{slug}.html" 
           target="_blank" rel="noopener">Twitter/X</a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://steuerwende.de/artikel/{slug}.html"
           target="_blank" rel="noopener">LinkedIn</a>
      </div>
    </div>
  </article>
"""

INDEX_BODY = """
  <section class="hero-section">
    <div class="container">
      {hero_html}
    </div>
  </section>

  <div class="stat-strip">
    <div class="container stat-grid">
      <div class="stat-item">
        <span class="stat-number">47,8%</span>
        <span class="stat-label">Steuer- & Abgabenlast auf Arbeit</span>
        <span class="stat-source">OECD Taxing Wages 2024</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">0%</span>
        <span class="stat-label">Vermögensteuer in Deutschland</span>
        <span class="stat-source">seit Aussetzung 1997</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">56%</span>
        <span class="stat-label">Privatvermögen beim reichsten Zehntel</span>
        <span class="stat-source">Bundesbank PHF 2021</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">90 Mrd.</span>
        <span class="stat-label">Potenzielle Einnahmen einer 1%-Vermögensteuer</span>
        <span class="stat-source">DIW Berlin 2016/2021</span>
      </div>
    </div>
  </div>

  <section class="article-grid-section">
    <div class="container">
      <div class="section-divider">
        <div class="line"></div>
        <div class="label">Aktuelle Artikel</div>
        <div class="line thin"></div>
      </div>
      <div class="article-grid">
        {article_cards_html}
      </div>
    </div>
  </section>
"""

ARTICLE_CARD = """
  <div class="article-card">
    <div class="card-img cat-{kategorie_slug}"></div>
    <div class="card-body">
      <span class="card-kicker">{kategorie}</span>
      <h3><a href="../artikel/{slug}.html">{titel}</a></h3>
      <p>{untertitel_short}</p>
      <div class="card-meta">
        <span>{datum}</span>
        <span>{lesezeit} Min.</span>
      </div>
    </div>
  </div>
"""


# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = open(ROOT / "static" / "css" / "main.css").read() if (ROOT / "static" / "css" / "main.css").exists() else ""


def slugify(text: str) -> str:
    text = text.lower()
    for a, b in [("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),(" ","-")]:
        text = text.replace(a, b)
    return "".join(c for c in text if c.isalnum() or c == "-")[:60]


def format_date(iso_date: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_date)
        months = ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
        return f"{dt.day}. {months[dt.month-1]} {dt.year}"
    except Exception:
        return iso_date[:10]


def load_articles() -> list:
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
            print(f"⚠️  Fehler beim Laden von {f}: {e}")
    return articles


def build_article_page(article: dict, output_dir: Path):
    slug = article["_meta"]["slug"]
    datum = format_date(article["_meta"].get("erstellt", ""))

    # Quellen HTML
    quellen_html = ""
    for q in article.get("quellen", []):
        url = q.get("url", "")
        link = f'<a href="{url}" target="_blank" rel="noopener">{url}</a>' if url else ""
        quellen_html += f'<li>{q.get("autor","")}: <em>{q.get("titel","")}</em> ({q.get("jahr","")}). {link}</li>\n'

    # Tags HTML
    tags_html = " ".join(f'<span class="tag">{t}</span>' for t in article.get("tags", []))

    # Daten-Highlight
    dh = article.get("daten_highlight", {})
    daten_highlight_html = ""
    if dh:
        daten_highlight_html = f"""
    <div class="daten-highlight container">
      <div class="dh-inner">
        <span class="dh-zahl">{dh.get('zahl','')}</span>
        <span class="dh-text">{dh.get('beschreibung','')}</span>
        <span class="dh-quelle">Quelle: {dh.get('quelle','')}</span>
      </div>
    </div>"""

    import urllib.parse
    body = ARTICLE_BODY.format(
        kategorie=article.get("kategorie", ""),
        titel=article.get("titel", ""),
        untertitel=article.get("untertitel", ""),
        datum=datum,
        lesezeit=article.get("lesezeit", 7),
        daten_highlight_html=daten_highlight_html,
        inhalt=article.get("inhalt", ""),
        quellen_html=quellen_html,
        tags_html=tags_html,
        slug=slug,
        titel_encoded=urllib.parse.quote(article.get("titel", ""))
    )

    html = BASE_HTML.format(
        page_title=article.get("titel", ""),
        meta_description=article.get("seo_beschreibung", "")[:160],
        canonical=f"artikel/{slug}.html",
        css_path="../",
        og_type="article",
        today=datetime.now().strftime("%d.%m.%Y"),
        root_path="../",
        year=datetime.now().year,
        body_content=body
    )

    out_path = output_dir / "artikel" / f"{slug}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)
    print(f"  ✅ {slug}.html")


def build_index(articles: list, output_dir: Path):
    # Hero: neuester Artikel
    hero_html = ""
    if articles:
        a = articles[0]
        slug = a["_meta"]["slug"]
        datum = format_date(a["_meta"].get("erstellt", ""))
        hero_html = f"""
      <div class="hero-card">
        <div class="hero-img cat-{slugify(a.get('kategorie',''))}"></div>
        <div class="hero-content">
          <span class="kicker">{a.get('kategorie','')}</span>
          <h2><a href="artikel/{slug}.html">{a.get('titel','')}</a></h2>
          <p class="deck">{a.get('untertitel','')}</p>
          <div class="meta">{datum} · {a.get('lesezeit',7)} Min. Lesezeit</div>
        </div>
      </div>"""

    # Artikel-Karten (ohne den ersten)
    cards_html = ""
    for a in articles[1:13]:  # max 12 Karten
        slug = a["_meta"]["slug"]
        datum = format_date(a["_meta"].get("erstellt", ""))
        untertitel = a.get("untertitel", "")[:120] + ("…" if len(a.get("untertitel","")) > 120 else "")
        cards_html += ARTICLE_CARD.format(
            kategorie=a.get("kategorie", ""),
            kategorie_slug=slugify(a.get("kategorie", "")),
            slug=slug,
            titel=a.get("titel", ""),
            untertitel_short=untertitel,
            datum=datum,
            lesezeit=a.get("lesezeit", 7)
        )

    body = INDEX_BODY.format(
        hero_html=hero_html,
        article_cards_html=cards_html
    )

    html = BASE_HTML.format(
        page_title="Startseite",
        meta_description="SteuerWende – Unabhängiger Journalismus für ein gerechtes Steuersystem. Warum Arbeit besteuert wird, Vermögen kaum.",
        canonical="index.html",
        css_path="",
        og_type="website",
        today=datetime.now().strftime("%d.%m.%Y"),
        root_path="",
        year=datetime.now().year,
        body_content=body
    )

    (output_dir / "index.html").write_text(html)
    print("  ✅ index.html")


def build_site():
    print("🔨 Baue SteuerWende Website...")

    # Output-Ordner vorbereiten
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "artikel").mkdir(exist_ok=True)
    (OUTPUT / "kategorie").mkdir(exist_ok=True)

    # CSS kopieren
    css_src = ROOT / "static" / "css" / "main.css"
    if css_src.exists():
        shutil.copy(css_src, OUTPUT / "style.css")

    # Artikel laden
    articles = load_articles()
    print(f"  📚 {len(articles)} veröffentlichte Artikel gefunden")

    # Seiten bauen
    for article in articles:
        build_article_page(article, OUTPUT)

    build_index(articles, OUTPUT)

    print(f"✅ Website gebaut: {OUTPUT}")
    print(f"   {len(articles)} Artikel · {len(list(OUTPUT.rglob('*.html')))} HTML-Seiten")


if __name__ == "__main__":
    build_site()
