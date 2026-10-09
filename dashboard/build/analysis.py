"""Build data.json for the survey dashboard from one CSV per module.

Both module exports share the same question layout: columns 0-26 are fixed,
the course blocks are delimited by the 14(i) / 14(ii) / 15 comment columns,
and everything after question 15 sits at a fixed offset from it.
"""
import pandas as pd, re, json, collections, os
from clean import clean as _clean
from overrides import POST

# Where the two CSV exports live. Override with CSV_DIR=/path when rebuilding.
CSV_DIR = os.environ.get('CSV_DIR', os.path.dirname(os.path.abspath(__file__)))

MODULES = [
    {'id':'animal','label':'Animal Bio-Resource','full':'Animal Bio-Resource Technology and Management',
     'csv':'animal.csv',
     'note':'Every graduate rated all 36 courses, including the three aquatic ones this '
            'specialisation does not take, so a low rating on those means "not taken" rather than "poor".'},
    {'id':'aquatic','label':'Aquatic Bio-Resource','full':'Aquatic Bio-Resource Technology and Management',
     'csv':'aquatic.csv',
     'note':'Every graduate rated all 34 courses in this specialisation.',
     'warn':'Only 9 graduates responded, so one person moves any percentage by about 11 points. '
            'Read these figures as indicative, and the written comments as the more reliable signal.'},
]

def clean(v):
    r = _clean(v)
    if r is None: return None
    r = POST.get(r, r)
    return re.sub(r"\bIts (good|great|better)", r"It's \1", r)

def year(v):
    m = re.search(r'(20\d\d)', str(v))
    if m: return m.group(1)
    m = re.search(r'-(\d\d)$', str(v).strip())
    return '20'+m.group(1) if m else 'Unknown'

def split(v): return [x.strip() for x in str(v).split(';') if x.strip() and str(v) != 'nan']

def dur(v):
    s = str(v).strip()
    if s.lower() in ('-','nan',''): return 'Not stated'
    if s in ('Less than 1 month','1-3 months','3-6 months','Over 6 months'):
        return s.replace('1-3','1–3').replace('3-6','3–6')
    return 'Over 6 months'

def cat_expect(v):
    s = str(v).strip().lower()
    if s.startswith('somewhat'): return 'Somewhat'
    if s.startswith('no') and not s.startswith('not '): return 'No'
    if s.startswith(('yes','excellent','good','find a job','from lectures')): return 'Yes'
    return 'Other answer'

def cat_rec(v):
    s = str(v).strip().lower()
    if s in ('*','.','-','nan','xxxx','xxx'): return 'No answer'
    if 'yes' in s or 'recommend' in s: return 'Yes'
    return 'With reservations'

def cat_chal(v):
    s = str(v).strip().lower()
    if s in ('*','.','-','nan','xxx','xx'): return 'No answer'
    if s.startswith('no'): return 'No'
    if s.startswith('sometimes'): return 'Sometimes'
    return 'Yes'

def cat_flex(v):
    s = str(v).strip().lower()
    if s in ('*','.','-','nan','xxxx','xxx'): return 'No answer'
    if s == 'no': return 'No'
    if any(k in s for k in ('somewhat','some extent','neutral','difficult')): return 'Somewhat'
    return 'Yes'

def cat_work(v):
    s = str(v).strip().lower()
    if s in ('*','.','-','nan','xx','xxx'): return 'No answer'
    # "not too much" / "no much workload" are light, not heavy - check before the heavy words
    if re.search(r'\b(not|no|isn\'?t|never)\b[\w\s]{0,12}(too much|much workload|work ?load)', s): return 'Manageable'
    if 'more difficult' in s: return 'Other comment'
    if any(k in s for k in ('entertainment','free time')): return 'Other comment'
    if 'bulky' in s or 'some subject' in s or 'some course' in s or 'some semesters' in s or 'some times' in s:
        return 'Heavy in some subjects'
    if any(k in s for k in ('but','although')) and any(k in s for k in
            ('manage','useful','necessary','worthwhile','bear','tolerance','look back','fair','capacity','experiences')):
        return 'Heavy but worthwhile'
    if any(k in s for k in ('too much','highly workload','huge','tough','little bit more','a bit high','a little high','saturday')):
        return 'Too heavy'
    return 'Manageable'

ROLE_PAT = [
    ('Quality assurance and food safety', r'quality|\bqa\b|food safety'),
    ('Farm and production management',    r'farm|production|livestock|supervisor|hatchery|breeder|poultry|dairy|shrimp|stores'),
    ('Academia and teaching',             r'demonstrator|lecturer|teach|instructor|registrar'),
    ('Research, laboratory and animal health', r'research|laborator|\blab\b|technologist|nutritionist|veterinar|patholog|biologist'),
    ('Business, sales and corporate',     r'market|sales|account|export|executive|analyst|medical|officer|manager|coordinator|business|entrepreneur|advisor'),
]
def cat_role(v):
    s = str(v).lower()
    if s in ('-','no','nan','*','.','xxx'): return 'Not stated'
    for name, p in ROLE_PAT:
        if re.search(p, s): return name
    return 'Other'

def label(c):
    m = re.match(r'\s*(LP\s?[\d]+)\s*-?\s*(.*)', c)
    code = m.group(1).replace(' ', '') if m else ''
    nm = (m.group(2) if m else c).strip()
    nm = (nm.replace('Behavior', 'Behaviour').replace('assesment', 'Assessment')
            .replace('Micro livestock', 'Micro-livestock').replace('Farm Practice-LP', 'Farm Practice (LP)')
            .replace('Utilization', 'Utilisation'))
    if nm.endswith('Fishery Product'): nm += 's'
    return code, nm[0].upper() + nm[1:]

# Courses named in answer to Q15. Only counted when the module actually offers that course.
PAT = [
    ('Quality Management of Food Processing and Handling', r'quality'),
    ('Poultry Production', r'poultry'),
    ('Meat Science and Technology', r'meat|mat science'),
    ('Laboratory Techniques in Livestock Production', r'lab(oratory)? ?tech'),
    ('Applied Animal Nutrition', r'applied animal nutrition|animal nutrition'),
    ('Principles of Food Science & Technology', r'food scien'),
    ('Food Microbiology', r'food micro|microbiolog'),
    ('Food and Nutrition', r'food (and|&) nutri'),
    ('Cereal Science & Technology', r'cereal'),
    ('Dairy Science and Technology', r'dairy science'),
    ('Dairy Production', r'dairy production'),
    ('Industrial Training', r'industr\w* training|lp *42012'),
    ('Research Project', r'research'),
    ('Proposal Formulation & Scientific Writing', r'propo?sal|propsal'),
    ('Farm Practice (LP)', r'farm practice'),
    ('Animal Health & Hygiene', r'health (and|&) hygiene'),
    ('Health Management of Livestock Species & Fish', r'health management of livestock'),
    ('Zoonoses and Public Health', r'zoonos'),
    ('Animal Reproduction & Assisted Reproductive Technologies', r'reproduct'),
    ('Animal Biotechnology', r'animal biotech'),
    ('Processing & Utilisation of Animal Byproducts', r'by ?products'),
    ('Animal Behaviour & Welfare', r'animal behavio'),
    ('Anatomy and Physiology of Farm Animals', r'anatomy'),
    ('Fundamentals of Biochemistry', r'biochem'),
    ('Agrostology', r'agrostology'),
    ('Management of Non-Ruminants', r'non.?ruminant'),
    ('Management of Ruminants', r'management of ruminants'),
    ('Ornamental Fish Culture', r'ornamental'),
    ('Fish Breeding and Larviculture', r'fish breeding|larvicult'),
    ('Biology of Aquatic Organisms', r'biology of aquatic'),
    ('Technology of Fish Species Production', r'technology of fish|fish species production'),
    ('Fishery Product Technology', r'fishery product technology'),
    ('Risk Assessment and Food Safety Management in Fishery Products', r'risk ass|food safety management in fishery'),
    ('Applied Fish Nutrition and Live Feed Technology', r'fish nutrition|live feed'),
    ('Fish Diseases and Health Management', r'fish disease'),
    ('Principles of Aquatic Bioresource Management', r'principles of aquatic'),
    ('Recent Advances in Biotechnology and Molecular Biology in Aquaculture', r'recent advances'),
    ('Introduction to Aquatic Biology and Aquaculture', r'aquatic biology'),
]
CODE = {'lp42012':'Industrial Training','lp31063':'Quality Management of Food Processing and Handling',
        'lp32073':'Meat Science and Technology','lp31053':'Poultry Production',
        'lp41093':'Laboratory Techniques in Livestock Production','lp32064':'Dairy Science and Technology',
        'lp31042':'Food and Nutrition','lp41042':'Cereal Science & Technology'}
EXTRA = ('Non-LP subjects (English, IT, management)',
         r'english|\bit\b|ict|management subjects|strategic management|human resource|agri ?business')

THEME = {
 'strength': [('Practical, farm and field training', r'practical|farm|field|hands-on|laborator|lab practice'),
   ('Experienced, supportive staff', r'staff|lecturer|professor|guidance|human resources|teaching|panel'),
   ('Industry relevance and training', r'industr|haccp|iso|food safety|job field|job market|survive in industry'),
   ('Broad, comprehensive curriculum', r'curriculum|comprehensive|multidisciplinar|multi disciplinar|wide range|management|theor|subject content|foundation|knowledge|specialisation|various fields'),
   ('Personal development and work ethic', r'work hard|profile|workload|life experience|english')],
 'weakness': [('Limited industry exposure or short training', r'industr'),
   ('Not enough practical or field work', r'practical|field|farm|hands-on'),
   ('Facilities, labs and resources', r'facilit|laborator|\blab\b|animals in faculty|equipment'),
   ('Workload, duration and delays', r'workload|too much|long|time taken|bulk|time to study'),
   ('Online teaching', r'online'),
   ('Outdated content or assessment', r'outdated|update|traditional|examination|assignment type'),
   ('Missing marine or aquaculture content', r'marine')],
 'newTopics': [('AI, precision farming and digital tools', r'artificial|\bai\b|precision|digital|data|software|gis|smart|technolog|innovation'),
   ('Food quality, safety and standards', r'quality|food safety|fssc|brc|audit|standard|certificate'),
   ('Business, marketing and entrepreneurship', r'business|management techni|marketing|entrepreneur|economics|supply chain|farm-to-table|agribusiness'),
   ('Marine, aquaculture and fisheries', r'marine|aquacultur|fisher|aqua ?scaping|breeding techni'),
   ('Longer industrial training and workplace skills', r'industrial training|six months|15 weeks|workplace|ethics|placement'),
   ('Communication and soft skills', r'communication|english|presentation|customer|problem solving'),
   ('Sustainability and modern farming', r'sustainab|climate|waste|eco|integrated farming|modern farming'),
   ('Meat science and livestock topics', r'meat science')],
 'research': [('Extend the training period (often six months)', r'extend|increase|longer|six months|6 month|more time|lengthen|15 weeks|not enough|insufficient|period'),
   ('Separate research from industrial training', r'separat|before industrial|two semesters|should not include research'),
   ('Stronger industry collaboration', r'industry expert|uni-industry|industrial related|industry exposure|collaboration|trends|opportunities|industrial experience'),
   ('Research skills, data analysis and supervision', r'data analysis|statistic|scientific writing|supervis|research topic|workshops')],
 'assessSugg': [('More practical and field-based assessment', r'practical|field|farm|industrial based'),
   ('Presentations, viva and discussion', r'presentation|viva|discussion'),
   ('Case studies, projects and continuous assessment', r'case stud|project|assignment|quiz|continuous|internship|problem solving'),
   ('Exam scheduling and workload', r'schedul|gap|stress|exam hall|daily|flexible')],
 'teachSugg': [('More practical, lab and field work', r'practical|field|laborator|hands-on'),
   ('Industry links and real-world examples', r'industr|real|solutions'),
   ('Case studies and problem-based learning', r'case|problem'),
   ('Self-directed and interactive learning', r'self|interactive|engagement'),
   ('Less online learning', r'online')],
}

# Short "nothing to change" answers to an improvement question are not a suggestion:
# keep the comment visible but leave it out of the theme counts.
NO_ISSUE = re.compile(r'^(no\b|none|nothing|there is no|everything (was|is) (good|perfect)|good|satisfactory'
                      r'|all (things )?are good|the current subjects are fine|current subjects are okay'
                      r'|i am satisfied|no idea)', re.I)
SUGGESTION_KEYS = ('weakness', 'newTopics', 'research', 'assessSugg', 'teachSugg')

PRACTICAL = ['Laboratory experiments','Product development','Industry visits','Workshops','Case studies','Field-based learning']


def build(mod):
    df = pd.read_csv(os.path.join(CSV_DIR, mod['csv']))
    C = list(df.columns)
    at = lambda prefix: next(i for i, c in enumerate(C) if c.startswith(prefix))
    i14a, i14b, b = at('14(i).'), at('14(ii)'), at('15.')
    core, comp, other = C[16:i14a], C[i14a+1:i14b], C[i14b+1:b]
    groups = {'Core': [label(c) for c in core], 'Specialisation': [label(c) for c in comp],
              'Electives': [label(c) for c in other]}
    names = {n for v in groups.values() for _, n in v}
    # column offsets from question 15, identical in both exports
    O = lambda k: C[b + k]
    rows = []
    for _, r in df.iterrows():
        row = {'year': year(r[C[1]]), 'result': r[C[3]], 'sector': str(r[C[4]]).replace('Self employed', 'Self-employed'), 'role': cat_role(r[C[5]]),
               'employDur': dur(r[C[8]]), 'wait': r[C[9]], 'related': r[C[10]], 'fields': split(r[C[11]]),
               'pg': r[C[12]], 'prep': int(r[C[15]]),
               'courses': {label(c)[1]: int(r[c]) for c in core + comp + other},
               'prac': dict(zip(PRACTICAL, (r[O(k)] for k in range(4, 10)))),
               'trainDur': r[O(10)], 'evalEff': r[O(11)], 'strengthen': split(r[O(12)]),
               'teach': {C[b+14+k].replace('.1', ''): int(r[C[b+14+k]]) for k in range(7)},
               'assess': {C[b+22+k]: int(r[C[b+22+k]]) for k in range(6)},
               'ilo': int(r[O(28)]), 'aligned': int(r[O(29)]), 'flexExam': int(r[O(30)]),
               'expect': cat_expect(r[O(32)]), 'recommend': cat_rec(r[O(39)]), 'challenge': cat_chal(r[O(35)]),
               'flex': cat_flex(r[O(36)]), 'workload': cat_work(r[O(34)]), 'outdated': r[O(1)],
               'compare': r[O(40)], 'strengths': split(r[O(41)]), 'improve': split(r[O(42)]),
               'overall': int(r[O(43)]), 'skills': int(r[O(44)])}
        cm = {'core': clean(r[C[i14a]]), 'comp': clean(r[C[i14b]])}
        for key, k in [('outdatedWhich',2),('newTopics',3),('research',13),('teachSugg',21),('assessSugg',31),
                       ('expectText',32),('teachComment',33),('workloadText',34),('challengeText',35),
                       ('flexText',36),('strength',37),('weakness',38),('recommendText',39),('final',45)]:
            cm[key] = clean(r[O(k)])
        for k in ('expectText','recommendText','challengeText','flexText','teachComment','workloadText'):
            if cm[k] and re.fullmatch(r"(Yes|No|Yeah|Somewhat|Sometimes|Good|Very good|Excellent|Best|Satisfactory"
                                      r"|Satisfied|Fine|Neutral|Ok|OK|Maybe|Normal|Adequate|Sufficient|Bearable|Enough|Manageable)\.?", cm[k]):
                cm[k] = None
        row['comments'] = cm

        s = re.sub(r'\s+', ' ', str(r[O(0)]).lower()); s2 = re.sub(r'\s', '', s)
        u = set()
        if s != 'nan':
            for name, p in PAT:
                if name in names and re.search(p, s): u.add(name)
            for code, name in CODE.items():
                if code in s2 and name in names: u.add(name)
            if re.search(EXTRA[1], s): u.add(EXTRA[0])
        row['useful'] = sorted(u)

        row['themes'] = {}
        for key, rules in THEME.items():
            t = cm.get(key)
            if not t: continue
            if key in SUGGESTION_KEYS and len(t.split()) < 12 and NO_ISSUE.match(t): continue
            row['themes'][key] = [n for n, p in rules if re.search(p, t.lower())] or ['Other']
        rows.append(row)

    out = {k: mod[k] for k in ('id','label','full','note') if k in mod}
    if 'warn' in mod: out['warn'] = mod['warn']
    out.update(n=len(rows), dates=[str(df[C[0]].iloc[0])[:10].replace('/', '-'),
                                   str(df[C[0]].iloc[-1])[:10].replace('/', '-')],
               groups={g: [{'code': a, 'name': n} for a, n in v] for g, v in groups.items()}, rows=rows)
    return out


if __name__ == '__main__':
    data = {'modules': [build(m) for m in MODULES]}
    json.dump(data, open('data.json', 'w'), ensure_ascii=False, default=str)
    import statistics as st
    for m in data['modules']:
        R = m['rows']
        print(f"== {m['id']}  n={m['n']}  overall={st.mean(r['overall'] for r in R):.2f}  "
              f"courses={len(R[0]['courses'])}  dates={m['dates']}")
        for k in ('workload','recommend','expect','compare'):
            print('  ', k, collections.Counter(r[k] for r in R).most_common())
        print('   useful', collections.Counter(x for r in R for x in r['useful']).most_common(6))
        print('   unmatched-useful-themes', collections.Counter(
            x for r in R for x in r['themes'].get('newTopics', []) if x == 'Other').most_common())
