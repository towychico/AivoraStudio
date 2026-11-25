//! Extracción léxica aproximada para código Python, sin dependencias ni ejecución de código.
mod model;
use std::{collections::{HashMap, HashSet}, hash::Hash};
pub const MAX_BYTES: usize = 64 * 1024;
pub use model::{NAME, THRESHOLD};
const KEYWORDS: &[&[u8]] = &[b"False",b"None",b"True",b"and",b"as",b"assert",b"async",b"await",b"break",b"class",b"continue",b"def",b"del",b"elif",b"else",b"except",b"finally",b"for",b"from",b"global",b"if",b"import",b"in",b"is",b"lambda",b"nonlocal",b"not",b"or",b"pass",b"raise",b"return",b"try",b"while",b"with",b"yield"];
const OPS: &[&[u8]] = &[b"**=",b"//=",b"<<=",b">>=",b"...",b"==",b"!=",b"<=",b">=",b"**",b"//",b"<<",b">>",b":=",b"->",b"+=",b"-=",b"*=",b"/=",b"%=",b"&=",b"|=",b"^=",b"@="];
fn letter(c:u8)->bool {c.is_ascii_alphabetic() || c==b'_' || c>=128}
type Tok = Vec<u8>;
struct Rep { t:Vec<Tok>, raw:Vec<Tok>, lines:Vec<Vec<Tok>>, indent:Vec<usize>, n:usize }
fn finish(line:&mut Vec<Tok>,r:&mut Rep,level:usize){ if !line.is_empty(){r.lines.push(std::mem::take(line));r.indent.push(level);} }
fn represent(s:&str)->Rep {
 let b=s.as_bytes(); let n=b.len(); let mut i=0; let mut start=true;let mut level=0;let mut line=Vec::new();
 let mut r=Rep{t:vec![],raw:vec![],lines:vec![],indent:vec![],n};
 while i<n {let c=b[i];
  if c==10 || c==13 {finish(&mut line,&mut r,level);start=true;level=0;i+=1;continue;}
  if matches!(c,32|9|12) {if start {level+=if c==9 {4}else{1};}i+=1;continue;}
  if c==35 {while i<n && b[i]!=10 && b[i]!=13 {i+=1;}continue;}
  start=false;let j=i;
  let (t,raw): (Tok,Tok)=if c==34 || c==39 {
    let triple=[c;3];let single=[c];let delim:&[u8]=if b[i..].starts_with(&triple){&triple}else{&single};i+=delim.len();
    while i<n {if b[i..].starts_with(delim){i+=delim.len();break;}if b[i]==92 {i=(i+2).min(n);}else if delim.len()==1 && matches!(b[i],10|13){break;}else{i+=1;}}
    (b"STRING".to_vec(),b"STRING".to_vec())
  }else if letter(c){i+=1;while i<n && (letter(b[i])||b[i].is_ascii_digit()){i+=1;}let raw=b[j..i].to_vec();let t=if KEYWORDS.contains(&raw.as_slice()){raw.clone()}else{b"IDENT".to_vec()};(t,raw)
  }else if c.is_ascii_digit(){i+=1;while i<n && (b[i].is_ascii_digit()||letter(b[i])||b[i]==46){i+=1;}(b"NUMBER".to_vec(),b"NUMBER".to_vec())
  }else{let len=OPS.iter().find(|op|b[i..].starts_with(op)).map_or(1,|op|op.len());i+=len;let t=b[j..i].to_vec();(t.clone(),t)};
  line.push(t.clone());r.t.push(t);r.raw.push(raw);
 }
 finish(&mut line,&mut r,level);r
}
fn counts<T:Eq+Hash>(a:impl IntoIterator<Item=T>)->HashMap<T,u64>{let mut out=HashMap::new();for v in a{*out.entry(v).or_insert(0)+=1;}out}
fn cos<T:Eq+Hash>(a:impl IntoIterator<Item=T>,b:impl IntoIterator<Item=T>)->f64{let a=counts(a);let b=counts(b);let aa=a.values().map(|v|v*v).sum::<u64>();let bb=b.values().map(|v|v*v).sum::<u64>();if aa==0||bb==0{return 0.0;}let dot=a.iter().map(|(k,v)|v*b.get(k).copied().unwrap_or(0)).sum::<u64>();dot as f64/((aa as f64)*(bb as f64)).sqrt()}
fn jac<T:Eq+Hash>(a:impl IntoIterator<Item=T>,b:impl IntoIterator<Item=T>)->f64{let a:HashSet<T>=a.into_iter().collect();let b:HashSet<T>=b.into_iter().collect();let union=a.union(&b).count();if union==0{1.0}else{a.intersection(&b).count() as f64/union as f64}}
fn diff(a:usize,b:usize)->f64{a.abs_diff(b) as f64/a.max(b).max(1) as f64}
fn features_with_lengths(a:&str,b:&str)->Result<([f64;11],usize,usize),String>{
 if a.len()>MAX_BYTES||b.len()>MAX_BYTES{return Err("Cada entrada admite hasta 64 KiB UTF-8.".into());}
 let a=represent(a);let b=represent(b);if a.t.is_empty()||b.t.is_empty(){return Err("Ambas entradas deben contener código, no solo comentarios o espacios.".into());}
 Ok(([cos(a.t.iter(),b.t.iter()),cos(a.t.windows(2),b.t.windows(2)),cos(a.t.windows(3),b.t.windows(3)),jac(a.t.iter(),b.t.iter()),jac(a.t.windows(2),b.t.windows(2)),cos(a.raw.windows(2),b.raw.windows(2)),cos(a.lines.iter(),b.lines.iter()),cos(a.indent.iter(),b.indent.iter()),diff(a.n,b.n),diff(a.t.len(),b.t.len()),diff(a.lines.len(),b.lines.len())],a.t.len(),b.t.len()))
}
pub fn features(a:&str,b:&str)->Result<[f64;11],String>{Ok(features_with_lengths(a,b)?.0)}
#[derive(Debug)] pub struct Comparison {pub similarity:f64,pub confidence:f64,pub predicted_similar:bool,pub feature_us:u128,pub inference_us:u128,pub total_us:u128}
pub fn compare(a:&str,b:&str)->Result<Comparison,String>{let start=std::time::Instant::now();let (f,na,nb)=features_with_lengths(a,b)?;let feature_us=start.elapsed().as_micros();let infer=std::time::Instant::now();let confidence=model::predict(&f);let inference_us=infer.elapsed().as_micros();
 // Definición operativa: coseno de unigramas, bigramas, trigramas y Jaccard de tokens (pesos iguales).
 // Secuencias cortas sin n-gramas en ambas entradas: omitir orden inexistente.
 let mut sum=f[0]+f[3];let mut n=2.0; if na>=2 || nb>=2{sum+=f[1];n+=1.0;} if na>=3 || nb>=3{sum+=f[2];n+=1.0;}
 Ok(Comparison{similarity:(sum/n).clamp(0.0,1.0),confidence,predicted_similar:confidence>=THRESHOLD,feature_us,inference_us,total_us:start.elapsed().as_micros()})}
pub fn predict(x:&[f64;11])->f64{model::predict(x)}
#[cfg(test)] mod tests{use super::*;#[test]fn symmetric(){let a="def x(n):\n return n+1";let b="def y(z):\n return z*2";assert_eq!(features(a,b).unwrap(),features(b,a).unwrap());}#[test]fn identical(){assert!((compare("x=1","x=1").unwrap().similarity-1.0).abs()<1e-10);}#[test]fn empty(){assert!(compare("# a","x").is_err());}#[test]fn short(){assert_eq!(compare("x","x").unwrap().similarity,1.0);}}
