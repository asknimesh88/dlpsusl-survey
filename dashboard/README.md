# Static survey dashboard

One self-contained page showing the Graduate Satisfaction Survey results for both
specialisations, as two tabs:

| Tab | Responses |
|---|---|
| Animal Bio-Resource Technology and Management | 37 |
| Aquatic Bio-Resource Technology and Management | 9 |

Switching tab reloads every chart, filter and comment for that module. The aquatic tab
carries a note about its small sample.

No build step, no framework, no JavaScript dependencies — one HTML file. This sits
alongside the Next.js app in the repository root; neither one affects the other.

## Files

| File | What it is |
|---|---|
| `index.html` | The dashboard. Open it in a browser, or host it anywhere static. |
| `worker.js` | The same page wrapped in a Cloudflare Worker. Paste into the Worker editor and deploy. |
| `data.json` | The cleaned, aggregated data for both modules. |
| `build/` | The scripts that turn the survey CSVs into `data.json`, `index.html` and `worker.js`. |

## Rebuilding from new CSV exports

The survey CSVs are not in this repository: they hold graduates' written comments and
employer names. Put them somewhere outside the repo as `animal.csv` and `aquatic.csv`,
then:

```bash
cd dashboard/build
CSV_DIR=/path/to/csvs python3 analysis.py      # -> data.json
python3 -c "import json;t=open('tpl.html').read();\
d=json.dumps(json.load(open('data.json')),ensure_ascii=False).replace('</','<\\/');\
open('index.html','w').write(t.replace('__DATA__',d))"
node mkworker.js                               # index.html -> worker.js
```

Then copy `data.json`, `index.html` and `worker.js` up into `dashboard/`.

`analysis.py` finds each question by name rather than by column number, so the two
exports work despite having different course blocks (36 courses for animal, 34 for
aquatic) and different column counts.

## How the free text is handled

`clean.py` fixes spelling, capitalisation and punctuation, and drops placeholder answers
(`-`, `.`, `No`, `Xxx`). `overrides.py` holds the hand-edited wording for each longer
comment. Themes are assigned by keyword in `analysis.py`, so theme counts are
approximate; short "nothing to change" answers to an improvement question are shown as
comments but left out of the theme counts.

## Adding a third module

Append an entry to `MODULES` in `analysis.py` with its `id`, `label`, `full` name, `csv`
filename and a `note` for the course table. The page builds its tab row from whatever is
in `data.json`.
