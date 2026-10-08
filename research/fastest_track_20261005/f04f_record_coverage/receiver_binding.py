"""Read stored F05 bytes and bind accepted aggregates to F04D's 25 outputs.

No RHS, root solver, derivative evaluator, certificate checker or native entry
point is imported. Hex values are binary64 observations/unit conversions;
exact ratios are arithmetic on those observations, not root/event enclosures.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import struct
import time
import zipfile

MODEL = 'REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1'
STATE = ['x_HII','x_HeII','x_HeIII','w_u_over_nH_eV','p0_over_nH','p1_over_nH','p2_over_nH']
NAMES = STATE + [f'PI_{a}_{g}' for a in range(3) for g in range(3)] + [f'CI_{a}' for a in range(3)] + [f'RR_{a}' for a in range(3)] + ['DR_0','DR_1','escaped_energy_over_nH_eV']
SITES = ['FULL_BE_ENDPOINT','HALF1_BE_ENDPOINT','HALF2_BE_ENDPOINT']
LOCK_SHA = '5631c65b87713520d8280e35507c8127141b28912d1d73bedfbe888925093e90'
DONOR_SHA = '14a076a223ad62a445149521ae00683b8b88ac23e26227b3e5a19f827fd17879'
MANIFEST_SHA = '779c429e5fada3149809190539a8fea9337f0ff00c4a298be78346f1935ed84b'
CONSTANTS_SHA = '92f085ba18282f566982d83b55ec5de989f586d1ced38fc3e177b03297b62608'
RUN = 'runs/rei_fastest_v1/first_interval/'
SCHEMA = set('accepted model_id t0_s dt_s old_state parent_box parent_center state next_box local_bounds public_widths sites events ledgers'.split())
LEDGERS = ['H_nuclei','He_nuclei','electron_charge_neutrality','photon_group0_absorption','photon_group1_absorption','photon_group2_absorption','thermal_binding_photon_escape_total_energy']


def require(ok, label):
    if not ok: raise ValueError(label)


def sha(data): return hashlib.sha256(data).hexdigest()


def read_json(path): return json.loads(Path(path).read_text())


def number(v):
    require(type(v) in (float, int) and math.isfinite(v), 'FINITE_NUMBER')
    return float(v)


def vector(v, n):
    require(isinstance(v,list) and len(v)==n, 'VECTOR_SHAPE')
    return [number(x) for x in v]


def matrix(v, n, m):
    require(isinstance(v,list) and len(v)==n, 'MATRIX_SHAPE')
    return [vector(x,m) for x in v]


def decode(bits):
    require(isinstance(bits,str) and len(bits)==16, 'BITS')
    return number(struct.unpack('>d',bytes.fromhex(bits))[0])


def bits(v): return struct.pack('>d',number(v)).hex()


def frame_sources(data):
    header = b'REI_F05_SOURCE_V1\n'
    require(data.startswith(header), 'SOURCE_HEADER'); offset = len(header); out = {}
    while offset < len(data):
        end = data.find(b'\n',offset); require(end >= 0,'SOURCE_FRAME')
        name, count = data[offset:end].decode('utf-8').rsplit(' ',1)
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts and str(path)==name and name not in out, 'SOURCE_PATH')
        require(count.isdigit(), 'SOURCE_LENGTH'); count=int(count); offset=end+1
        require(count>0 and offset+count<len(data) and data[offset+count:offset+count+1]==b'\n','SOURCE_LENGTH')
        out[name]=data[offset:offset+count]; offset+=count+1
    return out


def verify_archive(path):
    data=Path(path).read_bytes()
    require(len(data)==224864 and sha(data)==DONOR_SHA,'DONOR_ARCHIVE_IDENTITY')
    with zipfile.ZipFile(path) as z:
        members=z.infolist(); names=[x.filename for x in members]
        require(len(names)==len(set(names)), 'DONOR_DUPLICATE')
        for x in members:
            p=PurePosixPath(x.filename)
            require(not p.is_absolute() and '..' not in p.parts and not '\\' in x.filename and (x.external_attr>>16)&0o170000 != 0o120000,'DONOR_PATH')
        prefix='BASS_CR_CHAT_F04D_20261005/'
        raw=z.read(prefix+'FILE_MANIFEST.json');require(sha(raw)==MANIFEST_SHA,'DONOR_MANIFEST_IDENTITY')
        listed=[]
        for e in json.loads(raw)['files']:
            name=prefix+e['path'];b=z.read(name)
            require(len(b)==e['bytes'] and sha(b)==e['sha256'],'DONOR_PAYLOAD_IDENTITY');listed.append(name)
        require(len(listed)==len(set(listed)) and set(listed)=={x.filename for x in members if not x.is_dir()}-{prefix+'FILE_MANIFEST.json'},'DONOR_PAYLOAD_SET')
        require(z.testzip() is None,'DONOR_CRC')
    return len(listed)


class Context:
    @classmethod
    def from_capsule(cls, directory):
        p=Path(directory);self=cls()
        raw=(p/'SOURCE_LOCK.json').read_bytes();require(sha(raw)==LOCK_SHA,'LOCK_IDENTITY')
        self.lock=json.loads(raw);require(self.lock['receiver_ref']=='7c5469101f8d6ef027c8c3119cc5c053e15ba1d9','RECEIVER_REF')
        self.entries={x['path']:x for x in self.lock['files']}
        for name in ['parent_manifest.json','source_identity.dat','checker_receipt.json','ft03_first_interval.json']+[f'level_{i}_summary.json' for i in range(3)]:
            matches=[x for x in self.lock['files'] if Path(x['path']).name==name];require(len(matches)==1,'LOCK_ENTRY')
            e=matches[0];b=(p/name).read_bytes();require(len(b)==e['bytes'] and sha(b)==e['sha256'],'CAPSULE_IDENTITY')
        self.parent=read_json(p/'parent_manifest.json'); donor=read_json(p/'OWNER_PARENT_EXTRACT.json')
        manifest=(p/'FILE_MANIFEST.json').read_bytes();require(sha(manifest)==MANIFEST_SHA,'DONOR_MANIFEST_IDENTITY')
        for e in json.loads(manifest)['files']:
            name=Path(e['path']).name
            if name in ['OWNER_PARENT_EXTRACT.json','SOURCE_BINDING.json','ft03_map_constants.json','CENTRAL_PARENT_JETS.json']:
                b=(p/name).read_bytes();require(len(b)==e['bytes'] and sha(b)==e['sha256'],'DONOR_CAPSULE_IDENTITY')
        require(sha((p/'ft03_map_constants.json').read_bytes())==CONSTANTS_SHA,'COMPILED_CONSTANTS_IDENTITY')
        self.frames=frame_sources((p/'source_identity.dat').read_bytes());require(len(self.frames)==22,'COMPILED_SOURCE_COUNT')
        for name, digest in self.parent['source_identity'].items():
            if name in self.frames:require(sha(self.frames[name])==digest,'PARENT_COMPILED_SOURCE')
        binding=read_json(p/'SOURCE_BINDING.json')
        for name,digest in binding['production_sources_sha256'].items():
            require(sha(self.frames['rust/rei_microphysics/src/'+name])==digest,'DONOR_COMPILED_SOURCE')
        for name in ['rust/rei_microphysics/src/adaptive_history.rs','rust/rei_microphysics/examples/first_interval.rs']:
            require(sha(self.frames[name])==self.entries[name]['sha256'],'TRANSACTION_COMPILED_SOURCE')
        require(donor['model_id']==self.parent['model_id']==MODEL,'MODEL')
        require(donor['manifest_sha256_reported']==sha((p/'parent_manifest.json').read_bytes()),'PARENT_MANIFEST')
        require(donor['coordinate_ids']==self.parent['coordinate_ids']==STATE and donor['radii']==self.parent['radii'],'PARENT_COORDINATES')
        for key in ['center_bits','constants_bits','sigma_bits']:
            require(donor[key]==self.parent['actual_center_and_model_bits'][key],'PARENT_BITS')
        require(donor['h_s']==self.parent['fixed_model_inputs']['step_h_s'],'PARENT_STEP')
        cs=self.parent['actual_center_and_model_bits']['constants_bits'];self.nh=decode(cs[0]);self.ev=decode(cs[4])
        require(self.nh>0 and self.ev>0,'UNIT_SCALE')
        self.jets=read_json(p/'CENTRAL_PARENT_JETS.json');require(self.jets['names']==NAMES,'OUTPUT_NAMES')
        self.input=read_json(p/'ft03_first_interval.json');self.checker=read_json(p/'checker_receipt.json')
        require(self.checker['status']=='PASS' and self.checker['uniformly_certified_trials']==7000,'INHERITED_CHECKER')
        return self

    def normalized(self,s):
        return s[:3]+[s[3]/(self.nh*self.ev)]+[x/self.nh for x in s[4:7]]

    def verify_receiver(self, root):
        for path,e in self.entries.items():
            b=(Path(root)/path).read_bytes()
            require(len(b)==e['bytes'] and sha(b)==e['sha256'],'RECEIVER_IDENTITY:'+path)
            require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['git_blob'],'GIT_BLOB:'+path)


def check_box(box, center):
    box=matrix(box,7,2)
    require(all(lo<=c<=hi for (lo,hi),c in zip(box,center)), 'BOX_CENTER')


def bind_record(d,c):
    require(d.get('model_id')==MODEL,'MODEL')
    require(type(d.get('accepted')) is bool,'ACCEPTED_FLAG')
    if not d['accepted']:return None
    require(set(d)==SCHEMA,'TRANSACTION_SCHEMA')
    t=number(d['t0_s']);h=number(d['dt_s']);require(t>=0 and h>0,'TIME_DOMAIN')
    old=vector(d['old_state'],8);state=vector(d['state'],8)
    parent=vector(d['parent_center'],7)
    require(c.normalized(old)==parent,'PARENT_STATE_CENTER')
    check_box(d['parent_box'],parent)
    require(isinstance(d['sites'],list) and len(d['sites'])==3,'SITE_COUNT')
    for i,s in enumerate(d['sites']):
        require(set(s)==set('id step_s center box preconditioner'.split()) and s['id']==SITES[i],'SITE_IDENTITY')
        require(number(s['step_s'])==(h if i==0 else h/2),'SITE_STEP')
        center=vector(s['center'],7);check_box(s['box'],center);matrix(s['preconditioner'],7,7)
    accepted=vector(d['sites'][2]['center'],7)
    require(c.normalized(state)==accepted,'STATE_CENTER')
    check_box(d['next_box'],accepted)
    require(all(0<=x<2e-4 for x in vector(d['local_bounds'],4)),'LOCAL_LIMIT')
    require(all(0<=x<2e-3 for row in matrix(d['public_widths'],2,4) for x in row),'WIDTH_LIMIT')
    require(isinstance(d['ledgers'],dict) and set(d['ledgers'])==set(LEDGERS),'LEDGER_SCHEMA')
    require(all(abs(number(d['ledgers'][name]))<1e-12 for name in LEDGERS),'LEDGER_LIMIT')
    events=d['events'];require(set(events)=={'photo','collision','recombination','dr'},'EVENT_SCHEMA')
    raw=[x for row in matrix(events['photo'],3,3) for x in row]+vector(events['collision'],3)+vector(events['recombination'],3)+vector(events['dr'],2)
    require(all(x>=0 for x in raw) and state[7]>=old[7], 'EVENT_ESCAPE_DOMAIN')
    exact=[Fraction(x)/Fraction(c.nh) for x in raw]
    escape=(Fraction(state[7])-Fraction(old[7]))/(Fraction(c.nh)*Fraction(c.ev))
    values=accepted+[x/c.nh for x in raw]+[float(escape)]
    require(all(math.isfinite(x) for x in values),'NORMALIZATION_RANGE')
    return {'t0_hex':t.hex(),'dt_hex':h.hex(),'values_hex':[x.hex() for x in values],
            'event_escape_exact_ratios':[str(x) for x in exact+[escape]],
            'half1_center_bits':[bits(x) for x in d['sites'][1]['center']]}


class History:
    def __init__(self,context):
        self.c=context;self.previous=None;self.accepted=0;self.rejected=0;self.t=0.0
    def add(self,d):
        require(number(d['t0_s'])==self.t,'TIME_CHAIN')
        if self.previous is not None:
            p=self.previous
            require(d['old_state']==p['state'],'STATE_CHAIN')
            require(d['parent_box']==p['next_box'],'BOX_CHAIN')
            require(d['parent_center']==p['sites'][2]['center'],'PARENT_CHAIN')
        out=bind_record(d,self.c)
        if out is None:self.rejected+=1;return None
        if self.previous is None:
            require([bits(x) for x in d['parent_center']]==self.c.parent['actual_center_and_model_bits']['center_bits'],'INITIAL_PARENT_BITS')
        self.t=number(d['t0_s'])+number(d['dt_s']);require(math.isfinite(self.t),'TIME_RANGE')
        self.previous=d;self.accepted+=1
        return out


def run(capsule,receiver,output):
    start=time.monotonic();c=Context.from_capsule(capsule)
    count=verify_archive(Path(capsule)/'BASS_CR_CHAT_F04D_20261005_v1.zip');c.verify_receiver(receiver)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    levels=[];comparison=[]
    for level in range(3):
        path=Path(receiver)/(RUN+f'level_{level}_transactions.jsonl.gz');h=History(c)
        summary=read_json(Path(receiver)/(RUN+f'level_{level}_summary.json'))
        vector(summary['initial_state'],8)
        with gzip.open(path,'rb') as source, (output/f'level_{level}_25_outputs.jsonl.gz').open('xb') as destination:
            with gzip.GzipFile(filename='',fileobj=destination,mode='wb',mtime=0) as sink:
                for line_index,line in enumerate(source):
                    d=json.loads(line);row=h.add(d)
                    if row is None:continue
                    if h.accepted==1:
                        require(d['old_state']==summary['initial_state'] and d['parent_box']==summary['initial_parent_box'],'INITIAL_SUMMARY')
                    row.update({'line':line_index,'raw_line_sha256':sha(line)})
                    sink.write((json.dumps(row,separators=(',',':'))+'\n').encode())
                    if level==0 and h.accepted==1:
                        require(d['dt_s']==c.parent['fixed_model_inputs']['step_h_s'],'DONOR_POINT_STEP')
                        with localcontext() as ctx:
                            ctx.prec=90
                            for name,v,jet in zip(NAMES,row['values_hex'],c.jets['two_half_cumulative']):
                                comparison.append({'name':name,'observed_or_converted_hex':v,'donor_real_point_value':jet['value'],'binary64_minus_real_point':str(Decimal.from_float(float.fromhex(v))-Decimal(jet['value']))})
        require(h.accepted==summary['accepted_steps'] and h.rejected==summary['rejected_steps'],'COUNT_SUMMARY')
        require(h.t==summary['t_end_s']==1e12 and summary['finished'] is True,'END_SUMMARY')
        require(h.previous['state']==summary['final_state'],'FINAL_SUMMARY')
        inherited=next(x for x in c.checker['levels'] if x['level']==level)
        require(h.accepted==inherited['accepted'] and h.rejected==inherited['rejected'],'COUNT_CHECKER')
        levels.append({'level':level,'accepted':h.accepted,'rejected':h.rejected,'t_end_s':h.t,'journal':c.entries[RUN+f'level_{level}_transactions.jsonl.gz'],'inherited_checker_status':'PASS_NOT_RERUN'})
    result={'status':'READ_ONLY_AGGREGATE_BINDING_PASS','receiver_ref':c.lock['receiver_ref'],'donor_payload_files_verified':count,'output_names':NAMES,'levels':levels,'accepted_outputs':sum(x['accepted'] for x in levels),'compiled_source_frames':[{ 'path':name,'bytes':len(body),'sha256':sha(body)} for name,body in c.frames.items()],
            'missing_observations':{'half1_events':None,'half2_events':None,'half1_escape_increment':None,'half2_escape_increment':None,'native_output_gradients':None,'native_output_hessians':None,'uniform_event_escape_remainders':None},
            'point_comparison':'DIAGNOSTIC_ONLY_NO_PARITY_TOLERANCE_OR_INTERVAL_CLAIM','native_runs':0,'root_refinements':0,'certificate_checker_runs':0,'independent_review':'NOT_PERFORMED','production':'HOLD','actual_cr_dispatch_counts':None,'wall_s':time.monotonic()-start}
    (output/'BINDING_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (output/'FIRST_POINT_DIFFERENCES.json').write_text(json.dumps(comparison,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--capsule',type=Path,required=True);p.add_argument('--receiver',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=run(a.capsule,a.receiver,a.output)
    print(json.dumps({k:result[k] for k in ['status','accepted_outputs','native_runs','certificate_checker_runs','wall_s']}))
