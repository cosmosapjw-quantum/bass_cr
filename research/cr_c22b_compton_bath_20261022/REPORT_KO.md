# BASS_CR C22B — Compton 에너지 피드백 연구 결과

작성 시각: 2026-10-22T12:36:20.834796+09:00. Workflow: physmath-research-loop 1.0.0 / approval0.2.

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

권위 branch는 `research/cr-c21o-hheli-z2-sandbox-20261021`, PR96이다. Science C=`6b6db06e8148e6826a2d5bf7dbc53d362126ca62`, historical D=`f7ca6905729f7d8d36ca0605f7b1dd7ad5595819`, recovery R=`a5e12c5f3e6d323e211d65fefad34060ec07eff0`를 보존한다. C22A local handoff parent는 `005d30b71fd551c97aa368943c113828e639acf1`이다. 접근할 수 없는 이전 대화는 **UNAVAILABLE**, 원 핵반응 네트워크 PNG는 **NOT_RECOVERED_NOT_READ**다.

## 3. 물리 계약과 보존식

Non-tilted LRS, full Frobenius norm을 유지했다. Signed amplitudes를 먼저 더해서 `Pr=Pgamma+Pnu`, `Ptot=Pm+Pr`, `Pi_r=abs(Pr)`, `Pi_tot=abs(Ptot)`를 계산한다. Atomic gas는 isotropic stress closure이며 anisotropic matter stress는 별도 nonbaryonic Vlasov다. n,H1,D,T,He3,He4,Li6,Li7의21개 전하 상태를 명시한다. n/T 초기0은 선언된 inventory이며 미포함 종을 0으로 대신한 것이 아니다.

가스가 받는 열률을 양수로 두면

\[
Q_C=\frac{4\sigma_Tc\,a_RT_b^4 n_e k_B(T_b-T)}{m_ec^2},\qquad T_b=2.7255(1+z)\;{\rm K},
\]

\[
J_C=\frac{Q_C}{Hn_{\rm Href}(1.602176634\times10^{-12}\;{\rm erg/eV})},
\qquad U'=U'_{C22A}+J_C,\qquad L_b'=-J_C.
\]

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

Run IDs는 `c22b_compton_bdf_20261022_v1`, `c22b_compton_radau_20261022_v1`이다. 총4개 새로운 궤적·72개 성공 segment, saved804+accepted6670이다. Runtime source identity는 `e4e5ce42693d473939e72ac3cd2ade32cd4a342993524df94ccf121eb6afbd52`이며31개 파일을 freeze했다. 관측 CPU quota8,affinity0..8,메모리한도8GiB였다. Coordinator CPU0, nominal worker CPU2/3, reference worker CPU1을 사용했다. 각 numerical thread1, CPU55제외, 실제 lease discovery와 dispatch 재확인, create-only output을 지켰다. 이 관측은 exclusive CPU lease를 확보했다는 주장이 아니다.

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
