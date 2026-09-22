import hashlib,json,shutil
from pathlib import Path
O=Path('/mnt/sn850x2t/bass_cr_r3m14_20260922'); W=O/'worktree'; C=O/'collision0125'; R=O/'report'; R.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
a,b=[read(O/n/'receipt.json') for n in ['initial025','initial0125']];pair=read(O/'pair.json');result=read(C/'result.json');binding=read(C/'r3m14_initial_binding.json');state=read(C/'state.json');seal=read(C/'r3m11_checkpoint_seal.json');run=read(C/'r3m14_witness_run_receipt.json');env=read(O/'receipts/environment.json')
assert result['status']=='completed' and state['done']==state['nstep']
assert binding['schema']=='BASS_CR_R3M14_INTERNAL_INITIAL_BINDING_V2' and binding['status']=='PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED'
assert all(binding[k] is True for k in ['array_digest_match','norm_match','environment_match'])
assert binding['collision_propagation_started_when_written'] is False
assert all(sha(C/n)==h for n,h in seal['files'].items())
assert seal['source_digest']==env['source_digest']==binding['actual_source_digest']==binding['expected_source_digest']
assert all(x['script_sha256']==sha(W/'scripts/r3m13_initial_state_pair.py') for x in [a,b])
assert binding['prepared_receipt_sha256']==sha(O/'initial0125/receipt.json')
assert binding['prepared_state_file_sha256']==sha(O/'initial0125/initial.npy')
assert binding['instrumentation_sha256']==sha(W/'scripts/r3m14_collision_initial_witness.py')
assert binding['r3m13_helper_sha256']==a['script_sha256']
assert run['state_json_sha256']==sha(C/'state.json') and run['state_npy_sha256']==sha(C/'state.npy') and run['seal_sha256']==sha(C/'r3m11_checkpoint_seal.json')
g=result['analysis']['gram_audit'];ref=0.00775827737938;change=abs(g['P_span_nmax']-ref)/ref
d=pair['distance']['ray_distance'];ds=pair['conditional_interval']['sufficient_ray_distance'];pairpass=d<=ds;collisionpass=change<=0.01
history=[read(p) for p in sorted((O/'receipts').glob('collision0125.chunk*.checkpoint.json'))]
dec={'schema':'BASS_CR_R3M14_PRODUCTION_DECISION_V1','work_unit':'R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN','decision':'PREPARATION_CONTROL_PASS_SCOPED' if pairpass and collisionpass else 'NO_GO','preparation_pair_gate':'PASS_PAIR_ONLY' if pairpass else 'NO_GO','same_grid_collision_gate':'PASS_PAIR_ONLY' if collisionpass else 'NO_GO','initial_binding':binding['status'],'production_pair_d':d,'d_star':ds,'trace_distance':pair['distance']['trace_distance'],'conditional_interval':pair['conditional_interval'],'reference_probability_denominator':ref,'reference_probability_full_precision_record':read(O/'receipts/reference_identity.json')['reference_P_span_nmax_full_precision'],'reference_anchor_verified_for_conditional_theorem':False,'reference_anchor_limitation':'Historical R3M12 initial array was not stored/bound; pair theorem remains conditional. Saved reference result/config/state/seal hashes verified; checkpoint-only source repair documented.','P_span_nmax':g['P_span_nmax'],'relative_same_grid_change':change,'screen':0.01,'gram_audit':g,'final_norm':state['norm'],'preparations':{'initial025':a,'initial0125':b},'runtime_environment':env,'chunk_count':len(history),'restart_count':len(history)-1,'nstep':state['nstep'],'hashes':{str(p.relative_to(O)):sha(p) for p in [O/'initial025/initial.npy',O/'initial0125/initial.npy',O/'initial025/receipt.json',O/'initial0125/receipt.json',C/'state.npy',C/'state.json',C/'r3m11_checkpoint_seal.json',C/'r3m14_initial_binding.json',C/'r3m14_witness_run_receipt.json',C/'result.json',W/'scripts/r3m13_initial_state_pair.py',W/'scripts/r3m14_collision_initial_witness.py',W/'configs/r3m13/tdl_dx025_imag0125_T30.json',W/'configs/r3m13/tdl_dx025_imag025_T30.json']},'enriched_config_hash':binding['enriched_config_hash'],'numerical_source_digest':env['source_digest'],'inherited_spatial_gate':'NO_GO','inherited_spatial_relative_change_percent':2.289941,'bgrid':'NO_GO','physical_rate_evaluated':False,'all_bound_probability_evaluated':False,'continuum_probability_evaluated':False,'dx020_executed':False,'next_node':'R3M15_SPATIAL_REFINEMENT_DECISION_GATE' if pairpass and collisionpass else None,'next_action':'OWNER_DECISION_REQUIRED_ON_PREPARATION_PAIR_NO_GO' if not pairpass else ('REVIEW_COLLISION_SCREEN_NO_GO' if not collisionpass else 'R3M15_SPATIAL_REFINEMENT_DECISION_GATE'),'backup_status':'SEE_DETACHED_DELIVERY_RECEIPT','old_r3m12_drive_backup':'UNCHANGED_1_OF_19_NOT_CLOSED'}
(R/'DECISION.json').write_text(json.dumps(dec,ensure_ascii=False,indent=2)+'\n')
rows='\n'.join(f"| {n} | {r['initial']['energy_Eh']:.15g} | {r['initial']['stationary_residual_Eh']:.15g} | {r['target_only']['no_cap_one_step_ray_defect']:.15g} | {r['target_only']['cap_one_step_surviving_norm']:.16g} |" for n,r in [('0.025 × 1200',a),('0.0125 × 2400',b)])
text=f'''# R3M14 production 반환

최종 판정: **{dec['decision']}**. 준비 쌍 판정은 **{dec['preparation_pair_gate']}**, 실제 동일 격자 충돌 비교는 **{dec['same_grid_collision_gate']}**이다. 허용오차를 바꾸지 않았다.

## 준비 쌍

production 격자 280×240×480, dx=.25 a0, 총 imaginary time 30 t_a. d={d:.17g}, d_star={ds:.17g}, d/d_star={d/ds:.12g}, trace distance={dec['trace_distance']:.17g}. 조건부 구간 [{pair['conditional_interval']['lower']:.17g}, {pair['conditional_interval']['upper']:.17g}], 최대 상대 변화 상한 {100*pair['conditional_interval']['relative_error_upper']:.9f}%. 이는 floating 평가이며 roundoff enclosure가 아니다.

| 준비 | E (Eh) | Hamiltonian residual (Eh) | no-CAP 1-step ray defect | CAP 1-step norm |
| --- | ---: | ---: | ---: | ---: |
{rows}

Hamiltonian residual과 target-only ray defect는 다른 진단이다. 이 값을 capture 확률 오차로 등치하지 않는다. real dt_actual={result['dt_actual']:.17g} t_a.

## 실제 collision 및 binding

v2 wrapper가 inherited relaxed_initial()의 원 객체를 그대로 반환했으며, 저장 preparation과 typed array digest·norm·환경 일치를 전파 전에 확인했다. binding={binding['status']}. state 대입·cast·정규화는 하지 않았다. 총 {state['nstep']} step을 최대 128-step씩 {len(history)} chunk, {len(history)-1} sealed restart로 완료했다. 각 chunk의 stdout/stderr, state metadata, seal 및 wrapper receipt를 보존했다.

P_span(n≤3)={g['P_span_nmax']:.17g}. 지정 R3M12 reference/분모={ref:.14g}, 상대 변화={100*change:.9f}%. P_region={g['P_region']:.17g}, final norm={state['norm']:.17g}, Gram condition={g['Gram_condition']:.17g}, eigenvalue range={g['Gram_eigenvalues']}. 전체 nested-span·gap·eps·cross-term 진단은 DECISION.json의 gram_audit 및 collision0125/result.json에 있다.

과거 기준의 raw config는 .025 준비 설정과 일치하고 저장 state/seal 해시는 검증했다. 과거 source digest와 현재 값의 차이는 02546302의 checkpoint seal 저장 수선으로 분류했다. propagation·preparation·analysis 메서드 AST는 동일하며 옛 seal을 변경하거나 재시작하지 않았다. 과거 initial.npy 자체는 저장·binding되어 있지 않아 조건부 정리의 reference_anchor_verified는 false로 유지한다. 실제 reference 결과의 full precision은 {dec['reference_probability_full_precision_record']:.17g}; 판정 분모는 사용자 지정값을 그대로 사용했다.

## 환경과 소스

Ubuntu 24.04.5 LTS, kernel 7.0.0-31-generic; Python 3.12.3, NumPy {env['numpy']}, SciPy {env['scipy']}, CuPy {env['cupy']}, CUDA runtime {env['cuda_runtime']}, driver API {env['cuda_driver']}, NVIDIA driver 595.84, RTX 3090. GPU UUID와 라이브러리 경로 및 전체 버전은 receipts/environment.json에 있다.

source commit 0c068e902e59ad001c4a2ae1be4168d1d29907b8는 d04124e8a1b83f29fd26baa13f11cd68a8f33c15의 후손이다. cr_repro source digest={env['source_digest']}. canonical helper SHA={a['script_sha256']}; witness SHA={binding['instrumentation_sha256']}. 준비·설정·state·seal의 SHA와 enriched config hash는 DECISION.json에 모두 기록했다.

필수 pytest **52 passed**, wrapper --help PASS. 이 결과는 해당 네 테스트 파일 범위이며 full-suite/독립 리뷰 PASS를 주장하지 않는다. MLflow는 외부 subprocess orchestration에만 적용했고 scientific interpreter와 고정 소스는 유지했다. 최초 .025 준비는 tracing 도입 전 실행됐고 canonical receipt/stdout/stderr가 있다. 이후 trace 검증은 receipts/MLFLOW_VERIFICATION.json 참조.

## 판정 한계와 반환

준비 쌍 d>d_star이면 실제 collision 선별 결과이 1% 이내라도 전체 준비 제어 PASS를 선언하지 않는다. inherited spatial NO_GO(.3125→.25 변화 2.289941%), b-grid NO_GO를 유지한다. finite n≤3 sampled span은 all-bound/continuum 확률이 아니다. dx=.20, b-grid, physical rate는 실행하지 않았다. 이번 결과의 다음 행동: {dec['next_action']}. R3M15는 두 선별 기준의 scoped PASS가 있을 때만 다음 node가 된다.

큰 배열은 immutable production archive에 보존하고 Git에는 작은 결과·receipt·archive pointer만 넣는다. 두 provider 완료는 detached DELIVERY_RECEIPT.json의 실제 ID·크기·readback 검증으로만 판정한다. R3M12 Drive 1/19 문제는 별도로 미완료 상태를 유지한다.
'''
(R/'REPORT_KO.md').write_text(text)
(R/'CHUNK_HISTORY.json').write_text(json.dumps(history,indent=2)+'\n')
print(json.dumps({k:dec[k] for k in ['decision','production_pair_d','d_star','P_span_nmax','relative_same_grid_change','chunk_count','restart_count']},indent=2))
