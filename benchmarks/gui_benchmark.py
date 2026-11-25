"""Compare two release builds on the same machine. Development-only; no telemetry."""
import argparse,csv,json,os,platform,statistics,subprocess,tempfile,time
from pathlib import Path
import psutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--monaco',type=Path,required=True);p.add_argument('--textarea',type=Path,required=True);p.add_argument('--runs',type=int,default=5);p.add_argument('--timeout',type=float,default=60);p.add_argument('--settle',type=float,default=2);a=p.parse_args()
if a.runs<1 or a.timeout<=0 or a.settle<0:p.error('Invalid timing options')
rows=[]
for i in range(a.runs):
 for variant in (('textarea','monaco') if i%2==0 else ('monaco','textarea')):
  exe=getattr(a,variant).resolve()
  with tempfile.TemporaryDirectory() as td:
   marker=Path(td)/'ready';env=dict(os.environ,AIVORA_BENCH_READY=str(marker));start=time.perf_counter();proc=subprocess.Popen([str(exe)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);ps=psutil.Process(proc.pid);peak=0;cpu=0.;ready=None;seen={};status='timeout'
   try:
    while proc.poll() is None and time.perf_counter()-start<a.timeout:
     try:
      rss=0
      for q in [ps]+ps.children(recursive=True):
       try:
        rss+=q.memory_info().rss;c=q.cpu_times();seen[q.pid]=c.user+c.system
       except psutil.Error:pass
      peak=max(peak,rss);cpu=sum(seen.values())
     except psutil.Error:pass
     if marker.exists() and ready is None:
      got=marker.read_text().strip()
      if got==variant:ready=time.perf_counter();status='ok'
      elif got:status='variant_mismatch';break
     if ready and time.perf_counter()-ready>=a.settle:break
     time.sleep(.02)
    if proc.poll() is not None:status='early_exit'
   finally:
    try:children=ps.children(recursive=True)
    except psutil.Error:children=[]
    for q in reversed(children):
     try:q.terminate()
     except psutil.Error:pass
    if proc.poll() is None:
     proc.terminate()
     try:proc.wait(5)
     except subprocess.TimeoutExpired:proc.kill();proc.wait()
   rows.append(dict(variant=variant,run=i+1,status=status,ready_ms=round((ready-start)*1000,3) if ready else None,peak_sampled_tree_rss_bytes=peak,tree_cpu_seconds=cpu,binary_bytes=exe.stat().st_size));print(rows[-1],flush=True)
summary={}
for variant in ('textarea','monaco'):
 good=[r for r in rows if r['variant']==variant and r['status']=='ok'];summary[variant]={'valid_runs':len(good),'median_ready_ms':statistics.median(r['ready_ms'] for r in good) if good else None,'median_peak_sampled_tree_rss_bytes':statistics.median(r['peak_sampled_tree_rss_bytes'] for r in good) if good else None,'median_tree_cpu_seconds':statistics.median(r['tree_cpu_seconds'] for r in good) if good else None,'binary_bytes':getattr(a,variant).stat().st_size}
out=ROOT/'results';out.mkdir(exist_ok=True)
with (out/'gui_benchmark.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'gui_benchmark.json').write_text(json.dumps({'platform':platform.platform(),'machine':platform.machine(),'sample_interval_ms':20,'settle_s':a.settle,'summary':summary,'runs':rows,'limits':'Process tree only; shared WebView helpers can be missed. Repeated launches may be warm. No offline verification.'},indent=2));raise SystemExit(0 if all(r['status']=='ok' for r in rows) else 1)
