# R3M27 — B3 full collision 및 사전 등록 시간 판정

**판정:** 고정 h=.20, 100 keV/u, b=2, projectile hydrogen `n≤1/2/3` 선택 유한 span에서 `TEMPORAL_ESTIMATE_VALIDATED_FOR_FIXED_H_SELECTED_SPANS`다. 경험적 추정이며 `certified=false`다. 현재 선택 모형의 전체 numerical production은 **HOLD**, all-bound는 **OPEN**, b-grid는 **NO_GO**다. 공간·h-dt·preparation·box/CAP/finite-time은 열려 있다.

## 입력과 실행 동일성

R3M26 입력 branch `cr/r3m26-model-production-convergence-20260924`의 exact HEAD `e32f62864ded928580d00b31f2dcdbb4ea688ed9`와 tree `07f41219a01ab16ee56089a490ee38e864607092`를 확인한 뒤 새 branch `cr/r3m27-b3-full-collision-20260924`를 만들었다. 기존 branch와 사용자 untracked 파일은 보존했다. 사전 코드 commit은 `41ba35c6c95573602c19e1029287b64a5f940adf`. `cr_repro` digest는 `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`로 유지했다. B2 작은 raw result SHA는 `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc`, frozen forecast 파일 SHA는 `5eb9920d10ed467df7bc512cbbf983ee1ce95d2df94a15d21aa8e6940ebf743e`, payload SHA는 `be693bbae3a90420b25f441431ee0f63b2dd8131fd1c2017c81c847e83a4c64e`다. 관측 뒤 forecast·모형·임계값을 변경하지 않았다.

R3M27 전용 외부 coordinator `scripts/r3m27_b3_execute.py`와 config `configs/r3m27/B3.json`을 추가했다. frozen B1/B2 family에서 requested dt만 `.00625`로 바꿨다. 실제 dt는 `0.00624946176119497` au, 7172 step, 공통 horizon `44.821139751290325` au다. 기존 B2 전용 3586/29 검사와 frozen numerical source는 변경하지 않았다. 별도 계약 `results/R3M27/CONTRACT.json`의 SHA는 `d2ed93efd963a9aa8fb61b34dd8b2cc82ebefa4d17e199f4d4c6b71abf6ee689`이며 source/config/forecast/runtime/argv/output root/57 generation/자원·timeout을 묶었다. 이 SHA를 명시적으로 승인해 fresh output `/mnt/sn850x2t/bass_cr_r3m27_20260924/B3`에서 단 한 번 실행했다.

science interpreter는 `/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python`이며 Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, CuPy 14.2.0, CUDA runtime 12090, RTX 3090을 확인했다. 패키지 변경은 없었다. 외부 exact B3 preparation 1회는 417.48초였고 initial.npy SHA `ed2ff41eb7517f245d5d5a2df4ce699b607f101406c1a588d3fd4a9b522f5daa`로 canonical B initial과 같았다. 별도 preparation receipt는 전체 B3 config를 담고 B2 receipt를 재표기하지 않았다. collision 내부 witness preparation 1회도 준비 배열과 byte-identical임을 확인했다.

## 실제 원본 B0–B3 결과

| cell | nstep | actual dt (au) | P1 | P2 | P3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| B0 | 897 | 0.04996782580968821 | 0.005936876533244324 | 0.007416156280617876 | 0.007911255992446844 |
| B1 | 1793 | 0.02499784704477988 | 0.006068282194867191 | 0.007562290857479282 | 0.008063449050040342 |
| B2 | 3586 | 0.01249892352238994 | 0.006085241312208360 | 0.007581938013116333 | 0.008084190148156251 |
| B3 | 7172 | 0.00624946176119497 | 0.006089329814044807 | 0.007586698170080142 | 0.008089219135272727 |

세 채널의 B1→B2와 B2→B3 증분은 모두 양의 같은 부호이며 크기가 수축한다. 사전 규칙은 `|B3−B2|/|B3|≤0.001` 및 `U_time/|B3|≤0.001`, `U_time=2 max(E_model,D_hold)`다. 네 무한 dt 후보의 B3 잔여와 세 frozen forecast의 held-out residual을 사용했다. 안전계수 2는 설계값이며 확률적 신뢰도나 엄밀 상한이 아니다.

| channel | B2→B3 pair / B3 | E_model | D_hold | U_time / B3 | fine observed p | gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| P1 | 0.000671421 | 1.362834e-6 | 1.903909e-6 | 0.000625326 | 2.052417 | PASS |
| P2 | 0.000627435 | 1.586719e-6 | 2.123608e-6 | 0.000559824 | 2.045239 | PASS |
| P3 | 0.000621690 | 1.676329e-6 | 2.207605e-6 | 0.000545814 | 2.044153 | PASS |

Four-point even least-squares의 P∞ 후보는 P1 `0.006090077483018902`, P2 `0.007587625465438893`, P3 `0.008090220119295681`이다. fine even, fine p2, fine single-power 후보와 네 leave-one-out residual 전체는 `results/R3M27/B3_TEMPORAL_EVALUATION.json`에 남겼다. B3 held-out residual은 P1 `+8.462326e-7`, P2 `+9.084320e-7`, P3 `+9.302412e-7`이며 diagnostic이다. 관측 B3를 중앙값으로 보존한다.

## 실행·검증·남은 gate

한 GPU job으로 57개 128-step generation(마지막 4 step)을 순차 실행·게시했다. 57개 generation의 manifest·receipt·파일을 57.456GB 규모로 다시 해시해 PASS했고 최종 collision state SHA `cb2ba543be4616ca2776e46b3b21269308d149557e317d9eebc13752c352b4ad`가 마지막 generation과 같다. 최종 raw result SHA는 `7360649d2148420c3eebdb32f05938a3ee4afc048655e300a6b19b1e12f7dbce`. 다만 raw endpoint 배열을 독립 알고리즘으로 재계산한 것은 아니다.

전체 run wall 2544.38초다. 외부 preparation 418.56초, collision command 합 1796.52초(첫 내부 witness 준비와 마지막 Gram 분석 포함), snapshot command 합 115.28초다. 첫 witness 경계 약 419.02초는 설정·해시도 포함한다. 마지막 chunk 242.82초는 Gram 분석을 포함한다. 순수 GPU propagation, Gram만의 시간, D2H는 별도 계측되지 않았으며 microbenchmark로 대체하지 않는다. sampled 최소 GPU free는 12.81GiB, host available은 68.81GiB, disk free는 513.37GiB였다. 이는 다른 프로세스를 포함한 free-space 샘플이며 이 job의 독립 peak allocation 측정은 아니다. 실패·자동 재시도는 0회다. cloud raw readback은 NOT_RUN, restore는 RESTORE_NOT_TESTED다.

TDD 최초 RED(import 실패)를 그대로 보존했고 전용 시험은 최종 `3 passed`다. 최초 전체 suite는 CUDA 동적 라이브러리 경로 누락(`libcufft.so.11`)이라는 환경 실패로 `481 passed, 2 failed, 1 skipped`였다. 기존 라이브러리 경로를 명시한 재검증은 `484 passed`였고 source 확정 뒤 다시 `484 passed`였다. compileall 및 CLI 검사는 PASS다. 실패 기록을 성공 기록으로 덮지 않았다.

`results/R3M27/CURRENT_SELECTED_P3_LEDGER.json`에서는 P3의 real-time `U_time=4.415209956028926e-6`만 사전등록·held-out·envelope 검사를 갖춘 비인증 `VALIDATED_ESTIMATE`다. B3 기준 .10% 절대 배분 `8.089219135272728e-6` 이내다. 이전 공간·h-dt 차분은 `RAW_PAIR_DIFFERENCE`/`RAW_INTERACTION_DIFFERENCE`로 남고, preparation과 box/CAP/finite-time은 null/OPEN이다. typed 총 budget은 `NUMERICAL_BUDGET_OPEN`이다. `GLOBAL_TIME_ERROR`의 엄밀 인증도 NOT_EVALUATED다. 논문 그림/private raw와의 정확한 일치는 이 내부 모형의 production 선행조건이 아니다.

다음 canonical node는 `N1_TDL_PRODUCTION_H_SPATIAL_H_DT_BUDGET` 하나다. 같은 물리적 horizon과 충분히 작은 actual dt에서 h=.25/.20의 spatial .30% 및 projectile subcell translation을 판별하고 h-dt 상호작용을 한 번만 계상하는 실행 계약을 먼저 만든다. R3M27에서는 B4, finer h, representation 변경, 새 b-grid/physical rate, main merge를 수행하지 않았다.

상위 노력의 독립 read-only 검토(`results/R3M27/INDEPENDENT_REVIEW.md`)는 지정 범위에 PASS를 주고 차단 결함은 찾지 않았다. 검토자가 발견한 roadmap provenance MINOR는 frozen R3M26 commit의 파일 SHA와 갱신된 R3M27 working-tree 파일 SHA를 별도로 명시하여 닫았다(`results/R3M27/INDEPENDENT_REVIEW_CLOSEOUT.json`). 수정 전 ledger 두 버전을 보존했고 세 typed 평가의 수치 JSON은 동일하다. 독립 검토 역시 endpoint 전파·Gram projection의 독립 재계산을 주장하지 않는다.

최종 작은 bundle(55,289B, local SHA `c15388cb9237737dcb0f2249890e1c1fdd5f986a6b04701e2ed52ecc433e21a2`)은 final state **메타데이터**, raw result, witness, 57번째 manifest, 계약·분석·감사·코드·보고서 24개 파일과 내부 manifest를 담는다. state.npy 배열은 포함하지 않았다. Dropbox와 Drive 각각의 업로드 응답 및 ID·크기 metadata R1 일치를 `results/R3M27/delivery/DUAL_BACKUP_RECEIPT.json`에 기록했다. 제공자 checksum이 없어 원격 byte SHA 동일성은 미검증이다. `UPLOAD_VERIFIED != RESTORE_VERIFIED`이며 raw readback NOT_RUN, restore RESTORE_NOT_TESTED다.
