# R4AM weak-K 원점 정칙화 참조 구현

이 폴더는 원자 데이터 생산 전용이다. Bianchi 물리는 rei_bianchi가 담당한다.

R4AL 다음 단계의 weak gradient·Coulomb·ETF cross 적분을 직접 구현했다. 일반 shell 삼각형과 두 원점 chart를 정확히 연결하고 사차까지의 entire 각도 모멘트를 사용한다. 고정 geometry에서 complex ellipse majorant와 explicit Gauss remainder를 반환한다.

## 현재 판정

- 유도·reference provider·새 fixture 검증 완료. 실제 candidate cover의 영역 누락 0.
- 실제 원자 K 적분 0. 전체 K, 연속 K remainder, bridge 및 물리 source 승격은 없음.
- pure Python 정수구간 oracle다. native 성능 또는 full18 production solver 완료가 아니다.
- 기존 중심 S, M9, R8, shifted 적분, radial 적분과 과거 suite 재실행 없음.

`DERIVATION_KO.md`, `RESULT_SUMMARY.json`, `NEXT_DAG.json`, `SOURCE_INPUT_LOCK.json`, `CODEX_HANDOFF_KO.md`를 먼저 읽는다. 새 코드 변경시 해당 변경영역만 시험한다. 불변 vendor의 역사적 suite를 반복하지 않는다.

새 module 시험 명령:
```
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 pytest -q tests -p no:cacheprovider
```
이 명령은 새 R4AM fixture만 실행하며 원자 native 적분은 하지 않는다. 이미 기록한 이 릴리스의 동일 시험을 단순 handoff 수신 때 반복할 필요는 없다.

실제 원자 적분에 이 README 자체가 실행 승인을 부여하지 않는다. 첫 외부 작업은 기존 R4AH_m64다. R4AM reference runner는 별도 prepare/정확 hash 승인 및 자원 조건을 요구한다.
