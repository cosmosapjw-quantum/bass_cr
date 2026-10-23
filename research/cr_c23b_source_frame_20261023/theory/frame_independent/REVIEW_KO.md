# C23B 독립 검토: source frame 및 수명 정규화

## 판정

명시한 등방 parent-rest 전자 방출 measure의 gas-frame 변환과 decay-clock
구현은 **PASS_SCOPED**다. 완료된 C23A 계산은 재실행하지 않았다.
새로운 실행 `c23b_frame_independent_20261023_v1`은 아래 source snapshot을
검토했다.

| 파일 | bytes | SHA256 |
|---|---:|---|
| boost_kernel.py | 9232 | ac2ba5f6b180b14cc52db962643c164391dcd6028e415ef5bca73aee8628a682 |
| source_ledger.py | 4222 | 308795cf729013faa84f991486fd6095b7d649a0a51ef2f4a339af9ab7aaf32b |

검토는 producer의 출력만 읽은 것이 아니라 원식에서 rest-frame cosine의
구간을 80자리 정밀도로 독립 계산했다. 각 구간의 두 Gauss 점에서4개
moment를 적분했다. 해당 integrand는 cosine의 차수1 이하이므로 이
구간 적분에는 Gauss 절단오차가 없다. producer의 FP64 endpoint 및
보상합 표현을 reference에 복사하지 않았다.

## 실제 검증 결과

| 항목 | 결과 |
|---|---:|
| K,u 사례 | 106 |
| 에너지 bin 비교 | 832 |
| 실패한 bin | 0 |
| 최대 particle-number 절대오차 | 2.220446049250313e-16 |
| 최대 kinetic moment 정규화오차 | 2.048218445785895e-16 |
| 최대 total-energy moment 정규화오차 | 1.706686308295437e-16 |
| 최대 signed parallel-pc moment 정규화오차 | 1.9909183443876822e-16 |
| endpoint 오차 / max(1eV, total energy) | 3.2186250423474523e-16 |
| decay-clock 및 방향 평균 사례 | 15 |
| source tuple과 net flux의 불일치 | 0 |

검사 허용치는2e-12다. kinetic moment의 분모는 max(1eV, 완전 구간의
kinetic moment), total 및 pc의 분모는 max(1eV, 완전 구간의 total-energy
moment)다. 아주 작은 bin moment를 분모로 한 상대오차나 전 구간의
해석적 수치오차 상한으로 이 값을 표현하지 않는다. global_error_bound=null.

K 범위는0,1e-15,1e-6,1,10,5690,9937.21,18590,301370,782347,1e9 eV,
u 범위는0,1e-12,1e-8,1e-4,0.1,1,10,1000이다. 추가로
K=(gamma-1)M의 양옆 nextafter를 검사했다. 고정 transport 경계10,
100,9937.21,1e6 eV와 [0,infinity), 그리고 K 자체에서 나눈 좁은 구간을
포함한다. gamma=1/K=0 Dirac, tiny-u, matched-speed cancellation을
구분해 다뤘다. 이는 수학적 kernel 검사 범위이며 해당 고에너지에서
원자율/수송 모델의 물리적 채택을 뜻하지 않는다.

새 실행은 실제 cgroup/affinity/메모리 headroom와 다른 owner lease를
확인한 뒤 coordinator CPU2, worker CPU4, native1thread로 진행했다.
worker wall0.352789692s, coordinator 포함0.734326424s,
peak RSS17736KiB, exit0. CPU55는 보호 집합에 포함했고 이 sandbox의
가용 affinity0..8 안에서 실행했다. 해당 lease만 해제했다.

## 발견과 교정

1. 최초 읽은 producer는 electron rest-energy를510998.95eV로 두고
   C23A와 같은 상수라고 썼다. C23A의510998.95069eV와 일치시키도록
   전달했고, 검증 snapshot에는 교정이 반영됐다.
2. 최초 source API는 isotropic/equal-opposite ensemble에서도 tuple에
   양의 단일-parent parallel-pc를 반환하면서 별도 net field는0으로
   표기했다. 검증 snapshot은 단일-parent 진단을 별도 필드에 보존하고
   실제 ensemble tuple에는0을 반환한다.
3. tiny-u에서 절대 에너지 endpoint 두 개를 빼 bin 수를 계산하면
   O(ulp(K)/B) 조건수가 생긴다. producer는 center를 K와 작은 shift로
   나누어 보상합한 cosine 경계를 사용한다. independent reference의
   tiny-u/K-split 사례가 위 허용치로 통과했다.

이3건은 최초 읽기에서 발견하고 검사 전에 교정됐다. 존재하지 않는
수치 실패 실행을 만들지 않는다. 별도의 Wolfram 시도에는 syntax
실패1건과 잘못 옮긴 denominator 식1건이 있었으며 원 응답과 최종
0차이를 SYMBOLIC_CHECKS.json에 보존했다.

## 물리적 귀결과 남은 계약

등방 rest 전자 에너지K는 [A-B,A+B] 균등분포로 옮겨진다. u 입력과
(A-B)(A+B)=[K-(gamma-1)M]^2 항등식은 tiny boost 및 낮은 endpoint를
안정적으로 계산한다. 모든 moment에 같은 event 수를 곱하고,
gas-frame parent density를 쓰면 event rate=lambda*n/gamma다.
per-decay boost와 per-time 수명지연을 함께 적용해야 한다.

등방 parent 방향 평균은 scalar source를 허용한다. 반대방향 beam 쌍은
flux를 상쇄하지만 even stress anisotropy를 남길 수 있으므로 이를
등방 atomic-gas stress로 대체하지 않는다. 아직 필요한 것은 실제
evaluated spectrum, initial/final atomic 상태, source density/lifetime
입력, neutrino/recoil/rest-mass energy owner, stopping과 transport다.
원자의 등방 stress closure와 nonbaryonic Vlasov stress 소유권은 유지한다.

| 축 | 현재 상태 |
|---|---|
| EXECUTION | 독립 유도/Wolfram/새832bin+15clock 검사 COMPLETE_SCOPED |
| PUBLICATION | parent가 최종 통합 commit에 포함할 예정 |
| BACKUP | parent가 통합 release에 포함할 예정 |
| DAG | C23A source-frame 의무 -> 변환·clock 구현·독립 검토 완료; 실제 spectrum/state/stopping 채택 후속 |

원전은 PRIMARY_SOURCES.json, 유도는 FRAME_DERIVATION.md 및
PARAMETERIZATION_UPDATE.md, 원 출력은 실행 디렉터리의
ANGULAR_REFERENCE_CHECKS.json 및 DECAY_CLOCK_CHECKS.json에 연결한다.
Lorentz 이론의 신규성이나 full nuclear network 완료를 주장하지 않는다.
