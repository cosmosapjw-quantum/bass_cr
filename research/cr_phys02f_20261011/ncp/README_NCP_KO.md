# PHYS02F adjoint residence NCP 준비

준비 단계 수행. 현재 독립 판정은 review/INDEPENDENT_DECISION.json과 state/NEXT_DAG.json을 따른다. 실제 NCP는 실행하지 않았다.
이 환경에서 물리 G 생성, pulse, expm은 실행하지 않았다. 새 독립 Astra 검토와
현재 F FILE_MANIFEST 및 READY DAG가 필요하다. --plan exit 0은 READY를 뜻하지 않는다.

저장된 E/b/xT를 그대로 사용한다. 두 모델 각각 G를 한 번 생성하고 PR35 raw CSC
동일성을 확인한 뒤 active block에서 adjoint 3회, forward 2회(각 2 RHS)를 푼다.
900초, G 최대 2회, resolvent 최대 2개, solve 최대 10회, pulse/expm 0회이다.

저장소 루트에서 다음 명령을 사용한다:

```sh
python research/cr_phys02f_20261011/ncp/launch_residence.py --plan
python research/cr_phys02f_20261011/ncp/launch_residence.py --preflight
python research/cr_phys02f_20261011/ncp/run_and_collect.py --run-dir /ABS/FRESH_RUN --out /ABS/FRESH_RETURN
```

run과 return은 소스 저장소 밖의 서로 분리된 절대 경로여야 하며 기존 경로를 덮어쓰지 않는다.
wrapper는 execute 1회와 finally collect 1회를 수행한다. 실행 실패 또는 수집 실패를
성공 exit로 바꾸지 않는다. 정상 순서에서는 wrapper 뒤에 별도 collect 명령을 실행하지 않는다.
다음 명령은 수집 실패 원인이 확인되고 별도 복구가 정해진 경우에만 사용하는 진단·복구용이며,
위 세 단계의 후속 실행 명령이 아니다. 수집 재시도도 자동으로 승인되지 않는다.

```sh
python research/cr_phys02f_20261011/ncp/launch_residence.py --collect --run-dir /ABS/ACTUAL_RUN --out /ABS/NEW_RECOVERY_RETURN
```

ZIP 이후 생성된 collection/actual exit sidecar는 ZIP 외부
RETURN_FAMILY_MANIFEST에 포함한다. 전체 F 단위, 정확히 538개 의존 파일 및 18개 입력,
실제 run은 ZIP hash manifest로 복원한다. 이전 E root BUNDLE은 F 승인 근거가 아니다.

결과는 고정 연산자의 heat-weighted energy residence이며 입자 수명이나 local heat
침적 분포가 아니다. grid convergence 및 production gate는 기존 상태를 유지한다.
