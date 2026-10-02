import pandas as pd, re, json, collections
from clean import clean as _clean
from overrides import POST
df = pd.read_csv('survey.csv'); C=list(df.columns); N=len(df)

def clean(v):
    r=_clean(v)
    if r is None: return None
    r=POST.get(r,r)
    r=re.sub(r"\bIts (good|great|better)",r"It's \1",r)
    return r

def year(v):
    m=re.search(r'(20\d\d)',str(v))
    if m: return m.group(1)
    m=re.search(r'-(\d\d)$',str(v).strip())
    return '20'+m.group(1) if m else 'Unknown'
def split(v): return [x.strip() for x in str(v).split(';') if x.strip() and str(v)!='nan']
def dur(v):
    s=str(v).strip()
    if s.lower() in ('-','nan',''): return 'Not stated'
    if s in ('Less than 1 month','1-3 months','3-6 months','Over 6 months'):
        return s.replace('1-3','1–3').replace('3-6','3–6')
    return 'Over 6 months'

def cat_expect(v):
    s=str(v).strip().lower()
    if s.startswith('somewhat'): return 'Somewhat'
    if s.startswith(('yes','excellent','good','find a job','from lectures')): return 'Yes'
    return 'Other answer'
def cat_rec(v):
    s=str(v).strip().lower()
    if s in ('*','.','-','nan'): return 'No answer'
    if 'yes' in s or 'recommend' in s: return 'Yes'
    return 'With reservations'
def cat_chal(v):
    s=str(v).strip().lower()
    if s in ('*','.','-','nan'): return 'No answer'
    if s.startswith('no'): return 'No'
    if s.startswith('sometimes'): return 'Sometimes'
    return 'Yes'
def cat_flex(v):
    s=str(v).strip().lower()
    if s in ('*','.','-','nan'): return 'No answer'
    if s=='no': return 'No'
    if any(k in s for k in ('somewhat','some extent','neutral','difficult')): return 'Somewhat'
    return 'Yes'
def cat_work(v):
    s=str(v).strip().lower()
    if s in ('*','.','-','nan'): return 'No answer'
    if any(k in s for k in ('entertainment','free time')): return 'Other comment'
    if 'bulky' in s or 'some subject' in s or 'some course' in s or 'some semesters' in s or 'some times' in s: return 'Heavy in some subjects'
    if any(k in s for k in ('but','although')) and any(k in s for k in ('manage','useful','necessary','worthwhile','bear','tolerance','look back','fair','capacity','experiences')):
        return 'Heavy but worthwhile'
    if any(k in s for k in ('too much','highly workload','huge','tough','little bit more','a bit high','a little high','saturday')): return 'Too heavy'
    return 'Manageable'
def cat_role(v):
    s=str(v).lower()
    if s in ('-','no','nan','*','.'): return 'Not stated'
    for name,p in [('Quality assurance and food safety',r'quality|qa\b|food safety'),
                   ('Farm and production management',r'farm|production|livestock|supervisor|hatchery|breeder|poultry|dairy'),
                   ('Academia and teaching',r'demonstrator|lecturer|teach|instructor|assistant lecturer|registrar'),
                   ('Research, laboratory and animal health',r'research|laborator|\blab\b|technologist|nutritionist|veterinar|patholog'),
                   ('Business, sales and corporate',r'market|sales|account|export|executive|analyst|medical|officer|manager|coordinator|business')]:
        if re.search(p,s): return name
    return 'Other'

core=C[16:27]; comp=C[28:45]; other=C[46:54]
def label(c):
    m=re.match(r'\s*(LP\s?[\d]+)\s*-\s*(.*)',c)
    code=m.group(1).replace(' ','') if m else ''
    nm=(m.group(2) if m else c).strip()
    nm=(nm.replace('Behavior','Behaviour').replace('assesment','Assessment')
          .replace('Micro livestock','Micro-livestock').replace('Farm Practice-LP','Farm Practice (LP)')
          .replace('Utilization','Utilisation'))
    return code, nm[0].upper()+nm[1:]
groups={'Core':[label(c) for c in core],'Specialisation':[label(c) for c in comp],'Electives':[label(c) for c in other]}

PAT=[('Quality Management of Food Processing and Handling',r'quality'),
 ('Poultry Production',r'poultry'),('Meat Science and Technology',r'meat|mat science'),
 ('Laboratory Techniques in Livestock Production',r'lab(oratory)? ?tech'),
 ('Applied Animal Nutrition',r'applied animal nutrition|animal nutrition'),
 ('Principles of Food Science & Technology',r'food scien'),('Food Microbiology',r'food micro'),
 ('Food and Nutrition',r'food (and|&) nutri'),('Cereal Science & Technology',r'cereal'),
 ('Dairy Science and Technology',r'dairy science'),('Dairy Production',r'dairy production'),
 ('Industrial Training',r'industr\w* training|lp *42012'),('Research Project',r'research'),
 ('Proposal Formulation & Scientific Writing',r'proposal'),('Farm Practice (LP)',r'farm practice'),
 ('Animal Health & Hygiene',r'health (and|&) hygiene'),
 ('Health Management of Livestock Species & Fish',r'health management of livestock'),
 ('Zoonoses and Public Health',r'zoonos'),
 ('Animal Reproduction & Assisted Reproductive Technologies',r'reproduct'),
 ('Animal Biotechnology',r'biotech'),('Processing & Utilisation of Animal Byproducts',r'by ?products'),
 ('Animal Behaviour & Welfare',r'animal behavio'),
 ('Anatomy and Physiology of Farm Animals',r'anatomy'),('Fundamentals of Biochemistry',r'biochem'),
 ('Agrostology',r'agrostology'),('Management of Non-Ruminants',r'non.?ruminant'),
 ('Management of Ruminants',r'management of ruminants'),
 ('Risk Assessment and Food Safety Management in Fishery Products',r'risk ass'),
 ('Non-LP subjects (English, IT, management)',r'english|\bit\b|ict|management subjects|strategic management|human resource|agri ?business')]
CODE={'lp42012':'Industrial Training','lp31063':'Quality Management of Food Processing and Handling',
 'lp32073':'Meat Science and Technology','lp31053':'Poultry Production','lp41093':'Laboratory Techniques in Livestock Production',
 'lp32064':'Dairy Science and Technology','lp31042':'Food and Nutrition','lp41042':'Cereal Science & Technology'}

THEME={
 'strength':[('Practical, farm and field training',r'practical|farm|field|hands-on|laborator'),
   ('Experienced, supportive staff',r'staff|lecturer|professor|guidance|human resources|teaching'),
   ('Industry relevance and training',r'industr|haccp|iso|food safety|job field|job market'),
   ('Broad, comprehensive curriculum',r'curriculum|comprehensive|multidisciplinar|multi disciplinar|wide range|management|theor|subject content|foundation|knowledge|specialisation'),
   ('Personal development and work ethic',r'work hard|profile|workload|life experience|english')],
 'weakness':[('Limited industry exposure or short training',r'industr'),
   ('Not enough practical or field work',r'practical|field|farm|hands-on'),
   ('Facilities, labs and resources',r'facilit|laborator|\blab\b|animals in faculty|equipment'),
   ('Workload, duration and delays',r'workload|too much|long|time taken|bulk|time to study'),
   ('Online teaching',r'online'),
   ('Outdated content or assessment',r'outdated|update|traditional|examination|assignment type')],
 'newTopics':[('AI, precision farming and digital tools',r'artificial|\bai\b|precision|digital|data|software|gis|smart|technolog|innovation'),
   ('Food quality, safety and standards',r'quality|food safety|fssc|brc|audit|standard'),
   ('Business, marketing and entrepreneurship',r'business|management|marketing|entrepreneur|economics|supply chain|farm-to-table|agribusiness'),
   ('Longer industrial training and workplace skills',r'industrial training|six months|15 weeks|workplace|ethics|placement'),
   ('Communication and soft skills',r'communication|english|presentation|customer'),
   ('Sustainability and modern farming',r'sustainab|climate|waste|eco|integrated farming|modern farming')],
 'research':[('Extend the training period (often six months)',r'extend|increase|longer|six months|6 month|more time|lengthen|15 weeks|not enough|period'),
   ('Separate research from industrial training',r'separat|before industrial|two semesters|should not include research'),
   ('Stronger industry collaboration',r'industry expert|uni-industry|industry exposure|collaboration|trends|opportunities'),
   ('Research skills, data analysis and supervision',r'data analysis|statistic|scientific writing|supervis|research topic|workshops')],
 'assessSugg':[('More practical and field-based assessment',r'practical|field|farm'),
   ('Presentations, viva and discussion',r'presentation|viva|discussion'),
   ('Case studies, projects and continuous assessment',r'case stud|project|assignment|quiz|continuous|internship'),
   ('Exam scheduling and workload',r'schedul|gap|stress|exam hall|daily')],
 'teachSugg':[('More practical, lab and field work',r'practical|field|laborator|hands-on'),
   ('Industry links and real-world examples',r'industr|real|solutions'),
   ('Case studies and problem-based learning',r'case|problem'),
   ('Self-directed and interactive learning',r'self|interactive|engagement')],
}

rows=[]
for idx,r in df.iterrows():
    row={'year':year(r[C[1]]),'result':r[C[3]],'sector':r[C[4]],'role':cat_role(r[C[5]]),
     'employDur':dur(r[C[8]]),'wait':r[C[9]],'related':r[C[10]],'fields':split(r[C[11]]),
     'pg':r[C[12]],'prep':int(r[C[15]]),
     'courses':{label(c)[1]:int(r[c]) for c in core+comp+other},
     'prac':{c:r[c] for c in C[58:64]},'trainDur':r[C[64]],'evalEff':r[C[65]],'strengthen':split(r[C[66]]),
     'teach':{c.replace('.1',''):int(r[c]) for c in C[68:75]},
     'assess':{c:int(r[c]) for c in C[76:82]},
     'ilo':int(r[C[82]]),'aligned':int(r[C[83]]),'flexExam':int(r[C[84]]),
     'expect':cat_expect(r[C[86]]),'recommend':cat_rec(r[C[93]]),'challenge':cat_chal(r[C[89]]),
     'flex':cat_flex(r[C[90]]),'workload':cat_work(r[C[88]]),'outdated':r[C[55]],
     'compare':r[C[94]],'strengths':split(r[C[95]]),'improve':split(r[C[96]]),
     'overall':int(r[C[97]]),'skills':int(r[C[98]])}
    cm={}
    for key,i in [('core',27),('comp',45),('outdatedWhich',56),('newTopics',57),('research',67),('teachSugg',75),
                  ('assessSugg',85),('expectText',86),('teachComment',87),('workloadText',88),('challengeText',89),
                  ('flexText',90),('strength',91),('weakness',92),('recommendText',93),('final',99)]:
        cm[key]=clean(r[C[i]])
    for k in ('expectText','recommendText','challengeText','flexText','teachComment'):
        if cm[k] and re.fullmatch(r"(Yes|No|Yeah|Somewhat|Sometimes|Good|Very good|Excellent|Best|Satisfactory|Satisfied|Fine|Neutral|Ok|OK|Maybe|Normal|Adequate|Sufficient|Bearable)\.?",cm[k]): cm[k]=None
    row['comments']=cm
    # useful courses
    s=re.sub(r'\s+',' ',str(r[C[54]]).lower()); s2=re.sub(r'\s','',s)
    u=set()
    if s!='nan':
        for name,p in PAT:
            if re.search(p,s): u.add(name)
        for code,name in CODE.items():
            if code in s2: u.add(name)
    row['useful']=sorted(u)
    # themes
    th={}
    for key,rules in THEME.items():
        t=cm.get(key)
        if t: th[key]=[n for n,p in rules if re.search(p,t.lower())] or ['Other']
    row['themes']=th
    rows.append(row)

data={'n':N,'dates':[str(df[C[0]].iloc[0])[:10],str(df[C[0]].iloc[-1])[:10]],
 'groups':{g:[{'code':a,'name':b} for a,b in v] for g,v in groups.items()},'rows':rows}
json.dump(data,open('data.json','w'),ensure_ascii=False,default=str)
import statistics as st
print('N',N,'overall',round(st.mean(r['overall'] for r in rows),2),'prep',round(st.mean(r['prep'] for r in rows),2))
for k in ['workload','recommend','expect','flex','challenge','role','employDur']:
    print(k,collections.Counter(r[k] for r in rows).most_common())
print('useful',collections.Counter(x for r in rows for x in r['useful']).most_common(10))
for k in THEME: print(k,collections.Counter(x for r in rows for x in r['themes'].get(k,[])).most_common())
