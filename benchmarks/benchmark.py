"""Herramienta de desarrollo, no dependencia de la aplicación distribuida."""
import argparse,csv,io,json,os,platform,statistics,subprocess,time,pathlib,threading
P=pathlib.Path(__file__).resolve().parents[1]; ap=argparse.ArgumentParser();ap.add_argument('--binary',type=pathlib.Path,default=P/'engine/target/release'/('sovereign-engine.exe' if os.name=='nt' else 'sovereign-engine'));ap.add_argument('--app',type=pathlib.Path,help='Ejecutable Tauri, opcional; se mide tamaño, no arranque GUI');ap.add_argument('--package',type=pathlib.Path,help='Instalador o bundle');args=ap.parse_args()
binary=args.binary.resolve(); out=P/'results'; cmd=[str(binary),'bench',str(out/'parity.tsv')]; start=time.perf_counter(); proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True); peak=None; cpu=None
try:
 import psutil
 child=psutil.Process(proc.pid); peaks=[]; cpus=[]
 def sample():
  while proc.poll() is None:
   try: peaks.append(child.memory_info().rss); c=child.cpu_times();cpus.append(c.user+c.system)
   except psutil.Error: break
   time.sleep(.005)
 thread=threading.Thread(target=sample);thread.start()
except ImportError: thread=None
stdout,stderr=proc.communicate(); elapsed=time.perf_counter()-start
if thread:thread.join();peak=max(peaks,default=None);cpu=max(cpus,default=None)
(out/'native_benchmark.csv').write_text(stdout);(out/'native_parity.log').write_text(stderr)
rows=list(csv.DictReader(io.StringIO(stdout))); 
def stats(col):
 vals=sorted(float(r[col]) for r in rows); n=len(vals)
 if not n:return None
 return {'mean':statistics.mean(vals),'median':statistics.median(vals),'p95':vals[max(0,__import__('math').ceil(n*.95)-1)],'p99':vals[max(0,__import__('math').ceil(n*.99)-1)]}
def size(p):return (p.stat().st_size if p.is_file() else sum(f.stat().st_size for f in p.rglob('*') if f.is_file() and not f.is_symlink())) if p else None
# Inicio CLI de extremo a extremo, no tiempo de lanzamiento de la ventana.
import tempfile
with tempfile.TemporaryDirectory() as td:
 a=pathlib.Path(td)/'a.py';b=pathlib.Path(td)/'b.py';a.write_text('x=1');b.write_text('y=2');cold=[]
 for _ in range(10):
  t=time.perf_counter();subprocess.run([str(binary),'compare',str(a),str(b)],check=True,capture_output=True);cold.append((time.perf_counter()-t)*1000)
report={'platform':platform.platform(),'cpu':platform.processor(),'machine':platform.machine(),'pairs':len(rows),'parity_pass':proc.returncode==0,'cli_binary_bytes':size(binary),'tauri_binary_bytes':size(args.app),'package_bytes':size(args.package),'model_parameters_estimate_bytes':104,'peak_cli_rss_sampled_bytes':peak,'cli_cpu_sampled_seconds':cpu,'batch_wall_seconds':elapsed,'cli_launch_and_compare_ms_median':statistics.median(cold),'feature_us':stats('feature_us'),'inference_us':stats('inference_us'),'total_us':stats('total_us'),'gui_startup_ms':None,'offline_gui_verified':False}
(out/'native_benchmark.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));raise SystemExit(proc.returncode)
