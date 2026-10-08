"""One-shot A1 execution, intrinsic-only and saved reassembly; raw cross cap=0."""
from __future__ import annotations
import argparse,json,math,os,resource,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from gram_exact import sha,digest,load_bank,exact_moments,mp_inverse_moments
from intrinsic_blocks import assemble_intrinsic,boost_blocks
from native import Native
from reassemble_saved import collect_saved,join_metric,join_blocks,write_json,write_npz,verify_seal
import stencil_math as sm

def norms(a):
    return {'spectral':float(np.linalg.norm(a,2)),'frobenius':float(np.linalg.norm(a,'fro')),'elementwise_max':float(np.max(abs(a)))}
def compare(a,b,atol):
    d=norms(a-b);return {**d,'pass':all(x<=atol for x in d.values()),'atol':atol}
def exact_strings(m):return {k:[[str(x) for x in row] for row in value] for k,value in m.items()}

def main(args):
    started=time.time();contract=json.loads(Path(args.contract).read_text());binding=json.loads(Path(args.context).read_text());expected=dict(binding);cid=expected.pop('context_id')
    if digest(expected)!=cid or sha(args.contract)!=binding['contract_sha256']:raise ValueError('new context/contract binding mismatch')
    for name,value in binding['new_sources'].items():
        if sha(Path(__file__).parent/name)!=value:raise ValueError('new source pin mismatch: '+name)
    if sha(args.native)!=binding['native_build_sha256']:raise ValueError('new native build mismatch')
    if contract['raw_cross_call_cap']!=0 or contract['reassembled_record_cap']!=34:raise ValueError('invalid A1 execution scope')
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    write_json(out/'STARTED.json',{'context_id':cid,'epoch':started,'attempt':1,'new_cross_calls':0,'pid':os.getpid(),'affinity':sorted(os.sched_getaffinity(0))})
    def checkpoint():
        if time.time()-started>contract['maximum_wall_seconds']:raise TimeoutError('stage wall budget exceeded')
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024>contract['maximum_rss_bytes']:raise MemoryError('stage RSS budget exceeded')
    try:
        intake=Path(args.intake);root=intake/'payload';oldsource=root/'worktree/research/gap_closure_20261001/g02_continuous_basis_20261002'
        bank=load_bank(root/'archive_base_2/runs_r4x/candidate_v1',contract,oldsource)
        oldcontext,records=collect_saved(intake,contract);checkpoint()
        kernel=Native(args.native);exact,coeff=exact_moments(bank.edges,bank.endpoints,bank.bubbles)
        oracle={k:np.array(v,float) for k,v in exact.items()}
        mp90=mp_inverse_moments(bank.edges,coeff,90);mp120=mp_inverse_moments(bank.edges,coeff,120)
        native5=kernel.moments(bank.edges,bank.endpoints,bank.bubbles,5)
        fixed32=kernel.moments(bank.edges,bank.endpoints,bank.bubbles,32)
        primary={**fixed32,'G':native5['G']};oracle.update({k:mp120[k] for k in ('R1','R2')})
        ci=bank.channel_modes;lm=bank.channel_lm;I=assemble_intrinsic(primary,ci,lm);O=assemble_intrinsic(oracle,ci,lm)
        terr=contract['targets'];gerr=[[F(float(primary['G'][a,b]))-exact['G'][a][b] for b in range(len(bank.modes))] for a in range(len(bank.modes))]
        max_exact=max(abs(x) for row in gerr for x in row)
        # Exact rational Gershgorin bounds on the 9-channel intrinsic metric.
        cg=[[exact['G'][a][b] if lm[i]==lm[j] else F(0) for j,b in enumerate(ci)] for i,a in enumerate(ci)]
        lower=min(cg[i][i]-sum(abs(cg[i][j]) for j in range(len(ci)) if i!=j) for i in range(len(ci)))
        upper=max(cg[i][i]+sum(abs(cg[i][j]) for j in range(len(ci)) if i!=j) for i in range(len(ci)))
        moment_error={k:float(np.max(abs(primary[k]-oracle[k]))) for k in primary}
        intrinsic_error={k:float(np.max(abs(I[k]-O[k]))) for k in I}
        skew=max(float(np.linalg.norm(x+x.conj().T,'fro')) for x in I['A'])
        gram_frob=float(np.linalg.norm(primary['G']-oracle['G'],'fro'))
        checks={'exact_J_integration_by_parts':all(exact['J'][a][b]+exact['J'][b][a]==0 for a in range(len(bank.modes)) for b in range(len(bank.modes))),
                'gram_exact_max':max_exact<=F(terr['gram_max_abs']),'gram_frobenius':gram_frob<=terr['gram_frobenius'],
                'radial_moments':max(moment_error.values())<=terr['radial_moment_max_abs'],
                'intrinsic_blocks':max(intrinsic_error.values())<=terr['intrinsic_H0_A_max_abs'],
                'raw_A_skew':skew<=terr['intrinsic_A_skew_frobenius'],
                'mp90_120_rounded_agreement':all(np.array_equal(mp90[k],mp120[k]) for k in ('R1','R2')),
                'positive_intrinsic_metric_exact':lower>0}
        # No data-dependent correction is made if these comparisons fail.
        write_json(out/'GRAM_EXACT.json',{'schema':'R4AB_EXACT_POLYNOMIAL_MOMENTS_V1','candidate':bank.identity,'matrices_exact':exact_strings(exact),'gram_rounding_errors_exact':[[str(x) for x in row] for row in gerr],'gram_max_error_exact':str(max_exact),'gershgorin_lower_exact':str(lower),'gershgorin_upper_exact':str(upper),'exact_edge_difference':True,'stored_fp64_defines_exact_function':True})
        write_json(out/'INTRINSIC_CHECK.json',{'checks':checks,'all_pass':all(checks.values()),'gram_max_abs_error':float(max_exact),'gram_frobenius_difference_to_rounded_oracle':gram_frob,'radial_moment_max_abs_errors':moment_error,'intrinsic_block_max_abs_errors':intrinsic_error,'A_skew_frobenius_max':skew,'inverse_moments_precision_check':'90/120 digits, not an interval certificate','gershgorin_lower':float(lower),'gershgorin_upper':float(upper),'gram_offdiagonal_max':float(np.max(abs(I['S']-np.diag(np.diag(I['S']))))),'gram_diagonal_defect_max':float(np.max(abs(np.diag(I['S'])-1))),'exact_G_equals_identity':all(cg[i][j]==F(int(i==j)) for i in range(len(ci)) for j in range(len(ci)))})
        write_json(out/'INVERSE_MOMENTS_120.json',mp120['decimal'])
        write_npz(out/'INTRINSIC.npz',{**I,**{'exact_rounded_'+k:v for k,v in O.items()},**{'radial_'+k:v for k,v in primary.items()}})
        write_json(out/'CACHE_RECORD.json',{'context_id':cid,'candidate':bank.identity,'intrinsic_npz_sha256':sha(out/'INTRINSIC.npz'),'exact_oracle_sha256':sha(out/'GRAM_EXACT.json'),'native_sha256':binding['native_build_sha256'],'keys':['candidate','ordered_channels','own_charge','algorithm','quadrature','source','native'],'excluded_geometry_keys':['R','z','time','other_charge'],'runtime_arrays_immutable':True,'channel_records':list(bank.channel_records)})
        if not all(checks.values()):raise ArithmeticError('intrinsic preassembly gate failed')
        checkpoint()
        # S-only phase. NPZ access is lazy: neither archived H/D nor V is loaded.
        index={rule:{} for rule in sm.RULES};s_only={};sample_bindings=[];old_same_variation=0.
        for rec in records:
            with np.load(rec['path']/'RAW.npz',allow_pickle=False) as z:
                s=join_metric(I['S'],I['S'],z['S_tp'],z['S_pt'])
            with np.load(rec['path']/'FULL.npz',allow_pickle=False) as z:
                old_s=z['S'];old_same_variation=max(old_same_variation,float(np.max(abs(s[:9,:9]-old_s[:9,:9]))))
            s_only[rec['key']]=s
            sample_bindings.append({'key':rec['key'],'raw_sha256':rec['receipt']['raw_sha256'],'full_parent_sha256':rec['receipt']['full_sha256'],'geometry':rec['geometry'],'source_path':str(rec['path'].relative_to(intake))})
            task=rec['task']
            if task['moment_backend']=='fortran':index[(task['order'],task['inner_phase_budget'])][task['z_hex']]=rec
        derivatives={};details={}
        for rule,values in index.items():
            if set(values)!=set(z.hex() for z in sm.Z_VALUES):raise ValueError('incomplete stencil')
            label=f'q{rule[0]}_beta{rule[1]}';samples={zh:s_only[r['key']] for zh,r in values.items()};times={zh:r['geometry']['time_ta'] for zh,r in values.items()}
            ladder=sm.ladder_at_center(samples);windows=[]
            for j in (0,1):
                ld=ladder[j:j+4];a=sm.r8_nominal(ld,oldcontext['speed_a0_per_ta']);b=sm.r8_recursive(ld,oldcontext['speed_a0_per_ta']);act,certificate=sm.actual_time_probe(samples,times,[x[0] for x in ld],oldcontext['speed_a0_per_ta'])
                for name,arr in [('nominal',a),('recursive',b),('actual_time',act)]:derivatives[f'{label}__w{j}__{name}']=arr
                windows.append({'H_a0':ld[0][0],'nominal_vs_recursive':compare(a,b,sm.ATOL),'nominal_vs_actual_time':compare(a,act,sm.ATOL),'actual_time_certificate':certificate,'samecenter_derivative_max':float(max(np.max(abs(a[:9,:9])),np.max(abs(a[9:,9:]))))})
            details[label]={'windows':windows,'window_agreement':compare(derivatives[f'{label}__w0__nominal'],derivatives[f'{label}__w1__nominal'],sm.ATOL)}
        write_npz(out/'S_ONLY_SAMPLES.npz',s_only);write_npz(out/'S_ONLY_DERIVATIVES.npz',derivatives)
        write_json(out/'S_ONLY_SEAL.json',{'context_id':cid,'epoch':time.time(),'D_read_in_S_phase':False,'samples_sha256':sha(out/'S_ONLY_SAMPLES.npz'),'derivatives_sha256':sha(out/'S_ONLY_DERIVATIVES.npz'),'intrinsic_sha256':sha(out/'INTRINSIC.npz'),'details':details,'sample_bindings':sample_bindings,'fixed_h_and_weights_inherited':True,'geometry_count':11,'new_raw_cross_calls':0})
        seal=verify_seal(out,cid);first_D_read=time.time();checkpoint()
        # Post-seal H/D assembly. Saved V_other and all six raw cross arrays unchanged.
        fullroot=out/'reassembled';fullroot.mkdir();all_diag=[];direct={};old_changes=[]
        for rec in records:
            checkpoint();dest=fullroot/rec['key'];dest.mkdir()
            with np.load(rec['path']/'RAW.npz',allow_pickle=False) as z:cross={k:z[k].copy() for k in z.files}
            with np.load(rec['path']/'FULL.npz',allow_pickle=False) as z:old={k:z[k].copy() for k in z.files}
            for label,indices in [('T',np.arange(9)),('P',np.arange(9,18))]:
                if not np.array_equal(old[label+'__indices'],indices):raise ValueError('ordered-channel mismatch')
            geo=rec['geometry'];bs=[]
            for label,v in zip(('T','P'),geo['trajectory']['velocities']):bs.append(boost_blocks(I['S'],I['H0'],I['A'],old[label+'__V_other'],v))
            full=join_blocks(bs[0],bs[1],cross)
            if not np.array_equal(full['S'],s_only[rec['key']]):raise ArithmeticError('postseal metric mismatch')
            diagnostics={name+'_hermiticity_relative':float(np.linalg.norm(full[name]-full[name].conj().T)/max(np.linalg.norm(full[name]),1e-300)) for name in ('S','H')}
            ev=np.linalg.eigvalsh(full['S']);diagnostics.update(metric_min=float(ev[0]),metric_max=float(ev[-1]),metric_ratio=float(ev[0]/ev[-1]))
            cross_unchanged=all(np.array_equal(full[name][:9,9:],cross[name+'_tp']) and np.array_equal(full[name][9:,:9],cross[name+'_pt']) for name in ('S','H','D'))
            diagnostics['cross_values_bitwise_unchanged']=cross_unchanged
            diagnostics['V_other_values_bitwise_unchanged']=all(np.array_equal(bs[i]['V_other'],old[label+'__V_other']) for i,label in enumerate(('T','P')))
            diagnostics['pass']=bool(cross_unchanged and diagnostics['V_other_values_bitwise_unchanged'] and diagnostics['metric_ratio']>=terr['metric_min_max_ratio'] and max(diagnostics['S_hermiticity_relative'],diagnostics['H_hermiticity_relative'])<=terr['metric_hermiticity_relative'])
            if not diagnostics['pass']:raise ArithmeticError('new assembly screen failed')
            arr=dict(full)
            for label,bb,ids in zip(('T','P'),bs,(np.arange(9),np.arange(9,18))):
                arr.update({label+'__'+k:v for k,v in bb.items()});arr[label+'__indices']=ids
            write_npz(dest/'FULL.npz',arr)
            write_json(dest/'RESULT.json',{'context_id':cid,'parent_raw_sha256':rec['receipt']['raw_sha256'],'parent_full_sha256':rec['receipt']['full_sha256'],'new_full_sha256':sha(dest/'FULL.npz'),'geometry':geo,'task':rec['task'],'cache_sha256':sha(out/'INTRINSIC.npz'),'diagnostics':diagnostics})
            all_diag.append({'key':rec['key'],**diagnostics});old_changes.append({'key':rec['key'],**{k:norms(full[k]-old[k]) for k in ('S','H','D')}})
            if rec['task']['moment_backend']=='fortran' and rec['task']['z_a0']==sm.CENTER:direct[(rec['task']['order'],rec['task']['inner_phase_budget'])]=full['D']+full['D'].conj().T
        residuals={};cross_rules=[]
        for rule in sm.RULES:
            lab=f'q{rule[0]}_beta{rule[1]}'
            residuals[lab]=[compare(derivatives[f'{lab}__w{j}__nominal'],direct[rule],sm.ATOL) for j in (0,1)]
        for i,rule in enumerate(sm.RULES):
            for other in sm.RULES[i+1:]:
                for j in (0,1):
                    a=f'q{rule[0]}_beta{rule[1]}';b=f'q{other[0]}_beta{other[1]}'
                    cross_rules.append({'a':a,'b':b,'window':j,**compare(derivatives[f'{a}__w{j}__nominal'],derivatives[f'{b}__w{j}__nominal'],sm.ATOL)})
        passed=all(row['pass'] for rows in residuals.values() for row in rows) and all(d['window_agreement']['pass'] for d in details.values()) and all(x['pass'] for x in cross_rules) and all(w['nominal_vs_recursive']['pass'] and w['nominal_vs_actual_time']['pass'] and w['actual_time_certificate']['moments_pass'] for d in details.values() for w in d['windows'])
        result={'schema':'BASS_R4AB_SAVED_REASSEMBLY_RESULT_V1','node':'A1','context_id':cid,'candidate':bank.identity,'status':'R4AB_INTRINSIC_AND_LOCAL_R8_EMPIRICAL_PASS' if passed else 'R4AB_INTRINSIC_CLOSED_LOCAL_R8_TARGET_NOT_MET','A1_intrinsic_pass':all(checks.values()),'local_derivative_empirical_pass':passed,'historical_R4AA_status':'LOCAL_OFFCENTRAL_DERIVATIVE_TARGET_NOT_MET','historical_result_sha256':contract['parent_result_sha256'],'seal_precedes_first_D_read':seal['epoch']<=first_D_read,'first_D_read_epoch':first_D_read,'S_only_seal_sha256':sha(out/'S_ONLY_SEAL.json'),'residuals':residuals,'window_agreement':{k:v['window_agreement'] for k,v in details.items()},'cross_rule_agreement':cross_rules,'assembly_screens':all_diag,'old_to_new_full_changes':old_changes,'samecenter_derivative_max':max(w['samecenter_derivative_max'] for v in details.values() for w in v['windows']),'new_cross_queries':0,'new_Vother_queries':0,'saved_records_reassembled':len(records),'R4Z_calculations_and_tests_rerun':0,'R4AA_calculations_and_tests_rerun':0,'limitations':['Candidate-specific finite-panel exact Gram only','H0/A error comparison is not an interval certificate','Saved V_other has no new independent refinement','No C9 or continuous trajectory error certificate','No original eight-point gate closure','No capture, basis enlargement, b grid or physical rate'],'claim_ceiling':contract['claim_ceiling'],'wall_seconds':time.time()-started,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        checkpoint();write_json(out/'RESULT.json',result)
        write_json(out/'COMPLETED.json',{'context_id':cid,'result_sha256':sha(out/'RESULT.json'),'status':result['status'],'new_cross_calls':0,'records_reassembled':len(records)})
        print(json.dumps({k:result[k] for k in ['status','samecenter_derivative_max','saved_records_reassembled','wall_seconds','peak_rss_kib']},indent=2))
        print(json.dumps({'gram':float(max_exact),'moment_errors':moment_error,'A_skew':skew,'residuals':residuals,'window_agreement':result['window_agreement']},indent=2))
    except Exception as e:
        write_json(out/'FAILED.json',{'context_id':cid,'error_type':type(e).__name__,'message':str(e),'new_cross_calls':0,'elapsed_seconds':time.time()-started,'automatic_retry':False})
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('intake','out','contract','context','native'):p.add_argument('--'+name,required=True)
    main(p.parse_args())
