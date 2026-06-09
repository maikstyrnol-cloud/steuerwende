#!/usr/bin/env python3
"""Korrigiert ae/oe/ue/ss in allen veröffentlichten Artikeln zurück zu Umlauten."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PUBLISHED = ROOT / "articles" / "published"

# Wörter die NICHT ersetzt werden sollen (echte ae/oe/ue Kombinationen)
AUSNAHMEN = ["Israel", "Aero", "Koerper", "Museum", "Manuel", "Michael",
             "Ael", "Joel", "Noel", "Diesel", "Kassel", "Basel", "Israel"]

def fix_text(text):
    if not isinstance(text, str):
        return text
    # Vorsichtige Ersetzungen – nur eindeutige deutsche Umlaute
    replacements = [
        ("ae", "ä"), ("oe", "ö"), ("ue", "ü"),
        ("Ae", "Ä"), ("Oe", "Ö"), ("Ue", "Ü"),
        ("ss", "ß"),  # nur wo sinnvoll
    ]
    # Wende nur bekannte falsche Wörter an statt blinde Ersetzung
    known_fixes = {
        "staerker": "stärker", "waehrend": "während", "ueberproportional": "überproportional",
        "Haeuser": "Häuser", "fuer": "für", "Fuer": "Für",
        "ueber": "über", "Ueber": "Über", "ueberall": "überall",
        "Beitraege": "Beiträge", "Ertraege": "Erträge", "Vertraege": "Verträge",
        "Vermoegen": "Vermögen", "vermoegen": "vermögen",
        "Betraege": "Beträge", "Eintraege": "Einträge",
        "Hoehe": "Höhe", "hoeher": "höher", "Hoeher": "Höher",
        "groesser": "größer", "Groesser": "Größer", "groesste": "größte",
        "moeglich": "möglich", "Moeglich": "Möglich",
        "oeffentlich": "öffentlich", "Oeffentlich": "Öffentlich",
        "Steuersaetze": "Steuersätze", "Saetze": "Sätze",
        "Laender": "Länder", "laender": "länder",
        "Ernaehrung": "Ernährung", "jaehrlich": "jährlich",
        "regelmaessig": "regelmäßig", "Regelmaessig": "Regelmäßig",
        "Gleichmaessig": "Gleichmäßig", "gleichmaessig": "gleichmäßig",
        "Strassenbau": "Straßenbau", "Strasse": "Straße", "strasse": "straße",
        "Fuenftel": "Fünftel", "fuenftel": "fünftel",
        "Verfuegbar": "Verfügbar", "verfuegbar": "verfügbar",
        "aermsten": "ärmsten", "aermere": "ärmere",
        "Haushalte": "Haushalte",  # korrekt lassen
        "Einkuenfte": "Einkünfte", "Kuenftige": "Künftige",
        "natuerlich": "natürlich", "Natuerlich": "Natürlich",
        "tatsaechlich": "tatsächlich", "Tatsaechlich": "Tatsächlich",
        "saemtlich": "sämtlich", "Saemtlich": "Sämtlich",
        "zurueck": "zurück", "Zurueck": "Zurück",
        "Beduerfnis": "Bedürfnis", "beduerfnis": "bedürfnis",
        "Gruende": "Gründe", "gruende": "gründe",
        "staendige": "ständige", "Staendige": "Ständige",
        "Waehrung": "Währung", "waehrung": "währung",
        "gebuehren": "Gebühren", "Gebuehren": "Gebühren",
        "Buerger": "Bürger", "buerger": "bürger",
        "Huerden": "Hürden", "huerden": "hürden",
        "Spuerbar": "Spürbar", "spuerbar": "spürbar",
        "Zustaende": "Zustände", "zustaende": "zustände",
        "Uebergang": "Übergang", "uebergang": "übergang",
        "Spaeter": "Später", "spaeter": "später",
        "frueher": "früher", "Frueher": "Früher",
    }
    for wrong, correct in known_fixes.items():
        text = text.replace(wrong, correct)
    return text

def fix_value(v):
    if isinstance(v, str):
        return fix_text(v)
    elif isinstance(v, dict):
        return {k: fix_value(val) for k, val in v.items()}
    elif isinstance(v, list):
        return [fix_value(i) for i in v]
    return v

def main():
    files = list(PUBLISHED.glob("*.json"))
    print(f"📚 {len(files)} Artikel gefunden")
    for f in files:
        article = json.loads(f.read_text(encoding="utf-8"))
        fixed = fix_value(article)
        f.write_text(json.dumps(fixed, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✅ {fixed.get('titel','')[:50]}")
    print("✅ Fertig")

if __name__ == "__main__":
    main()
