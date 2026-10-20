"""Turn a survey CSV export into the record shape app/lib/aggregate.js expects.

    CSV_DIR=/path/to/csvs python3 build_responses.py aquatic.csv > ../public/data/responses-aquatic.json

Both module exports share the same question layout: columns 0-26 are fixed, the course
blocks are delimited by the 14(i) / 14(ii) / 15 comment columns, and every question after
15 sits at a fixed offset from it. Column *numbers* differ between exports (the animal
module has 36 courses, the aquatic one 34), so nothing here is indexed by hand.
"""
import pandas as pd, re, json, os, sys
from clean import clean as _clean
from overrides import POST

# Pilot submissions filed while the form was being set up: staff accounts whose
# free-text answers are all placeholders ("Xxx", "Mo"). Keyed on the form's own
# timestamp so a rebuild cannot quietly let them back in.
EXCLUDE_TIMESTAMPS = {
    "2026/07/03 6:31:39 AM GMT+5:30",  # aquatic: Senior Lecturer, year given as 2005
}

PLACEHOLDER = {'', '-', '.', '*', 'nan', 'xx', 'xxx', 'xxxx', 'xxxxx', 'mo', 'x'}

def txt(v):
    """Raw-ish text: trim and drop placeholder answers. Returns None when empty."""
    s = re.sub(r'\s+', ' ', str(v)).strip()
    return None if s.lower() in PLACEHOLDER else s

def tidy(v):
    """Readable text: spelling, capitalisation and punctuation fixed."""
    r = _clean(v)
    if r is None: return None
    return POST.get(r, r)

def role(v):
    """Job title / employer: a bare "No" means there wasn't one."""
    s = txt(v)
    return None if s and s.lower() in ('no', 'none', 'first job', 'student') else s

def num(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def multi(v):
    s = str(v)
    return [] if s == 'nan' else [x.strip() for x in s.split(';') if x.strip()]

def year(v):
    m = re.search(r'((?:19|20)\d\d)', str(v))
    if m: return m.group(1)
    m = re.search(r'-(\d\d)$', str(v).strip())
    return '20' + m.group(1) if m else 'Unknown'

def emp_duration(v):
    s = txt(v)
    if not s: return None
    if s in ('Less than 1 month', '1-3 months', '3-6 months', 'Over 6 months'): return s
    return '1 year or more'          # free-text answers are all a year or longer

YES = ('yes', 'yed', 'yeah', 'definitely', 'of course', 'exactly', 'highly recommend', 'absolutely')
SOFT = ('somewhat', 'partly', 'partially', 'to some extent', 'in to some extent', 'little', 'sometimes')
def yn(v, soft_label='Somewhat'):
    """Free-text yes/no answer -> the vocabulary already used in responses.json."""
    s = (txt(v) or '').lower()
    if not s: return 'Other'
    if s.startswith(SOFT): return soft_label
    if s.startswith('no') and not s.startswith(('not bad', 'none of')): return 'No'
    if s.startswith(YES) or s.startswith(('good', 'very good', 'excellent', 'best', 'perfect', 'satisfied', 'highly')):
        return 'Yes'
    return 'Other'

# Free-text course names -> the canonical course title in this module
PAT = [
    ('Quality Management of Food Processing and Handling', r'quality'),
    ('Poultry Production', r'poultry'), ('Meat Science and Technology', r'meat|mat science'),
    ('Laboratory Techniques in Livestock Production', r'lab(oratory)? ?tech'),
    ('Applied Animal Nutrition', r'applied animal nutrition|animal nutrition'),
    ('Principles of Food Science & Technology', r'food scien'),
    ('Food Microbiology', r'food micro|microbiolog'), ('Food and Nutrition', r'food (and|&) nutri'),
    ('Cereal Science & Technology', r'cereal'), ('Dairy Science and Technology', r'dairy science'),
    ('Dairy Production', r'dairy production'), ('Industrial Training', r'industr\w* training|lp *42012'),
    ('Research Project', r'research'), ('Proposal Formulation & Scientific Writing', r'propo?sal|propsal'),
    ('Farm Practice-LP', r'farm practice'), ('Animal Health & Hygiene', r'health (and|&) hygiene'),
    ('Health Management of Livestock Species & Fish', r'health management of livestock'),
    ('Zoonoses and Public Health', r'zoonos'),
    ('Animal Reproduction & Assisted Reproductive Technologies', r'reproduct'),
    ('Animal Biotechnology', r'animal biotech'),
    ('Processing & Utilization of Animal Byproducts', r'by ?products'),
    ('Animal Behavior & Welfare', r'animal behavio'),
    ('Anatomy and Physiology of Farm Animals', r'anatomy'),
    ('Fundamentals of Biochemistry', r'biochem'), ('Agrostology', r'agrostology'),
    ('Management of Non-Ruminants', r'non.?ruminant'), ('Management of Ruminants', r'management of ruminants'),
    ('Ornamental Fish Culture', r'ornamental'), ('Fish Breeding and Larviculture', r'fish breeding|larvicult'),
    ('Biology of Aquatic Organisms', r'biology of aquatic'),
    ('Technology of Fish Species Production', r'technology of fish|fish species production'),
    ('Fishery Product Technology', r'fishery product technology'),
    ('Risk Assessment and Food Safety Management in Fishery Product', r'risk ass|food safety management in fishery'),
    ('Applied Fish Nutrition and Live Feed Technology', r'fish nutrition|live feed'),
    ('Fish Diseases and Health Management', r'fish disease'),
    ('Principles of Aquatic Bioresource Management', r'principles of aquatic'),
    ('Recent Advances in Biotechnology and Molecular Biology in Aquaculture', r'recent advances'),
    ('Introduction to Aquatic Biology and Aquaculture', r'aquatic biology'),
]
CODE = {'lp42012': 'Industrial Training', 'lp31063': 'Quality Management of Food Processing and Handling',
        'lp32073': 'Meat Science and Technology', 'lp31053': 'Poultry Production',
        'lp41093': 'Laboratory Techniques in Livestock Production', 'lp32064': 'Dairy Science and Technology',
        'lp31042': 'Food and Nutrition', 'lp41042': 'Cereal Science & Technology'}

def course_title(header):
    return re.sub(r'^\s*LP\s?[\d]+\s*-?\s*', '', header).strip()

def build(path, readable=True):
    df = pd.read_csv(path)
    C = list(df.columns)
    df = df[~df[C[0]].astype(str).isin(EXCLUDE_TIMESTAMPS)]
    at = lambda p: next(i for i, c in enumerate(C) if c.startswith(p))
    i14a, i14b, b = at('14(i).'), at('14(ii)'), at('15.')
    blocks = [('core', C[16:i14a]), ('compulsory', C[i14a+1:i14b]), ('elective', C[i14b+1:b])]

    columns, col_of = [], {}
    for cat, headers in blocks:
        for h in headers:
            code = re.match(r'\s*(LP\s?[\d]+)', h).group(1).replace(' ', '')
            cid = f'{code}-{len(columns)}'
            columns.append({'id': cid, 'code': code, 'title': course_title(h), 'category': cat})
            col_of[cid] = h
    titles = {c['title'] for c in columns}
    text_fn = tidy if readable else txt
    O = lambda k: C[b + k]

    records = []
    for _, r in df.iterrows():
        raw15 = re.sub(r'\s+', ' ', str(r[O(0)]).lower())
        flat15 = re.sub(r'\s', '', raw15)
        useful = set()
        if raw15 != 'nan':
            for name, p in PAT:
                if name in titles and re.search(p, raw15): useful.add(name)
            for code, name in CODE.items():
                if code in flat15 and name in titles: useful.add(name)

        text = {}
        for q, col in [('12', C[14]), ('14i', C[i14a]), ('14ii', C[i14b]), ('15', O(0)), ('16b', O(2)),
                       ('17', O(3)), ('22', O(13)), ('24', O(21)), ('29', O(31)), ('30', O(32)),
                       ('31', O(33)), ('32', O(34)), ('33', O(35)), ('34', O(36)), ('35', O(37)),
                       ('36', O(38)), ('37', O(39)), ('43', O(45))]:
            v = text_fn(r[col])
            if v: text[q] = v

        records.append({
            'year': year(r[C[1]]), 'finalResult': txt(r[C[3]]), 'sector': multi(r[C[4]]),
            'roleNow': role(r[C[5]]), 'rolePrev': role(r[C[6]]), 'company': role(r[C[7]]),
            'empDuration': emp_duration(r[C[8]]), 'waitingPeriod': txt(r[C[9]]),
            'jobRelatedness': txt(r[C[10]]), 'fieldExpertise': multi(r[C[11]]),
            'postgrad': txt(r[C[12]]), 'qualification': txt(r[C[13]]), 'careerPrep': num(r[C[15]]),
            'courses': {c['id']: num(r[col_of[c['id']]]) for c in columns},
            'usefulCourses': sorted(useful), 'outdated': txt(r[O(1)]),
            'activities': {c: txt(r[C[b+4+i]]) for i, c in enumerate(
                ['Laboratory experiments', 'Product development', 'Industry visits',
                 'Workshops', 'Case studies', 'Field-based learning'])},
            'trainingDuration': txt(r[O(10)]), 'evalEffective': txt(r[O(11)]),
            'strengthen': multi(r[O(12)]),
            'teaching': {C[b+14+i].replace('.1', ''): num(r[C[b+14+i]]) for i in range(7)},
            'assessment': {C[b+22+i]: num(r[C[b+22+i]]) for i in range(6)},
            'ilo': num(r[O(28)]), 'assessAligned': num(r[O(29)]), 'examFlex': num(r[O(30)]),
            'expectationsMet': yn(r[O(32)]), 'facedChallenges': yn(r[O(35)]),
            'flexibility': yn(r[O(36)]), 'recommend': yn(r[O(39)]),
            'comparedSimilar': txt(r[O(40)]), 'strengths': multi(r[O(41)]), 'improve': multi(r[O(42)]),
            'overallExp': num(r[O(43)]), 'jobSkills': num(r[O(44)]), 'text': text,
        })
    return {'courseColumns': columns, 'responses': records}


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'aquatic.csv'
    raw = '--raw' in sys.argv
    path = os.path.join(os.environ.get('CSV_DIR', os.path.dirname(os.path.abspath(__file__))), name)
    print(json.dumps(build(path, readable=not raw), ensure_ascii=False, indent=1))
