#!/usr/bin/env python3
"""Generate Summer 2027-only listing files from data/listings.json.

Writes one file per category into listings/summer-2027/, newest first.
Run after scrape.py.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "listings.json"
OUTDIR = ROOT / "listings" / "summer-2027"

TERM = "Summer 2027"

# category value in listings.json -> output filename
CATEGORIES = {
    "Product": "product-management.md",
    "Software": "software-engineering.md",
    "AI/ML/Data": "data-science-ai-machine-learning.md",
    "Quant": "quantitative-finance.md",
    "Hardware": "hardware-engineering.md",
}


def days_old(ts):
    if not ts:
        return ""
    posted = datetime.fromtimestamp(ts, tz=timezone.utc)
    return (datetime.now(timezone.utc) - posted).days


def date_str(ts):
    if not ts:
        return ""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def main():
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    OUTDIR.mkdir(parents=True, exist_ok=True)

    counts = []
    for category, filename in CATEGORIES.items():
        matches = [
            r for r in rows
            if r.get("category") == category
            and r.get("active")
            and TERM in (r.get("terms") or [])
        ]
        matches.sort(key=lambda r: r.get("date_posted") or 0, reverse=True)

        lines = [
            f"# {TERM} — {category} ({len(matches)})",
            "",
            "Auto-generated. Do not hand-edit.",
            "",
            "| Company | Role | Location | Date Posted | Days Old |",
            "|---|---|---|---|---|",
        ]
        for r in matches:
            company = r.get("company_name", "")
            url = r.get("url", "")
            title = (r.get("title") or "").replace("|", "/")
            locs = ", ".join(r.get("locations") or []) or "N/A"
            ts = r.get("date_posted")
            name = f"[{company}]({url})" if url else company
            lines.append(f"| {name} | {title} | {locs} | {date_str(ts)} | {days_old(ts)} |")

        (OUTDIR / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")
        counts.append(f"{category}: {len(matches)}")

    print(f"{TERM} written — " + ", ".join(counts))


if __name__ == "__main__":
    main()
