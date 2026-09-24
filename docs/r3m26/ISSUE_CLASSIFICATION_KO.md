# R3M26 문제 분류와 해결 경로

같은 관측값 변화가 여러 근사에 의존하므로 아래 분류는 원인을 확정한 부분과 아직 판별해야 할 부분을 구분한다. 현재 자료는 '물리 모형이 모순이어서 시간수렴이 실패했다'는 결론을 지지하지 않는다. 반대로 물리 모형의 현실 오차가 1% 미만이라는 결론도 주지 않는다.

| 구분 | 확인한 사실 / 원인 판정 | 해결책과 필요한 증거 |
|---|---|---|
| 물리 모형 | 단일 비상대론 전자·고정 target·처방된 직선 proton 궤적은 명시 가능한 준고전 모형. recoil/deflection/상대론을 생략한 실제 실험 discrepancy는 미정 | 차원 있는 3체 출발점→처방 궤적→전자 Hamiltonian→au를 명시. 외부 비교는 사용 조건이 맞을 때 수행하며 private raw exact match는 제외. 이 모형의 수치오차와 현실 discrepancy를 분리 |
| 수학적 정의 | +1/R 핵간 항은 같은 b의 전자 확률에 대해 scalar gauge. Galilean ETF의 공간 위상은 필요. Gram 보정은 sampled finite-span의 정사영 | 부호·단위·위상 불변성·weighted projector를 직접 유도. raw overlap 합/생존 norm 정규화/finite complement를 다른 관측량으로 혼동하지 않음 |
| 시간 알고리즘과 정확도 | B0/B1/B2는 수축하나 B1→B2 P 변화 .2566–.2787%로 예산 초과. 겉보기 p≈2.9만으로 Strang 결함이나 물리 오류를 확정할 수 없음. 혼합 dt²+dt⁴도 기존 3점을 설명하므로 모델 미식별 | R3M25 same-H 실제 t=0 CF4 국소 PASS 재사용. 새 B3를 사전에 고정한 세 예측과 비교하고 네 잔여 모델의 envelope로 시간 추정. p=2 screen 단독 veto는 미래 기준에서 제외. 추정은 엄밀상한이 아님 |
| 공간 표현과 정확도 | 이전 dt=.025 P3 h gap 2.9528%, h–dt interaction 1.0445%. 시간과 공간의 독립 가산을 가정할 수 없음. 세 h의 projectile mesh phase도 동일하지 않았음 | 시간 단계를 닫은 뒤 공통 endpoint/정확도와 subcell shift를 포함한 spatial 판별. Coulomb singularity-aware 대안은 그 결과가 필요할 때 한 가지 선택. 지금 'FFT가 틀렸다'고 단정하거나 softening으로 모델을 바꾸지 않음 |
| 준비와 끝점 | prepared/internal byte identity는 같은 상태 사용을 증명하지만 continuum 1s 정확도를 증명하지 않음. incoming global Coulomb phase와 누락된 tidal dynamics는 다름 | isolated-atom analytic 식, discrete residual, imaginary-time τ/T 및 h 확인. finite-start/stop과 target/projectile separation에 따른 실제 확률 안정성 평가 |
| 경계와 CAP | fixed-rate W≥0 CAP는 수축적 numerical boundary. B1/B2 norm의 작은 차이는 작은 capture 오차의 증명이 아님 | norm loss를 ionization으로 동일시하지 않고 box/width/strength/endpoint 민감도로 full-component .15% envelope. high-n support와의 결합 포함 |
| 채널 완전성·적분 | P3는 n≤3이며 total capture가 아님. 단일 b는 σ가 아님 | 명시적 n-ladder+tail 또는 적합한 all-bound projector 중 하나를 완성. b 적분·끝부분을 검증한 뒤 원래 50/100/225 keV/u 목표로 종합 |
| 구현·증거 | R3M25 첫 시도는 VRAM 실패로 과학적 반증과 구별됨. 두 번째 실제 창은 국소 PASS. 현 원자료 바인딩은 일치 | 실패 원문 보존, new attempt 별도 봉인. R3M26에는 판정기·typed ledger·소규모 이론 검산을 추가. source hash/시험 수/JSON 'PASS'를 numerical accuracy 대신 쓰지 않음 |
| 성능·자원 | actual GPU buffer reuse 속도는 약1배, CPU4-worker microbenchmark는2.09배. CF4 국소 비용으로 full-run 우월성을 주장할 수 없음 | 정확도를 맞춘 전체 비용을 측정. B3는 frozen Strang 유지, VRAM headroom과 host staging/I/O 관리. GPU와 CPU를 모두100% 채우는 것보다 검증된 time-to-solution을 최소화 |

수학적 정초와 직접 원전 locator는 `MODEL_FOUNDATION_KO.md`, 수치 분기와 오차 추정은 `NUMERICAL_STRATEGY_KO.md`, 실제 코드/성능 자료는 `PERFORMANCE_AND_CODE_REVIEW_KO.md`에 있다. 다른 HH 스레드의 개선 수식이나 속도 수치를 CR의 증거로 전용하지 않았다. 반영한 것은 모형 정의·검증·관측량·출시 범위의 분리 원칙이다.

R3M26의 변경은 종료 기준을 명료하게 만들고 실행 가능한 판정기를 제공한다. 기존 시간/공간 실패를 삭제하거나 새 물리 결과를 만들어낸 것은 아니다.
