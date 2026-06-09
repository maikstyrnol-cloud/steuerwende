#!/usr/bin/env python3
"""Korrigiert ae/oe/ue/ss Ersetzungen in allen veröffentlichten Artikeln."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PUBLISHED = ROOT / "articles" / "published"

# Vollständige Liste bekannter falscher Schreibweisen
FIXES = {
    # ae → ä
    "aelter": "älter", "aeltere": "ältere", "aeltesten": "ältesten",
    "aermste": "ärmste", "aermsten": "ärmsten", "aermere": "ärmere",
    "ahnlich": "ähnlich", "Ahnlich": "Ähnlich",
    "Aeltere": "Ältere", "Aeltesten": "Ältesten",
    "jaehrlich": "jährlich", "Jaehrlich": "Jährlich",
    "jaehrige": "jährige", "jaehrigen": "jährigen",
    "Beitraege": "Beiträge", "beitraege": "beiträge",
    "Ertraege": "Erträge", "ertraege": "erträge",
    "Vertraege": "Verträge", "vertraege": "verträge",
    "Betraege": "Beträge", "betraege": "beträge",
    "Eintraege": "Einträge", "eintraege": "einträge",
    "Laender": "Länder", "laender": "länder",
    "Stadte": "Städte", "stadte": "städte",
    "Staedten": "Städten", "staedten": "städten",
    "staerker": "stärker", "Staerker": "Stärker",
    "staerkste": "stärkste", "Staerkste": "Stärkste",
    "staendig": "ständig", "Staendig": "Ständig",
    "staendige": "ständige", "Staendige": "Ständige",
    "waehrend": "während", "Waehrend": "Während",
    "Waehrung": "Währung", "waehrung": "währung",
    "saemtlich": "sämtlich", "Saemtlich": "Sämtlich",
    "saemtliche": "sämtliche", "Saemtliche": "Sämtliche",
    "tatsaechlich": "tatsächlich", "Tatsaechlich": "Tatsächlich",
    "tatsaechliche": "tatsächliche",
    "naemlich": "nämlich", "Naemlich": "Nämlich",
    "regelmaessig": "regelmäßig", "Regelmaessig": "Regelmäßig",
    "gleichmaessig": "gleichmäßig", "Gleichmaessig": "Gleichmäßig",
    "unregelmaessig": "unregelmäßig",
    "Kaeufer": "Käufer", "kaeufer": "käufer",
    "Verkaeufer": "Verkäufer", "verkaeufer": "verkäufer",

    # oe → ö
    "hoeher": "höher", "Hoeher": "Höher",
    "hoechst": "höchst", "Hoechst": "Höchst",
    "hoehere": "höhere", "Hoehere": "Höhere",
    "hoeheren": "höheren",
    "Hoehe": "Höhe", "hoehe": "höhe",
    "moeglich": "möglich", "Moeglich": "Möglich",
    "moegliche": "mögliche", "Moegliche": "Mögliche",
    "moeglichen": "möglichen",
    "moeglichst": "möglichst",
    "oeffentlich": "öffentlich", "Oeffentlich": "Öffentlich",
    "oeffentliche": "öffentliche", "Oeffentliche": "Öffentliche",
    "oeffentlichen": "öffentlichen",
    "oeffentlicher": "öffentlicher",
    "goennern": "gönnern", "Goennern": "Gönnern",
    "groesser": "größer", "Groesser": "Größer",
    "groesste": "größte", "Groesste": "Größte",
    "Boerse": "Börse", "boerse": "börse",
    "Boersen": "Börsen",
    "Loehne": "Löhne", "loehne": "löhne",
    "Vermoegen": "Vermögen", "vermoegen": "vermögen",
    "Vermoegens": "Vermögens",
    "Einkommens": "Einkommens",  # korrekt lassen

    # ue → ü
    "fuer": "für", "Fuer": "Für",
    "ueber": "über", "Ueber": "Über",
    "ueberall": "überall", "Ueberall": "Überall",
    "ueberproportional": "überproportional",
    "Ueberproportional": "Überproportional",
    "ueberwiegend": "überwiegend", "Ueberwiegend": "Überwiegend",
    "ueberwiegen": "überwiegen",
    "zurueck": "zurück", "Zurueck": "Zurück",
    "zurueckgehen": "zurückgehen",
    "zurueckzufuehren": "zurückzuführen",
    "Buerger": "Bürger", "buerger": "bürger",
    "Buergerinnen": "Bürgerinnen",
    "buergerlich": "bürgerlich",
    "Verfuegbar": "Verfügbar", "verfuegbar": "verfügbar",
    "verfuegbare": "verfügbare",
    "natuerlich": "natürlich", "Natuerlich": "Natürlich",
    "natuerliche": "natürliche",
    "tatsaechlich": "tatsächlich",
    "gruende": "gründe", "Gruende": "Gründe",
    "Gruenden": "Gründen",
    "begruendet": "begründet", "Begruendet": "Begründet",
    "fuehren": "führen", "Fuehren": "Führen",
    "fuehrt": "führt", "fuehrte": "führte",
    "Fuehrung": "Führung",
    "Huerden": "Hürden", "huerden": "hürden",
    "Spuerbar": "Spürbar", "spuerbar": "spürbar",
    "Beduerfnis": "Bedürfnis",
    "genuegen": "genügen", "Genuegen": "Genügen",
    "genuegend": "genügend",
    "muessen": "müssen", "Muessen": "Müssen",
    "muessten": "müssten", "Muessten": "Müssten",
    "duerfen": "dürfen", "Duerfen": "Dürfen",
    "duerfte": "dürfte", "duerften": "dürften",
    "frueherer": "früherer", "frueher": "früher", "Frueher": "Früher",
    "fruehestens": "frühestens",
    "Spaeter": "Später", "spaeter": "später",
    "spaetestens": "spätestens",
    "Zustaende": "Zustände", "zustaende": "zustände",
    "Uebergang": "Übergang",
    "Auszuege": "Auszüge",
    "Zuege": "Züge",
    "Begruendung": "Begründung",

    # Mobilität/Verkehr spezifisch
    "taeglich": "täglich", "Taeglich": "Täglich",
    "taeglichen": "täglichen",
    "Mobilitaet": "Mobilität", "mobilitaet": "mobilität",
    "Verkehrstraeger": "Verkehrsträger",
    "Nahverkehr": "Nahverkehr",  # korrekt
    "laendlichen": "ländlichen", "laendlich": "ländlich",
    "Laendlichen": "Ländlichen",
    "haeufig": "häufig", "Haeufig": "Häufig",
    "haeufiger": "häufiger", "haeufigste": "häufigste",
    "faehrt": "fährt", "fahrt": "fahrt",  # korrekt lassen
    "europaeische": "europäische", "Europaeische": "Europäische",
    "europaeischen": "europäischen",
    "innereuropaeische": "innereuropäische",

    # Steuer-spezifisch
    "Steuersaetze": "Steuersätze", "steuersaetze": "steuersätze",
    "Steuersatz": "Steuersatz",  # korrekt
    "Sozialabgaben": "Sozialabgaben",  # korrekt
    "Abgaben": "Abgaben",  # korrekt
    "Ernaehrung": "Ernährung",
    "unzureichend": "unzureichend",  # korrekt
    "ausgebaut": "ausgebaut",  # korrekt
    "angewiesen": "angewiesen",  # korrekt
}

def fix_text(text):
    if not isinstance(text, str):
        return text
    for wrong, correct in FIXES.items():
        # Nur als ganzes Wort ersetzen (Wortgrenzen beachten)
        text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text)
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
    fixed_total = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        article = json.loads(original)
        fixed = fix_value(article)
        new_text = json.dumps(fixed, ensure_ascii=False, indent=2)
        if new_text != original:
            f.write_text(new_text, encoding="utf-8")
            fixed_total += 1
            print(f"  ✅ {fixed.get('titel','')[:50]}")
        else:
            print(f"  ⏭️  {article.get('titel','')[:50]} – keine Änderungen")
    print(f"\n✅ {fixed_total} Artikel korrigiert")

if __name__ == "__main__":
    main()
