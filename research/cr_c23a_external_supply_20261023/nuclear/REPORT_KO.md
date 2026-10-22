# C23A 핵 β 공급 → FS2010 전자 에너지 범위: 한정 연구 결과

## 결론

**FS2010의 실제 표 범위 10–9937.21 eV에 중성자·삼중수소 β 공급을 전체 그대로
연결하는 계약은 승인되지 않았다.** 새 계산은 전자 운동에너지의 지원구간을
정량화했으며, 열·전리·광자 발생량을 계산하지 않았다. 기존 REI β/에너지 장부,
HH81 capture, C21O/C22D ODE는 재실행하지 않았다.

두 종류의 결론을 분리한다. 첫째는 선택한 ENDF 중앙값의 평균과 에너지 상한만
사용하는 조건부 수학적 범위다. 둘째는 Coulomb Fermi function을1로 둔 명시적인
예시 분포 적분이다. 두 결과의 평균이 다르므로 서로 같은 평가 스펙트럼의
검증 결과로 해석하지 않는다.

## 실제 source와 빈칸

검증된 REI commit `9620e1fcc4bdda76e0311206f614234926600381`의
`EVALUATED_DECAY_INPUTS.json`은 수명만 담는다. Gitblob은
`33fd920abce6cc28ff26a850b030bb7b4fd2462e`, SHA256은
`683315ca3464057ea0bc75cbb00c409a4327090a48faa13bc00717ba253b7f26`이다.
이 파일에 없는 평균·끝점 에너지를 기존 코드나 수명에서 추정하지 않았다.

대신 IAEA 배포 ENDF/B-VIII.0 decay ZIP2개를 실제 다운로드하고 CRC와 SHA256을
검사했다. 원본은 EVAL-NOV05, ENSDF conversion20111222, DIST-FEB18의 역사적 평가다.
선택한 중앙값을 고정했으며 최신 최선 평가값으로 승격하지 않았다.

| 전자 source | ENDF Q=ER (eV) | 평균 β 전자 운동에너지 (eV) | 원본의 평균 불확도 | 연속 spectrum |
|---|---:|---:|---|---|
| neutron β | 782347 | 301370 | 기록0; 물리적 정확성0을 뜻하지 않음 | LCON0, 없음 |
| tritium β | 18590 | 5690 | 40 eV; 이번 계산에서 전파하지 않음 | LCON0, 없음 |

ENDF `Q`는 전체 decay 가용 에너지이며 최대 전자 에너지와 일반적으로 같지 않다.
이번 원본은 ER=Q로 기록되어 있다. 따라서 Q는 조건부 support ceiling과 예시
분포의 endpoint parameter로만 사용한다. 자유 중성자 recoil, 전하 상태,
원자·분자 final states를 반영한 정밀 전자 끝점이라고 주장하지 않는다.
오래된 ENDF 수명과 recoil0 항목도 현재 수명 계약이나 물리적 recoil 값을
대체하지 않는다. LNHB PDF 실제 다운로드는503 실패로 보존되며 읽었다고 주장하지 않는다.

FS 표의 실제258행을 읽고 원본 SHA256
`771458627c9f9a99773c3454d9ad370996e1b86030f71e82c011403a6572a974`와
첫·끝 에너지를 확인했다. 전체 FS axis/closure 재감사는 부모의 독립 packet을
재사용한다. 이 연구는 해당 결함을 닫거나 upstream C code를 실행하지 않는다.

## 평균·상한만으로 얻는 범위

양의 전자 분포가 [0,Q] 안에 있고 정규화1, 평균 m을 가진다고 하자.
표 지원구간 D=[L,U]에서 입자수 비율 P_D와 전자 운동에너지 비율 F_D는

\[
0\le P_D\le \min(1,m/L,(Q-m)/(Q-U)),\qquad
0\le F_D\le \min(1,U(Q-m)/(m(Q-U)))
\]

를 만족한다. 점별 부등식의 적분으로 유도했으며, 양의 measure 범위에서는
상·하한을 실현하는 원자적 분포를 구성할 수 있다. 연속 β 물리 분포가 이
극값 분포와 같다는 주장이 아니다. 자세한 유도와 smooth perturbation은
`THEORY_AND_CONTRACT.md`, 유리수로 정확히 검산한 두 counterexample은 RESULT에 있다.

| 선택한 평가 중앙값 | 표 안 입자수의 상한 | 표 안 운동에너지의 상한 | 표 밖 운동에너지의 하한 |
|---|---:|---:|---:|
| neutron β | 62.2696664681% | 2.05324601760% | **97.9467539824%** |
| tritium β | 100% | 100% | **0%: 유의한 양의 하한을 정하지 못함** |

이 수치는 고정한 mean/Q 계약에 조건부다. neutron bound의 강한 제한은 큰
평균 에너지가 표의 상한을 크게 넘는 데서 생긴다. Tritium에서는 mean이 표 안에
있기 때문에 mean만으로 꼬리를 추정할 수 없다. 정규화·평균·endpoint가 모두
같아도 supported fraction은 달라질 수 있으므로 평균 에너지 한 점의 전자를
β 스펙트럼 대신 공급해서는 이 계약을 충족하지 못한다.

## 별도의 F=1 예시 적분

사용한 비정규화 분포는

\[
w(T)=\sqrt{T(T+2m_ec^2)}(T+m_ec^2)(Q-T)^2.
\]

이는 **illustrative allowed phase-space diagnostic, not evaluated beta spectrum**이다.
평가 평균값에 맞추지 않았다. NIST2022 CODATA의 전자 질량 에너지 중앙값
510998.95069 eV를 사용했다. Coulomb/Fermi function, recoil/weak magnetism,
radiative corrections, atomic/molecular final states, screening/exchange,
forbidden shape 및 neutrino mass를 생략한다. 두 decay가 allowed로 분류된다고
해서 이런 효과를 생산용 계산에서 생략할 수 있다는 뜻은 아니다.

| 예시 source | 예시 평균 (eV) | 표 안 입자수 | 표 안 운동에너지 | 높은 꼬리 운동에너지 |
|---|---:|---:|---:|---:|
| neutron β | 302773.719182 | 0.365966577247% | 0.00720572841140% | 99.9927942714% |
| tritium β | 6230.47603410 | 81.9798477290% | 64.6641194379% | 35.3358753883% |

낮은 꼬리 [0,10 eV)의 운동에너지 비율도0으로 버리지 않았다. neutron은
2.31710734123e-12, tritium은5.17380817383e-8이다. 예시 per-primary 장부는
아래와 같으며 상세한 입자수·에너지·이차 moment는6행 CSV와 JSON에 있다.

| 예시 source | low-tail eV/primary | in-domain eV/primary | high-tail eV/primary |
|---|---:|---:|---:|
| neutron β | 7.01559207450e-7 | 21.8170519054 | 302751.902130 |
| tritium β | 0.000322352878321 | 4028.88246424 | 2201.59324751 |

예시 평균은 평가 평균과 각각 약1403.72 eV, 540.48 eV 다르다. 이 차이를
적분 실패로 숨기거나 평균을 강제로 맞추지 않았다. 물리 모델과 correction이
다르기 때문에 평가 spectrum의 정확도 검사로 쓰지 않는다.

## ownership과 구현 경계

입력 carrier는 **electron**, 에너지 종류는 **kinetic**, 단위는 **eV**로 명시한다.
neutron/proton born kinetic energy, photon, antineutrino, total electron energy,
암묵적인 keV 입력은 거부한다. 음수·NaN·미제공 energy 역시 거부한다.

β가 낳은 primary electron만 전자 transport의 후보 source다. Antineutrino와
daughter recoil은 독립 에너지 owner를 가진다. 단순한 Q−mean 장부를 실제
recoil/radiative partition으로 승격하지 않는다. JSON의 toy antineutrino
complement는 recoil-free/massless toy 안에서만 의미가 있다.

낮은·높은 전자 꼬리의 deposition은 `UNRESOLVED`다. heat/ionization 필드는
`null`이며0이 아니다. 표 안 에너지도 FS의 bath/axis/closure 문제가 남아
있으므로 곧바로 physical heating이라고 부르지 않는다. 초기 n/T inventory,
21 species abundance, 반응 rate, 초기조건은 변경하지 않았다. 이 결과는
per-primary 지원구간 계약이며 실제 핵 공급 진폭이나 source rate 계산이 아니다.

## 검증과 자원

새 run ID는 `c23a_beta_fs2010_coverage_20261023_v1`이다. 원본 source/code SHA를
실행 전에 고정했다. CPU5 affinity, native thread1, create-only output,
outer60초/internal55초 제한을 사용했고 실제 실행은 약1.67초였다.

SciPy의 매끄러운 u=sqrt(T/Q) 적분을 mpmath80자리 direct-x 적분 및 닫힌
antiderivative recurrence와 비교했다. 두 source ×3 moments ×4 intervals,
총24건의 서로 다른 moment/interval 비교에서 SciPy 대 mpmath 최대 상대차는
3.87786667531e-16, analytic 대 mpmath는2.96999892079e-60이었다.
입자수·운동에너지·이차 moment의 partition closure, eV↔keV scaling,
정확한 counterexample moments, electron-only API 거부가 통과했다.

위 교차검증은 한 작성자가 실행한 독립 방법 검증이다. 별도의 C9 검토는
부모가 `/root/igm_supply`에 배정했으며 `review/nuclear_supply/`의 evidence를
최종 authority로 연결한다. 본 보고서는 그 검토의 미래 결과를 미리 통과로
기록하지 않는다. `global_error_bound=null`이며 모델 불확도를 quadrature
오차로 대체하지 않는다. 신규 ODE0, 역사적 ODE0, NCP job0이다.

## 네 축과 다음 DAG

| 축 | 현재 결과 |
|---|---|
| EXECUTION | source contract, moment proof, 새 bounded diagnostic 및 수치검증 COMPLETE_SCOPED |
| PUBLICATION | PARENT_PENDING; 이 하위 작업은 GitHub/외부 게시를 하지 않음 |
| BACKUP | PARENT_PENDING; 실제 새 durable backup ACK/byte readback을 주장하지 않음 |
| DAG | coverage4단계 완료 → 독립 C9 → 부모 C10 → corrected spectrum/transport contract OPEN |

본 하위 작업4개 gate는 source pin, moment contract, illustrative operator,
numerical validation이다. 이4/4는 전체 thermochemical/nuclear 연구의 완성률이
아니다. 다음 물리 gate는 corrected/evaluated β spectrum, 명시적 electron-bath
transport, 두 에너지 꼬리의 처리, neutrino/recoil/radiative ownership이다.
FS 원본 axis 및 energy closure 문제는 부모 packet의 상태를 유지한다.
Full nuclear high-energy network와 general triaxial/tilted/polarized CMB는 HOLD다.

## 참조와 재현

source URL 및 정확한 hash는 `source/EVALUATED_ENERGY_AND_DOMAIN_CONTRACT.json`,
원 다운로드·CRC는 `source/PRIMARY_DOWNLOAD_RECEIPT.json`에 있다. 평가 raw DAT2,
기존 lifetime JSON, 도구 반환 source 확인 기록을 함께 보존했다. 재현 코드와
실행 pins는 기존 completed result를 재실행하라는 지시가 아니며, 다음 작업은
이 결과를 재사용하고 새 입력이 있을 때만 새 run ID를 생성한다.

## 독립 검토에서 확인한 추가 adoption 조건

`ADOPTION_OBLIGATIONS.json`은 에너지 frame 조건을 명시한다. 선택한 mean/Q와
[0,Q] support는 같은 frame, 통상 parent rest frame의 에너지에 적용한다.
움직이는 n/T나 cosmic-ray parent의 β 전자를 bath frame에 공급하려면 spectrum과
support의 frame 변환이 먼저 필요하다. Q를 바뀌지 않은 bath-frame 상한으로
사용하지 않는다. Free/atomic/molecular 및 charge-state initial-state 계약도
별도다. 이 확인은 새 계산이 아니며 이미 고정된 source/code/RESULT를 바꾸지 않았다.
