# PHYS02F 독립 심사

## 판정

**PASS_SCOPED**. 실제 PHYS02E 반환에서 수행한 조기·후기 heat 지연과 birth 혼합의 scalar 분석, 그 유도, 새 adjoint residence 진단의 준비 구현을 수락한다. 이 판정은 `CR-PHYS02F-TAIL-CENSORING-AND-RESIDENCE`의 현재 named 범위에만 적용한다. 새로운 `CR-PHYS02F-NCP-ADJOINT-RESIDENCE`를 실행할 준비의 독립 심사이며, 실제 NCP에서 얻은 체류시간 결과를 수락하는 판정은 아니다.

검토자는 `/root/phys02f_remote_intake`다. 앞선 작업은 PR35의 source intake와 바이트 동일한 기존 파일 복구에 한정되었다. 이번 후보 선택·유도 기여·acceptance 설계·구현·생산 시험에 참여하지 않았다. 발견한 모호성은 owner에게 돌려보냈으며, 수치 convention을 명시적으로 채택한 주체도 root acceptance owner다. 검토자는 수정된 고정 문서와 변경되지 않은 코드·수치 증거를 다시 대조했다.

보이는 host developer label은 `GPT-6 Astra Pro`다. 독립 역할은 확인하지만 실제 backend 신원이나 `Pro`의 router alias를 독립 인증하지 않는다. 기존 채택 Astra v4.0.0 하네스의 독립 review 및 물리·수학 검증 지침을 적용했다. 모델 비용·성능 비교 주장은 없다.

## 고정 검토 대상

최종 `state/REVIEW_PACKET.json` SHA256은 `312ec128e048cbc9a3def6f5a7679031af898de6ca007ad882a2f89049c9791a`다. 76개 candidate 파일과 5개 계약·입력 식별자를 결속한다. 초기 75개 packet의 identity도 갱신 기록에 보존되어 있다. 판정 이후 수정할 수 있는 DAG·연구 상태·FILE manifest·publication 기록은 독립 검토 파일 목록에 넣지 않았다.

검토에서 candidate 76개, 직접 입력 18개, 의존 파일 538개의 실제 바이트·SHA256이 모두 일치했다. 여섯 필수 코드인 `tail_analysis.py`, `residence.py`, launcher, ops, collector, wrapper를 읽었다. 허용 기준, 네 시험 파일, 정확 toy, 원시 최초 실패·repair·closure 로그와 source identities, 유도, 보고서, 상세 NCP 시작문을 함께 검토했다. 기존 9600 pulse의 source-grid adapter와 pulse moment convention도 관련 함수 범위에서 확인했다.

이전 자료를 재실행하지 않았다. 검토 전용 독립 산술은 후보 모듈을 import하지 않고 저장된 JSON·NPZ를 읽는 명령 하나로 수행했다. 실제 명령·종료·source hash는 `REVIEW_EXECUTION_RECEIPT.json`, 전체 비교 결과는 `REVIEW_SAVED_EVIDENCE_RESULT.json`에 있다.

## 이론과 수치 분석

heat 지연 측도는 eventual heat yield로 정규화한 $dF=K(t)dt/H_0$다. electron 수명이나 전체 주입 에너지에 대한 확률로 바꾸지 않았다. $p=F(T)$, ramp moments $R,S$, uncapped moments μ, m₂가 같은 고정 연산자와 source에 속한다는 전제가 유지된다.

조기 raw moments $T(p-R)$, $T^2(p-2R+S)$, 전체에서 조기를 뺀 후기 raw moments, 후기의 시간 원점을 T만큼 옮긴 residual moments가 직접 유도와 일치한다. 특히 residual second moment의 $T^2(1-S)$ 항, 조건부 분모 $1-p$, $T_0$와 $T_0^2$의 복원에 오류를 발견하지 않았다. 열 yield에 따른 birth 혼합과 조기·후기 posterior를 구별하며, 전체 분산 법칙에서 birth 평균 차이 항을 포함한다.

검토 전용 Decimal80 계산은 실제 source JSON의 수치 토큰에서 출발했다. tail raw moments를 먼저 만든 뒤 시간 이동을 적용하는 식과 early variance의 별도 대수식을 사용하여 저장된 FP64 결과 및 Decimal oracle과 비교했다. 두 모델의 두 birth 열과 selected 합, plot CDF·정규화 density, birth 가중치와 분산을 포함해 **516개 비교가 통과**했다. 가장 큰 차이는 고정 scalar 허용한도의 **0.0007511332161403407배**였다. 이 검토는 입력 FP64 오차를 둘러싸는 interval 인증이 아니다.

저장 NPZ 두 개는 모든 배열이 finite였고 pulse shape은 (17, 9611, 2)였다. E, source, 초기 pulse, 17개 sample time을 원시 입력과 대조했다. 열 장부에서 직접 읽어 H0로 나눈 birth·selected CDF와 source JSON의 최대 절대 차이는 양쪽 모두 0이었다. 저장 pulse의 최소값은 0이었다.

| selected 결과 | fullBED | legacy |
| --- | ---: | ---: |
| F(T) | 0.06390638042977166 | 0.06376934057435844 |
| 조기 조건부 평균, yr | 147.369707574 | 147.347185418 |
| uncapped 평균, yr | 14719.993888687 | 15073.220456645 |
| 후기 잔여 평균, yr | 15397.974683897 | 15772.983379282 |

fullBED의 낮은 에너지 birth 비중은 eventual heat 0.1059080920, early heat 0.6762666994, tail heat 0.0669701553, 전체 1차 모멘트 0.00378309074다. 따라서 source ancestry와 체류 에너지 구간을 구분해야 한다는 해석은 자료가 지지한다. 실제 어느 구간에서 지연이 누적되는지는 아직 계산하지 않았다. 도표 PNG를 읽어 축·범례·로그 척도·표본 연결이라는 설명과 자료의 대응을 확인했다.

후보 기여자의 Fraction toy는 4상태의 직접 지수 kernel 적분과 forward/adjoint moments, tail state, 별도 atom 측도의 censoring·mixture를 비교한다. 63개 정확 항등식의 실제 한 번 실행과 exit 0 기록을 검토했다. 이 toy를 다시 실행하거나 실제 9600 연산자의 독립 물리 oracle로 승격하지 않았다.

## 새 adjoint·residence 구현

active block $A=-G_{active}$만 풀며, 전체 absorbing generator를 역행렬 대상으로 삼지 않는다. 코드의 실제 표기는 `A=-G[:n,:n]`이다. A는 upper triangular, 양의 대각과 비양의 비대각이며, $A^T$의 세 번 lower triangular solve와 A의 두 번 upper triangular solve 방향이 맞다. forward RHS 두 개는 각각 두 birth 열을 보존하므로 모델당 solver 호출은 5회다.

$q_0^T b$, $T_0q_1^Tb$, $2T_0^2q_2^Tb$는 저장된 세 모멘트와 일치해야 한다. $T_0q_{0i}w_{ij}$의 합은 birth별 H1이고, $T_0q_{0i}v_{ij}$의 합은 T 이후 잔여 first moment다. $q_{0i}x_{ij}(T)$는 T 시각 상태가 앞으로 만들 heat의 분포로서 미래 체류시간과 다르다. 구현·단위 metadata·보고서가 이 구분을 유지한다. 여섯 오른쪽 닫힌 구간이 모든 E를 한 번씩 포함하며, per-state 합과 별도 bin 합을 birth 및 selected 각각에서 비교한다.

네 NPZ의 전체 identity 검사가 load보다 앞서고, 양 모델의 source와 pulse 의미 검사가 physical import·BUILD 예약보다 앞선다. worker도 내부 preflight를 자체 수행한다. 새 G가 돌아오면 생성 완료를 기록한 뒤, PR35의 실제 G와 CSC format·shape·nnz·data/indices/indptr dtype 및 raw hash, saved E를 비교한다. 실제 inherited parent method object guard와 method name/qualname도 비교한다. loader module alias의 철자만 제외하는 것은 pinned parent bytes와 실제 object guard를 약화시키지 않는다. G 불일치는 resolvent 예약과 풀이 전에 실패한다.

허용된 범위는 fresh 2 G / 2 resolvent block / 10 triangular-solve calls / 900 s이며 pulse와 expm은 0이다. 예약, solver 반환 완료, 다섯 풀이와 crosscheck가 끝난 block 완료를 구분한다. 중간 실패에서는 exact 호출 수를 꾸며내지 않고 [완료, 예약] 구간을 남긴다. deadline은 coordinator 진입부터이고 owned child process group을 종료하는 경로를 정적으로 확인했다. 이번 준비에서 별도 timeout fixture를 실제 실행했다는 주장은 하지 않는다.

wrapper의 실행 실패·수집 성공과 실행 성공·수집 실패가 모두 nonzero인 fixture 결과를 확인했다. collector는 현재 F unit과 고정 의존 파일·원시 run·입력 복사본을 포함하며, return manifest는 자신을 제외한 payload의 정확한 집합·bytes·hash를 기록한다. ZIP 뒤에 생성되는 wrapper sidecar 둘은 외부 family에 결속한다. NCP의 실제 process exit와 외부 환경·로그를 새 envelope에 함께 보존하도록 시작문이 명시한다.

## 발견과 해결

| 발견 | 영향 | 해결 및 판정 |
| --- | --- | --- |
| NCP README가 wrapper 뒤에 collect를 일반 명령처럼 나열 | one-shot 수집을 두 번 수행할 수 있는 문서 모호성 | 정상 순서는 plan/preflight/wrapper 세 단계로 정리. collect는 별도 진단·복구 명령으로 분리됨. RESOLVED |
| 보고서의 Bladt–Nielsen 절 번호 두 곳에 잘못된 backtick | 서지 문장과 Markdown 가독성 | 두 곳 모두 제3절로 수정. RESOLVED |
| `adjoint_relative_nonnegative`가 scale floor를 설명하지 않음 | 미래 NCP가 순수 상대 허용오차로 오해할 수 있음 | root의 `NUMERICAL_CONVENTION_CLARIFICATION.json`을 고정 검토에 포함. RESOLVED_WITH_EXPLICIT_SCOPE |

마지막 항목의 실제 규칙은 각 solve 반환 전체에 대해

`min(result) >= -2e-12 * max(1, max(abs(result)))`

인 **절대·상대 혼합 guard**다. q0에는 추가로 절대 범위 [-2e-12, 1+2e-12]를 적용한다. 코드는 이 식을 사용하며, 이전 E forward solve의 unit floor convention과도 맞는다. owner가 실제 F NCP 실행 전에 이를 명시했고, 코드·기존 다섯 contract bytes·수치 기준·raw 결과는 바꾸지 않았다. 이 기준은 0 근처 성분의 순수 상대 정확성을 인증하지 않는다. signed 값과 잔차를 보존하고 clipping을 하지 않으며, componentwise scaled residual 및 birth별 scalar/bin 교차 검사를 유지하므로 현재 준비 범위에서 수락한다. 이 판단은 실패한 물리 결과를 사후 수락하도록 tolerance를 바꾼 것이 아니다.

최초 collector 시험 실패는 fixture가 SHA 함수를 넓게 대체해 archive metadata까지 잘못 만든 문제였다. 원시 assertion·exit 1·당시 source identities가 남아 있다. 생산 DEP hash 값은 유지하고 fixture가 그 상수만 대체하도록 한 repair는 exit 0이다. root의 명시적 범위 보완에 따른 최종 closure도 exit 0이고, 최종 과학 코드의 identities와 일치한다. NCP 준비 검증은 12개 distinct rows, 24개 row executions, 3개 command다. 원래 실패를 없애거나 성공 횟수로 바꾸지 않았다.

## 남은 gate와 claim ceiling

**TO04 final science ZIP 복구 및 stdlib plan은 이 판정 시점에 미수행**이다. 실제 commit·최종 archive가 만들어진 후의 detached publication gate로 남긴다. 이 심사가 그 복구나 Drive/Dropbox publication을 수행한 것은 아니다. 실제 NCP runtime·resource admission, 새 G의 PR35 parity, 실제 q/occupation/bin 수치, 새 실제 반환의 독립 review도 아직 남아 있다.

열 지연과 uncapped moment는 고정 bath·원자 모델·cutoff·finite grid를 계속 유지한 조건부 결과다. 에너지 grid convergence, continuum tail 안정성, 긴 시간 동안 bath가 고정된다는 물리 타당성, production history를 검증하지 않았다. 작은 backward solve residual과 같은 연산자의 scalar 일치는 물리 오차한계가 아니다. 기존 gate는 모두 유지한다: PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC exporter SOURCE_IDENTITY_UNRESOLVED.

미해결 material blocker는 없다. owner는 이 actual decision의 SHA를 사용해 scoped 상태와 새 NCP admission을 갱신할 수 있다. 최종 publication과 실행은 위의 아직 남은 gate를 실제로 통과한 뒤 진행한다.

## 원문 확인 범위

- [Bladt–Nielsen 2009, 제3절](https://backend.orbit.dtu.dk/ws/files/4616859/tr09_12.pdf): printed p.3의 matrix-exponential density·moment·CDF 식을 확인했다. 해당 구조를 보조하는 문헌이며 bass_cr의 물리 인증 출처가 아니다.
- [SciPy 1.17.0 spsolve_triangular](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.sparse.linalg.spsolve_triangular.html): CSC/CSR, 삼각 방향, vector 및 multi-RHS 규약과 실패 조건을 확인했다. 실제 NCP 실행 증거를 대신하지 않는다.
