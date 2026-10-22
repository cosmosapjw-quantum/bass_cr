#!/usr/bin/env python3
"""Create the pre-transport C22B scientific handoff from actual receipts. ODE0."""
from pathlib import Path
import json
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
def read(p):return json.loads((HERE/p).read_text())
def create(p,value):
    with (HERE/p).open('x',encoding='utf8') as f:
        if isinstance(value,str):f.write(value)
        else:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def sha(p):return hashlib.sha256((HERE/p).read_bytes()).hexdigest()

s=read('analysis_v2/SUMMARY.json');contract=read('CONTRACT.json')
source=read('evidence/SOURCE_FREEZE.json');now=datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
assert s['status']=='PASS_SCOPED'
R='a5e12c5f3e6d323e211d65fefad34060ec07eff0'
pub={'status':'OPEN_UNKNOWN_NO_ACK_LOCAL_COMMIT_AND_BUNDLE_TO_FOLLOW',
     'remote_head_last_observed':R,'remote_PR':96,'PR_state':'open_draft_unmerged',
     'remote_read_receipt':'evidence/publication_final_remote_read.json',
     'write_retry_receipt':'evidence/retry_and_external_intake/GITHUB_PROBE_RECEIPT.json',
     'write_permission':'UNDETERMINED; no permission denial observed','publication_complete':False}
backup={'status':'PRE_TRANSPORT_SCIENCE_SNAPSHOT;checkpoint_R1_COMPLETE_SCOPED',
        'checkpoint_receipt':'evidence/checkpoint_backup/SUMMARY.json',
        'checkpoint_Library':'libfile_37025ed8ca548191bf5415f69da10e48',
        'checkpoint_Dropbox':'id:BSpOijBcT10AAAAAAD_h2Q',
        'new_final_delivery':'FINAL_AUTHORITY_SIDECAR_TO_FOLLOW',
        'prior_C22A_Drive_retry':'UNKNOWN_NO_ACK',
        'historical_C21O_Drive':'OPEN;mainUNKNOWN_NO_ACK,documentNOT_RUN,recoveryNOT_ATTEMPTED',
        'triple_backup_claim':False}
dag={'status':'C22B_CONDITIONAL_SCIENCE_COMPLETE_SCOPED;PUBLICATION_OPEN',
     'next':'C22C excitation-energy and actual low-temperature atomic-rate coverage contract',
     'full_thermochemical_radiative_closure':'OPEN','global_error_bound':None,
     'HOLD':['full nuclear high-energy','general triaxial/tilted/polarized CMB']}
stage_rows=[
 ('R1','연구 위치·계약','C22A continuation with prescribed isotropic bath; unchanged authority C/D/R and missing conversations recorded.',['CONTRACT.json','evidence/PRIOR_SCOPE_PRESERVATION.json']),
 ('R2','근거·재사용','Latest1259 advertised heads,6docs+2code blobs; immutable C22A baseline and primary atomic/Compton literature reused.',['evidence/retry_and_external_intake/LATEST_EXTERNAL_INTAKE.json','theory/SOURCE_EVIDENCE.json']),
 ('R3','주장·전제 정렬','Non-tilted LRS,full Frobenius,signed sums,21explicit populations,n/T declared0,commonT and externalbath assumptions separated.',['CONTRACT.json','theory/THEORY_CONTRACT_DRAFT.md']),
 ('R4','가설·표현 탐색','Selected open thermostat; finite dynamic Planck bath would need photon/spectral closure; no general no-go.',['theory/THEORY_CONTRACT_DRAFT.md']),
 ('R5','구성적 유도','Opposite gas/bath energy flux; particle-count EOS term and zero-inventory invariant-face construction.',['theory/WOLFRAM_ALGEBRA_RECEIPT.json','model.py','compton.py']),
 ('R6','독립 검증','Independent SI formula,18stored states as finite RHS inputs,EOS directional derivative,28parent source hashes.',['evidence/independent_pre_ODE_review/C22B_REVIEW.json']),
 ('R7','판별 검증','9focused tests incl zero-electron/equalT/entropy/off-mode highT; one genuine off-mode bug fixed before freeze.',['evidence/FOCUSED_TESTS_v2.json','evidence/independent_pre_ODE_review/INDEPENDENT_FINITE_CHECKS.json']),
 ('R8','결과 판정','Algebra invariant established under declared closure; matched new trajectories support material Compton feedback; full physical closure remains OPEN.',['analysis_v2/SUMMARY.json','atomic_diagnostics_v1/SUMMARY.json']),
 ('R9','정식 결과·코딩 연결','75full outputs,72active solver states; one gas flux and opposite cumulative bath state.',['model.py','CONTRACT.json']),
 ('R10','종료·재개','Theory bridge delivered to C22B implementation; next coverage and spectral closure obligations explicit.',['REPORT_KO.md','DAG.json']),
 ('C1','목표·baseline','Three immutable C22A histories reused; no C21O/NCP/C22A restore-purpose ODE.',['analysis_v2/SUMMARY.json','evidence/PRIOR_SCOPE_PRESERVATION.json']),
 ('C2','식–데이터–코드','Source identity binds31files; model indices,rate units,source and input identities recorded.',['evidence/SOURCE_FREEZE.json','model.py','compton.py']),
 ('C3','수치 설계','Preregistered BDF3+Radau1,tolerances,201saved times,18threshold segments,unchanged gates.',['CONTRACT.json','run_pilot.py']),
 ('C4','실행 DAG·자원','Actual quota8/memory8GiB/lease observation; CPU55protected,coordinator0,worker2/3 nominal and1 reference,one thread.',['runs/c22b_compton_bdf_20261022_v1/RESOURCE.json','runs/c22b_compton_radau_20261022_v1/RESOURCE.json']),
 ('C5','구현','Compton term and signed cumulative ledger implemented over immutable parent; no extra Einstein CMB density.',['model.py','compton.py','run_pilot.py']),
 ('C6','구현 검증','9focused checks plus independent pre-ODE physics/code audit; preregistration identity negative probes rejected.',['evidence/FOCUSED_TESTS_v2.json','evidence/ANALYZER_PROVENANCE_CHECKS.json']),
 ('C7','과학 검증','4new trajectories complete; saved804 and accepted6670 checks pass; historical A Radau failure retained.',['analysis_v2/SUMMARY.json','SCIENCE_ACCEPTANCE.json']),
 ('C8','수치·재현성','7field same-input tighter-reference comparison passes;diagnostic mesh differences and domain gaps retained,global error bound null.',['analysis_v2/SUMMARY.json','atomic_diagnostics_v1/MATCHED_COMPARISON.json']),
 ('C9','독립 검토','Independent raw/CSV/tensor/source audit and actual image/PDF review;v1time-axis failure preserved and v2 repaired.',['evidence/independent_result_review/SAVED_DATA_REVIEW.json','evidence/independent_result_review/FINAL_FIGURE_REVIEW.json','evidence/ANALYSIS_REPAIR_BINDING.json']),
 ('C10','판정·인계','Scoped scientific handoff prepared; local Git bundle and final provider receipts are separately bound after this snapshot.',['REPORT_KO.md','NEXT_THREAD_HANDOFF_KO.md','DAG.json'])]
stages=[]
for stage,name,scope,evidence in stage_rows:
    stages.append({'stage':stage,'name':name,'status':'SCIENTIFIC_COMPLETE_SCOPED_PUBLICATION_OPEN' if stage=='C10' else 'COMPLETE_SCOPED',
        'scope':scope,'EXECUTION':{'status':'COMPLETE_SCOPED','evidence':evidence,'new_C22B_trajectories_total':4,'old_ODE_reruns':0},
        'PUBLICATION':pub,'BACKUP':backup,'DAG':dict(dag,stage=stage),'global_error_bound':None})
create('STAGE_RECORDS.json',{'schema':'C22B_20_STAGE_RECORDS_V1','created_KST':now,
    'workflow':'physmath-research-loop1.0.0/approval0.2','stages':stages,
    'EXECUTION':{'status':'COMPLETE_SCOPED','new_C22B_ODE':4,'old_ODE':0,'segments':72},
    'PUBLICATION':pub,'BACKUP':backup,'DAG':dag,'conversations':'UNAVAILABLE',
    'original_nuclear_network_PNG':'NOT_RECOVERED_NOT_READ','strong_no_go':'NONE;NG1_NG7_NOT_APPLICABLE',
    'final_transport_authority':'See separately saved C22B_FINAL_AUTHORITY_20261022.json','global_error_bound':None})
create('DAG.json',{'schema':'C22B_DAG_V1','created_KST':now,
    'nodes':[
      {'id':'C21O_RECOVERY','status':'COMPLETE_SCOPED_REUSED','depends_on':[]},
      {'id':'C22A_CONDITIONAL_SCIENCE','status':'COMPLETE_SCOPED_REUSED;old_reference_failure_preserved','depends_on':['C21O_RECOVERY']},
      {'id':'C22A_PUBLICATION_RETRY','status':'UNKNOWN_NO_ACK;remoteR','depends_on':['C22A_CONDITIONAL_SCIENCE']},
      {'id':'C22A_DRIVE_RETRY','status':'UNKNOWN_NO_ACK','depends_on':['C22A_CONDITIONAL_SCIENCE']},
      {'id':'C22B_OPEN_BATH_CONTRACT','status':'COMPLETE_SCOPED','depends_on':['C22A_CONDITIONAL_SCIENCE']},
      {'id':'C22B_IMPLEMENTATION_AND_RUNS','status':'COMPLETE_SCOPED_4NEW','depends_on':['C22B_OPEN_BATH_CONTRACT']},
      {'id':'C22B_SAVED_DATA_REVIEW','status':'PASS_SCOPED','depends_on':['C22B_IMPLEMENTATION_AND_RUNS']},
      {'id':'C22B_LOCAL_PUBLICATION_BUNDLE','status':'PREPARING;remotepublicationOPEN','depends_on':['C22B_SAVED_DATA_REVIEW']},
      {'id':'C22B_FINAL_BACKUP','status':'PREPARING;finalauthoritysidecarfollows','depends_on':['C22B_SAVED_DATA_REVIEW']},
      {'id':'C22C_ATOMIC_ENERGY_COVERAGE','status':'OPEN;contractbeforeactivation','depends_on':['C22B_SAVED_DATA_REVIEW']},
      {'id':'FULL_SPECTRAL_RADIATION_CLOSURE','status':'OPEN','depends_on':['C22B_OPEN_BATH_CONTRACT','C22C_ATOMIC_ENERGY_COVERAGE']},
      {'id':'FULL_NUCLEAR_HIGH_ENERGY','status':'HOLD','depends_on':[]},
      {'id':'GENERAL_TRIAXIAL_TILTED_POLARIZED_CMB','status':'HOLD','depends_on':[]}],
    'next_contract_obligations':['Actual coefficients/domain and unavailable semantics for excitation and lowT CI',
       'Per-reaction charge,nuclear identity and energy conservation',
       'Excited-state/escape treatment and RR/DR/charge-exchange/bremsstrahlung energy coverage',
       'H1 versus D/T isotope quotient assumptions and threshold/binding-energy alignment',
       'Dominant omitted processes along new histories; no off-domain zero substitution',
       'New source/input/run identity,resource/lease admission and create-only output before future integration'],
    'EXECUTION':{'status':'C22B_COMPLETE_SCOPED','old_ODE':0},'PUBLICATION':pub,'BACKUP':backup,
    'global_error_bound':None})
create('SCIENCE_ACCEPTANCE.json',{'schema':'C22B_SCIENTIFIC_ACCEPTANCE_V1','created_KST':now,
    'status':'PASS_SCOPED_CONDITIONAL_COMPTON_MODEL','source_identity_sha256':source['identity_sha256'],
    'new_ODE':{'nominal_BDF':3,'reference_Radau':1,'successful_segments':72},'old_ODE_reruns':0,
    'saved_points':804,'accepted_points':6670,'full_state_size':75,'solver_state_size':72,
    'maximum_energy_relative_residual':max(v['measurements']['energy_relative_residual'] for x in s['mesh_acceptance'].values() for v in x['meshes'].values()),
    'maximum_reference_scaled_difference':max(v['max_scaled_difference'] for v in s['tighter_reference']['finite_uv_compton_lrs'].values()),
    'declared_n_T':'EXACT_ZERO_ALL_SAVED_AND_ACCEPTED','clipping':'NONE;smallnegativeUVandatomicresidualsretainedwithinregisteredgates',
    'analysis_summary_sha256':sha('analysis_v2/SUMMARY.json'),'independent_review_sha256':sha('evidence/independent_result_review/SAVED_DATA_REVIEW.json'),
    'atomic_diagnostic_summary_sha256':sha('atomic_diagnostics_v1/SUMMARY.json'),
    'full_thermochemical_radiative_closure':'OPEN','reference_scope':'oneLRSsameinputcase;finitecomparisonnotglobalbound',
    'historical_C22A_reference':'FAILED_PRESERVED;notretroactivelyrepaired',
    'rejected_analysis':'v1referenceplotnegative-timeautoscale;rawandnumericalgatesretained',
    'EXECUTION':{'status':'COMPLETE_SCOPED'},'PUBLICATION':pub,'BACKUP':backup,'DAG':dag,'global_error_bound':None})

report=f'''# BASS_CR C22B — Compton 에너지 피드백 연구 결과

작성 시각: {now}. Workflow: physmath-research-loop 1.0.0 / approval0.2.

## 판정

**C22B의 조건부 과학 결과는 PASS_SCOPED이다.** 기존 C22A에 prescribed isotropic CMB thermostat와 가스 사이의 Compton 열 교환을 실제 결합했다. 새 BDF 3개와 더 엄격한 Radau 1개를 실행했으며, 기존 C21O·NCP·C22A 계산은 복원 목적으로 재실행하지 않았다. 새 모델은 75개 전체 상태를 출력하고, 선언된 n/T 초기 0을 유지하는 72개 좌표에서 적분한다.

LRS에서 z=2의 T는 약 216.61 K에서 30.40 K, 전자밀도는 약 3.6171e-7에서 1.4604e-7 cm^-3, 누적 Thomson depth는 0.029266에서 0.022465로 바뀌었다. 이 결과는 고정된 원자 모형과 외부 CMB bath 아래의 비교다. Full thermochemical/radiative closure는 **OPEN**, `global_error_bound=null`이다.

원격 게시와 과학 계산을 구분한다. 이번 GitHub 쓰기 probe와 C22A Drive retry는 ACK를 받지 못했다. 2026-10-22 12:30:29 KST 실제 읽기에서 branch와 Draft PR96 모두 R head였다. 새 C22B 게시 완료나 삼중 백업 완료를 주장하지 않는다. 이후 생성되는 최종 authority sidecar가 이 문서보다 늦은 Git bundle·배송 ACK를 정한다.

## 1. 먼저 수행한 게시·백업 재시도

| 대상 | 실제 조치와 결과 |
|---|---|
| GitHub branch / PR96 | retry 전과 최종 read ACK. head R, open·draft·unmerged. |
| GitHub write | 46-byte blob 1회, 45.001초 뒤 ACK 없음. UNKNOWN_NO_ACK. 권한 거부를 관측한 것은 아니다. tree/ref/PR bulk mutation 0. |
| C22A Drive | 정확 파일명·지정 폴더 검색, 폴더 72개 항목 확인에서 match0; upload1회 44.001초 ACK 없음; 후속 검색도0. 검색 범위 밖 부재는 주장하지 않는다. |
| 기존 C22A Library / Dropbox | 실제 이전 성공을 재사용. 중복 업로드하지 않았다. |
| C22B 실행 전 checkpoint | Library ZIP+receipt succeeded ACK, Dropbox completed ACK·ID·466840 bytes. R1, byte readback NOT_RUN. |

상세 근거는 `evidence/retry_and_external_intake`, `evidence/checkpoint_backup`, `evidence/publication_final_remote_read.json`에 있다. 원 C21O Drive main UNKNOWN_NO_ACK, document NOT_RUN, recovery NOT_ATTEMPTED 상태는 별도 보존했다.

## 2. 최신 외부 intake와 authority

7개 저장소의 실제 advertised heads는 **1259**이다. 직전1255 대비 **+4 added /3 changed /0 removed**이며 관측은 2026-10-22 12:09:28 KST이다. 새 문서6개와 핵심 코드2개를 Git blob SHA1·크기로 검증했다. HH PHYS79에는 domain-guarded Voronov CI와 Savin D/H CX 부분 구현이 있지만 저온 CI·excitation·에너지 coverage가 OPEN이다. REC thermal code에는 RR/DR fit-derived energy moments와 external-UV closure가 있지만 해당 HEAD science IVP0이고 Compton 구현은 없었다. HE33은 C5까지, VigilODE 최신 P05는 preregistration이다.

REI220/BASS180 compact33 연구는 같은 mirror이며 125grid+2cancel+2full62oracle이다. 기존 대표 raw2쌍/4파일 PASS_SCOPED는 전체127 raw 재감사가 아니다. 최초127의 JSON실패·재적분, VigilODE P02 C6FAIL, HE85/REI219 미완료 campaign을 유지했다. 서로 다른 RR/DR·UV/T·tolerance/source ensemble을 합치지 않았고, 62→33 대수 축약을 측정 speedup으로 부르지 않았다.

권위 branch는 `research/cr-c21o-hheli-z2-sandbox-20261021`, PR96이다. Science C=`6b6db06e8148e6826a2d5bf7dbc53d362126ca62`, historical D=`f7ca6905729f7d8d36ca0605f7b1dd7ad5595819`, recovery R=`{R}`를 보존한다. C22A local handoff parent는 `005d30b71fd551c97aa368943c113828e639acf1`이다. 접근할 수 없는 이전 대화는 **UNAVAILABLE**, 원 핵반응 네트워크 PNG는 **NOT_RECOVERED_NOT_READ**다.

## 3. 물리 계약과 보존식

Non-tilted LRS, full Frobenius norm을 유지했다. Signed amplitudes를 먼저 더해서 `Pr=Pgamma+Pnu`, `Ptot=Pm+Pr`, `Pi_r=abs(Pr)`, `Pi_tot=abs(Ptot)`를 계산한다. Atomic gas는 isotropic stress closure이며 anisotropic matter stress는 별도 nonbaryonic Vlasov다. n,H1,D,T,He3,He4,Li6,Li7의21개 전하 상태를 명시한다. n/T 초기0은 선언된 inventory이며 미포함 종을 0으로 대신한 것이 아니다.

가스가 받는 열률을 양수로 두면

\\[
Q_C=\\frac{{4\\sigma_Tc\\,a_RT_b^4 n_e k_B(T_b-T)}}{{m_ec^2}},\\qquad T_b=2.7255(1+z)\\;{{\\rm K}},
\\]

\\[
J_C=\\frac{{Q_C}}{{Hn_{{\\rm Href}}(1.602176634\\times10^{{-12}}\\;{{\\rm erg/eV}})}},
\\qquad U'=U'_{{C22A}}+J_C,\\qquad L_b'=-J_C.
\\]

따라서 `U+B+V+E_RR_export+Wgas+WUV+L_b`가 같은 사건 에너지 장부 안에서 보존된다. `L_b`는 **부호 있는 누적 외부 에너지 수령량**이며 resident radiation이 아니다. `-L_b` redshift 항이나 positivity gate를 붙이지 않았고 Einstein source에 CMB density를 한 번 더 더하지 않았다. `U=(3/2)kBT(Nnuc+Ne)`에서 T를 구하므로 이온화에 따른 입자수 변화가 포함된다.

Inherited angular CMB의 elastic Thomson 진화는 유지한다. 새 bath의 spectral energy와 실제 evolving gamma distribution을 자기일관적으로 연결한 계산은 아니다. 유한 bath를 항상 Planck 형태로 강제하면 에너지 교환과 함께 photon-number source 조건이 필요하므로, 그 대안은 spectral/photon-number/rethermalization 계약으로 남겼다. 이는 일반적인 불가능성 주장이 아니다.

단위와 EOS 기준은 [Hui & Gnedin1997 Eq.2 및 Appendix A](https://arxiv.org/pdf/astro-ph/9612232)와 대조했다. [Chluba & Sunyaev2012](https://arxiv.org/abs/1109.6552)의 spectrum/thermalization 문제는 별도 범위로 구분했다. 삼각 tensor norm, bath 부호, 단위, EOS 방향미분을 독립 검토했다.

## 4. 새 입력과 실제 실행

초기 가스 T=300 K, z20→2, 201 saved times이다. 유한 UV6cohort는 초기 에너지[10,20,40,60,100,150]eV와 photons/Href=[0.05,0.25,0.003,0.0002,0.00001,0.000001]를 유지한다. Dark는 이 photon scale이0, FLRW는 초기 shear와 signed stress0, LRS는 Sigma=0.3,Pm=2e-4,Pr=8e-4이다. Photo+Case-A RR의 기존 rate와 fit-derived RR capture moment는 바꾸지 않았다.

| 실행 | 방법·tolerance | 상태 | saved / accepted |
|---|---|---|---:|
| dark_compton | BDF rtol3e-11,atol3e-13 | COMPLETED_SCOPED | 201 /611 |
| finite_uv_compton_flrw | 동일 BDF | COMPLETED_SCOPED | 201 /1521 |
| finite_uv_compton_lrs | 동일 BDF | COMPLETED_SCOPED | 201 /1523 |
| LRS tighter reference | Radau rtol3e-12,atol3e-14 | COMPLETED_SCOPED | 201 /3015 |

Run IDs는 `c22b_compton_bdf_20261022_v1`, `c22b_compton_radau_20261022_v1`이다. 총4개 새로운 궤적·72개 성공 segment, saved804+accepted6670이다. Runtime source identity는 `{source['identity_sha256']}`이며31개 파일을 freeze했다. 관측 CPU quota8,affinity0..8,메모리한도8GiB였다. Coordinator CPU0, nominal worker CPU2/3, reference worker CPU1을 사용했다. 각 numerical thread1, CPU55제외, 실제 lease discovery와 dispatch 재확인, create-only output을 지켰다. 이 관측은 exclusive CPU lease를 확보했다는 주장이 아니다.

## 5. 결과와 검증

| z=2 관측량 | 저장된 C22A LRS | 새 C22B LRS | 상대 변화 |
|---|---:|---:|---:|
| T [K] |216.6139188766|30.3958220568|−85.9677429%|
| ne [cm^-3] |3.61705008849e-7|1.46040138203e-7|−59.6245187%|
| H1 ionized fraction |0.0697957677691|0.0281719902488|−59.6365351%|
| tau_T |0.0292659808600|0.0224652804936|−23.2375617%|
| Sigma_F |0.0156323145746|0.0156321994002|−0.000736771%|
| Pi_r_F |0.000136547341550|0.000136722159958|+0.128027690%|

새 FLRW 최종T=30.26164524995K, darkT=6.10858052427K이다. LRS accepted 최대T는9916.1995835K다. CMB로 넘긴 누적 순에너지는1.153551299773eV/Href, 초기 장부 총에너지5.677836979412eV/Href의20.3167386%다. 이전 C22A 궤적 위의 Compton 누락 진단 적분2.53120424eV/Href와 동일한 물리량의 같은 궤적 평가가 아니다. 새 계산에는 온도→RR→ne→열률의 피드백이 들어가므로 두 값을 같다고 놓지 않았다.

최대 상대 에너지 장부 잔차는 **1.4171373336e-11**로 사전1e-8 gate 이내다. nucleus residual 최대2.24265e-14, charge·photon residual은약1.1e-15이하이다. n/T좌표는 모든saved/accepted표본에서exact0이다. 작은 음수 수치잔차는 clipping하지 않았다: 최소 UV약−1.32303e-14/Href, 최소scaledpopulation약−3.86252e-28이며 사전−2e-11/−2e-9 허용값 이내다. 이를 strict positivity로 표현하지 않는다.

같은 LRS 입력의 BDF–Radau7field 최대 정규화 차이는 T의 **9.5113328836e-9**, 기준은2e-7이다. 일반 field는 `max(abs(reference),1e-8*maxabs(reference),1e-30)`, bath는 균일peak로 정규화했다. Method·tolerance·case list·saved count를 계약과 직접 대조하므로 같은 run을 reference로 넣어 통과시킬 수 없다. 이 검산은 한LRS case의 유한 비교이며 global convergence 또는 physical accuracy bound가 아니다.

실제 발견한 구현 오류1개는 off-mode에서도 Compton온도 selector를 평가하던 분기였다. 1e8K에서 원C22A와 다른 거부를 일으켜, rate계산 전에 disabled return하도록 고쳤다. 이후9focused checks와 독립18저장상태RHS검사를 통과했다. 분석 그림v1의 reference time축 autoscale이 음의경과시간을 표시한 문제도 실제열람에서 발견했다. v1은보존하고 v2에0이상 xlim을 명시했다. CSV2개와 acceptedNPZ4개 및 나머지4PNG/4PDF는 byte-identical이다. 최종HISTORY.csv804행·14472수치cell이 원배열과float round-trip exact다.

과거 C22A Radau의 strict zero 실패는 그대로 FAILED_PRESERVED다. 새72좌표 구조와 새run이 그 기록을 사후복구하거나 과거 통과로 바꾸지 않는다.

## 6. 실제 atomic-rate coverage와 다음 연구

[Scholz & Walters1991](https://doi.org/10.1086/170587)의 H ground CI를 진단 전용으로 구현했다. Domain2000≤T≤1e8K, oneRy=13.605693122994eV, H1만이다. Table1 독립값7점과 fit의 최대차0.591638%는 원전fit수준0.6% 이내였고 Decimal65와의 산술차는6.23e-13이다. 원PDFbytes·표영상은 UNAVAILABLE이며 원전indexedtext와 독립표값에 한정한 근거다. Table3의1s→2s/2p계수 열배치는 확인되지 않아 typed UNAVAILABLE을 유지한다. T<2000K도 OPEN이다. activechemistry13.6eV와 진단threshold1Ry를 섞지 않았다.

| C22B LRS accepted 진단 | 유효구간 적분 [eV/Href] | 초기 총에너지 대비 | 유효 proper-time 구간 |
|---|---:|---:|---:|
| HG H excitation |0.0511134909990|0.900228224%|0.685333109%|
| SW91 H1 CI |0.000132197003465|0.00232829868%|2.21828089%|

HG excitation은5000–500000K에서 기존H1+D+T electronic-isotope equality profile을 사용한다. SW91은H1만이다. 범위 밖은 NaN+false mask이며, 0 대체·외삽·미확인 계수 활성화가 없다. Dark case는 두 진단 모두 OPEN/null이다. Compton은 이미 활성 항으로 기록했다.

포함된 RR의 **kinetic capture cooling** 전체적분은0.0369241733573eV/Href다. 위 excitation부분적분은 그1.38428261배, 같은 유효 구간 RR의 3.27376833배이며 instantaneous |Q|/(HUthermal) 최대3.82883796이다. 이것은 binding energy를 포함한 총 RR 방출 에너지와 다르다. Excitation의 실제 energy closure는 다음 연구 후보이다. 다만 유효 시간의 0.6853%만 평가했으므로  전체 누락 효과가 작다는 결론을 내릴 수 없다.

Saved 201개 표본의 적분은 accepted mesh 대비 excitation +4.00568%, CI +2.72792%다. 두 mesh의 domain 경계에서 사용하는 인접 interval도 달라져, 이를 순수 quadrature error bound로 해석하지 않는다. Accepted mesh도 정확해가 아니다. 다음 C22C는 저온 excitation/CI·RR/DR·CX·bremsstrahlung의 실제 coverage, 반응별 전하·핵종·에너지 보존, 유효 온도와 dominant omitted processes, isotope quotient/threshold 조건을 먼저 계약해야 한다. 이후 새 source/input/run ID로 실행한다.

Full nuclear high-energy와 general triaxial/tilted/polarized CMB는 HOLD다. 전체 thermal/UV/stars/nuclear network 완료를 주장하지 않는다.

## 7. 근거와 인계

`CONTRACT.json`, `SCIENCE_ACCEPTANCE.json`, `STAGE_RECORDS.json`, `DAG.json`이 판정과 20단계의 EXECUTION | PUBLICATION | BACKUP | DAG를 기록한다. `analysis_v2`가 최종 수치/그림, `atomic_diagnostics_v1`이 12개 새 진단, `atomic_diagnostic_figures_v1`이 coverage 그림이다. 독립 감사는 `evidence/independent_pre_ODE_review`, `evidence/independent_result_review`, root의 실제 그림 열람은 `evidence/root_figure_review`다. 원시 history와 기존 failed/rejected 기록을 유지했다.

배송 ZIP와 Git bundle은 원 계산 재실행 없이 복원·검토하도록 구성한다. 최종 업로드 ACK·실제 다운로드 검증·local commit/bundle SHA는 별도 `C22B_FINAL_AUTHORITY_20261022.json`을 우선한다. 이 과학 snapshot 시점의 GitHub publication과 Drive는 OPEN이며, 모든 완료 표기는 선언한 scope에 한정한다.
'''
create('REPORT_KO.md',report)
create('README.md',f'''# C22B prescribed Compton-bath pilot

Conditional scientific result: PASS_SCOPED. Full thermochemical/radiative closure OPEN.
Runtime identity: `{source['identity_sha256']}` (31 files).

Read `REPORT_KO.md`, `CONTRACT.json`, `SCIENCE_ACCEPTANCE.json`, and `STAGE_RECORDS.json` first.
Final numerical artifacts: `analysis_v2`. The rejected v1 reference time-axis image is preserved.
New runs: BDF3 + Radau1,72segments. Completed C21O/NCP/C22A runs were not rerun.

## Review stored evidence without ODE execution

The delivery ZIP verifier hashes and opens the same in-memory ZIP bytes. Use its recorded delivery SHA.
`analyze.py` reads completed nominal/reference histories and the preserved C22A baseline, validates the
registered methods/tolerances/cases and source hashes, then derives accepted summaries. It makes no ODE call.
Choose a new output directory when deriving analysis again; all outputs are create-only.

```bash
python3 analyze.py --nominal runs/c22b_compton_bdf_20261022_v1 --reference runs/c22b_compton_radau_20261022_v1 --baseline ../cr_c22a_thermochemical_20261022/runs/c22a_finite_uv_bdf_20261022_v1 --out review_new_unique
```

Do not start `run_pilot.py` merely to reconstruct completed results. Future scientific extensions require
new inputs, a new source freeze/run ID, actual resource and lease checks, CPU55/coordinator separation,
and one numerical thread per worker.

GitHub and Drive publication/preservation status is independently tracked. Read the final authority sidecar
for actual commit, bundle, upload ACK and byte readback evidence. No triple-backup claim is made.
''')
create('NEXT_THREAD_HANDOFF_KO.md',f'''# 다음 대화 인계 — C22B

{now}

## 완료된 실제 상태

- Runtime31files identity `{source['identity_sha256']}`.
- 새C22B BDF3+Radau1,72segments,각201saved,accepted611/1521/1523/3015. 모두PASS_SCOPED.
- 최대energyrelative1.4171373336e-11;7field tighterreference최대9.5113328836e-9<2e-7.
- LRSz2 T30.3958220568K,ne1.46040138203e-7cm^-3,tau0.0224652804936,bath수령1.15355129977eV/Href.
- 75full/72solver,declaredn/Texact0. oldC22ARadauFAILED_PRESERVED그대로. oldODE0.
- 최종analysis_v2. v1reference음의timeaxisREJECTED_PLOT보존. CSV804행·14472cells원배열일치.
- 새로운atomic진단12개(저장A3+B3의saved/accepted),ODE0/RHS0. C22BLRSHGExc유효적분0.051113491eV/Href(coverage0.6853331%),SW91H1CI0.000132197eV/Href(coverage2.218281%). fullcoverage미완료.

## 권위·게시·백업

원remoteR=`{R}`,branch research/cr-c21o-hheli-z2-sandbox-20261021,PR96open/draft/unmerged(최종12:30:29KST관측).
C22Aparentlocalhead005d30b71fd551c97aa368943c113828e639acf1. 새localcommit/bundle/배송ID는최종 `C22B_FINAL_AUTHORITY_20261022.json`을읽어라.
이번GitHub46byteprobe45.001snoACK,Drive기존C22A44.001snoACK. 권한거부라고단정하지말고반복bulkwrite하지말라. Library/Dropbox기존성공은재사용한다. 과학완료와remote게시완료를혼동하지말라.
Checkpoint Librarylibfile_37025ed8ca548191bf5415f69da10e48,Dropboxid:BSpOijBcT10AAAAAAD_h2Q,R1ACK;최종ZIP은별도authority가정한다.
원C21ODriveopen상태와기존복원COMPLETE_SCOPED를보존한다.

## 다음 연구

1. 최신refs/PR/외부실행/백업을실제관측하고변경된근거만읽는다. 현재7repo1259heads(+4/3changed/0removed),6doc+2codeblobs검증.
2. C22C는excitation-energy와실제저온atomicratecoverage계약부터. SW91H1CI는diagnosticonly,2e3..1e8K,H1only,1Ry;SW91excitationTable3계수열배치와<2000KOPEN.
3. 반응별전하·핵종·에너지,threshold/isotopequotient,유효T,dominantomittedprocess를정한뒤구현→가벼운검증→새입력/새run→분석→게시/백업.
4. FullspectralCMB/thermochemicalclosureOPEN. prescribedbath의누적L_b를residentradiation으로바꾸지말라. 추가EinsteinCMBdensity없음.
5. Fullnuclearhighenergy와generaltriaxial/tilted/polarizedCMBHOLD. `global_error_bound=null`.

Non-tiltedLRS/fullFrobenius/signedPr=Pgamma+Pnu/Ptot=Pm+Pr 규칙,atomicisotropic와별도Vlasov,21populations를유지한다.
접근불가대화UNAVAILABLE,원핵반응PNGNOT_RECOVERED_NOT_READ. REI220/BASS180mirror와대표raw4PASS_SCOPED≠127재감사,원JSON실패/재적분,VigilODEP02C6FAIL,HE85/REI219미완료를보존한다.

매단계EXECUTION|PUBLICATION|BACKUP|DAG를기록하라. 완료된C21O/NCP51/C22A/C22B를복원용으로재실행하지말라.
''')
create('PR96_UPDATE_DRAFT.md','''## C22B: couple Compton gas energy to an explicitly prescribed CMB bath

C22A's stored-history diagnostics found a material omitted Compton heat term. C22B adds that term to the gas thermal energy and the same flux with opposite sign to a signed cumulative external bath ledger. The inherited elastic angular CMB and Einstein source remain unchanged; full spectral radiation closure remains OPEN.

The new solver evolves72active coordinates and writes75full coordinates, keeping the explicitly declared n/T zero inventory exact. The old C22A Radau failure is preserved. No completed C21O/NCP/C22A calculation was rerun for recovery.

Three new BDF trajectories and one tighter same-input LRS Radau reference complete72segments. Saved/accepted energy, number, inventory and numerical-population gates pass. Maximum relative energy residual is1.41714e-11; maximum registered7field reference difference is9.51133e-9 against2e-7. The LRS finalT/ne/tau changes by−85.97%/−59.62%/−23.24% relative to storedC22A.

Independent source, tensor/norm, CSV and figure review passes within scope. The rejectedv1reference time-axis plot and repairedv2artifacts are both preserved. Low-temperature CI/excitation coverage and other energy providers remain incomplete; new SW91HCI is diagnostic only. `global_error_bound=null`.

This text is a prepared update, not evidence that PR96 was modified. Actual remote publication, bundle and backup statuses are recorded separately in the final authority.
''')
print(json.dumps({'status':'SCIENTIFIC_HANDOFF_CREATED','stage_count':len(stages),'source_identity':source['identity_sha256'],'old_ODE':0,'publication':pub['status']}))
