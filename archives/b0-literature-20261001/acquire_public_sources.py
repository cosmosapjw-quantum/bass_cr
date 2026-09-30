"""Download-only acquisition. Never installs, imports, builds or runs collected code.
Public network only; no paid access or authentication bypass. Original responses
and failed attempts are retained. No claim of scientific validation is made.
"""
import concurrent.futures as cf
import hashlib, html, io, json, os, re, subprocess, tarfile, time, urllib.parse, urllib.request, zipfile
from pathlib import Path

ROOT = Path('payload')
ROOT.mkdir(exist_ok=False)
START = time.monotonic()
ATTEMPTS = []
UA = 'BASS-CR-public-source-archive/1.0 (bounded personal research backup)'

def save(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(data)
    return {'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def fetch(url, path, kind='data', cap=25000000):
    rec = {'requested_url': url, 'path': path, 'kind': kind}
    try:
        if time.monotonic() - START > 650:
            raise TimeoutError('global acquisition deadline')
        if not url.startswith(('https://', 'http://')):
            raise ValueError('public http(s) URL required')
        headers = {'User-Agent': UA}
        # The read-only token is sent ONLY to api.github.com, never a publisher.
        if urllib.parse.urlsplit(url).hostname == 'api.github.com' and os.getenv('GH_TOKEN'):
            headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as r:
            rec.update(http_status=r.status, final_url=r.url, content_type=r.headers.get('Content-Type'))
            data = r.read(cap + 1)
        if len(data) > cap:
            raise ValueError('per-file size limit')
        if kind == 'pdf' and not data.lstrip().startswith(b'%PDF-'):
            raise ValueError('response is not a PDF; not counted as full text')
        if kind == 'json':
            json.loads(data)
        if kind == 'tar':
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as t:
                rec['archive_members'] = len(t.getmembers())
        if kind == 'zip':
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if z.testzip() is not None:
                    raise ValueError('ZIP CRC mismatch')
                rec['archive_members'] = len(z.infolist())
        rec.update(save(path, data), status='ACQUIRED')
        ATTEMPTS.append(rec)
        return data, rec
    except Exception as e:
        rec.update(status='FAILED', error_type=type(e).__name__, error=str(e)[:400])
        ATTEMPTS.append(rec)
        return None, rec

def get_json(url, path):
    b, _ = fetch(url, path, 'json')
    return json.loads(b) if b else {}

def pdf_links(text, base):
    urls = []
    for tag in re.findall(r'<meta\b[^>]*>', text, re.I):
        if re.search(r'citation_pdf_url', tag, re.I):
            m = re.search(r'content\s*=\s*[\"\x27]([^\"\x27]+)', tag, re.I)
            if m:
                urls.append(urllib.parse.urljoin(base, html.unescape(m.group(1))))
    for href in re.findall(r'href\s*=\s*[\"\x27]([^\"\x27]+)', text, re.I):
        if re.search(r'\.pdf(?:[?#]|$)', href, re.I):
            urls.append(urllib.parse.urljoin(base, html.unescape(href)))
    return urls[:8]

def paper(row):
    sid, doi, arxiv, landing = row
    out = {'source_id': sid, 'doi': doi or None, 'arxiv': arxiv or None,
           'fulltext_status': 'NOT_ACQUIRED', 'license_status': 'UNVERIFIED_NO_PUBLIC_REDISTRIBUTION'}
    prefix = 'literature/' + sid + '/'
    candidates = []
    if arxiv:
        page, rec = fetch('https://arxiv.org/abs/' + arxiv, prefix + 'arxiv.html')
        if page:
            txt = page.decode('utf-8', 'replace')
            candidates += pdf_links(txt, rec['final_url'])
            out['arxiv_metadata_url'] = rec['final_url']
        candidates.append('https://arxiv.org/pdf/' + arxiv)
    cr = {}
    if doi:
        cr = get_json('https://api.crossref.org/works/' + urllib.parse.quote(doi, safe=''), prefix + 'crossref.json').get('message', {})
        out['title'] = cr.get('title', [None])[0]
        out['authors'] = cr.get('author', [])
        out['published'] = cr.get('published')
        out['registered_licenses'] = cr.get('license', [])
        out['metadata_verified'] = cr.get('DOI', '').lower() == doi.lower()
        if not landing:
            landing = cr.get('resource', {}).get('primary', {}).get('URL') or 'https://doi.org/' + doi
    if landing:
        page, rec = fetch(landing, prefix + 'landing.html')
        if page:
            if page.lstrip().startswith(b'%PDF-'):
                p = save(prefix + 'landing_fulltext.pdf', page)
                out.update(fulltext_status='PDF_ACQUIRED_IDENTITY_REVIEW_PENDING', fulltext=p, fulltext_url=rec['final_url'])
                return out
            candidates += pdf_links(page.decode('utf-8', 'replace'), rec['final_url'])
    if doi and not arxiv:
        oa = get_json('https://api.openalex.org/works/https://doi.org/' + doi, prefix + 'openalex.json')
        if str(oa.get('doi', '')).lower() == ('https://doi.org/' + doi).lower():
            locs = [oa.get('best_oa_location')] + oa.get('locations', [])
            for loc in locs:
                if loc and loc.get('is_oa') and loc.get('pdf_url'):
                    candidates.insert(0, loc['pdf_url'])
    for link in cr.get('link', []):
        if link.get('content-type') == 'application/pdf':
            candidates.append(link['URL'])
    if doi.startswith('10.1103/'):
        journal = 'prl' if 'PhysRevLett.' in doi else 'pra'
        candidates.append('https://journals.aps.org/' + journal + '/pdf/' + doi)
    elif doi.startswith('10.1137/'):
        candidates.append('https://epubs.siam.org/doi/pdf/' + doi)
    elif doi.startswith('10.1007/'):
        candidates.append('https://link.springer.com/content/pdf/' + doi + '.pdf')
    elif doi == '10.1063/1.1704171':
        candidates.append('https://pubs.aip.org/aip/jmp/article-pdf/5/6/729/19136571/729_1_online.pdf')
    for i, url in enumerate(dict.fromkeys(candidates)):
        if i >= 6:
            break
        data, rec = fetch(url, prefix + 'fulltext_candidate_%02d.pdf' % i, 'pdf')
        if data:
            out.update(fulltext_status='PDF_ACQUIRED_IDENTITY_REVIEW_PENDING', fulltext=rec, fulltext_url=rec['final_url'])
            break
    return out

ROWS = [
('Toshima1999','10.1103/PhysRevA.59.1981','',''),
('RungeMicha1996','10.1103/PhysRevA.53.1388','',''),
('ThorsonDelos1978','10.1103/PhysRevA.18.117','',''),
('Dollard1964','10.1063/1.1704171','',''),
('Enss1979','10.1016/0003-4916(79)90252-5','',''),
('Kadyrov2005','10.1103/PhysRevA.72.032712','nucl-th/0508014',''),
('Kato1976','10.1007/978-3-642-66282-9','',''),
('Stewart2011','10.1137/100792093','',''),
('TemplatesGHEP','10.1137/1.9780898719581.ch5','','https://www.netlib.org/utk/people/JackDongarra/etemplates/node134.html'),
('Stewart1972','10.1137/0709056','',''),
('Mathias1997','10.1137/S5089547989529577','',''),
('Lehtola2019','10.1063/1.5139948','1911.10372',''),
('Martinazzo2020','10.1103/PhysRevLett.124.150601','1907.00841',''),
('Burgarth2022','10.22331/q-2022-06-14-737','2111.08961','https://quantum-journal.org/papers/q-2022-06-14-737/'),
('AlMohyHigham2011','10.1137/100788860','','https://eprints.maths.manchester.ac.uk/1591/'),
('HochbruckLubich1997','10.1137/S0036142995280572','',''),
('AlvermannFehske2011','10.1016/j.jcp.2011.04.006','1102.5071',''),
('ITVOLT2023','10.1016/j.cpc.2023.108780','2210.15677',''),
('LiEtAl2011','10.1137/100808356','',''),
('LiEtAlErratum2013','10.1137/120874795','',''),
('BrayStelbovics1992PRL','10.1103/PhysRevLett.69.53','',''),
('BrayStelbovics1992PRA','10.1103/PhysRevA.46.6995','',''),
('Antonio2024','10.1103/PhysRevA.110.062810','',''),
('Antonio2025','10.1103/xchs-rct2','',''),
('Fachin2026','','2606.06185',''),
('Yafaev2000','10.1007/BFb0105531','',''),
('KuangLin1996','10.1088/0953-4075/29/22/020','',''),
('KuangLin1997','10.1088/0953-4075/30/1/012','',''),
('Errea1998','10.1088/0953-4075/31/14/017','',''),
('DickinsonMcCarroll1983','10.1088/0022-3700/16/3/020','',''),
('Kunikeev1999','10.1016/S0168-583X(99)00013-0','',''),
]

def github_code(repo):
    sid = repo.replace('/', '__')
    pref = 'code/' + sid + '/'
    meta = get_json('https://api.github.com/repos/' + repo, pref + 'repository.json')
    commit = get_json('https://api.github.com/repos/' + repo + '/commits/' + meta.get('default_branch', 'main'), pref + 'commit.json')
    sha = commit.get('sha')
    record = {'repository': repo, 'commit': sha, 'license': meta.get('license'), 'status': 'NOT_ACQUIRED',
              'git_history': 'NOT_INCLUDED', 'submodules': 'NOT_INCLUDED_UNLESS_DISTRIBUTION_CONTAINS_THEM', 'build_or_tests_run': False}
    if sha and re.fullmatch('[0-9a-f]{40}', sha):
        data, receipt = fetch('https://codeload.github.com/' + repo + '/tar.gz/' + sha, pref + sha + '.tar.gz', 'tar', 120000000)
        if data:
            record.update(status='SOURCE_TREE_ARCHIVE_ACQUIRED', archive=receipt)
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as tf:
                for item in tf.getmembers():
                    base = item.name.split('/')[-1].lower()
                    if item.isfile() and item.size < 500000 and (base.startswith(('license','copying','citation')) or base == '.gitmodules'):
                        content = tf.extractfile(item).read()
                        clean = item.name.split('/', 1)[1]
                        if '..' not in Path(clean).parts:
                            save(pref + 'license_and_submodule_metadata/' + clean, content)
    return record

DOCS = [
('PROV_O','https://www.w3.org/TR/prov-o/'),
('CFF','https://citation-file-format.github.io/'),
('SPDX_3_0_1','https://spdx.github.io/spdx-spec/v3.0.1/'),
('BagIt_RFC8493','https://www.rfc-editor.org/rfc/rfc8493.txt'),
('DataCite_4_6','https://datacite-metadata-schema.readthedocs.io/en/4.6/introduction/about-schema/'),
('RO_Crate','https://www.researchobject.org/ro-crate/specification.html'),
('RO_Crate_1_3_announcement','https://www.researchobject.org/ro-crate/blog/2026-06-23/announcing-ro-crate-1-3'),
('SLEPc_EPS','https://slepc.upv.es/release/documentation/manual/eps.html'),
('SLEPc_eigenvector','https://slepc.upv.es/release/manualpages/EPS/EPSGetEigenvector.html'),
('SLEPc_download','https://slepc.upv.es/release/installation/download.html'),
('SciPy_eigh','https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh.html'),
('SciPy_sparse_linalg','https://docs.scipy.org/doc/scipy/reference/sparse.linalg.html'),
('LAPACK_zhegv','https://www.netlib.org/lapack/complex16/zhegv.f'),
('LAPACK_zhegvd','https://www.netlib.org/lapack/complex16/zhegvd.f'),
('LAPACK_zhegvx','https://www.netlib.org/lapack/complex16/zhegvx.f'),
]

if __name__ == '__main__':
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        papers = list(pool.map(paper, ROWS))
        codes = list(pool.map(github_code, ['scipy/scipy','Reference-LAPACK/lapack','slepc/slepc','ry-schneider/Iterative_Volterra_Propagator']))
        docs = list(pool.map(lambda x: fetch(x[1], 'documentation/' + x[0] + '.original')[1], DOCS))
    # Canonical SLEPc GitLab identity, separate from its GitHub mirror.
    gl = get_json('https://gitlab.com/api/v4/projects/slepc%2Fslepc/repository/commits/release', 'code/slepc_canonical_release.json')
    if re.fullmatch('[0-9a-f]{40}', str(gl.get('id', ''))):
        fetch('https://gitlab.com/slepc/slepc/-/archive/' + gl['id'] + '/slepc-' + gl['id'] + '.tar.gz', 'code/slepc_canonical_release.tar.gz', 'tar', 60000000)
    # Pinned SciPy distribution includes vendored sources absent from git archives.
    py = get_json('https://pypi.org/pypi/scipy/1.17.0/json', 'code/scipy_1.17.0_pypi.json')
    for ent in py.get('urls', []):
        if ent.get('packagetype') == 'sdist':
            b, rec = fetch(ent['url'], 'code/' + ent['filename'], 'tar', 120000000)
            if b and rec['sha256'] != ent['digests']['sha256']:
                raise ValueError('PyPI supplied SHA256 mismatch')
    # Original author code supplementary to Al-Mohy--Higham.
    land = ROOT / 'literature/AlMohyHigham2011/landing.html'
    if land.exists():
        links = re.findall(r'href\s*=\s*[\"\x27]([^\"\x27]+\.zip)', land.read_text(errors='replace'), re.I)
        for i, link in enumerate(links[:2]):
            fetch(urllib.parse.urljoin('https://eprints.maths.manchester.ac.uk/1591/', link), 'code/AlMohyHigham_expmv_%d.zip' % i, 'zip')
    summary = {'papers': papers, 'code': codes, 'documentation': docs, 'attempts': ATTEMPTS,
               'scientific_calculations': 0, 'downloaded_code_execution': 0,
               'elapsed_seconds': time.monotonic() - START}
    save('ACQUISITION.json', json.dumps(summary, ensure_ascii=False, indent=2).encode())
    manifest = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(ROOT.rglob('*')) if p.is_file()]
    save('MANIFEST.json', json.dumps(manifest, indent=2).encode())
    with zipfile.ZipFile('payload.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file():
                z.write(p, str(p.relative_to(ROOT)))
    Path('sealed').mkdir(exist_ok=False)
    subprocess.run(['openssl','cms','-encrypt','-binary','-aes-256-cbc','-in','payload.zip','-out','sealed/payload.cms','-outform','DER','transport-public.pem'],check=True)
    receipt = {'payload_bytes': Path('payload.zip').stat().st_size, 'payload_sha256': hashlib.sha256(Path('payload.zip').read_bytes()).hexdigest(), 'sealed_sha256': hashlib.sha256(Path('sealed/payload.cms').read_bytes()).hexdigest(), 'papers_targeted': len(papers), 'pdf_acquired': sum(p['fulltext_status'].startswith('PDF_ACQUIRED') for p in papers), 'code_trees_acquired': sum(p['status']=='SOURCE_TREE_ARCHIVE_ACQUIRED' for p in codes), 'scientific_calculations': 0}
    Path('sealed/TRANSPORT_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt))
