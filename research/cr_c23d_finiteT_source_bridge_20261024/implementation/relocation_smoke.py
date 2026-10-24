"""Targeted delivery repair check: relocation/import/path/guards, NO evolution."""
import pathlib,tempfile,shutil,importlib.util,sys,json,hashlib
UNIT=pathlib.Path(__file__).resolve().parents[1]
# Import current delivery adapter in a relocated sibling-repository layout.
with tempfile.TemporaryDirectory(prefix='c23d_relocate_') as tmp:
 root=pathlib.Path(tmp);unit=root/'research/cr_c23d_finiteT_source_bridge_20261024';(unit/'implementation').mkdir(parents=True);(unit/'inputs').mkdir();shutil.copy2(UNIT/'implementation/source_ee_bridge.py',unit/'implementation/source_ee_bridge.py');shutil.copy2(UNIT/'inputs/CASE.json',unit/'inputs/CASE.json')
 provider=UNIT/'intake/selected_text/bass_cr/research/cr_coulomb_partition_20261014/coulomb_partition.py';csv=UNIT.parent/'n4_resume_transport_20261024/verified_restore/main/repository/research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv'
 p=root/'research/cr_coulomb_partition_20261014/coulomb_partition.py';p.parent.mkdir();shutil.copy2(provider,p);q=root/'research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv';q.parent.mkdir(parents=True);shutil.copy2(csv,q)
 spec=importlib.util.spec_from_file_location('relocated_c23d_adapter',unit/'implementation/source_ee_bridge.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);resolved=m.configure_paths();inp=json.loads(resolved['inputs'].read_text());m.validate(inp);m.load_provider();assert resolved['provider']==p.resolve() and resolved['source_csv']==q.resolve();explicit=m.resolve_input_paths(p,q,unit/'inputs/CASE.json');assert explicit==resolved
 wrong=dict(inp);wrong.pop('n_e_thermal_cm3')
 try:m.validate(wrong);raise AssertionError('missing bath accepted')
 except ValueError:pass
 result={'status':'PASS_RELOCATION_IMPORT_RESOLUTION_GUARD_ONLY','repository_relative_resolution':True,'explicit_overrides':True,'exact_provider_identity_import':True,'missing_bath_rejected':True,'scientific_evolution_executed':False,'old_suite_replay':False}
 (UNIT/'mechanical/RELOCATION_SMOKE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
