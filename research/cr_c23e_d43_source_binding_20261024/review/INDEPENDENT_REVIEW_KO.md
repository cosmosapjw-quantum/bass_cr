# C23E D43K source binding 독립 검토

## 현재 판정

**PASS_SCOPED / NUMERICALLY_CHECKED_SCOPED**. 아래 조건부 과학 범위의 식·원전 재사용·저장 수치 결과를 승인한다. 유일한 실행 전달 결함 R1은 root 승인 아래 lower-tier coder가 한 번 수정했고, 동일 검토자가 변경 diff·경량 검산 결과·실제 bytes를 확인하여 CLOSED로 판정했다. 원 과학 suite 재실행이나 새 reviewer 없이 검토를 종료한다.

- 대상: `C23E_D43_PHOTO_RR_SOURCE_BINDING`, frozen V2.
- 검토자: native fresh-context `/root/c23e_independent_review`; requested tier/model은 Astra/gpt-6-astra. 실제 runtime model identity는 독립 확인되지 않았다.
- 독립성: 계약/구현 작성 및 primary 실행에 참여하지 않은 새 agent의 정적 수학·코드 검토와 보존 raw evidence 확인이다. 별도 수치 solver 재실행이나 독립 실험은 아니다.
- 읽은 정책: `intake/rei_AGENTS.md`, `intake/bass_AGENTS.md`, `intake/policy/PHYSMATH_MAIN.md`, `THEORY_LOOP.md`, `CODING_LOOP.md`. 적용 범위는 R6/C9이다.
- 검토 중 과학 실행 0, 기존 H 재적분 0, CX ODE 0, 원 suite replay 0, 코드 수정 0. 파일 읽기·hash·JSON/CSV 집계만 수행했다.

## 단일 material finding과 한 번의 repair

**R1 / MEDIUM / 재현 가능한 실행 전달물 / CLOSED**

`implementation/validate_d_binding.py`의 입력 준비가 `inputs/C23B_CASES_EXACT.json`을 `xb`로 다시 쓴다. 이 파일은 primary 실행 후 이미 존재하므로 전달된 상태에서 명령은 FileExistsError로 종료한다. saved atom 경로도 이전 scratch 복원 트리의 절대 경로여서 독립 복사본에 입력이 결속되지 않는다. 또한 `implementation/dispatch_d_binding.py`의 module-level 본문은 import만으로 output 생성·lease·과학 worker 실행을 수행하며 frozen 계약의 import-time science/write 금지와 맞지 않는다.

수치 모형이나 원 primary 결과의 오류는 아니다. runnable command, 상대 입력 경로 및 import 동작에 한정된 전달 결함이다.

최소 repair는 원 실행된 세 script와 manifest/raw 결과를 보존하고, exact atom bytes를 `inputs/`에 포함하며, exact CASES와 atoms를 ROOT-relative 경로에서 읽고 digest를 확인하고, dispatcher 본문을 `main`/`__name__` guard로 감싸는 것이다. create-only output 생성은 유지한다. 검산은 입력 읽기/identity, import 무쓰기·무실행, output collision 거부에 한정한다. 모멘트·반응식·허용오차·수치 suite는 바꾸거나 재실행하지 않는다. 이 한 repair의 diff/결과로 최종 결정을 내린다.

## 수학·단위·물리 범위

`q(E)=S(E) sigma_H(E)/(EV_ERG E^2)`는 S가 `4*pi*nu*J_nu`일 때 사건률 밀도 `s^-1 eV^-1`이다. 새 D는 동일 H 단면적을 `chi_D=13.6+43 kB` 이상에서만 사용하는 조건부 모형이다. 새로운 실험 D 단면적, finite-mass kinetics 또는 Milne pair를 제공하지 않는다.

정적 전개로 `Gamma_D=Gamma_H-Glo`, `K_D=K_H-delta Gamma_H+B`, `A_D=A_H-Alo`를 확인했다. `B=integral(chi_D-E)q dE`를 직접 양의 integrand로 적분하므로 작은 양을 큰 수의 차로 만드는 추가 cancellation을 피한다. 같은 band를 쓸 때 `chi_D Gamma_D+K_D-A_D`는 원 H 잔차를 상속한다. delta=0 한계는 H이고, raw 결과의 양수성과 단위가 맞는다. 이 대수적 변환을 측정 speedup으로 해석하지 않는다.

`band()`는 native source knots로 나눈 direct-E GL8/16/32를 쓴다. 검증의 새 D 적분은 log-E 변수에서 Jacobian E를 곱하고 같은 native interval을 scipy.quad로 적분한다. H 전체를 재적분하는 경로는 호출되지 않는다. 수치 방법과 적분 구간은 독립이나 spectrum/cross-section primitive는 공유하므로 검산은 구현/적분 일치의 근거이며 empirical source model의 독립 검증은 아니다.

RR의 `3/2+d ln(alpha)/d ln(T)`를 VF 식에 적용하면 구현의 두 양의 항이 나온다. `Kcap=kB T*rr_energy_factor`의 eV 단위가 일치한다. alpha_D=alpha_H 및 capture_D=capture_H는 명시된 조건부 근사다. 원 fit의 rate 정확도가 그 온도 미분이나 isotope correction을 인증하지 않는다.

CX 추출식은 실제 WU79 `d_cx_rates(..., detailed_balance)`와 동일하다. 순방향 `D0+H+ -> D++H0`에서 결합에너지는 `+delta J`, 열에너지는 `-delta J`이고, 역반응 J<0에서도 부호가 맞는다. 독립 Savin forward fit을 보존했다는 주장은 없다. 공동 T domain `[3,200000] K`가 코드에서 거부/허용된다.

## 21 population과 두 전자 pool

모든 named21 입력을 요구하고 ionic charge는 spectators까지 포함한다. 원자 spectator의 dn=0은 이 선택 사건 집합의 incidence이며 실제 반응률 0 선언이 아니다. 전하합과 thermal+fast 입력합이 별도로 검사된다.

PI는 fast 전자만 증가시키고 primary kinetic energy를 fast ledger에 넣는다. RR은 thermal 전자만 소비하며 rate가 n_e,thermal에 비례한다. 실제 첫 fast-fraction pair의 PI/CX 값은 같고 RR만 0.9배가 되어 두 pool 분리의 의도와 맞는다. CX는 두 전자 pool을 바꾸지 않는다. 열화/stopping은 계산하지 않는다.

PI/RR/CX별 결합·열·fast·escaped·absorbed energy 부호를 직접 확인했다. 하나의 potential descriptor를 요구하고 equal-H/D threshold와 D43K CX를 혼합하면 거부한다. 동일 potential cycle은 정확 대수상 0이며 raw Fraction 검사도 0이다. 상태 potential contraction은 작은 순잔차가 아니라 구성 에너지 크기로 정규화한다. 핵종/전하 정수 incidence는 eight nuclei와 전하를 보존한다.

## 실제 source identity와 보존된 결과

검토자가 실제 bytes를 읽어 `implementation/reuse/INTAKE_MANIFEST.json`의 9개 항목 각각에 대해 길이와 SHA256 일치를 확인했다. C23B provider/CONTRACT/3개 PW19 spectrum/Verner table, C23C inventory, C22A RR, C21O RR table이 모두 일치한다. run의 `EXECUTED_SOURCE_MANIFEST.json` 3개 구현 파일과 frozen contract도 원 실행 hash와 일치했다. parent CASES의 transport newline 정규화 후 원 Git blob 일치와 saved atoms identity는 실제 검증 코드 및 보존 check로 확인했다. snapshot/transport normalization은 원 immutable source를 몰래 바꾼 것으로 취급하지 않는다.

근거 run: `runs/C23E_D43_SOURCE_BINDING_20261024T021612Z_v1/`.

| 검사 | 실제 최대값/결과 | frozen 허용값 |
|---|---:|---:|
| GL8/16/32 band 상대차 | 5.626252649309911e-16 | 2e-10 |
| 새 D quad와 boundary 상대차 | 1.7485509595587793e-15 | 2e-11 |
| PI 에너지 상대잔차 | 8.07907976464989e-17 | 5e-14 |
| floating 핵종 잔차 | 0 | 2e-13 |
| pool 정규잔차 | 1.1401679038436815e-16 | 2e-13 |
| 전체 에너지 정규잔차 | 6.824722606685112e-17 | 2e-13 |
| 상태 potential 정규잔차 | 1.25791865881435e-16 | 2e-13 |

`RESULT.json`의 104 checks가 실제 모두 True이고 `POINT_SOURCES.json`에는 정확히 18개 상태가 있다. 신규 D integration 3개, band order evaluations 9개, ODE/parent rerun/benchmark는 0이다. 결과 파일과 읽은 실행 경로가 이 count를 뒷받침한다. 실패경로는 T 하단/상단/NaN, 누락 population, 잘못된 pool 합, 혼합 potential을 명시 거부한다. domain endpoint 3/200000 K도 허용된다.

단순 saved atom filter의 count 오차는 세 z에서 약 -0.00144346, -0.00145010, -0.00145810이고 kinetic 오차는 약 -2.01e-7..-2.06e-7이다. 이는 새 D 문턱에서 원 finite atom measure를 필터한 값과 continuous integral이 다른 진단이며 원 H 측도의 실패가 아니다. 실제 D/H 사건률 이동은 약 -0.00123906..-0.00125168이다.

실행 receipt는 exit0, child CPU 2.161932 s, wall 2.1714153429929866 s, maxRSS 122500 KiB이다. 내부 RESULT CPU는 import 제외 구간이므로 이와 구별한다. 실제 affinity 0..8에서 worker8/coordinator0, thread1, CPU60 s/wall180 s/address-space1GiB 제한과 local lease가 확인된다. preflight가 보존되었고 CPU55는 이 host affinity에 없었다. inherited 13.331329114 s와 합친 15.493261114 s는 알려진 lineage 하한이며 전체 project 지출이 아니다. matplotlib cache 경고는 /tmp fallback 후 정상 종료하여 과학 결과 결함이 아니다.

## 최종 admission 범위

R1 해소 후 최종 판정은 **PASS_SCOPED / NUMERICALLY_CHECKED_SCOPED**: 고정된 세 PW19 source node, threshold-gated H-equality D43K PI, 같은 VF-fit RR/capture 근사, D43K CX 및 명시한 18개 순간 제조상태에서의 source/energy/pool 일치이다.

empirical isotope-resolved D/Milne, full21 rate coverage, cosmological integration, stopping은 OPEN이며 full nuclear/general Bianchi는 HOLD이다. `global_error_bound=null`, `global_completion_fraction=null`을 유지한다. publication/backup/DAG는 과학 검토와 별도 상태다. 새로운 과학 blocker나 후속 suite를 추가하지 않는다.

## 단일 repair 종료 확인

`runs/C23E_D43_SOURCE_BINDING_20261024T021612Z_v1/delivery_repair/`의 실제 세 diff, `TARGETED_REPAIR_RECEIPT.json`, `DELIVERED_SOURCE_MANIFEST.json`과 `implementation/verify_delivery_repair.py`를 읽었다. root가 승인한 입력 경로/기존 파일 읽기/main guard만 바뀌었고 `d_binding.py.diff`는 비어 있다. 수치식, quadrature, 입력값, tolerances, 104-check primary는 바뀌지 않았다.

실제 bytes를 재확인하여 원 세 script snapshot은 원 실행 manifest와 같고, frozen contract도 원 hash와 같으며, 전달 세 script는 delivery manifest와 같음을 확인했다. bundled atoms는 1681578 bytes/SHA256 `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`, exact CASES는 25699 bytes/Git blob `61bcbc0b44206f496534da6bdffcdfe1731ad063`로 일치한다.

29개 targeted checks가 모두 통과한다. import의 쓰기·process spawn을 mock으로 차단한 상태에서 세 module import가 성공했고, 상대 경로 exact input identity 및 create-only collision에서 preflight/worker 이전 거부가 확인되었다. 나머지는 원 raw/snapshot/contract의 보존 확인이다. numerical main, source quad, point source의 새 호출은 각각 0이며 primary replay는 false다. 이는 delivered 코드로 전체 과학 suite를 다시 실행했다는 주장이 아니라, unchanged physics 증거와 delivery-only diff의 결합에 의한 최종 admission이다.

R1은 해소되었다. 남은 material finding은 0이고 추가 repair 또는 suite 요구는 없다. 다음 행동은 root의 이미 승인된 scoped 결과 게시·보존·DAG 갱신이다.
