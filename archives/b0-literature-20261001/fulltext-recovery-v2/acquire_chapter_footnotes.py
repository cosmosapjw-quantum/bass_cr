"""Recover official chapter footnotes and Kato open front matter for edition evidence."""
import concurrent.futures as cf
import hashlib
import json
from pathlib import Path
import time
import urllib.parse
import zipfile
import acquire_missing_fulltexts as a


def main():
    a.ROOT = Path('payload_footnotes')
    a.ROOT.mkdir(exist_ok=False)
    a.START = time.monotonic()
    spec = json.loads(Path('footnote_spec.json').read_text())
    known = set(spec['already_acquired_image_urls'])
    sid = 'TemplatesGHEP'
    base = 'https://www.netlib.org/utk/people/JackDongarra/etemplates/'
    b, r = a.fetch(sid, base+'footnode.html', 'chapter/footnode.html',
                   'official_chapter_footnote_dependency')
    result = {'scope': [sid, 'Kato1976'], 'required_anchors': spec['required_anchors'],
              'scientific_calculations': 0, 'native_authorization_consumption': 0,
              'downloaded_code_execution': 0}
    if b:
        text = b.decode('utf-8', 'replace')
        result['anchors_present'] = {x: x in text for x in spec['required_anchors']}
        urls = set(urllib.parse.urljoin(base, u).replace('http://www.netlib.org',
                    'https://www.netlib.org') for u in a.Links(text).images)
        result['image_urls'] = sorted(urls)
        def image(u):
            parsed = urllib.parse.urlsplit(u)
            if parsed.hostname != 'www.netlib.org':
                return {'url':u,'status':'REJECTED_SOURCE'}
            label = 'chapter/' + ('icons/' if '/utk/icons/' in parsed.path else '') + Path(parsed.path).name
            return a.fetch(sid,u,label,'official_footnote_image')[1]
        with cf.ThreadPoolExecutor(max_workers=4) as pool:
            result['new_images'] = list(pool.map(image, sorted(urls-known)))
    a.fetch('Kato1976', 'https://link.springer.com/content/pdf/bfm:978-3-642-66282-9/1',
            'publisher_frontmatter.pdf', 'official_open_book_frontmatter', 'pdf')
    result['attempts'] = a.ATTEMPTS
    a.save('ACQUISITION_FOOTNOTES.json',json.dumps(result,indent=2).encode())
    manifest = [{'path':str(q.relative_to(a.ROOT)),'bytes':q.stat().st_size,
                 'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
                for q in sorted(a.ROOT.rglob('*')) if q.is_file()]
    a.save('MANIFEST.json',json.dumps(manifest,indent=2).encode())
    with zipfile.ZipFile('recovery_payload.zip','x',zipfile.ZIP_DEFLATED) as z:
        for q in sorted(a.ROOT.rglob('*')):
            if q.is_file():z.write(q,str(q.relative_to(a.ROOT)))
    print(json.dumps({'target_count':2,'attempts':len(a.ATTEMPTS),'scientific_calculations':0}))


if __name__=='__main__':
    main()
