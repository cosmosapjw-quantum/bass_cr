# 조건부 첫 crossing 잔여 전자 응답

CR-PHYS02C-CONDITIONAL-CROSSING-RESPONSE01의 첫 실행은 `PASS_SCOPED`이다.
상위 Astra가 고정한 계약을 하위 tier가 구현했고 독립 Astra 검토도
`PASS_SCOPED`였다. 검토자는 저장된 ledger/refinement 지표를 재계산하고
경계 전용 검사 두 개만 재실행했다. 추가 비영시간 물리 진화는 없었다.
기존 P02B 코드는 SHA `ea72b12d07bc500cb7c917c5e500325c6864da77cdd90637ddceab7aeddfa0da` 그대로 사용했다.

1000.001 eV 전자가 upstream에서 HI NIST 2p 사건 한 번을 겪은 잔여
989.797 eV, 또는 HeI NIST singlet 사건 한 번을 겪은 잔여 978.783 eV를
각각 crossing 전자 한 개로 정규화했다. 고정 100 K bath에서 proper age
0..1e11 s를 계산했다. 128/256/512 grid 각각에 정확한 잔여 에너지를 새로
투영했으며 downstream 사건 계수는 출생시 모두 0이었다.

upstream HI 10.204 eV 및 HeI singlet 21.218 eV는 별도 변경 없는 ledger다.
downstream old HI/HeI 23s/HeII excitation은 종별로 별도 반환한다. 10 eV
cutoff의 수와 에너지는 미배분 reservoir로 남는다. upstream와 downstream의
HeI excitation을 동일 물리 채널로 합치지 않았다.

검증 기준은 첫 실행에서 모두 통과했다. number ledger 최대 오차
5.3291e-15, upstream 포함 energy ledger 상대 오차 4.5519e-15이다.
grid channel 차이/E0는 1.3780e-5에서 7.5485e-6으로 감소했다.
64/128/256 sparse stage를 642-stage SSPRK2와 비교한 차이/E0는
9.1775e-9, 8.1203e-9, 6.9771e-9로 감소했다. daughter quadrature 8/12
차이/E0는 1.6992e-10이다. finite/nonnegative와 t0/OFF identity도 통과했다.

실제 nonzero evolve 호출은 두 열을 묶어 7회이며 process CPU 93.3908 s,
wall 93.5274 s를 측정했다. 미측정 overhead는 UNKNOWN_NOT_ZERO다.
경계 전용 검사 2개도 통과했고 추가 물리 evolve 호출은 없다. 첫 실패와
수정은 없으며 campaign 재실행도 없다. 원 실행 결과는
`evidence/VALIDATION.json`에 보존했다.

이 결과는 두 지정된 crossing 사건의 조건부 잔여 전자 응답이다.
continuous source convolution, volumetric injection, gas feedback 및 전체
CR/IGM history는 실행하지 않았으며 global scientific admission은 HOLD다.
active bounded harness 파일 부재는 HARNESS_UNAVAILABLE로 기록했고 과거
기억으로 복원하지 않았다. 다음 단계는 이 sidecar의 scoped backup/publication이며,
연속 source-evolution은 새 Astra 계약 없이는 시작하지 않는다.
