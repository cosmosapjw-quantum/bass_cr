# BASS_CR: 시간 변화 배경에서의 전자 열화와 열적 진화

**CR-THEORY-THERMAL-EVOLUTION-20261012를 완료했다.** 독립 최종 판정은 **PROMOTE_SCOPED**이며, TH1–TH7을 명시된 조건 아래 완결된 이론 결과로 채택했다. 고정 배경의 실제 source 결속과 A2 cutoff 편입에서 출발해, 이동 경계·모든 자유전자의 회계·충돌 시계·계수 변화에 따른 온도 오차까지 연결했다.

주요 산출물은 **32쪽 PDF**, 전체 유도 원문, 네 함수의 receiver 코드, 판별 검산, 독립 검토와 다음 연구 DAG다.

## 먼저 읽을 파일

| 파일 | 내용 |
|---|---|
| [latex/report.pdf](latex/report.pdf) | 전체 보고서 32쪽: 결과 설명, 세 분과의 증명, 검산과 출처 |
| [REPORT_KO.md](REPORT_KO.md) | 연구 결과와 의미를 정리한 본문 |
| [review/DECISION.json](review/DECISION.json), [review/REVIEW_KO.md](review/REVIEW_KO.md) | TH1–TH7의 최종 채택 범위와 독립 검토 |
| [derivations/MOVING_CUTOFF_KO.md](derivations/MOVING_CUTOFF_KO.md) | 움직이는 cutoff의 수·에너지·momentum 보존 |
| [derivations/THERMAL_EXCESS_KO.md](derivations/THERMAL_EXCESS_KO.md) | Thermal–all-free 동치, 편입 EOS, 팽창 후 온도 오차 |
| [derivations/COLLISION_CLOCK_KO.md](derivations/COLLISION_CLOCK_KO.md) | 충돌 시계, 실제 Coulomb 계수 분리, Duhamel 상계 |
| [receiver_interface.py](receiver_interface.py) | 열적 전달률·총 모멘트·유한 packet·온도 오차 API |
| [PLAN_KO.md](PLAN_KO.md), [NEXT_DAG.json](NEXT_DAG.json), [HANDOFF.json](HANDOFF.json) | 다음 이론 구성과 재개 입력 |

## 주가정과 완결한 결과

배경은 주어진 homogeneous Bianchi I의 comoving geodesic cell이다. Metric signature는 \((-+++)\), 시간과 밀도는 proper-time·proper-volume 기준이다. Momentum 반전 대칭으로 평균 momentum은 0이며, active 전자의 비등방 stress와 \(K:\Pi_A\) 일은 유지한다. Thermal nuclei와 thermal electrons는 공통 온도의 비상대론적 단원자 이상기체로 두고 양의 thermal particle count를 사용한다. 각 사건의 실제 수·kinetic energy·원자 내부에너지·열 이관을 한 번씩 센다. 세부 조건은 [CONTRACT.json](CONTRACT.json)과 각 정리에 모았다.

| 채택 결과 | 구성한 연결 |
|---|---|
| TH1 이동 cutoff | 상대 경계속도 \(\dot E_c-\dot W\)의 signed number flux, 연속 경계의 \(E_cJ_N\), 실제 subcutoff daughter energy, active·하부 모멘트의 상쇄 |
| TH2 all-free 동치 | \(u_{\rm ex}=u_A-(3/2)k_BTn_A\)와 대응 stress를 사용해 전체 자유전자 회계와 thermal 온도식을 정확히 연결 |
| TH3 정확한 충돌 시계 | 고정 finite operator의 공통 양의 계수에 대해 \(X=Vx,\ \tau=\int a\,dt\), source \(Vs/a\), 물리 출력의 변환 |
| TH4 Coulomb 밀도 분리 | 고정 격자·조성에서 실제 source 코드의 \(G(d)=dG(1)-(d\log d/2)C_0\) 분해 |
| TH5 비가환 residual 상계 | 양의 에너지 가중치와 complete energy ledgers를 사용해 state·누적 heat 오차를 동시에 제어 |
| TH6 scalar clock 선택 | 명시한 coefficient residual 상계를 최소화하는 허용 구간 내 weighted median |
| TH7 온도 certificate | 같은 팽창 이력에서 cumulative thermal deposition → thermal endpoint energy/count → temperature 오차를 연결 |

TH1의 정확한 kinetic 분할과 하부를 thermal 기체로 편입하는 closure는 각각 조건을 명시했다. TH3–TH6은 채택한 finite generator·계수 정의역에서 성립하며, TH7은 같은 완전한 thermal deposition과 양의 particle-count 하한을 사용한다.

## 실제 검산과 독립 검토

**Root의 판별 검산 15/15**, **유도 작성자의 Wolfram 정확 기호 검산 21/21**이 통과했다. 독립 검토자는 원문·소스·실행 결과를 읽고 별도의 해석 논증으로 검토했으며, 검토자 자신의 scientific execution은 0회다.

- [results/THEORY_CHECKS.json](results/THEORY_CHECKS.json): 정확한 유리수 예제, 기존 두 함수의 30개 stopping coefficient, 하나의 8-state 무차원 비가환 IVP. Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0에서 0.0168초.
- [results/CLOCK_SYMBOLIC_CHECKS.json](results/CLOCK_SYMBOLIC_CHECKS.json): 두 단계 해석 예제의 충돌 시계·source Jacobian·물리 heat 출력·에너지 회계·비가환 항·residual 적분을 한 번의 성공한 Wolfram 평가로 확인.
- [review/DECISION.json](review/DECISION.json): Heaviside 미분, 정확한 역대입, 양의 전파자와 Duhamel 논증, scalar subgradient, Stieltjes 부분적분, EOS 차분 항등식에 의한 독립 검토.

새 full generator build, 실제 PHYS02 transport, 과거 full suite 반복과 NCP 과학 작업은 모두 0회다. Frozen candidate와 최종 문서의 연결은 [review/POST_REVIEW_BINDING.json](review/POST_REVIEW_BINDING.json)에 보존했다.

## R1–R10 완료 근거

| 단계 | 완료 근거 |
|---|---|
| R1 연구 위치·계약 | CONTRACT의 질문·가정·수용 기준과 독립 이론 요청 |
| R2 근거 재사용 | inputs/RECOVERY.json, inputs/prior, 원 cascade·coherent BED 코드 |
| R3 주장·전제 | CONTRACT, CLAIMS, 세 유도문의 정의역과 조건 |
| R4 표현 탐색 | 이동 경계, active 기준에너지, comoving collision clock의 직접 구성 |
| R5 실제 유도 | 세 유도문에 완성한 모멘트·동치·변환·오차 정리 |
| R6 독립 검증 | review의 분과별 논증과 최종 DECISION |
| R7 판별 검산 | Root 15개와 작성자 Wolfram 21개의 실제 결과 |
| R8 결과 판정 | PROMOTE_SCOPED, TH1–TH7 조건부 정리 채택 |
| R9 원고·코드 연결 | receiver_interface.py, 전체 LaTeX 원고와 32쪽 PDF |
| R10 재개점 보존 | NEXT_DAG, PLAN, HANDOFF와 원문·실행·검토 identity |

## 코드 재현

이 문서가 있는 디렉터리에서, 이번 판별 검산을 재현할 때 아래 명령을 사용한다. Python 의존성은 NumPy와 SciPy다. Receiver 네 함수 자체는 Python 표준 라이브러리만 사용하며, rational 입력과 rational \(k_B\)를 주면 Fraction 연산을 유지한다.

~~~bash
python3 checks/run_theory_checks.py
~~~

Wolfram Engine을 사용할 수 있는 환경에서는 기호 예제를 다음처럼 평가할 수 있다.

~~~bash
wolframscript -code 'Print[Get["checks/verify_analytic_case.wl"]]'
~~~

유한 step의 receiver에는 실제 적분한 comoving particle increment와 thermal energy increment를 입력한다. Thermal energy increment에는 팽창 pressure work와 선택한 다른 source·cooling 항이 포함된다. 물리 source의 단위·중복 계상 조건은 각 함수 docstring에 적었다.

## LaTeX와 PDF 재현

전체 재생성에는 Python의 NumPy·SciPy·Matplotlib, Pandoc, XeLaTeX와 원고에서 사용하는 LaTeX 패키지가 필요하다.

~~~bash
python3 build_report.py
~~~

이 명령은 저장된 TOY_EVOLUTION.csv에서 그림을 만들고, 검토된 본문과 세 유도문을 합쳐 LaTeX를 생성한 뒤 XeLaTeX를 두 번 실행한다. 이미 생성된 LaTeX만 다시 컴파일하려면 다음을 사용한다.

~~~bash
cd latex
xelatex -interaction=nonstopmode -halt-on-error report.tex
xelatex -interaction=nonstopmode -halt-on-error report.tex
~~~

전체 source ZIP에는 Noto Sans CJK KR의 Regular·Bold OTF와 DejaVu Sans Mono TTF 원본, [licenses](licenses)의 라이선스를 포함한다. Git 경로에서는 글꼴 파일을 제외한다. build_report.py와 생성된 report.tex는 로컬 OTF가 있으면 포함 글꼴을, 없으면 Linux 시스템의 **Noto Sans CJK KR**와 **DejaVu Sans Mono**를 사용하도록 구성했다.

## 다음에 바로 시작할 이론

다음 노드는 **CR_THEORY_SELF_CONSISTENT_FEEDBACK**이다. Prescribed evolving background에서
\(G(T,\mathrm{H/He\ composition},n)=\sum_k r_kD_k\) 형태의 고정 event 행렬과 변화하는 반응계수를 사용해, **T·H/He 조성 피드백을 포함하는 양수성·보존성 한 step**을 구성한다.

첫 작업은 active state, H/He populations, thermal count·energy가 동일 사건 increment를 공유하도록 정하고, 계수를 고정한 step과 EOS 갱신을 연결하는 것이다. 이어서 계수·EOS 피드백을 닫는 국소 조건을 증명하고, 이번 coefficient residual과 temperature certificate를 step 선택 기준으로 사용한다.

실제 astrophysical scenario의 source·초기조건·관측량 결속은 기존 application node들에서 이어간다. 일반 이론의 위 구성은 명시한 가정에서 직접 진행한다. 이전 local node 22개와 global node 19개의 상태를 보존했으며, 현재 local DAG는 30개 노드·53개 간선이다.
