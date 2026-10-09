# Rebuilding the response data

`public/data/responses.json` (animal) and `public/data/responses-aquatic.json` (aquatic)
are generated from the Google Forms CSV exports. The CSVs are **not** in this repository:
they contain graduates' written answers and employer names.

```bash
cd scripts
CSV_DIR=/path/to/csvs python3 build_responses.py aquatic.csv > ../public/data/responses-aquatic.json
```

`build_responses.py` finds each question by name rather than column number, so it reads
both exports despite their different course blocks (36 courses for animal, 34 for
aquatic) and different column counts.

Pass `--raw` to skip the text tidy-up and keep answers exactly as typed. The committed
animal file was generated elsewhere and is raw; the aquatic file is tidied, so its
written answers have sentence case, spelling fixes and full stops. `clean.py` does the
mechanical fixes and `overrides.py` holds the hand-edited wording for longer comments.

## Adding a third module

Write its CSV out with this script, drop the JSON in `public/data/`, and append an entry
to `MODULES` in `app/page.js`. The tab row builds itself from that list.

## Known issue in the animal file

Placeholder answers (`-`, `.`) were read as "No" when it was generated, so the animal tab
shows one "No" under *Would they recommend it?* and three under *Course structure felt
flexible* that were really blank answers. Regenerating `responses.json` with this script
fixes that, but it also shifts a few other derived figures, so it has been left alone.
