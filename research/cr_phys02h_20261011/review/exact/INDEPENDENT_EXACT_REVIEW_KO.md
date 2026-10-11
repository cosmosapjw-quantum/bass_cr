# PHYS02H exact scalar 독립 판정

## 판정과 독립성

**PASS_SCOPED.** 고정된 계약 아래 생성된 20개 정수 초 구간을, 저장된 십진 모멘트가 정의하는 비어 있지 않은 확률분포군에 대한 정확 산술 인증으로 채택할 수 있다. `selected_record`와 `birth_defined`는 각각 독립적으로 정의된 제약이며 서로 교집합하지 않았다. 실제 cascade 모멘트의 오차·연산자 binding·전체 격자 정확성·물리 bath의 장시간 유효성은 이 판정의 대상이 아니다.

검토자 `/root/phys02h_decision_review`는 후보, 원래 허용조건, 구현 또는 생산 테스트의 작성에 참여하지 않았다. 고정 코드와 실제 산출물을 읽은 뒤 생산 모듈을 import하지 않는 별도 Fraction 참조 프로그램을 한 번 실행했다. 현재 변경 중인 parallel operator 코드와 NCP launcher는 이번 판정에서 읽거나 승인하지 않았다. `DERIVATION_KO.md`는 전체를 읽었지만 병렬 관련 절에 대한 판정은 별도의 고정 실행 manifest까지 보류한다.

프로젝트의 source-bound canonical Astra v4.0.0 흐름을 적용했다. 현재 상속된 호스트 라벨과 실제 backend alias의 관측을 구분하며 exact alias는 `MODEL_UNRESOLVED`이다. 부모가 전달한 이전 explicit-model reviewer의 unsupported default-effort 거절은 **실행 전 routing/runtime 실패**이다. 그 시도에서 과학 검토나 수치 실행이 이루어졌다고 계산하지 않는다.

## 고정된 입력과 실제 검토 범위

| 항목 | SHA256 |
|---|---|
| `state/SCIENTIFIC_CONTRACT.json` | `a49b1fa88c86d46c4e37cdb7ba37fbd44e5fa05511febc3a3089ab5ed5331dc4` |
| `research/DERIVATION_KO.md` | `d46e6bdfb375a34a148db5a18d6ccef450e41c9a6ba15cde9a4e124a64318250` |
| 원래 F cached artifact | `dfdca59ca0b4131c6143fe3cf0e402a7b18efb113a9af9bcc82a66696f5ec6f5` |
| `src/exact_moments.py` | `d3af8b7b985668b5b8d769119273d712b12ffc6e42b8e8f64775b3d306a6405b` |
| `scripts/run_exact.py` | `ff1194213d06e281560b3027fa08581810a995cf0ad973ab0a95ceabab9d1ff2` |
| `tests/test_exact_moments.py` | `d0f77c1b96e6af4dd848aa87c6e50fa30ef3990654e210ab1ba0dc9886e6ba9c` |
| `evidence/exact/EXACT_CERTIFICATES.json` | `246cf5d53381380b5eef15debdad53d7d3dcae91cb1db2dcc74a4029b8202113` |
| `review/exact/INDEPENDENT_REFERENCE.py` | `09a1df406576843ca028757abd4a787d6baf488cef57a9940abef72348dc4883` |
| `review/exact/INDEPENDENT_REFERENCE_RECEIPT.json` | `0f8f6cbbbb6d0089cf33ab25cc8216a1c0063852d3f6f56c12a845585cc82965` |

생산 실행 영수증은 exact analysis 1회, 실제 exit 0, 내부 wall 약 0.214335초와 외부 process wall 약 0.291567초를 기록한다. 두 시간은 중첩되어 있으므로 합산하지 않는다. 생산 targeted test는 실제 8개 통과이며, 이 검토에서 다시 실행하지 않았다.

독립 참조 실행은 2026-10-11 08:54:42.663536–08:54:42.738034 UTC, 실제 exit 0, 내부 wall **0.074502792초**, 60초 상한의 한 번 실행이었다. stdout·stderr와 실행 영수증을 같은 디렉터리에 보존했다. 새 G, F retry, pulse, expm, resolvent, linear solve, 이전 suite 재실행은 모두 0이다.

## 수학적 검토

시간은 초이고 `T=10^10 s`, `year=31557600 s`는 정확 상수이다. 정규화는 최종 열량 `H0>0`을 사용한 `dF=K(t)dt/H0`이다. 전체 주입에너지의 비율이나 입자 생존확률로 재해석하지 않는다.

### 모멘트 분포군의 비공집합성

초기 질량 `p=P(tau<=T)`에 대한 `U=(T-tau)/T`는 `[0,1]`에 있다. `R/p=E[U]`, `S/p=E[U²]`이므로 `0<=S<=R<=p`, `R²<=pS`가 필요하다. 생산 코드는 이 조건을 정확하게 확인하고, 0 또는 1점의 퇴화 경우와 2점의 일반 증인을 구분한다. 일반 증인의 위치 `0,S/R` 및 고점 질량 `R²/(pS)`는 조건부 U의 두 모멘트를 재현한다. `U=0`인 질량은 `tau=T`에 속하므로 p에 포함하는 것이 맞다.

잔여 질량은 `q=1-p>0`이다. 독립 프로그램은 생산식의 단순 복사 대신 초기 시간 모멘트 `T(p-R)`와 `T²(p-2R+S)`를 전체 모멘트에서 뺀 뒤 `X=tau-T`로 중심을 옮겼다. 이 결과는 생산 코드의

`a=[mu-T(1-R)]/q`,

`b=[m2-2T mu+T²(1-S)]/q`

와 정확히 일치했다. 단위는 각각 s, s²이다. 검사한 모든 행에서 `a>0`, `v=b-a²>=0`이다. `v=0`의 양의 한 점, `v>0`의 `a/2`와 `a+2v/a` 두 점은 모두 strict residual support `X>0`에 있으며 두 모멘트를 재현한다.

독립 프로그램은 저장된 증인에서 `region` 라벨만 신뢰하지 않고 실제 `tau<=T`와 `tau>T`를 재분류했다. 원자들의 비음수 질량·정규화·지지집합을 확인하고 p,R,S,mu,m2를 직접 적분했다. 두 모델의 selected 2개, birth 4개, birth-pooled 2개로 총 **8개 증인**이 모두 원래 정확 유리수 모멘트를 재구성했다. 이 유한 원자 증인은 분포군이 공집합이 아님을 보이며, 실제 유한율 cascade가 원자적인 시간분포를 갖는다는 주장은 아니다.

### 확률 경계와 끝점의 부호

비음수 X, 평균 a, 분산 v에서 x<a이면 Cantelli를 `X<=x`에 적용해 `P(X>x)>=(a-x)²/[v+(a-x)²]`을 얻는다. x>=a의 하한 0은 유효하다. 상한은 적용 가능한 `1`, Markov `a/x`, x>a일 때의 Cantelli `v/[v+(x-a)²]`의 최솟값으로 독립 계산했다. 이는 생산 코드의 `x<=a`, `a<x<b/a`, `x>=b/a` 분기와 정확히 일치했다. `x=b/a`에서 두 비자명 상한은 `a²/b`로 일치한다. `v=0`이면 `P(X>x)=1[x<a]`로 처리해야 하며 생산 코드와 테스트는 등호에서 0을 사용한다.

`t=T`에서는 잔여 지지집합이 엄격하게 양수이므로 `P(tau>T)=q`를 정확하게 사용한다. t>T의 pooled 및 birth residual 경계는 이 q와 양의 열량 가중치로 결합된다. selected 표현은 자기 unconditional·pooled 두 경계만, birth 표현은 자기 unconditional·pooled·birth 세 경계만 결합한다. 각 성분이 같은 표현의 모든 허용분포에 대한 유효 경계이므로 lower의 최댓값과 upper의 최솟값도 유효하다.

`Q_f=inf{t:F(t)>=f}`에 대해 아래 끝점에는 `L(t_lo)>1-f`, 위 끝점에는 `U(t_hi)<=1-f`가 필요하다. 전자는 `F(t_lo)<f`와 CDF의 오른쪽 연속성으로 `Q_f>t_lo`, 후자는 `Q_f<=t_hi`를 준다. 따라서 이번 결론의 정확한 구간 표기는 **`t_lo < Q_f <= t_hi`**이다. 단순 근삿값 표시에 따른 ±1초 규칙을 쓰지 않았다.

모든 lower/upper 성분은 t에 대해 비증가하고, T에서 정확값 q를 쓰는 접속도 이 성질을 해치지 않는다. 실제 20개 인증의 종료점과 인접한 정수 초에서 반대쪽 조건을 확인했다. 따라서 bisection에서 얻은 마지막 strict lower와 첫 closed upper를 재현할 수 있다. 지수 확장·이분 횟수는 각각 계약 상한 64·80 이내였다. 연 단위 표현은 `integer_seconds/31557600`과 정확히 일치하며 `decimal_convenience`는 증명 입력으로 사용하지 않았다.

## 독립 대조 결과

| 검사 | 실제 통과 개수 |
|---|---:|
| 분모 양수·기약 표현을 갖는 저장 유리수 | 1,388 |
| 정수 교차곱·부호·정확 여유·relation | 240 |
| 정확 원자 증인과 원래 모멘트의 재구성 | 8 |
| 두 모델 × 두 표현 × 다섯 확률의 구간 | 20 |
| 끝점별 성분 경계 쌍 | 100 |
| 최종 인접 정수 초의 부등식 전환 | 40 |
| 별도 유한분포의 strict survival 검사 | 226 |

별도 유한분포 검사는 delta0, 양의 결정론적 시간, 0을 포함한 두 점, 비대칭 꼬리, 세 점 분포를 포함한다. 원자 위치·평균·분기점에서의 등호도 확인했다. 이는 직접 유도의 제한된 실행 검산이며 모든 분포에 대한 증명은 위의 부등식과 구성에 근거한다.

## 남는 제한과 해석

차단할 scalar 결함은 발견하지 않았다. 다만 다음 제한은 채택 조건의 일부이다.

1. **두 기록 표현을 합치지 않는다.** 두 모델 모두 H0,p,R,S,mu,m2의 selected 값과 birth-defined 값이 정확하게는 다르다. 입력은 float 변환 없이 원래 JSON 숫자 토큰에서 Fraction으로 읽었고 차이를 그대로 보존했다. 이 사실은 physical SSOT의 교체를 허가하지 않는다.
2. **두 표현의 구간 폭 차이를 극소 십진 오차의 효과로 설명하지 않는다.** birth 표현에는 selected 표현에서 사용할 수 없는 birth별 제약이 추가되어 있다. 큰 폭의 sharpening은 이 추가 제약과 관련되며, 이번 작업은 그 효과와 작은 기록 불일치를 분리한다.
3. **인증 대상을 명시한다.** 20개 구간은 기록된 십진 모멘트가 정의하는 분포군에 조건부인 정확 산술 인증이다. 저장된 모멘트의 전방 오차, 원래 실제 연산자, 격자·연속체 수렴, 실제 bath, 물리적 불확실성 또는 실제 quantile의 값은 인증하지 않았다. 일반 2모멘트 경계의 개별 sharpness와 모든 정보를 결합한 전역 sharpness도 구분한다.
4. **기존 상태를 보존한다.** 이전 G-R01의 raw FP64 결과와 failure 기록은 수정하지 않는다. `F HOLD_OPERATOR_BINDING_UNRESOLVED`, `G frontier BLOCKED_BY_F_OPERATOR_BINDING_HOLD`, `PHYS02_DELAY OPEN`, `production_history HOLD`, `atomic_G02 UNRESOLVED`, `b_grid NO_GO`, `all_bound OPEN` 등 기존 gate는 그대로다.
5. **이번 scalar 판정은 NCP 실행 승인에 사용하지 않는다.** 큰 행렬 생성·병렬화·정확 값 보존·resource admission·실제 NCP 64 CPU 성능은 별도 실행 manifest와 독립 admission이 필요하다.

후속 보고에는 정확한 정수 초 인증을 원본으로 사용하고 연 단위 소수는 표시로만 제공하면 된다. 이번 scalar leg에는 추가 테스트나 수치 재실행이 필요하지 않다.
