"""One-shot, source-pinned R4AC certificate and saved H-only reassembly."""
from __future__ import annotations
import argparse,json,math,os,resource,signal,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from dyadic_interval import Interval as I,error_upper,upward_float,BITS,LOG_TERMS
from vother_certificate import PolynomialBank,geometry_interval,projected_matrix
from native_vother import Native,angular_matrix
from reassemble_vother import reassemble,CHANGED
from runtime_contract import sha,digest,verify_pins,read_inputs,write_json,write_npz

def matrix_bounds(a,truth):
    rows=[[error_upper(complex(a[i,j]),truth[i][j]) for j in range(len(a))] for i in range(len(a))]
    upper=max(x for row in rows for x in row)
    frob=I.point(sum((x*x for row in rows for x in row),F(0))).sqrt().fractions()[1]
    width=max(x.width() for row in truth for x in row)
    return {'component_upper_exact':str(upper),'component_upper_Eh':upward_float(upper),
            'frobenius_upper_exact':str(frob),'frobenius_upper_Eh':upward_float(frob),
            'certificate_max_width_exact':str(width),'certificate_max_width_Eh':upward_float(width)}

def run(root,out):
    root,out=Path(root).resolve(),Path(out).resolve()
    contract=json.loads((root/'contracts/EXECUTION_CONTRACT.json').read_text())
    context=json.loads((root/'contracts/CONTEXT.json').read_text());body=dict(context);cid=body.pop('context_id')
    if digest(body)!=cid or sha(root/'contracts/EXECUTION_CONTRACT.json')!=context['contract_sha256']:raise ValueError('execution contract/context mismatch')
    verify_pins(root,context['source_pins'])
    if sha(root/'native/build/BUILD.json')!=context['native_build_sha256']:raise ValueError('build manifest mismatch')
    out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();counts={'primary_GL32':0,'refinement_GL48':0,'certified_geometry':0,'raw_cross':0,'old_Vother_reruns':0}
    write_json(out/'STARTED.json',{'context_id':cid,'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'attempt':1,'counts':counts})
    def timed_out(signum,frame):raise TimeoutError('stage wall limit reached')
    signal.signal(signal.SIGALRM,timed_out);signal.alarm(contract['caps']['stage_wall_seconds'])
    def checkpoint():
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024>contract['caps']['stage_rss_bytes']:raise MemoryError('stage RSS budget exceeded')
        if time.monotonic()-start>contract['caps']['stage_wall_seconds']:raise TimeoutError('wall budget exceeded')
    try:
        if any(os.environ.get(k)!='1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')):raise ValueError('single-thread runtime contract required')
        maxmem=int(Path('/sys/fs/cgroup/memory.max').read_text());current=int(Path('/sys/fs/cgroup/memory.current').read_text())
        if maxmem-current<contract['caps']['memory_reserve_bytes']+contract['caps']['stage_rss_bytes']:raise MemoryError('not enough admitted RAM plus reserve')
        resource.setrlimit(resource.RLIMIT_AS,(contract['caps']['stage_rss_bytes'],contract['caps']['stage_rss_bytes']))
        bank,meta,lm,ix,cache,records,groups=read_inputs(root,contract)
        e,p,q=bank['edges'],bank['shared_endpoint_values'],bank['bubble_coefficients']
        if np.any(p[:,0]!=0) or np.any(p[:,-1]!=0):raise ValueError('candidate Dirichlet traces changed')
        polynomial=PolynomialBank(e,p,q);native=Native(root/'native/build/BUILD.json')
        target=contract['targets'];geo_results=[];record_results=[]
        potroot=out/'potentials';potroot.mkdir();recroot=out/'reassembled';recroot.mkdir()
        for key,group in sorted(groups.items()):
            checkpoint();dout=potroot/key;dout.mkdir();rec0=group[0][1];geo=rec0['geometry']
            centers=np.array(geo['actual_centers_a0'],float);delta=centers[1]-centers[0]
            write_json(dout/'STARTED.json',{'context_id':cid,'geometry':geo,'methods':['GL32','GL48','integer_interval_320'],'raw_cross_cap':0})
            R,n=geometry_interval(delta);rf=math.sqrt(float(delta@delta))
            counts['primary_GL32']+=1;primary=native.radial(e,p,q,rf,32)
            counts['refinement_GL48']+=1;refined=native.radial(e,p,q,rf,48)
            counts['certified_geometry']+=1;truth=polynomial.radial(R)
            pots={};certs={};checks={};potdata={'radial_GL32':primary,'radial_GL48':refined}
            for c,lab in enumerate(('T','P')):
                dr=delta if c==0 else -delta;direction=n if c==0 else [-x for x in n]
                pots[lab]=angular_matrix(primary,lm,ix,dr,geo['trajectory']['charges'][1-c])
                ref=angular_matrix(refined,lm,ix,dr,geo['trajectory']['charges'][1-c])
                certs[lab]=projected_matrix(truth,lm,ix,direction,geo['trajectory']['charges'][1-c])
                bound=matrix_bounds(pots[lab],certs[lab]);difference=float(np.max(abs(pots[lab]-ref)))
                passed=(F(bound['component_upper_exact'])<=F(target['FP64_component_error_upper_Eh']) and F(bound['frobenius_upper_exact'])<=F(target['FP64_Frobenius_error_upper_Eh']) and F(bound['certificate_max_width_exact'])<=F(target['certificate_component_width_Eh']) and difference<=target['refinement_component_difference_Eh'])
                checks[lab]={**bound,'GL32_vs_GL48_component_difference_Eh':difference,'pass':passed}
                potdata[lab+'__V32']=pots[lab];potdata[lab+'__V48']=ref
            write_npz(dout/'POTENTIALS.npz',potdata)
            certificate={'schema':'R4AC_EXACT_CANDIDATE_SAMPLE_ENCLOSURE_V1','context_id':cid,'candidate':meta['identity'],'geometry':geo,'fractional_bits':BITS,'log_terms':LOG_TERMS,'R_bounds_exact':R.record(),'radial':[[[x.record() for x in row] for row in matrix] for matrix in truth],'potentials_real':{lab:[[x.record() for x in row] for row in mat] for lab,mat in certs.items()},'potentials_imaginary':'exact_zero_for_registered_xz_plane','claim':'finite stored real candidate at exact stored binary64 center coordinates; not continuous geometry nor physical model error','checks':checks}
            write_json(dout/'CERTIFICATE.json',certificate)
            if not all(x['pass'] for x in checks.values()):raise ArithmeticError('predeclared V_other target not met at '+key)
            for d,rec in group:
                checkpoint()
                with np.load(d/'FULL.npz',allow_pickle=False) as z:old={k:z[k].copy() for k in z.files}
                new=reassemble(old,pots,geo['trajectory']['velocities'])
                unchanged={k:np.array_equal(new[k],old[k]) for k in old if k not in CHANGED}
                herm=float(np.linalg.norm(new['H']-new['H'].conj().T)/max(np.linalg.norm(new['H']),1e-300))
                cross_unchanged=all(np.array_equal(new[k][s1,s2],old[k][s1,s2]) for k in ('S','H','D') for s1,s2 in ((slice(0,9),slice(9,18)),(slice(9,18),slice(0,9))))
                older={lab:matrix_bounds(old[lab+'__V_other'],certs[lab]) for lab in ('T','P')}
                deltaH={lab:float(np.max(abs(new[lab+'__H']-old[lab+'__H']))) for lab in ('T','P')}
                record={'key':d.name,'context_id':cid,'parent_full_sha256':sha(d/'FULL.npz'),'geometry':geo,'potential_certificate_sha256':sha(dout/'CERTIFICATE.json'),'S_D_H0_A_and_indices_bitwise_unchanged':all(unchanged.values()),'all_six_cross_blocks_bitwise_unchanged':cross_unchanged,'H_hermiticity_relative':herm,'old_order20_error_bounds':older,'H_component_change_Eh':deltaH,'pass':bool(all(unchanged.values()) and cross_unchanged and herm<=target['full_H_hermiticity_relative'])}
                if not record['pass']:raise ArithmeticError('H-only reassembly failed at '+d.name)
                dest=recroot/d.name;dest.mkdir();write_npz(dest/'FULL.npz',new);record['new_full_sha256']=sha(dest/'FULL.npz');write_json(dest/'RESULT.json',record);record_results.append(record)
            completed={'key':key,'context_id':cid,'certificate_sha256':sha(dout/'CERTIFICATE.json'),'potential_npz_sha256':sha(dout/'POTENTIALS.npz'),'checks':checks,'records':len(group),'counts':dict(counts)}
            write_json(dout/'COMPLETED.json',completed);geo_results.append(completed)
            print(json.dumps({'geometry':key,'new_component_upper_Eh':max(x['component_upper_Eh'] for x in checks.values()),'certificate_width_Eh':max(x['certificate_max_width_Eh'] for x in checks.values()),'elapsed_seconds':time.monotonic()-start}),flush=True)
        newchecks=[c for g in geo_results for c in g['checks'].values()]
        oldchecks=[c for g in record_results for c in g['old_order20_error_bounds'].values()]
        result={'schema':'BASS_R4AC_VOTHER_RESULT_V1','context_id':cid,'node':'A2/R4AC','status':'R4AC_SAMPLE_VOTHER_CERTIFIED_AND_H_ONLY_REASSEMBLY_PASS','candidate':meta['identity'],'parent_R4AB_result_sha256':sha(root/'inputs/R4AB_RESULT.json'),'counts':counts,'geometries_completed':len(geo_results),'center_certificates':2*len(geo_results),'records_reassembled':len(record_results),'new_component_error_upper_Eh':max(c['component_upper_Eh'] for c in newchecks),'new_frobenius_error_upper_Eh':max(c['frobenius_upper_Eh'] for c in newchecks),'max_certificate_component_width_Eh':max(c['certificate_max_width_Eh'] for c in newchecks),'GL32_GL48_max_component_difference_Eh':max(c['GL32_vs_GL48_component_difference_Eh'] for c in newchecks),'old_order20_component_error_upper_Eh':max(c['component_upper_Eh'] for c in oldchecks),'old_order20_frobenius_error_upper_Eh':max(c['frobenius_upper_Eh'] for c in oldchecks),'full_H_hermiticity_relative_max':max(c['H_hermiticity_relative'] for c in record_results),'H_component_change_Eh':max(c for g in record_results for c in g['H_component_change_Eh'].values()),'S_D_H0_A_cross_unchanged':True,'old_R4Z_R4AA_R4AB_test_or_calculation_replays':0,'S_only_derivative_analysis_replays':0,'point_certificate_not_global':True,'physical_candidate_adoption':False,'geometry_records':geo_results,'record_results':record_results,'wall_seconds':time.monotonic()-start,'peak_rss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'ceiling':contract['ceiling']}
        verify_pins(root,json.loads((root/'contracts/INPUT_PINS.json').read_text()))
        checkpoint();write_json(out/'RESULT.json',result);write_json(out/'COMPLETED.json',{'context_id':cid,'result_sha256':sha(out/'RESULT.json'),'status':result['status'],'counts':counts})
        print(json.dumps({k:v for k,v in result.items() if k not in ('geometry_records','record_results')},indent=2),flush=True)
    except Exception as e:
        write_json(out/'FAILED.json',{'context_id':cid,'error_type':type(e).__name__,'error':str(e),'counts':counts,'elapsed_seconds':time.monotonic()-start,'automatic_retry':False})
        raise
    finally:signal.alarm(0)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.root,a.out)
