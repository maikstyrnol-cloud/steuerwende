#!/usr/bin/env python3
"""
SteuerWende – Infografiken nachträglich hinzufügen
Liest alle veröffentlichten Artikel ohne Infografik,
generiert eine passende SVG-Grafik via Claude API,
und speichert sie in der JSON-Datei.
"""

import anthropic
import json
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PUBLISHED = ROOT / "articles" / "published"

INFOGRAFIK_PROMPT = """Du bist Datenjournalist bei SteuerWende. Basierend auf diesem Artikel, generiere eine passende Infografik mit echten belegbaren Zahlen.

Antworte NUR mit rohem JSON, kein Markdown:
{
  "typ": "balken",
  "titel": "Kurzer Grafiktitel (max 40 Zeichen)",
  "quelle": "OECD 2024",
  "daten": [
    {"label": "Deutschland", "wert": 47.8, "farbe": "rot"},
    {"label": "Schweden", "wert": 43.0, "farbe": "blau"}
  ]
}

WICHTIG:
- Maximal 4 Datenpunkte - weniger ist mehr
- Labels maximal 15 Zeichen, so einfach wie möglich
- Für Einkommensgruppen NUR: "Arm", "Mittel", "Reich" - niemals Fünftel oder Quintile
- Für Ländervergleiche: Ländernamen ausschreiben
- Werte als Prozentzahl (47.8 für 47.8%) - KEINE Euros oder Milliarden
- Farblogik: "rot" für höchsten/problematischsten Wert, "blau" für niedrigsten, "grau" für Mittelwerte
- Für "typ": "balken" (Vergleiche zwischen Kategorien) oder "donut" (Anteile die 100% ergeben)
- Wähle den Grafiktyp der die Kernaussage des Artikels am besten zeigt
- Nur echte, belegbare Zahlen

Artikel:
"""


def build_svg_balken(info):
    daten = info.get("daten", [])
    if not daten:
        return ""
    farben = {"rot": "#c8102e", "blau": "#2d6a9f", "grau": "#9ca3af", "gold": "#f0a500"}
    max_wert = max(d["wert"] for d in daten)
    if max_wert == 0:
        max_wert = 1
    bar_h = 30
    gap = 18
    label_w = 200
    bar_max_w = 210
    pad = 20
    total_w = pad + label_w + bar_max_w + 80 + pad
    total_h = len(daten) * (bar_h + gap) + 70
    bars = ""
    for i, d in enumerate(daten):
        y = 44 + i * (bar_h + gap)
        w = max(3, int((d["wert"] / max_wert) * bar_max_w))
        farbe = farben.get(d.get("farbe", "blau"), "#2d6a9f")
        einheit = " Mrd." if d["wert"] >= 1000 else "%"
        label = d["label"][:30]
        bars += f'<text x="{pad + label_w - 8}" y="{y + bar_h//2 + 5}" text-anchor="end" font-size="12" fill="#4b5563" font-family="sans-serif">{label}</text>'
        bars += f'<rect x="{pad + label_w}" y="{y}" width="{w}" height="{bar_h}" fill="{farbe}" rx="3"/>'
        bars += f'<text x="{pad + label_w + w + 8}" y="{y + bar_h//2 + 5}" font-size="13" font-weight="bold" fill="#1a2332" font-family="sans-serif">{d["wert"]}{einheit}</text>'
    titel = info.get("titel", "")[:65]
    quelle = info.get("quelle", "")[:80]
    return f'<svg viewBox="0 0 {total_w} {total_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;display:block;margin:0 auto;"><text x="{pad}" y="24" font-size="14" font-weight="bold" fill="#1a2332" font-family="sans-serif">{titel}</text>{bars}<text x="{pad}" y="{total_h - 8}" font-size="11" fill="#9ca3af" font-family="sans-serif">Quelle: {quelle}</text></svg>'
def build_svg_donut(info):
    daten = info.get("daten", [])
    if not daten:
        return ""
    farben_map = {"rot": "#c8102e", "blau": "#2d6a9f", "grau": "#9ca3af", "gold": "#f0a500"}
    farben_list = ["#c8102e", "#2d6a9f", "#f0a500", "#9ca3af"]
    total = sum(d["wert"] for d in daten)
    if total == 0:
        return ""
    cx, cy, r_out, r_in = 120, 130, 100, 58
    angle = -90
    paths = ""
    legend = ""
    for i, d in enumerate(daten):
        deg = (d["wert"] / total) * 360
        r1 = math.radians(angle)
        r2 = math.radians(angle + deg)
        x1o, y1o = cx + r_out * math.cos(r1), cy + r_out * math.sin(r1)
        x2o, y2o = cx + r_out * math.cos(r2), cy + r_out * math.sin(r2)
        x1i, y1i = cx + r_in * math.cos(r2), cy + r_in * math.sin(r2)
        x2i, y2i = cx + r_in * math.cos(r1), cy + r_in * math.sin(r1)
        large = 1 if deg > 180 else 0
        farbe = farben_map.get(d.get("farbe", ""), farben_list[i % len(farben_list)])
        paths += f'<path d="M {x1o:.1f} {y1o:.1f} A {r_out} {r_out} 0 {large} 1 {x2o:.1f} {y2o:.1f} L {x1i:.1f} {y1i:.1f} A {r_in} {r_in} 0 {large} 0 {x2i:.1f} {y2i:.1f} Z" fill="{farbe}"/>'
        ly = 50 + i * 24
        legend += f'<rect x="250" y="{ly}" width="14" height="14" fill="{farbe}" rx="2"/><text x="270" y="{ly+12}" font-size="13" fill="#4b5563" font-family="sans-serif">{d["label"]}: {d["wert"]}%</text>'
        angle += deg
    titel = info.get("titel", "")[:50]
    quelle = info.get("quelle", "")[:60]
    return f'<svg viewBox="0 0 480 270" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;display:block;margin:0 auto;"><text x="0" y="22" font-size="14" font-weight="bold" fill="#1a2332" font-family="sans-serif">{titel}</text>{paths}{legend}<text x="0" y="262" font-size="11" fill="#9ca3af" font-family="sans-serif">Quelle: {quelle}</text></svg>'


def build_svg(info):
    return build_svg_donut(info) if info.get("typ") == "donut" else build_svg_balken(info)


def generate_infografik(article):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    artikel_text = f"Titel: {article.get('titel','')}\n{article.get('inhalt','')[:800]}"
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": INFOGRAFIK_PROMPT + artikel_text}],
    )
    raw = re.sub(r'```(?:json)?', '', message.content[0].text.strip()).strip()
    start, end = raw.find("{"), raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"Kein JSON: {raw[:100]}")
    return json.loads(raw[start:end])


def main():
    if not PUBLISHED.exists():
        print("Kein published-Ordner gefunden.")
        sys.exit(1)

    files = list(PUBLISHED.glob("*.json"))
    print(f"📚 {len(files)} veröffentlichte Artikel gefunden")

    updated = 0
    for f in files:
        article = json.loads(f.read_text())
        # Immer neu generieren um fixes anzuwenden
        # if article.get("infografik_svg"):
        #     continue

        print(f"  🎨 Generiere Infografik für: {article.get('titel','')[:50]}")
        try:
            # Alte Infografik-Daten löschen damit alles neu generiert wird
            article.pop("infografik", None)
            article.pop("infografik_svg", None)
            info = generate_infografik(article)
            article["infografik"] = info
            article["infografik_svg"] = build_svg(info)
            f.write_text(json.dumps(article, ensure_ascii=False, indent=2))
            updated += 1
            print(f"     ✅ Fertig")
        except Exception as e:
            print(f"     ❌ Fehler: {e}")

    print(f"\n✅ {updated} Artikel mit Infografiken aktualisiert")


if __name__ == "__main__":
    main()
