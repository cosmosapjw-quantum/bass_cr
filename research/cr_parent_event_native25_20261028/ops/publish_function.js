async function publishStage(stage,purpose,files,basis=['derived'],binaryBlobs={}) {
 const ROOT='/workspace/scratch/865c84d871b7', UNIT=ROOT+'/bass_cr/research/cr_parent_event_native25_20261028';
 const q=s=>"'"+String(s).replace(/'/g,"'\\''")+"'";
 const unpack=r=>{if(r.isError)throw Error(JSON.stringify(r));if(r.structuredContent)return r.structuredContent;for(const c of r.content||[]){if(c.type==='text'){try{return JSON.parse(c.text);}catch{}}}throw Error('Unparsed tool response: '+JSON.stringify(r));};
 async function command(cmd,network=false,max=100000){let r=await tools.exec_command({cmd,workdir:ROOT,max_output_tokens:max,yield_time_ms:1000,...(network?{sandbox_permissions:'require_escalated',justification:'Continue authorized expected-SHA research publication and verify remote branch.'}:{})});let out=r.output;while(r.session_id){r=await tools.write_stdin({session_id:r.session_id,chars:'',yield_time_ms:1000,max_output_tokens:max});out+=r.output;}if(r.exit_code!==0)throw Error(out);return out.trim();}
 const read=async path=>JSON.parse(await command('cat '+q(path)));
 const write=async(path,obj)=>command('python3 -c '+q('import pathlib,sys; pathlib.Path(sys.argv[1]).write_text(sys.argv[2])')+' '+q(path)+' '+q(JSON.stringify(obj,null,2)+'\n'));
 const state=await read(ROOT+'/parent_ops/pub_state.json'), pendingPath=ROOT+'/parent_ops/'+stage+'_pending.json';
 let p=JSON.parse(await command('python3 -c '+q('import pathlib,sys; p=pathlib.Path(sys.argv[1]); print(p.read_text() if p.exists() else "{}")')+' '+q(pendingPath)));
 if(p.complete)return p.receipt;
 if(!p.tree){
  if(!p.prepared){
   const input={cmd:'prepare',stage,purpose,files,expected_head:state.head,basis,binary_blobs:binaryBlobs,response_file:ROOT+'/parent_ops/'+stage+'_prepared.json'};
   p.prepared=JSON.parse(await command('python3 parent_ops/stage.py <<\'STAGE_INPUT\'\n'+JSON.stringify(input)+'\nSTAGE_INPUT'));p.parent=state.head;p.next_chunk=0;p.partial_tree=p.prepared.base_tree;await write(pendingPath,p);
  }
  while(p.next_chunk<p.prepared.chunk_count){
   const elements=JSON.parse(await command('python3 -c '+q('import pathlib,json,sys; print(json.dumps(json.loads(pathlib.Path(sys.argv[1]).read_text())["chunks"][int(sys.argv[2])]))')+' '+q(p.prepared.response_file)+' '+p.next_chunk));
   const tr=unpack(await tools.mcp__codex_apps__github_create_tree({repository_full_name:state.repo,base_tree_sha:p.partial_tree,tree_elements:elements}));p.partial_tree=tr.sha;p.next_chunk++;await write(pendingPath,p);
  }
  p.tree=p.partial_tree;await write(pendingPath,p);
 }
 if(!p.commit){const cr=unpack(await tools.mcp__codex_apps__github_create_commit({repository_full_name:state.repo,message:stage+': '+purpose,parent_sha:p.parent,tree_sha:p.tree}));p.commit=cr.sha;await write(pendingPath,p);}
 if(!p.ref){p.ref=unpack(await tools.mcp__codex_apps__github_update_ref({repository_full_name:state.repo,branch_name:state.branch,expected_sha:p.parent,sha:p.commit,force:false}));await write(pendingPath,p);}
 if(!p.git_readback){
  const py='import subprocess; r="'+ROOT+'/bass_cr"; b="'+state.branch+'"; s="'+p.commit+'"; subprocess.run(["git","fetch","--depth=1","origin",b],cwd=r,check=True,stdout=subprocess.DEVNULL); subprocess.run(["git","reset","--mixed",s],cwd=r,check=True,stdout=subprocess.DEVNULL); h=subprocess.run(["git","ls-remote","origin","refs/heads/"+b],cwd=r,check=True,capture_output=True,text=True).stdout.split()[0]; assert h==s,(h,s); print(h)';
  const rb=await command('python3 -c '+q(py),true,2000);p.git_readback=rb.endsWith(p.commit);if(!p.git_readback)throw Error(rb);await write(pendingPath,p);
 }
 if(!p.archive){p.archive=JSON.parse(await command('python3 parent_ops/stage.py <<\'STAGE_INPUT\'\n'+JSON.stringify({cmd:'package',stage,commit:p.commit,parent:p.parent})+'\nSTAGE_INPUT'));await write(pendingPath,p);}
 if(!p.dropbox){p.dropbox=unpack(await tools.mcp__codex_apps__dropbox_upload_file({destination_path:'/BASS_DERIVATION_DOSSIERS_20260912/bass_cr/'+p.archive.name,source_file:p.archive.path}));await write(pendingPath,p);}
 while(p.dropbox.status==='in_progress'){
  p.dropbox=unpack(await tools.mcp__codex_apps__dropbox_check_upload_file_status({operation_id:p.dropbox.operation_id,wait_ms:Math.max(1000,Math.min(30000,p.dropbox.recommended_poll_after_ms||1000))}));await write(pendingPath,p);
 }
 if(p.dropbox.status!=='completed')throw Error('Dropbox not complete '+JSON.stringify(p.dropbox));
 if(!p.drive){p.drive=unpack(await tools.mcp__codex_apps__google_drive_upload_file({file_uri:p.archive.path,file_name:p.archive.name,mime_type:'application/zip',parent_folder_id:'1V4ZQza59dWVC7apeRz9P1TL66eaVYyJy'}));await write(pendingPath,p);}
 const dbid=p.dropbox.file.file_id, dvid=p.drive.id||p.drive.file?.id||p.drive.file_id;
 if(!dvid)throw Error('Need Drive upload schema '+JSON.stringify(p.drive));
 if(!p.dbmeta){const dr=unpack(await tools.mcp__codex_apps__dropbox_download_link({entries:[dbid]}));p.dbmeta={...dr.entries[0]};delete p.dbmeta.download_url;await write(pendingPath,p);}
 if(!p.dvmeta){p.dvmeta=unpack(await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:dvid,fields:'id,name,size,modifiedTime,parents'}));await write(pendingPath,p);}
 if(Number(p.dbmeta.size)!==p.archive.bytes||Number(p.dvmeta.size)!==p.archive.bytes)throw Error('R2 size mismatch');
 const ordinal=(stage[0]==='C'?10:0)+Number(stage.slice(1));
 const preflight=await read(UNIT+'/intake/preflight/'+stage+'.json');
 const receipt={schema:'CR_PARENT_EVENT_STAGE_PUBLICATION_V1',stage,commit:p.commit,tree:p.tree,expected_parent:p.parent,force:false,Git_ref_readback:p.git_readback,archive:p.archive,Dropbox:{id:dbid,ack:true,bytes:Number(p.dbmeta.size),metadata:p.dbmeta,tier:'R2'},Drive:{id:dvid,ack:true,bytes:Number(p.dvmeta.size),metadata:p.dvmeta,tier:'R2'},central_completed:preflight.central_completed,central_total:preflight.central_total,completed_loop_stage:ordinal,total_loop_stages:20,raw_archive_readback:false};
 await write(UNIT+'/publication/'+stage+'_RECEIPT.json',receipt);
 state.head=p.commit;state.tree=p.tree;state.stages=state.stages.filter(x=>x.stage!==stage);state.stages.push(receipt);await write(ROOT+'/parent_ops/pub_state.json',state);
 p.complete=true;p.receipt=receipt;await write(pendingPath,p);
 await write(ROOT+'/parent_ops/CONTINUATION_STATE.json',{unit:'CR_PHYS02_PARENT_EVENT_NATIVE25_V1',unit_path:UNIT,branch:state.branch,head:state.head,last_complete_stage:stage,stages_published:state.stages.length,central:receipt.central_completed+'/'+receipt.central_total,fresh_CPU_cap_s:40,auto_next_node:false,scientific_execution_state:'read actual budget ledger and runs; stage count is not scientific completion'});
 return receipt;
}
