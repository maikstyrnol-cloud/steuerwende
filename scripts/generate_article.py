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
    # ── DEUTSCHLAND: KLASSISCHE STEUERTHEMEN ──
    {"kategorie": "Wirtschaft", "thema": "Erbschaftsteuer und Unternehmensübertragung", "winkel": "Warum Milliardenerben fast keine Steuern zahlen", "keywords": ["Erbschaftsteuer Deutschland", "Betriebsvermögen Steuerbefreiung"]},
    {"kategorie": "Gesellschaft", "thema": "Wohnungskrise und Immobilienvermögen", "winkel": "Während Mieten explodieren, wächst Immobilienvermögen steuerfrei", "keywords": ["Immobiliensteuer Deutschland", "Grundsteuer Reform"]},
    {"kategorie": "Klima", "thema": "CO2-Steuer und soziale Gerechtigkeit", "winkel": "Die CO2-Steuer trifft Pendler härter als Privatjet-Besitzer", "keywords": ["CO2 Steuer sozial", "Klimasteuer Verteilung"]},
    {"kategorie": "Politik", "thema": "Lobbyismus in der Steuerpolitik", "winkel": "Wie Vermögensverbände seit Jahrzehnten Steuerpolitik mitschreiben", "keywords": ["BDI Steuerpolitik Lobbying", "Steuerreform blockiert"]},
    {"kategorie": "Sport", "thema": "Profifußball und Steueroptimierung", "winkel": "Bundesliga-Klubs als Steuerkonstrukte", "keywords": ["Bundesliga Steuer", "Fußball GmbH Steuer"]},
    {"kategorie": "Hintergrund", "thema": "Das schwedische Modell", "winkel": "Was Deutschland von Skandinavien lernen kann", "keywords": ["Schweden Vermögenssteuer", "Nordeuropa Steuermodell"]},
    {"kategorie": "Wirtschaft", "thema": "Kapitalertragssteuer im Vergleich", "winkel": "25% auf Kapitalerträge, 45% auf Arbeit: Deutschland bevorzugt Kapital", "keywords": ["Abgeltungssteuer", "Kapitalertragsteuer Reform"]},
    {"kategorie": "Gesellschaft", "thema": "Altersarmut und Vermögenskonzentration", "winkel": "Wer ein Leben lang gearbeitet hat, ist im Alter arm. Wer geerbt hat, nicht.", "keywords": ["Altersarmut Deutschland", "Rentenarmut Vermögen"]},
    {"kategorie": "Politik", "thema": "EU-Vermögensteuer Initiativen", "winkel": "Globale Milliardärssteuer – wie realistisch ist das?", "keywords": ["Zucman Milliardärssteuer", "EU Vermögensteuer"]},
    {"kategorie": "Hintergrund", "thema": "Geschichte der deutschen Vermögensteuer", "winkel": "Von der Kaiserzeit bis 1997: Wie die Vermögensteuer abgeschafft wurde", "keywords": ["Vermögensteuer Geschichte", "BVerfG 1995 Urteil"]},
    {"kategorie": "Wirtschaft", "thema": "Vermögenszuwachs in Krisenzeiten", "winkel": "Während Krisen Jobs vernichten, wächst das Vermögen der Reichsten", "keywords": ["Corona Vermögen", "Pandemie Ungleichheit Deutschland"]},
    {"kategorie": "Gesellschaft", "thema": "Pflege und Steuergerechtigkeit", "winkel": "Pflegekräfte gehören zu den meistbesteuerten Berufsgruppen", "keywords": ["Pflegesteuer", "Sozialbeiträge Pflege"]},

    # ── GLOBALE GERECHTIGKEIT ──
    {"kategorie": "Hintergrund", "thema": "Steueroasen und globaler Süden", "winkel": "Konzerne verschieben Gewinne aus Entwicklungsländern – Oxfam schätzt 100 Mrd. Dollar jährlich allein aus Afrika", "keywords": ["Steueroasen Afrika", "Gewinnverschiebung Entwicklungsländer", "Oxfam Steuern"]},
    {"kategorie": "Politik", "thema": "IWF, Sparmaßnahmen und Steuerpolitik", "winkel": "Warum der IWF ärmeren Ländern Sparmaßnahmen aufzwingt während reiche Länder Vermögen schützen", "keywords": ["IWF Strukturanpassung", "Sparmaßnahmen globaler Süden", "Steuerpolitik Entwicklung"]},
    {"kategorie": "Wirtschaft", "thema": "Die Kakao-Bäuerin und der Konzern", "winkel": "Produzenten im globalen Süden zahlen effektiv mehr als die Konzerne die ihre Rohstoffe verarbeiten", "keywords": ["Lieferketten Steuern", "Kakao Ghana Steuern", "Konzernsteuern Entwicklung"]},
    {"kategorie": "Hintergrund", "thema": "Globale Mindeststeuer – was bisher geschah", "winkel": "Die globale Mindeststeuer von 15% klingt nach Durchbruch – ist aber voller Schlupflöcher", "keywords": ["OECD Mindeststeuer", "Pillar Two", "globale Unternehmenssteuer"]},
    {"kategorie": "Politik", "thema": "Steuerwettbewerb zwischen Staaten", "winkel": "Wenn Länder sich gegenseitig mit Niedrigsteuern unterbieten, verlieren alle außer den Großkonzernen", "keywords": ["Steuerwettbewerb Europa", "Race to the Bottom Steuern", "EU Steuerpolitik"]},
    {"kategorie": "Gesellschaft", "thema": "Panama Papers und Pandora Papers", "winkel": "Was die größten Datenlecks der Geschichte über legale Steuervermeidung verraten", "keywords": ["Panama Papers Deutschland", "Pandora Papers", "Offshore Vermögen"]},

    # ── NATUR UND RESSOURCEN ──
    {"kategorie": "Klima", "thema": "Ressourcensteuer statt Einkommensteuer", "winkel": "Warum wir Arbeit besteuern statt Naturverbrauch – und warum das ökologisch absurd ist", "keywords": ["Ressourcensteuer", "ökologische Steuerreform", "Naturverbrauch Steuern"]},
    {"kategorie": "Klima", "thema": "Land Value Tax – Bodenspekulation besteuern", "winkel": "Henry Georges Idee könnte Wohnungskrise und Steuergerechtigkeit auf einmal lösen", "keywords": ["Land Value Tax", "Bodensteuer", "Henry George"]},
    {"kategorie": "Klima", "thema": "Privatjets, Yachten und Steuerprivilegien", "winkel": "Die emissionsintensivsten Konsumformen der Superreichen werden steuerlich begünstigt", "keywords": ["Privatjet Steuer", "Yacht Steuer", "Luxusemissionen"]},
    {"kategorie": "Klima", "thema": "Agrarindustrie und Bodeneigentum", "winkel": "Wenige Großgrundbesitzer kontrollieren immer mehr Agrarfläche – steuerfrei wachsend", "keywords": ["Agrarfläche Eigentum", "Großgrundbesitz Steuer", "Bodenkonzentration Deutschland"]},
    {"kategorie": "Hintergrund", "thema": "Warum Boden anders ist als anderes Vermögen", "winkel": "Boden kann nicht produziert werden – wer ihn besitzt, profitiert von gesellschaftlichem Wachstum ohne eigene Leistung", "keywords": ["Bodenrente", "Grundeigentum Steuern", "Boden Wirtschaft"]},
    {"kategorie": "Klima", "thema": "Klimaschäden und wer zahlt", "winkel": "Die Länder die am meisten unter dem Klimawandel leiden haben am wenigsten zu ihm beigetragen – und tragen die Kosten trotzdem", "keywords": ["Klimaschäden Finanzierung", "Loss and Damage", "Klimagerechtigkeit Steuern"]},

    # ── VERSTECKTE UND SYSTEMISCHE THEMEN ──
    {"kategorie": "Hintergrund", "thema": "Zentralbankpolitik und Vermögensungleichheit", "winkel": "Wie Niedrigzinsen und Quantitative Easing systematisch Vermögende gegenüber Arbeitnehmern bevorzugen", "keywords": ["EZB Geldpolitik Ungleichheit", "Quantitative Easing Vermögen", "Niedrigzinsen Reiche"]},
    {"kategorie": "Wirtschaft", "thema": "Daten als unbesteuertes Vermögen", "winkel": "Facebook und Google akkumulieren Milliardenvermögen aus unseren Daten – ohne Substanzsteuer", "keywords": ["Digitalsteuer", "Daten Vermögen Steuer", "Tech Konzerne Steuern"]},
    {"kategorie": "Wirtschaft", "thema": "Patente als Vermögensakkumulation", "winkel": "Wie Patentrecht stille Renten für Vermögende erzeugt – auf Kosten von Innovation und Allgemeinheit", "keywords": ["Patentrecht Steuer", "geistiges Eigentum Rente", "Urheberrecht Vermögen"]},
    {"kategorie": "Gesellschaft", "thema": "Intergenerationelle Ungerechtigkeit", "winkel": "Heutige Vermögende profitieren von Infrastruktur die vergangene Generationen gebaut haben – ohne dafür zu zahlen", "keywords": ["Generationengerechtigkeit Steuern", "Infrastruktur Finanzierung", "Erbschaft Gesellschaft"]},
    {"kategorie": "Hintergrund", "thema": "Die Privatisierung öffentlicher Güter", "winkel": "Wenn Wasser, Energie und Gesundheit in private Hände übergehen, fließen Gewinne steuerbegünstigt ab", "keywords": ["Privatisierung Steuern", "öffentliche Güter", "PPP Steuer"]},
    {"kategorie": "Politik", "thema": "Wie Steuergesetze wirklich geschrieben werden", "winkel": "Lobbyisten sitzen buchstäblich mit am Tisch wenn Steuergesetze entstehen", "keywords": ["Lobbyismus Steuergesetz", "Transparency International", "BMF Lobbyisten"]},
    {"kategorie": "Wirtschaft", "thema": "Private Equity und die Steuerlücke", "winkel": "Wie Private-Equity-Fonds systematisch weniger Steuern zahlen als die Unternehmen die sie aufkaufen", "keywords": ["Private Equity Steuern", "Carried Interest", "Finanzinvestoren Steuern"]},

    # ── ALLTAG UND LEBENSREALITÄT ──
    {"kategorie": "Gesellschaft", "thema": "Mehrwertsteuer – eine versteckt regressive Steuer", "winkel": "Reiche und Arme zahlen denselben Satz auf Lebensmittel – aber für Arme ist der Anteil am Einkommen viel größer", "keywords": ["Mehrwertsteuer Lebensmittel", "regressive Steuer", "Grundnahrungsmittel Steuer"]},
    {"kategorie": "Gesellschaft", "thema": "Gesundheit und Vermögen", "winkel": "Wer arm ist, stirbt früher – und zahlt trotzdem denselben Kassenbeitrag wie Besserverdiener", "keywords": ["Krankenversicherung Ungleichheit", "Gesundheit Einkommen", "Krankenkasse sozial"]},
    {"kategorie": "Gesellschaft", "thema": "Das Dienstwagenprivileg", "winkel": "Deutschland subventioniert Firmenwagen mit Milliarden – ein Steuervorteil der fast ausschließlich Gutverdienern zugutekommt", "keywords": ["Dienstwagenprivileg Kosten", "Firmenwagen Steuer", "Kfz Subvention"]},
    {"kategorie": "Gesellschaft", "thema": "Mieten, Eigenheim und die große Spaltung", "winkel": "Wer Eigentum besitzt profitiert von steuerfreiem Wertzuwachs – wer mietet, baut Vermögen für andere auf", "keywords": ["Eigenheim Steuer", "Mietverhältnis Vermögen", "Wohneigentum Förderung"]},
    {"kategorie": "Gesellschaft", "thema": "Bildung, Chancen und Vermögen", "winkel": "Wer reich geboren wird, bleibt reich – nicht wegen Leistung, sondern weil Vermögen Bildungschancen kauft", "keywords": ["Bildungsungleichheit Vermögen", "soziale Mobilität Deutschland", "Chancengerechtigkeit"]},
    {"kategorie": "Gesellschaft", "thema": "Frauen, Vermögen und der Gender Wealth Gap", "winkel": "Das Gender Pay Gap ist bekannt – der Gender Wealth Gap ist noch größer und noch weniger diskutiert", "keywords": ["Gender Wealth Gap", "Frauen Vermögen", "Geschlechterungleichheit Steuern"]},
    {"kategorie": "Gesellschaft", "thema": "Wohnungslosigkeit und Bodenspekulation", "winkel": "Menschen leben auf der Straße während Immobilien leer stehen – das Steuersystem macht das möglich", "keywords": ["Wohnungslosigkeit Steuern", "Leerstand Steuer", "Spekulation Wohnungen"]},

    # ── INTERNATIONALE VERGLEICHE ──
    {"kategorie": "Hintergrund", "thema": "Norwegen: Öl, Staatsfonds und Vermögenssteuer", "winkel": "Norwegen besteuert Vermögen, betreibt den größten Staatsfonds der Welt – und hat eine der stärksten Wirtschaften Europas", "keywords": ["Norwegen Vermögenssteuer", "Staatsfonds Norwegen", "Öl Steuer Norwegen"]},
    {"kategorie": "Hintergrund", "thema": "USA: Wie Milliardäre Einkommensteuer legal auf null bringen", "winkel": "ProPublica hat geleakt: Die reichsten Amerikaner zahlen effektive Steuersätze unter einem Prozent – legal", "keywords": ["ProPublica Milliardäre Steuern", "USA Steuervermeidung", "Buffett Steuer"]},
    {"kategorie": "Politik", "thema": "Frankreich und die abgeschaffte Vermögensteuer", "winkel": "Frankreich schaffte die Vermögensteuer ab – dann stiegen Ungleichheit und Staatsverschuldung", "keywords": ["Frankreich ISF Vermögensteuer", "Macron Vermögensteuer", "Frankreich Steuerpolitik"]},
    {"kategorie": "Hintergrund", "thema": "Wie Steueroasen wirklich funktionieren", "winkel": "Was Singapur, Dubai und Monaco wirklich sind, wer sie nutzt, und was sie die Welt kosten", "keywords": ["Steueroasen Funktionsweise", "Monaco Steuern", "Dubai Steuern"]},

    # ── ZUKUNFT UND NEUE THEMEN ──
    {"kategorie": "Wirtschaft", "thema": "Automatisierung, KI und die Steuerfrage", "winkel": "Wenn Roboter und KI menschliche Arbeit ersetzen – wer zahlt dann die Sozialsysteme?", "keywords": ["Robotersteuer", "KI Automatisierung Steuern", "Maschinensteuer"]},
    {"kategorie": "Wirtschaft", "thema": "Kryptowährungen und Steuervermeidung", "winkel": "Wie Krypto-Vermögen steuerlich kaum erfasst wird – und was sich ändern müsste", "keywords": ["Krypto Steuer Deutschland", "Bitcoin Steuern", "DeFi Steuer"]},
    {"kategorie": "Hintergrund", "thema": "Grundeinkommen finanziert durch Vermögensteuer", "winkel": "Ein bedingungsloses Grundeinkommen finanziert durch Vermögensteuern – was die Forschung dazu sagt", "keywords": ["Grundeinkommen Finanzierung", "BGE Vermögensteuer", "UBI Deutschland"]},
    {"kategorie": "Politik", "thema": "Wahlkampffinanzierung und Steuerpolitik", "winkel": "Wer Parteien finanziert, beeinflusst Steuerpolitik – eine Analyse der Verbindungen in Deutschland", "keywords": ["Parteispenden Steuern", "Wahlkampffinanzierung", "Demokratie Geld Steuern"]},
    {"kategorie": "Hintergrund", "thema": "Piketty: r > g und was es bedeutet", "winkel": "Die bekannteste Formel der Wirtschaftswissenschaften erklärt warum Ungleichheit zwangsläufig wächst", "keywords": ["Piketty r größer g", "Kapital 21 Jahrhundert", "Ungleichheit Wachstum"]},
    {"kategorie": "Gesellschaft", "thema": "Ehrenamt, Gemeinnützigkeit und Steuern", "winkel": "Wer sich ehrenamtlich engagiert trägt zur Gesellschaft bei – und wird dafür steuerlich kaum belohnt", "keywords": ["Ehrenamt Steuer", "Gemeinnützigkeit", "Zivilgesellschaft Steuern"]},
    {"kategorie": "Wirtschaft", "thema": "Superreiche und Staatsbürgerschaft zu verkaufen", "winkel": "Wie reiche Einzelpersonen durch Citizenship-by-Investment-Programme Steuern legal auf null optimieren", "keywords": ["Goldenes Visum Steuern", "Staatsbürgerschaft kaufen", "Steueroptimierung Auswanderung"]},
    {"kategorie": "Hintergrund", "thema": "Die Finanztransaktionssteuer – warum sie nie kommt", "winkel": "Eine Steuer von 0,1% auf Finanztransaktionen würde Milliarden einbringen – und wird seit 20 Jahren blockiert", "keywords": ["Finanztransaktionssteuer", "Tobin Tax", "Börsensteuer Deutschland"]},
]

SYSTEM_PROMPT = """Du bist Redakteur bei SteuerWende. Antworte NUR mit rohem JSON, ohne Markdown, ohne Codeblöcke, ohne Erklärungen.

WICHTIGSTE REGEL: Schreibe NIEMALS über einzelne namentlich genannte Personen. Nur über Systeme, Strukturen, Gesetze und Statistiken.

SPRACHE – ABSOLUT KRITISCH: Schreibe IMMER korrektes Deutsch mit Umlauten:
- ä: täglich, während, ärmste, häufig, stärker, Länder, jährlich, europäisch
- ö: höher, möglich, Vermögen, Börse, größer, Österreich
- ü: für, über, müssen, dürfen, Bürger, natürlich, früher, führen, zurück
- ß: stoßen, Straße, Maßnahme, groß, schließen, regelmäßig
Niemals ae/oe/ue/ss statt Umlaute verwenden.

QUELLEN – GLOBALE PERSPEKTIVE: Beziehe bewusst Stimmen und Daten aus verschiedenen Weltregionen ein. Pro Artikel mindestens eine nicht-westliche Quelle wenn das Thema es erlaubt.

Empfohlene Quellen:
INTERNATIONAL: Piketty, Zucman, Saez, Stiglitz (Nobelpreisträger), Acemoğlu (MIT), Mazzucato (UCL), Ha-Joon Chang (Cambridge), Kate Raworth, Jason Hickel, Tax Justice Network, Oxfam, UNCTAD, IWF Fiscal Monitor, OECD
SÜDAMERIKA: Alicia Bárcena / CEPAL/ECLAC, Magdalena Sepúlveda (UN-Sonderberichterstatterin), CEPAL-Steuerberichte
AFRIKA: Carlos Lopes (AU), Tax Justice Network Africa, Thabo Mbeki Panel (illegale Finanzflüsse), Mo Ibrahim Foundation
ASIEN: Jayati Ghosh (Indien), C.P. Chandrasekhar (Indien), Action Aid Asia
DEUTSCHLAND/EU: DIW Berlin, IMK, Bundesbank, Destatis, Eurostat, BMF

Das JSON muss exakt dieses Format haben – mit einem "infografik" Feld:
{
  "titel": "...",
  "untertitel": "...",
  "kategorie": "...",
  "lesezeit": 6,
  "inhalt": "<p>HTML Artikeltext hier. Maximal 500 Wörter.</p>",
  "daten_highlight": {"zahl": "47%", "beschreibung": "...", "quelle": "OECD 2024"},
  "infografik": {
    "typ": "balken",
    "titel": "Titel der Grafik",
    "beschreibung": "Was die Grafik zeigt",
    "quelle": "OECD 2024",
    "daten": [
      {"label": "Deutschland", "wert": 47.8, "farbe": "rot"},
      {"label": "Schweden", "wert": 43.0, "farbe": "blau"},
      {"label": "USA", "wert": 29.9, "farbe": "blau"}
    ]
  },
  "quellen": [{"autor": "...", "titel": "...", "jahr": 2024, "url": "https://..."}],
  "seo_beschreibung": "...",
  "tags": ["Tag1", "Tag2"]
}

Für "typ" wähle: "balken" (Vergleiche), "donut" (Anteile/Prozente), oder "zeitstrahl" (Entwicklung ueber Zeit).
Für "farbe" bei balken: "rot" fuer Deutschland/Hauptwert, "blau" fuer Vergleichswerte, "grau" fuer Nebenwerte.
- Labels klar und allgemeinverständlich formulieren: "Ärmste 20%" statt "Unterstes Fünftel", Ländernamen ausschreiben, keine Abkürzungen oder Fachtermini.
Maximal 6 Datenpunkte. Nur echte, belegbare Zahlen verwenden.

Stil: Seriös wie Süddeutsche Zeitung, echte Quellen (OECD, DIW, Bundesbank), max 500 Wörter Artikeltext."""


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
    prompt = f"""Schreibe einen Artikel fuer SteuerWende.

Kategorie: {thema['kategorie']}
Thema: {thema['thema']}
Winkel: {thema['winkel']}
Keywords: {', '.join(thema['keywords'])}

Generiere auch eine passende Infografik mit echten Zahlen zum Thema.
WICHTIG: Nur rohes JSON, kein Markdown, keine Erklärungen."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
        system=SYSTEM_PROMPT,
    )

    raw = message.content[0].text.strip()
    print(f"Roh-Antwort Anfang: {repr(raw[:80])}")
    raw = re.sub(r'```(?:json)?', '', raw).strip()

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"Kein JSON gefunden: {raw[:200]}")

    return json.loads(raw[start:end])


def build_svg_balken(info):
    """Generiert ein SVG-Balkendiagramm aus den Infografik-Daten."""
    daten = info.get("daten", [])
    if not daten:
        return ""
    farben = {"rot": "#c8102e", "blau": "#2d6a9f", "grau": "#9ca3af", "gold": "#f0a500"}
    max_wert = max(d["wert"] for d in daten)
    if max_wert == 0:
        max_wert = 1
    bar_h = 30
    gap = 16
    label_w = 185
    bar_max_w = 230
    pad = 20
    total_w = pad + label_w + bar_max_w + 80 + pad
    total_h = len(daten) * (bar_h + gap) + 70
    bars = ""
    for i, d in enumerate(daten):
        y = 44 + i * (bar_h + gap)
        w = max(3, int((d["wert"] / max_wert) * bar_max_w))
        farbe = farben.get(d.get("farbe", "blau"), "#2d6a9f")
        if d["wert"] >= 1000:
            einheit = " Mrd."
        else:
            einheit = "%"
        label = d["label"][:30]
        bars += f'<text x="{pad + label_w - 8}" y="{y + bar_h//2 + 5}" text-anchor="end" font-size="12" fill="#4b5563" font-family="sans-serif">{label}</text>'
        bars += f'<rect x="{pad + label_w}" y="{y}" width="{w}" height="{bar_h}" fill="{farbe}" rx="3"/>'
        bars += f'<text x="{pad + label_w + w + 8}" y="{y + bar_h//2 + 5}" font-size="13" font-weight="bold" fill="#1a2332" font-family="sans-serif">{d["wert"]}{einheit}</text>'
    titel = info.get("titel", "")[:65]
    quelle = info.get("quelle", "")[:80]
    return f'<svg viewBox="0 0 {total_w} {total_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;display:block;margin:0 auto;"><text x="{pad}" y="24" font-size="14" font-weight="bold" fill="#1a2332" font-family="sans-serif">{titel}</text>{bars}<text x="{pad}" y="{total_h - 8}" font-size="11" fill="#9ca3af" font-family="sans-serif">Quelle: {quelle}</text></svg>'
def build_svg_donut(info):
    """Generiert ein SVG-Donut-Diagramm."""
    daten = info.get("daten", [])
    if not daten:
        return ""

    farben_map = {"rot": "#c8102e", "blau": "#2d6a9f", "grau": "#9ca3af", "gold": "#f0a500"}
    farben_list = ["#c8102e", "#2d6a9f", "#f0a500", "#9ca3af", "#4ade80", "#818cf8"]

    total = sum(d["wert"] for d in daten)
    cx, cy, r_outer, r_inner = 120, 120, 100, 60
    angle = -90

    paths = ""
    legend = ""
    for i, d in enumerate(daten):
        pct = d["wert"] / total
        deg = pct * 360
        rad1 = angle * 3.14159 / 180
        rad2 = (angle + deg) * 3.14159 / 180
        x1o = cx + r_outer * (rad1.__class__.__name__ and __import__('math').cos(rad1))
        y1o = cy + r_outer * __import__('math').sin(rad1)
        x2o = cx + r_outer * __import__('math').cos(rad2)
        y2o = cy + r_outer * __import__('math').sin(rad2)
        x1i = cx + r_inner * __import__('math').cos(rad2)
        y1i = cy + r_inner * __import__('math').sin(rad2)
        x2i = cx + r_inner * __import__('math').cos(rad1)
        y2i = cy + r_inner * __import__('math').sin(rad1)
        large = 1 if deg > 180 else 0
        farbe = farben_map.get(d.get("farbe",""), farben_list[i % len(farben_list)])
        paths += f'<path d="M {x1o:.1f} {y1o:.1f} A {r_outer} {r_outer} 0 {large} 1 {x2o:.1f} {y2o:.1f} L {x1i:.1f} {y1i:.1f} A {r_inner} {r_inner} 0 {large} 0 {x2i:.1f} {y2i:.1f} Z" fill="{farbe}"/>'
        ly = 60 + i * 22
        legend += f'<rect x="250" y="{ly}" width="14" height="14" fill="{farbe}" rx="2"/><text x="270" y="{ly+12}" font-size="13" fill="#4b5563" font-family="sans-serif">{d["label"]}: {d["wert"]}%</text>'
        angle += deg

    titel = info.get("titel","")[:50]
    quelle = info.get("quelle","")[:60]

    return f"""<svg viewBox="0 0 480 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;display:block;margin:0 auto;">
  <text x="0" y="20" font-size="14" font-weight="bold" fill="#1a2332" font-family="sans-serif">{titel}</text>
  {paths}
  {legend}
  <text x="0" y="252" font-size="11" fill="#9ca3af" font-family="sans-serif">Quelle: {quelle}</text>
</svg>"""


def build_svg(info):
    """Wählt den richtigen SVG-Typ."""
    typ = info.get("typ", "balken")
    if typ == "donut":
        return build_svg_donut(info)
    return build_svg_balken(info)


def save_article(article, thema, drafts_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    slug = re.sub(r'[^a-z0-9-]', '', article["titel"].lower()
        .replace(" ", "-").replace("ä","ae").replace("ö","oe")
        .replace("ü","ue").replace("ß","ss"))[:60]
    filename = f"{timestamp}_{slug}.json"

    # SVG generieren und einbetten
    if "infografik" in article:
        article["infografik_svg"] = build_svg(article["infografik"])

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
