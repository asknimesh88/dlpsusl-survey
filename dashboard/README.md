# Static survey dashboard

A single self-contained page showing the Graduate Satisfaction Survey results for the
Animal Bio-Resource Technology and Management specialisation (37 responses, July 2026).
No build step, no framework, no JavaScript dependencies — one HTML file.

This sits alongside the Next.js app in the repository root; neither one affects the other.

## Files

| File | What it is |
|---|---|
| `index.html` | The dashboard. Open it in a browser, or host it anywhere static. |
| `worker.js` | The same page wrapped in a Cloudflare Worker. Paste into the Worker editor and deploy. |
| `data.json` | The cleaned, aggregated survey data embedded in the page. |
| `build/` | The scripts that turn the survey CSV into `data.json`, `index.html` and `worker.js`. |

## Rebuilding from a new CSV export

The survey CSV is not in this repository: it holds graduates' written comments and
employer names. Put it next to the build scripts as `survey.csv`, then:

```bash
cd dashboard/build
python3 analysis.py                        # survey.csv -> data.json
python3 -c "import json;t=open('tpl.html').read();\
d=json.dumps(json.load(open('data.json')),ensure_ascii=False).replace('</','<\\/');\
open('index.html','w').write(t.replace('__DATA__',d))"
node mkworker.js                           # index.html -> worker.js
```

`clean.py` fixes spelling, capitalisation and punctuation in the free-text answers;
`overrides.py` holds the hand-edited version of each longer comment. Themes are assigned
by keyword in `analysis.py`, so theme counts are approximate.
