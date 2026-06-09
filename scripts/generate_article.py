#!/usr/bin/env python3
"""
SteuerWende – Artikel-Generator
Ruft die Claude API auf, generiert einen Artikel als Entwurf
und speichert ihn im /articles/drafts/ Ordner.
"""

import anthropic
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

# ── Themen-Pool ────────────────────────────────────────────────────────────────
# Jedes Thema hat eine Kategorie, einen Winkel und Keywords für die Recherche.
# Das System rotiert durch diese Liste, damit keine Wiederholungen entstehen.

THEMEN = [
    {
        "kategorie": "Wirtschaft",
        "thema": "Erbschaftsteuer und Unternehmensübertragung",
        "winkel": "Warum Milliardenerben fast keine Steuern zahlen – und welche Schlupflöcher das ermöglichen",
        "keywords": ["Erbschaftsteuer Deutschland", "Betriebsvermögen Steuerbefreiung", "DIW Erbschaft"]
    },
    {
        "kategorie": "Gesellschaft",
        "thema": "Wohnungskrise und Immobilienvermögen",
        "winkel": "Während Mieten explodieren, wächst Immobilienvermögen steuerfrei – die strukturellen Ursachen",
        "keywords": ["Immobiliensteuer Deutschland", "Grundsteuer Reform", "Wohnungskrise Vermögen"]
    },
    {
        "kategorie": "Klima",
        "thema": "CO2-Steuer und soziale Gerechtigkeit",
        "winkel": "Die CO2-Steuer trifft Pendler härter als Privatjet-Besitzer – eine Analyse der Verteilungswirkung",
        "keywords": ["CO2 Steuer sozial", "Klimasteuer Verteilung", "Energiesteuer Einkommen"]
    },
    {
        "kategorie": "Politik",
        "thema": "Lobbyismus in der Steuerpolitik",
        "winkel": "Wie Vermögensverbände seit Jahrzehnten Steuerpolitik mitschreiben – und wer das finanziert",
        "keywords": ["BDI Steuerpolitik Lobbying", "Steuerreform blockiert", "Vermögenssteuer Widerstand"]
    },
    {
        "kategorie": "Sport",
        "thema": "Profifußball und Steueroptimierung",
        "winkel": "Bundesliga-Klubs als Steuerkonstrukte: Wie Vereinsvermögen und Spielergehälter optimiert werden",
        "keywords": ["Bundesliga Steuer", "Fußball GmbH Steuer", "Sportverein Gemeinnützigkeit"]
    },
    {
        "kategorie": "Hintergrund",
        "thema": "Das schwedische Modell",
        "winkel": "Schweden schaffte die Vermögensteuer ab – und führte dafür andere Umverteilungsmechanismen ein. Was Deutschland daraus lernen kann",
        "keywords": ["Schweden Vermögensteuer", "Nordeuropa Steuermodell", "Ungleichheit Skandinavien"]
    },
    {
        "kategorie": "Wirtschaft",
        "thema": "Kapitalertragssteuer im Vergleich",
        "winkel": "25% auf Kapitalerträge, 45% auf Arbeit: Warum Deutschland Kapital systematisch bevorzugt",
        "keywords": ["Abgeltungssteuer", "Kapitalertragsteuer Reform", "Einkommensteuer Kapital"]
    },
    {
        "kategorie": "Gesellschaft",
        "thema": "Altersarmut und Vermögenskonzentration",
        "winkel": "Wer ein Leben lang gearbeitet hat, ist im Alter arm. Wer geerbt hat, nicht. Die Zahlen sind erschreckend",
        "keywords": ["Altersarmut Deutschland", "Rentenarmut Vermögen", "DIW Altersvorsorge"]
    },
    {
        "kategorie": "Politik",
        "thema": "EU-Vermögensteuer Initiativen",
        "winkel": "Gabriel Zucman schlägt eine globale Milliardärssteuer vor – wie realistisch ist das, und was würde es bringen?",
        "keywords": ["Zucman Milliardärssteuer", "EU Vermögensteuer", "G20 Reichensteuer"]
    },
    {
        "kategorie": "Hintergrund",
        "thema": "Geschichte der deutschen Vermögensteuer",
        "winkel": "Von der Kaiserzeit bis 1997: Wie die Vermögensteuer schrittweise ausgehöhlt und schließlich abgeschafft wurde",
        "keywords": ["Vermögensteuer Geschichte", "BVerfG 1995 Urteil", "Steuerpolitik Nachkrieg"]
    },
    {
        "kategorie": "Wirtschaft",
        "thema": "Vermögenszuwachs in Krisenzeiten",
        "winkel": "Während der Pandemie verloren Arbeitnehmer Jobs – das Vermögen der Reichsten wuchs um Hunderte Milliarden",
        "keywords": ["Corona Vermögen", "Pandemie Ungleichheit Deutschland", "DIW Krisengewinner"]
    },
    {
        "kategorie": "Gesellschaft",
        "thema": "Pflege und Vermögenssteuer",
        "winkel": "Pflegekräfte gehören zu den meistbesteuerten Berufsgruppen. Wer ihr System am Laufen hält – und wer davon profitiert",
        "keywords": ["Pflegesteuer", "Sozialbeiträge Pflege", "Pflegenotstand Finanzierung"]
    },
]

SYSTEM_PROMPT = """Du bist Redakteur bei SteuerWende, einer deutschen Nachrichtenplattform, 
die sich dem Thema Steuerungerechtigkeit widmet. Dein Kernthema: 
In Deutschland wird Arbeit viel zu hoch und Vermögen viel zu niedrig besteuert. 
Das Ziel der Plattform ist es, dieses Thema für ein breites Publikum zugänglich zu machen – 
Menschen, die sich normalerweise nicht mit Steuerpolitik beschäftigen.

Dein Stil:
- Seriös wie Süddeutsche Zeitung oder DIE ZEIT
- Klar und direkt, ohne akademisches Rumdrucksen
- Mit echten, belegbaren Zahlen und Quellen (OECD, DIW, Bundesbank, Destatis, Piketty, Zucman)
- Lebendige Beispiele aus dem Alltag (Krankenschwester, Handwerker, Pendler)
- Nie reißerisch oder boulevardesk – aber mit Haltung

Format-Anforderungen:
- Schreibe IMMER im JSON-Format (siehe unten)
- Mindestens 3 belegte Quellen pro Artikel
- Zwischen 600 und 900 Wörter
- Ein konkretes Daten-Highlight (Zahl, Statistik) als Aufmacher

Gib den Artikel als gültiges JSON zurück, sonst nichts:
{
  "titel": "...",
  "untertitel": "...",
  "kategorie": "...",
  "lesezeit": 7,
  "inhalt": "HTML-Inhalt des Artikels mit <p>, <h2>, <blockquote> Tags",
  "daten_highlight": {
    "zahl": "47,8%",
    "beschreibung": "Kurze Erklärung",
    "quelle": "OECD 2024"
  },
  "quellen": [
    {"autor": "...", "titel": "...", "jahr": 2024, "url": "https://..."}
  ],
  "seo_beschreibung": "Max. 160 Zeichen für Meta-Description",
  "tags": ["Vermögensteuer", "OECD", "Ungleichheit"]
}"""


def get_unused_thema(drafts_dir: Path, published_dir: Path) -> dict:
    """Wählt ein Thema, das in letzter Zeit nicht verwendet wurde."""
    used = set()
    for f in list(drafts_dir.glob("*.json")) + list(published_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            used.add(data.get("kategorie", ""))
        except Exception:
            pass

    # Bevorzuge Kategorien, die noch nicht vorkamen
    unused = [t for t in THEMEN if t["kategorie"] not in used]
    pool = unused if unused else THEMEN
    return random.choice(pool)


def generate_article(thema: dict) -> dict:
    """Generiert einen Artikel über die Claude API."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""Schreibe einen Artikel für SteuerWende zum folgenden Thema:

Kategorie: {thema['kategorie']}
Thema: {thema['thema']}
Winkel / These: {thema['winkel']}

Wichtige Quellen, die du einbeziehen solltest (recherchiere die aktuellen Zahlen):
{', '.join(thema['keywords'])}

Denke daran: Der Artikel soll Menschen ansprechen, die normalerweise keine 
Wirtschaftszeitungen lesen. Starte mit einem konkreten Alltagsbeispiel oder 
einer überraschenden Zahl. Das Thema Vermögens- vs. Einkommensteuer soll 
organisch eingebaut sein, nicht als Parole, sondern als logische Schlussfolgerung."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
        system=SYSTEM_PROMPT,
    )

    raw = message.content[0].text.strip()
    print(f"API Antwort (erste 200 Zeichen): {raw[:200]}")

    # Markdown-Codeblöcke entfernen (```json ... ```)
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            if part.startswith("json"):
                raw = part[4:].strip()
                break
            elif part.strip().startswith("{"):
                raw = part.strip()
                break

    # JSON extrahieren
    start = raw.find("{")
    end = raw.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError(f"Kein JSON gefunden. Antwort: {raw[:500]}")

    article_json = raw[start:end]
    return json.loads(article_json)


def save_draft(article: dict, thema: dict, drafts_dir: Path) -> Path:
    """Speichert den Artikel als Entwurf."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    slug = (
        article["titel"]
        .lower()
        .replace(" ", "-")
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    # Nur alphanumerische Zeichen und Bindestriche
    slug = "".join(c if c.isalnum() or c == "-" else "" for c in slug)[:60]

    filename = f"{timestamp}_{slug}.json"
    filepath = drafts_dir / filename

    # Metadaten hinzufügen
    article["_meta"] = {
        "erstellt": datetime.now().isoformat(),
        "status": "entwurf",
        "thema_id": thema["thema"],
        "slug": slug,
        "filename": filename,
    }

    filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2))
    print(f"✅ Entwurf gespeichert: {filepath}")
    return filepath


def main():
    root = Path(__file__).parent.parent
    drafts_dir = root / "articles" / "drafts"
    published_dir = root / "articles" / "published"

    drafts_dir.mkdir(parents=True, exist_ok=True)
    published_dir.mkdir(parents=True, exist_ok=True)

    # Thema wählen
    thema = get_unused_thema(drafts_dir, published_dir)
    print(f"📝 Generiere Artikel: {thema['thema']}")

    # Artikel generieren
    try:
        article = generate_article(thema)
        filepath = save_draft(article, thema, drafts_dir)
        print(f"🎉 Fertig: {article['titel']}")

        # Output für GitHub Actions
        print(f"::set-output name=article_title::{article['titel']}")
        print(f"::set-output name=article_file::{filepath.name}")

    except Exception as e:
        print(f"❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
