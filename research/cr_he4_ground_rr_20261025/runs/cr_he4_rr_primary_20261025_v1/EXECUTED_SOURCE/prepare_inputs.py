"""Restore exact admitted bytes; no scientific computation or baseline replay."""
import argparse, hashlib, json, shutil, time
from pathlib import Path

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main(unit, canonical_root):
    t=time.process_time()
    manifest=json.loads((canonical_root/'MANIFEST.json').read_text())
    checked=[]
    for row in manifest['files']:
        p=canonical_root/row['path']
        if p.stat().st_size!=row['size_bytes'] or digest(p)!=row['sha256']:
            raise ValueError('CANONICAL_PAYLOAD_IDENTITY:'+row['path'])
        checked.append(row['path'])
    old=canonical_root/'research/cr_n5_rr_milne_20261025'
    old_config=json.loads((old/'inputs/CONFIG.json').read_text())
    config={**old_config, 'schema':'CR_HE4_RR_ON_SAVED_H1_V1',
        'input_id':'cr_he4_rr_input_20261025_v1',
        'consumer':'CR_HE4_GROUND_RR_ON_H1_SAVED_CHAIN_V1',
        'primary_run_id':'cr_he4_rr_primary_20261025_v1',
        'test_run_id':'cr_he4_rr_controls_20261025_v1',
        'review_run_id':'cr_he4_rr_c9_20261025_v1',
        'plot_run_id':'cr_he4_rr_plot_20261025_v1',
        'I_He_eV':24.59, 'g_He_bound':1, 'g_He_ion':2, 'd_He':4,
        'n_HeII_cm3':0.02, 'PI_maximum_eV':50000.0,
        'isotope_assignment':'CONDITIONAL_ELEMENTAL_HE_TO_HE4',
        'source_residual_state_resolution':'CONDITIONAL_SMOOTH_GROUND_CHANNEL_MODEL',
        'finite_mass':False, 'recoil_owner':'ZERO_RECOIL_MODEL',
        'operator_baseline':'EXACT_STORED_PR105_K_DIAG',
        'planned_primary_cases':8, 'planned_primary_rhs':192,
        'resources':{'inherited_known_lineage_cpu_s':'39.097868524',
          'separate_C23E_lineage_cpu_s':'15.493261114',
          'sum_historical_lineages':False,'new_unit_total_cpu_s':30.0,
          'test_cpu_s':5,'primary_cpu_s':8,'review_cpu_s':10,'plot_cpu_s':5,
          'wall_s':60,'worker_cpu':0,'reviewer_cpu':2,'coordinator_cpu':8,
          'native_threads':1,'RLIMIT_AS_bytes':512*1024**2,
          'memory_reserve_bytes':1024**3}}
    inp=unit/'inputs';inp.mkdir(parents=True,exist_ok=False)
    with (inp/'CONFIG.json').open('x') as f:json.dump(config,f,indent=2);f.write('\n')
    copies=[]
    for p in sorted((old/'inputs/reused/pr104').glob('*.npz')):
        copies.append((p,'inputs/reused/pr104/'+p.name))
    for p in sorted((old/'runs/n5_rr_milne_primary_20261025_v1').glob('*.npz')):
        copies.append((p,'inputs/reused/pr105/'+p.name))
    for p in sorted((old/'inputs/reused/c23d').glob('ATOMS_*.csv')):
        copies.append((p,'inputs/reused/c23d/'+p.name))
    for rel in ['spectral_photo_source.py','data/verner_photo.dat']:
        copies.append((old/'inputs/reused/c23b'/rel,'inputs/reused/c23b/'+rel))
    if len(copies)!=21:raise ValueError('EXPECTED_21_IMMUTABLE_INPUTS')
    rows=[]
    for src,rel in copies:
        dst=unit/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('xb') as f:f.write(src.read_bytes())
        rows.append({'path':rel,'canonical_path':str(src.relative_to(canonical_root)),
            'bytes':dst.stat().st_size,'sha256':digest(dst),
            'publication':'PRIVATE_INPUT_NOT_PUBLIC_GIT'})
    record={'schema':'CR_HE4_RR_IMMUTABLE_INPUTS_V1','files':rows,
      'canonical_archive_sha256':'f1afdb40303b28a498a62f9f8d38858b8bea584d0ed8a4e63bd87e4e11d362c5',
      'canonical_manifest_payloads_verified':len(checked),
      'frozen_contract_sha256':digest(unit/'FROZEN_CONTRACT.md'),
      'config_sha256':digest(inp/'CONFIG.json'),
      'new_scientific_execution':False,'recovery_cpu_s':time.process_time()-t}
    with (inp/'INPUT_MANIFEST.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps({'status':'INPUT_RESTORE_PASS','files':len(rows),
                     'canonical_payloads_verified':len(checked),'recovery_cpu_s':record['recovery_cpu_s']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True)
    p.add_argument('--canonical-root',type=Path,required=True);a=p.parse_args()
    main(a.unit,a.canonical_root)
