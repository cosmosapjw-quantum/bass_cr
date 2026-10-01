#!/usr/bin/env python3
"""Append validated supplied PDFs to a frozen BASS_CR archive; no network or science execution."""
import argparse, csv, hashlib, json, re, shutil, sqlite3, unicodedata, zipfile
from datetime import datetime, timezone
from pathlib import Path
import fitz

TARGETS = {
 'Toshima1999': ('PhysRevA.59.1981.pdf', 7, 'convergence and completeness of the pseudostate expansion', 'Toshima'),
 'RungeMicha1996': ('PhysRevA.53.1388.pdf', 12, 'time dependent approach to slow ion atom collisions', 'Runge'),
 'Dollard1964': ('dollard1964.pdf', 11, 'asymptotic convergence and the Coulomb interaction', 'Dollard'),
 'Enss1979': ('1-s2.0-0003491679902525-main.pdf', 16, 'asymptotic completeness for quantum mechanical potential scattering', 'Enss'),
 'Kato1976': ('kato1995.pdf', 643, 'perturbation theory for linear operators', 'Kato'),
 'Stewart2011': ('stewart2011.pdf', 40, 'on the numerical analysis of oblique projectors', 'Stewart'),
 'Stewart1972': ('stewart1972.pdf', 18, 'on the sensitivity of the eigenvalue problem', 'Stewart'),
 'Mathias1997': ('mathias1997.pdf', 7, 'a bound for the matrix square root', 'Mathias'),
 'Antonio2024': ('PhysRevA.110.062810.pdf', 6, 'connecting excitation and ionization cross sections', 'Antonio'),
 'Yafaev2000': ('yafaev2000.pdf', 185, 'scattering theory some old and new problems', 'Yafaev'),
 'KuangLin1996': ('Jiyun_Kuang_1996_J._Phys._B__At._Mol._Opt._Phys._29_5443.pdf', 16, 'comprehensive convergence study of TCAO close coupling method', 'Kuang'),
 'Errea1998': ('L_F_Errea_1998_J._Phys._B__At._Mol._Opt._Phys._31_3199.pdf', 17, 'convergent molecular close coupling calculations', 'Errea'),
 'DickinsonMcCarroll1983': ('A_S_Dickinson_1983_J._Phys._B__Atom._Mol._Phys._16_459.pdf', 9, 'adiabatic switching factors in slow atomic collisions', 'Dickinson'),
 'Kunikeev1999': ('1-s2.0-S0168583X99000130-main.pdf', 7, 'asymptotic expansions for three body continuum and bound states', 'Kunikeev'),
}
SUPPLEMENTS = [
 {'supplement_id':'EsryEtAl1993','name':'B_D_Esry_1993_J._Phys._B__At._Mol._Opt._Phys._26_1579.pdf','doi':'10.1088/0953-4075/26/9/006','title':'Close-coupling calculations of electron capture cross sections from the n=2 states of H by protons and alpha particles','authors':'B. D. Esry; Z. Chen; C. D. Lin; R. D. Piacentini','bib_author':'Esry, B. D. and Chen, Z. and Lin, C. D. and Piacentini, R. D.','year':1993,'journal':'Journal of Physics B: Atomic, Molecular and Optical Physics','volume':'26','pages':'1579-1586'},
 {'supplement_id':'AguenyEtAl2019','name':'1-s2.0-S0092640X19300191-main.pdf','doi':'10.1016/j.adt.2019.05.002','title':'Electron capture, ionization and excitation cross sections for keV collisions between fully stripped ions and atomic hydrogen in ground and excited states','authors':'Hicham Agueny; Jan Petter Hansen; Alain Dubois; Abdelkader Makhoute; Abdelmalek Taoutioui; Nicolas Sisourat','bib_author':'Agueny, Hicham and Hansen, Jan Petter and Dubois, Alain and Makhoute, Abdelkader and Taoutioui, Abdelmalek and Sisourat, Nicolas','year':2019,'journal':'Atomic Data and Nuclear Data Tables','volume':'129-130','pages':'101281'},
 {'supplement_id':'ShahGilbody1978','name':'M_B_Shah_1978_J._Phys._B__Atom._Mol._Phys._11_121.pdf','doi':'10.1088/0022-3700/11/1/016','title':'Electron capture and He+(2s) formation in fast He2+-H and He+-H collisions','authors':'M. B. Shah; H. B. Gilbody','bib_author':'Shah, M. B. and Gilbody, H. B.','year':1978,'journal':'Journal of Physics B: Atomic and Molecular Physics','volume':'11','pages':'121-131'},
 {'supplement_id':'PieksmaOvchinnikov1992','name':'M_Pieksma_1992_J._Phys._B__At._Mol._Opt._Phys._25_L373.pdf','doi':'10.1088/0953-4075/25/15/005','title':'Asymptotic dependence of the electron capture cross section on the n quantum number in slow He2+-H collisions','authors':'Marc Pieksma; S. Yu. Ovchinnikov','bib_author':'Pieksma, Marc and Ovchinnikov, S. Yu.','year':1992,'journal':'Journal of Physics B: Atomic, Molecular and Optical Physics','volume':'25','pages':'L373-L380'},
]

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def write_json(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).casefold())
def insert(c,t,x):
 c.execute('INSERT INTO '+t+' ('+','.join(x)+') VALUES ('+','.join('?' for _ in x)+')',list(x.values()))
def bib_chunks(s):
 out={}
 for m in re.finditer(r'@\w+\s*\{([^,]+),',s):
  begin=m.start();start=s.index('{',begin);depth=0;i=start
  while i<len(s):
   if s[i]=='{' and (i==0 or s[i-1]!='\\'):depth+=1
   elif s[i]=='}' and (i==0 or s[i-1]!='\\'):
    depth-=1
    if depth==0:break
   i+=1
  if depth:raise ValueError('Unclosed BibTeX entry '+m.group(1))
  out[m.group(1)]=s[begin:i+1]
 return out

def build(base):
 root=base/'user_import_v3';pkg=root/'package';v=pkg/'v3';deliver=root/'deliverables'
 if any(pkg.iterdir()):raise RuntimeError('Generated package already exists; resume from state, do not rebuild silently')
 original=base/'recovery_v2/restored';prior=base/'recovery_v2/deliverables'
 frozen=prior/'BASS_CR_LITERATURE_FULLTEXT_RECOVERY_20261001_v2.zip'
 if sha(frozen)!='94a6a0627b4ea40bd5c31e902c6c5942401dbc112253056e35d172f4db78b8d2':raise ValueError('Frozen v2 archive identity changed')
 shutil.copytree(original,pkg,dirs_exist_ok=True)
 v.mkdir();(v/'user_uploads/paper').mkdir(parents=True);(v/'evidence').mkdir();(v/'scripts').mkdir();(v/'provenance/prior_v2_delivery').mkdir(parents=True)
 for p in prior.iterdir():
  if p.suffix!='.zip' and p.name not in {f.name for f in (original/'v2').iterdir() if f.is_file()}:
   shutil.copy2(p,v/'provenance/prior_v2_delivery'/p.name)
 for p in (root/'evidence').iterdir():
  if p.is_file():shutil.copy2(p,v/'evidence'/p.name)
 shutil.copy2(Path(__file__),v/'scripts'/Path(__file__).name)
 utc=datetime.now(timezone.utc).isoformat()
 auth=json.loads((root/'evidence/INPUT_AUTHORITY.json').read_text())
 inspections=json.loads((root/'evidence/PDF_INSPECTION.json').read_text());by_name={Path(x['member']).name:x for x in inspections}
 db=v/'BASS_CR_SOURCE_DATABASE_20261001_v3.sqlite';shutil.copy2(prior/'BASS_CR_SOURCE_DATABASE_20261001_v2.sqlite',db)
 c=sqlite3.connect(db);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON')
 works={x['work_id']:dict(x) for x in c.execute('SELECT * FROM works')}
 missing={k for k,x in works.items() if x['fulltext_status'] in ['NOT_ACQUIRED_FINAL','FULL_BOOK_NOT_PUBLICLY_ACQUIRED']}
 if missing!=set(TARGETS):raise ValueError('The actual missing14 set differs from import target map')
 c.execute('CREATE TABLE supplemental_uploads(supplement_id TEXT PRIMARY KEY,title TEXT NOT NULL,authors TEXT,doi TEXT,publication_year INTEGER,relative_path TEXT NOT NULL REFERENCES files(relative_path),identity_status TEXT NOT NULL,complete_fulltext INTEGER NOT NULL,notes TEXT)')
 c.execute('CREATE TABLE file_relations(from_relative_path TEXT NOT NULL REFERENCES files(relative_path),to_relative_path TEXT NOT NULL REFERENCES files(relative_path),relationship TEXT NOT NULL,evidence TEXT NOT NULL,PRIMARY KEY(from_relative_path,to_relative_path,relationship))')
 decisions=[]
 for wid,(name,pages,title_anchor,author_anchor) in TARGETS.items():
  x=by_name[name];w=works[wid];text=norm(x['first_text']+' '+x['metadata'].get('title',''))
  if x['pages']!=pages or norm(title_anchor) not in text or norm(author_anchor) not in text:raise ValueError('Target identity failed: '+wid)
  year=1995 if wid=='Kato1976' else w['publication_year']
  if str(year) not in x['first_text'] and str(year) not in str(x['metadata']):raise ValueError('Publication year not observed: '+wid)
  vid=wid+':user-upload-20261001'
  status='BOOK_REPRINT_VERIFIED' if wid=='Kato1976' else 'BOOK_EDITION_VERIFIED' if wid=='Yafaev2000' else 'EXACT_VERSION_VERIFIED'
  cl='BOOK_REPRINT' if wid=='Kato1976' else 'BOOK_EDITION' if wid=='Yafaev2000' else 'EXACT_PUBLISHER_FULLTEXT'
  vt='PUBLISHER_BOOK_REPRINT_SCAN' if wid=='Kato1976' else 'PUBLISHER_BOOK_EDITION_SCAN' if wid=='Yafaev2000' else 'PUBLISHED_VERSION_OF_RECORD'
  reason='User-supplied publisher-formatted cited article; title/authors/year/DOI or PII/journal-range agree; signature, all-page parsing and physical extent checked. Not a claim of identical publisher-server bytes or latest Crossmark status.'
  material='SAME_CITED_PUBLISHED_VERSION_IDENTITY;LATEST_UPDATES_NOT_RECHECKED'
  target_version=w['cited_version_id']
  if wid=='Kato1976':
   reason='User-supplied1995 reprint of1980 corrected second edition; explicit DOI/copyright/edition leaves; complete internal front matter and printed scholarly folios1–619, plus publisher end matter, physical643 pages. All619 body slots present; eight OCR folio-boundary exceptions visually checked. Publisher metadataXXI623 and chapter locator offsets are disclosed; no missing scholarly section identified. Cited1976 anchor remains separate.'
   material='REPRINT_OF_CORRECTED_1980_PRINTING;1976_VS_1980_CORRECTIONS_NOT_REASSESSED;PUBLISHER_EBOOK_BYTE_EQUIVALENCE_NOT_ASSESSED'
   target_version='Kato1976:reprint1995'
  if wid=='Yafaev2000':
   reason='User-supplied LNM1735 book2000, ISBN3-540-67587-6; physical185 pages. Complete scholarly folios1–153 and155–169, front matter throughxvi; official publisher chapter17 ends153 and back matter is155–169. Folio154 is not a missing listed chapter page. Bibliography/index reach169. Publisher catalogXVI176 is retained as distinct metadata; not substituted by ICM1998 article.'
   material='CITED_2000_BOOK_IDENTITY_VERIFIED;2007_EBOOK_BYTE_EQUIVALENCE_NOT_ASSESSED'
  insert(c,'versions',{'version_id':vid,'work_id':wid,'title':w['title'],'authors':w['authors'],'doi':w['doi'],'arxiv':w['arxiv'],'publication_year':year,'version_type':vt,'version_label':('1995 reprint of1980 corrected second edition, supplied scan' if wid=='Kato1976' else '2000 LNM1735 book, supplied scan' if wid=='Yafaev2000' else 'Cited journal publisher-formatted version supplied by user'),'identity_status':status,'complete_fulltext':1,'cited_version':0,'latest_selection_reason':reason,'material_change_status':material,'notes':'Acquisition provenance USER_UPLOAD; private archive; scientific content not evaluated.'})
  c.execute('UPDATE works SET fulltext_status=?,version_class=?,fulltext_format=?,selected_version_id=?,latest_version=?,selection_reason=?,material_change_status=?,manual_access=?,notes=? WHERE work_id=?',(status,cl,'PDF',vid,'User-supplied selected manifestation; newest publisher revision not rechecked',reason,material,'Complete selected fulltext now supplied; prior route failures remain historical','V2 historical: '+w['notes']+' V3 current: '+reason,wid))
  insert(c,'relations',{'from_work_id':wid,'to_work_id':wid,'from_version_id':vid,'to_version_id':target_version,'relationship':'COPY_OF','material_change_status':material,'evidence':'USER_UPLOAD; title/author/year/DOI-PII/extent and version leaves: '+name})
  if wid in ['Kato1976','Yafaev2000']:
   insert(c,'relations',{'from_work_id':wid,'to_work_id':wid,'from_version_id':vid,'to_version_id':wid+':frontmatter','relationship':'EXTENDS_PARTIAL_COPY','material_change_status':'COMPLETE_SCHOLARLY_CONTENT_ACQUIRED','evidence':'Full supplied body, bibliography and indexes; old front matter retained unchanged.'})
  decisions.append({'work_id':wid,'member':x['member'],'version_id':vid,'status':status,'version_class':cl,'version_type':vt,'title':w['title'],'authors':w['authors'],'doi':w['doi'],'year':year,'page_count':pages,'sha256':x['sha256'],'bytes':x['bytes'],'reason':reason,'material_change_status':material,'role':'TARGET','complete_fulltext':True})
 target_by_name={Path(x['member']).name:x for x in decisions};supp_by_name={x['name']:x for x in SUPPLEMENTS};catalog=[]
 for x in inspections:
  name=Path(x['member']).name;relative='v3/user_uploads/'+x['member'];dest=pkg/relative;shutil.copy2(Path(x['path']),dest)
  if sha(dest)!=x['sha256'] or dest.stat().st_size!=x['bytes']:raise ValueError('Supplied PDF bytes changed: '+name)
  primary=target_by_name.get(name);duplicate=name=='BFb0105531.pdf'
  if duplicate:
   primary=target_by_name['yafaev2000.pdf']
   if x['sha256']!=primary['sha256']:raise ValueError('Yafaev duplicate alias hash differs')
  sup=supp_by_name.get(name)
  if not primary and not sup:raise ValueError('Unclassified uploaded file '+name)
  if sup:
   d=fitz.open(dest);uris={q.get('uri','') for pg in d for q in pg.get_links()};d.close()
   if not any(sup['doi'] in u for u in uris):raise ValueError('Supplement DOI not bound to PDF annotation: '+name)
  meta=primary or sup
  role='DUPLICATE_ALIAS' if duplicate else 'TARGET' if primary else 'SUPPLEMENTAL_UPLOAD'
  wid=primary['work_id'] if primary else None;vid=primary['version_id'] if primary else None
  note='Supplied unchanged; license/redistribution not inferred. '+('Byte-identical duplicate of yafaev2000.pdf; not an additional work.' if duplicate else 'Supplemental register, excluded from original31 target count.' if sup else meta['reason'])
  insert(c,'files',{'relative_path':relative,'sha256':x['sha256'],'bytes':x['bytes'],'mime_type':'application/pdf','source_id':wid,'work_id':wid,'version_id':vid,'title':meta['title'],'authors':meta['authors'],'doi':meta['doi'],'publication_year':meta['year'],'version_type':meta.get('version_type','PUBLISHED_SUPPLEMENTAL_USER_UPLOAD'),'source_url':'attachment:'+auth['upload_name']+'#'+x['member'],'access_route':'USER_UPLOAD','local_path':relative,'page_count':x['pages'],'identity_status':meta.get('status','SUPPLEMENTAL_IDENTITY_VERIFIED'),'license_status':'USER_PROVIDED_COPYRIGHT_RETAINED_REDISTRIBUTION_NOT_ASSESSED','acquired_utc':utc,'supersedes_or_relation':'DUPLICATE_BYTE_IDENTICAL' if duplicate else 'EXTENDS_PREVIOUS_RECOVERY','notes':note})
  record={'member':x['member'],'role':role,'work_id':wid,'supplement_id':sup['supplement_id'] if sup else None,'version_id':vid,'relative_path':relative,'title':meta['title'],'authors':meta['authors'],'doi':meta['doi'],'publication_year':meta['year'],'pages':x['pages'],'bytes':x['bytes'],'sha256':x['sha256'],'identity_status':meta.get('status','SUPPLEMENTAL_IDENTITY_VERIFIED'),'complete_fulltext':True,'acquisition_provenance':'USER_UPLOAD','notes':note}
  catalog.append(record)
  insert(c,'acquisition_attempts',{'work_id':wid,'batch':'V3_USER_UPLOAD_20261001','source_url':'attachment:'+auth['upload_name']+'#'+x['member'],'access_route':'USER_UPLOAD','kind':'supplied_pdf_import','status':'IMPORTED_USER_UPLOAD','started_utc':utc,'completed_utc':utc,'local_path':relative,'sha256':x['sha256'],'bytes':x['bytes'],'notes':note,'record_json':json.dumps(record,ensure_ascii=False)})
  if sup:insert(c,'supplemental_uploads',{'supplement_id':sup['supplement_id'],'title':sup['title'],'authors':sup['authors'],'doi':sup['doi'],'publication_year':sup['year'],'relative_path':relative,'identity_status':'SUPPLEMENTAL_IDENTITY_VERIFIED','complete_fulltext':1,'notes':note})
  if duplicate:insert(c,'file_relations',{'from_relative_path':relative,'to_relative_path':'v3/user_uploads/paper/yafaev2000.pdf','relationship':'DUPLICATE_BYTE_IDENTICAL','evidence':'Both supplied names have identical SHA256474cc0c5e0c4929ab654661652bea9400fb9523399e957a5de7d318fbb6ca7d7.'})
 insert(c,'provenance',{'provenance_id':'V3_USER_UPLOAD','entity_type':'artifact','entity_id':auth['upload_name'],'source_url':'attachment:'+auth['upload_name'],'sha256':auth['upload_sha256'],'acquired_utc':utc,'origin':'USER_PROVIDED_ATTACHMENT','notes':'19 members:14 unique target works,4 supplemental works,1 duplicate alias; no network acquisition.','record_json':json.dumps(auth,ensure_ascii=False)})
 insert(c,'provenance',{'provenance_id':'V3_BASE_V2_ARCHIVE','entity_type':'artifact','entity_id':frozen.name,'sha256':sha(frozen),'origin':'FROZEN_V2_REUSED','notes':'All1177 frozen v2 archive members preserved at their original paths.','record_json':json.dumps({'bytes':frozen.stat().st_size,'sha256':sha(frozen)})})
 current={x['work_id']:dict(x) for x in c.execute('SELECT * FROM works')}
 summary={'target_works':31,'prior_complete_fulltext':17,'new_user_supplied_target_fulltexts':14,'new_user_supplied_target_articles':12,'new_user_supplied_target_books':2,'complete_target_fulltexts':31,'complete_target_PDF_works':30,'complete_target_HTML_chapters':1,'target_not_acquired':0,'uploaded_PDF_files':19,'uploaded_unique_PDF_hashes':18,'duplicate_upload_aliases':1,'supplemental_upload_works':4,'target_plus_supplemental_complete_works':35,'target_version_classes':{'EXACT_PUBLISHER_FULLTEXT':15,'BOOK_REPRINT':1,'BOOK_EDITION':1,'AUTHORITATIVE_PREPRINT':9,'INSTITUTIONAL_COPY':5,'ACCEPTED_MANUSCRIPT':0},'previous_route_attempts_retained':704,'new_user_import_records':19,'total_attempt_records':723,'failed_attempts_retained':98,'pinned_code_projects':4,'literature_source_downloads':0,'code_source_downloads':0,'scientific_calculations':0,'native_authorization_consumption':0,'claim_ceilings':'UNCHANGED','capture':False,'production':'HOLD','all_bound':'OPEN','b_grid':'NO_GO'}
 write_json(v/'BASS_CR_USER_UPLOAD_INTEGRATION_CATALOG_20261001_v3.json',{'input_authority':auth,'summary':summary,'target_identity_decisions':decisions,'files':catalog,'supplements':SUPPLEMENTS,'book_completeness_evidence':{'Kato':'All printed1–619 in physical23–641; internally numbered21 front pages plus initial cover and publisher ending. Eight OCR boundary pages rendered and read. All ten chapters, supplementary notes/bibliographies and indexes present. Publisher catalog/locator folios differ; no publisher-server byte equivalence claimed.','Yafaev':'Physical185; printed1–153 and155–169; official chapter17 range145–153 and back matter155–169. No listed scholarly section missing at154. CatalogXVI176 versus actual185 physical remains disclosed. Duplicate file same hash.'}})
 chunks=bib_chunks((prior/'BASS_CR_REFERENCES_20261001_v2.bib').read_text());new_chunks=[]
 for wid,entry in chunks.items():
  if wid in TARGETS:
   note='Recovery status: '+current[wid]['fulltext_status']+'. '+current[wid]['selection_reason']
   note=note.replace('_',r'\_').replace('–','--').replace('{','').replace('}','')
   entry=re.sub(r'  note = \{[^\n]*\}',lambda m:'  note = {'+note+'}',entry)
   entry=entry[:-1].rstrip()+',\n  file = {v3/user_uploads/paper/'+TARGETS[wid][0]+'}\n}'
  new_chunks.append(entry)
 (v/'BASS_CR_REFERENCES_20261001_v3.bib').write_text('\n\n'.join(new_chunks)+'\n')
 entries=[]
 for s in SUPPLEMENTS:
  entries.append('@article{'+s['supplement_id']+',\n'+',\n'.join('  '+k+' = {'+str(val)+'}' for k,val in [('title',s['title']),('author',s['bib_author']),('year',s['year']),('doi',s['doi']),('journal',s['journal']),('volume',s['volume']),('pages',s['pages']),('file','v3/user_uploads/paper/'+s['name']),('note','Supplemental user upload; outside original31 target scope; scientific claim status unchanged')])+'\n}')
 (v/'BASS_CR_USER_UPLOAD_SUPPLEMENTAL_REFERENCES_20261001_v3.bib').write_text('\n\n'.join(entries)+'\n')
 oldrows=list(csv.DictReader((prior/'BASS_CR_FULLTEXT_RECOVERY_STATUS_20261001.csv').open()))
 fields=list(oldrows[0])+['previous_v2_status','user_uploaded_file','user_upload_sha256','user_uploaded_page_count','acquisition_provenance']
 for row in oldrows:
  wid=row['work_id'];row['previous_v2_status']=row['fulltext_status'];row.update({k:current[wid][k] if current[wid][k] is not None else '' for k in ['fulltext_status','version_class','fulltext_format','selected_version_id','latest_version','selection_reason','material_change_status','manual_access','notes']})
  row['attempt_count']=c.execute('SELECT count(*) FROM acquisition_attempts WHERE work_id=?',(wid,)).fetchone()[0]
  if wid in TARGETS:
   x=target_by_name[TARGETS[wid][0]];row['user_uploaded_file']='v3/user_uploads/'+x['member'];row['user_upload_sha256']=x['sha256'];row['user_uploaded_page_count']=x['page_count'];row['acquisition_provenance']='USER_UPLOAD';row['acquired_file']=row['user_uploaded_file'];row['source_url']='attachment:'+auth['upload_name']+'#'+x['member']
 with (v/'BASS_CR_FULLTEXT_RECOVERY_STATUS_20261001_v3.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(oldrows)
 with (v/'BASS_CR_WORK_STATUS_ALL31_20261001_v3.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(next(iter(current.values()))));writer.writeheader();writer.writerows(current.values())
 with (v/'BASS_CR_VERSION_RELATIONS_20261001_v3.csv').open('w',newline='') as f:
  data=[dict(x) for x in c.execute('SELECT * FROM relations ORDER BY relation_id')];writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
 report=['# BASS_CR user upload integration v3','', '기존 미확보14건을 사용자 제공 PDF로 반영했다. 논문12편과 책2권의 scholarly fulltext를 확보해 원래31 works 모두 원문을 보유한다(PDF30+공식 HTML1). 추가 문헌4편은 별도 supplemental register/Bib에 기록했고 원래31건의 분모를 늘리지 않았다. Yafaev 두 파일은 byte-identical alias이며 두 작품으로 세지 않았다.','', '| Work | selected version | PDF pages |','|---|---|---:|']
 report += ['| '+x['work_id']+' | '+x['status']+' | '+str(x['page_count'])+' |' for x in decisions]
 report += ['', 'Kato는1995년 재쇄본으로1980년 corrected second edition의 재쇄임이 판권·title leaf에 명시된다. 인용1976판/1980정정쇄/1995재쇄/2012전자판을 분리했다. 제공본은643 PDF페이지이며 내부 인쇄 쪽수1–619와 front matter, 참고문헌·추가문헌·색인·출판사 끝부분을 모두 담는다. 출판사 catalogXXI623 및 온라인 chapter locator와 인쇄 folio의 차이는 기록한다.1976판과의 모든 수정점이나 publisher ebook의 byte equality는 검증하지 않았다.', 'Yafaev는2000년 LNM1735 책185 PDF페이지이다. 내부 본문1–153, back matter155–169, front matterxvi를 확인했다. 공식 출판사도 마지막 chapter를145–153, back matter를155–169로 명시하므로154를 누락된 연구 본문으로 판정하지 않는다. catalogXVI176과 physical185의 차이는 유지했다.2007전자판과 byte equality는 미평가이고 ICM1998 article로 대체하지 않았다.', '', 'Publisher version authorities:', '- https://link.springer.com/book/10.1007/978-3-642-66282-9', '- https://link.springer.com/book/10.1007/BFb0105531', '', 'v1/v2 archive members, original legacy rows,704 prior attempts and98 FAILED rows,13 original PDFs, four source-only code pins, partial front matter and rejected candidate are preserved. Current authority is v3 works/versions/files; v1/v2 metadata remain historical. Acquisition provenance is USER_UPLOAD; public availability/license permission is not inferred. Raw PDF/scans and full text remain private; public repository receives only metadata/scripts.', '', 'scientific calculations=0; native authorization consumption=0; source/code downloads=0; claim ceilings unchanged; capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO. 원문 확보는 과학적 주장 검증이나 gate closure가 아니다.', '', 'Final byte identities, local validation, provider object IDs/revisions/R1 and Git commit/tree are in the separate DELIVERY_RECEIPT. No R3 or separate remote restore test is claimed.']
 (v/'BASS_CR_USER_UPLOAD_INTEGRATION_REPORT_KO_20261001_v3.md').write_text('\n'.join(report)+'\n')
 write_json(v/'RECOVERY_SUMMARY_V3.json',summary)
 # Index new supporting files only. Self hashes and manifest/checksum cycles are excluded explicitly.
 for p in sorted(v.rglob('*')):
  if not p.is_file() or p==db or p.suffix in ['.sqlite-journal','.sqlite-wal','.sqlite-shm']:continue
  relative=p.relative_to(pkg).as_posix()
  if c.execute('SELECT 1 FROM files WHERE relative_path=?',(relative,)).fetchone():continue
  insert(c,'files',{'relative_path':relative,'sha256':sha(p),'bytes':p.stat().st_size,'mime_type':'application/json' if p.suffix=='.json' else 'image/png' if p.suffix=='.png' else 'text/plain','local_path':relative,'access_route':'V3_GENERATED_METADATA_OR_PRESERVED_EVIDENCE','notes':'Support artifact; not a new literature WORK; excluded from scientific fulltext count.'})
 c.commit();c.close()
 file_records=[{'path':p.relative_to(pkg).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(pkg.rglob('*')) if p.is_file()]
 artifacts={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in v.iterdir() if p.is_file()}
 man=v/'BASS_CR_FULLTEXT_RECOVERY_MANIFEST_20261001_v3.json'
 write_json(man,{'schema':'BASS_CR_USER_UPLOAD_INTEGRATION_V3','input_authority':auth,'summary':summary,'artifacts':artifacts,'new_identity_decisions':decisions,'files':file_records,'prior_frozen_zip':{'name':frozen.name,'bytes':frozen.stat().st_size,'sha256':sha(frozen),'all_member_paths_preserved':True},'exclusions':['This v3 recovery manifest itself','Current v3 SQLite self row','New package root manifest and SHA256SUMS_V3','Delivery receipt/validation/final audit outside frozen ZIP'],'copyright':'User-provided personal research copies; private backup; no redistribution permission inferred.'})
 package_records=[{'path':p.relative_to(pkg).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(pkg.rglob('*')) if p.is_file()]
 package_manifest=pkg/'BASS_CR_PACKAGE_MANIFEST_20261001_v3.json'
 write_json(package_manifest,{'files':package_records,'exclusions':['This root v3 package manifest itself','SHA256SUMS_V3'],'legacy_root_manifest':'MANIFEST.json remains unchanged and covers prior v2 scope only'})
 all_files=[p for p in sorted(pkg.rglob('*')) if p.is_file()]
 (pkg/'SHA256SUMS_V3').write_text(''.join(sha(p)+'  '+p.relative_to(pkg).as_posix()+'\n' for p in all_files))
 for p in v.iterdir():
  if p.is_file() and p.name.startswith('BASS_CR_') and 'WORK_STATUS_ALL31' not in p.name:shutil.copy2(p,deliver/p.name)
 archive=deliver/'BASS_CR_LITERATURE_FULLTEXT_RECOVERY_20261001_v3.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(pkg.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(pkg).as_posix())
 print('BUILD_COMPLETE '+json.dumps({'summary':summary,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'new_DB_sha256':sha(db),'target_decisions':len(decisions),'uploaded_files':len(catalog),'package_files':len([p for p in pkg.rglob('*') if p.is_file()])},ensure_ascii=False))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--base',type=Path,required=True);args=parser.parse_args();build(args.base.resolve())
