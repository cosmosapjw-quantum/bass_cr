"""Resolution-qualified policy reused unchanged, with alias provenance."""
import qualification_runtime as qr


def _specs(family,z,rule,contract):
    eps=float(contract.get('epsilon_z_a0',1e-4));q=rule['order'];h=rule['subdivisions']
    return [{'family':family,'order':q,'integration_subdivisions':h,'z_center_a0':float(z),'dz_a0':float(dz)} for dz in (-eps,0.,eps)]


def execute_geometry_policy(z,contract,epsilon_t,ensure_rows,progress=None):
    plan=qr.resolution_plan(contract,'reference');reference_rows=[];receipt=None
    groups=[plan[:2]]+[[r] for r in plan[2:]]
    for group in groups:
        specs=[]
        for r in group:specs.extend(_specs('reference',z,r,contract))
        reference_rows.extend(ensure_rows(specs))
        receipt=qr.qualify_reference_ladder(reference_rows,epsilon_t,contract)
        if progress:progress(event='reference_assessed',z_a0=z,status=receipt['status'],attempted_resolutions=receipt['attempted_resolutions'])
        if receipt['status']=='REFERENCE_QUALIFIED':break
    if receipt['status']!='REFERENCE_QUALIFIED':
        return {'status':'REFERENCE_CONVERGENCE_UNRESOLVED','z_a0':float(z),'qualified_reference_order':None,
                'qualified_reference_subdivisions':None,'reference_qualification':receipt,
                'failed_screens':['reference convergence unresolved'],'candidate_evaluated':False,'capture_execution_allowed':False}
    q=receipt['qualified_order'];h=receipt['qualified_subdivisions']
    selected=[r for r in reference_rows if r.get('reference_order')==q and r.get('integration_subdivisions',1)==h]
    attempts=[]
    for cr in qr.resolution_plan(contract,'candidate'):
        cq,ch=cr['order'],cr['subdivisions'];rows=ensure_rows(_specs('candidate',z,cr,contract))
        result=qr.qualify_candidate_against_reference(z,rows,selected,epsilon_t,contract,q,cq)
        alias=all(a.get('numerical_task_id')==b.get('numerical_task_id') for a,b in zip(sorted(rows,key=lambda r:r['dz_a0']),sorted(selected,key=lambda r:r['dz_a0'])))
        if alias:
            result['candidate_vs_reference']['evidence_relation']='ALIASED_SAME_NUMERICAL_TASK_NOT_INDEPENDENT_CROSSCHECK'
        else:
            result['candidate_vs_reference']['evidence_relation']='INDEPENDENT_NUMERICAL_TASK_COMPARISON'
        result.update(qualified_reference_subdivisions=h,qualified_candidate_subdivisions=ch,candidate_reference_alias=alias)
        attempts.append({'candidate_order':cq,'integration_subdivisions':ch,'candidate':result['candidate'],
                         'candidate_vs_reference':result['candidate_vs_reference'],'candidate_reference_alias':alias,
                         'failed_screens':result['failed_screens']})
        if progress:progress(event='candidate_assessed',z_a0=z,order=cq,subdivisions=ch,alias=alias,
            connection=result['candidate']['connection_relative'],raw_difference=result['candidate_vs_reference']['max_raw_cross_relative_difference'],failed_screens=result['failed_screens'])
        if not result['failed_screens']:
            result.update(reference_qualification=receipt,candidate_attempts=attempts)
            return result
    return {'status':'CANDIDATE_CONVERGENCE_UNRESOLVED','z_a0':float(z),'qualified_reference_order':q,
            'qualified_reference_subdivisions':h,'qualified_candidate_order':None,'reference_qualification':receipt,
            'candidate_attempts':attempts,'failed_screens':['candidate finite quadrature budget exhausted'],
            'capture_execution_allowed':False}


def sequence_geometries(z_samples,execute):
    rows=[];first=None
    for z in z_samples:
        row=execute(float(z));rows.append(row)
        if row.get('status')=='REFERENCE_CONVERGENCE_UNRESOLVED':first={'kind':'reference','z_a0':float(z),'failed_screens':list(row.get('failed_screens',[]))};break
        if row.get('status')=='CANDIDATE_CONVERGENCE_UNRESOLVED':first={'kind':'candidate','z_a0':float(z),'failed_screens':list(row.get('failed_screens',[]))};break
        if row.get('failed_screens'):first={'kind':'numerical','z_a0':float(z),'failed_screens':list(row['failed_screens'])};break
    return rows,first
