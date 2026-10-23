# BASS_CR / REI_BIANCHI C23B — 기준계와 실제 광전자 공급

작성일: 2026-10-23 UTC. 연구 단위: `C23B_SOURCE_FRAME_AND_PW19_SUPPLY`.

## 1. 판정과 적용 범위

**실제 PW19 스펙트럼으로부터 3개 redshift × 3개 원자 fit 채널의 광전자 공급을 계산하고, 등방적 parent-rest 전자 측도의 Lorentz 변환·유한 침적표 축약·proper decay clock·원자 source 조립을 구현 및 독립 검증했다. 판정은 `COMPLETE_SCOPED`이다.** 이 결과는 전체 21-population thermochemical/radiative closure의 구성요소다. 전체 물리 결합, 전체 cosmic-ray history 또는 완성된 핵반응 network를 뜻하지 않는다. `global_error_bound=null`, 전체 목표의 completion percent도 `null`이다.

새 source quadrature는 9개 사례, 통합 실행은 49 contractions / 147 finite-table queries / 120 clock evaluations / 6 primary-source assemblies다. 통합 단계는 이미 저장된 양의 quadrature atom 32,592개를 읽었다. 새 ODE는 0이며, C21O–C22D/C23A 및 NCP51의 완료 계산을 복원 목적으로 재실행하지 않았다.

이 과학 보고서는 게시 전 snapshot이다. 게시 commit·실제 provider ID·재다운로드 판정은 후속 `delivery/C23B_FINAL_AUTHORITY_20261023.json`, `delivery/STAGES_FINAL.json`, 최종 배송 영수증이 권위다. 하위 packet에 남은 `PENDING_PARENT_C23B` 등은 해당 시점 기록으로 보존한다.

| 축 | 이 snapshot의 상태 |
|---|---|
| EXECUTION | 새 유도·구현·구성요소 실행·독립 검토 완료, 기존 완료 science 재실행 0 |
| PUBLICATION | C23B 별도 경로의 additive commit 준비, PR96 draft 유지 |
| BACKUP | 이전 C23A 최종 문서 9개 추가 보존은 Library/Dropbox 실제 byte R3 PASS; C23B 배송본은 후속 receipt 참조 |
| DAG | C23B source-frame 구성요소 완료 → 저에너지 stopping/thermal exchange 및 실제 atomic-rate coverage → 보존적인 결합 → 새 입력 실행 |

## 2. 최신 refs·PR·외부 근거 조사

`intake/INTAKE_REPORT_KO.md`, `INTAKE_RECEIPT.json`, `ALL_SELECTED_TEXT_BINDINGS.json`에 조사 시각·pin·변화를 기록했다. 접근 가능한 7개 저장소의 advertised REST heads는 **1,285개**였고 직전 1,278 대비 **+7 added / 5 changed / 0 removed**였다. 선택한 53개 text, 625,625 bytes의 Git blob SHA1와 로컬 SHA256을 확인했으며, 51개는 tree size도 비교했다. 관련 PR14개는 관측 시점 open/draft/unmerged였다. 모든 branch의 모든 과학 raw를 재감사했다는 뜻은 아니다. API ref snapshot 뒤 이동한 HE37 HEAD는 별도 `POST_SNAPSHOT_HE37_MOVEMENT.json`으로 남겼다.

접근할 수 없는 과거 대화는 **UNAVAILABLE**이다. 외부 host의 실제 실행 process/lease는 intake 시점 **UNOBSERVED**이며, 저장소의 완료 보고와 현재 host 실행을 구분했다. 원 핵반응 network PNG는 **NOT_RECOVERED_NOT_READ**다.

| 재사용 후보 | 이번 확인과 다음 결합 조건 |
|---|---|
| REI221 ANGTHERM01, `6daf382ee698835e7a141378c232d1d97c1c5cf1` | 저장 C21O grid044/022를 사용하는 새10 trajectories와 finite M4의 221→41 축약, gas/binding/photon/escape/mean+shear-work ledger를 pin했다. prescribed background, M8/M16 차이 및 Li angular 기여를 보존한다. 10 trajectories를 재실행하지 않았다. |
| HE37, 초기 `9932e420535f5ad11c1aa7653f58683eb07f14cf`, 후속 `a5a670968cb1326375f394faa867c6b260c5840d` | H1 Le–Cambier Eq85/III.E의 stationary-heavy-target/isotropic-outgoing net number·heat·electron STF와 129-T 진단을 확인했다. 13.6 eV와 CCC 13.6058 eV의 공급 계약은 분리한다. |
| HH81, `b3ec271a96cb67e583bffa9b61533802838236f9` | H1/He4/Li7 finite CI, 7→3 hazard, 새3 parcel ODE, cold COM radiative-capture photon/recoil 장부. 실제 normal-frame/Lorentz 어댑터로 승격하지 않는다. HH82의 Li threshold→6 eV source gap은 별도 진행 중이었다. |
| REC127/128 | 완료 ANGULAR01의 405 rows와 escape-probability STF는 재사용 후보. LINE01 source-card/Lambert-W 계획을 완료 실행으로 세지 않았다. |
| 기존 CR geometry kernel, `ba39fc75521aa18705ec832d789e50dd5c6565bc` | stable kinetic energy, diagonal-Bianchi scaling, comoving counts, signed work, barycentric projection 및 energy rebind를 확인했다. 선택 scan 안에는 이번 Lorentz angular marginal/proper decay-clock/FS spectral contraction이 없었다. 전역 최초성 주장은 하지 않는다. |

REI220/BASS180의 compact33 mirror 관계, 최초127 raw의 JSON 실패·재적분 이력, 대표 raw4 비교의 `PASS_SCOPED`는 그대로 유지한다. 외부 RR/DR·UV/T·tolerance가 다른 ensemble은 C21O와 합치지 않는다. 62→33 및 221→41 대수 축약을 측정 speedup으로 부르지 않는다. VigilODE P02 C6FAIL 및 HE85/REI219의 과거 미완료 campaign도 후속 scoped 결과와 별도로 남긴다.

## 3. 실제 UVB 데이터와 원자 fit 계약

Taira, Kopenhafer & O'Shea(2025)의 데이터 release `10.5281/zenodo.15367103`, Git `863c3b7fa73a8510fbf57ee7b75ad1e8c34086de`를 사용했다. 원 ZIP 8,388,585 bytes의 SHA256은 `afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55`다. Zenodo MD5, 824개 ZIP member CRC, 선택 Git blob57개의 SHA1/size를 확인했다. release metadata의 CC0와 논문의 license는 구분했다. [논문](https://arxiv.org/html/2505.23544v1), [데이터 release](https://doi.org/10.5281/zenodo.15367103).

PW19 CSV51개를 조사했으나 **원 Cloudy-format과 실제 변환 관계를 확인한 z=2.316, 2.479, 2.649만 채택**했다. z 보간은 하지 않았다. 공급량은

\[
S(E)=4\pi\nu J_\nu,
\]

이며 단위는 erg s⁻¹ cm⁻² per dlnE이다. CSV 값은 bin-integrated energy가 아니다. 채택 구간에서 log photon-energy에 대해 log S를 선형 보간한다. 원 format→CSV 1,878개 값의 최대 상대차는 4.45×10⁻¹⁶이었다.

공식 [Verner photoionization 자료](https://www.pa.uky.edu/~verner/photo.html)의 ground-state HI/HeI/HeII fit을 채택했다. `photo.dat` SHA256은 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`다. 적용 photon domain은 각 fit threshold부터 50 keV까지이며 threshold는 **13.60 / 24.59 / 54.42 eV**다. 이 값은 채택한 원자 fit의 threshold이다. 정밀 isotope binding energy, 기존 C22의 13.6058 eV 또는 arbitrary-temperature thermal rate와 동일시하지 않는다.

전자 운동에너지 K=E−χ에 대한 per-target 공급은, ε=1.602176634×10⁻¹² erg/eV로 쓰면

\[
q_i(K)=\frac{S(K+\chi_i)\,\sigma_i(K+\chi_i)}{\epsilon\,(K+\chi_i)^2}
\]

다. 단위는 electrons target⁻¹ proper-s⁻¹ eV⁻¹이며 **bath에서 정지한 ground-state target, zero-recoil 근사**다. 표적의 열운동·여기상태·isotope shift는 이 계약 안에 들어 있지 않다. 이 source는 이미 bath frame에 있으므로 비영 boost를 다시 적용하지 않는다.

흡수 photon energy는 χΓ와 primary-electron kinetic energy의 합으로 기록한다. kinetic energy를 즉시 gas heat로 더하지 않는다. 50 keV 위 photon intensity가 있어도 원자 반응률의 채택 domain 밖이므로 rate는 **unknown/null**이다.

### 3.1 실제 9개 source 결과와 검증

Run `c23b_pw19_spectral_source_20261023_v1`은 3z×3채널, 양의 atom 32,592개를 생성했다. wall 2.4517 s / CPU 2.3984 s / maxRSS 74,336 KiB, worker CPU3·coordinator6·native1, lease RELEASED다. 다음 수치는 이 finite source representation 안의 수치 비교다.

| 검사 | 최대 상대차 |
|---|---:|
| Verner formula 대 독립 80-digit 평가 | 5.68×10⁻¹⁵ |
| Gauss8→16 | 5.24×10⁻¹⁶ |
| Gauss16 대 독립 photon-energy adaptive integral | 3.17×10⁻¹⁵ |
| photon = binding + kinetic 장부 | 1.72×10⁻¹⁶ |
| 독립 C9의 선별 6개 70-digit 적분 | 2.50×10⁻¹⁴ |

대표 z=2.479에서 저장된 수치로 계산한 kinetic-energy fraction은 다음과 같다. 분모는 채택한 photon fit domain에서 공급되는 primary-electron kinetic energy다. FS의 finite energy band는 [10, 9937.21] eV다.

| 채널 | mean K (eV) | K<10 eV | FS finite band | FS 위, 원자 fit 안 |
|---|---:|---:|---:|---:|
| HI | 3.73701137 | 0.66918417 | 0.33081583 | 9.55×10⁻¹⁰ |
| HeI | 7.07386341 | 0.40665431 | 0.59334566 | 3.18×10⁻⁸ |
| HeII | 19.96943547 | 0.09428961 | 0.90570953 | 8.59×10⁻⁷ |

이 값은 **실제 low-energy stopping/thermal-pool exchange가 다음 선행 과제**임을 보여 준다. 특히 HI source의 약66.9% kinetic energy가 10 eV 아래에 있다. 이 tail을 0, 100% heat 또는 외삽된 FS 응답으로 바꾸지 않았다.

### 3.2 입력 이상과 서로 다른 source identity

PW19 z=0 CSV626개 값은 약3.7656–3.76885×10¹⁹였으며, 13.59476499 eV에서 z=.04912와의 비는 약4.1587×10²⁵였다. z0 원 Cloudy-format을 확보하지 못해 원인을 결정할 수 없다. `SOURCE_ANOMALY.json`에 **QUARANTINED_UNRESOLVED_CAUSE**로 기록하고 원본을 보존했다. smoothing, 대체값 생성 또는 임의 단위 교정은 하지 않았다.

이 release와 C23A의 D1/P19V1 rate table은 별도 identity다. HeII Γ 비는 선택3z에서 1.211–1.643이었다. 공급 차이를 수치 오차로 지우거나 ensemble에 합치지 않았다.

## 4. 등방 전자 source의 정확한 boost와 계산 축약

이 단계는 표준 Lorentz kinematics의 재사용이다. [PDG Kinematics](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-kinematics.pdf)의 4-vector 및 time-dilation 식과, massive daughter의 isotropic boost에 관한 [Agashe et al.](https://arxiv.org/abs/1512.02265)을 근거로 한다. 전역 신규 이론이나 무조건적 no-go를 주장하지 않는다.

M=m_ec²=510998.95069 eV, u=γβ≥0, γ=hypot(1,u)로 놓는다. 작은 u에서도 γ−1을 잃지 않도록 δγ=u[u/(γ+1)]를 계산한다. rest kinetic energy K의 전자에 대해

\[
q=pc=\sqrt K\sqrt{K+2M},\quad
A=K+\delta\gamma(K+M),\quad B=uq,
\]

\[
K_{bath}=A+B\mu,\qquad\mu\sim U[-1,1]
\]

다. 따라서 B>0이면 [A−B,A+B] 위의 uniform kernel이고, B=0이면 Dirac다. **unpolarized isotropic rest electron marginal**이라는 전제가 필수다. 작은 endpoint의 cancellation은

\[
(A-B)(A+B)=[K-\delta\gamma M]^2,\qquad
K_-=d(d/K_+),\quad d=K-\delta\gamma M
\]

를 사용해 피한다. 매우 좁은 bin은 absolute endpoints의 뺄셈으로 판단하지 않고 `fsum(edge,-K,-center_shift)/B`로 μ 경계를 얻는다. 구간별 count, kinetic energy, total energy와 parallel pc를 해석적으로 계산한다.

FS의 선언된 piecewise-linear interpolation hat basis를 이 양의 angular kernel에 대해 먼저 적분하면, 이후 같은 source의 xi 조회는 node weights와 table row의 contraction이 된다. normalized-angle Bernstein polynomial 적분을 사용해 양의 number/energy basis를 유지했다. 이 축약은 **선택한 finite interpolant의 각도 적분**에 관한 것이며, FS 물리의 전역 오차를 없앤다는 뜻은 아니다. C23B에서는 timing benchmark를 수행하지 않았으므로 speedup 배수를 주장하지 않는다.

### 4.1 서로 다른 spectrum은 mean만으로 대체하지 않는다

T의 mean5.690 keV와 endpoints0/18.590 keV, n의 mean301.370 keV와 endpoints0/782.347 keV를 사용해 같은 rest mean을 갖는 진단 측도 두 가지를 만들었다. **실제 evaluated beta spectrum이 아니다.** T 진단의 FS finite-band kinetic fraction은 다음처럼 달랐다.

| u=γβ | mean-energy line | 같은 mean의 endpoint mixture |
|---|---:|---:|
| 0 | 1 | 0 |
| .05 | .9540164313 | .0699183456 |
| .2 | .1009719464 | .0167854234 |
| 1 | 0 | 0 |

두 측도는 같은 boosted mean을 갖지만 유한 영역의 응답은 다르다. 이 구성적 진단은 현재 측도와 finite-band 질문에만 적용한다. β spectrum, parent population, 방향 분포, stopping 또는 escape 모델의 검증을 대신하지 않는다.

## 5. proper decay clock와 에너지 소유권

N개 전자의 per-event rest yield, rest total electron energy E*, bath parent density n_b, proper mean lifetime τ를 사용한다. γ가 한 parent class에서 고정일 때

\[
\dot N_{event}=\frac{n_b}{\gamma\tau},\quad
\dot n_e=\frac{n_b N}{\gamma\tau},\quad
Q_{e,total}=\frac{n_b E_*}{\tau},
\]

\[
Q_{e,kinetic}=\frac{n_b}{\tau}\left(E_*-\frac{MN}{\gamma}\right),\quad
Q_{p_\parallel c}=\frac{n_b\beta E_*}{\tau}.
\]

마지막 식은 한 parent-axis 방향의 결과다. 등방 parent axes이면 ensemble net flux는 0이다. 같은 수의 반대 방향 beam은 flux만 상쇄하며 stress는 별도 계산해야 한다. single beam을 isotropic scalar source라고 부르지 않는다. comoving density에는 V=a_parallel·a_perp²를, 시간 좌표에는 dt/dη를, reference-normalized source에는 실제 reference density를 각각 명시적으로 사용한다.

이 장부는 electron component다. daughter charge·recoil, rest mass, neutrino, atomic binding과 parent loss에는 별도의 owner가 필요하다. cosmic-ray parent의 실제 spectrum/abundance와 charge-state-dependent decay는 아직 결합하지 않았다.

## 6. primary source의 보존적인 원자 조립

현재 assembler는 HI/HII/HeI/HeII/HeIII의 **5개 atomic fit label**이다. Full21 isotope network로 승격하지 않았다. explicit target population을 per-target source에 한 번만 곱하고,

\[
\dot n_{HI}=-r_H,\quad\dot n_{HII}=r_H,
\]

\[
\dot n_{HeI}=-r_{HeI},\quad
\dot n_{HeII}=r_{HeI}-r_{HeII},\quad
\dot n_{HeIII}=r_{HeII}
\]

를 적용한다. 자유전자 생성은 r_H+r_HeI+r_HeII다. thermal electron과 nonthermal electron의 구분은 후속 kinetic/thermal exchange가 담당한다.

z=2.479, explicit inventory HI=1, HeI=.083, 나머지 세 label=0의 진단에서 per-reference 결과는 다음과 같다.

| source | 값 |
|---|---:|
| 자유전자 생성 | 1.2362233337650286×10⁻¹² s⁻¹ |
| photon absorption energy | 2.213613805854393×10⁻¹¹ eV s⁻¹ |
| binding 증가 | 1.7352454706255568×10⁻¹¹ eV s⁻¹ |
| primary nonthermal kinetic energy | 4.783683352288363×10⁻¹² eV s⁻¹ |
| thermal heating | null |

He/H=.083은 이 assembler 진단 inventory의 선언값이다. FS2010 gas composition의 검증값으로 사용하지 않았다. isotope quotient는 H1/D/T 및 He3/He4의 threshold·cross-section·rate·recoil가 채택 정확도에서 같다는 계약 뒤에만 허용한다. missing isotope/rate를 0으로 채우지 않는다.

FS2010의 [원 논문](https://arxiv.org/abs/0910.4410) 및 source에서 x_i=x_HII=x_HeII, HeIII=0을 확인했다. 그러나 이번 자료로 numeric He/H까지 확정하지 못했으므로 실제 21-population gas에 대한 물리 결합은 **NOT_ADMITTED**다. 다른 논문의 Y=.24를 가져와 빈 계약을 채우지 않았다. 과거 low-xi header/C 충돌과 raw energy defect를 보존하고, 안전하게 pin한 high-xi MIT mirror만 finite-response 계산에 사용했다.

## 7. 독립 검증과 최소 교정

| 검증 단위 | 실제 범위 | 결과 |
|---|---|---|
| 독립 boost | 106개 K/u 사례, 832 bins, 80-digit 별도 angular quadrature | count/kinetic/total/parallel pc 정규화 오차 최대2.23×10⁻¹⁶ 수준; endpoint3.22×10⁻¹⁶ |
| 독립 decay clock | 방향 계약15개 | PASS |
| 독립 finite deposition | 9 spectra×3xi=27queries,7channels=189 comparisons; 별도 parser/direct μ integral | 최대 channel 상대차1.6937×10⁻¹⁴; positive weights; raw defect 보존 |
| 독립 UV provider | 저장 pin/outputs 및 32,592 atoms의 9개 재합산, 새 선별6개 고정밀 적분 | PASS_SCOPED_FINDINGS_CLOSED |
| 통합 campaign | 49 contractions,147queries,120clocks,6assemblies,16guards | 15개 summary checks PASS |
| 독립 integration C9 | 실행 source15개·output10개 hash; 저장6assemblies exact-rational incidence/energy audit | PASS_SCOPED |

통합 run `c23b_boost_and_source_20261023_v2`는 wall **3.087571727 s**, CPU **3.066876944 s**, maxRSS **21,420 KiB**, CPU1·coordinator0·native1이었다. source aggregate는 `df268a500575bfce7764a1ceeec4e5c0dac067a49c83a985a0fd237f87a4d780`이다. number partition 상대차는1.6473×10⁻¹⁶, energy partition2.8711×10⁻¹⁶, primary energy ledger1.5557×10⁻¹⁶이었다. 원자/source 모델 오차의 bound로 해석하지 않는다.

Provider C9는 manually constructed Verner coefficients가 pin 검사를 우회할 수 있음을 찾았다. 실제 9개 실행은 `from_table`을 사용해 유효했다. 원 code/history를 보존하고 constructor·consumer guard를 추가한 뒤 **새 targeted51 checks**만 수행했다. integration C9는 assembler의 threshold/support/epoch validation 누락을 찾았다. 저장9cases는 유효 domain이었고, 원 v2 code를 `implementation/history/v2/`에 보존한 뒤 **revision3에서 invalid17개와 changed-path valid1개만** 검사했다. 기존 campaign/source quadrature/독립 boost suite는 다시 실행하지 않았다.

현재 assembler SHA256은 `674ab7e51e6bdb3c5c4043a7024f708abdfb5d34d1867b1abcea3c4078106ec9`, 실행된 v2 원본은 `bbfb0c668adb13493a05236f272e1e2cf96c010a62a9960a0fffd7e222755110`다. `review/integration_c9/SOURCE_REVISION_MAP.json`이 실행 근거의 연결을 명시한다.

최초 통합 v1은 외부 작업의 해석 불명 lease 때문에, 최초 targeted guard v1은 coordinator CPU2가 busy였기 때문에 worker 시작 전 **NOT_RUN_RESOURCE_BLOCKED**였다. 외부 lease를 삭제하거나 CPU count를 임의의 CPU index로 해석하지 않았다. 조건이 사라진 뒤 새 run ID로 실행했다. 환경 차단을 science 실패로 기록하지 않는다.

## 8. 그림과 분석

`analysis/runs/c23b_saved_analysis_20261023_v3/`의 source/boost 그림은 실제 저장 output만 읽었다. source는 대표 z=2.479의 10,864개 양의 atom을 사용하고, boost는 저장32개 witness partitions를 이산 marker로 표시한다. neutron의 0을 제거하지 않도록 symlog 축을 사용했다. u축 위치는 이산 sample이며 가독성용 horizontal offset을 물리 이동으로 해석하지 않는다.

180 mm 및90 mm 버전은 실제 별도 레이아웃이다. v1의 clipping/overlap, v2의 legend 뒤 guide residual을 보존하고 새 v3 render로 수정했다. root와 작성 agent가 최종 PNG4개를 실제 열어 확인했다. 그림 생성은 physics 적분 또는 ODE 재실행이 아니다. 수치 불확실성은 위 검증표와 raw closure defect, source-domain 제약으로 함께 해석한다.

## 9. 다음 연구 DAG와 완료의 경계

| 노드 | 현재 | 다음 검증 계약 |
|---|---|---|
| N0 최신 intake·기존 배송 문서 복구 | COMPLETE_SCOPED | inaccessible conversations UNAVAILABLE; old Drive 항목 별도 추적 |
| N1 actual3z UV source + finite atomic fits | COMPLETE_SCOPED | z0 anomaly quarantine; z/thermal/isotope 보간 미채택 |
| N2 massive-electron angular boost·proper clock | COMPLETE_SCOPED | evaluated beta spectrum/parent direction·charge/recoil/neutrino owner 필요 |
| N3 positive finite-table contraction +5-label source assembly | COMPLETE_SCOPED | finite FS 수치만, physical gas/thermal closure OPEN |
| N4 저에너지 stopping·thermal/nonthermal exchange | OPEN, 다음 우선 노드 | K<10 eV, Coulomb/elastic/inelastic, excitation/secondary·escape, bath energy와 electron count |
| N5 실제 atomic-rate/isotope coverage | OPEN, N4와 병행 | photo/CI/Case-A RR/DR/CX, levels/molecules, T-domain, dominant omitted processes, isotope quotient, single-owner energy |
| N6 thermochemical/radiative conservative coupling | OPEN, N4/N5 이후 | binding+gas+nonthermal+radiation+escape+expansion/shear work; 외부 REI/HE/HH/REC 근거를 조건별 재사용 |
| N7 새 입력의 lightweight closed-parcel 검증 → coupled run | OPEN, N6 이후 | analytic limits, charge/nuclei/energy, tolerance/domain checks, lease/CPU55/native1/create-only |
| N8 full high-energy nuclear / general triaxial·tilted·polarized CMB | HOLD | 별도 물리·자료·자원 계약 |

원래 범위인 non-tilted LRS, full Frobenius norm, `Pi_r=abs(Pgamma+Pnu)`, `Pi_tot=abs(Pm+Pr)`를 유지한다. signed amplitudes, scalar norms와 cancellation을 구별한다. atomic gas는 isotropic stress closure이며 matter anisotropic stress는 별도 nonbaryonic Vlasov의 소유다. n/T 초기0은 선언한 inventory다. C21O는 prescribed UV/T + photo/Case-A RR → ne → photon Thomson 모델이며, 이번 구성요소 결과로 그 완료 범위를 소급 확장하지 않는다.

다음 loop는 N4/N5 계약을 먼저 결정한 뒤 구현→가벼운 검증→새 input/run ID 실행→분석→독립 review→게시/백업 순서로 진행한다. C23B의 검증된 source/boost/저장 atom은 hash와 domain이 동일하면 근거로 재사용한다.
