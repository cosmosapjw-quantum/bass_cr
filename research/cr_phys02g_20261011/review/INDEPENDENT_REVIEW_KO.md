# PHYS02G 독립 Astra 심사

## 판정과 허용 범위

**판정: `PASS_SCOPED`.** 고정된 후보의 수학적 부등식 유도, 저장된 모멘트를 사용한 FP64 평가, 실제 F 반환을 기다리는 G frontier 후처리 준비를 이 범위에서 승인한다. 실제 F residence 계산의 성공, 실제 9,600 상태 frontier 결과, 원시 FP64 horizon 끝점의 인증된 수치 포함구간은 이번 판정의 승인 대상이 아니다.

기계 판정의 기준 파일은 `review/INDEPENDENT_DECISION.json`이다. 크기는 **43,577 bytes**, SHA256은 **`9dd9c623fdd881667b6692ea8c3c9fbac08d545ba821fe33f66c2dbd38322002`**이다. 이 문서는 그 판정과 근거를 설명한다. 변경 없는 과학적 주장 상한은 다음과 같다.

- `DERIVED_INEQUALITIES`
- `NUMERICALLY_CHECKED_FP64_EVALUATION`
- `PREPARED_NOT_EXECUTED_FRONTIER`

현재 고정 준비 범위에 대한 미해결 차단 요인은 없다. 실제 NCP 실행을 인정하려면 F의 실제 실행·소모·반환 상태를 먼저 확인하고, 아래의 실행 조건과 후속 독립 심사를 충족해야 한다. 이번 준비 판정은 기존 F 예산을 새로 부여하거나 초기화하지 않는다.

## 독립성, 입력 고정과 실제 읽기 범위

심사자는 이번 요청에서 원격 source intake만 담당한 뒤 별도 고정 packet을 받았다. G 후보 설계, acceptance 기준 작성, 구현, 생산자 테스트 설계에 참여하지 않았다. 심사 중 생산자 코드·계약·수치 결과를 수정하지 않았다. `review/**` 아래의 독립 읽기·산술·판정 기록만 작성했다.

고정 입력은 `review/REVIEW_PACKET.json`의 **122개 파일**이다. packet은 **22,304 bytes**, SHA256 **`2a2389c7abc776f7169ac7d124dd5d7910f8d5a66b7b97fe22f64101fd035916`**이다. 첫 binding과 한 번의 독립 저장 산술 명령에서 각 파일의 실제 길이와 SHA256을 비교했고 불일치는 없었다. 최종 JSON의 `reviewed_files`에 전체 파일 지도가 들어 있다. 이 확인은 읽은 객체의 동일성을 고정한다. 수학·코드·결과의 타당성은 아래의 별도 검토에서 평가했다.

| 고정 계약·입력 | SHA256 |
|---|---|
| `state/SCIENTIFIC_CONTRACT.json` | `517dd569f2e0d0857b37e33a5d90da6475978ab1a43374f3dfbe0323ffb35832` |
| `state/VALIDATION_CONTRACT.json` | `259d6964154cc190050761db092c9edd5499649867f822003db8afdfa42d9aba` |
| `ncp/NCP_EXECUTION_CONTRACT.json` | `06a06f865bba44ce93cc3bcf905cf95440de0978e87ee76529d2f440c6065856` |
| `inputs/INPUT_IDENTITIES.json` | `748076a5628c5a64ad4a057f96c58fd9b54da70dfef9d90e64823234c2df47c9` |
| `inputs/F_BACKUP_DEPENDENCY.json` | `984cb304788d9de7b89fd79d1bd1cf1daa57d12c5e63f5b1267a53743e22740f` |

직접 읽은 의미 자료는 전체 유도문, `moment_bounds.py`, `cached_analysis.py`, `frontier.py`, `postprocess_frontier.py`, 세 테스트 파일, 계약·convention·owner synthesis, 생산자 원시 실행 기록과 실패·수정 기록, 내부 `START_NCP_CODEX_KO.md`와 `REPORT_KO.md`이다. 원래 F wrapper/collector와 관련 launch/residence 구현을 읽어 반환 schema와 성공 receipt 필드를 대조했다. 두 PNG도 실제 열어 범례, 축, 알려진 T 점, survival 곡선과 horizon 표시를 확인했다. PDF는 파일 동일성을 고정했으며 별도로 렌더링하지 않았다.

## 수학·물리 계약 평가

### 비음수 두 모멘트의 strict survival

`X >= 0`, `a = E[X] > 0`, `b = E[X^2]`, `v = b-a^2 > 0`에서 대상은 `P(X > x)`다. 유도의 하계는 `0 <= x < a`에서 `(a-x)^2 / (v+(a-x)^2)`, 그 뒤에는 0이다. 상계는 `0 <= x <= a`에서 1, `a < x < b/a`에서 `a/x`, `x >= b/a`에서 `v / (v+(x-a)^2)`다. 다항식 minorant/majorant의 점별 관계, 모멘트 대입, `b/a`에서의 경계 연결을 확인했다.

엄격 부등호의 원자 질량 처리가 중요하다. 유도는 threshold 위의 원자와 threshold 자체의 원자를 구분한다. 일반 비음수 두 모멘트 분포족에서의 sharp infimum/supremum과 실제 attainment를 구분했으며, 일부 경계가 극한으로만 접근되는 점도 맞다. `v=0`의 점질량과 `a=b=0`의 영점질량은 별도 처리한다. `a=0, b>0`을 유효한 확률분포 입력으로 받아들이지 않는다.

이 sharpness는 일반 두 모멘트 분포족에 대한 것이다. 실제 CR의 공통 연산자 G가 만드는 더 좁은 분포족에서 동시에 달성 가능하다거나 source uncertainty를 인증했다는 주장은 승인하지 않는다.

### T 이후 잔여 모멘트와 anchor

`p=F(T)`, `q=1-p`, `R=E[(1-tau/T)_+]`, `S=E[(1-tau/T)_+^2]`에 대해 잔여 조건부 평균과 두 번째 모멘트

\[
a_T=\frac{\mu-T(1-R)}q,\qquad
b_T=\frac{m_2-2T\mu+T^2(1-S)}q
\]

를 원시 적분 항등식과 대조했다. `t>T`에는 `q L(t-T)`와 `q U(t-T)`를 사용하며, `t=T`의 알려진 survival은 정확한 계약 anchor `q`로 따로 둔다. 일반 두 모멘트 하계의 `x=0` 값을 anchor로 대체하지 않는다. `q=0`은 영사건 분기로 처리하여 나눗셈하지 않는다.

birth 혼합은 `w_j=H0_j/sum(H0)`와 비정규화된 tail 질량 `w_j q_j`를 사용한다. birth별 모멘트 제약이 pooled 제약보다 많은 정보를 주므로 정확히 호환되는 입력에서는 혼합 하계가 pooled 하계보다 작지 않고 상계는 크지 않다. 실제 저장 FP64 입력의 호환성·dominance 검사는 수치 계약의 범위이며, 물리적인 입력 오차 구간을 새로 제공하지 않는다.

### 양의 열 semigroup과 frontier 혼합

`A=-G_active`가 stable이고 `-A`가 Metzler이며 `h>=0`인 계약에서

\[
k_i(r)=h^T\exp(-Ar/T_0)e_i/T_0
\]

는 비음수 미래 열 측도 밀도다. adjoint 계열 `q0=A^{-T}h`, `q1=A^{-T}q0`, `q2=A^{-T}q1`에 대해 이 측도의 0·1·2차 모멘트는 각각 `q0_i`, `T0*q1_i`, `2*T0^2*q2_i`다. 따라서 상태별 정규화 모멘트와 `alpha_ij=q0_i*xT_ij/H0_j`의 단위·정규화가 맞다. `K_j(T+r)=sum_i xT_ij k_i(r)`가 미래 열 혼합의 근거다.

state → birth → pooled 정보 감소에 따른 하계·상계 dominance와 전체 모멘트 혼합 관계를 확인했다. `q0=0` 상태의 typed zero 처리, finite·shape·비음수·분산 조건, 잘못된 확률 표현의 거부가 구현돼 있다. 원시 음수나 잘못된 모멘트를 clip 또는 floor하여 통과시키지 않는다. synthetic frontier 검사는 대수 관계와 준비 코드를 다루며 실제 F의 양의 semigroup을 실험으로 인증한 것은 아니다.

### horizon 판정

`Q_f=inf{t:F(t)>=f}`의 하측 판정은 `L(t)>1-f`, 상측 판정은 `U(t)<=1-f`다. 하측의 strict 조건을 확인했다. 이 작업은 CDF 외삽이나 fitted quantile 점추정이 아니며, 유한한 100% 완료시간도 얻지 않는다. 수학적 판정과 실제 FP64 끝점 사이에는 다음 절의 명시적인 제한이 있다.

## 독립 저장 산술의 실제 결과와 G-R01

허용된 독립 명령을 **1회** 실행했다. Python stdlib `Fraction`으로 원래 F JSON의 decimal token을 정확한 유리수로 읽어 잔여 모멘트와 저장된 곡선 항을 계산했다. 생산자 모듈을 import하지 않았으며, 상계는 생산자와 같은 분기 구현을 복사하지 않고 세 majorant의 최소값으로 비교했다. 실제 cached analysis나 테스트, G 생성, 선형 solve, pulse, expm은 실행하지 않았다.

실행 receipt는 `review/REVIEW_SAVED_ARITHMETIC_RECEIPT.json`이다. **exit 0**, wall **0.3817469610 s**, 사전 상한 **120 s**였다. **3,936개 곡선 비교**가 기존 고정 tolerance 안에 들어왔고, 가장 큰 편차는 허용 tolerance의 **0.0003752200231배**였다. 저장 plot/summary와 원시 결과의 대응도 맞았다. 고정 후보 122개와 직접 사용하는 F pin 12개도 같은 명령에서 확인했다.

그러나 **원시 FP64 horizon 10쌍 중 8쌍**은 F decimal token과 표시 목표분율을 정확한 유리수로 해석하면 적어도 한 끝점의 strict/closed 판정 부호가 달라졌다. 생산자의 FP64 작업 산술에서는 10쌍 모두 기록된 끝점 조건을 만족한다. 차이는 bisection root 인접의 확률 여유 약 `10^-17` 규모다. 이 관찰을 성공으로 덮거나, 양수로 clip하거나, tolerance를 바꾸지 않았다.

| 모형·목표분율 | 정확 token 하측 여유 `L-(1-f)` | 정확 token 상측 여유 `(1-f)-U` | 두 정확 조건 |
|---|---:|---:|---|
| fullBED, 0.90 | `-2.9494817954e-17` | `1.2371165947e-17` | 불성립 |
| fullBED, 0.95 | `5.2278059354e-17` | `-3.9934129159e-17` | 불성립 |
| legacy, 0.50 | `0.4362306594` | `-7.0927338375e-18` | 불성립 |
| legacy, 0.99 | `1.8586706890e-17` | `-3.7974384762e-18` | 불성립 |

전체 10쌍, 정확 분수와 비교 근거는 `review/REVIEW_SAVED_ARITHMETIC_RESULT.json`에 보존했다. 그 파일은 **951,200 bytes**, SHA256 **`339a0dc525235dc4f2b83692e53aecb0bae6de37aeeb849bdddccdc7cd3ab12e`**다. 대응 생산자 결과는 `evidence/analysis/NUMERICAL_ARTIFACT.json`, **2,438,561 bytes**, SHA256 **`4e6b9c36ea26dd39cafec73f173c9f86439d7553a9f8f9cd3b78e896c1d3c56f`**다.

이것은 물리 모형 간 차이라는 증거가 아니다. 저장 decimal 입력의 정확한 해석과 FP64 모멘트·목표분율·경계 계산 사이의 차이다. 기존 `REPORT_KO.md`는 이미 directed rounding이나 exact-input/forward-error certification을 주장하지 않고, 표시 숫자를 바깥 방향 정수 연도로 보여 준다고 명시한다. 그러므로 **수학적 부등식과 수치 점검된 FP64 평가라는 고정 범위에는 통과**하되, 원시 horizon 끝점 쌍을 **인증된 exact-input 수치 포함구간 또는 물리적 불확실성 구간으로 격상할 수 없다**. 정수 표시 또한 새로운 독립 수치 인증을 수행했다는 뜻으로 해석하지 않는다. owner는 이 8/10 관찰과 주장 상한을 최종 설명·상태에 반영하고 원래 결과를 보존하기로 확인했다.

## 생산자 실행·실패·수정 증거 평가

원래 실행 기록을 읽었으며 재실행하지 않았다. 성공 횟수와 실패한 시도를 구분한다.

| 작업 | 실제 보존된 결과 | 평가 |
|---|---|---|
| cached unit test | 첫 7개 exit 1 → fixture-only 수정 뒤 7개 exit 0 | 합성 기대 두 번째 모멘트의 `20.5625`가 잘못됐고 식 `(24-8+0.95)/0.8=21.1875`와 맞게 수정됐다. 생산 코드·기존 tolerance는 그대로다. |
| 두 모형 cached 분석 | 1회, exit 0, 약 2.4958 s | 모형마다 Decimal 80자리 비교 2,077개가 기록됐다. F의 새 실행으로 세지 않는다. |
| exact theory oracle | 1회, exit 0, 622개 검사, 약 0.0644 s | 최대 6개 원자 사용. sharpness witness와 대수 항등식의 보조 증거이며 실제 공통 G embedding 증거가 아니다. |
| NCP 준비 최초 검사 | 9개 통과, 이어서 root completion 2개 통과 | 실패/deadline 기록 보존과 최종 review/DAG 변조 거부가 추가 확인됐다. |
| conformance closure | 운영 4개 통과, frontier 4개 import 오류로 미실행 | exit 1과 원래 stdout/stderr·수정 전 source가 보존됐다. |
| import 한정 수정 후 | 전에 미실행된 frontier 4개만 통과 | 이미 통과한 운영 4개는 다시 돌리지 않았다. |

NCP 준비는 **서로 다른 테스트 메서드 15개**, import-error placeholder 4개를 포함한 보고 행 **23개**, 실제 테스트 메서드 실행 **19개**, 명령 **4개**다. 23개를 모두 독립 실제 통과로 세면 안 된다. 마지막 conformance 수정은 누락된 horizon 출력, 정확한 F schema/sidecar, 원시 `L<=U` 순서, 전체 G source root 밖의 output/ledger 경계를 고정 계약에 맞췄다. 수정 전 자료와 원래 실패를 제거하지 않았으며 최종 고정 소스를 별도로 읽었다.

## NCP 준비·반환 admission 평가와 G-R02

`postprocess_frontier.py`는 plan 단계에서 stdlib만 사용하며, 독립 판정·다섯 계약 pin·전체 FILE manifest·review/DAG binding을 요구한다. F wrapper return-family의 정확한 schema, ZIP 한 개와 필수 sidecar, member 안전성·동일성, 원래 F source 12개, 입력 source, 내부·외부 receipt 일치, actual exit와 작업 횟수, runtime·thread, 실제 E의 연산자 parity를 검증하는 경로를 직접 읽었다. worker는 family와 own admission을 다시 확인한 후 `allow_pickle=False`로 배열을 읽는다.

코드상 frontier 후처리는 실제 F가 만든 `xT`, adjoint 결과와 알려진 source를 사용하며 새로운 G·solve·pulse·expm을 호출하지 않는다. runtime pin, 9,600 상태와 float64 shape, 모멘트의 확률적 적합성, birth/pooled/state dominance, source 밖의 create-only output·ledger와 단일 작업 예약을 검사한다. coordinator는 전체 **90초**, 후처리 **최대 1회** 한도를 갖고 실패·deadline·로그를 보존한다.

**현재 실제 F 반환 family를 관측하지 못했으므로 완전한 actual-family happy path와 실제 9,600 상태·90초 frontier 수행은 실행되지 않았다.** 준비 코드 읽기와 합성 검사만으로 그 runtime의 성공이나 실제 모형 결과를 인정하지 않는다. 현재 조회한 GitHub/지정 백업에서 F 반환이 보이지 않았다는 기록과 전역 실행 부재는 다르다. 공개되지 않은 NCP 실행 및 F 예산 소모 여부는 **UNKNOWN**이다.

기존 F ZIP의 로컬 생존본은 **26,927,005 bytes**, SHA256 **`9d91d2971eab2db05e0039fe1fc2a5827086a28d585e792d56f6851840e6ebef`**이며 G의 dependency와 일치했다. 이는 새로운 원격 restore 또는 실제 F 수치 반환 검증을 수행한 사실이 아니다. 내부 START는 이 기존 F 전체 의존성을 이용해 추가 사용자 첨부 없이 복구하도록 작성돼 있고, 기존 F 예약·진행·종료 상태를 먼저 확인하여 재사용 또는 대기하도록 한다. 새 G 준비는 F 재실행·재시도 권한을 만들지 않는다.

후속 순서는 실제 F 상태 확인, 기존 승인에 맞는 actual F 반환 확보, F family admission, 한 번의 G 후처리, **actual F+G에 대한 새 독립 심사**, 결과·실패기록·ledger·source와 실제 family를 포함한 전체 반환이다. G 결과의 family 참조가 원래 F ZIP 자체를 자동 포함한다는 뜻은 아니므로, 내부 START의 전체 외부 반환 요구가 유지돼야 한다.

## 유지되는 물리 gate와 출판 경계

| gate | 이번 심사 후 상태 |
|---|---|
| PHYS02_DELAY | OPEN |
| production_history | HOLD |
| atomic_G02 | UNRESOLVED |
| b_grid | NO_GO |
| all_bound | OPEN |
| R17B2B | NO_CERTIFIED_SOURCE_SHARPENING |
| CCC_2026_exporter_identity | SOURCE_IDENTITY_UNRESOLVED |

owner는 이 실제 판정 SHA를 최종 DAG에 binding하고 `RESEARCH_STATE`, `DECISION_LOG`, FILE manifest 및 실제 출판·백업·복구 기록을 추가할 수 있다. 그러한 후속 leaf는 고정된 122개 후보에 소급하여 포함되지 않는다. 최종 clean recovery/stdlib plan의 실제 receipt와 배포 START의 객체 ID 일치 등 P01 출판 사실은 해당 결과가 생긴 뒤 확인해야 한다. 이번 결정은 아직 존재하지 않는 commit·backup·복구 성공을 미리 인정하지 않는다. 고정 후보 코드·계약·결과를 바꾸면 영향 범위에 대한 새 심사가 필요하다.

## 참조와 심사 완료 기록

외부 일차 문헌은 Bertsimas–Popescu의 INSEAD working paper 원문을 열어 moment problem의 sharp optimum 정의와 polynomial dual/weak duality 부분을 확인했다: <https://flora.insead.edu/fichiersti_wp/inseadwp2002/2002-01.pdf>. 확인한 범위는 인쇄 p.2의 정의, pp.6–7의 dual argument, pp.15–16의 기존 모멘트 부등식 표다. 이 문헌은 일반적 방법론의 근거이며 현재 CR 데이터나 전체 새 식의 실증 검증을 대신하지 않는다. 현재 식의 적용·strict 경계·단위·혼합은 고정 source와 위 독립 읽기·저장 산술에 근거한다.

정확한 backend attestation은 제공하지 않는다. 독립 역할과 실제 수행한 명령만 기록한다. 이 심사에서 실제 cached 분석 재실행 0, 후보 테스트 실행 0, G/선형 solve/pulse/expm 0, 실제 NCP 실행 0, Git·백업 원격 변경 0이다. 단일 독립 저장 산술의 원문·예약·stdout/stderr·receipt·전체 결과와 기계 판정은 함께 보존했다.
