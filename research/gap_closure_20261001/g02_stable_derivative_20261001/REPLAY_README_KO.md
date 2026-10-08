# R4W 재현 안내

이번 단계는 G02만 다룬다. `base/BASS_CR_R4V_RESEARCH_PACKAGE_20261001_v1.zip`은 변경하지 않은 이전 패키지이며, SHA256은 `dd7a5df422cc6b75a928d6583546ef5578de1e0fd5e7d669e0ae06253a1d69f3`이다. 그 안에 입력기저,72개 operator cache,이전 실패 판정,DBv8,그 이전 R4U 감사 자료가 있다.

바깥 패키지의 `source/`는 새 G02 연구 모듈과 AGENTS.md의 추가 안내다. `runs_r4w/`는 실제 분석·고정밀 기준 계산·테스트·독립 검토이며, `reports/`는 보고서와 새 DB다. `MANIFEST.json`의 member hash가 byte identity의 기준이다. 변경 전 기준 계산과 독립 검토로 수정한 이유는 `runs_r4w/initial_reference/` 및 최종 검증 영수증에 보존했다.

`cache_error_budget.py`는 저장된72개 캐시만 사용한다. `exact_trace_oracle.py`는 같은 캐시와 BASIS.npz/.json을 사용하며 원시 연산자나 전파기를 실행하지 않는다. NumPy,기존 캐시 검증 의존성과 Python 표준 라이브러리 Fraction/Decimal을 사용한다. mpmath 같은 새 production dependency를 추가하지 않았다.

실행 순서와 인수는 각 script의 `--help` 및 `G02_EXACT_TRACE_VALIDATION.json`을 따른다. 원래 절대경로와 source/native/input binding을 임의로 바꾸어 과거 실행의 identity가 유지된다고 주장하지 않는다. 현재 위치에서 이미 검증된 결과를 우선 읽고, 이동한 환경에서 재실행하려면 기존 프로젝트의 복구 및 새 실행 문맥 절차를 적용한다. 원래 물리 계산의 예산을 다시 소비하지 않는다.

고정밀 계산은 저장된 binary64 입력을 정확한 유리수로 해석한 기준이다. 물리적 정확도가80자리 또는120자리라는 뜻이 아니다. 연속성 회복 후보의 radial L² 변화와 셀 내부 derivative 변화는 전체 H¹ 또는 trajectory error bound가 아니다. 후보는 production 기저로 저장하거나 채택하지 않았다.

DBv9의 최신 상태는 `current_research_gap_status`에서 읽는다. DBv8의 이전 view는 `current_research_gap_status_v8`로 보존하고 모든 기존 테이블과 행은 유지한다. 이번 G02 증거와 상태만 별도로 추가한다. G02는 UNRESOLVED이며 production HOLD,capture=false,all_bound OPEN,b-grid NO_GO를 유지한다.
