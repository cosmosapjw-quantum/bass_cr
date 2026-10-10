# CR-PHYS05 직접 생성 전자 source convolution

구현과 한 번의 수리 후 수치 판정은 `PASS_SCOPED`이며, 독립 review도 같은
제한 범위를 승인했다. production 및 전체 CR/IGM history admission은 `HOLD`다.
결과는 고정된 100 K, nH=140 m^-3, Y=.248, xHII/H=xHeII/He=.01 bath에서
1–4 MeV 양성자가 직접 생성한 10–1000 eV 전자를 대상으로 한다.
PR24의 full-spectrum-normalized 주입을 유지한 `Qe(W,t)=t A(W)`를
proper interval 0..10^10 s에서 convolution했다.

`convolution.py`는 SHA가 고정된 injection/Rudd 및 P02B kernel을 불러온다.
각 birth cohort는 자기 나이와 characteristic energy grid에서 observable로
변환한 뒤 합산한다. 서로 다른 cohort의 상태 배열을 같은 energy grid로
취급하지 않는다. 새 production provider 변경은 없다.

계약 전개와 최초 실패

PR26은 birth time을 해석적으로 적분해 energy 적분으로 바꾸므로 새 cohort의
birth-time 격자가 없어 처음 intake는 `CONTRACT_INCOMPLETE`였다. Parent가
결과를 보기 전에 Gauss–Legendre birth order 8/16/32와 `16→32 ≤3e-6`를
명시했으며 `EXECUTION_CONTRACT.json`에 고정했다. 이전 `CONTRACT.json`은
그 최초 상태로 남아 있다.

최초 120-cohort 실행은 cutoff energy의 birth-time 차이
0.011067010826446212로 FAIL했다. Source·energy-grid·ledger 검사는 통과했다.
최초 `evidence/VALIDATION.json`의 SHA는
`700abc957650d92c9d1f2b178baccaffc33c160268b4a45b3a53ee928441484a`이며 그대로 보존한다.

한 번의 수리는 P02B의 기존 tau(E_node)에서 계산한 birth time
`T-tau(E_node)`만 적분 구간 경계로 사용한다. 128/256/512 격자의 panel 수는
각각 5/10/19다. 물리 입력, kernel, source, order 및 허용오차를 유지한
1392-cohort 수리 계약은 실행 전에 고정했다. 추가 수리는 수행하지 않았다.

검증 결과

| 항목 | 관측값 | 기준 |
| --- | ---: | ---: |
| panel birth 16→32 최대 observable 상대차 | 1.3349112e-6 | 3e-6 |
| source order 64→96 상대차 | 1.0698907e-15 | 2e-7 |
| grid 256→512 energy fraction | 2.3899308e-5 | 0.02, 감소 필요 |
| grid 128→256 energy fraction | 1.0285278e-4 | 감소 비교 |
| number ledger 상대차 | 1.0666429e-15 | 2e-11 |
| energy ledger 상대차 | 1.3942858e-15 | 2e-11 |
| raw SDCS와 source 대조 | 7.9038206e-16 | 2e-10 |
| local ramp와 Bianchi 표본 source 차이 | 6.9299968e-7 | 3e-6 |

상태 비음성, 인과적 cohort age, t=0 및 source OFF 검사는 통과했다.
8개 focused test는 cohort grid를 잘못 쓰는 negative control과 cutoff-step
birth integral의 정확한 회귀검사를 포함한다. 변경 없는 P02B의 기존
1e11 s time-method 검증은 source SHA 확인 후 재사용했다. 새로운 시간법
정확도 인증이나 continuum/model-error 인증은 하지 않는다.

최종 시각의 선택 전자 주입은 `8.320202688915386e-16 m^-3`,
`5.431501145570614e-14 eV m^-3`이다. 남은 active kinetic energy는
`5.3720967636923064e-14 eV m^-3`, 누적 Coulomb bath heat는
`2.1028721464173746e-16 eV m^-3`, unresolved cutoff kinetic energy는
`2.1370846748847522e-16 eV m^-3`이다. Secondary binding과 excitation
energy는 각각 `9.522214926260066e-17`, `7.482598739019312e-17 eV m^-3`로
별도 보존한다. Primary binding은 source partition ledger에 따로 있다.

직접 생성 <10 / 10–1000 / >1000 eV source의 수와 에너지는
`evidence/VALIDATION.json`에 함께 보존했다. 낮은/높은 구간은 이 계산에서
침적시키지 않았고, P02B cutoff도 P02A에 전달하지 않았다. Gas feedback,
전체 secondary energy domain, cosmological electron transport 및 지연을
포함한 전체 IGM history는 후속 계약이 필요하다.

실행과 재현

Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0, FP64로 실행했다.
최초 실행은 exit 1, 75.529032 s wall / 75.443266 s CPU였다.
수리 네 case는 모두 exit 0이며 closeout도 exit 0이다. 수리 CPU 합계는
817.145330 s, process wall 합계는 817.815238 s다. 병렬 process wall 합계는
전체 경과시간이 아니다. 가장 긴 process wall은 460.414526 s였다.
기록된 계산의 총 CPU는 892.588597 s, 총 process wall 합계는 893.344270 s이며,
그 밖의 orchestration/review overhead는 `UNKNOWN_NOT_ZERO`다.

재현 시 `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`을 사용한다.
원 evidence를 덮어쓰지 않도록 실행기는 이미 있는 출력에 대해 중단한다.
새 evidence 복사본에서 최초 `validate.py` 및 수리 `repair.py --grid N
--birth-order M`의 계약상 네 조합을 실행한 뒤 `repair.py --closeout`한다.
독립 reviewer는 네 저장 case를 재계산해 birth `16→32=1.3349111553e-6`, grid
`1.0285277518e-4→2.3899307537e-5`, source `1.0698906826e-15`, 직접 수/에너지
보존 `3.56e-16/1.39e-15`, 정확히 1392 cohorts를 확인했다. 이 작업자는
commit/push를 수행하지 않았다.

`research-code-task`, numerical/scientific validation 및 closeout 하네스의
계약·최초 실패 보존·유한 수리 규칙을 적용했다. 독립 검토는 PASS_SCOPED로
종료했다. 다음 단계는 parent의 scoped publication 및 남은 domain/interface
계약이며, full history claim은 아니다.
