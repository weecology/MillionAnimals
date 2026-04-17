# Airborne Source Registry

This folder stores the first-pass curation outputs for the "Airborne data" worksheet from the MillionAnimals collection spreadsheet.

## Files

- `airborne_sources_registry.csv`: normalized table of all worksheet rows with inferred access category and extracted candidate download URLs.
- `open_download_candidates.md`: subset of sources with links that look open/repository-backed.
- `contact_author_email_drafts.md`: short outreach drafts for request-only/contact-required sources.
- `generate_airborne_registry.py`: script to regenerate all of the above from an exported worksheet CSV.
- `ready_to_download_links.md`: curated list of direct file download URLs discovered via API checks.
- `ready_to_download_links.csv`: machine-readable version of the direct-download list.

## Access category rules (heuristic)

- `open_download_candidate`: one or more URLs matched known open data/repo domains.
- `contact_author`: source appears request-only and includes contact information.
- `manual_review`: everything else requiring human triage.

## Current counts

- Total worksheet rows processed: 366
- Open download candidates: 6
- Contact-author drafts generated: 58

No datasets were downloaded during this pass.

## Regeneration

```bash
python data_prep/source_registry/generate_airborne_registry.py /path/to/airborne.csv
```
