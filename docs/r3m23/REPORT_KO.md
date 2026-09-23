# R3M23 B2 closest/outgoing 짧은 창의 full-H 작업 정밀도

입력은 `cr/r3m22-inner-action-reference-20260923`의 exact HEAD `bd6cd9c183967e4319162c6023074162a3259d81`이다. 별도 branch `cr/r3m23-b2-cross-window-work-precision-20260923`에서 원본 B2 generation seal, manifest, receipt, 설정, 선택표와 두 checkpoint SHA를 검증했다. 선택은 `closest:g001152` (`539afab21049668e2c165e1700c907d760159cf0fbc6321f9b28032ce428f3c1`) 및 `outgoing:g002048` (`ddd80c96d304f3e7a500e5cc0445a16f1432078bdc85c673f78eff9335e46434`)이다. 선행 incoming 창은 R3M20/R3M22 증거를 그대로 사용했고 다시 실행하지 않았다. 두 창 모두 원본의 4 B2-dt, 길이 `0.04999569408955976` au이며 그리드·box·CAP·에너지·b·표현을 바꾸지 않았다. 원격 checkpoint 복원 시험은 하지 않았다.

GPU 전 strict tiny CPU oracle 4/4 PASS를 확인했다. 과거 R3M22의 첫 coarse denominator 실패와 GPU 이후 CPU gate 수리는 그대로 남아 있으며, 이를 GPU 전 통과로 소급하지 않는다. CodeRabbit의 사전 검토가 실행 계약의 입력·소스 해시 검사 누락 1건을 지적했고, GPU 시작 전에 검사와 집중 테스트를 추가했다. 실행은 GPU job 1회이며 자동 재시도는 없었다.

최종 테스트는 올바른 CUDA 라이브러리 경로에서 `365 passed`다. 그에 앞선 무지정 `pytest -q` 실행은 보관된 source 복제본과의 import 이름 충돌로 수집에 실패했고, `pytest -q tests` 첫 실행은 누락된 `LD_LIBRARY_PATH`로 CuPy 2개가 로딩 실패했다. 두 실패 로그를 그대로 보존했으며, 과학 결과나 테스트 기준을 바꾸지 않고 실행 환경을 바로잡았다.

실측 환경은 AMD Ryzen 9 5900X, affinity 24 logical/12 physical, 가용 RAM 약 79.4 GB, RTX 3090 24 GiB/CuPy 14.2.0이다. GPU probe 후 여유 `2,635,268,096` bytes로 2 GiB 하한을 넘었다. 사전 비용 `920.27`초는 R3M22 rate를 곱한 **예측**이다. 이번 실측 GPU job은 `903.058`초, probe 포함 FFT matvec `3,795`회였다. 각 창은 `477.537`초/`1,978`회 및 `423.551`초/`1,814`회이며, 기록된 최소 GPU 여유는 `4,145,217,536` 및 `5,176,295,424` bytes다. 모두 동결된 1,800초/창, 7,200초/job, 4,000 matvec, 2 GiB GPU 및 8 GiB 호스트 하한 안에 있다. 세부 실행·전송 시간은 `results/R3M23/GPU_RESULT.json`에 각각 기록했다.

| 같은 출발점의 창 | 자체 Strang 척도 (raw L2) | 그 1% | CF4 n8→16 | n16 inner repeat | n8 substep repeat | 판정 |
|---|---:|---:|---:|---:|---:|---|
| closest | `1.795672139813351e-5` | `1.795672139813351e-7` | `7.41035160757068e-9` | `0` | `1.6605985172529764e-15` | Strang 척도에 대해 일치 |
| outgoing | `1.5006759727088076e-5` | `1.5006759727088075e-7` | `2.0651164776986198e-9` | `6.181932652712236e-15` | `8.717507491097588e-15` | Strang 척도에 대해 일치 |

각 창의 자체 Strang 척도는 동일 출발점의 S4/S8/S16과 CF4 n16 사이 raw L2 거리의 최소값이다. CF4 n8→16 거리는 각각 이 척도의 `0.04127%`, `0.01376%`다. frozen/buffer 1·4 step parity, 한 단계 CF4 substep/inner 보정 한계 `2.103970853068276e-14`, 두 반복 비교, 모든 endpoint의 유한성 및 FFT accounting을 독립 JSON 재계산에서 확인했다. `results/R3M23/HOST_VALIDATION.json`의 판정은 `PASS_STRANG_SCALE_COMPARISON_ONLY`이다.

이 비교는 동일한 **이산** 비Hermitian full-H/CAP의 두 짧은 restart에서만 성립한다. CF4 자체 n8→16 차이를 분모로 하는 새 1% 기준은 여전히 미해결이고, 독립 production ODE 기준해·시간 수렴·전체 충돌·투영 채널 정확도도 입증하지 않았다. 따라서 서로 같은 정확도 목표를 만족한 wall time 비교나 production speedup을 주장할 수 없다. 참고용 실측 전파 시간은 closest S16 `1.553`초/CF4 n16 `118.796`초, outgoing S16 `1.572`초/CF4 n16 `98.208`초이지만 두 방법의 오차 수준이 같지 않다. 정확도를 production 판단의 우선 조건으로 두고 속도는 같은 정확도를 검증한 뒤에만 비교한다.

첫 실패·미해결 기준은 그대로 유지한다. R3M11/R3M14의 b-grid `NO_GO`, R3M22 CPU coarse gate 원본 실패 및 self-scaled CF4 1% 미해결, 본 노드의 time refinement 미검증은 성공한 짧은 창으로 덮어쓰지 않는다. 새 full collision, preparation 재실행, finer h, 표현 변경, projection/checkpoint write는 모두 0회다. Production admission은 `HOLD`, b-grid는 `NO_GO`다. 다음 canonical node는 정확히 `N1_TDL_PRODUCTION_H_CF4_SELF_SCALED_REFERENCE_AND_TIME_REFINEMENT` 하나이며, 별도 동결 계약에서 독립 기준해와 시간 수렴을 먼저 정해야 한다.

독립 GPT‑6 Astra/xhigh 읽기 전용 검토는 저장된 결과에 BLOCKER/MAJOR가 없다고 판정했다. MINOR 1건은 같은 스크립트를 재호출하면 기존 `PREFLIGHT.json`의 create-only 충돌을 알기 전에 GPU probe 3회를 실행할 수 있다는 것이다. 실제 재호출은 없었고 저장된 3,795회에는 영향이 없다. 측정에 사용한 스크립트와 계약 해시를 변조하지 않기 위해 이 노드에서 GPU 작업을 다시 호출하지 않고, 다음 실행용 진입점에서 출력 존재 검사를 probe 전에 두어야 한다. 내부 정확도 상계는 exact-arithmetic bound이며 부동소수점 오차의 상계가 아니라는 제한도 유지한다.
