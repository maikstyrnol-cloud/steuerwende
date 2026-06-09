#!/usr/bin/env python3
import anthropic
import json
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path

THEMEN = [
    {"kategorie": "Wirtschaft", "thema": "Erbschaftsteuer und Unternehmensübertragung", "winkel": "Warum Milliardenerben fast keine Steuern zahlen", "keywords": ["Erbschaftsteuer Deutschland", "Betriebsvermögen Steuerbefreiung"]},
    {"kategorie": "Gesellschaft", "thema": "Wohnungskrise und Immobilienvermögen", "winkel": "Während Mieten explodieren, wächst Immobilienvermögen steuerfrei", "keywords": ["Immobiliensteuer Deutschland", "Grundsteuer Reform"]},
    {"kategorie": "Klima", "thema": "CO2-Steuer und soziale Gerechtigkeit", "winkel": "Die CO2-Steuer trifft Pendler härter als Privatjet-Besitzer", "keywords": ["CO2 Steuer sozial", "Klimasteuer Verteilung"]},
    {"kategorie": "Politik", "thema": "Lobbyismus in der Steuerpolitik", "winkel": "Wie Vermögensverbände seit Jahrzehnten Steuerpolitik mitschreiben", "keywords": ["BDI Steuerpolitik Lobbying", "Steuerreform blockiert"]},
    {"kategorie": "Sport", "thema": "Profifußball und Steueroptimierung", "winkel": "Bundesliga-Klubs als Steuerkonstrukte", "keywords": ["Bundesliga Steuer", "Fußball GmbH Steuer"]},
    {"kategorie": "Hintergrund", "thema": "Das schwedische Modell", "winkel": "Was Deutschland von Skandinavien lernen kann", "keywords": ["Schweden Vermögenteuer", "Nordeuropa Steuermodell"]},
    {"kategorie": "Wirtschaft", "thema": "Kapitalertragssteuer im Vergleich", "winkel": "25% auf Kapitalerträge, 45% auf Arbeit: Deutschland bevorzugt Kapital", "keywords": ["Abgeltungssteuer", "Kapitalertragsteuer Reform"]},
    {"kategorie": "Gesellschaft", "thema": "Altersarmut und Vermögenskonzentration", "winkel": "Wer ein Leben lang gearbeitet hat, ist im Alter arm. Wer geerbt hat, nicht.", "keywords": ["Altersarmut Deutschland", "Rentenarmut Vermögen"]},
    {"kategorie": "Politik", "thema": "EU-Vermögensteuer Initiativen", "winkel": "Gabriel Zucman schlägt eine globale Milliardärssteuer vor", "keywords": ["Zucman Milliardärssteuer", "EU Vermögensteuer"]},
    {"kategorie": "Hintergrund", "thema": "Geschichte der deutschen Vermögensteuer", "winkel": "Von der Kaiserzeit bis 1997: Wie die Vermögensteuer abgeschafft wurde", "keywords": ["Vermögensteuer Geschichte", "BVerfG 1995 Urteil"]},
    {"kategorie": "Wirtschaft", "thema": "Vermögenszuwachs in Krisenzeiten", "winkel": "Während der Pandemie verloren Arbeitnehmer Jobs – Vermögen der Reichsten wuchs", "keywords": ["Corona Vermögen", "Pandemie Ungleichheit Deutschland"]},
    {"kategorie": "Gesellschaft", "thema": "Pflege und Vermögenssteuer", "winkel": "Pflegekräfte gehören zu den meistbesteuerten Berufsgruppen", "keywords": ["Pflegesteuer", "Sozialbeiträge Pflege"]},
]

SYSTEM_PROMPT = """Du bist Redakteur bei SteuerWende. Antworte NUR mit rohem JSON, ohne Markdown, ohne Codeblöcke, ohne Erklärungen davor oder danach.

WICHTIGSTE REGEL: Schreibe NIEMALS über einzelne namentlich genannte Personen. Keine Artikel über Politiker, Unternehmer, Prominente oder andere Privatpersonen. Schreibe ausschließlich über Systeme, Strukturen, Gesetze und Statistiken. Statt "Milliardär X zahlt keine Steuern" schreibe "Milliardäre zahlen kaum Steuern - die strukturellen Gründe".

Das JSON muss exakt dieses Format haben:
{"titel": "...", "untertitel": "...", "kategorie": "...", "lesezeit": 7, "inhalt": "<p>HTML hier</p>", "daten_highlight": {"zahl": "47%", "beschreibung": "...", "quelle": "OECD 2024"}, "quellen": [{"autor": "...", "titel": "...", "jahr": 2024, "url": "https://..."}], "seo_beschreibung": "...", "tags": ["Tag1", "Tag2"]}

Stil: Seriös wie Süddeutsche Zeitung, mit echten belegbaren Zahlen (OECD, DIW, Bundesbank), 600-900 Wörter, Alltagsbeispiele. Das Thema Vermögens- vs. Einkommensteuer als roter Faden."""


def get_thema(drafts_dir, published_dir):
    used = set()
    for f in list(drafts_dir.glob("*.json")) + list(published_dir.glob("*.json")):
        try:
            used.add(json.loads(f.read_text()).get("kategorie", ""))
        except Exception:
            pass
    unused = [t for t in THEMEN if t["kategorie"] not in used]
    return random.choice(unused if unused else THEMEN)


def generate_article(thema):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""Schreibe einen Artikel für SteuerWende.

Kategorie: {thema['kategorie']}
Thema: {thema['thema']}
Winkel: {thema['winkel']}
Keywords: {', '.join(thema['keywords'])}

WICHTIG: Antworte NUR mit dem rohen JSON-Objekt. Kein ```json, keine Erklärungen, nur JSON."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
        system=SYSTEM_PROMPT,
    )

    raw = message.content[0].text.strip()
    print(f"Roh-Antwort Anfang: {repr(raw[:80])}")

    # Alle Backtick-Blöcke entfernen
    raw = re.sub(r'```(?:json)?', '', raw).strip()

    # JSON-Objekt extrahieren
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"Kein JSON gefunden: {raw[:200]}")

    return json.loads(raw[start:end])


def save_article(article, thema, drafts_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    slug = re.sub(r'[^a-z0-9-]', '', article["titel"].lower()
        .replace(" ", "-").replace("ä","ae").replace("ö","oe")
        .replace("ü","ue").replace("ß","ss"))[:60]
    filename = f"{timestamp}_{slug}.json"
    article["_meta"] = {
        "erstellt": datetime.now().isoformat(),
        "status": "entwurf",
        "slug": slug,
        "filename": filename,
    }
    path = drafts_dir / filename
    path.write_text(json.dumps(article, ensure_ascii=False, indent=2))
    print(f"✅ Gespeichert: {path}")
    return path


def main():
    root = Path(__file__).parent.parent
    drafts_dir = root / "articles" / "drafts"
    published_dir = root / "articles" / "published"
    drafts_dir.mkdir(parents=True, exist_ok=True)
    published_dir.mkdir(parents=True, exist_ok=True)

    thema = get_thema(drafts_dir, published_dir)
    print(f"📝 Generiere Artikel: {thema['thema']}")

    try:
        article = generate_article(thema)
        save_article(article, thema, drafts_dir)
        print(f"🎉 Fertig: {article['titel']}")
    except Exception as e:
        print(f"❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
