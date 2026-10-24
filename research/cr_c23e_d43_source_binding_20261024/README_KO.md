# BASS_CR C23E — D43K source binding

**COMPLETE_SCOPED / NUMERICALLY_CHECKED_SCOPED**, independent PASS_SCOPED. 실제3개 PW19 광원에 대해 저장H 모멘트에서 D43K 문턱 모멘트를 구성하고,21species 순간 source의 PI/RR/CX·thermal/fast electron·에너지 장부를 결속했다. 새ODE0, 완료 계산 재실행0.

읽는 순서: [RESULTS_KO.md](RESULTS_KO.md), [THEORY_KO.md](THEORY_KO.md), [FROZEN_CONTRACT.md](FROZEN_CONTRACT.md), [독립 검토](review/INDEPENDENT_REVIEW_KO.md), [DAG](NEXT_DAG.json), [handoff](HANDOFF_KO.md).

기존 완료 근거를 복원하기 위해 아래 실행을 반복하지 않는다. 결과는 `runs/C23E_D43_SOURCE_BINDING_20261024T021612Z_v1/`에서 직접 읽는다. 새로운 입력/코드 변경으로 별도 검증을 허용받은 경우에만 다음 portable entry point가 새 create-only output을 만든다.

```bash
python implementation/dispatch_d_binding.py
```

필요 환경은 Python3.12, NumPy2.3.5, SciPy1.17.0, Matplotlib이며 실제 source/환경/자원은 run의 manifest와 preflight에 있다. 모든 입력은 상대경로로 포함되어 있다. 원 실행 source와 배송용 경로 교정 source는 별도 identity로 보존한다. 배송 교정29checks와 원 과학104checks는 다른 검사 집합이다.

선택된 근사는 D threshold-gated H-equality 및 조건부 VF RR moment다. 실제 동위원소별 PI/RR Milne·full21 rate coverage·full stopping·우주론적 열진화는 OPEN이다. 고에너지 핵 전체 campaign과 general triaxial/tilted/polarized CMB는 HOLD이다. 소유권·유효영역·source identity가 다른 REI/WU 계산을 단일 ensemble로 합치지 않는다.
