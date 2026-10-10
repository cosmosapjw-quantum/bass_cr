# CR-PHYS04b — 고정 CR population의 Coulomb 에너지 전달 진단

100 K, `nH=140 m^-3`, `Y=.248`, `xHII=xHeII=.01`, `xHeIII=0` 조건에서
기존 PHYS01 충돌 없는 양성자 population의 순간 Coulomb loss를 계산했다.
`1..10 MeV` 결과는 `4.195312575917908e-43 J m^-3 s^-1`이다.
이 값의 출력 이름은 `plasma_transferred_energy_j_m3_s`다. Plasma 전자의
후속 에너지 분배가 없으므로 열, ionization/deposition rate 또는 history로
채택하지 않는다. `solver_intervals=0`, `collision_feedback=NOT_APPLIED`다.

## 채택한 식과 단위

세 원문 header는 [source manifest](evidence/SOURCE_MANIFEST.json)에 고정했다.
원 코드의 proton 식은

`omega_p = e_G sqrt(4 pi ne_CGS / me_CGS)`,

`B = ln(2 gamma me c^2 beta^2 / (hbar omega_p)) - beta^2/2 + 0.5 ln(1+(0.5615 beta/alpha)^2)`,

`loss_CGS = e_G^2 omega_p^2 B / v` (erg/s)이다.

Gaussian의 `e_G^2`는 SI에서 `e_SI^2/(4 pi eps0)`에 해당한다.
그러므로 SI prefactor는 `e_SI^2 omega_p^2/(4 pi eps0 v)`이며
`omega_p = e_SI sqrt(ne_SI/(me_SI eps0))`다. 원 코드의 MKS branch는
`4 pi eps0`를 곱한다. 원본 bytes 및 그 literal 연산을 negative control로
보존했다. 이 경우 올바른 값에 대한 비율은 `(4 pi eps0)^2 =
1.2379901458881492e-20`이며 단위 변환 검사에 실패한다. 이 correction은
source normalization의 재보정이나 물리 tolerance 변경이 아니다.

수치 상수는 port에 CODATA 2018 값으로 명시했다. 원 header가 참조하는
미확인 GSL build의 수치상수·binary를 재현했다고 주장하지 않는다.
CGS와 SI 경로는 별도 단위 연산으로 평가한다. CGS charge는 같은 물리 상수의
Gaussian 변환값 `4.8032047138777412e-10 sqrt(erg cm)`로 고정했다.
이 비교는 단위·구현 일관성 검사이며 독립 실험 정확도 검증은 아니다.

GasData의 `neFree=xe*nH`에서 `xe`는 H nucleus당 free electron 수다.
여기서는 PHYS01 per-He fraction을 명시적으로 변환하여
`ne = nH*xHII + nHe*(xHeII+2*xHeIII) = 1.5154255319148937 m^-3`를 사용한다.
He electron을 생략하는 회귀를 따로 검사했다. 양성자 속도는 가장 느린
1 MeV에서도 100 K electron thermal speed `sqrt(2 kB T / me)`의 약
251.20배다. 이 진단은 선택한 fast-projectile Coulomb 모델이며 plasma의
열적 반응·secondary spectrum 정확도까지 인증하지 않는다.

## population과 회계

PHYS01 `InjectionModel`의 전체 `10 keV..1 PeV` source normalization을
그대로 사용한다. `dt=1e10 s`, `H=3.3e-17 s^-1`, `s=3.3e-18 s^-1`의
정확한 collisionless Bianchi characteristics와 proper-volume birth measure를
재사용했다. 선택 proton band만 다시 normalize하지 않는다. 관측 시점의
population weight와 proton의 `J/s` loss를 곱한 합이 최종 `J m^-3 s^-1`다.
여기에 source age를 곱해 시간 적분 deposition이라고 부르지 않는다.
Positive projectile loss와 plasma-transferred energy는 같은 회계 항의
양쪽 의미다. 기존 neutral ionization loss와 중복되는 결합전자를 쓰지 않는다.

| proton band | plasma-transferred energy (`J m^-3 s^-1`) |
| --- | ---: |
| 1..4 MeV | 3.538932575353178e-43 |
| 4..10 MeV | 6.563800005647333e-44 |
| 1..10 MeV | 4.195312575917908e-43 |

출력의 sampled fractional loss×age 약 `1.99e-7`은 **최종 quadrature node의
최댓값×source age 진단**이다. 모든 trajectory의 상한, 시간 적분,
feedback 오차 인증 또는 Coulomb 무시 허가는 아니다.

## 검증과 최초 실패

[원 실행 기록](evidence/EXECUTION.json)에 명령·exit·최초 실패와 repair를 남겼다.
최초 focused test 7개 중 두 개가 실패했다: Gaussian charge의 끝자리 오기,
그리고 다른 연산 순서의 ne를 exact equality로 검사한 false FAIL이었다.
charge를 수정하고 ne assertion을 `3e-15` absolute 기준으로 바꾼 후 7개가
통과했다. 원 로그는 [TESTS_FIRST.log](evidence/TESTS_FIRST.log)에 보존했다.
물리 모델·refinement/CGS-SI/additivity 기준은 바꾸지 않았다.

[한 번의 bounded campaign](evidence/VALIDATION.json)의 결과:

- `(48,8,8) → (64,12,12)` energy/age/angle refinement: `2.89e-15 <= 2e-6`.
- `1..4 + 4..10`과 `1..10` 적분의 relative difference: `8.88e-16 <= 3e-13`.
- 17개 proton energy의 CGS/SI 최대 relative difference: `7.77e-16 <= 3e-14`.
- 양성·유한값, domain rejection, zero-ne, zero-age/OFF, He electron inclusion,
  upstream MKS negative control 검사 PASS.
- Python 3.12.3, NumPy 2.4.2, campaign CPU `0.178975534 s`,
  measured wall `0.17898328404407948 s`. 미측정 overhead는 UNKNOWN_NOT_ZERO.

이는 finite quadrature의 scoped 결과다. 오차가 작다는 이유로 Coulomb
모델 오차 또는 CR source의 불확실도를 0으로 두지 않는다.

```sh
OPENBLAS_NUM_THREADS=1 python3 -B -m unittest discover -s research/cr_phys04b_coulomb_20261010/tests -v
OPENBLAS_NUM_THREADS=1 python3 -B research/cr_phys04b_coulomb_20261010/coulomb_ledger.py --validation --output /tmp/cr-phys04b-new-validation.json
```

출력 경로가 이미 존재하면 실행을 거부한다. 현재 evidence를 덮어쓰지 않는다.
다음 실행은 독립 scoped review 후 승인된 branch에 게시하는 것이다.
CR-PHYS02 causal delay, 실제 gas thermal partition, proton stopping feedback,
미모델 loss channel과 전체 history는 여전히 HOLD다. Production provider와
REI receiver는 이 진단을 호출하지 않는다.
