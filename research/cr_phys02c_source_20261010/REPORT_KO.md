# CR-PHYS02C-SOURCE01 — 1 keV 초과 direct-born source

결과는 `PASS_SCOPED`다. 고정된 PR24 양성자 주입·중성 H/He SDCS에서 1 keV 초과 전자의 실제 source를 운동학적 끝점까지 계산한다. 독립 검토도 같은 source-only 범위를 승인했고, 게시·백업은 부모 에이전트의 다음 작업이다. 전체 CR 침적·IGM history는 `HOLD`다.

## 구현과 물리 범위

기준 commit은 `b65d51abebe5bd307b3e434632d2cfb8c05ee270`, tree는 `66619cc048429052572e6fe0eaa15deb3f995705`다. `injection.py`, `rudd.py`의 원 bytes는 `SOURCE_MANIFEST.json` 두 SHA256에 고정하고 import 전에 확인한다. 이번 변경은 이 폴더에만 추가했다. 생산 provider, P02B, P05는 바꾸지 않았다.

100 K, `nH=140 m^-3`, `Y=0.248`, `xHII=xHeII=0.01`, `xHeIII=0`인 bath에서 `Q_s(W,t)=t A_s(W)`를 계산한다. proton `q_p(K)`는 기존 z=8 주입과 10 keV–1 PeV 전체 에너지 정규화를 유지한다. 이 source가 소비하는 충돌 구간은 1–4 MeV다. `A_s` 단위는 proper `m^-3 s^-2 eV^-1`, Q의 시계는 local proper second다. 이것은 고정 bath의 국소 ramp이며 새 cosmological propagation 계산이 아니다.

`A_s(W)=n_s ∫ q_p(K) v_p(K) [dσ_s/dW] dK`, 적분 하한은 `max(1 MeV,(W+I_s)/(4 me/mp))`, 상한은 4 MeV다. 하한이 상한 이상이면 정확히 0이다. 방향 적분은 주입과 SDCS에 이미 들어 있으므로 추가 4π 인자를 쓰지 않는다. 기존 Rudd adapter의 비상대론적 끝점을 그대로 사용한다.

| target | Wmax(1 MeV), eV | Wmax(4 MeV), eV |
| --- | ---: | ---: |
| H | 2164.862392825006 | 8700.266650669006 |
| He | 2153.878085948 | 8689.282343792 |

W 적분은 두 target의 네 끝점과 10/1000 eV에서 분할한다. 신규 source quadrature의 최대 GL order는 96이며, 동결된 full-spectrum normalization은 기존 128을 유지한다. kinetic energy와 primary binding cost를 따로 적산한다. 방출 전자 kinetic energy를 heat 또는 침적으로 재분류하지 않는다.

## 실행 결과

최초 한 campaign의 focused tests 8개는 통과했다. 최초 raw-SDCS parity는 H의 상한보다 1 ppm 낮은 에너지에서 `8.099279321817133e-10 > 2e-10`로 FAIL이다. 실패 파일과 당시 validator는 그대로 남겼다. 비교기의 두 `log(K)` 경계값을 뺄 때 발생한 3.99 eV 구간 폭 손실이 원인이었다. 상수 integrand oracle에서도 같은 상대 폭 오차 `8.099272991895129e-10`가 확인됐다.

허용된 단일 수리는 raw-SDCS 비교기의 적분좌표만 `K=Kmin+(Kmax-Kmin)u`, `u∈[0,1]`로 바꿨다. source·에너지 표본·tolerance는 그대로다. 수리 campaign은 exit 0, targeted regression 1개 PASS다.

| 검사 | 관측 오차 | 기준 |
| --- | ---: | ---: |
| raw SDCS 독립 adaptive 비교, 수리 후 | 2.158157438983604e-15 | 2e-10 |
| spectrum GL64→96 | 9.642558385984125e-16 | 2e-7 |
| W spectrum 적분 ↔ 해석적 SDCS 모멘트의 K 적분 | 6.057715208142252e-15 | 2e-7 |
| integrated moments GL64→96 | 3.975375605343361e-15 | 2e-7 |
| <10 / 10–1000 / >1000 eV 분할 합 | 2.067270483788961e-16 | 2e-12 |

끝점/그 이상/OFF/t=0은 정확히 0이며 검사한 source와 모멘트는 유한·비음수다. 기존 저에너지의 상수 coefficient를 3/5/8 keV로 잘못 외삽한 음성 대조는 각 target에서 38.4–97.6% 상대 차이를 보였다.

선택한 1–4 MeV proton window가 생성하는 전체 direct-born 전자 중 >1 keV 성분은 개수의 `0.005941785799259185`, kinetic energy의 `0.24461890323948224`다. 후자는 약 24.46%의 **생성 에너지 비중**이다. 그것이 언제 어디에 침적되는지는 아직 계산하지 않았다.

1 keV 초과 source 계수는 number `2.040876437855455e-37 m^-3 s^-2`, kinetic `3.7390103515915883e-34 eV m^-3 s^-2`, 별도 primary binding `3.0946271963620816e-36 eV m^-3 s^-2`다. ramp의 10^10 s 누적량은 각각 `1.0204382189277274e-17 m^-3`, `1.8695051757957942e-14 eV m^-3`, `1.5473135981810409e-16 eV m^-3`다.

## 재현과 한계

실행 환경은 Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0이다. 최초·수리 명령은 evidence의 `execution.command`에 있고 각각 exit 1/0이다. 두 검증 script는 기존 evidence 덮어쓰기를 거부한다. 새 결과가 필요한 경우 새 출력 복사본에서만 실행한다. 최초 process 내부 wall 0.25193 s, 수리 0.47922 s다. Python process CPU는 각각 0.11898 s, 0.14658 s이며 child-test CPU와 나머지 overhead는 미측정이다. solver interval 실행은 0이다.

PHYS–MATH v4.0.0 지침에 따라 입력/기준을 실행 전에 고정했고 최초 실패를 보존한 뒤 한 번의 좁은 수리를 적용했다. 패키지 이름으로 runtime 모델 변경을 주장하지 않는다. `~/.codex/bounded-work-harness/RULES.md`는 없어서 `HARNESS_RULES_UNAVAILABLE`로 기록했다.

독립 검토는 PASS_SCOPED로 종료했다. 다음은 recovery package와 scoped publication이다. 이후 >1 keV electron response 계약과 source-backed degradation, 저에너지 접합을 해결해야 한다. 이 결과는 고에너지 cascade, P05 full source convolution, cutoff response, gas feedback 또는 global scientific admission을 닫지 않는다.
