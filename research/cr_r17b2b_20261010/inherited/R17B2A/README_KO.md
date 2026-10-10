# R17B2A

`REPORT_KO.md`는 새로운 물리 유도와 실제 nominal numerical 결과, `SOURCE_BINDING.json`은 원 입력, `NCP_HANDOFF_KO.md`는 후속 homotopy certification 계약이다.

- `python -B reproduce.py --verify-only`: manifest/선택 source identity 확인. 과학 재실행 없음.
- `python -B reproduce.py --output NEW_EMPTY_DIR`: 새18시험/nominal probe 결과/원 source point 대조/30조건을 재현. 기존 donor certificate suite는 호출하지 않음.

새 결과는 실제 photon–gas tangent, temperature·optical response, birth K0–K2 jump cancellation이다. 현재 값은 nominal diagnostic이며 새 FT03 source/tau interval certification은 없다. Python3, numpy/scipy/sympy 필요. 정확 패키지 version은 ENVIRONMENT.json에 있다.
