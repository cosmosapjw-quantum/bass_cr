# CR-PHYS02B 독립 최종 검토

## 1. 판정과 승인 범위

**판정: PROMOTE_SCOPED.** 고정된 CR-PHYS02B 후보를 **조건부 유한 격자 연구 모형의 유도·구현·수치 결과**로 승격한다. 이 범위에서 승격을 막는 수식, 분기 계수, 부호, 단위 또는 구현 오류는 발견하지 않았다. 아래의 원자 입력 불일치와 물리적 제한은 계속 유효하다. 모형의 물리 정확도, 전체 PHYS02 완료, 생산 이력 도입은 승인하지 않는다.

승격 대상은 주어진 \(Q_e(W,t)=tA(W)\), 빈 초기 전자 분포, 고정된 \(100\,\mathrm K\) bath에서 \(0.1\!-\!900\,\mathrm{eV}\), \(0\le t\le10^{10}\,\mathrm s\)를 다루는 명시적 모형이다. HI/HeI의 채택 총 이온화율에 정규화한 인쇄 BED 공유 분포, 27개 CCC \(n=2\ldots4\) 여기 채널의 유효 비용, 지정된 leading-log Coulomb drift를 함께 사용한다. 최종 활성 격자는 4,800개다.

모형의 원자 입력이 일관된 단일 자료 집합으로 인증된 것은 아니다. He의 총률·공유 분포 불일치와 CCC 여기 비용의 분광학 차이는 이 판정에서 해소된 것으로 취급하지 않는다. 따라서 이 승격은 후속 원자 일관성 연구에서 비교할 수 있는 고정 기준선과 그 계산 결과에 한정된다.

| 상속 gate | 판정 후 상태 |
|---|---|
| PHYS02_DELAY | OPEN |
| production_history | HOLD |
| atomic_G02 | UNRESOLVED |
| b_grid | NO_GO |
| all_bound | OPEN |
| R17B2B | NO_CERTIFIED_SOURCE_SHARPENING |

구체적인 수정 요구 없이 이 후보의 독립 최종 gate를 닫는다. 위 gate의 해소에 필요한 추가 연구가 완료되었다는 뜻은 아니다.

## 2. 검토자 독립성 및 고정 대상

검토자는 **/root/phys02_decision_review**다. 이 CR-PHYS02B 후보의 생성, 유도, 구현, 검증 설계 및 과학 suite 실행에 참여하지 않았다. 이전 CR-PHYS02A의 독립 판정은 별도 후보의 완료된 작업이다. 이번에는 새 후보가 고정된 뒤 원본 코드·증거를 읽고 독립 판정을 수행했다. 다른 검토자에게 이 판정을 재위임하지 않았다.

호스트 선언은 GPT-6 Astra Pro이며 모델·effort override는 요청하지 않았다. 실제 backend 모델·effort는 독립적으로 관측하지 않았으므로 UNKNOWN으로 기록한다. 모델 성능 평가는 수행하지 않았다.

고정 기준은 다음과 같다.

- 기준 부모 HEAD: `58c8e1cda5c8f8ca8b83269cb89899ea40ab91fe`
- packet: `review/REVIEW_PACKET.json`
- packet SHA256: `0c32320b708ab6296e3d7777f656b81dfa0f39906fce9ac5c28cb88fe311219e`
- packet 고정 시각: 2026-10-10 12:14:43.618500 UTC
- 고정 파일: 27개. 실제 bytes 길이와 SHA256를 독립 계산하여 **27/27 일치**를 확인했다.
- 코드 `src/causal_cascade.py` SHA256: `d87a9cc122125b2d37b47f261f57eab698baa59e07a6b21723860f39313c7b72`
- 검증 코드 `tests/verify_cascade.py` SHA256: `28ffa8391f6786ac7348846c8a6c461ec4f4e9694c86d7f7deccf6a146373e52`
- 독립 oracle 코드 SHA256: `d3c6bdcd27c80e3b5ff72558cb65608b168de5cb9c13a990147103a8fb155942`
- R002 수치 결과 SHA256: `1f2ebaef36c1d77ae4fcab83ef81f0618060a701eaebb5db611307aa8b090ced`

실제 검토한 모든 고정 파일과 hash는 함께 작성한 `FINAL_DECISION.json`의 `fixed_target.reviewed_files`에 수록했다. 텍스트 파일은 직접 읽었고, 큰 수치 JSON은 파싱하여 metadata, 원시 check 값, 격자 변화, 최종 결과 및 진단 항목을 확인했다. NPZ는 배열을 읽어 별도의 장부 산술을 수행했고, 진단 그림도 열어 확인했다. 고정 보고서와 연구 상태 snapshot은 수정하지 않았다.

부모 manifest가 참조하는 PHYS01/PHYS02A 파일 4개의 실제 bytes도 모두 일치했다. CCC registry가 참조하는 27개 raw table 역시 hash, 에너지 증가성, 유한값, 단면적 비음성, 첫 zero row와 비용의 일치, 900 eV 이상 자료 범위를 확인했다. 기존 PHYS01/PHYS02A 과학 suite를 재실행하지 않았다.

## 3. 수식과 구현의 일치

### 분기와 에너지 공유

이온화 사건의 속도는 \(n_s\sigma_s(E)v(E)\)다. 부모 전자 하나를 제거하고, 느린 딸전자 에너지 \(W\)와 나머지 딸전자 에너지 \(E-B_s-W\)를 각각 한 번 넣는다. 적분 구간 \(0\le W\le(E-B_s)/2\)는 두 동일 전자를 이중으로 세지 않는 convention과 일치한다. 사건마다 전자 수는 하나 증가하고 결합 비용 \(B_s\)는 종별 장부로 간다.

여기 사건은 부모 하나를 제거하고 \(E-\Delta_s\)의 딸전자 하나를 넣으며 \(\Delta_s\)를 해당 종의 여기 에너지에 기록한다. 이 \(\Delta_s\)는 채택된 유효 비용이다. 두 과정 모두 에너지·전자수 projection은 비음의 선형 가중치로 구성되어 두 보존량을 함께 유지한다.

총 단면적의 면적 단위, 미분 공유 분포의 면적/eV, \(n\sigma v\)의 \(\mathrm s^{-1}\), stopping \(b(E)\)의 eV/s, 그리고 eV→J 및 시간 무차원화의 위치가 일관된다. NIST 공식 식 1·3·4와 Müller 원문의 반구간 적분 convention을 대조했다. [NIST 공식 식](https://physics.nist.gov/PhysRefData/Ionization/Eqs/latex.html), [Müller 등 원문 Table I 및 식 42–47](https://backend.orbit.dtu.dk/ws/portalfiles/portal/4857374/Naulin_paper.pdf)

### 인과 전파와 보존 장부

활성 상태는 \(E_jN_j\)로 에너지 가중된다. Coulomb drift는 아래쪽 이웃으로의 rate \(b(E_j)/(E_j-E_{\rm prev})\)와 에너지 차이만큼의 heat를 결합한다. 시간 \(u=t/T\)에 대한 augmented matrix는
\[
\frac{d\mathbf x}{du}=G\mathbf x+u\mathbf a,\qquad \mathbf x(0)=0
\]
를 구현한다. 이때 \(G=T G_{\rm physical}\)다. 이 선형 모형의 비대각 원소가 비음이므로 비음성 전파를 갖는다. 소스 ramp와 초기조건을 실제 코드에서 확인했다.

장부의 의미는 다음 두 식이다.
\[
E_{\rm active}+H+I_{\rm H}+I_{\rm He}
 +X_{\rm H}+X_{\rm He}+K_{\rm cut}
 =E_{\rm injected},
\]
\[
N_{\rm active}+N_{\rm cut}
 =N_{\rm injected}+N_{\rm ion,H}+N_{\rm ion,He}.
\]
이온화 횟수는 두 번째 식의 자유전자 증가에 사용한다. 여기 에너지나 cut kinetic energy를 heat와 합쳐 세지 않는다. 저에너지 경계 통과의 에너지·전자수 counter는 별도의 진단이며 위 에너지 장부에서 제외되어 있다.

0.1 eV 아래로 나가는 전자의 남은 운동에너지는 별도로 보존된다. 이 양을 이미 bath에 전달된 열로 간주하지 않는다. 경계 바로 위 projection에는 ghost boundary에 따른 수치적인 조기 흡수 효과가 있으며, 이것은 유한 격자 근사의 한계다.

같은 frozen generator의 transient block에 대한 resolvent로 terminal yield를 구하는 방식도 타당하다. 다만 이는 그 모형의 수학적 종단 반응이다. 실제 bath나 우주 이력을 무한한 시간까지 고정했다는 물리적 증거가 아니다.

## 4. 원자 입력의 불일치와 source completion

### He 총률과 공유 분포

고정 He 총단면적은 \(Q=0.8841\)을 사용한다. 인쇄 BED 다항식은 \(N_i=1.61008\), \(Q_{\rm df}=0.9130416667\)을 함의한다. 인쇄 \(K_{\rm BED}=1.1860\)도 다항식으로부터 얻는 \(2-N_i/N=1.19496\)과 일치하지 않는다. 원문 표의 읽기와 코드의 적분·정규화 해석을 직접 대조했다.

양의 에너지 공유 모양을 채택 총률에 정규화하면 조건부 확률 kernel은 정의된다. 그러나 그 조작으로 서로 다른 원천 상수가 하나의 물리적으로 일관된 자료가 되지는 않는다. NIST의 미분 단면적 정규화 설명은 이러한 구성의 의미를 뒷받침하지만, 현재 후보가 NIST CGI 내부 자료를 그대로 재현했다는 증거를 제공하지 않는다. [NIST 설명 B절](https://physics.nist.gov/PhysRefData/Ionization/intro.html)

따라서 이 불일치는 **현재의 조건부 모형 승격에는 비차단 항목**, **원자 정확도·일관성 승격에는 계속 열린 근거 결함**이다. 정규화 오차나 quadrature 수렴값으로 물리 차이를 대체해서는 안 된다.

### CCC의 여기 비용

채택 비용은 CCC 표의 native first-zero marker다. 예를 들어 He \(2\,{}^1P\)의 비용 21.1156 eV는 직접 읽은 NIST level 값 21.2180 eV와 다르다. [NIST He 원자 표](https://physics.nist.gov/cgi-bin/Ionization/atom.php?element=He)

입력 registry와 코드가 이 값을 같은 방식으로 사용하는 것은 확인했다. 그러나 독립적인 target-state energy certificate는 확보되지 않았다. 따라서 에너지 보존이 증명하는 것은 채택된 유효 비용의 장부 일관성이다. 실제 여기 비용의 정확도는 별개다. 또한 여기 에너지 저장량으로부터 광자 수, 방출 시점, 준안정 상태의 분기, 재흡수량을 결정할 수 없다.

### 실행 전 addendum

원래 계약은 11:51:51 UTC에 고정되었고 source-completion addendum은 12:01:26 UTC에 채택되었다. 첫 full 계산 R001은 그 뒤 12:01:57 UTC에 시작했다. 따라서 이 변경은 실패한 수치 결과를 보고 acceptance threshold를 바꾼 것이 아니다.

원 CGI 수치 비교는 외부 HTTP500 실패로 `NOT_EVALUATED_EXTERNAL_SERVICE_FAILURE`로 남아 있다. 원래 상대 허용값 \(5\times10^{-4}\)도 기록에 보존되어 있다. 대신 실행된 공개식 기반 적분은 더 좁은 수학적·단위 일관성 검사다. 이를 CGI 수치 검증의 PASS나 실험적 원자 정확도의 증거로 승격하지 않는 처리가 적절하다. 검토자는 해당 CGI 실패를 새로 재현하지 않았으며 owner가 보존한 실패·취득 기록을 읽었다.

packet 이후 정리된 원천 감사 문서도 읽었다. 이것은 기존 자료의 위치·접근 실패·남은 차이를 정리한 기록이며, 새 원자 입력이나 새 물리 검증으로 취급하지 않았다.

## 5. 실행 증거, 실패 보존 및 검증 독립성

과학 실행의 actual exit는 실행 owner가 관측하여 보존한 receipt다. 검토자는 receipt와 raw output을 확인했으며 기존 suite를 스스로 재실행했다고 주장하지 않는다.

| 항목 | R001 | R002 |
|---|---:|---:|
| 비교한 저/고에너지 격자 | 200/400 → 400/800 | 800/1600 → 1600/3200 |
| 실행 check | 12/13 PASS | 13/13 PASS |
| process exit | 1 | 0 |
| 누적 저에너지 진입 에너지 변화 | 5.126664% | 1.392781% |
| 누적 저에너지 진입 전자수 변화 | 4.315482% | 1.152949% |
| 판정 | FAIL | PASS_SCOPED |

에너지 기준 2%, 경계 전자수 기준 3%를 유지했다. R001과 R002의 source identities는 동일하다. R001 실패를 버리지 않고 사전 계획에 있던 격자 배증으로만 보정했다. 수치 허용값이나 원자 입력을 바꿔 성공으로 만든 흔적은 없다.

R002 raw stdout의 각 check JSON을 수치 결과 JSON과 대조해 일치함을 확인했다. 마지막 PASS_SCOPED marker가 있고 stderr는 비어 있다. actual exit receipt는 session 78368, final chunk `66e5a6`, exit 0을 기록한다.

증거별 의미는 구별해야 한다.

- 단일 분기 ramp의 독립 closed-form toy는 분기·시간 계수의 기본 검증이다. 생산 generator 전체의 물리 인증은 아니다.
- 독립 DOP853 비교는 **활성 240개 격자**에서 같은 \(G\)를 사용하여 시간 전파 알고리즘을 비교한다. 정규화 오차 약 \(2.64\times10^{-12}\)가 보고되어 기준을 통과한다. 최종 4,800개 전체를 독립 코드로 재현한 증거는 아니다.
- 부모의 저에너지 연속 해와의 비교는 선택된 저에너지 Coulomb 극한을 검증한다. 고에너지 원자 자료의 정확도를 검증하지 않는다.
- 마지막 격자 배증에서 순간 heat 변화 약 0.04890%, 누적 heat 변화 약 0.05529% 및 위 누적 경계 기준이 통과한다. 이는 관측된 격자 차이다. 엄밀한 연속극한 오차 상계는 아니다.
- 1.3928%/1.1529%는 **누적** 진입량에 대한 값이다. 순간 진입률, 모든 에너지의 pointwise spectrum, 저에너지 heat partition에 별도의 정확도 상계를 부여하지 않는다.
- quadrature 및 방정식 적분은 주어진 공유 모형 안의 계산 안정성을 확인한다. He 원천 차이를 소거하지 않는다.

검토자가 추가로 수행한 read-only 검사는 보존된 NPZ 배열에 대한 직접 장부 산술이다. 저장 배열은 21개 시간, 4,811개 전체 상태, 두 birth tag이며 활성 노드는 4,800개다. 독립적으로 구성한 에너지·전자수 functional을 적용한 최대 상대 잔차는 각각 \(2.70\times10^{-14}\), \(2.70\times10^{-14}\)다. 저장 상태의 최솟값은 0이고, 저에너지 출생 tag가 10 eV 위로 올라간 값도 0이다. 이는 저장 결과와 장부의 일관성을 추가 확인한다. 과학 suite 재실행은 아니다.

### 추가 환경 근거: 명시적 1-thread 재현

최종 검토 도중 프로젝트 HPC 정책의 BLAS/NumExpr 기본 1-thread 규칙과 R002 실행 당시 thread 수 미기록 사이의 공백이 확인되었다. 정책 원문 고정 사본을 직접 읽었다. 현재 fresh process에서 관측한 설정을 과거 R002에 소급하지 않는다. **원 R002의 실제 thread 수는 NOT_RECORDED로 남긴다.**

별도 사전 계약은 5개 thread-control 환경변수를 1로 고정하고 동일한 4,800개 활성 격자의 최종 시점만 한 번 재전파하도록 범위를 한정했다. 첫 시도는 메모리 admission에서 exit 1로 끝났으며 수송을 시작하지 않았다. 실패 코드·로그·receipt가 `ATTEMPT01`에 보존되어 있다.

owner는 관측한 inactive file cache만 reclaimable로 계산하고 active cache와 원래의 1 GiB reserve를 유지했다. 한 generator의 9,080,055 nonzero에 근거한 2 GiB incremental estimate를 기록했다. 실패 당시 코드와 최종 코드의 diff를 직접 읽었으며 바뀐 부분은 이 자원 산정뿐이다. 물리식, FP64, 원 13개 과학 기준 및 별도 비교 기준 \(10^{-11}\)은 바뀌지 않았다. 다른 process 종료나 cache 삭제는 보고되지 않았다.

승인된 환경에서의 실제 focused 실행은 **76.9667초, exit 0**이다. 두 loaded OpenBLAS pool의 `num_threads=1`, `/proc/self/status`의 `Threads=1`을 기록했고 peak RSS인 VmHWM은 1,143,116 kB다. 새 결과와 기존 R002 최종 observable의 비교 상대차는 모두 0이다. 보존된 21시점 NPZ의 마지막 state와 비교한 정규화 \(L^\infty\) 차는 두 tag에서 각각 \(3.39868\times10^{-15}\), \(1.00656\times10^{-16}\)이다. 검토자도 두 저장 배열과 source를 읽어 같은 비교값, 동일한 grid 및 동일한 source를 확인했다.

추가 manifest 14개 파일의 SHA256·길이가 모두 일치하고 raw stdout은 결과 JSON과 일치하며 stderr는 비어 있다. 실제 receipt는 session 82000, final chunk `36669a`, exit 0을 기록한다. 원 27개 과학 packet은 그대로다. 추가 manifest SHA256은 `d42aa86b79cbfa0138d3a89bfcc48a47f9397388322c88179aedb23962089989`다.

이 근거는 명시적 1-thread 환경에서의 국소 재현과 정책 준수를 뒷받침한다. 기존 13개 suite를 다시 수행한 것은 아니며, 과거 실행의 thread provenance 복구, NCP64 scaling 또는 속도 개선의 증거로 사용하지 않는다. 이 환경 보완을 확인했으므로 해당 공백을 이유로 조건부 과학 판정을 보류할 필요는 없다.

## 6. 핵심 결과의 허용된 해석

아래 숫자의 분모는 선택된 0.1–900 eV 직접 전자 주입이다. 이 구간이 포함하는 에너지는 현재 활성 1–4 MeV 양성자의 전체 직접 방출 전자 운동에너지 중 **73.55293%**다. 소스 바깥의 tail을 포함한 전체 cosmic-ray 에너지 수지와 혼동해서는 안 된다.

| \(t=10^{10}\,\mathrm s\)의 조건부 결과 | 값 |
|---|---:|
| 선택된 누적 전자 주입 에너지 | \(9.00631\times10^{-33}\ \mathrm{J\,m^{-3}}\) |
| 활성 전자 에너지 | \(8.85276\times10^{-33}\ \mathrm{J\,m^{-3}}\) |
| 활성 전자에 남은 주입 에너지 비율 | 98.29509% |
| 누적 bath stopping heat | \(1.19160\times10^{-34}\ \mathrm{J\,m^{-3}}\) |
| 누적 heat의 주입 에너지 비율 | 1.32307% |
| 현재 stopping-heat power | \(3.440995\times10^{-44}\ \mathrm{J\,m^{-3}\,s^{-1}}\) |
| 같은 모형 terminal-yield immediate proxy | \(1.008826\times10^{-42}\ \mathrm{J\,m^{-3}\,s^{-1}}\) |
| 현재 heat / 위 immediate proxy | 3.41089% |

이 비율은 해당 시점에 대부분의 선택 주입 에너지가 아직 활성 전자에 저장되어 있음을 보여준다. 비교 기준은 같은 frozen operator의 terminal yield를 현재 주입에 즉시 적용한 값이다. 실제 FS10 원본 수치나 전체 IGM history의 즉시 가열 오차를 측정한 결과로 해석할 수 없다.

birth energy와 heat를 발생시킨 순간의 energy를 분리한 점이 중요하다.

- 직접 저에너지 출생 전자의 heat power: \(2.413636\times10^{-44}\ \mathrm{J\,m^{-3}\,s^{-1}}\).
- 고에너지 출생 전자의 **모든 에너지에서의** heat power: \(1.027359\times10^{-44}\). 위 기준 대비 **42.5648%**다.
- 그 고에너지 출생 전자가 **\(E\le10\,\mathrm{eV}\)에서** 발생시킨 heat power: \(5.687740\times10^{-46}\). 같은 기준 대비 **2.3565%**다.

따라서 “고에너지 cascade가 저에너지 heat를 42.56% 늘렸다”는 해석은 허용하지 않는다. 42.56%는 고에너지 구간에서 이미 발생한 heat도 포함한다. 저에너지에서 발생한 추가량을 묻는 경우 이 진단의 해당 값은 2.36%다. 두 비율을 원시 결과에서 다시 계산하여 확인했다.

진단 코드는 저장 trajectory와 같은 \(G\)로 occupation integral을 계산하고 heat row를 에너지 구간에 따라 분할한다. 진단의 7개 내부 consistency check와 exit 0을 확인했다. 생성 그림의 energy budget·시간 비교·분할 표시도 결과와 일치한다. 이 진단은 4,800개 유한 모형에 대한 후처리다. 별도의 격자 연구나 독립 원자 모형 검증으로 세지 않는다.

## 7. Coulomb 처방 및 미포함 물리

고전·양자 로그의 작은 값을 쓰는 처방은 명시된 leading-log 모형이다. Krommes의 고전·양자 논의 및 식 5·14를 읽어 matching prescription과 양자 \(-1/2\) 항의 의미를 확인했다. 그것을 이 bath와 모든 에너지에서의 정확한 충돌식으로 간주할 수는 없다. [Krommes 2018](https://arxiv.org/html/1806.04990v1)

\(-1/2\) 항을 더한 사전 지정 비교에서 얻은 heat 변화 약 −0.1184%는 한 처방에 대한 민감도다. 이 숫자는 원자 불일치, thermal diffusion, cut 처리 및 source history를 합친 물리 오차막대가 아니다. 특히 낮은 에너지의 처방 및 고전/양자 전이에는 해당 근사의 가정이 그대로 남아 있다.

이번 결과는 다음을 포함하지 않는다.

- 직접 source의 0.1 eV 아래 및 900 eV 위 부분.
- HeII 충돌, \(n\ge5\) 여기 및 원자 resonance·continuum의 완전성.
- 중성 원자 탄성 recoil, thermal diffusion, cutoff 뒤의 열평형 도달.
- 광자 방출 분기·전달·재흡수와 gas/ionization feedback.
- source의 시간·redshift 근사 인증 및 전체 IGM history.

그 결과를 추가 자료 없이 추정해 채우지 않은 것은 적절하다. 위 제한을 유지한 상태에서 causal storage와 반복 분기 효과를 계산한 점이 PHYS02A 대비 이번 연구 단위의 실질적인 진전이다.

## 8. 최종 gate 평가

증거는 고정 코드·입력·원시 출력·실패 기록·실제 종료 상태와 연결된다. 유한 모형의 수학적 정의와 보존 장부는 타당하며, 실행 가능한 범위에서 검증이 완료되었다. 전파·toy·부모 극한·격자 검사는 서로 다른 측면을 검증하고 각 독립성의 한계를 공개한다. 첫 실패에 따른 격자 수정도 과학 기준을 유지했다. 지역 계산의 실제 시간과 산출물이 tractability를 뒷받침하지만 더 큰 시스템의 scaling은 주장하지 않는다.

새로 얻은 것은 이 조건부 모형 안에서의 고에너지 반복 분기, 인과적 저장 및 낮은 에너지 구간으로의 유입이다. 문헌 최초성이나 원 FS10의 재현을 주장할 근거는 없다. 원래의 finite-time delay 질문은 유지되었고 전체 고에너지 출생 heat와 낮은 에너지에서의 deposition도 구분되었다.

**이 고정 후보의 조건부 연구 산출물은 PROMOTE_SCOPED다.** 물리 정확도·원자 일관성·전체 이력과 관련된 gate는 위에 기재한 상태로 남는다. 새 설계 대안이나 과학 suite의 추가 반복을 이 판정의 전제 조건으로 요구하지 않는다. 기계 판독 판정과 모든 고정 파일 hash는 `review/FINAL_DECISION.json`에 함께 보존한다.

