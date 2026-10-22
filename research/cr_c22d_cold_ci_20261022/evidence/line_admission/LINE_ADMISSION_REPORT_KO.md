# C22E 선복사 admission: 저장된 C22D 해에서 방향별 팽창을 판별

## 확보한 결과

**C22D의 저장 시점 804개와 solver 수락 시점 8,047개를 재사용한 최소 진단 단위를 완료했다.** 4개 계산, 합계 8,851개 시간 표본에서 모든 광자 방향의 순간 적색편이율이 양수다. LRS 계산의 전체 표본에서 최솟값은 `min(Hγ/H)=0.8775255128608411`, 최댓값은 `max(Hγ/H)=1.2449489742783177`이다. 방향별 팽창률의 폭 `3|s|/H`는 처음 약 0.36742346에서 마지막 약 0.01914546으로 줄어든다. 이 결과는 실제 저장된 signed H와 s에 적용한 대수적 판정이다. 각 시점에서 방향 전체를 다루지만, 시간 표본 사이의 극값은 별도 의무로 남는다.

이 계산으로 확보한 것은 선복사 처리를 위한 **운동학적 입력과 부호 판정**이다. 실제 cell 크기·column, line A/f/profile, 2γ spectrum, residence/destruction, RR cascade와 splitting-resolved mixing 입력은 아직 공급되지 않았다. 따라서 excited-level 제거와 즉시 경계 탈출의 물리적 admission은 `REGIME_NOT_ESTABLISHED`이며, 해당 수치는 JSON에서 null이다. 다음 물리 작업은 이 입력을 확보하여 시간척도와 에너지 이동을 계산하는 것이다.

실행은 `c22e_line_admission_20261022_v1` 한 번이다. 새 ODE 0, 완료 ODE 재실행 0, RHS 호출 0, atomic-rate provider 호출 0, model import 0이다. 기존 4개 raw와 재사용한 accepted-summary 파일은 전후 SHA-256이 동일하다. **global_error_bound=null**을 유지한다.

![저장된 C22D 해의 방향별 팽창 진단](c22e_line_admission_20261022_v1/DIRECTIONAL_EXPANSION.png)

## 1. 정의에서 계산식까지

상속한 non-tilted LRS metric은 signature `(-,+,+,+)`에서

\[
ds^2=-c^2dt^2+a^2\{e^{-2b}(dx^2+dy^2)+e^{4b}dz^2\},
\qquad s=\dot b,\quad H=\dot a/a
\]

로 쓴다. 따라서 `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`이고 `H_perp=H-s`, `H_parallel=H+2s`다. 원 공급자 `einstein_vlasov.py`의 metric·출력 정의, `canonical_fv.py`의 transverse/longitudinal physical momentum 변환, `lrs_boltzmann.py`의 angular Liouville 항과 부호가 일치한다. 이번에는 이 파일들의 정의를 읽었으며 import하거나 RHS를 호출하지 않았다. 관련 파일은 동결 source identity에 포함돼 있다.

공간 병진 대칭 아래 자유 비행 광자의 comoving momentum이 고정되면 physical momentum 성분은 `p_i ∝ a_i^-1`이다. 광자 방향 `μ=p_parallel/|p|`에 대해

\[
\frac{d\ln\nu}{dt}
=-[(H-s)(1-\mu^2)+(H+2s)\mu^2]
=-[H+s(3\mu^2-1)].
\]

또한 `d ln|p_parallel|/dt=-(H+2s)`이므로

\[
\dot\mu=\mu[-(H+2s)+H+s(3\mu^2-1)]
=-3s\mu(1-\mu^2).
\]

`u=μ²`는 `[0,1]`에 있고 `Hγ=H-s+3su`는 u에 대한 affine 함수다. 그러므로 **각 시간에서 방향별 최솟값·최댓값은 두 끝점만 평가하면 정확히 정해진다**.

\[
H_{\gamma,\min}=\min(H-s,H+2s),\qquad
H_{\gamma,\max}=\max(H-s,H+2s).
\]

이 계산은 별도 angular grid를 요구하지 않는다. `H>0`인 본 입력에서는 모든 방향의 순간 적색편이 조건이 `-H/2<s<H`와 동치다. 유한 표본 각각의 방향 최적화를 두 스칼라 연산으로 바꾼 것이 이번 물리에 기반한 계산 단순화다. 전체 radiative transport를 소거한 것은 아니며, wall-time 비교 캠페인은 실시하지 않았다.

저장된 full Frobenius convention은 `signed_Sigma_F=√6 s/H`, `Sigma_F=√6 |s|/H`다. 코드에서 이를 대조했고 s의 부호는 저장된 signed s에서 직접 읽었다. `3|s|/H=√(3/2) Sigma_F`는 방향별 팽창률 폭을 평균 팽창률로 나눈 진단이다. atomic gas의 isotropic stress closure와 별도 nonbaryonic Vlasov matter stress는 상속한 범위로 유지된다.

## 2. 실제 입력과 실행 범위

물리 source identity는 `2e065d2ec2605fcee4bd9f6444e90b58f85bbf047f4d1444dfe7e386eb828c72`다. raw `history.npz` 4개는 부모가 확정한 SHA-256과 각 `RECEIPT.json`의 source/history identity를 확인했다. accepted 값은 이미 완료한 `analysis_v1/*_ACCEPTED.npz`에서 재사용했다. 해당 파일은 `ARTIFACT_MANIFEST.json`의 SHA/크기를 확인하고, 보존된 eta/Y가 각각 raw의 `accepted_eta/accepted_Y`와 원소별 동일한지 확인했다. accepted H·s·rates를 다시 계산하지 않았다.

`LINE_ADMISSION.csv`는 tier/case/mesh/time, H·signed s, directional endpoints, ratio·부호, a/z/T/ne/nHref/H1 ground, H1 2s/2p 사건률, 6개 UV cohort의 photon 수와 energy를 담는다. 저장된 `H1_excitation_events_per_H_per_eta`에 `dη/dt=H`를 곱해 사건률의 단위만 `events/Href/s`로 바꿨다. 이 rate는 이미 계산된 finite-source H1 n=2 충돌 여기 부분집합이며, RR cascade photon source는 이 안에 없다.

실행 전 실제 affinity는 CPU 0–8, quota는 8 CPU분, memory limit은 8 GiB였다. 메모리 여유는 약 2.81 GiB였다. 알려진 lease root와 바로 아래 lease/resource/state 폴더에서 JSON lease 기록 0개, discovery error 0개를 관찰했다. exclusive lease를 획득했다고 주장하지 않는다. coordinator CPU 0과 보호 CPU 55를 사용하지 않고 진단은 CPU 4에 고정했으며, native thread 수는 실제로 1이었다. 실행 wall 4.775154516 s, process CPU 4.624651476 s다. 이 시간에는 입력 검증과 출력 쓰기가 포함된다.

## 3. 네 계산의 결과

아래는 accepted mesh 결과다. 각 계산의 saved mesh 201점에서도 방향별 부호 판정은 동일했다. LRS 최솟값/최댓값이 같은 것은 공통 초기 H·s가 해당 ratio 극값을 정하기 때문이다.

| 입력 | accepted 표본 | 최소 Hγ/H | 최대 Hγ/H | 최대 3\|s\|/H | 마지막 3\|s\|/H |
|---|---:|---:|---:|---:|---:|
| BDF registry control LRS, CI off | 1,618 | 0.8775255129 | 1.2449489743 | 0.3674234614 | 0.0191454556736 |
| BDF LRS, CI on | 1,618 | 0.8775255129 | 1.2449489743 | 0.3674234614 | 0.0191454556573 |
| BDF FLRW, CI on | 1,616 | 1.0 | 1.0 | 1.418460716e−20 | 4.378431133e−21 |
| 더 엄격한 Radau LRS, CI on | 3,195 | 0.8775255129 | 1.2449489743 | 0.3674234614 | 0.0191454555940 |

LRS에서 가장 작은 absolute Hγ는 마지막 시점의 약 `6.58006683e−18 s^-1`이고, 가장 큰 값은 초기 약 `1.48458627e−16 s^-1`이다. 모든 입력에서 `Hγ,min<=0`인 표본은 0개다. 이는 현재 표본에서 모든 방향이 redshift하는 운동학적 조건을 충족함을 뜻한다. Sobolev escape나 실제 경계 탈출을 채택하려면 velocity gradient 외에 opacity, redistribution, boundary와 destruction 입력이 필요하다.

FLRW에서 signed s는 solver의 작은 수치 잔차를 그대로 보존했다. `H±s`는 float64에서 H와 같게 반올림되지만 `3|s|/H`에는 최대 약 `1.42e−20`이 남는다. 데이터나 그림을 만들 때 s를 0으로 치환하거나 clipping하지 않았다.

CI on/off에 따른 LRS 전단의 매우 작은 차이는 부모의 strict-reference 비교에서 분해되지 않은 범위다. 위 끝자리 차이를 새로운 CI 전단 효과로 채택하지 않는다. CI/registry 효과의 과학적 비교는 C22D의 별도 `MATCHED_EFFECTS.json` 및 독립 검토를 따른다.

## 4. 실제 rate/source coverage와 남은 에너지 계약

| 항목 | 현재 확보된 값 또는 누락 입력 | 상태 |
|---|---|---|
| directional expansion | 실제 저장 H,s와 위 직접 유도 | `COMPUTED_SCOPED` |
| n=2 충돌 여기 주입 | 저장 finite-source H1 2s/2p 사건률 | `CONDITIONAL_INPUT_DIAGNOSTIC` |
| cell geometry·column | 실제 길이·column·경계 | `REQUIRED_INPUT_UNAVAILABLE`, null |
| Lyα opacity·준위 수명 | A2p, f, profile, fine-structure convention | 같은 누락 상태, null |
| 2s two-photon 방출 | A2s와 정규화한 differential spectrum | 같은 누락 상태, null |
| residence·destruction | scattering redistribution, recoil, true absorption, escape 경계 | 같은 누락 상태, null |
| collisional return·mixing | downward thermal provider 및 splitting-resolved e/p mixing | 같은 누락 상태, null |
| RR cascade | capture state와 cascade branch별 수·에너지 | 같은 누락 상태, null |
| excited-state PI/CI | 해당 state의 실제 문턱·단면적 | 같은 누락 상태, null |
| secondary electrons | energy-sharing/yields와 neutral-inelastic 경쟁 | 같은 누락 상태, null |
| peculiar velocity | 추가 line-of-sight gradient 또는 명시적 무시 계약 | 같은 누락 상태, null |

기존 addendum에 downward CCC 후보의 header/SHA가 기록돼 있지만, 이번 진단은 해당 source를 새 rate로 채택하거나 평가하지 않았다. A/f·2γ·mixing 원전을 새로 읽었다고 기록하지 않는다. 실제 spectrum이 없으므로 2γ의 두 적분정규화 검사는 `NOT_RUN_REQUIRED_INPUT_UNAVAILABLE`다. 임의 spectrum을 만들어 그 검사를 완료시키지 않았다.

다음 adapter에서는 **원자 방출**, **공명 대역 이탈**, **공간 경계 탈출**을 구별한다. `2p→1s`는 준위 에너지 이동이며, 적색편이로 Lyα 공명을 벗어난 photon은 계산 영역의 continuum radiation에 남을 수 있다. boundary export는 실제 경계를 통과한 에너지다. scattering cycle에서 전체 photon 에너지를 gas heat로 적립하지 않고 실제 recoil·Doppler energy transfer의 반대값만 gas에 준다.

현재 H1 n=2 source에 β를 곱해 gas cooling을 변경하려면 나머지 에너지가 excited level, resident photon, absorption 중 어디에 남는지 먼저 정한다. 필요한 장부의 한 형태는

\[
\frac{d}{dt}(U+B+E_{exc}+R_{line}+R_{2\gamma}+V_{UV}
+W_{exp}+L_{boundary}+L_{RR}+L_{bath})=0
\]

의 반응별 상쇄다. CI는 기존 `ΔU=-χ ΔC_CI`, `ΔB=+χ ΔC_CI`, CI export 0을 그대로 사용한다. RR cascade를 resident radiation으로 옮길 때 원 Case-A `L_RR`와 새 resident 항에 같은 에너지를 두 번 넣지 않는다. excited population을 추가하면 기존 H1 neutral inventory를 ground/excited로 분배하여 핵종 수를 보존한다.

isotropic resident radiation을 별도로 가정하면 per-Href 에너지는 expansion에 대해 `R'=-R`, 이에 대응하는 work는 `W_R'=R`이다. angular line radiation을 채택하면 stress-work `σ:π`와 각도·주파수 수송을 함께 연결한다. atomic gas가 isotropic이라는 가정만으로 새 line radiation의 isotropy가 정해지지는 않는다.

빠른 준위 제거와 즉시 escape의 수용에는 실제 입력으로 `t_level/t_macro`, `t_escape/t_macro`, excited fraction, destruction probability를 평가해야 한다. 현재 이 네 값, τscat, τtrue, β는 모두 null이다. 이 자료 부족을 모든 optically thick regime의 배제 명제로 바꾸지 않는다.

## 5. 가벼운 검증과 연구·코딩 연결

작은 synthetic fixture는 실제 과학 입력과 분리했다. `H=2`에 대해 s 양수·음수·0, stationary 방향을 갖는 경우, redshift/blueshift가 섞인 경우를 검산했다. 별도 exact `Fraction` 계산으로 `u=μ²`의 convex combination을 확인하여 endpoint 결과와 대조했다. H 또는 s 누락은 null로 남고, H<=0·NaN·bool·shape 불일치는 현재 진단 정의역에서 거부한다. signed s를 norm에서 복원하는 경로는 없다. CI/여기 energy exchange는 exact rational 상쇄를 확인했으며 실제 원자 rate 검증과 분리했다.

| 이론 단계 | 실제 처리와 근거 |
|---|---|
| R1 연구 위치·계약 | 부모의 `NEXT_LINE_ENERGY_CONTRACT_KO.md`에서 geometry/source admission을 최소 단위로 고정 |
| R2 근거·재사용 | source identity, raw receipt, 완료 accepted NPZ의 바이트·eta/Y binding 재사용 |
| R3 주장·전제 정렬 | non-tilted LRS, signed s, H>0, finite time sampling, missing-source null 명시 |
| R4 가설·표현 탐색 | 각도격자 대신 u=μ² affine 표현 선택 |
| R5 구성적 유도 | metric→momentum→Hγ·μdot→두 endpoint 극값 도출 |
| R6 독립 검증 | inherited momentum/metric 부호 대조, exact rational convex-combination fixture |
| R7 판별 검증 | 새 diagnostic ID로 8,851 표본 실제 계산 |
| R8 결과 판정 | sampled directional redshift 확보; physical line admission은 입력 의존성 OPEN |
| R9 정식 결과·코딩 연결 | 식·단위·누락 상태를 `directional`·CSV/JSON 계약에 반영 |
| R10 종료·재개 | 진단 단위 완료, 다음 source/geometry 수집과 energy adapter 조건 인계 |
| 코딩 단계 | 실제 처리와 근거 |
| C1 목표·baseline | 완료 C22D source/raw/analysis pin 고정 |
| C2 식–데이터–코드 | raw H,s → endpoint; per-eta 사건률×H → per-second |
| C3 수치 설계 | angular 극값은 대수식; 시간 interpolation·새 ODE 없음 |
| C4 DAG·자원 | 실제 lease/affinity/memory 관찰, CPU4·thread1, coordinator/CPU55 보호 |
| C5 구현 | create-only 진단기·coverage·CSV/NPZ/JSON 작성 |
| C6 구현 검증 | sign/missing/invalid input fixture 및 serialization 완료 |
| C7 과학 검증 | inherited signed full Frobenius 일치와 reaction ledger 확인 |
| C8 수치·재현성 | input hash·accepted binding·전후 불변, 실행 시간/환경 기록 |
| C9 독립 검토 | exact-rational 검산과 원 metric/momentum 표현 대조; 별도 부모 reviewer에 source/result 전달 |
| C10 판정·인계 | 실행·물리 수용·게시·백업을 아래 네 축으로 분리 |

새 strong no-go 성과는 채택하지 않았다. NG1–NG7은 이번 단순한 kinematic equivalence와 유한 입력 진단의 신규 배제 정리 심사에 해당하지 않는다. 실제 watchdog 조치는 angular grid라는 추가 수치화가 현재 부호 질문에 필요하지 않음을 endpoint 식으로 해결한 것이다. 기존 정확도나 물리 목표를 바꾸지 않았다.

## 6. EXECUTION | PUBLICATION | BACKUP | DAG

| 축 | 이 패킷에서 실제로 확인한 상태 |
|---|---|
| EXECUTION | read-only algebra 1회 완료; saved804/accepted8047; ODE/RHS/provider/model-import 0; PNG 실제 판독 PASS |
| PUBLICATION | 이 패킷은 local create-only 산출물이다. 부모의 실제 commit·remote ACK로 게시 상태를 확정한다. |
| BACKUP | 이 패킷 자체는 저장 서비스에 전송하지 않았다. 부모 archive/provider/readback 영수증과 결합한다. |
| DAG | C22E 최소 운동학·누락 진단 COMPLETE_SCOPED → 실제 atomic-line/geometry/secondary source 계약 → level/resident-radiation adapter 선택. Full thermal/radiative OPEN, full nuclear high-energy 및 general triaxial/tilted/polarized CMB HOLD. |

접근하지 못한 대화는 `UNAVAILABLE`, 원 핵반응 PNG는 `NOT_RECOVERED_NOT_READ`다. 기존 외부 campaign·JSON/reintegration 실패 및 복원·백업 상태는 부모 authority를 유지한다. 이 진단이 그 이력을 수정하거나 새 독립 ensemble을 추가하지 않는다.

주요 산출물은 `diagnose_line_admission.py`, `c22e_line_admission_20261022_v1/LINE_ADMISSION.json`, `LINE_SOURCE_COVERAGE.json`, `LINE_ADMISSION.csv`, `LINE_ADMISSION_ARRAYS.npz`, `FIXTURE_CHECKS.json`, `DIRECTIONAL_EXPANSION.png/pdf`다. 정확한 input/code/output SHA와 실제 명령은 JSON/manifest에 들어 있다. 이미 완료된 본 진단을 복원 목적으로 재실행하지 말고 보존된 파일을 재사용한다.
