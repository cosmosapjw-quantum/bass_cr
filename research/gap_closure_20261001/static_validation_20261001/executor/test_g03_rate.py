import hashlib,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from g03_rate_postprocess import analyze_query

class G03RateTests(unittest.TestCase):
    def fixture(self,root):
        q=root/'queries';q.mkdir();item=SimpleNamespace(query_id='a'*64,time_hex=float(1).hex())
        arrays={};H=np.eye(18,dtype=complex);H[0,9]=H[9,0]=.2
        arrays.update(selected__S=np.eye(18,dtype=complex),selected__H=H,selected__D=np.zeros((18,18),complex))
        attempts=[]
        for order,value in [(32,.19),(40,.2)]:
            tag=f'q{order}_h1';attempts.append({'resolution':{'order':order,'subdivisions':1}})
            for k in ('S','H','D'):
                raw=np.zeros((9,9),complex)
                if k=='H':raw[0,0]=value
                arrays[tag+'__'+k+'_tp']=raw;arrays[tag+'__'+k+'_pt']=raw.conj().T
        np.savez(q/(item.query_id+'.npz'),**arrays)
        record={'query_id':item.query_id,'time_hex':item.time_hex,'payload_sha256':hashlib.sha256((q/(item.query_id+'.npz')).read_bytes()).hexdigest(),
                'qualification':{'status':'RUNTIME_QUERY_QUALIFIED','lower_resolution':{'order':32,'subdivisions':1},'selected_resolution':{'order':40,'subdivisions':1}},'attempts':attempts}
        (q/(item.query_id+'.json')).write_text(json.dumps(record))
        return q,item,{'z_a0':48.,'R_a0':float(np.hypot(48,2)),'time_hex':item.time_hex}
    def test_levels_spectrum_cluster_and_create_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);q,item,row=self.fixture(root);sample=analyze_query(q,item,row,root/'out')
            self.assertAlmostEqual(sample['rho_per_atomic_time'],.2)
            self.assertAlmostEqual(sample['adjacent_relative_rho_discrepancy'],.05)
            self.assertEqual(sample['dominant_abs_cluster_dimension'],2)
            self.assertEqual(sample['P_selected_status'],'unavailable_without_state')
            with np.load(root/'out'/item.query_id/'q40_h1.npz') as f:
                P=f['dominant_S_orthogonal_projector'];S=f['S']
                np.testing.assert_allclose(P@P,P,atol=1e-13)
                np.testing.assert_allclose(P.conj().T@S,S@P,atol=1e-13)
            with self.assertRaises(FileExistsError):analyze_query(q,item,row,root/'out')
    def test_payload_identity_failure_before_diagnostics(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);q,item,row=self.fixture(root)
            with (q/(item.query_id+'.npz')).open('ab') as f:f.write(b'changed')
            with self.assertRaises(ValueError):analyze_query(q,item,row,root/'out')
            self.assertFalse((root/'out').exists())
    def test_selected_full_cross_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);q,item,row=self.fixture(root);npz=q/(item.query_id+'.npz')
            with np.load(npz) as f:arrays={k:np.array(f[k]) for k in f.files}
            arrays['selected__H'][0,9]=.3;np.savez(npz,**arrays)
            jp=q/(item.query_id+'.json');r=json.loads(jp.read_text());r['payload_sha256']=hashlib.sha256(npz.read_bytes()).hexdigest();jp.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'selected full'):analyze_query(q,item,row,root/'out')

if __name__=='__main__':unittest.main()
