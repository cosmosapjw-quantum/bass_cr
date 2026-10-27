async function dualBackup(key, archive) {
 const ROOT='/workspace/scratch/865c84d871b7';
 const q=s=>"'"+String(s).replace(/'/g,"'\\''")+"'";
 const unpack=r=>{if(r.isError)throw Error(JSON.stringify(r));if(r.structuredContent)return r.structuredContent;for(const c of r.content||[]){if(c.type==='text'){try{return JSON.parse(c.text);}catch{}}}throw Error('Cannot parse provider response');};
 async function command(cmd,max=10000){let r=await tools.exec_command({cmd,workdir:ROOT,max_output_tokens:max,yield_time_ms:1000});let out=r.output;while(r.session_id){r=await tools.write_stdin({session_id:r.session_id,chars:'',yield_time_ms:1000,max_output_tokens:max});out+=r.output;}if(r.exit_code!==0)throw Error(out);return out.trim();}
 const write=async(path,obj)=>command('python3 -c '+q('import pathlib,sys; pathlib.Path(sys.argv[1]).write_text(sys.argv[2])')+' '+q(path)+' '+q(JSON.stringify(obj,null,2)+'\n'));
 const path=ROOT+'/parent_ops/'+key+'_backup_pending.json';
 let p=JSON.parse(await command('python3 -c '+q('import pathlib,sys; p=pathlib.Path(sys.argv[1]); print(p.read_text() if p.exists() else "{}")')+' '+q(path)));
 if(p.complete)return p;
 if(!p.archive){p.archive=archive;await write(path,p);}
 if(JSON.stringify(p.archive)!==JSON.stringify(archive))throw Error('Immutable archive identity changed');
 if(!p.dropbox){p.dropbox=unpack(await tools.mcp__codex_apps__dropbox_upload_file({destination_path:'/BASS_DERIVATION_DOSSIERS_20260912/bass_cr/'+archive.name,source_file:archive.path}));await write(path,p);}
 while(p.dropbox.status==='in_progress'){
  p.dropbox=unpack(await tools.mcp__codex_apps__dropbox_check_upload_file_status({operation_id:p.dropbox.operation_id,wait_ms:Math.max(1000,Math.min(30000,p.dropbox.recommended_poll_after_ms||1000))}));await write(path,p);
 }
 if(p.dropbox.status!=='completed')throw Error('Dropbox completion missing');
 if(!p.drive){p.drive=unpack(await tools.mcp__codex_apps__google_drive_upload_file({file_uri:archive.path,file_name:archive.name,mime_type:'application/zip',parent_folder_id:'1V4ZQza59dWVC7apeRz9P1TL66eaVYyJy'}));await write(path,p);}
 p.dropbox_id=p.dropbox.file.file_id;p.drive_id=p.drive.id||p.drive.file?.id||p.drive.file_id;
 if(!p.drive_id)throw Error('Drive identity unavailable');
 if(!p.dropbox_metadata){let db=unpack(await tools.mcp__codex_apps__dropbox_download_link({entries:[p.dropbox_id]}));p.dropbox_metadata={...db.entries[0]};delete p.dropbox_metadata.download_url;await write(path,p);}
 if(!p.drive_metadata){p.drive_metadata=unpack(await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:p.drive_id,fields:'id,name,size,modifiedTime,parents'}));await write(path,p);}
 if(Number(p.dropbox_metadata.size)!==archive.bytes||Number(p.drive_metadata.size)!==archive.bytes)throw Error('Backup metadata size mismatch');
 p.complete=true;p.metadata_tier='R2';await write(path,p);return p;
}
