// Run from repository root: node benchmarks/build_variants.mjs
import {spawnSync} from 'node:child_process';
import {mkdirSync,copyFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
const win=process.platform==='win32';
for(const variant of ['textarea','monaco']){
 const target=resolve('benchmark-builds',variant);mkdirSync(target,{recursive:true});
 const args=['run','tauri','build','--','--no-bundle',...(variant==='textarea'?['--config','src-tauri/tauri.textarea.conf.json']:[])];
 const result=spawnSync(win?'npm.cmd':'npm',args,{stdio:'inherit',shell:win,env:{...process.env,CARGO_TARGET_DIR:target}});
 if(result.status!==0)process.exit(result.status??1);
 const exe=resolve(target,'release',`python-similarity-detector${win?'.exe':''}`);if(!existsSync(exe))throw new Error(`No binary at ${exe}`);
 console.log(`${variant}: ${exe}`);
}
