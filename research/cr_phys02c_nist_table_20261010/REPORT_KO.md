# CR-PHYS02C-NIST-TABLE01 반환

현재 구현/신규 검증은 `PASS_SCOPED`, 독립 검토도 같은 component 범위를 승인했다.
기준 commit은 `c471d455d0516385c94d6418c2b3bf583a0e717f`, tree는
`87cb43f59fa5e3579625da9860e0b973a0fc5f74`다. 새 sidecar 디렉터리 외에
기존 tracked 파일은 수정하지 않았다. Commit/push는 parent에 남겼다.

## 구현과 물리 의미

NIST 원 PDF를 정확한 SHA-256
`2492e6923503515bc6bf310da043eb64f72f3b2e609991fa037065a8afc966d1`로
로컬 보존하고, Tables 1 (pp. 328–329) 및 2 (p. 330)의 1000/1500/2000/3000 eV 두 전이 값을 전사했다.
Provider는 시작 때 로컬 PDF와 표의 identity를 확인한다. 실행 중 다운로드는 없다.

- `HI_1s_2p`: H I 1s 2S -> 2p 2P, 표의 excitation energy 10.204 eV.
- `HeI_1s2_1S_1s2p_1P`: He I 1s2 1S -> 1s2p 1P, 21.218 eV.
- [1000,3000] eV 안에서만 E와 sigma에 대한 구간별 선형 보간을 한다.
  원 표 노드는 그대로 반환하며 범위 밖/비유한 입력은 오류다.
- angstrom2에서 cm2로 1e-16을 곱한다. 반환값은 단면적이지 n*sigma*v
  반응율(s^-1)이 아니다. transition ID, 초기/최종 상태, excitation energy,
  단위와 source identity를 명시적으로 함께 반환한다.

HeI singlet 21.218 eV는 기존 old provider의 triplet `23s`
19.819614683951094 eV와 다르다. 새 표를 old 회계에 붙이거나 기존 채널을
대체하지 않았다. HI의 에너지도 인쇄된 표 값을 선택했으며, 기존 코드의
Rydberg 기반 값을 조용히 대입하지 않았다. P02B/P05/PR24 provider와
P02C endpoint source는 그대로다.

## 실제 신규 검증

실행 명령:

```bash
timeout 30s python3 -B research/cr_phys02c_nist_table_20261010/validate.py
```

Python 3.12.3, standard library만 사용했다. 첫 실행 exit 0, AST syntax 3개
파일 PASS, focused test 9개 PASS다. 독립 literal/Decimal fixture로 원 표
8개와 선형 중점 6개를 검사했다. 단위/채널 에너지, 범위 양 끝 포함,
바로 바깥 `nextafter` 및 비유한/잘못된 입력 거부, 기존 `HeI_23s` ID 거부,
양성/convex 보간과 반환 metadata 불변성을 확인했다.

수치 비교 허용오차 1e-14는 부동소수 연산 검증용이다. 원자물리 오차나
실제 cross section에 대한 보간 오차를 뜻하지 않는다. 첫 raw 로그와 실행
source hashes는 `evidence/FIRST_RUN.log`, `evidence/VALIDATION.json`에 있다.
Repair는 사용하지 않았다. 측정 CPU 0.016409080000000006 s,
process wall 0.0444786170264706 s다. source 취득과 Git subprocess CPU 등
기타 overhead는 `UNKNOWN_NOT_ZERO`다. Solver interval은 **0**이다.

## 범위와 다음 단계

이는 `SOURCE_BACKED_ATOMIC_COMPONENT_ONLY`다. 실제 model-error budget,
연속 물리 cross section에 대한 보간 오차, kernel 연결, old `23s` closure
교체, gas feedback, 전체 CR/IGM history와 global scientific admission은
계속 HOLD다. 선형 보간의 양성은 양성 양 끝의 convex combination에서
따르지만 원자물리의 정확도 bound를 만들지 않는다.

최소 다음 단계는 이 새 directory만 독립 review한 뒤 parent의 복구 패키지와
scoped publication이다. 그 이후 kernel에 쓰려면 singlet 채널 채택과
저에너지 old closure 연결을 별도 계약으로 정해야 한다. Source를 다시
찾거나 기존 커널을 반복 실행할 필요는 없다. 검증 driver는 최초 receipt를
덮어쓰지 않으므로 필요할 때는 source/evidence를 보존한 별도 출력 사본에서
실행해야 한다. 이미 완료한 kernel suite는 재실행하지 않는다.

연구/코딩 하네스에 따라 contract를 첫 실행 전에 동결했고, 원 source와
실행 identity, 범위별 validation 및 독립 review 상태를 분리했다.
