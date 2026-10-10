# CR-PHYS02B 구현 반환

현재 상태: 아래 최초 donor-cell 실패 서술을 보존하며, 문서 끝에 추가한
characteristic repair는 수치 `PASS_SCOPED`다. 독립 검토도 이 제한된 범위를
`PASS_SCOPED`로 승인했다.

절대 proper time을 유지하는 고정 gas 전자 cascade sidecar를 구현했다. 공급받은
DarkHistory commit `b556d0f0418a0665719fd6da26dcc303466b9659`의 source 6개와 동일
commit의 MIT LICENSE를 보존했다. 원시 nσv와 Coulomb 에너지 손실식에 현재 gas의
nH, Y, xHII/H 및 xHeII/He를 명시적으로 넣는다. 상류의 기본 cosmology와 Y=0.245는
사용하지 않는다.

이온화는 두 전자를 생성하고 E1+E2=E−I를 보존한다. 10 eV 이하 전자는 수와
실제 잔여 운동에너지를 미해결 reservoir에 저장하며 열로 전환하지 않는다.
결합·여기·Coulomb 열·active·cutoff 에너지를 분리했다. 실제 시간 evolution은
차원이 있는 generator의 지수 작용으로 실행했다.

8개 focused test는 PASS다. 실제 bounded validation에서 시간법 SSPRK2의 관측
차수는 2.018/2.009, finest energy-fraction 오차는 9.24e-7이었다. sparse/dense
지수 비교는 1.93e-15, daughter quadrature 차이는 1.70e-10, number/energy ledger
최대 오차는 2.8e-14 미만이었다. 양성, t=0의 침적 부재, OFF 항등도 통과했다.

그러나 공간 격자 판정은 FAIL이다. 128→256 차이 0.0240124보다 256→512 차이
0.0274871이 커졌고, 계약 상한 0.02를 넘었다. 20 eV impulse의 t=1e11 s에서
active/cutoff 에너지 분할이 실패를 지배한다. 원 결과와 모든 45개 저장 history를
`evidence/VALIDATION.json`에 보존했다. tolerance를 변경하거나 sweep을 늘리지
않았으며, 수치 격자 수렴 미확정 HOLD로 반환한다.

최소 다음 작업은 같은 원시 물리를 유지하며 이 transient cutoff case의 donor-cell
수치 오차를 조사하는 한 번의 제한된 repair다. 그 후에만 reviewer가 scoped
수치 사용을 판단할 수 있다. 전체 CR 지연 kernel은 source convolution과 실제
secondary 지원 범위 확장, 추가 손실 계약 등이 아직 필요하다. Production 변경,
CR/IGM history 및 global physical admission은 이 결과에 포함되지 않는다.

측정된 validation CPU는 1.5543 s, process wall은 1.5574 s다. 기타 overhead는
UNKNOWN_NOT_ZERO이며 테스트 CPU는 측정하지 않았다. 독립 review는 구현 worker가
실시하지 않았고 parent의 분리 review로 인계한다. Commit/push도 실시하지 않았다.

## 추가 기록 — 한 번의 characteristic repair

원시 cross section, gas, cutoff, impulse 20/100/1000 eV, epoch
0/1e10/1e11/1e12/1e13 s, 격자 128/256/512 및 모든 허용오차를 유지했다.
Coulomb drag만 tau(E)=integral(dE/b)에 따른 characteristic으로 교체했다.
각 노드의 실제 감소 에너지는 heat에 기록하고, 10 eV에 도착한 노드는 수와
운동에너지를 inert cutoff에 남긴다. 충돌은 해당 midpoint 에너지/상태를 함께
소비하며 원래 paired-daughter projection을 사용한다.

최초 repair focused run의 두 실패(작은 시간차의 root cancellation,
exact-inert 상태의 exponential roundoff)는 원 로그에 남겼다. 해당 두 구현
결함을 국소 수리한 뒤 9개 test가 통과했다. 이후 단 한 번의 전체 repair
validation이 exit 0, `PASS_SCOPED`로 종료했다.

- 격자 최대 energy-fraction 차이: 0.00358890880 → 0.000995304556.
- 시간 차이: 2.77542e-5 → 1.52128e-7 → 8.37377e-9.
- sparse/dense 같은 stage 차이: 3.12639e-15.
- daughter quadrature 8/12 차이: 1.68672e-10.
- energy/number ledger 최대 오차: 4.9960e-15 / 4.2633e-14; 최솟값 0.
- 20 eV continuum arrival oracle 9.456523330348772e10 s와 적분값의 상대차
  4.25660e-13. 저장된 도달 후 9개 case의 active energy는 모두 정확히 0.

시간의 관측 비율은 threshold 위치와 유한 reference를 포함한 진단값이며,
7.51/4.18이라는 값에서 일반적인 고차 convergence theorem을 주장하지 않는다.
새 receipt의 CPU 383.423912465 s, process wall 383.655116494 s이고,
그 외 overhead와 회수하지 못한 최초 test process 비용은 UNKNOWN_NOT_ZERO다.

실행된 source SHA는 새 `evidence/REPAIR_VALIDATION.json`에 있다. 원 FAIL JSON의
SHA는 여전히 `487bb2efa40ef642731bc8c2edc4018bceb37a18caffd81acb8980cc83f2810c`다.
코드는 실행 후 변경하지 않았다. 독립 reviewer는 원 FAIL JSON·동결 contract/source
manifest를 확인하고, 20 eV 도달 시간을 독립 적분으로
`9.456523330348772e10 s` (적분 오차 추정 `0.001049885 s`)로 재확인했다.

중요하게, receipt의 `8.37377e-9`는 1284-step SSPRK2 비교값이지 기본 저장
history의 시간 오차가 아니다. reviewer가 기본 128-grid 저장 history와 같은
`1e11 s`의 2568-step reference를 직접 비교한 최대 channel 차이/초기 에너지는
20/100/1000 eV에 각각 `1.1889741524804265e-4`, `9.149982341227769e-7`,
`6.45614898076019e-8`로, 동결 기준 `2e-4` 이내였다. 이 독립 진단은 exit 0,
CPU `124.625298052 s`, wall `124.674442718 s`였다.

승인되더라도 범위는 고정 gas의 10–1000 eV impulse로 제한되며, 실제 CR source
convolution, 10–8700 eV 지원, full history 및 global admission은 계속 HOLD다.
