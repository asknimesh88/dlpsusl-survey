import re
TYPOS = {
 'managment':'management','managemnt':'management','prodution':'production','feild':'field','fild':'field',
 'prctices':'practices','practicle':'practical','practiclas':'practicals','theoritical':'theoretical','theoritically':'theoretically',
 'exposer':'exposure','exporsure':'exposure','expouser':'exposure','exposurer':'exposure','orieneted':'oriented',
 'colloboration':'collaboration','colloborate':'collaborate','industral':'industrial','traing':'training','trainig':'training',
 'perid':'period','perod':'period','preffered':'preferred','releted':'related','seperately':'separately','seperate':'separate',
 'assement':'assessment','assesment':'assessment','usefull':'useful','evalutation':'evaluation','stressfull':'stressful',
 'experinced':'experienced','experince':'experience','atrtractive':'attractive','senesters':'semesters','mange':'manage',
 'tuff':'tough','nutral':'neutral','mich':'much','nenecessary':'necessary','wirkload':'workload','shoul':'should','thar':'that',
 'cordinate':'coordinate','valuble':'valuable','facalties':'faculties','yhat':'that','werent':"weren't",'subect':'subject',
 'recommed':'recommend','commen':'common','digress':'degree','impotent':'important','oppertunites':'opportunities',
 'atleast':'at least','ssustainable':'sustainable','exctension':'extension','helth':'health','scienes':'science',
 'fomulation':'formulation','kknowledge':'knowledge','aplications':'applications','softwares':'software','aswell':'as well',
 'animl':'animal','intrument':'instrument','ffood':'food','cerificate':'certificate','bettwr':'better','mor':'more',
 'ues':'Yes','yed':'Yes','sacrifies':'sacrifice','activites':'activities','enviroment':'environment','developement':'development',
 'carrier':'career','ect':'etc.','guidence':'guidance','comparision':'comparison','demonstartor':'demonstrator',
 'aliza':'ELISA','behavior':'behaviour','behaviour':'behaviour','analyse':'analyse','analyze':'analyse','analyzing':'analysing',
 'program':'programme','programs':'programmes','organize':'organise','organized':'organised','utilization':'utilisation',
 'specialization':'specialisation','specialized':'specialised',
}
NONRESP = {'','-','.','*','no','none','nothing','no comments','no comment','no special comments','no suggestions',
           'not applicable','no idea','n/a','na','no.','nil','no problems','no answer','no answer for that',
           'xx','xxx','xxxx','xxxxx','mo','x','ok.','none.'}

def _typos(s):
    for k,v in TYPOS.items():
        def rep(m,v=v):
            w=m.group(0)
            return v[0].upper()+v[1:] if w[0].isupper() and v[0].islower() else v
        s = re.sub(r'(?<![A-Za-z])'+re.escape(k)+r'(?![A-Za-z])', rep, s, flags=re.I)
    return s

def _sentence(line):
    s = line.strip().replace('​','').replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')
    s = s.strip('"').strip()
    if len(s) > 5 and s.isupper(): s = s.lower()
    s = _typos(re.sub(r'\s+',' ',s))
    s = re.sub(r'\.{2,}','.',s)
    s = re.sub(r'\s+([,.;:!?])',r'\1',s)
    s = re.sub(r'([,;:])(?=[A-Za-z])',r'\1 ',s)
    s = re.sub(r'\.(?=[A-Z][a-z])','. ',s)
    s = re.sub(r',\s*,',',',s)
    s = re.sub(r'\bi\b','I',s)
    s = s.strip(' ,;')
    if not s: return ''
    s = s[0].upper()+s[1:]
    s = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1)+m.group(2).upper(), s)
    return s if s[-1] in '.!?' else s+'.'

def clean(text):
    if text is None or isinstance(text,float): return None
    raw = str(text)
    if raw.strip().lower().strip(' .') in NONRESP or raw.strip().lower() in NONRESP: return None
    out = ' '.join(filter(None,(_sentence(l) for l in re.split(r'\n+', raw) if l.strip())))
    return out or None
