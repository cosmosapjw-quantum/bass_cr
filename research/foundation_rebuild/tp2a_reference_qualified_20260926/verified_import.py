"""Explicit, read-only bridge from the single authorized pre-repair run.

An old failed qualification is never relabelled. Only identity-checked operator
payloads with unchanged physical and quadrature semantics enter the new context.
The sibling archive and report hashes are supplied by the frozen import grant.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, io, json, re, zipfile
import numpy as np
import qualification_runtime as qr

PHYSICS_FIELDS=('energy_keV_per_u','b_a0','epsilon_z_a0','phase_budget_rad',
                'phase_order','reference_orders','same_center_order','radial_spec','screens','z_samples_a0')


def _sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _checked_bytes(source, archive, relative):
    path=Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('unsafe archived relative path')
    data=(source/path).read_bytes()
    if data!=archive.read(path.as_posix()):
        raise ValueError('source file differs from authorized archive: '+str(path))
    return data


def validate_previous_run(source, grant, native_sha, contract):
    """Validate authority before copying basis or importing task payloads."""
    source=Path(source).resolve()
    archive_path=source.with_name(source.name+'_RETURN.zip')
    if qr.sha(archive_path)!=grant['archive_sha256']:
        raise ValueError('authorized previous archive SHA mismatch')
    with zipfile.ZipFile(archive_path) as archive:
        report_bytes=_checked_bytes(source,archive,'RETURN_REPORT.json')
        if _sha_bytes(report_bytes)!=grant['report_sha256']:
            raise ValueError('authorized previous report SHA mismatch')
        report=json.loads(report_bytes)
        if report['execution_head']!=grant['execution_head']:
            raise ValueError('previous execution commit mismatch')
        intake=json.loads(_checked_bytes(source,archive,'INTAKE.json'))
        context=intake['context']
        if qr._digest(context)!=intake['context_id']:
            raise ValueError('previous context digest mismatch')
        if qr._digest(context['contract'])!=grant['contract_digest']:
            raise ValueError('previous contract identity mismatch')
        if context['source_pins']!=grant['source_pins']:
            raise ValueError('previous source pins mismatch')
        if context['native_library_sha256']!=native_sha:
            raise ValueError('previous native binary identity mismatch')
        for field in PHYSICS_FIELDS:
            if context['contract'][field]!=contract[field]:
                raise ValueError('physical or quadrature rule changed: '+field)
        for name in ('BASIS.json','BASIS.npz'):
            _checked_bytes(source,archive,name)
    from runtime import load_bank
    bank,basis=load_bank(source)
    if basis['identity']!=context['basis_identity']:
        raise ValueError('previous basis identity mismatch')
    return {'source':str(source),'archive':str(archive_path),'context':context,
            'context_id':intake['context_id'],'report':report,'grant':grant},bank,basis


def import_tasks(previous, destination, new_context):
    """Copy exact NPZ bytes; write new receipts linking old and new identities."""
    source=Path(previous['source']);destination=Path(destination)
    old_context=previous['context'];old_id=previous['context_id']
    config=new_context['contract'];new_id=qr._digest(new_context)
    from runtime import load_bank
    from bass_foundations.two_center import symmetric_channels
    from cr_repro.observables import projectile_speed_au
    bank,_=load_bank(source);channels=symmetric_channels(bank)
    nt=sum(c.center==0 for c in channels);np_=sum(c.center==1 for c in channels);n=nt+np_
    ti=np.array([i for i,c in enumerate(channels) if c.center==0]);pi=np.array([i for i,c in enumerate(channels) if c.center==1])
    speed=projectile_speed_au(config['energy_keV_per_u']);imported=[]
    with zipfile.ZipFile(previous['archive']) as archive:
        for p in sorted((source/'tasks').glob('*.json')):
            tid=p.stem
            if not re.fullmatch('[0-9a-f]{32}',tid):
                raise ValueError('invalid previous task identifier')
            receipt_bytes=_checked_bytes(source,archive,'tasks/'+p.name)
            receipt=json.loads(receipt_bytes)
            method=receipt['method'];q=receipt.get('reference_order')
            z=receipt['z_center_a0'];dz=receipt['dz_a0']
            if method not in ('phase24','reference') or z not in config['z_samples_a0']:
                raise ValueError('previous task has unsupported scope')
            if dz not in (-config['epsilon_z_a0'],0.,config['epsilon_z_a0']):
                raise ValueError('previous stencil does not match')
            if (method=='reference' and q not in config['reference_orders']) or (method=='phase24' and q is not None):
                raise ValueError('previous quadrature order mismatch')
            expected=qr.task_identity(method,z,dz,old_context,reference_order=q)
            if tid!=expected or receipt['task_id']!=expected or receipt['context_id']!=old_id:
                raise ValueError('previous task identity mismatch')
            if receipt['channel_count']!=n or float(receipt['time_ta']).hex()!=float((z+dz)/speed).hex():
                raise ValueError('previous basis size or time mismatch')
            meta=receipt['metadata']
            if meta.get('radial_order')!=(q if method=='reference' else config['phase_order']):
                raise ValueError('previous task metadata order mismatch')
            if method=='phase24' and meta.get('phase_budget_rad')!=config['phase_budget_rad']:
                raise ValueError('previous phase budget mismatch')
            payload=_checked_bytes(source,archive,'tasks/'+tid+'.npz')
            if _sha_bytes(payload)!=receipt['matrix_sha256']:
                raise ValueError('previous matrix receipt hash mismatch')
            with np.load(io.BytesIO(payload),allow_pickle=False) as f:
                if set(f.files)!=set(qr.FULL_KEYS+qr.CROSS_KEYS):
                    raise ValueError('previous matrix keys mismatch')
                arrays={key:np.array(f[key]) for key in f.files}
            for key,value in arrays.items():
                shape=(n,n) if key in qr.FULL_KEYS else ((nt,np_) if key.endswith('tp') else (np_,nt))
                if value.shape!=shape or value.dtype!=np.dtype('complex128') or not np.isfinite(value).all():
                    raise ValueError('previous matrix shape/type/finiteness mismatch')
            for key in qr.CROSS_KEYS:
                left,right=(ti,pi) if key.endswith('tp') else (pi,ti)
                if not np.array_equal(arrays[key],arrays[key[0]][np.ix_(left,right)]):
                    raise ValueError('previous raw/full block mismatch')
            new_tid=qr.task_identity(method,z,dz,new_context,reference_order=q)
            new_receipt=dict(receipt,task_id=new_tid,context_id=new_id,imported=True,
                provenance={'source_run':str(source),'source_archive_sha256':previous['grant']['archive_sha256'],
                    'source_report_sha256':previous['grant']['report_sha256'],'source_context_id':old_id,
                    'source_task_id':tid,'source_receipt_sha256':_sha_bytes(receipt_bytes),
                    'reuse':'EXACT_MATRIX_BYTES_UNCHANGED_QUADRATURE_SEMANTICS'})
            qr._atomic_file(destination/'tasks'/(new_tid+'.npz'),lambda f,data=payload:f.write(data))
            qr._write_json(destination/'tasks'/(new_tid+'.json'),new_receipt)
            imported.append({'old_task_id':tid,'new_task_id':new_tid,'method':method,'order':q or 24,
                'z_a0':z,'dz_a0':dz,'matrix_sha256':receipt['matrix_sha256']})
    bridge={'schema':'BASS_TP2A_EXPLICIT_IMPORT_V1','source_status':previous['report']['status'],
        'old_failure_preserved':True,'source_report_sha256':previous['grant']['report_sha256'],
        'source_archive_sha256':previous['grant']['archive_sha256'],'imported_tasks':imported,
        'count':len(imported),'new_scientific_evaluations':0,'capture_execution_allowed':False}
    qr._write_json(destination/'IMPORT_RECEIPT.json',bridge)
    return bridge
