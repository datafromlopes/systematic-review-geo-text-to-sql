# Systematic review: LLM-based text-to-SQL for geospatial data and Brazilian Portuguese.
# Author: Diego Lopes. Part of the pipeline documented in ../README.md.
# All paths are relative to the repository root; run the scripts from there.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *  # noqa: F401,F403
import json, re, collections, unicodedata

acc = json.load(open(W('accepted.json')))
corpus = json.load(open(W('corpus.json')))

def norm(t):
    t = unicodedata.normalize('NFKD', t or '')
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()

def cnt(text, pats):
    return sum(len(re.findall(p, text)) for p in pats)

def hits(text, d, thr=1):
    return sorted({k for k, pats in d.items() if cnt(text, pats) >= thr})

def strip_refs(t):
    for m in re.finditer(r' references ', t):
        if m.start() > 0.45 * len(t):
            return t[:m.start()]
    return t

SPATIAL_STRONG = [r'\bpostgis\b', r'\bst contains\b', r'\bst within\b', r'\bst intersects\b',
    r'\bst distance\b', r'\bst buffer\b', r'\bst dwithin\b', r'\bst area\b', r'\bst geomfromtext\b',
    r'\bst asgeojson\b', r'\bst centroid\b', r'\bspatial sql\b', r'\bspatial database[s]?\b',
    r'\bspatial quer\w+', r'\bgeospatial\b', r'\bspatial join\b', r'\bspatial extension\b',
    r'\bspatiotemporal\b', r'\bspatio temporal\b', r'\bgeographic information system\b',
    r'\bspatial data\b', r'\bspatial relation\w*', r'\bnl2geo\w*', r'\bgeoquer\w+', r'\btext to geosql\b']
SPATIAL_WEAK = [r'\bspatial\b', r'\bgeograph\w+', r'\bgis\b', r'\blatitude\b', r'\blongitude\b',
    r'\bgeometry\b', r'\bgeometric\b', r'\bmap[s]?\b', r'\bsrid\b', r'\bshapefile\b', r'\bwkt\b',
    r'\bopenstreetmap\b', r'\bpoint of interest\b', r'\bcoordinates\b']

MODELS = {
 'GPT-4 family': [r'\bgpt 4\b', r'\bgpt4\b', r'\bgpt 4o\b', r'\bgpt 4 turbo\b'],
 'GPT-3.5': [r'\bgpt 3 5\b', r'\bchatgpt\b', r'\bcodex\b', r'\bgpt 3\b'],
 'GPT-5/o-series': [r'\bgpt 5\b', r'\bo1 preview\b', r'\bo3 mini\b', r'\bo1 mini\b'],
 'Llama': [r'\bllama\b', r'\bllama 2\b', r'\bllama 3\b', r'\bcode llama\b', r'\bcodellama\b'],
 'Qwen': [r'\bqwen\b'],
 'DeepSeek': [r'\bdeepseek\b'],
 'Mistral': [r'\bmistral\b', r'\bmixtral\b'],
 'Gemini/PaLM': [r'\bgemini\b', r'\bpalm\b', r'\bbard\b'],
 'Claude': [r'\bclaude\b'],
 'T5/BART': [r'\bt5\b', r'\bflan t5\b', r'\bbart\b', r'\bcodet5\b'],
 'BERT-family': [r'\bbert\b', r'\broberta\b', r'\belectra\b', r'\bgrappa\b', r'\btabert\b'],
 'LSTM/RNN': [r'\blstm\b', r'\bbi lstm\b', r'\bseq2seq\b', r'\brecurrent neural\b'],
 'GLM/Baichuan/Yi': [r'\bchatglm\b', r'\bglm\b', r'\bbaichuan\b', r'\byi 34b\b', r'\binternlm\b'],
 'StarCoder/CodeGen': [r'\bstarcoder\b', r'\bcodegen\b', r'\bcodegeex\b', r'\bwizardcoder\b'],
 'Phi/Gemma': [r'\bphi 2\b', r'\bphi 3\b', r'\bgemma\b'],
}
DATASETS = {
 'Spider': [r'\bspider\b'], 'BIRD': [r'\bbird\b', r'\bbird sql\b'], 'WikiSQL': [r'\bwikisql\b'],
 'SParC': [r'\bsparc\b'], 'CoSQL': [r'\bcosql\b'], 'KaggleDBQA': [r'\bkaggledbqa\b'],
 'Spider-Syn': [r'\bspider syn\b'], 'Spider-DK': [r'\bspider dk\b'], 'Spider-Realistic': [r'\bspider realistic\b'],
 'Dr.Spider': [r'\bdr spider\b'], 'Spider 2.0': [r'\bspider 2 0\b', r'\bspider2\b'],
 'CSpider': [r'\bcspider\b'], 'DuSQL': [r'\bdusql\b'], 'Chase': [r'\bchase (?:dataset|benchmark)\b', r'\bon chase\b', r'\bchase and \w+sql\b'], 'TableQA': [r'\btableqa\b'],
 'ATIS': [r'\batis\b'], 'GeoQuery': [r'\bgeoquery\b'], 'Scholar': [r'\bscholar dataset\b'],
 'Academic': [r'\bacademic dataset\b'], 'Restaurants': [r'\brestaurants dataset\b'],
 'ScienceBenchmark': [r'\bsciencebenchmark\b'], 'EHRSQL': [r'\behrsql\b'], 'MIMICSQL': [r'\bmimicsql\b'],
 'Archer': [r'\barcher\b'], 'BULL': [r'\bbull (?:dataset|benchmark)\b', r'\bbull cn\b', r'\bon bull\b'], 'AmbiQT': [r'\bambiqt\b'], 'BEAVER': [r'\bbeaver (?:dataset|benchmark)\b', r'\bon beaver\b'],
 'SNAILS': [r'\bsnails\b'], 'Squall': [r'\bsquall\b'], 'FIBEN': [r'\bfiben\b'],
 'SEDE': [r'\bsede\b'], 'AmbrosiaAmbig': [r'\bambrosia\b'], 'ScienceQA/WikiTQ': [r'\bwikitablequestions\b', r'\bwikitq\b'],
}
LANGS = {
 'Chinese': [r'\bchinese\b', r'\bmandarin\b'], 'Portuguese': [r'\bportuguese\b', r'\bbrazilian portuguese\b'],
 'Spanish': [r'\bspanish\b'], 'German': [r'\bgerman language\b', r'\bgerman quer\w+'],
 'French': [r'\bfrench\b'], 'Russian': [r'\brussian\b'], 'Arabic': [r'\barabic\b'],
 'Turkish': [r'\bturkish\b'], 'Indonesian': [r'\bindonesian\b'], 'Filipino': [r'\bfilipino\b', r'\btagalog\b'],
 'Vietnamese': [r'\bvietnamese\b'], 'Korean': [r'\bkorean\b'], 'Japanese': [r'\bjapanese\b'],
 'Hindi': [r'\bhindi\b'], 'Persian': [r'\bpersian\b', r'\bfarsi\b'], 'Bangla': [r'\bbangla\b', r'\bbengali\b'],
 'Thai': [r'\bthai\b'], 'Italian': [r'\bitalian\b'], 'Ukrainian': [r'\bukrainian\b'], 'Polish': [r'\bpolish\b'],
 'Czech': [r'\bczech\b'], 'Hebrew': [r'\bhebrew\b'], 'Urdu': [r'\burdu\b'], 'Kazakh': [r'\bkazakh\b'],
}
APPROACH = {
 'Rule/template-based': [r'\brule based\b', r'\btemplate based\b', r'\bgrammar based\b', r'\bhandcrafted rules\b'],
 'Seq2seq / PLM fine-tuning': [r'\bfine tun\w+', r'\bseq2seq\b', r'\bsequence to sequence\b', r'\bpre trained language model\b'],
 'PEFT (LoRA/adapters)': [r'\blora\b', r'\bqlora\b', r'\bparameter efficient\b', r'\bpeft\b', r'\bprefix tuning\b', r'\bp tuning\b', r'\badapter\w*\b', r'\bia3\b'],
 'Prompting / in-context learning': [r'\bin context learning\b', r'\bfew shot prompt\w*', r'\bprompt engineering\b', r'\bzero shot prompt\w*', r'\bprompt design\b'],
 'Chain-of-thought / decomposition': [r'\bchain of thought\b', r'\bcot\b', r'\bquestion decomposition\b', r'\bdecompos\w+'],
 'Schema linking': [r'\bschema linking\b', r'\bschema link\w*', r'\bschema selection\b', r'\bvalue linking\b'],
 'Graph neural networks': [r'\bgraph neural network\b', r'\bgnn\b', r'\brelation aware\b', r'\bgraph encoder\b'],
 'Retrieval-augmented generation': [r'\bretrieval augmented\b', r'\brag\b', r'\bvector (?:store|database)\b', r'\bembedding retrieval\b'],
 'Multi-agent / agentic': [r'\bmulti agent\b', r'\bagentic\b', r'\bagent framework\b', r'\bllm agent\b'],
 'Self-correction / refinement': [r'\bself correct\w*', r'\bself refine\w*', r'\bself debug\w*', r'\berror correction\b', r'\brefinement\b', r'\bself consistency\b'],
 'Reranking / selection': [r'\brerank\w*', r'\bcandidate selection\b', r'\bn best\b', r'\bself consistency\b'],
 'Intermediate representation': [r'\bintermediate representation\b', r'\bsketch\b', r'\bskeleton\b', r'\bnatsql\b', r'\bsemql\b'],
 'Reinforcement learning': [r'\breinforcement learning\b', r'\bppo\b', r'\bgrpo\b', r'\bdpo\b', r'\breward model\b'],
 'Data augmentation / synthesis': [r'\bdata augmentation\b', r'\bsynthetic data\b', r'\bdata synthesis\b', r'\bback translation\b', r'\bparaphras\w+'],
 'Execution-guided decoding': [r'\bexecution guided\b', r'\bexecution feedback\b', r'\bexecution based\b'],
}
METRICS = {
 'Execution accuracy': [r'\bexecution accuracy\b', r'\bexecution match\b', r'\bex accuracy\b'],
 'Exact-set match': [r'\bexact match\b', r'\bexact set match\b', r'\blogical form accuracy\b'],
 'Test-suite accuracy': [r'\btest suite\b'],
 'Valid efficiency score': [r'\bvalid efficiency score\b', r'\bves\b'],
 'Executable / validity rate': [r'\bexecutable rate\b', r'\bvalid sql\b', r'\bvalidity rate\b', r'\bsyntax(?:tic)? accuracy\b'],
 'F1 / precision / recall': [r'\bf1 score\b', r'\bprecision and recall\b'],
 'BLEU/ROUGE': [r'\bbleu\b', r'\brouge\b'],
 'Latency / cost': [r'\blatency\b', r'\binference cost\b', r'\btoken cost\b', r'\bthroughput\b'],
 'Human evaluation': [r'\bhuman evaluation\b', r'\bhuman study\b', r'\buser study\b'],
}
DOMAIN = {
 'Healthcare / clinical': [r'\belectronic health record\w*', r'\bclinical\b', r'\bhealthcare\b', r'\bmedical record\w*', r'\bmimic\b', r'\bpatient\b'],
 'Finance / banking': [r'\bfinancial\b', r'\bfinance\b', r'\bbanking\b', r'\bstock market\b'],
 'Industry / manufacturing': [r'\bmanufactur\w+', r'\bindustrial\b', r'\bproduction line\b', r'\bsupply chain\b'],
 'Energy / power': [r'\bpower grid\b', r'\bpower equipment\b', r'\benergy consumption\b', r'\bsmart grid\b'],
 'E-commerce / business intelligence': [r'\be commerce\b', r'\bbusiness intelligence\b', r'\bsales data\b', r'\benterprise data\b'],
 'Government / open data': [r'\bopen government\b', r'\bpublic administration\b', r'\bcensus\b', r'\bgovernment data\b'],
 'Education / academia': [r'\beducation\w*', r'\buniversity database\b', r'\bstudent record\w*'],
 'Telecom / networks': [r'\btelecom\w*', r'\bnetwork operator\b', r'\b5g\b'],
 'Agriculture': [r'\bagricultur\w+', r'\bcrop\b', r'\bfarming\b'],
 'Legal': [r'\blegal\b', r'\bjudicial\b', r'\blaw firm\b'],
 'Transport / mobility': [r'\btraffic\b', r'\btransportation\b', r'\bmobility\b', r'\btrajector\w+'],
}
DBMS = {
 'PostgreSQL/PostGIS': [r'\bpostgresql\b', r'\bpostgres\b', r'\bpostgis\b'],
 'MySQL': [r'\bmysql\b'], 'SQLite': [r'\bsqlite\b'], 'Oracle': [r'\boracle (?:database|db|sql|19c|autonomous|cloud|select ai)\b'],
 'SQL Server': [r'\bsql server\b'], 'Snowflake/BigQuery': [r'\bsnowflake\b', r'\bbigquery\b'],
 'ClickHouse/Spark': [r'\bclickhouse\b', r'\bspark sql\b', r'\bhive\b'],
}
REALWORLD = [r'\breal world\b', r'\bindustrial deployment\b', r'\bproduction environment\b',
  r'\bin production\b', r'\benterprise\b', r'\breal world database\w*', r'\bdeployed\b', r'\bcase study\b']

STUDY_TYPE_DATASET = [r'\bwe (?:introduce|present|propose|construct|build|release)\s+(?:a\s+)?(?:new\s+)?(?:\w+\s+){0,3}(?:dataset|benchmark|corpus)\b',
  r'\bnew benchmark\b', r'\bnovel dataset\b', r'\bwe construct a\b.{0,40}dataset']

def qa_scores(t, r):
    s = {}
    strong, weak = cnt(t, SPATIAL_STRONG), cnt(t, SPATIAL_WEAK)
    tt = norm(r['title'] + ' ' + r.get('abstract', ''))
    tspat = cnt(tt, SPATIAL_STRONG) + cnt(tt, [r'\bspatial\b', r'\bgeograph\w+', r'\bgis\b'])
    if strong >= 8 and tspat >= 1: s['QA1'] = 1.0
    elif strong >= 3 or tspat >= 1 or weak >= 12: s['QA1'] = 0.5
    else: s['QA1'] = 0.0
    obj = cnt(t, [r'\bin this (?:paper|work|study|article)\b', r'\bthis (?:paper|work|study|article) (?:aims|proposes|presents|introduces|investigates)\b',
                  r'\bwe (?:propose|present|introduce|develop|design)\b', r'\bthe (?:goal|objective|aim) of this\b',
                  r'\bour (?:goal|objective|contribution)\b', r'\bresearch question\w*'])
    s['QA2'] = 1.0 if obj >= 4 else (0.5 if obj >= 1 else 0.0)
    ds = hits(t, DATASETS)
    pub = cnt(t, [r'\bpublicly available\b', r'\bgithub com\b', r'\bhuggingface\b', r'\bopen source\b',
                  r'\bavailable at\b', r'\bwe release\b', r'\bcode is available\b'])
    if ds and pub: s['QA3'] = 1.0
    elif ds or pub: s['QA3'] = 0.5
    else: s['QA3'] = 0.0
    meth = cnt(t, [r'\bmethodolog\w+', r'\barchitecture\b', r'\balgorithm \d', r'\bwe implement\w*',
                   r'\bhyperparameter\w*', r'\bimplementation detail\w*', r'\bexperimental setup\b',
                   r'\bthe framework consists\b', r'\bmodule\b', r'\bpseudo code\b', r'\bprompt template\b'])
    s['QA4'] = 1.0 if (meth >= 6 and len(t) > 18000) else (0.5 if meth >= 2 else 0.0)
    mt = hits(t, METRICS)
    res = cnt(t, [r'\btable \d', r'\bexperimental result\w*', r'\bevaluation\b'])
    if len(mt) >= 2 and res >= 3: s['QA5'] = 1.0
    elif mt or res >= 2: s['QA5'] = 0.5
    else: s['QA5'] = 0.0
    bl = cnt(t, [r'\bbaseline\w*', r'\bcompared (?:with|to|against)\b', r'\bstate of the art\b',
                 r'\boutperform\w*', r'\bprior work\b', r'\bexisting method\w*'])
    s['QA6'] = 1.0 if bl >= 6 else (0.5 if bl >= 2 else 0.0)
    lim = cnt(t, [r'\blimitation\w*', r'\bthreats? to validity\b', r'\bwe acknowledge\b',
                  r'\bshortcoming\w*', r'\bfailure case\w*', r'\berror analysis\b'])
    fut = cnt(t, [r'\bfuture work\b', r'\bfuture research\b', r'\bfuture direction\w*'])
    if lim >= 3 or cnt(t, [r'\bthreats? to validity\b']) >= 1: s['QA7'] = 1.0
    elif lim >= 1 or fut >= 1: s['QA7'] = 0.5
    else: s['QA7'] = 0.0
    return s, strong, weak


def study_type(title, t):
    ti = title.lower()
    if any(w in ti for w in ['dataset','benchmark','corpus',' -spider','spider:']) or cnt(t[:25000], STUDY_TYPE_DATASET) >= 2:
        return 'Dataset/benchmark'
    if re.match(r'^(evaluating|an empirical|a comparative|comparative|performance evaluation|benchmarking|an? (in-depth|analysis|assessment)|analysis of|investigating|are we|how (well|do)|do llms|can llms|exploring|a survey|understanding|revisiting|on the)', ti):
        return 'Empirical study'
    if any(w in ti for w in [' system',' application',' platform','chatbot','interface','assistant','copilot','demo','deployment','industrial','in practice','pipeline for']):
        return 'Application/system'
    return 'Technique/framework'

out = []
for i, r in enumerate(acc):
    t = corpus.get(str(i))
    if t: t = strip_refs(t)
    rec = {'idx': i, 'title': r['title'], 'year': r['year'], 'source': r['source'],
           'doi': r['doi'], 'key': r['bib']['key'], 'venue': r['bib'].get('journal') or r['bib'].get('booktitle') or r['journal'],
           'author': r['bib'].get('author', r['author']), 'abstract': r.get('abstract', ''),
           'has_text': bool(t)}
    if t:
        q, strong, weak = qa_scores(t, r)
        rec.update(qa=q, qa_total=round(sum(q.values()), 1), sp_strong=strong, sp_weak=weak,
                   models=hits(t, MODELS, 3), datasets=hits(t, DATASETS, 3), langs=hits(t, LANGS, 2),
                   approaches=hits(t, APPROACH, 3), metrics=hits(t, METRICS, 2), domains=hits(t, DOMAIN, 3),
                   dbms=hits(t, DBMS, 2), realworld=cnt(t, REALWORLD),
                   proposes_dataset=cnt(t, STUDY_TYPE_DATASET), tlen=len(t),
                   study_type=study_type(r['title'], t))
    out.append(rec)
json.dump(out, open(W('extraction.json'),'w'), ensure_ascii=False)
withtext = [r for r in out if r['has_text']]
print('extracted', len(withtext))
print('QA total distribution:', collections.Counter(r['qa_total'] for r in withtext).most_common())
print('pass cutoff 3.0:', sum(1 for r in withtext if r['qa_total'] >= 3.0))
print('QA1 dist:', collections.Counter(r['qa']['QA1'] for r in withtext))
print('spatial strong>=8:', sum(1 for r in withtext if r['sp_strong'] >= 8))