#!/usr/bin/env python3
"""Create a path/hash inventory and audit prompt from already recorded BASS CR evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/audit/R3M30'
DROPBOX = Path('/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912')
EXTERNAL_ROOTS = [
    Path('/mnt/sn850x2t/bass_cr_r3m11_20260921'),
    Path('/mnt/sn850x2t/bass_cr_r3m12_20260921'),
    Path('/mnt/sn850x2t/bass_cr_r3m14_20260922'),
    Path('/mnt/sn850x2t/bass_cr_r3m15_20260922'),
    Path('/mnt/sn850x2t/bass_cr_r3m16_20260922'),
    Path('/mnt/sn850x2t/bass_cr_r3m18_20260923'),
    Path('/mnt/sn850x2t/bass_cr_r3m19_n1_20260923'),
    Path('/mnt/sn850x2t/bass_cr_r3m27_20260924'),
    Path('/mnt/sn850x2t/bass_cr_r3m28_20260924'),
]
MILESTONES = [
    ('R3M10', 'Repository intake', 'Imported manifest-verified independent physical-problem checkpoint; repository root commit.', ['results/R3M10_LOCAL_RETURN_20260921']),
    ('R3M11', 'Single-b baseline and controlled variables', 'Recorded imported scientific NO_GO and separated fixed-CAP/finite-span controls.', ['docs/r3m11/REPORT_KO.md', 'docs/r3m11/STATUS.json']),
    ('R3M12', 'Controlled single-b return', 'Added controlled comparisons and preserved the NO_GO decision and publication failures/receipts.', ['results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921/README_KO.md', 'results/R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921']),
    ('R3M13', 'Preparation diagnostics', 'Added conditional preparation-pair diagnostics and transfer bounds; no new production collision or cross section.', ['docs/r3m13/REPORT_KO.md', 'docs/r3m13/STATUS.json']),
    ('R3M14', 'Preparation-pair gate and collision', 'Preparation-pair NO_GO; collision comparison passed only as a pair screen. Production remains NO_GO.', ['docs/r3m14/production/REPORT_KO.md', 'docs/r3m14/production/FINAL_DECISION.json']),
    ('R3M15', 'Controlled spatial matrix', 'Three A/B/C collisions and preparation controls recorded; scientific convergence NO_GO.', ['docs/r3m15/REPORT_KO.md', 'docs/r3m15/FINAL_DECISION.json']),
    ('R3M16', 'Coulomb/FFT h-dt study', 'Two A1/B1 collisions and target-only diagnostics; time refinement remained open.', ['docs/r3m16/REPORT_KO.md', 'docs/r3m16/FINAL_DECISION.json']),
    ('R3M17', 'Production validation infrastructure', 'Added independent time reference, immutable checkpoint handling and execution contracts; production HOLD.', ['docs/r3m17/REPORT_KO.md', 'docs/r3m17/FINAL_DECISION.json']),
    ('R3M18', 'B2 temporal refinement', 'Recorded B2 and channel changes exceeding the 0.10% screen; temporal gate remained open.', ['docs/r3m18/REPORT_KO.md', 'docs/r3m18/FINAL_DECISION.json']),
    ('R3M19', 'Full-H diagnostics and work precision', 'Time refinement remained open; bounded full-H diagnostics and CPU performance candidates were recorded.', ['docs/r3m19/REPORT_KO.md', 'docs/r3m19/FINAL_DECISION.json']),
    ('R3M20', 'Short-window GPU reference/work precision', 'Ran bounded diagnostics on retained B2 checkpoints; scope remained local Strang reference, not production.', ['docs/r3m20/REPORT_KO.md', 'docs/r3m20/FINAL_DECISION.json']),
    ('R3M21', 'Incoming CF4 reference resolution attempt', 'Incoming B2 CPU/GPU reference ladder did not satisfy its strict oracle gate; first failure retained.', ['docs/r3m21/REPORT_KO.md', 'docs/r3m21/FINAL_DECISION.json']),
    ('R3M22', 'Incoming full-H inner action reference', 'Bounded GPU reference retry and strict CPU oracle evidence; unresolved historical failures retained.', ['docs/r3m22/REPORT_KO.md', 'docs/r3m22/FINAL_DECISION.json']),
    ('R3M23', 'Closest/outgoing B2 cross-window work precision', 'Two retained-window comparisons passed only for REFERENCE_FOR_STRANG; no global time or production promotion.', ['docs/r3m23/REPORT_KO.md', 'results/R3M23/FINAL_DECISION.json']),
    ('R3M24', 'Local integration and bounded reference', 'Local integration suite and two B2 windows; typed result scope remained REFERENCE_FOR_STRANG.', ['docs/r3m24/LOCAL_INTEGRATION_REPORT_KO.md', 'results/R3M24_LOCAL_20260924T1532KST']),
    ('R3M25', 'Physical t=0 event window', 'Four-step local event window passed its local CF4/Strang-scale checks; no global time certificate.', ['docs/r3m25/REPORT_KO.md', 'results/R3M25/ATTEMPT_2/RESULT.json']),
    ('R3M26', 'Model foundation and prospective convergence strategy', 'Completed model/units/observable and prospective numerical criteria; production remains HOLD.', ['docs/r3m26/REPORT_KO.md', 'docs/r3m26/FINAL_DECISION.json']),
    ('R3M27', 'B3 full collision and frozen time estimate', 'One preparation and one witnessed 7172-step B3 collision; fixed-h selected-span temporal estimate validated, noncertified.', ['docs/r3m27/REPORT_KO.md', 'results/R3M27/B3_TEMPORAL_EVALUATION.json']),
    ('R3M28', 'A3 same-horizon spatial pair', 'One preparation and one witnessed 7172-step A3 collision; P1-P3 pair screen NO_GO at 3.03-3.29%; continuum spatial error remains open.', ['docs/r3m28/REPORT_KO.md', 'results/R3M28/SPATIAL_EVALUATION.json']),
    ('R3M29', 'Point-Coulomb cell and phase discriminator', 'Local singular-cell bias and production-order phase histogram prioritized cell-average as a short-window candidate; causality and production spatial budget remain open.', ['docs/r3m29/REPORT_KO.md', 'results/R3M29/RESULT_V3.json']),
]

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def markdown(path: str) -> str:
    if path.startswith('/'): return f'[{Path(path).name}]({path})'
    return f'[{path}](../../../{path})'

def metadata(path: Path, scope: str) -> dict:
    abs_path = path.resolve()
    if scope == 'repository':
        rel = path.relative_to(ROOT).as_posix()
        link = '../../../' + rel
    else:
        rel = str(abs_path)
        link = str(abs_path)
    return {'scope': scope, 'path': rel, 'absolute_path': str(abs_path), 'size_bytes': path.stat().st_size,
            'sha256': sha(path), 'markdown_link': f'[{path.name}]({link})'}

def build():
    branch = subprocess.check_output(['git','-C',str(ROOT),'branch','--show-current'],text=True).strip()
    head = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    tree = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD^{tree}'],text=True).strip()
    root_commit = subprocess.check_output(['git','-C',str(ROOT),'rev-list','--max-parents=0','HEAD'],text=True).splitlines()[0]
    raw = subprocess.check_output(['git','-C',str(ROOT),'log','--first-parent','--reverse','--format=%H%x09%ad%x09%s','--date=iso-strict','HEAD'],text=True)
    commits=[]
    for line in raw.splitlines():
        sha1,date,subject=line.split('\t',2)
        commits.append({'commit':sha1,'date':date,'subject':subject})
    all_raw = subprocess.check_output(['git','-C',str(ROOT),'log','--all','--format=%H%x09%ad%x09%s','--date=iso-strict'],text=True)
    all_commits=[]
    for line in all_raw.splitlines():
        sha1,date,subject=line.split('\t',2)
        all_commits.append({'commit':sha1,'date':date,'subject':subject})
    status=subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain=v1','--branch'],text=True).splitlines()
    remote_line=subprocess.check_output(['git','-C',str(ROOT),'ls-remote','origin',f'refs/heads/{branch}'],text=True).strip()
    remote_head=remote_line.split('\t',1)[0] if remote_line else None
    docs=[]
    for m in MILESTONES:
        refs=[]
        for ref in m[3]:
            if ref.startswith('results/') and (ROOT/ref).is_dir():
                files=[p for p in (ROOT/ref).rglob('*') if p.is_file()]
                refs.append({'path':ref,'markdown_link':markdown(ref),'file_count':len(files)})
            elif (ROOT/ref).is_file():
                refs.append(metadata(ROOT/ref,'repository'))
        docs.append({'id':m[0],'title':m[1],'recorded_outcome':m[2],'authority_files':refs})
    repo_artifacts=[]
    for p in sorted((ROOT/'results').rglob('*')):
        if p.is_file(): repo_artifacts.append(metadata(p,'repository'))
    run_names={'result.json','result_final.json','result_v2.json','result_v3.json','result_v4.json','gpu_result.json','a1_result.json','b1_result.json'}
    run_files=[p for p in sorted((ROOT/'results').rglob('*')) if p.is_file() and p.name.lower() in run_names]
    local_run_files=[]
    for base in EXTERNAL_ROOTS:
        if not base.exists(): continue
        for p in sorted(base.rglob('*')):
            if not p.is_file() or p.name.lower() not in run_names: continue
            relative_parts = p.relative_to(base).parts
            if any(part.lower() in {'worktree','extracted','repo_copy','remote_readback','packages','packet'} for part in relative_parts): continue
            local_run_files.append(p)
    run_catalog=[]
    seen=set()
    for p in run_files+local_run_files:
        key=str(p.resolve())
        if key in seen: continue
        seen.add(key)
        run_catalog.append(metadata(p,'repository' if p.resolve().is_relative_to(ROOT) else 'local_run_root'))
    dropbox=[]
    for p in sorted(DROPBOX.iterdir()):
        if p.is_file() and re.search(r'(R3M(?:1[0-9]|2[0-9])|BASS_CR_R3M)',p.name,re.I):
            dropbox.append(metadata(p,'local_dropbox_backup'))
    for m in docs:
        number=int(m['id'][3:])
        def belongs_to_milestone(item):
            if item['scope'] == 'repository':
                match = re.search(r'(?:^|/)R3M(\d+)(?:_|/)', item['path'], re.I)
            else:
                match = re.search(r'bass_cr_r3m(\d+)(?:_|/)', item['absolute_path'], re.I)
            return bool(match and int(match.group(1)) == number)
        m['actual_local_run_result_files']=[a for a in run_catalog if belongs_to_milestone(a)]
    handoff_files=[]
    for p in ['docs/r3m11/REPORT_KO.md','docs/r3m13/REPORT_KO.md','docs/r3m14/production/REPORT_KO.md',
              *[f'docs/r3m{n}/REPORT_KO.md' for n in range(15,24)],
              'docs/r3m24/LOCAL_INTEGRATION_REPORT_KO.md',*[f'docs/r3m{n}/REPORT_KO.md' for n in range(25,30)],
              'docs/roadmap/DAG.json','docs/roadmap/ERROR_BUDGET.json']:
        if (ROOT/p).is_file(): handoff_files.append(metadata(ROOT/p,'repository'))
    return {
      'schema':'BASS_CR_LIFECYCLE_EXECUTION_AUDIT_V1','generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'purpose':'Audit how the selected fixed-target one-electron H+ + H(1s) TDL/AOCC research repository developed from its R3M10 imported checkpoint through R3M29, preserving run provenance, first failures, scientific claim ceilings, and backup/readback distinctions.',
      'desired_audit_result':'An independent, evidence-linked assessment of implementation/run integrity, numerical gate history, preserved failures, claim scope, and remaining blockers, ending with one justified next action. The audit must not promote production from a local reference or pair screen alone.',
      'repository':{'root':str(ROOT),'origin':'https://github.com/cosmosapjw-quantum/bass_cr.git','branch':branch,'snapshot_head':head,'snapshot_tree':tree,'remote_branch_ref':f'refs/heads/{branch}','remote_head_at_generation':remote_head,'local_matches_remote_at_generation':head==remote_head,'root_commit':root_commit,'first_parent_commit_count':len(commits),'all_reachable_commit_count':int(subprocess.check_output(['git','-C',str(ROOT),'rev-list','--all','--count'],text=True).strip()),'working_tree_status_at_generation':status,'dirty_at_generation':any(not s.startswith('##') for s in status),'historical_root_import_commit':root_commit},
      'report_compilation':{'task_id':'BASS_CR_R3M30_COMPLETE_EXECUTION_AUDIT_HANDOFF_20260924','authorization':'owner-directed Host documentation and inventory only','scientific_runs_performed':0,'additional_scientific_analysis_performed':False,'generated_files':['docs/audit/R3M30/EXECUTION_REPORT.json','docs/audit/R3M30/EXTERNAL_AUDIT_HANDOFF.md'],'generator':'scripts/r3m30_audit_inventory.py'},
      'scientific_scope':{'model_contract':markdown('docs/r3m26/MODEL_CONTRACT.json'),'model_foundation':markdown('docs/r3m26/MODEL_FOUNDATION_KO.md'),'model_id':'NONRELATIVISTIC_ONE_ELECTRON_FIXED_TARGET_STRAIGHT_LINE_POINT_COULOMB_V1','target':'Numerically faithful selected physical model; all-bound capture cross sections at 50/100/225 keV/u are the project objective. Literature/private raw agreement is not prerequisite.','budgets':{'numerical_total_relative':0.01,'real_time_relative':0.001,'spatial_relative':0.003,'remaining_components':'as preregistered in ERROR_BUDGET.json'},'physical_model_discrepancy':'Separate from numerical budget.'},
      'current_claim_state':{'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','global_time_error':'NOT_EVALUATED','fixed_h_selected_span_temporal_estimate':'VALIDATED_ESTIMATE_NONCERTIFIED_FOR_R3M27_SCOPE','spatial_pair_screen':'NO_GO_FOR_R3M28_A3_B3_RAW_PAIR','spatial_full_component_estimate':'OPEN','cell_average_point_coulomb':'CANDIDATE_FOR_SHORT_WINDOW_VALIDATION_ONLY','preparation':'OPEN','CAP_box_final_time':'OPEN','channel_completeness':'OPEN'},
      'milestones':docs,'first_parent_commit_history':commits,'all_reachable_commit_history':all_commits,
      'actual_local_run_result_files':run_catalog,
      'complete_results_tree_catalog':{'count':len(repo_artifacts),'total_bytes':sum(a['size_bytes'] for a in repo_artifacts),'files':repo_artifacts},
      'local_dropbox_backup_files':dropbox,
      'authoritative_document_index':handoff_files,
      'backup_semantics':'Every listed local Dropbox file is linked by absolute local path. File presence/size does not prove remote restore. Follow the linked receipt per backup and retain RESTORE_NOT_TESTED or NOT_RUN exactly as recorded.',
      'execution_policy_for_auditor':['Read the local repository and all linked actual run result files before conclusions.','Do not rerun full collisions, preparations, finer h, b-grid, physical rates, or overwrite evidence.','Do not treat paired raw differences, local windows, completed jobs, reviewer passes, or backup upload receipts as production admission.','Preserve original failure logs and distinguish runtime/environment failures from scientific NO_GO.','Cite every finding to a linked exact file and state what was not tested.']}

def render(report):
    lines=['# BASS_CR external audit handoff — R3M10 through R3M29','',
      '## Audit purpose and requested outcome','',
      report['purpose'],'',report['desired_audit_result'],'',
      'The selected production model, numerical targets, and current claim ceilings are recorded in the machine-readable [execution report](EXECUTION_REPORT.json). This handoff requests review of recorded work; it does not authorize new runs.','',
      '## Repository identity','',f"- Root commit: `{report['repository']['root_commit']}`",f"- Inventory snapshot branch and HEAD: `{report['repository']['branch']}` / `{report['repository']['snapshot_head']}`",f"- First-parent commits: {report['repository']['first_parent_commit_count']}; all reachable commits: {report['repository']['all_reachable_commit_count']}",f"- Uncommitted or untracked material was present at inventory generation: {report['repository']['dirty_at_generation']} (the report files were being created in this snapshot).",'',
      '## Recorded project history','',
      'Each milestone links to its authoritative report/decision and its run folder or result file. The JSON report also links every file under `results/`, every recognized canonical local run-result JSON, the first-parent chronology, and all commits reachable from local refs. Packaged/readback copies remain in the full results catalog and are not counted as fresh local runs.','']
    for m in report['milestones']:
        lines.append(f"### {m['id']} — {m['title']}")
        lines.append(m['recorded_outcome'])
        for a in m['authority_files']:
            if 'markdown_link' in a: lines.append(f"- {a['markdown_link']}")
        if m.get('actual_local_run_result_files'):
            lines.append('Actual run results:')
            for a in m['actual_local_run_result_files']:
                lines.append(f"- {a['markdown_link']} — SHA-256 `{a['sha256']}`")
        lines.append('')
    lines += ['## Actual local run-result files','', 'The following table lists recognized result JSONs in the repository and canonical local run roots. Explicit readback mirrors and packaged copies are excluded from this table; they remain indexed in the full results tree when stored in the repository. The complete evidence inventory, with size and SHA-256, is in the linked machine-readable report.','', '| Result file | SHA-256 |','|---|---|']
    for a in report['actual_local_run_result_files']:
        lines.append(f"| {a['markdown_link']} | `{a['sha256']}` |")
    lines += ['', '## Local Dropbox backups','', 'These links point to the backed-up files on this computer. Each file is linked individually so the reviewer can open it without extra context. Consult its linked in-repository receipt for backup tier and restore status.','']
    for a in report['local_dropbox_backup_files']:
        lines.append(f"- {a['markdown_link']} — {a['size_bytes']} bytes")
    lines += ['', '## Request to the external reviewer','',
      'Please independently audit the chronology, exact identities, run-result provenance, failure preservation, scientific status transitions, and backup claims. Compare the machine-readable inventory with the linked local records. Report factual discrepancies, missing evidence, unsupported status promotion, and any claim that exceeds its recorded scope. Separate code/test evidence, numerical evidence, scientific admission, remote publication, and restore verification. Do not rerun scientific work or modify this checkout. Return a concise but detailed audit with findings by severity and exact file links; conclude with one next canonical action.','',
      '## Fixed status and limits','',
      '- `production_admission = HOLD`; `all_bound = OPEN`; `b-grid = NO_GO`; `GLOBAL_TIME_ERROR = NOT_EVALUATED`.',
      '- R3M27 time evidence is a noncertified estimate for fixed h=.20 selected spans only.',
      '- R3M28 A3/B3 is a raw pair NO_GO; it is not a continuum spatial-error lower bound.',
      '- R3M29 cell-average Coulomb is only a candidate for a short same-h validation.',
      '- Dropbox upload records do not imply raw readback or restore. Use the status in each receipt.',
      '- Purpose-specific numerical target is 1% total, .10% time, .30% space, with remaining allocations as registered in the linked roadmap. Model discrepancy remains separate.',
      '- Model authority: [MODEL_CONTRACT.json](../../../docs/r3m26/MODEL_CONTRACT.json), [MODEL_FOUNDATION_KO.md](../../../docs/r3m26/MODEL_FOUNDATION_KO.md), [DAG.json](../../../docs/roadmap/DAG.json), and [ERROR_BUDGET.json](../../../docs/roadmap/ERROR_BUDGET.json).','']
    return '\n'.join(lines)

def write():
    OUT.mkdir(parents=True,exist_ok=True)
    report=build()
    (OUT/'EXECUTION_REPORT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    (OUT/'EXTERNAL_AUDIT_HANDOFF.md').write_text(render(report))

def validate():
    report=json.loads((OUT/'EXECUTION_REPORT.json').read_text())
    assert report['repository']['snapshot_head']=='8e1d49e5ef6af70bb47d9238e64cda68ea0f5c4f'
    assert report['repository']['root_commit']=='9da0011f93147ad8dddf166d3825de9a1c683ca9'
    assert len(report['first_parent_commit_history'])==81
    for item in report['complete_results_tree_catalog']['files']:
        assert (ROOT/item['path']).is_file(), item['path']
    for item in report['local_dropbox_backup_files']:
        assert Path(item['absolute_path']).is_file(), item['absolute_path']
    md=(OUT/'EXTERNAL_AUDIT_HANDOFF.md').read_text()
    assert 'Audit purpose and requested outcome' in md
    assert 'Actual local run-result files' in md and 'Local Dropbox backups' in md
    assert report['current_claim_state']['production_admission']=='HOLD'
    for item in report['actual_local_run_result_files']:
        assert item['markdown_link'] in md, item['absolute_path']
    for item in report['local_dropbox_backup_files']:
        assert item['markdown_link'] in md, item['absolute_path']
    for destination in re.findall(r'\[[^\]]+\]\(([^)]+)\)', md):
        target = Path(destination)
        if not target.is_absolute(): target = (OUT / target).resolve()
        assert target.exists(), f'broken handoff link: {destination}'
    print('inventory links verified',len(report['complete_results_tree_catalog']['files']),
          'repo files;',len(report['actual_local_run_result_files']),'run result JSONs;',
          len(report['local_dropbox_backup_files']),'Dropbox backups')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--validate',action='store_true');args=parser.parse_args()
    validate() if args.validate else write()
