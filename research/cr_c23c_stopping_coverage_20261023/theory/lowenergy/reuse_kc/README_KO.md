# BASS_CR — 실제 kernel과 온도 의존 cutoff

**CR-THEORY-KERNEL-CUTOFF-20261013 · PROMOTE_SCOPED / PASS**

저장된 실제 전자 에너지 격자와 HI·HeI kernel을 양의 보존 사건에 연결하고, \(E_c(T)=\chi k_BT\)의 유한 thermal/active 분할과 implicit EOS를 구성한 연구 단위다. 독립 검토의 정확한 수락 범위는 [DECISION.json](review/DECISION.json), 가정은 [CONTRACT.json](CONTRACT.json), claim별 근거는 [CLAIMS.json](CLAIMS.json)에 있다.

## 결과와 읽는 순서

| Claim | 완료한 범위 |
|---|---|
| KC1 | 실제 저장 격자의 양의 daughter/event 표현, nuclei·charge·energy 보존 및 명시한 fixed-bath generator 대응 |
| KC2 | 실제 neutral composition과 thermal-bath stopping 계수의 양성·미분 한계 |
| KC3 | 고정 common inventory의 signed 유한 분할, \(C_{\rm eff}>0\) bracket에서 양의 유일근과 온도 certificate |
| KC4 | retained atoms의 branch 열거와 \(\chi\ge3/2\)의 유한 가열·냉각 continuation |
| KC5 | 공변 moving-boundary 수 전류와 rest-mass를 뺀 운동에너지 source의 상쇄 |
| KC6 | 고정 reconstruction basis 또는 고정 atomic prefix에서 coupled feedback gain·inner/outer residual 한계 |
| KC7 | 실제 에너지 사건 17개와 정확한 box/prefix 사례를 연결한 scoped reference 구현 |

[전체 PDF](latex/report.pdf)와 [보고서 Markdown](REPORT_KO.md)을 먼저 읽고, 상세 유도는 [derivations](derivations/)에서 확인한다. 실제 결과는 [RESULTS.json](RESULTS.json), 재개 위치는 [HANDOFF.json](HANDOFF.json)과 [NEXT_DAG.json](NEXT_DAG.json)에 있다. 다음 이론 과제는 실제 반응이 원자 inventory를 바꿀 때의 coupled branch solver와 Bianchi redshift 뒤의 에너지/kernel 재결속이다.

수·에너지 상태는 comoving cell 값이다. Thermal \(N=N_{\rm nuc}+N_{e,\rm th}\), common \(\mathscr C=N_{\rm nuc}+N_{e,\rm all}\), bath density \(n_e=N_{e,\rm th}/V\)를 구별한다. Base reservoir는 retained lower atoms의 모멘트를 뺀 \(N_B,U_B\)다. 연속 사례의 오차는 \(\tau=T/T_*\)에 대한 값이며 물리 온도 한계에는 \(T_*\)를 곱한다. 실제 source/scenario와 consumer observable budget, 기존 physical gate는 해당 원래 의존성에 남아 있다.

## 문서 재빌드

이하 명령은 **이 연구 단위의 복사본을 작업 디렉터리로** 두고 사용한다. 문서 재빌드에는 Python의 NumPy·Matplotlib, Pandoc, XeLaTeX가 필요하다.

~~~bash
python3 build_report.py
~~~

이 entry point는 추가 CLI 옵션이 없다. 보고서·세 유도 문서·선별 문헌 노트·이미 기록된 결과를 읽고 그림, CSV, LaTeX 본문과 PDF를 만든다. 새 ODE 적분이나 과학 검사를 호출하지 않는다. 생성되는 figures/ 및 latex/ 파일은 복사본에서 갱신된다.

이미 제공된 LaTeX만 다시 컴파일하려면 latex/ 디렉터리에서 다음을 실행한다.

~~~bash
xelatex -interaction=nonstopmode -halt-on-error report.tex
xelatex -interaction=nonstopmode -halt-on-error report.tex
~~~

빌드 원본은 [build_report.py](build_report.py), 기존 컴파일 로그는 latex/compile_1.* 및 latex/compile_2.*다. 문서 환경이 달라질 때 생성 PDF의 bytes까지 같다고 전제하지 않는다.

## 기록된 과학 검사의 재현

아래 세 Python entry point에는 argparse 옵션이 없다. 코드나 실행 환경의 변경으로 재확인이 필요한 경우에만 **복사본에서** 해당 검사를 실행한다. 각 명령은 결과 JSON을 새로 쓰므로 동결된 원 작업본의 기존 결과에 덮어쓰지 않는다.

~~~bash
python3 checks/check_kernel_adapter.py
python3 checks/check_sharing_capacity.py
python3 checks/run_thermal_cutoff_checks.py
~~~

앞의 두 검사는 NumPy·SciPy와 inputs/kernel_sources/의 원 입력을 사용한다. Cutoff 검사는 Python 표준 라이브러리의 정확한 Fraction 연산을 사용한다. Kernel 검사는 results/KERNEL_ADAPTER_CHECKS.json과 examples/ACTUAL_KERNEL_EVENT_COLUMNS.json, 나머지는 각각 results/SHARING_CAPACITY_CHECKS.json과 results/THERMAL_CUTOFF_CHECKS.json을 기록한다. 라이브러리 모듈 kernel_event_adapter.py와 thermal_cutoff_solver.py 자체에는 별도 사용자 CLI를 부여하지 않았다. 실제 실행 환경과 source identity는 해당 결과 및 results/KERNEL_ADAPTER_EXECUTION.json을 따른다.

Wolfram 결과를 별도로 재현할 때는 이 단위를 작업 디렉터리로 둔 새 Wolfram Language 세션에서 다음 저장 코드를 평가한다.

~~~wolfram
Get["checks/wolfram_scalar_checks.wl"]
Get["checks/wolfram_xact_cutoff_checks.wl"]
~~~

xAct 스크립트는 공식 xCore·xPerm·xTensor 원본을 다운로드하여 고정 SHA256을 확인한 뒤 읽는다. 따라서 Wolfram 실행 환경과 해당 네트워크 접근이 필요하며, package hash 불일치를 기존 성공 결과로 대체하지 않는다. 원래 실행 결과는 results/WOLFRAM_SCALAR_RAW.json과 results/WOLFRAM_XACT_RAW.json에 보존되어 있다. 이 README와 외부 문헌 index를 작성하는 과정에서는 과학 검사를 재실행하지 않았다. 최종 보고서의 실제 컴파일과 시각 검수는 results/PDF_QA.json에 기록했다.

## 원 입력, 폰트와 외부 문헌

| 자료 | 위치와 배포 의미 |
|---|---|
| 실제 kernel 원 입력 11개 | inputs/kernel_sources/의 원래 상대경로를 유지한다. [KERNEL_SOURCE_BINDING.json](inputs/KERNEL_SOURCE_BINDING.json)에 원 commit·blob·SHA256과 저장된 9600-node 배열의 identity가 있다. 격자나 generator를 다시 만들어 대체하지 않는다. |
| 이전 채택 근거 | inputs/prior/와 [PRIOR_REUSE.json](inputs/PRIOR_REUSE.json)에 결속되어 있다. 새 결과와 이전 성공을 구별한다. |
| 보고서 폰트 | ZIP에는 Noto Sans CJK KR regular/bold와 DejaVu Sans Mono의 세 원 font 파일을 넣는다. Git에는 font README와 license를 남기고 font 바이너리는 제외한다. Git만 사용할 때는 같은 이름의 시스템 폰트를 설치한다. 자세한 파일 identity는 [font README](latex/fonts/README.md)에 있다. |
| 폰트 license | [Noto OFL](licenses/Noto-OFL.txt) 및 [DejaVu license](licenses/DejaVu-LICENSE.txt)를 함께 제공한다. 원 코드·데이터의 권리와 기존 출처 조건도 그대로 유지한다. |
| 선별 외부 문헌 | [SOURCES.json](SOURCES.json)과 [LITERATURE_KO.md](LITERATURE_KO.md)에 서지·원문 URL·실제로 비교한 범위를 기록한다. |
| 외부 원문 retrieval cache 11개 | inputs/literature/의 원 응답은 ZIP/Git에서 제외하고 로컬 동결본에 보존한다. [EXTERNAL_REFERENCE_INDEX.json](EXTERNAL_REFERENCE_INDEX.json)에 경로·size·SHA256·검색 질문·source URL/DOI를 제공한다. |

외부 retrieval 응답에는 논문 본문·긴 발췌와 서비스 응답이 섞여 있으므로 배포형에는 그 원문을 재수록하지 않는다. 문서 재빌드와 세 과학 검사는 이 cache를 읽지 않는다. 원문을 새로 취득한 응답은 시점·서비스 표현에 따라 bytes가 달라질 수 있으므로 기존 cache의 SHA256으로 표시하지 않는다.

## 동결 manifest와 배포 snapshot

[review/CANDIDATE_MANIFEST.json](review/CANDIDATE_MANIFEST.json)은 독립 검토한 **72개 파일의 원래 identity**를 유지한다. Source ZIP에는 이 중 **61개 동결 파일을 포함**하고, 외부 retrieval 응답 **11개는 index만 포함**한다. 외부 응답을 배포에서 제외해도 원 manifest의 해당 항목과 로컬 원 bytes를 삭제하거나 변경하지 않는다. 이 README와 외부 index는 검토 이후의 배포 보충 문서다.

SOURCE_MANIFEST.json은 **아카이브를 만든 시점의 파일 snapshot**과 61개 포함/11개 외부 index의 대응을 기록한다. 이후 Dropbox·Google Drive 등의 실제 delivery receipt는 최종 HANDOFF/Git metadata와 DELIVERY.json에 별도로 결속된다. 후속 receipt가 추가되어도 이미 만든 ZIP과 그 source manifest의 bytes를 변경하지 않는다.

[package_source.py](package_source.py)의 실제 argparse는 두 필수 옵션을 받는다.

~~~bash
python3 package_source.py \
  --science-commit "$BASS_CR_SCIENCE_COMMIT" \
  --archive-path "$BASS_CR_ARCHIVE_PATH"
~~~

두 변수에는 실제 40자리 소문자 science commit과 source 디렉터리 밖의 새 ZIP 절대경로를 지정한다. 기존 ZIP을 덮어쓰는 경로는 허용하지 않는다. 이 포장 명령은 로컬 원응답 11개를 보유한 작업본에서 사용하며, 외부 index·post-review binding·PDF QA·publication 기록도 필요하다. 원응답을 제외한 배포 ZIP에서 문서나 계산을 재현하는 작업과 원 작업본의 배포 snapshot을 다시 포장하는 작업을 구별한다.

