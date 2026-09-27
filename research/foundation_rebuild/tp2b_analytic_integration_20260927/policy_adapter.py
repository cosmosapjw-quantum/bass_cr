"""TP2B-owned resolution policy with alias provenance.

The TP2B integration contract owns the ordered reference/candidate resolution
ladders. We reuse only the stable low-level matrix/connection helpers from the
TP2A runtime; no upstream resolution-plan API is assumed.
"""
import qualification_runtime as qr


def resolution_plan(contract, family):
    if family not in ('reference', 'candidate'):
        raise ValueError('family must be reference or candidate')
    key = family + '_resolutions'
    rows = contract.get(key)
    if rows is None:
        orders = contract['reference_orders'] if family == 'reference' else contract['candidate_orders']
        rows = [{'order': q, 'subdivisions': 1} for q in orders]
    if not isinstance(rows, list) or len(rows) < (2 if family == 'reference' else 1):
        raise ValueError('finite resolution ladder required')
    out = []; seen = set()
    for row in rows:
        q = row.get('order'); h = row.get('subdivisions')
        if type(q) is not int or not 2 <= q <= 64:
            raise ValueError('bounded resolution order required')
        if type(h) is not int or h not in (1, 2, 4):
            raise ValueError('subdivisions must be 1,2,4')
        pair = (q, h)
        if pair in seen:
            raise ValueError('duplicate resolution rule')
        seen.add(pair); out.append({'order': q, 'subdivisions': h})
    return out


def _specs(family,z,rule,contract):
    eps=float(contract.get('epsilon_z_a0',1e-4));q=rule['order'];h=rule['subdivisions']
    return [{'family':family,'order':q,'integration_subdivisions':h,'z_center_a0':float(z),'dz_a0':float(dz)} for dz in (-eps,0.,eps)]


def _qualify_reference_resolutions(rows, epsilon_t, contract):
    screens=contract['screens'];plan=resolution_plan(contract,'reference')
    receipts={};attempted=[];previous=None;qualified_order=None;qualified_subdivisions=None
    for rule in plan:
        q,h=rule['order'],rule['subdivisions']
        subset=[r for r in rows if r.get('method')=='reference' and r.get('reference_order')==q and r.get('integration_subdivisions',1)==h]
        if len(subset)!=3:break
        rec=qr._connection_receipt(subset,epsilon_t,screens)
        attempted.append({'order':q,'subdivisions':h})
        rec.update(reference_order=q,integration_subdivisions=h,previous_raw_cross_relative_max=None,
                   previous_raw_cross_relative_differences=None,raw_cross_convergence_pass=None)
        if previous is not None:
            diff,detail=qr._stencil_cross_relative_max(previous['rows'],subset)
            rec['previous_raw_cross_relative_max']=diff
            rec['previous_raw_cross_relative_differences']=detail
            rec['raw_cross_convergence_pass']=diff<=screens['raw_cross_relative_max']
            p=previous['receipt']
            if (p['connection_pass'] and p['hermiticity_pass'] and p['metric_pass']
                    and rec['connection_pass'] and rec['hermiticity_pass'] and rec['metric_pass']
                    and rec['raw_cross_convergence_pass']):
                qualified_order,qualified_subdivisions=q,h
                receipts[f'q{q}_h{h}']=rec;break
        receipts[f'q{q}_h{h}']=rec
        previous={'rows':subset,'receipt':rec}
    status='REFERENCE_QUALIFIED' if qualified_order is not None else 'REFERENCE_CONVERGENCE_UNRESOLVED'
    return {'status':status,'qualified_order':qualified_order,'qualified_subdivisions':qualified_subdivisions,
            'attempted_resolutions':attempted,'resolutions':receipts,'candidate_evaluated':False}


def execute_geometry_policy(z,contract,epsilon_t,ensure_rows,progress=None):
    plan=resolution_plan(contract,'reference');reference_rows=[];receipt=None
    groups=[plan[:2]]+[[r] for r in plan[2:]]
    for group in groups:
        specs=[]
        for r in group:specs.extend(_specs('reference',z,r,contract))
        reference_rows.extend(ensure_rows(specs))
        receipt=_qualify_reference_resolutions(reference_rows,epsilon_t,contract)
        if progress:progress(event='reference_assessed',z_a0=z,status=receipt['status'],attempted_resolutions=receipt['attempted_resolutions'])
        if receipt['status']=='REFERENCE_QUALIFIED':break
    if receipt['status']!='REFERENCE_QUALIFIED':
        return {'status':'REFERENCE_CONVERGENCE_UNRESOLVED','z_a0':float(z),'qualified_reference_order':None,
                'qualified_reference_subdivisions':None,'reference_qualification':receipt,
                'failed_screens':['reference convergence unresolved'],'candidate_evaluated':False,'capture_execution_allowed':False}
    q=receipt['qualified_order'];h=receipt['qualified_subdivisions']
    selected=[r for r in reference_rows if r.get('reference_order')==q and r.get('integration_subdivisions',1)==h]
    attempts=[]
    for cr in resolution_plan(contract,'candidate'):
        cq,ch=cr['order'],cr['subdivisions'];rows=ensure_rows(_specs('candidate',z,cr,contract))
        result=qr.qualify_candidate_against_reference(z,rows,selected,epsilon_t,contract,q,cq)
        alias=all(a.get('numerical_task_id')==b.get('numerical_task_id') for a,b in zip(sorted(rows,key=lambda r:r['dz_a0']),sorted(selected,key=lambda r:r['dz_a0'])))
        result['candidate_vs_reference']['evidence_relation']=('ALIASED_SAME_NUMERICAL_TASK_NOT_INDEPENDENT_CROSSCHECK' if alias else 'INDEPENDENT_NUMERICAL_TASK_COMPARISON')
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
