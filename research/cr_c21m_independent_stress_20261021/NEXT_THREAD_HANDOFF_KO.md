# BASS_CR C21L → C21M 마감 후 다음 대화 인계

기준일: 2026-10-21. **C21L 성분 분리 게시와 C21M 독립 초기응력 첫 pilot27을 완료했다.**
그 상태를 복원한 뒤 새 외부 반환을 수용하고, 필요하면 준비된 NCP98 refinement로
이어 간다. 이미 완료된 과학 ODE를 다시 수행하지 않는다.

## 1. 다음 대화에 복사할 짧은 prompt

```text
$physmath-research-loop, SciSpace, Exa, Wolfram을 사용해
cosmosapjw-quantum/bass_cr의 C21M 마감 상태에서 연구를 이어서 수행해줘.

권위 source는 BASS_CR C21M content 659c94312eb9c12ebb987de934459c12a63d67b0,
document head SELF_DOCUMENT_COMMIT_RESOLVE_FROM_FINAL_AUTHORITY_RECEIPT, PR https://github.com/cosmosapjw-quantum/bass_cr/pull/91다.
C21L component content는17244259d25f793a25e0874443a28806e7c31d17,
C21L document head는e954467132eef864a0fb86ba5de44f90f76b08e0, 원pilot content는
60a3f1cb0d8f0875820d18c0d10c448d480334c4다.
원 REI physics source3b85dedce84d37b3e165da00685a8a984950aafe를 유지해.

최종배송 BASS_CR_C21LM_RESEARCH_DELIVERY_20261021T082802Z.zip (17539759bytes),
SHA256 e0592be2859b7db606ec5a2ca008015c5ab02a3b2ff09fdd97fafe209cfe167a.
Drive UNKNOWN_NO_ACK — 객체 ID 미수신, Dropbox id:BSpOijBcT10AAAAAAD_fqQ, Library libfile_9ec015516fd48191bf149640f43bea7a.
Provider ACK와 실제 다운로드/byte검증 수준은 최종권위영수증을 읽고 분리해 보고해.

먼저 최신 Git refs/관련repo/PR/외부실행반환/Drive/Dropbox/Library를 확인하고
source/input/solver/tolerance/build/runtime/raw/검증 범위가 맞는 새결과만 DAG에수용해.
접근불가한대화나저장처는 UNAVAILABLE로기록하고 전역부재를단정하지마.

C21L81은재실행하지마. C21M 독립초기응력격자27은신규26실제적분+원C21L중심1
재사용으로완료됐어. sourcefull40state,101시점,FP64,DOP853rtol3e-11atol3e-13,
z20→4 collisionless non-tilted LRS야. matter/photon/massless-neutrino와
signedfullFrobenius/norm/cancellation을보존해. 원codePi_*_J_m3는Delta p/3이야.

확인된외부625,600+6,HH63와다른C15warm729/mirror/REC후처리도중복적분하지마.
REC116축응답법을C21M27에적용한최종결과는axis_response_diagnostic_results_v2야.
support15/heldout12×101의사후진단이며solver대체승인이나전역오차상계가아니야.

NCPactualexecution은NOT_RUN이고원격현재자원은아직관측하지못했어.
선택적인후속98점입력은grid_ncp_refinement98.json,
SHA768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04야.
초기조건98점검산만PASS이며첫pilot27마감의필수미완료분이아니야.
추가정밀격자가목표라면 CODEX_NCP_HANDOFF_KO.md의SSH/독립checkout/ncp_run.sh
plan/run/resume 명령으로가용자원내에서실행하고,analyze_campaign.py로기존26+새98+
원중심1을125점으로결합해. CPU55/기존lease/다른owner작업을보호하고coordinator를
계산에포함해. worker62는상한이지사용수나speedup보장이아니야.

각단계 EXECUTION|PUBLICATION|BACKUP|DAG를분리해갱신하고 실제결과를한국어로
게시·백업·보고해. 새대규모벤치마크는하지마. global_error_bound=null,
generaltriaxial/fullreionization/CMBextension은HOLD를유지해.
```

## 2. 권위 자료 복원

### 저장소와 게시 식별자

| 항목 | 식별자 |
|---|---|
| Repository | `https://github.com/cosmosapjw-quantum/bass_cr` |
| C21M content | `659c94312eb9c12ebb987de934459c12a63d67b0` |
| C21M document | `SELF_DOCUMENT_COMMIT_RESOLVE_FROM_FINAL_AUTHORITY_RECEIPT` |
| C21M PR | `https://github.com/cosmosapjw-quantum/bass_cr/pull/91` |
| C21L component content | `17244259d25f793a25e0874443a28806e7c31d17` |
| C21L document | `e954467132eef864a0fb86ba5de44f90f76b08e0` |
| C21L original content | `60a3f1cb0d8f0875820d18c0d10c448d480334c4` |
| C21L PR/branch | PR90 / `research/cr-c21l-rei-sigma-pi-pilot-20261021` |
| C21K parent document | `dc1c0c0721b74454958e5d16264c24ec465ba1d8` |
| REI source | `3b85dedce84d37b3e165da00685a8a984950aafe` |

소스와 실제 raw는 C21M content의 독립 checkout에서 읽고, 마감 영수증·게시 ACK·
provider 상태는 document head에서 읽는다. 최신 HEAD가 달라져도 기존 run manifest의
source를 바꾸지 않는다. Git 또는 배송본을 복원할 때 전체 repository를 재실행할
필요 없이 다음 두 연구 경로를 sparse checkout하면 된다.

```text
research/cr_c21l_rei_pilot_20261021/
research/cr_c21m_independent_stress_20261021/
```

### 배송 ZIP과 provider

| 항목 | 값 |
|---|---|
| 파일 | `BASS_CR_C21LM_RESEARCH_DELIVERY_20261021T082802Z.zip` |
| bytes | `17539759` |
| SHA256 | `e0592be2859b7db606ec5a2ca008015c5ab02a3b2ff09fdd97fafe209cfe167a` |
| Google Drive ID | `UNKNOWN_NO_ACK — 객체 ID 미수신` |
| Dropbox ID | `id:BSpOijBcT10AAAAAAD_fqQ` |
| Library ID | `libfile_9ec015516fd48191bf149640f43bea7a` |

이 표의 ID는 저장 위치를 가리킨다. 실제 provider ACK와 다운로드 후 byte 검증
완료 여부는 최종 영수증의 각 provider 항목을 그대로 수용한다. 접근이 끊겼으면
`UNAVAILABLE`을 기록하고 ACK나 Library ID를 추측해 만들지 않는다. 다운로드하면
ZIP bytes/SHA와 내부 manifest를 실제 내용에 대조한다.

역사적 최초 배송은 `BASS_CR_C21L_RESEARCH_DELIVERY_20261021T061130Z.zip`,
5,476,701 bytes, SHA256
`ca1a806e50be55a3743182d1dd580c8654c9d795a1fcc5e51d09f77385789e7f`다.
해당 배송의 Drive ID `1aLlPhZLGeWNVx2ZrzsbJImKtFWAsh-78`와 Dropbox ID
`id:BSpOijBcT10AAAAAAD_fUw`는 새 배송 식별자와 구분한다.

## 3. 완료된 과학 결과와 물리 convention

C21L81은 A=0을 고정한 preliminary LRS collisionless pilot이다. 원 raw에서
matter/radiation을 분리한 추가분을 실제 게시했고, 원 source340파일·v1/v2 provenance를
보존했다. 독립적인 초기 (P_{m,0})·(P_{r,0}) sweep로 재분류하지 않는다.

C21M은 초기 signed full 좌표

```text
S0  = [-0.012, 0, 0.012]
Pm0 = [-0.0002, 0, 0.0002]
Pr0 = [-0.0002, 0, 0.0002]
```

중 26개 신규점을 실제 적분했다. 중심은 C21L `s04_p04`의 원40×101 raw를
재사용했다. C21M run identity는
`ff462f48e264b2032ec50018e9969a6eb1808c7a6fc2a60139b98efacb01c05a`다.
초기 중심의 실제 full signed 값은
`S0=0, Pm0=-2.111149637247e-19, Pr0=+2.1111496372470007e-19`이며,
quadrature 수준 offset을 지우거나 새 builder의 완전 동일 상태라고 부르지 않는다.

| C21M27의 z=4 ensemble 최대 norm | 실제 값 |
|---|---:|
| Sigma | `0.0014449836382490454` |
| Pi_m | `1.2574783729509532e-5` |
| Pi_r | `6.344480064794384e-5` |
| Pi_tot | `7.577499571350794e-5` |

이는 이 ensemble의 최대이며 보편적 상계가 아니다. 그림은
`analysis_pilot27/initial_stress_slices.png/.pdf`와
`analysis_pilot27/opposing_stress_histories.png/.pdf`다. 첫 그림의 shear는 같은
S0의 zero-stress 기준점에 대한 최종 차이이며 최종 shear 그 자체와 구분한다.

원 source의 `sigma_hat=diag(-s,-s,2s)`, `pi_X_hat=diag(-p_X,-p_X,2p_X)`에서
`p_X=Delta p_X/3`이다. Full Frobenius norm은 `sqrt(6)*abs(s)`와
`sqrt(6)*abs(p_X)=sqrt(2/3)*abs(Delta p_X)`다. 원 half-contraction norm은
full보다 sqrt(2) 작다. Signed 좌표와 양의 norm을 혼동하지 않는다.

H가 초의 역수이고 응력이 J/m^3이므로
`P_X=sqrt(6)*(8*pi*G/c^2)*p_X/H^2`를 쓴다. 이는 에너지 단위 Einstein
coupling `kappa=8*pi*G/c^4`, `H_geom=H/c` 표현과 동일하다. Radiation은 photon과
존재하는 massless-neutrino를 분리한 뒤 tensor로 합친다. Pi_tot는 일반적으로
Pi_m+Pi_r와 다르다. UV와 unmodeled species는 임의의 수치0으로 대체하지 않는다.

## 4. 구현·검증·재사용 방법

`builder.py`는 각 A에 대해 canonical momentum distribution, cell population,
reference energy normalization을 새로 구성한다. 단일 A scalar만 바꾸는 shortcut을
사용하지 않는다. 원40성분 RHS, FP64, DOP853, n101, rtol3e-11/atol3e-13과
z20→4를 유지한다. Worker당 immutable template·matrix와 검증된 common-expression
재사용, bounded queue, case 병렬화, single-thread 설정을 적용했다.

다음 근거를 읽고 통과 범위 이상으로 승격하지 않는다.

- `checks/builder_checks.json`, `INDEPENDENT_BUILDER_REVIEW.json`: 양성·정규화·
  초기 사상·Hamiltonian·FLRW/r-only/m-only/opposing IC, 원/재사용 moment와 RHS
  비교 범위. 기존81 ODE 반복이 아니다.
- `runs/pilot26/`, `analysis_pilot27/PHYSICS_CHECKS.json`: 신규26 실제 실행과
  재사용중심의 저장40×101 검산. 최대 초기축 오차 `1.734723475976807e-18`,
  Hamiltonian 잔차 `2.220446049250313e-16`, massive number 잔차
  `4.440892098500626e-16`은 국소/저장수량의 일관성 검사다.
- `INDEPENDENT_OPERATIONS_REVIEW.json`, `checks/shared_operations_focused_v4.json`:
  fake-worker 운영·source binding·resume·resource 계산·lease·queue 범위다.
  fake-worker는 science로 집계하지 않고 실제 NCP 실행으로도 승격하지 않는다.
- `INDEPENDENT_CLOSEOUT_REVIEW.json` 및 하위 수치·그림·axis review: 실제
  source/raw/그림에 대한 독립 검토 범위를 읽는다.
- `checks/campaign_compatibility.json`: 범용 다중 run 분석기가 기존27의 NPZ60개
  배열과 CSV 공통 값을 동일하게 만들었고 중복좌표 거부를 확인했다. 미래125 검증은 아니다.

REC116 축 재구성식 `Fhat=F(S,m,0)+F(S,0,r)-F(S,0,0)`을 실제 C21M27에
적용한 결과는 `axis_response_diagnostic_results_v2/`다. Support15/held-out12의
101개 시점에서 최대 절대잔차는 signed S `1.2601685821e-9`, Pm
`1.1647880057e-9`, Pr `1.4831875142e-9`, Ptot `2.5829708927e-9`다.
Pointwise relative의 작은 분모를 가리는 floor는 없다. Exact-zero actual은
undefined mask를 보존한다. Decimal80 보조 계산은 정확한 유리수 연산이 아니며,
v2에서 그 명칭을 바로잡았다. 원 v1 결과와 실행 소스는 보존돼 있다.
이 방법은 사후 진단으로만 채택했고 production surrogate를 승인하지 않았다.

## 5. 외부 결과 수용 범위

시작 시 공개 advertised branch head 1,224개를 일곱 관련 repo에서 열거하고 관련
PR/source/manifest/실행 반환과 provider 검색 범위를 조사했다. 모든 branch의 모든
파일·비공개 대화를 읽었다는 뜻이 아니다. `EXTERNAL_UPTAKE.json`,
`external_evidence/`, C21L `component_split_20261021/LIVE_REF_INTAKE.json`과
복구 영수증을 읽고 이후 새 반환과 구분한다.

| 결과 | 채택 범위·중복 방지 |
|---|---|
| REI PR198 | HEAD `8bd35af5f11c7ea5945b656be1c013d1c1933498`, 고정 source/results `b140170ce0c58159368b6b81be49ac35ca764851`; 기존625 분해와 신규600+6. Same PR147 physics, reduced8/65시점, half→full sqrt(2). 외부 전체raw 현재 재검증 주장 없음. |
| HH PR127 | A=0인 full signed63 control과 component 후처리. 독립 초기matter 축이 아니며 재실행하지 않는다. |
| REI PR213 / BASS PR176 | 같은 warm source-on729의 mirror. REI result `c8e9f67aa031ffb33a9b0347bdea61dbb01fb746`, 실행 source `82372ed8db68085868603d4267a630ed9cde6abb`, C15 owner `80825585f9fe31d2ee0d5af545ada3fa1f52be72`. 현재 collisionless pilot로 섞지 않는다. |
| REC PR116 | 동일 warm729의 axis 후처리. 새 ODE나 mesh가 아니다. 방법만 C21M에서 별도로 검산했다. |
| HE PR82 | 계약/연계 체크포인트. 실제 신규 science 완료로 수용하지 않는다. |

## 6. DAG와 다음 행동

| Node | 상태 |
|---|---|
| C21K 이론·최적화·게시 | `COMPLETE_SCOPED` 유지 |
| C21L 원81·preliminary 그림 | `COMPLETE_SCOPED` |
| C21L component 분리·외부path 분석·게시 | `COMPLETE_SCOPED`, 실제 content 위 SHA |
| C21M 독립 initial stress builder | `COMPLETE_SCOPED` |
| C21M 신규26+재사용중심1 pilot27·그림 | `COMPLETE_SCOPED_PRELIMINARY` |
| C21M REC116 방법의 사후 검산 | `COMPLETE_SCOPED`, production surrogate 미승인 |
| NCP98 입력·초기조건 검산·실행/분석 코드 | `OPTIONAL_NEXT_UNIT_READY` |
| NCP98 실제 적분 | `NOT_RUN` |
| NCP의 현재 실자원 | `UNOBSERVED` |
| 일반 triaxial/full 재이온화/CMB 확장 | `HOLD` |

시작 시 네 상태를 따로 기록한다. `EXECUTION`은 실제 수행량과 검증 범위,
`PUBLICATION`은 실제 branch/PR/content/document SHA, `BACKUP`은 provider ACK와
download 검증 단계, `DAG`는 의존성과 COMPLETE/NOT_RUN/HOLD다. 연구 마감은
첫 pilot27의 완료를 뜻하며 NCP98를 필수 미완료로 되돌리지 않는다.

선택98은 signed 축 S0=[-.012,-.006,0,.006,.012], Pm0=Pr0=[-.0002,-.0001,0,
.0001,.0002]의 nested125에서 기존27점을 제외했다. 검토한 C21L/HH/PR198 입력과의
추가중복은 없었으며 98점의 초기 분포 양성·정규화·사상만 검산했다.
입력 SHA256은 `768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04`다.

실행을 이어가면 동봉 `CODEX_NCP_HANDOFF_KO.md`의 실제 SSH 계약과 독립 sparse
checkout, Python3.12/requirements, source binding, ncp_run.sh plan/run/resume,
26+98+ref125 분석 명령을 따른다. `/tmp/bass_cpu_leases`는 기존 현장 표준과
대조하고 CPU55·coordinator·다른owner를 보호한다. 명목64CPU/128GB를 관측한
자원으로 쓰지 않는다. 실제 source 충돌이나 P0 오류가 있으면 해당 promotion만
멈추고 실패 근거를 보존한다. 다른 독립 작업은 가용자원 안에서 계속한다.

새 결과는 원본을 바꾸지 않는 별도 run/manifest/content/document와 새 배송본으로
게시한다. Google Drive/Dropbox/Library ACK/object ID/bytes/SHA 및 실제 다운로드
검증을 구별해 남긴다. 수행하지 않은 speedup, scaling, memory 개선을 주장하지
않고 새 대규모 성능 benchmark를 수행하지 않는다. 모든 결과에
`global_error_bound=null`을 유지하며 C21F/G/H/I/J/K의 원 science, 실패 raw,
역사적 NOT_PUBLISHED 및 HOLD를 보존한다.

## 최종 문서 identity와 백업 확인

이 Git 문서에 쓰인 `SELF_DOCUMENT_COMMIT_RESOLVE_FROM_FINAL_AUTHORITY_RECEIPT`는 자신을 포함한 commit을 뜻한다.
파일에 자기 commit SHA를 넣는 순환을 피했으며, 별도 배포용 handoff와
`FINAL_AUTHORITY_RECEIPT.json`에는 실제 document SHA를 채운다.

통합 ZIP은 Library 성공 ACK 후 실제 다운로드 bytes·SHA256 일치를 확인했고,
Dropbox는 완료 ACK와 크기 일치를 확인했다. Drive는 320초 뒤 응답 없는 호출을
중단했으며 ACK와 object ID를 받지 못했다. Drive의 파일 부재나 실패를 확정하지
않는다. 모호한 호출은 정확한 파일명·폴더 조회와 필요 시 다운로드 검증으로
해소하고, 확인 없이 같은 파일을 중복 업로드하지 않는다.
