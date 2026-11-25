from pathlib import Path
import json, zipfile, io, platform, hashlib
from functools import lru_cache
import numpy as np, pandas as pd, sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,confusion_matrix
from features import represent,features,NAMES
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
with zipfile.ZipFile(ROOT/'training/poolc_prepared.zip') as z:
    data={s:pd.read_csv(io.BytesIO(z.read(f'poolc_prepared/{s}.csv'))) for s in ('train','validation','test')}
for a,b in [('train','validation'),('train','test'),('validation','test')]:
    for x,y in [('hash1','hash2'),('code1_group','code2_group')]:
        assert not ((set(data[a][x])|set(data[a][y])) & (set(data[b][x])|set(data[b][y])))
rep=lru_cache(maxsize=10000)(represent)
X={s:np.array([features(rep(a),rep(b)) for a,b in zip(df.code1,df.code2)]) for s,df in data.items()}; Y={s:df.similar.to_numpy() for s,df in data.items()}
assert all(np.isfinite(x).all() for x in X.values())
models={'Logistica':LogisticRegression(max_iter=1000,random_state=42), 'Bosque compacto':RandomForestClassifier(n_estimators=32,max_depth=7,min_samples_leaf=3,random_state=42,n_jobs=2,class_weight='balanced'), 'Bosque completo':RandomForestClassifier(n_estimators=100,max_depth=12,min_samples_leaf=3,random_state=42,n_jobs=2,class_weight='balanced')}
def rf_nodes(model):
    out=[]; roots=[]
    for est in model.estimators_:
        t=est.tree_; base=len(out); roots.append(base)
        for k in range(t.node_count):
            if t.children_left[k]<0:
                v=t.value[k][0]; out.append((-1,0.,0,0,float(v[1]/v.sum())))
            else: out.append((int(t.feature[k]),float(t.threshold[k]),base+int(t.children_left[k]),base+int(t.children_right[k]),0.))
    return out,roots

def scores(model,x): return x[:,1] if model is None else model.predict_proba(x)[:,1]
def threshold(y,p): return max(((float(f1_score(y,p>=t,zero_division=0)),float(t)) for t in np.linspace(.05,.95,91)),key=lambda q:(q[0],-abs(q[1]-.5)))
rows=[]; models={'Coseno bigramas':None,**models}; fitted={}
for name,model in models.items():
    if model is not None: model.fit(X['train'],Y['train'])
    val,t=threshold(Y['validation'],scores(model,X['validation'])); p=scores(model,X['test']); pred=p>=t
    nodes=rf_nodes(model)[0] if hasattr(model,'estimators_') else []
    bytes_=len(nodes)*32+len(model.estimators_)*4+8 if nodes else (len(NAMES)+2)*8 if model is not None else 8
    rows.append(dict(model=name,validation_f1=val,threshold=t,accuracy=float(accuracy_score(Y['test'],pred)),precision=float(precision_score(Y['test'],pred,zero_division=0)),recall=float(recall_score(Y['test'],pred,zero_division=0)),f1=float(f1_score(Y['test'],pred,zero_division=0)),roc_auc=float(roc_auc_score(Y['test'],p)),parameters_bytes_estimate=bytes_,nodes=len(nodes),confusion=confusion_matrix(Y['test'],pred).tolist())); fitted[name]=model
ml=rows[1:]; top=max(r['validation_f1'] for r in ml); chosen=min((r for r in ml if r['validation_f1']>=top-.02),key=lambda r:r['parameters_bytes_estimate']); name=chosen['model']; model=fitted[name]; t=chosen['threshold']
result={'selected':name,'selection':'Menor tamaño estimado entre candidatos supervisados a <= 0.02 F1 del mejor en validación','models':rows,'environment':{'python':platform.python_version(),'sklearn':sklearn.__version__,'platform':platform.platform()},'dataset_sha256':hashlib.sha256((ROOT/'training/poolc_prepared.zip').read_bytes()).hexdigest(),'features':NAMES}
(OUT/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)); pd.DataFrame(rows).to_csv(OUT/'metrics.csv',index=False)
s=f'pub const NAME: &str = {json.dumps(name,ensure_ascii=False)};\npub const THRESHOLD: f64 = {t!r};\n'
if hasattr(model,'estimators_'):
    nodes,roots=rf_nodes(model); s+='type Node = (i8,f64,u32,u32,f64);\nstatic NODES: &[Node] = &[\n'+''.join(f'({a},{b!r},{c},{d},{e!r}),\n' for a,b,c,d,e in nodes)+'];\nstatic ROOTS: &[u32] = &'+str(roots)+';\npub fn predict(x: &[f64; 11]) -> f64 { ROOTS.iter().map(|&r| { let mut i=r as usize; loop { let (f,t,l,r,p)=NODES[i]; if f<0 {break p;} i=if (x[f as usize] as f32 as f64)<=t {l as usize}else{r as usize}; }}).sum::<f64>() / ROOTS.len() as f64 }\n'
else:
    s+='const W: [f64;11] = '+repr(model.coef_[0].tolist())+';\nconst B:f64 = '+repr(float(model.intercept_[0]))+';\npub fn predict(x:&[f64;11])->f64 { let z=B+W.iter().zip(x).map(|(w,v)|w*v).sum::<f64>(); 1.0/(1.0+(-z).exp()) }\n'
(ROOT/'engine/src/model.rs').write_text(s)
with (OUT/'parity.tsv').open('w') as f:
    for a,b,x,p,y in zip(data['test'].code1,data['test'].code2,X['test'],scores(model,X['test']),Y['test']):
        f.write(a.encode().hex()+'\t'+b.encode().hex()+'\t'+','.join(map(repr,map(float,x)))+'\t'+repr(float(p))+'\t'+str(y)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
