# R4T 독립 검토

판정: **조건부 유도·구현 범위 수용**. 미해결 blocking finding은 없다. 구현 담당과 별도로 원 정리와 코드를 읽어 부호, 정규화, 함수공간과 적용 범위를 검토했다. 기존 suite나 담당자의 신규 suite를 중복 실행하지 않았다. 담당자 검증은 신규 테스트 30개, projector Fraction 항등식 33개, 저장 행렬 6개 비교이며 서로 다른 증거로 구분한다. 검토 대상의 정확한 SHA-256은 `INDEPENDENT_REVIEW.json`에 고정했다.

## 검토 결과

- **Projector:** `W=S(Pi_dot+[Pi,A])`와 projector 미분식에서 정규화된 rate의 대각 블록이 사라진다. `E=Y†[(D+iH/ħ)J+S Jdot]L_G^-†`의 부호가 맞고 `rho=||E||`에는 추가 인자 2가 없다. 인자 2는 상태별 `|Pdot|≤2sqrt(P(N−P))rho`에 들어간다. Schur residual, Cholesky 오른쪽 whitening, 시간 의존 좌표변환의 Jdot 항도 일치한다.
- **Angle:** endpoint regularization의 분모는 `p(1−p)+epsilon+epsilon²`로 닫힌다. 따라서 p=0,1을 포함한 각도 적분 부등식과 clipped sine-square 구간이 유효하다. 정수 제곱근 기반 올림, 구간에서 p(1−p)의 최댓값, dyadic quadratic admission이 정확하다. 작은 초기 population의 이득은 같은 endpoint의 인증된 population을 실제로 가질 때만 적용된다.
- **Galilean:** ETF의 공간 위상과 `−i|v|²t/2` 위상을 함께 유지하면 `Hkin−i∂t`의 두 속도 항이 상쇄된다. H1 약형과 다른 중심의 test function에서도 성립한다. 같은 중심 Galerkin 잔차의 소거가 다른 중심의 약형 잔차까지 소거하지는 않는다. potential leakage의 물리적 직교투영 경로에는 Gram 역행렬 증폭 인자가 필요 없지만, 약형 잔차에는 유한 test-space의 metric bound가 필요하다. 상수 `927/200`, `rho≤8409/800`, bridge `25227/50=504.54`를 확인했다. 확률 변화 상계는 여전히 1이고 목표 `5×10^-6`은 실패한다.
- **Regularity/transfer:** 다섯 repaired radial mode의 shell derivative jump와 두 l=1 mode의 origin obstruction은 strong L2 Coulomb residual을 배제한다. archived mode의 value jump 때문에 작은 cellwise repair를 global H1 거리로 쓸 수 없다. finite-metric transfer는 양쪽 `Gamma_k`에 의한 norm growth를 보존하며 `R=L1T−TL0−Tdot` 및 covector B의 부호가 맞다. coefficient error E, common-L2 embedding error beta, projector mismatch delta를 별도로 요구한다.
- **저장 행렬 비교:** 여섯 원 모델 snapshot의 S/H Hermitian projection과 `Sdot=D+D†` 구성은 명시되어 있다. 이는 새 factorization의 FP64 대수적 일치만 검증한다. G02, 연속 구간, 실제 상태, rigorous rounding bound를 검증하지 않는다.

## 해결된 지적

`PROJECTOR_RATE_THEOREM.md` §6의 Hilbert-space residual 표기에 strong operator domain 조건을 명시하도록 요청했다. 담당자가 L2 residual에는 해당 조건이 필요하고 H1-only reference에는 약형 pairing만 적용한다는 문장을 추가했다. 코드와 테스트에는 변경이 없어 suite 재실행을 하지 않았다.

## 남은 경계

후보 reference 채택, 실제 B0 상태의 이식, tail endpoint population, 연속 majorant 및 trajectory error는 이 검토로 인증되지 않는다. ±12의 수치 결과를 ±32의 static matrix에 붙일 수 없다. canonical coefficient SHA와 pretty-file SHA의 과거 필드 혼동은 원 파일에서 두 identity를 따로 검증해 해소했으며 과거 certificate를 수정하지 않았다. `capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`와 기존 연속/trajectory gate를 유지한다. 검토 과정의 신규 physical/native query와 physical propagation은 모두 0이다.
