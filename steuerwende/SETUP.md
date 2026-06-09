# SteuerWende – Setup-Anleitung

## Was du brauchst
- Ein GitHub-Konto (kostenlos)
- Einen Anthropic API-Key
- Ein Gmail-Konto für Benachrichtigungen (oder anderer SMTP-Anbieter)

---

## Schritt 1: GitHub Repository anlegen

1. Gehe zu [github.com](https://github.com) → **New repository**
2. Name: `steuerwende` (oder beliebig)
3. Sichtbarkeit: **Public** (für GitHub Pages kostenlos)
4. Klicke **Create repository**

---

## Schritt 2: Dateien hochladen

Lade alle Dateien aus diesem Paket in dein Repository:

```
steuerwende/
├── .github/
│   └── workflows/
│       ├── generate_article.yml   ← Artikel-Generator (3x täglich)
│       └── deploy_site.yml        ← Website-Deployment (nach Freigabe)
├── scripts/
│   ├── generate_article.py        ← Ruft Claude API auf
│   ├── build_site.py              ← Baut HTML-Seiten
│   └── approve_draft.py           ← Verschiebt Entwurf → Veröffentlicht
├── articles/
│   ├── drafts/                    ← Hier landen neue Entwürfe
│   └── published/                 ← Hier liegen veröffentlichte Artikel
├── static/
│   └── css/
│       └── main.css               ← Das Stylesheet
└── docs/                          ← Wird automatisch gebaut (GitHub Pages)
```

**Einfachste Methode:** Klicke im Repository auf **"uploading an existing file"** 
und ziehe den ganzen Ordner rein.

---

## Schritt 3: GitHub Pages aktivieren

1. Im Repository: **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** / Ordner: **/ (root)**
4. Klicke **Save**

Deine Website ist dann unter:
`https://DEIN-USERNAME.github.io/steuerwende/`

### Eigene Domain (optional, ~10€/Jahr)
- Domain bei Namecheap oder Hetzner kaufen
- Im Repository unter Settings → Pages → Custom domain eintragen
- Beim Domain-Anbieter einen CNAME-Eintrag setzen:
  `www` → `DEIN-USERNAME.github.io`

---

## Schritt 4: API-Keys als Secrets hinterlegen

Im Repository: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Wert | Woher |
|---|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | [console.anthropic.com](https://console.anthropic.com) |
| `MAIL_USERNAME` | `deine@gmail.com` | Dein Gmail-Konto |
| `MAIL_PASSWORD` | `xxxx xxxx xxxx xxxx` | Gmail App-Passwort (siehe unten) |
| `NOTIFY_EMAIL` | `deine@email.de` | Wohin die Benachrichtigung soll |

### Gmail App-Passwort erstellen:
1. Gmail → Google-Konto → Sicherheit
2. 2-Faktor-Authentifizierung aktivieren (falls noch nicht)
3. Sicherheit → App-Passwörter → "Mail" + "Anderes Gerät"
4. Das generierte 16-stellige Passwort als `MAIL_PASSWORD` eintragen

---

## Schritt 5: Ersten Test durchführen

1. Im Repository: **Actions** → **SteuerWende – Artikel generieren**
2. Klicke **Run workflow** → **Run workflow**
3. Nach ~2 Minuten erhältst du eine Email mit einem Link
4. Klicke im Link auf **"Merge pull request"**
5. Nach weiteren ~1-2 Minuten ist die Website aktualisiert

---

## Wie der tägliche Ablauf aussieht

```
07:00 Uhr  →  GitHub Actions startet automatisch
             →  Claude generiert einen Artikel
             →  Du bekommst eine Email mit Link

             Du klickst auf "Merge pull request"
             →  Artikel wird veröffentlicht
             →  Website wird automatisch aktualisiert

12:00 Uhr  →  Zweiter Artikel (gleicher Ablauf)
18:00 Uhr  →  Dritter Artikel (gleicher Ablauf)
```

**Wichtig:** Du musst nichts tun außer auf den Link zu klicken.
Wenn du einen Artikel nicht willst: einfach ignorieren oder "Close pull request".

---

## Kosten

| Was | Kosten/Monat |
|---|---|
| GitHub (Repo + Actions + Pages) | **0 €** |
| Claude API (~3 Artikel/Tag, ~800 Wörter) | **~30–50 €** |
| Domain (optional) | **~1 €** |
| **Gesamt** | **~30–50 €** |

> API-Kosten variieren je nach Modell. Mit `claude-haiku-4-5` statt `claude-opus-4-6`
> sinken die Kosten auf ~5–10€/Monat, mit leichtem Qualitätsunterschied.

---

## Häufige Fragen

**Q: Was passiert, wenn ich eine Email ignoriere?**  
A: Nichts. Der Entwurf bleibt als Branch im Repository und kann später noch gemergt werden.

**Q: Kann ich Artikel nachträglich bearbeiten?**  
A: Ja – direkt die JSON-Datei in `articles/published/` im GitHub-Editor bearbeiten,
dann `git commit` → Website wird automatisch neu gebaut.

**Q: Kann ich das Thema eines Artikels vorgeben?**  
A: Ja – über "Run workflow" mit dem Parameter `force_topic` kannst du ein Stichwort eingeben.
Oder einfach in `scripts/generate_article.py` die `THEMEN`-Liste anpassen.

**Q: Wie füge ich Bilder ein?**  
A: Bilder von Unsplash in `static/img/` ablegen, dann in der JSON-Datei des Artikels
ein Feld `"bild": "static/img/dateiname.jpg"` hinzufügen.

---

## Support

Bei Fragen: Öffne einfach eine neue Konversation mit Claude und zeige 
diese Anleitung – dann kann direkt weitergemacht werden.
