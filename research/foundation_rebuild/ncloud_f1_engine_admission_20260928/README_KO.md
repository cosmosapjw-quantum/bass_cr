# NAVER Cloud F1: Intel/native engine admission

이 sidecar는 F0 cache-only M4 완료 뒤의 **새 native engine admission 구현**을 준비한다.

현재 상태:

```text
F0: STOP_F0_COMPLETE (reported; durable artifacts import pending)
F1 code implementation: authorized
F1 scientific native admission run: NOT AUTHORIZED
F2/F3: NOT OPEN
```

읽는 순서:

1. `F1_CONTRACT.json`
2. `F1_REPRESENTATIVE_QUERIES.json`
3. `F1_IMPLEMENTATION_PLAN_KO.md`
4. `F1_CODEX_HANDOFF_KO.md`
5. `F1_RETURN_CONTRACT.json`

F1은 새 engine의 수치 동일성/정책 동일성을 검증하는 단계이며 성능 benchmark가 아니다.
실제 c64-g3 worker scaling은 F1 admission이 닫힌 뒤 별도 F2에서 수행한다.

historical source, TP2D archive, basis, thresholds를 수정하지 않는다.
