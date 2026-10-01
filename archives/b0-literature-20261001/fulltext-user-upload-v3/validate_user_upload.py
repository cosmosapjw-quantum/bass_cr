#!/usr/bin/env python3
"""Read-only validation of imported literature artifacts. No science/network execution."""
import argparse, collections, csv, hashlib, importlib.util, json, re, sqlite3, zipfile
from pathlib import Path
import fitz

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def check(value, message):
    if not value: raise AssertionError(message)

def ro(p):
    c = sqlite3.connect('file:'+str(p.resolve())+'?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    return c

def rows(c,t): return collections.Counter(tuple(x) for x in c.execute('SELECT * FROM "'+t+'"'))

def validate(base):
    root=base/'user_import_v3'; pkg=root/'package'; v=pkg/'v3'; d=root/'deliverables'
    prior=base/'recovery_v2/deliverables'
    module_spec=importlib.util.spec_from_file_location('integration',root/'scripts/integrate_user_upload.py')
    mod=importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(mod)
    upload=base/'upload/paper(1).zip'
    check(sha(upload)=='0175fb89e8d82634efc9339d75639df31d5475da26b7fbe5768556ea4d541381','Uploaded ZIP identity')
    frozen=prior/'BASS_CR_LITERATURE_FULLTEXT_RECOVERY_20261001_v2.zip'
    check(sha(frozen)=='94a6a0627b4ea40bd5c31e902c6c5942401dbc112253056e35d172f4db78b8d2','Frozen v2 archive identity')
    archive=d/'BASS_CR_LITERATURE_FULLTEXT_RECOVERY_20261001_v3.zip'
    archive_hash=sha(archive)
    frozen_count=0; uploaded_count=0
    with zipfile.ZipFile(archive) as z,zipfile.ZipFile(frozen) as z2,zipfile.ZipFile(upload) as zu:
        check(z.testzip() is None,'v3 ZIP CRC'); check(zu.testzip() is None,'Upload CRC')
        names=z.namelist(); check(len(names)==len(set(names)),'No ZIP path collision')
        for info in z2.infolist():
            if info.is_dir(): continue
            check(info.filename in names,'Prior path lost: '+info.filename)
            check(hashlib.sha256(z.read(info.filename)).digest()==hashlib.sha256(z2.read(info)).digest(),'Prior member changed: '+info.filename)
            frozen_count+=1
        for info in zu.infolist():
            if info.is_dir(): continue
            path='v3/user_uploads/'+info.filename
            check(z.read(path)==zu.read(info),'Supplied member bytes changed: '+info.filename)
            uploaded_count+=1
        check(uploaded_count==19,'All19 supplied members')
        check(frozen_count==1177,'Frozen1177 members')
        for p in pkg.rglob('*'):
            if p.is_file(): check(z.read(p.relative_to(pkg).as_posix())==p.read_bytes(),'ZIP/local mismatch: '+str(p))
    man=json.loads((v/'BASS_CR_FULLTEXT_RECOVERY_MANIFEST_20261001_v3.json').read_text())
    rootman=json.loads((pkg/'BASS_CR_PACKAGE_MANIFEST_20261001_v3.json').read_text())
    for collection in [man['files'],rootman['files']]:
        for item in collection:
            p=pkg/item['path']; check(p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],'Manifest binding: '+item['path'])
    checksums=(pkg/'SHA256SUMS_V3').read_text().splitlines()
    for line in checksums:
        h,path=line.split('  ',1); check(sha(pkg/path)==h,'Checksum binding: '+path)
    check(len(checksums)==len([p for p in pkg.rglob('*') if p.is_file()])-1,'Checksum physical coverage excluding itself')
    for p in d.iterdir():
        if p.name.startswith('BASS_CR_') and p.name!='BASS_CR_LITERATURE_FULLTEXT_RECOVERY_20261001_v3.zip':
            check(p.read_bytes()==(v/p.name).read_bytes(),'Delivery sidecar matches ZIP: '+p.name)
    old=ro(prior/'BASS_CR_SOURCE_DATABASE_20261001_v2.sqlite')
    c=ro(v/'BASS_CR_SOURCE_DATABASE_20261001_v3.sqlite')
    check(c.execute('PRAGMA integrity_check').fetchone()[0]=='ok','DB integrity')
    check(not list(c.execute('PRAGMA foreign_key_check')),'DB foreign keys')
    unchanged=[]; extended=[]
    mutable={'works','files','versions','acquisition_attempts','relations','provenance'}
    for t, in old.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        if t=='works': continue
        if t in mutable:
            check(not(rows(old,t)-rows(c,t)),'Prior rows altered/lost: '+t); extended.append(t)
        else:
            check(rows(old,t)==rows(c,t),'Immutable table altered: '+t); unchanged.append(t)
    works={x['work_id']:dict(x) for x in c.execute('SELECT * FROM works')}
    check(len(works)==31,'Target works denominator31')
    missing=set(mod.TARGETS)
    allowed={'fulltext_status','version_class','fulltext_format','selected_version_id','latest_version','selection_reason','material_change_status','manual_access','notes'}
    for oldwork in old.execute('SELECT * FROM works'):
        w=works[oldwork['work_id']]
        for key in oldwork.keys():
            if oldwork['work_id'] not in missing or key not in allowed:
                check(w[key]==oldwork[key],'Unexpected work field alteration: '+oldwork['work_id']+'.'+key)
    class_counts=collections.Counter(w['version_class'] for w in works.values())
    check(dict(class_counts)=={k:val for k,val in man['summary']['target_version_classes'].items() if val},'Disjoint version classes')
    formats=collections.Counter(w['fulltext_format'] for w in works.values())
    check(dict(formats)=={'PDF':30,'HTML_CHAPTER_BUNDLE':1},'30PDF+1HTML target formats')
    for w in works.values():
        selected=c.execute('SELECT * FROM versions WHERE version_id=?',(w['selected_version_id'],)).fetchone()
        check(selected and selected['work_id']==w['work_id'] and selected['complete_fulltext']==1,'Selected complete version: '+w['work_id'])
        check(c.execute('SELECT count(*) FROM files WHERE work_id=? AND version_id=?',(w['work_id'],w['selected_version_id'])).fetchone()[0]>0,'Selected file exists: '+w['work_id'])
    attempts=c.execute('SELECT count(*) FROM acquisition_attempts').fetchone()[0]
    failed=c.execute("SELECT count(*) FROM acquisition_attempts WHERE status='FAILED'").fetchone()[0]
    check(attempts==723 and failed==98,'Attempt totals/history')
    check(c.execute('SELECT count(*) FROM versions').fetchone()[0]==68,'54old+14new versions')
    check(c.execute('SELECT count(*) FROM relations').fetchone()[0]==40,'24old+16new relations')
    check(c.execute('SELECT count(*) FROM supplemental_uploads').fetchone()[0]==4,'Separate supplement table4')
    check(c.execute('SELECT count(*) FROM file_relations').fetchone()[0]==1,'One duplicate relationship')
    for row in c.execute('SELECT * FROM files'):
        p=pkg/(row['local_path'] or row['relative_path'])
        check(p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'DB physical catalog binding: '+row['relative_path'])
    pins={x['artifact_id']:x['commit_sha'] for x in c.execute('SELECT * FROM code_artifacts')}
    check(set(pins.values())=={'2638372d6d07cc861336f64ab321d47660692cf7','74d4d63747bf1770bb60e1110c2075227baa324e','aaaf10689eedae8c6817acae6aacd041cda89acf','46cc1dbef70fdc52fb523075d3c405ea26492908'},'Four code pins')
    check(all(x[0]==0 for x in c.execute('SELECT downloaded_code_executed FROM code_artifacts')),'No pinned code executed')
    catalog=json.loads((v/'BASS_CR_USER_UPLOAD_INTEGRATION_CATALOG_20261001_v3.json').read_text())
    pdf_identity=[]
    for item in catalog['files']:
        p=pkg/item['relative_path']; check(p.read_bytes().startswith(b'%PDF'),'PDF signature')
        doc=fitz.open(p); check(not doc.needs_pass,'Not encrypted')
        check(len(doc)==item['pages'],'Physical page count')
        alltext=[pg.get_text() for pg in doc]
        text=mod.norm(' '.join(alltext[:24])); uris=[link.get('uri','') for pg in doc for link in pg.get_links()]
        doi_observed=mod.norm(item['doi']) in mod.norm(' '.join(uris)+' '+' '.join(alltext[:24]))
        # Older print copies may predate printed DOI strings. Match their printed
        # publisher locator/PII/ISBN to the already established cited DOI metadata.
        locator_anchors={
            'Enss1979':['Annals of Physics','119, 117-132 (1979)','II. Singular and Long-Range Potentials'],
            'Kunikeev1999':['Nuclear Instruments and Methods in Physics Research B 154 (1999)','S0168583X99000130'],
            'Toshima1999':['Physical Review A','Volume 59, Number 3','March 1999','1981'],
            'RungeMicha1996':['Physical Review A','Volume 53, Number 3','March 1996','1388'],
            'Stewart1972':['SIAM J. NUMER. ANAL.','Vol. 9, No. 4, December 1972','669','686'],
            'Mathias1997':['SIAM J. MATRIX ANAL. APPL.','861-867','S5089547989529577'],
            'Yafaev2000':['Lecture Notes in Mathematics','1735','ISBN 3-540-67587-6','Springer, 2000'],
        }
        locator_verified=item['work_id'] in locator_anchors and all(mod.norm(a) in text for a in locator_anchors[item['work_id']])
        check(doi_observed or locator_verified,'DOI or printed publisher locator binding: '+item['relative_path'])
        if item['work_id'] in mod.TARGETS:
            _,pages,title_anchor,author_anchor=mod.TARGETS[item['work_id']]
            check(mod.norm(title_anchor) in text and mod.norm(author_anchor) in text,'Title/author anchor: '+item['relative_path'])
            check(str(item['publication_year']) in ' '.join(alltext[:24]),'Year evidence: '+item['relative_path'])
        else:
            sup=next(x for x in mod.SUPPLEMENTS if x['supplement_id']==item['supplement_id'])
            check(mod.norm(sup['title'])[:60] in text,'Supplement title anchor')
            check(mod.norm(sup['authors'].split(';')[0].split()[-1]) in text,'Supplement author anchor')
            check(str(sup['year']) in ' '.join(alltext[:3]),'Supplement year')
        pdf_identity.append({'member':item['member'],'sha256':sha(p),'pages':len(doc),'role':item['role'],'doi':item['doi'],'DOI_evidence':'PDF_TEXT_OR_LINK' if doi_observed else 'CITED_DOI_METADATA_MATCHED_BY_PRINTED_PUBLISHER_LOCATOR','all_pages_parsed':True})
        doc.close()
    # Content sequence comes from original folio map and direct boundary render observations,
    # with publisher TOC range evidence cited in the frozen catalog/report.
    katomap=json.loads((root/'evidence/PAGE_MAP_kato1995.json').read_text())
    check(len(katomap)==643,'Kato physical643')
    kafile=fitz.open(pkg/'v3/user_uploads/paper/kato1995.pdf')
    check('619' in kafile[640].get_text(),'Kato final printed619')
    check('XXI' in kafile[21].get_text(),'Kato frontXXI')
    check('1995' in ' '.join(kafile[i].get_text() for i in range(24)), 'Kato reprint1995')
    check('1980' in ' '.join(kafile[i].get_text() for i in range(24)), 'Kato corrected1980')
    kafile.close()
    yafile=fitz.open(pkg/'v3/user_uploads/paper/yafaev2000.pdf')
    check('169' in yafile[-1].get_text(),'Yafaev scholarly final169')
    check('1735' in ' '.join(yafile[i].get_text() for i in range(24)), 'Yafaev LNM1735')
    yafile.close()
    bib=mod.bib_chunks((v/'BASS_CR_REFERENCES_20261001_v3.bib').read_text())
    oldbib=mod.bib_chunks((prior/'BASS_CR_REFERENCES_20261001_v2.bib').read_text())
    check(set(bib)==set(works) and len(bib)==31,'Primary Bib31 keys')
    for wid,entry in bib.items():
        if wid not in missing: check(entry==oldbib[wid],'Unchanged prior Bib entry: '+wid)
        w=works[wid]
        if w['doi']: check('doi = {'+w['doi']+'}' in entry,'Bib DOI binding: '+wid)
        if wid in missing:
            check(w['fulltext_status'] in entry.replace(r'\_', '_'),'Bib selected status: '+wid)
            path=re.search(r'file = \{([^}]+)\}',entry).group(1)
            check((pkg/path).is_file(),'Bib PDF binding: '+wid)
    supbib=mod.bib_chunks((v/'BASS_CR_USER_UPLOAD_SUPPLEMENTAL_REFERENCES_20261001_v3.bib').read_text())
    check(set(supbib)=={x['supplement_id'] for x in mod.SUPPLEMENTS},'Separate Bib4')
    status=list(csv.DictReader((v/'BASS_CR_FULLTEXT_RECOVERY_STATUS_20261001_v3.csv').open()))
    check(len(status)==18,'Original recovery18 scope')
    for row in status:
        check(row['fulltext_status']==works[row['work_id']]['fulltext_status'],'CSV current status: '+row['work_id'])
        if row['work_id'] in missing:
            check(sha(pkg/row['user_uploaded_file'])==row['user_upload_sha256'],'CSV hash: '+row['work_id'])
    allpdf=[p for p in pkg.rglob('*') if p.is_file() and p.suffix.lower()=='.pdf']
    pdfhash=collections.defaultdict(list)
    for p in allpdf:pdfhash[sha(p)].append(p.relative_to(pkg).as_posix())
    duplicates={h:paths for h,paths in pdfhash.items() if len(paths)>1}
    check(len(allpdf)==38 and len(pdfhash)==37 and len(duplicates)==1,'PhysicalPDF38/unique37')
    check({Path(p).name for paths in duplicates.values() for p in paths}=={'BFb0105531.pdf','yafaev2000.pdf'},'Only known alias duplicated')
    summary=man['summary']
    for field,expected in [('scientific_calculations',0),('native_authorization_consumption',0),('literature_source_downloads',0),('code_source_downloads',0),('capture',False),('production','HOLD'),('all_bound','OPEN'),('b_grid','NO_GO'),('claim_ceilings','UNCHANGED')]:
        check(summary[field]==expected,'Scientific boundary field '+field)
    result={'status':'PASS','archive':{'name':archive.name,'bytes':archive.stat().st_size,'sha256':archive_hash,'CRC':'PASS'},'frozen_v2_member_hashes_verified':frozen_count,'user_member_byte_equalities_verified':uploaded_count,'target_works':len(works),'complete_target_selected_versions':31,'target_formats':dict(formats),'version_class_counts':dict(class_counts),'supplemental_works':4,'PDF_physical_files':38,'PDF_unique_hashes':37,'duplicate_groups':duplicates,'immutable_tables_verified':unchanged,'append_only_history_tables_verified':extended,'catalog_files_hash_verified':c.execute('SELECT count(*) FROM files').fetchone()[0],'old_catalog_rows_preserved':old.execute('SELECT count(*) FROM files').fetchone()[0],'old_attempts_preserved':704,'new_import_records':19,'total_attempts':attempts,'FAILED_preserved':failed,'primary_Bib_entries':31,'supplemental_Bib_entries':4,'recovery_status_rows':18,'code_pin_count':4,'book_limitations_recorded':True,'current_database_sha256':sha(v/'BASS_CR_SOURCE_DATABASE_20261001_v3.sqlite'),'science_flags':{k:summary[k] for k in ['scientific_calculations','native_authorization_consumption','literature_source_downloads','code_source_downloads','capture','production','all_bound','b_grid','claim_ceilings']},'PDF_identity_checks':pdf_identity}
    out=d/'BASS_CR_USER_UPLOAD_LOCAL_VALIDATION_20261001_v3.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('LOCAL_VALIDATION_PASS '+json.dumps({k:val for k,val in result.items() if k not in ['PDF_identity_checks','immutable_tables_verified','append_only_history_tables_verified','duplicate_groups']},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base',type=Path,required=True);args=parser.parse_args();validate(args.base.resolve())
