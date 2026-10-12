# BASS_CR source binding — 전달물과 재현 안내

이 번들은 **저장된 입력에서 scalar source-binding 결과와 독립 기준 계산, 그림, 한국어 보고서를 재현하는 단위**다. [최종 독립 판정](review/DECISION.json)은 PROMOTE_SCOPED이며, 읽기용 문서는 [REPORT_KO.md](REPORT_KO.md)와 [9쪽 PDF](latex/report.pdf)다. 범위와 남은 물리 조건은 [HANDOFF.json](HANDOFF.json), [CLAIM_LEDGER.json](CLAIM_LEDGER.json)에 있다.

## 포함 범위

현재 단위의 Python 원문, 입력 JSON, 회수한 source text와 identity, 결과, 첫 실패·수정 기록, 독립 review, 계획/DAG, LaTeX·매크로·그림·PDF, 아래 폰트 원 바이트와 라이선스를 함께 보존한다. 캐시, TeX 보조 파일, QA용 페이지 이미지는 재현 입력이 아니므로 ZIP에서 제외할 수 있다.

과거 sibling 연구 단위나 GitHub commit으로 향하는 DAG·source-inventory 경로는 **고정된 과거 근거 참조**다. 이 ZIP은 전체 과거 저장소, H/generator payload, transport binary·operator bank의 복원본이 아니다. inputs/source_lineage와 review/sources의 옛 launcher·계산 소스는 출처 조사용 원문이다. 현재 재현 entrypoint는 아래 네 Python 파일과 latex/report.tex이며, 옛 launcher나 old suite를 실행할 필요가 없다.

## 재현 환경

정적 점검에서 확인한 실제 환경은 Python **3.12.14**, NumPy **2.3.5**, Matplotlib **3.10.8**, XeTeX **0.999995 / TeX Live 2023 (Debian)**이다.

- evaluate_source_binding.py와 review/reference_source_binding.py는 Python 표준 라이브러리만 사용한다.
- build_report_values.py도 표준 라이브러리만 사용하며, 저장 결과와 review/DECISION.json에서 TeX 매크로를 만든다.
- render_results.py는 NumPy·Matplotlib을 사용한다. Agg backend이므로 GUI가 필요 없고, 그림의 DejaVu Sans는 Matplotlib에 포함된 폰트를 사용한다.
- PDF 재조판에는 XeLaTeX와 geometry, fontspec, amsmath, amssymb, mathtools, graphicx, booktabs, longtable, array, xcolor, enumitem, fancyhdr, titlesec, hyperref가 필요하다. Computer Modern 수학 폰트는 TeX 배포 환경에서 제공한다.

Python 3.12 작업 환경에서 그림 의존성은 다음과 같이 맞출 수 있다.

~~~bash
python -m pip install "numpy==2.3.5" "matplotlib==3.10.8"
~~~

## 정확한 재현 명령

ZIP 원본은 보존하고 새로 푼 작업 사본의 cr_source_binding_20261012 디렉터리에서 실행한다. 배포 준비 점검에서는 아래 과학·검증 계산을 다시 실행하지 않았다.

**1. Scalar 결과를 별도 파일로 재생성**

~~~bash
python evaluate_source_binding.py --inputs inputs --output reproduced/SOURCE_BOUND_RESPONSE.json
cmp results/SOURCE_BOUND_RESPONSE.json reproduced/SOURCE_BOUND_RESPONSE.json
~~~

이 entrypoint의 직접 입력은 inputs/CACHED_RESPONSE.json, PULSE_RECORD.json, PAIRED_RECORD.json, SOURCE_COVERAGE_RECORD.json 네 파일이다. 기존 저장 기록에 대한 37개 산술·정규화 검사를 포함하며, transport·pulse·generator를 호출하지 않는다.

**2. 독립 기준 계산을 재생성하는 경우**

~~~bash
python review/reference_source_binding.py
~~~

이 명령은 작업 사본의 review/REFERENCE_RESULT.json을 다시 쓴다. 직접 입력은 review/ATOMIC_FIXTURE.json, CONTRACT.json, inputs의 pulse·paired·source-coverage 기록, results/SOURCE_BOUND_RESPONSE.json이다. 기존 독립 실행과 판정의 원 영수증은 ZIP 안에 보존돼 있으며 새 실행이 그 과거 identity를 대체하지 않는다.

**3. 저장 결과에서 그림과 보고서를 재생성**

~~~bash
python render_results.py
python build_report_values.py
cd latex
xelatex -interaction=nonstopmode -halt-on-error report.tex
xelatex -interaction=nonstopmode -halt-on-error report.tex
~~~

출력은 results/SOURCE_BINDING_SUMMARY.pdf 및 PNG, latex/result_macros.tex, latex/review_status.tex, latex/report.pdf다. 그림·매크로는 저장 결과를 읽으며 원 science JSON을 바꾸지 않는다. 이미 포함된 그림과 매크로를 쓰면 XeLaTeX 두 명령만으로 PDF를 재조판할 수 있다. 이 LaTeX는 XeTeX의 한국어 줄바꿈 명령을 사용하므로 pdflatex로 대체하지 않는다. 재생성 PDF의 생성 시각·TeX 환경 등에 따라 파일 SHA256은 달라질 수 있으므로 원 PDF의 byte identity와 재조판 결과를 구분한다.

## 폰트와 라이선스

latex/report.tex는 세 폰트를 모두 fonts/ 아래 파일명으로 참조한다. 세 폰트는 다음 경로에 **실제 파일 내용**으로 준비했으며, 전달 ZIP에도 이 바이트를 포함한다.

| ZIP 상대경로 | 크기 | 라이선스 |
| --- | ---: | --- |
| latex/fonts/NotoSansCJKkr-Regular.otf | 16,433,112 B | latex/fonts/OFL.txt |
| latex/fonts/NotoSansCJKkr-Bold.otf | 16,997,996 B | latex/fonts/OFL.txt |
| latex/fonts/DejaVuSansMono.ttf | 343,140 B | latex/fonts/DejaVu-LICENSE.txt |

폰트의 원 바이트 SHA256은 다음과 같다.

~~~text
NotoSansCJKkr-Regular.otf  6bcb2a0703aa137e874fc2dffa85f6c21ba9a67fa329e81b8c801663af7e992a
NotoSansCJKkr-Bold.otf     26d0c6748500a0444844280b308f5b62c7ae92ac6c6ac88148e502dd211eb52a
DejaVuSansMono.ttf        c805f9436dbc268644c1d9584f01a601a653e028e08fd74b9b949f6cf8304d88
~~~

Noto의 SIL OFL 1.1과 DejaVu의 저작권·사용 허가 원문을 함께 복사했다. Noto 원 폰트의 © 2014–2021 Adobe 표시와 라이선스 정보는 폰트 metadata에도 남아 있다. 원 폰트 bytes를 유지한다.

## 준비 점검 결과

현재 네 Python entrypoint의 직접 입력, LaTeX가 읽는 두 매크로와 그림, review 결과·판정은 모두 존재한다. 두 폰트 라이선스도 latex/fonts에 실제 텍스트 파일로 준비했다. Mono는 fonts/DejaVuSansMono.ttf의 명시적 상대경로로 수정되어 시스템 font-name 조회에 의존하지 않는다.

최종 준비 과정에서 세 폰트의 symlink를 같은 digest의 실제 파일로 바꾸었다. 세 폰트와 두 라이선스가 단위 안에 존재하며, ZIP 파일 목록에도 크기와 digest를 기록한다. 현재 scalar·그림·보고서 재현에 필요한 단위 내부 경로의 누락은 없다. 필요한 Python/TeX 실행 환경은 별도로 설치한다.
