"""Generate MillionAnimals Airborne worksheet curation artifacts.

Usage:
    python data_prep/source_registry/generate_airborne_registry.py /path/to/airborne.csv
"""

import csv
import re
import sys
from pathlib import Path
from textwrap import dedent


URL_RE = re.compile(r'https?://[^\s,\)\]\"]+')
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
OPEN_DOMAINS = [
    "zenodo.org",
    "kaggle.com",
    "github.com",
    "huggingface.co",
    "datadryad.org",
    "figshare.com",
    "frdr-dfdr.ca",
    "lila.science",
]
REQUEST_MARKERS = [
    "by request",
    "upon request",
    "reasonable request",
    "contact the author",
    "available by request",
    "data available upon request",
    "not be made public",
    "not publicly available",
    "request access",
]


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:90] if text else "untitled_source"


def classify_access(urls: list[str], available: str, data: str, comments: str,
                    has_email: bool) -> str:
    lower = " ".join([data.lower(), available.lower(), comments.lower()])
    has_open = any(any(domain in u.lower() for domain in OPEN_DOMAINS) for u in urls)
    explicit_request = any(marker in lower for marker in REQUEST_MARKERS)

    if has_open:
        return "open_download_candidate"
    if explicit_request and has_email:
        return "contact_author"
    if available.lower().startswith("no") and has_email:
        return "contact_author"
    return "manual_review"


def main(input_csv: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    registry_dir = repo_root / "data_prep" / "source_registry"
    templates_dir = repo_root / "data_prep" / "sources_airborne"
    registry_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(input_csv.open(newline="", encoding="utf-8")))
    processed = []
    for idx, row in enumerate(rows, start=1):
        title = (row.get("Title") or "").strip()
        contact = (row.get("Contact") or "").strip()
        link = (row.get("Link") or "").strip()
        taxa = (row.get("Taxa") or "").strip()
        data = (row.get("Data") or "").strip()
        available = (row.get("Available?") or "").strip()
        comments = (row.get("Comments") or "").strip()

        combined = " ".join([link, data, available, comments])
        urls = [u.rstrip(".,;") for u in URL_RE.findall(combined)]
        urls = list(dict.fromkeys(urls))
        has_email = bool(EMAIL_RE.search(contact))

        processed.append({
            "row_id": idx,
            "source_slug": slugify(title),
            "title": title,
            "contact": contact,
            "link": link,
            "taxa": taxa,
            "data": data,
            "available": available,
            "comments": comments,
            "access_category": classify_access(urls, available, data, comments,
                                               has_email),
            "has_contact_email": str(has_email),
            "candidate_download_links": "; ".join(urls),
        })

    registry_csv = registry_dir / "airborne_sources_registry.csv"
    with registry_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "row_id",
            "source_slug",
            "title",
            "contact",
            "link",
            "taxa",
            "data",
            "available",
            "comments",
            "access_category",
            "has_contact_email",
            "candidate_download_links",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed)

    open_rows = [r for r in processed if r["access_category"] == "open_download_candidate"]
    contact_rows = [
        r for r in processed if r["access_category"] == "contact_author" and any(
            m in " ".join([r["available"], r["comments"], r["data"]]).lower()
            for m in REQUEST_MARKERS)
    ]

    open_md = registry_dir / "open_download_candidates.md"
    lines = [
        "# Open Download Candidates (Airborne worksheet)",
        "",
        "These sources include links that look like open repositories or downloadable archives.",
        "No data were downloaded; links were only cataloged for later implementation.",
        "",
    ]
    for r in open_rows:
        lines += [
            f"## {r['title']}",
            f"- Source slug: `{r['source_slug']}`",
            f"- Taxa: {r['taxa'] or 'Not specified'}",
            f"- Worksheet link: {r['link'] or 'Not provided'}",
            f"- Candidate download links: {r['candidate_download_links'] or 'None extracted'}",
            "",
        ]
    open_md.write_text("\n".join(lines), encoding="utf-8")

    for r in open_rows:
        script = dedent(f"""\
        \"\"\"Dataset prep scaffold for: {r['title']}.

        Auto-generated from the MillionAnimals airborne worksheet.
        NOTE: This file is a template only; no downloads are performed here.
        \"\"\"

        from pathlib import Path
        import pandas as pd


        SOURCE_TITLE = {r['title']!r}
        SOURCE_SLUG = {r['source_slug']!r}
        WORKSHEET_LINK = {r['link']!r}
        CANDIDATE_DOWNLOAD_LINKS = {r['candidate_download_links']!r}


        def build_annotations(raw_dir: str = "data/raw", output_dir: str = "data_prep/annotations") -> Path:
            \"\"\"Create an annotation CSV scaffold for this source.\"\"\"
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            df = pd.DataFrame(columns=["geometry", "image_path", "label", "source"])
            target = output_path / f"{{SOURCE_SLUG}}_annotations.csv"
            df.to_csv(target, index=False)
            return target


        if __name__ == "__main__":
            out = build_annotations()
            print(f"Wrote scaffold annotations to: {{out}}")
        """)
        (templates_dir / f"{r['source_slug']}.py").write_text(script, encoding="utf-8")

    contact_md = registry_dir / "contact_author_email_drafts.md"
    contact_lines = [
        "# Contact Email Drafts (Request-Only Sources)",
        "",
        "These are brief draft emails for sources that appear request-only or contact-author in the worksheet.",
        "Each draft includes project context, manuscript invitation language, and geospatial privacy statement.",
        "",
        "![MillionAnimals sample image](../../docs/public/open_drone_example.png)",
        "",
    ]
    for r in contact_rows:
        emails = ", ".join(EMAIL_RE.findall(r["contact"])) or r["contact"] or "email-not-listed"
        contact_lines += [
            f"## {r['title']}",
            f"- To: {emails}",
            f"- Worksheet link: {r['link'] or 'Not provided'}",
            "",
            "Subject: MillionAnimals dataset collaboration request",
            "",
            f"Hello, we are building MillionAnimals, an open benchmark for airborne animal detection, and we are currently reviewing `{r['title']}` for inclusion.",
            "If sharing is possible, we would be grateful for access to the imagery and annotations (or guidance on your preferred access path).",
            "All contributing dataset authors will be invited to co-author the manuscript, and all geospatial information is removed from released data products to protect re-use.",
            "A sample benchmark image is shown above for context.",
            "Thank you for considering this request.",
            "",
        ]
    contact_md.write_text("\n".join(contact_lines), encoding="utf-8")

    print(f"Processed rows: {len(processed)}")
    print(f"Open download candidates: {len(open_rows)}")
    print(f"Contact draft sections: {len(contact_rows)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python data_prep/source_registry/generate_airborne_registry.py /path/to/airborne.csv")
    main(Path(sys.argv[1]))
