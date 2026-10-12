# BASS_CR: 온도와 H/He 조성의 자기일관적 진화

**CR-THEORY-FEEDBACK-20261013 — COMPLETE_CONDITIONAL_THEORY · PROMOTE_SCOPED / PASS**

이번 단위는 공통 사건 extent로 경쟁 반응의 재고를 제한하고, 각 iterate에서 양수성과 핵수·전하·총에너지를 보존하는 유한 step을 구성한다. 온도와 조성의 endpoint 피드백에 대해 정의역 보존, 존재, 계산 가능한 수축 조건과 온도 오차 상계를 유도했다. 공변 에너지·입자수 투영은 실제 Wolfram+xAct로 검산하고 prescribed Bianchi I geometry에 연결했다.

## 읽을 파일

- [33쪽 전체 PDF](latex/report.pdf)와 [전체 Markdown 원고](latex/manuscript.md)
- [독립 판정](review/DECISION.json), [독립 검토](review/REVIEW_KO.md), [결과](RESULTS.json)
- [현재 가정](CONTRACT.json), [상세 가정](derivations/FEEDBACK_ASSUMPTIONS.json), [오차 지도](derivations/FEEDBACK_ERROR_MAP.json)
- [다음 계획](PLAN_KO.md), [DAG](NEXT_DAG.json), [인계 상태](HANDOFF.json)
- [전체 LaTeX 원고](latex/report.tex)와 [문서 생성 코드](build_report.py)

`CONTRACT.json`과 `CLAIMS.json`은 독립 검토가 읽은 후보 snapshot으로 보존한다. 최종 채택은 `review/DECISION.json`과 `RESULTS.json`에 있다. `REPORT_KO.md`는 설명 부분의 조립 입력이며, 세 유도와 원전 비교를 모두 포함하는 전체 원고는 `latex/manuscript.md`다.

## 실행 근거

Python Fraction 사건 검산 9개와 feedback driver 검산 2개, Wolfram 23개 named group / 25개 scalar 영잔차를 보관했다. xAct의 응력 직교성·무흔적성·에너지 투영·입자수 current 네 항목도 실제 실행 결과다. 독립 검토는 원출력과 코드 및 직접 유도를 사용했고 과학 재실행은 0회였다.

정확한 중성 예제는 eta=4/17에서 extent=1/4, c_v T/E0=7/10, q=170/841을 갖는다. Driver의 15회 accepted update 후 실제 온도 오차 6.290324474015892e-14 K가 반환 상계 2.31157671764639e-13 K 이하였고, 실제 ODE endpoint rate defect는 별도로 반환했다. 이 예제의 E0=(3/2) k_B (1 K)는 검산을 위한 에너지 단위다.

## 재현

작은 exact reference의 실행 환경은 Python 3.12 표준 라이브러리다.

```bash
python3 checks/run_event_checks.py
python3 checks/run_feedback_checks.py
```

위 명령은 검산 출력 파일을 새로 쓴다. 원 기록을 보존하려면 별도 복사본에서 실행한다. 다음 연구를 재개할 때에는 우선 기존 identity와 근거를 재사용한다.

`checks/wolfram_xact_checks.wl`, `checks/wolfram_feedback_checks.wl`, `checks/wolfram_geometry_checks.wl`은 각자 새 Wolfram kernel에서 실행할 수 있다. xAct bootstrap은 공식 소스의 SHA-256을 먼저 확인하고 지원하는 순수 Wolfram Language permutation backend를 선택한다. 초기 backend 진단과 중간 CAS 메시지도 원출력에 남아 있다.

PDF만 다시 컴파일하려면 `latex/`에서 XeLaTeX로 `report.tex`을 두 번 컴파일한다. 전체 그림·원고 조립은 `python3 build_report.py`이며 matplotlib, numpy, pandoc, XeLaTeX가 필요하다. 전체 SOURCE ZIP에는 폰트와 라이선스가 포함된다. Git checkout에서는 같은 시스템 폰트(Noto Sans CJK KR, DejaVu Sans Mono)를 사용할 수도 있다. 문서 재생성은 과학 검산을 실행하지 않는다.

## 다음 연구

1. 실제 atomic kernel의 현재 parent/daughter 에너지를 양의 보존 사건 열에 결속한다.
2. 온도 의존 cutoff의 implicit 경계 응답을 moving-boundary moment와 현재 EOS에 결합한다.

현재 결과의 대상은 고정된 유한 사건 열, 유효 rate domain, 공통 angular closure와 정칙 시간 branch다. 실제 scenario/source 및 관측량 오차 예산은 DAG의 응용 node에서 결속한다.

## Publication identity

소스 archive는 science commit과 `PUBLICATION.json`을 결속한 불변 snapshot이다. Archive 자체와 provider receipts의 순환 hash를 피하기 위해 이후 저장 완료 증명서는 현재 Git branch의 `DELIVERY.json` 및 최종 인계 JSON에 덧붙인다. 기존 archive를 덮어쓰지 않는다.
