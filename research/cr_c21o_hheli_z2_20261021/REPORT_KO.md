# C21O 최종 과학 보고서: 조건부 H/He/Li–LRS z=20→2 pilot

## 결과와 해석 범위

샌드박스에서 새로운 독립 초기응력 격자 45개와 비교·상쇄 사례 6개를 모두 적분했다. 21개 population의 전하 반응에서 계산한 전자밀도를 원 LRS photon Thomson 항에 연결했고, 물질·광자·무질량 neutrino의 signed stress와 full Frobenius norm을 보존했다. 기존 C21L 81개와 C21M/N의 완료 계산은 재실행하지 않았다. 최종 분석은 `analysis_v2/`이며, 이전 그림과 실패 검사는 삭제하지 않았다.

이는 **처방 UV/온도 아래 photoionization + Case-A RR + trace-gas electron–Thomson 결합**의 preliminary model이다. H/He/Li의 주요 원시 isotope와 모든 전하 상태를 포함하지만, 모든 가능한 단명 핵종·모든 핵반응·열수지·별·UV 전달을 완성한 모델은 아니다. 해당 확장은 `RESEARCH_DAG.json`에서 OPEN/HOLD로 남긴다. 작은 생략 에너지 비율은 누락 반응이나 장시간 오차를 보증하지 않는다.

## 최신 외부 성과 수용

7개 관련 저장소의 advertised branch refs 1,246개와 최근 PR metadata 280개를 조사했다. 직전 1,240개 snapshot 대비 새 ref 6개와 변경 ref 4개를 기록했다. 이는 조사 시점의 advertised heads 전수이며 모든 PR 본문·모든 과거 대화·모든 백업 raw의 전수 다운로드를 뜻하지 않는다. 상세 근거는 `intake/github/`, `intake/backups/` 및 `intake/FINAL_INTAKE_SYNTHESIS_KO.md`다.

BASS_HE HE31/PR84의 실제 3개 H/He–electron–Thomson–LRS sandbox 실행을 수용했다. Source head `88e415c45d8607c85cd3ab36aabeaed4378820ce`, execution pin `1c8a56aac89d0e40ede8770009f80ebca40a4d2c`다. 이 반환은 reduced-Q, HII=HeII, HeIII=0, residual=0, z≥4의 제한을 가진다. C21O의 full 21-population z20→2 계산으로 소급 대체하지 않았다. REI PR211/RUN19 compatibility와 PR150 H/He Grackle source도 구분했다. R9 Python rate provider와 원 Verner 입력 6개를 source SHA·size로 대조하여 재사용했다.

Drive 알려진 폴더 72개 파일, Dropbox bass_cr 46개 파일, Library의 관련 권위 문서/배송본을 점검했다. 이전 C21N Drive ACK가 없는 항목은 UNKNOWN으로 보존했다. 접근할 수 없는 개인 대화는 UNAVAILABLE이다. 조사 범위 밖에 새 결과가 전혀 없다고 주장하지 않는다.

## 물리 유도와 단위

LRS orthonormal frame에서 shear와 성분별 stress는 diag(-s,-s,2s), diag(-p_X,-p_X,2p_X)다. 따라서 full contraction은 각각 6s², 6p_X²이며 Δp_X=3p_X다. Full norm은 source half-contraction norm의 sqrt(2)배다.

proper-time H_t[s^-1]와 pressure[J/m³]를 사용하는 source에서 signed 좌표는

\[
S_F=\sqrt6s/H_t,\qquad P_X=\sqrt6(8\pi G/c^2)p_X/H_t^2.
\]

이는 κ_E=8πG/c⁴, H_geom=H_t/c로 쓰는 사용자의 정의에 대응한다. Σ=|S_F|, Π_X=|P_X|이고 P_r=P_gamma+P_nu, P_tot=P_m+P_r다. Tensor를 먼저 더하고 norm을 취하므로 일반적으로 Π_tot≠Π_m+Π_r다. Cancellation은 1−|P_m+P_r|/(|P_m|+|P_r|)로 기록한다. 완전히 0인 분모는 소스에 선언된 처리에 따르며, 반대 부호 입력의 실제 FP 잔차를 강제로 0으로 덮지 않았다.

원자 abundance Y_i=n_i/n_Href를 isotope scale D로 나누어 x=D^-1Y를 적분했다. 이는 매우 작은 Li abundance를 O(1) fraction으로 다루는 좌표 변환이며 clipping이나 사후 정규화가 아니다. 전자는 n_e=n_Href q^T D x로 닫힌다. Photo operator P, beta B, RR coefficient operator R에 대해

\[
x'=D^{-1}[(P+B)Y+n_{Href}(q^TY)RY]/H,
\]
\[
J_x=D^{-1}[P+B+n_eR+n_{Href}(RY)q^T]D/H.
\]

마지막 rank-one 항과 H 및 Thomson opacity에 대한 교차 미분을 포함한 전체 block Jacobian을 구현했다. Wolfram symbolic 결과는 `theory/WOLFRAM_SYMBOLIC_RECEIPT.json`, 직접 유도는 `PHYSICAL_CONTRACT_KO.md`와 `theory/CONDITIONAL_NETWORK_THEORY_KO.md`에 있다.

H1/D/T는 q=0,1, He3/He4는 q=0,1,2, Li6/Li7는 q=0,1,2,3, 자유 n까지 총 21 populations를 추적한다. 각 isotope에 동일한 elemental electronic rates를 적용한다는 근사를 명시적으로 opt-in했다. 실제 n/T 초기량 0은 선언된 후기 초기조건이고, beta adapter가 없는 것으로 숨긴 0이 아니다. 반면 CI/DR/CX/분자/음이온/core-Auger/secondary electron/전체 nuclear collision channels는 UNMODELED다. 원시 전핵종 목록 전체를 활성 반응망으로 오인하지 않는다.

## 입력, 구현, 최적화

Signed 초기 좌표는 S0∈{-0.6,-0.3,0,0.3,0.6}, Pm0∈{-5e-4,0,5e-4}, Pr0∈{-1.2e-3,0,1.2e-3}다. 5×3×3=45개이고 각 초기조건의 양성·정규화·Hamiltonian constraint를 확인했다. A를 바꿀 때 massive distribution과 normalization을 함께 재생성했다. |S0|=0.6에서 Pm의 허용 구간은 약 [-0.00064259,0.00128519], Pr은 ±0.00140328이므로 선택 격자는 검증된 범위 안에 있다.

원 C21M/N builder의 angular family는 matter W=1+A P2(mu), radiation W=1+k P2(mu)다. Matter의 continuum 양성 범위 A∈[-1,2]를 사용하고 radiation은 원 source의 더 좁은 |k|≤0.5 계약을 유지한다. 초기 photon/neutrino에는 공통 k_gamma=k_nu를 주므로 Pm와 Pr은 독립이지만 photon과 neutrino의 초기 quadrupole까지 서로 독립인 격자는 아니다. 두 radiation sector의 이후 stress는 각각 저장한다. Continuum의 <P2²>=1/5 관계는 pressure moment의 기준식이며, 실제 target 역상은 고정 finite-volume quadrature의 fields로 평가한다.

UV는 10,20,40,60,100,150eV cohort, soft/hard tanh 이력과 지정 T(z)를 사용한다. 선언된 external UV는 별·복사전달 결과가 아니며, 60eV soft photon은 HeII 문턱을 넘는다. 따라서 그림의 이른 HeIII 전이는 실제 우주 helium 재이온화 시점의 추정이 아니다. LiI의 중간 재결합 증가는 LiII 초기조건과 낮은 처방 T, UV turn-on 이전의 RR에 대한 조건부 응답이다.

62-state L8 모델은 FP64 BDF, rtol=3e-11, scaled atol=3e-13으로 z20→2의 eta 균등 201개 시각을 저장했다. L12는 78 states다. 추가 6개는 FLRW Radau 1개, 양·음 extreme L12 2개, Thomson-off 1개, 초기 Pm=−Pr 상쇄 2개다. 원 C21L의 DOP853/tolerance/끝점은 수정하지 않았다.

실제 적용한 최적화는 C21N worker-local immutable momentum/angular 준비, 동일 reduction 순서의 moment/RHS 재사용, 공유 field 평가, analytic block Jacobian, exact-binary64-z rate/operator 단일-entry cache, 독립 multiprocessing, bounded dispatch, BLAS/OpenMP 1 thread다. x/ne를 cache하지 않으며 보간하지 않는다. solve_ivp가 RHS 배열을 보유하므로 반환 배열을 위험하게 재사용하지 않는다. Source/input/runtime/raw를 결속하고 create-only·미시작 case만 resume하도록 구현했다.

Resource 관측은 affinity/cgroup CPU quota/RAM/current load/lease를 사용한다. CPU55를 보호하고 coordinator 비용을 포함한다. 512MiB/worker,768MiB coordinator,1GiB reserve는 보수적 입장 예산이며 측정된 peak RSS가 아니다. 실제 host af4832b34a81은 affinity0–8, quota8CPU, memory8GiB였고 4개 및 5개 worker를 사용했다. NCP 64CPU 실행·scaling·speedup·memory improvement는 측정하지 않았다.

## 실제 결과

다음은 지정 45-case ensemble의 값이며 보편적 상계가 아니다.

| 변수 | 전체 저장 trajectory 최대 | z=2 endpoint 최대 |
|---|---:|---:|
| Σ | 0.6000000 | 0.03196565589 |
| Π_m | 5.778775954e-4 | 4.053340970e-5 |
| Π_r | 2.195128290e-3 | 7.428382738e-4 |
| Π_tot | 2.698542566e-3 | 7.826594133e-4 |

초기 shear가 큰 branch는 감쇠하고, S0=0이라도 응력이 있으면 shear가 생긴다. 초기 Pm=+5e-4,Pr=−5e-4인 상쇄 사례는 실제 Ptot≈3.37e-19에서 출발하지만, 성분이 다르게 진화하여 z2에서 Ptot≈−5.4185e-5와 Σ≈5.0645e-5에 도달한다. 반대 부호 사례도 별도 raw로 보존했다. 초기 총응력이 작다는 이유만으로 이후 전체 응답을 작게 대체할 수 없다.

z20→2 Thomson 누적 optical depth는 0.07477690819–0.07493000527이다. 이는 z0까지의 관측 τ가 아니다. z2에서 n_e≈5.99619783e-6 cm^-3, FLRW n_e/n_Href≈1.164026655이다. 이 scenario의 FLRW endpoint는 HII/DII≈0.9999843843, HeIII≈0.9999667053, LiIV≈0.9999227752다. Li6/7 electronic fraction의 동일성은 공통 rate 근사의 결과다. LiI 저장점 최대 fraction0.6237606574는 z≈10.60017에서 나타난다.

생략 thermal+ionization+externalUV energy의 최대 ε_H²는 1.323852510e-7이다. 같은 순간 상태를 고정해 positive density만 추가하는 대수 진단에서 δH/H≤ε/2≈6.62e-8이다. 전체 coupled trajectory와 누락 reaction/model effect에 대한 전역 오차 상계가 아니므로 `global_error_bound=null`을 유지한다.

## 검산과 독립 검토 범위

| 검사 | 수행 범위·결과 |
|---|---|
| Atomic rates/operator | Photo36·RR24 literal comparison; RR diff0; 441 complex-step Jacobian entries max relative4.76e-16; exact-z cache/direct bytes 일치 |
| 원 LRS source 비교 | 동일 electron 값의 3개 상태×40 RHS values=120개 exact numerical equality (`assert_array_equal`); signed-zero/raw-byte 검사는 별도 수행하지 않음. 새 chemistry trajectory와 옛 collisionless trajectory의 동등성 주장이 아님 |
| 전체 Jacobian | 3,782=62×61 central-difference entries, max scaled7.8866e-8. 불변 u=0의 음수 trial이 source-domain을 벗어나 해당 열(index3)은 제외 |
| 저장 raw51개 | source/input/build/raw SHA binding, 2,340,147 saved FP64 values 검산 |
| 핵자·isotope | max baryon relative2.6645e-15, Li6/7 fraction difference1.3323e-15, 최소 population0 |
| Radiation | 42,029,100 angular sampled values, 최소0.1786649783; 연속 각도 양성 증명이 아님 |
| Hamiltonian·massive number | 실행 영수증의 hash-bound 검사 재사용; 후처리에서 RHS를 다시 돌렸다고 계상하지 않음 |
| FLRW BDF/Radau | max full-state absolute1.8418e-9; local tolerance scale ratio858.47. 전역 오차가 tolerance 안이라는 주장은 하지 않음 |
| 두 L8/L12 사례 | max ΔΣ4.1818e-11, max ΔΠ_r8.6329e-11; common ell0..8 radiation moments max2.0780e-4. 전체 계층 수렴 확립 아님 |
| Thomson on/off | 다른 물리 모델 비교. max signed photon stress difference1.20065e-5; solver accuracy test 아님 |
| 운영 | 완료 receipt.case 대조, worker source identity, fresh single-task admission, exact runtime resume guard를 첫 ODE 전에 수정·집중검사 |
| 독립 검토 | 별도 agent의 source/algebra, operations, PNG5/PDF2 검토; 자기 검사를 독립 과학 모델로 계상하지 않음 |
| 그림/분석 | v1/v2 CSV2+NPZ1 byte-identical; 표기/가독성만 수정. Endpoint CSV↔NPZ495 scalar,45격자좌표·출력14개hash 확인 |

첫 atomic test의 absolute roundoff 기준 실패와 당시 source/output을 보존했다. 큰 beta/H의 cancellation roundoff에 맞춘 scaled FP 기준으로 수정했으며 물리식을 바꾸어 통과시킨 것이 아니다. 운영 검토에서 발견된 완료 case 혼입 P0는 첫 science run 전에 case identity 검증으로 닫았다. 그림 v1의 P_nu escape·주석 overlap·표시 대비 문제는 analyzer만 수정하고 ODE 없이 v2로 닫았다.

## 게시·백업·DAG

2026-10-21 15:55 UTC 마감 근거: EXECUTION=51/51 COMPLETE_SCOPED, PUBLICATION=content `6b6db06e8148e6826a2d5bf7dbc53d362126ca62` / draft PR96 게시 완료, BACKUP=Library·Dropbox 실제 ACK와 동일 크기 확인 / Drive UNKNOWN_NO_ACK다. 308개 게시 파일의 Git blob SHA와 local bytes를 모두 대조했다. Main ZIP은 28,473,836 bytes, SHA256 `5741bcac7943e91cdacd8ca15cd8c34ff8a83b7b08b6d8a6bfad31cdb5b2c781`이다. Provider download/readback은 NOT_RUN이며, local ZIP·복원 검사와 구분한다. Drive는 329.7초 동안 응답하지 않은 도구 호출 이후 unknown으로 보존하고 중복 업로드하지 않았다. 실제 document head와 별도 closeout ZIP ACK는 이 문서 commit 이후 external authority로 고정한다. 과학 실행 원본과 main ZIP은 변경하지 않는다.

전체 thermal/UV/stellar/nuclear feedback, 추가 isotope/Be7/molecules, 일반 triaxial/tilted/CMB polarization 확장은 이 pilot에서 완료하지 않았다. NCP actual C21O execution=NOT_RUN이고 이 51-case pilot의 완료 조건에는 필요하지 않다. 새 host에서 원 완료 계산을 다시 실행하는 대신 우선 저장 결과를 읽고 새로운 물리 입력 또는 미완료 작업만 별도 run으로 진행한다.

## 원전

- Verner et al. photoionization author data: https://www.pa.uky.edu/~verner/photo.html ; https://doi.org/10.1086/177435
- Verner & Ferland RR author data: https://www.pa.uky.edu/~verner/rec.html ; https://doi.org/10.1086/192284 (fit temperature3K–1e9K)
- ACROPOLIS nuclear-spectrum reference: https://arxiv.org/abs/2011.06518 (확장 경계 조사; full nuclear code를 이번 활성 ODE로 채택하지 않음)
- SciPy solve_ivp: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- SciSpace/Exa 실제 조회·출처 및 isotope/UV 관련 검토: `theory/PRIMARY_SOURCE_RECEIPT_SANITIZED.json`. 원 추출 논문 전문은 게시하지 않는다.
