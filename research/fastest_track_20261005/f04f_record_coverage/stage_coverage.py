"""Reuse verified F04E observations; describe the current F08 interface boundary.

This is a static observation view, not a PrimaryStep or an expanding execution
record. The delivered parser is used unchanged. No donor test/driver is run.
"""
from fractions import Fraction
import importlib.util
import json
from pathlib import Path, PurePosixPath
import zipfile

from receiver_binding import Context, NAMES, bind_record, bits, require, sha

F04E_SHA='b88932c7a2337972df19231755491725b7090bab347d203fa514fce2717b7cdd'
F04E_MANIFEST_SHA='a7de6920525d4a8ac8b2c7680e574566ce5e36e530d12f64feec50ee3d772610'
OWNER_LOCK_SHA='efd3af79bcfa0dead2baa783668d8bddc9b5515980c12b9def2a554d78257e8d'


def intake_f04e(inputs):
    inputs=Path(inputs);p=inputs/'f04e';archive=inputs/'BASS_CR_CHAT_F04E_20261005_v1.zip'
    raw=archive.read_bytes();require(len(raw)==404871 and sha(raw)==F04E_SHA,'F04E_ARCHIVE')
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist();names=[x.filename for x in infos]
        require(len(names)==len(set(names)),'F04E_DUPLICATE')
        for x in infos:
            name=PurePosixPath(x.filename)
            require(not name.is_absolute() and '..' not in name.parts and '\\' not in x.filename and (x.external_attr>>16)&0o170000!=0o120000,'F04E_PATH')
        manifest=z.read('FILE_MANIFEST.json');require(sha(manifest)==F04E_MANIFEST_SHA,'F04E_MANIFEST')
        entries=json.loads(manifest)['files'];listed=set()
        for e in entries:
            b=z.read(e['path']);require(len(b)==e['bytes'] and sha(b)==e['sha256'],'F04E_PAYLOAD')
            require(e['path'] not in listed,'F04E_MANIFEST_DUPLICATE');listed.add(e['path'])
        require(listed=={x.filename for x in infos if not x.is_dir()}-{'FILE_MANIFEST.json'} and z.testzip() is None,'F04E_PAYLOAD_SET_CRC')
        for f in p.rglob('*'):
            if f.is_file():require(f.read_bytes()==z.read(str(f.relative_to(p))),'F04E_MATERIALIZED')
    spec=importlib.util.spec_from_file_location('delivered_f04e_parser',p/'src/receiver_binding.py')
    donor=importlib.util.module_from_spec(spec);spec.loader.exec_module(donor)
    observation=(p/'results/native01/03.stdout').read_bytes()
    execution=json.loads((p/'results/native01/EXECUTION.json').read_text())
    record=json.loads((p/'inputs/F05_FIRST_TRANSACTION.json').read_text())
    require(sha((p/'inputs/F05_FIRST_TRANSACTION.json').read_bytes())==execution['record_sha256'],'F04E_RECORD_IDENTITY')
    c=Context.from_capsule(inputs)
    for name,digest in execution['source_files'].items():
        require(sha(c.frames['rust/rei_microphysics/src/'+name])==digest,'F04E_SOURCE_IDENTITY')
    return c,record,donor.parse_observation(observation.decode()),execution


def static_stage_views(c,record,obs):
    bind_record(record,c)
    require(record['t0_s']==0 and obs['CONTROL'][0]==record['dt_s'] and obs['CONTROL'][1]==record['dt_s']/2,'STATIC_TIME_IDENTITY')
    require([bits(x) for x in obs['OLD']]==[bits(x) for x in record['old_state']],'STATIC_INPUT_IDENTITY')
    require([bits(x) for x in obs['CONSTANTS']]==c.parent['actual_center_and_model_bits']['constants_bits'],'STATIC_MODEL_IDENTITY')
    views=[];old=obs['OLD']
    for i in range(2):
        tag=f'HALF{i+1}';state=obs[tag+'_STATE'];events=obs[tag+'_EVENTS']
        require(len(events)==17,'STAGE_EVENT_SHAPE')
        scale=Fraction(c.nh);energy_scale=scale*Fraction(c.ev)
        # F04D/FT03 PI is absorber-major; F08 PrimaryEvents is packet-major.
        photo=[[str(Fraction(events[3*a+g])/scale) for a in range(3)] for g in range(3)]
        view={'site':f'HALF{i+1}_BE_ENDPOINT','static_endpoint_s':str(Fraction(record['t0_s'])+Fraction(record['dt_s'])*(i+1)/2),
              'endpoint_time_origin':'DERIVED_FROM_STATIC_BE_RECORD_NOT_EXPANDING_CLOCK',
              'photo_per_h_packet_major_exact':photo,'collision_per_h_exact':[str(Fraction(x)/scale) for x in events[9:12]],
              'recombination_per_h_exact':[str(Fraction(x)/scale) for x in events[12:15]],'dr_per_h_exact':[str(Fraction(x)/scale) for x in events[15:17]],
              'state_bits':[bits(x) for x in state],'temperature_observed_K':obs[tag+'_AUX'][0],
              'escape_difference_of_stored_states_eV_per_h_exact':str((Fraction(state[7])-Fraction(old[7]))/energy_scale),
              'native_reported_escape_increment_erg_cm3_bits':bits(obs['ESCAPE_INCREMENT'][i]),
              'actual_F08_stage':None,'actual_expanding_time_a':None,'actual_stage_weight':None,'actual_F08_thermal_work_ev_per_h':None}
        views.append(view);old=state
    return views


def owner_contract(root):
    root=Path(root);raw=(root/'OWNER_SOURCE_LOCK.json').read_bytes();require(sha(raw)==OWNER_LOCK_SHA,'OWNER_LOCK_IDENTITY')
    lock=json.loads(raw)
    for e in lock['files']:
        b=(root/e['capsule']).read_bytes();require(len(b)==e['bytes'] and sha(b)==e['sha256'],'OWNER_SOURCE_IDENTITY')
    state=json.loads((root/'owner_snapshot/EXECUTION_STATE.json').read_text())
    qualification=json.loads((root/'owner_snapshot/qualification.json').read_text())
    return {'receiver_ref':lock['receiver_ref'],'source':'rust/rei_microphysics/src/coupled_primary.rs',
            'call_site':'endpoint -> PrimaryEvents -> primary_stage_step; try_primary_stage_step commits after checks',
            'photo_axes':'photo_per_h[packet][absorber]; F04D PI_[absorber]_[group] requires explicit transpose for fixed 3 packets only',
            'units':'photons/events per H; w/escape/work eV per H; dt seconds; nH proper cm^-3; Hmean s^-1',
            'required_owner_context':['packet_id/energy at conditional stage','n_h_cm3','f_he','h_mean_per_s','dt','old/state identity','accepted commit identity','transport/time/scale-factor convention'],
            'paired_history':state['F08_stage']['paired_history'],'conditional_stage_status':state['F08_stage']['state'],
            'qualified_root_scope':qualification['scope'],'qualification_reexecuted':False,
            'reuse_static_records_as_expanding_stage':'FORBIDDEN_CONTEXT_NOT_OBSERVED','mandatory_new_gate':False}


def analyze(root):
    root=Path(root);c,record,obs,execution=intake_f04e(root/'inputs')
    sample=json.loads((root/'inputs/level_0_sample.jsonl').read_text().splitlines()[0])
    require(record==sample,'F04E_F05_FIRST_RECORD')
    aggregate=json.loads((root/'evidence/binding/BINDING_RESULT.json').read_text())
    require(aggregate['accepted_outputs']==7000 and aggregate['status']=='READ_ONLY_AGGREGATE_BINDING_PASS','AGGREGATE_RECEIPT')
    return {'task':'F04F_READ_ONLY_RECORD_AND_STAGE_COVERAGE','state':'SCOPED_READ_ONLY_RECORD_COVERAGE_COMPLETE__EXPANDING_BINDING_UNOBSERVED',
            'aggregate_25_output_records':7000,'native_stage_observed_records':1,'remaining_native_stage_observation_records':6999,
            'observation_record_selection':{'level':0,'line':0,'t0_s':0,'dt_s':1e9,'source':'verified F04E first-record probe, no rerun'},
            'native_stage_observation_coverage':[{'level':0,'records':1},{'level':1,'records':0},{'level':2,'records':0}],
            'first_record_stage_views':static_stage_views(c,record,obs),'owner_contract':owner_contract(root),
            'new_native_runs':0,'new_root_refinements':0,'new_history_runs':0,'new_certificate_checker_runs':0,
            'inherited_F04E_native_binary_sha256':execution['binary_sha256'],
            'inherited_F04E_compiler_sha256':execution['rustc_sha256'],'inherited_native_binary_locally_executed':False,
            'unverified':{'native_FP_derivatives':None,'uniform_event_escape_remainders':None,'expanding_stage_owner_binding':None,'physical_fit_error':None},
            'next_optional_task':'OWNER_STAGE_LOG_CONTRACT_OR_EVENT_OBSERVABLE_ENCLOSURE_USING_EXISTING_ROOT_BOXES',
            'new_mandatory_gate':False,'physical_production':'HOLD','actual_CR_dispatch_counts':None,'independent_review':'NOT_PERFORMED'}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=analyze(a.root)
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ['state','aggregate_25_output_records','native_stage_observed_records','new_native_runs']}))
