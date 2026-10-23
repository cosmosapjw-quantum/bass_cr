# C23B 최종 integration C9

## 판정과 실행 identity

Root의 `c23b_boost_and_source_20261023_v2` 저장 결과는
**PASS_SCOPED**로 수용한다. 실제15개 source pin과 worker가 봉인한10개
파일의 size/SHA256가 모두 일치했고, source aggregate는
`df268a500575bfce7764a1ceeec4e5c0dac067a49c83a985a0fd237f87a4d780`이다.
이 검토는 source·저장 출력의 읽기와 저장 값의 유리수 검산으로 수행했다.
boost/FS 기존 suite, provider quadrature, 전체 campaign은 재실행하지 않았다.

실제 저장 campaign은49contractions,147table queries,120clock evaluations,
6primary assemblies를 포함하며 저장된 PW19 electron atoms32,592개를
소비했다. 새 ODE0, source quadrature 재실행0, 완료 계산 재실행0이다.
기록된 worker wall3.087571727s, CPU3.066876944s, peak RSS21420KiB,
worker CPU1/native1, coordinator CPU0, exit0, lease RELEASED를 확인했다.
초기 root v1은 foreign lease encoding 때문에 worker 시작 전 막혔다는
이력을 보존하고, root v2의 과학 결과와 구별한다.

## Target 밀도와 stoichiometry

각 rate는 absorbing target 하나당 proper second로 정의된다.
population x가 reference inventory 하나당 해당 target 수일 때
extent I_k=x_k*Gamma_k를 한 번만 적용한다. 이 코드에는 population의
추가 곱이나 전자 밀도의 추가 곱이 없다. 반환 단위는 reference당
proper second다. physical-volume source가 필요하면 이후 n_ref를
한 번 적용해야 하며, 현재 함수가 그 변환을 암묵적으로 수행하지 않는다.

HI,HeI,HeII의 공통 event extent를 I_H,I_1,I_2라 하면

\[
\dot x_{HI}=-I_H,\quad\dot x_{HII}=I_H,
\]
\[
\dot x_{HeI}=-I_1,\quad
\dot x_{HeII}=I_1-I_2,\quad
\dot x_{HeIII}=I_2,
\quad\dot n_e=I_H+I_1+I_2.
\]

이 incidence는 H 및 He nucleus 수를 각각 보존하고
dot(x_HII+x_HeII+2x_HeIII)-dot(n_e)=0을 준다.
6개 저장 assembly를 입력 JSON의 정확한 binary-float 유리수 값에서
독립 검산했다. 모든 incidence 잔차는 유리수로 정확히0이다.
저장 FP64 population source의 최대 정규화 차이는1.8839852351131732e-18,
energy source의 최대 상대차이는7.721441870766823e-17였다.
근거는 SAVED_EVIDENCE_AUDIT.json에 있다.

## 에너지 및 thermal/nonthermal 분리

동일한 target 가중치로 absorbed photon, primary binding, primary electron
kinetic source를 계산한다. 선택한 rest-target/zero-recoil 근사에서
photon=binding+kinetic이고 기존 저장잔차는 승인된5e-14 기준을 만족한다.
binding은 threshold 증가분의 소유자이며 전자 kinetic source와 분리된다.

`thermal_heating_source_eV_per_reference_s`는6개 모두 null이다.
freed-electron count는 charge ledger이고 thermal-electron 수로 이름을
바꾸지 않는다. finite FS component의 heat 결과를 primary kinetic source에
중복해서 더하지 않는다. secondary transport, stopping, low/high-energy
tails, radiation backreaction은 해당 후속 소유자에게 남는다.

PW19 saved atoms는 bath/rest-target 입력이다. campaign은 이들을
`frame='bath'`, `units='electrons_per_target_per_second'`로 만들고 u0으로
소비한다. parent-rest beta witness의 per-event measure와 clock 경로가
분리돼 있으며 bath source를 다시 boost하거나 decay clock에 넣는
guard도 저장 결과에서 PASS다.

HI/HeI/HeII는 선택한 Verner fit labels이다. 이를21population의 isotope
mapping으로 승격하지 않는다. 새 HI threshold13.6eV는 기존 다른 모델의
13.6058eV ledger로 자동 이식되지 않는다. 관련 isotope/threshold mapping은
계약을 명시해 연결해야 한다. finite50keV photon 공급 구간 바깥의
흡수율을0으로 채우지 않으며, 반환값은 선언한 finite source에 해당한다.

## API finding과 최소 교정

최초 assembly 구현은 frame 및 per-target 단위를 확인하면서도
`threshold_eV`와 `photon_support_eV`를 검증하지 않은 채50keV domain을
출력했다. 실제9개 source case는 의도한 범위였으므로 저장 v2 결과는
유효하지만, 다른 범위의 향후 입력을 같은 domain으로 표시할 수 있었다.

Parent 승인 후 **primary_source_assembly.py 하나만 revision3으로 교정**했다.
실행된 v2 원본3575bytes는 `implementation/history/v2/`에 보존했다.
그 SHA는 `bbfb0c668adb13493a05236f272e1e2cf96c010a62a9960a0fffd7e222755110`이다.

Revision3은 다음 공급 계약을 확인한다.

- 모든 source epoch는 finite/nonnegative이고 동일하다.
- channel threshold는 HI13.6,HeI24.59,HeII54.42eV와 일치한다.
- photon support는 각 channel의 [threshold,50000eV]와 정확히 일치한다.
- 다른 finite provider는 새로운 supplier contract로 연결한다.
- 기존의 explicit five-label inventory와 isotope mapping OPEN을 유지한다.

변경된 primary_source_assembly.py는4540bytes,
SHA256 `674ab7e51e6bdb3c5c4043a7024f708abdfb5d34d1867b1abcea3c4078106ec9`다.
기존 population/energy 계산식은 변경하지 않았다.

## 변경 범위만 검증한 새 실행

`c23b_primary_guard_revision3_20261023_v1`은 coordinator CPU2가 실제
관측 구간에서100%busy여서 resource admission에서 중단됐다.
worker 및 lease가 생성되지 않았고 원 receipt를 보존했다.

새 resource observation 후 create-only ID
`c23b_primary_guard_revision3_20261023_v2`로 진행했다.
새 invalid input17개를 모두 거절했고, 유효한 changed path1개는 기존
saved assembly의 모든 기존 필드를 그대로 재현했다. 추가 출력은
revision/supplier identity뿐이다. 전체6assembly나 source quadrature를
다시 실행하지 않았다.

실제 worker CPU4/native1, coordinator CPU2,
worker wall0.006205301s, outer wall0.245201237s,
peak RSS11264KiB, exit0, 해당 lease RELEASED다.
COMPLETE SHA256는
`ef6e9be73a5be20fd688e220bb68a59cdab574c0330ab6f21b7564913d5907c1`이다.

원 v2 campaign 결과는 원 source identity로 유지한다. revision3의
허용 조건은 저장된9개 원 source case에 모두 성립하며, 변경된 guard
경로의 실제 검사와 수치식의 불변성을 근거로 기존 수치 결과를 재사용한다.
원 campaign이 새 revision3 전체 코드를 실행했다고 기록하지 않는다.

| 축 | 상태 |
|---|---|
| EXECUTION | 저장 v2 provenance/ledger 검토 + 새 revision3 targeted 검사 COMPLETE_SCOPED |
| PUBLICATION | parent 통합 commit 대기 |
| BACKUP | parent 통합 release 대기 |
| DAG | finite source 공급 -> per-target/stoichiometric assembly -> source API guard 완료; actual isotope/thermal/transport closure 후속 |

`global_error_bound=null`, 전체 목표 completion percent=null을 유지한다.
