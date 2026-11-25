"""Mide la referencia Python del modelo logístico exportado, no Rust ni GUI."""
import sys, pathlib, time, json, csv, statistics, math, re, platform
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'training'))
from features import represent, features
s=(P/'engine/src/model.rs').read_text();w=json.loads(re.search(r'const W: \[f64;11\] = (\[.*?\]);',s).group(1));b=float(re.search(r'const B:f64 = (.*?);',s).group(1))
rows=[]
for i,line in enumerate((P/'results/parity.tsv').read_text().splitlines()):
 a,c,x,p,y=line.split('\t');a=bytes.fromhex(a).decode();c=bytes.fromhex(c).decode();t=time.perf_counter_ns();f=features(represent(a),represent(c));t2=time.perf_counter_ns();z=b+sum(v*k for v,k in zip(f,w));pred=1/(1+math.exp(-z));t3=time.perf_counter_ns();rows.append(dict(index=i,feature_us=(t2-t)/1000,inference_us=(t3-t2)/1000,total_us=(t3-t)/1000,error=abs(pred-float(p))))
with (P/'results/python_reference_benchmark.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
def stats(k):
 x=sorted(r[k] for r in rows);return dict(mean=statistics.mean(x),median=statistics.median(x),p95=x[math.ceil(.95*len(x))-1],p99=x[math.ceil(.99*len(x))-1])
result=dict(environment=platform.platform(),python=platform.python_version(),pairs=len(rows),max_probability_error=max(r['error'] for r in rows),**{k:stats(k) for k in ['feature_us','inference_us','total_us']});(P/'results/python_reference_benchmark.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
