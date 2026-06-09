#!/usr/bin/env python3
"""
SteuerWende – Entwurf genehmigen
Verschiebt den neuesten Entwurf von /drafts nach /published.
Wird automatisch beim Merge eines Pull Requests ausgeführt.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
DRAFTS = ROOT / "articles" / "drafts"
PUBLISHED = ROOT / "articles" / "published"


def approve_latest_draft():
    drafts = sorted(DRAFTS.glob("*.json"), reverse=True)

    if not drafts:
        print("ℹ️  Keine Entwürfe gefunden.")
        return

    draft_path = drafts[0]
    print(f"✅ Genehmige: {draft_path.name}")

    # Status aktualisieren
    article = json.loads(draft_path.read_text())
    article["_meta"]["status"] = "veröffentlicht"
    article["_meta"]["veröffentlicht_am"] = datetime.now().isoformat()

    # In published verschieben
    PUBLISHED.mkdir(parents=True, exist_ok=True)
    target = PUBLISHED / draft_path.name
    target.write_text(json.dumps(article, ensure_ascii=False, indent=2))
    draft_path.unlink()

    print(f"📰 Veröffentlicht: {article.get('titel', '')}")


if __name__ == "__main__":
    approve_latest_draft()
