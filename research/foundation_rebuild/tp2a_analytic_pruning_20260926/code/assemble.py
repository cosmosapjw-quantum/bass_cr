"""Join new angular kernel to unchanged same-center weak operators."""
import numpy as np
import bootstrap
from full_operator import assemble_full,_bind_cross,same_center_blocks
from exact_cross import cross,cartesian_transform

def assemble(trajectory,channels,t,kernel,*,order=56,subdivisions=2,phase_budget=None,sector='full',progress=None):
    raw=cross(trajectory,channels,t,kernel,order=order,subdivisions=subdivisions,phase_budget=phase_budget,sector=sector,progress=progress)
    if sector=='full':
        snap=_bind_cross(trajectory,channels,t,raw,raw['metadata'])
        full=assemble_full(trajectory,channels,t,same_order=20,cross=snap)
        return raw,full
    groups=[tuple(c for c in channels if c.center==k) for k in (0,1)]
    u0=cartesian_transform(groups[0])[:,raw['metadata']['sector_columns_T']]
    u1=cartesian_transform(groups[1])[:,raw['metadata']['sector_columns_P']]
    tt=same_center_blocks(trajectory,channels,t,0,order=20);pp=same_center_blocks(trajectory,channels,t,1,order=20)
    full={name:np.block([[u0.conj().T@tt[name]@u0,raw[name+'_tp']],[raw[name+'_pt'],u1.conj().T@pp[name]@u1]]) for name in ('S','H','D')}
    ev=np.linalg.eigvalsh(full['S'])
    if ev[0]<=0 or ev[0]/ev[-1]<1e-8:raise ArithmeticError('even-sector metric unresolved')
    full['diagnostics']={'metric_min':float(ev[0]),'metric_max':float(ev[-1]),'metric_ratio':float(ev[0]/ev[-1])}
    full['metadata']={'sector':'even','capture_execution_allowed':False,'original_dimension':len(channels),'dimension':len(full['S'])}
    return raw,full
