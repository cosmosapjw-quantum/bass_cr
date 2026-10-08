# R4AJ 실행 보고서: selected-1s와 공진 부분공간 판별

2026-10-03. **CLOSED_SELECTOR_AND_REFERENCE_RESONANCE_DISCRIMINATOR**.

R4AI에서 우선순위1로 지정한 local node를 수행했다. 실제 BASS 원자적분이나 memory prepare를 다시 실행하지 않고, 저장된 9×9 intrinsic 행렬쌍과 현재 channel metadata의 정확 산술, 새 작은 reference fixture로 선택자와 phase-gap의 적용 조건을 판별했다. 직전 중국어 응답은 docs/R4AI_PREVIOUS_REPLY_KO.md에 한국어로 온전히 재출력했다. 번역본의 R4AI 결과는 과거 단계의 기록이며 새 시험으로 세지 않는다.

## 1. 실제 결과

| 항목 | 결과 | 근거 상태 |
|---|---|---|
| 현재 측정 | projectile labeled1s, full index9 | metadata identity와 channel order 확인 |
| 옛 reference | projectile negative rank5 | 보존된 reference 문서 |
| rank5와 rank1 직교 projector 차이 | 정확히1 | 공통 Hilbert 공간에서 직접 증명 |
| 저장 한 중심 행렬 gap | ≥373/1000 Eh | 정확 유리수 min-max 및 독립 LDL 확인 |
| raw1s에서 저장행렬 ground projector까지 거리 | ≤4.488×10^-15 | residual과 spectral separation, 위쪽 반올림 |
| 동일 두 중심 직합에서 P1s 대 full complement gap | 정확히0 | 같은 isolated ground의 이중 중복 |
| 직합 ground pair 대 rest gap | ≥373/1000 Eh | 위 단일 행렬 certificate의 직합 |
| 실제 finite-separation bridge gap | null | 아직 연속 physical operator 상계 없음 |

저장행렬의 부동소수점 일반화 고유값 진단은 약 −0.4999999997137595, −0.1249999999940158(3개), −0.1249999999641030, +0.0005525039691252, +0.0140128582518972(3개)다. 이 표시값을 interval certificate로 쓰지 않았다. certificate의 α=−499/1000, β=−126/1000은 사전 계약에 고정했다.

이번 결정은 **측정은 P1s로 유지하고 T1s/P1s를 함께 retained dynamic cluster로 취급하는 경로**다. 새 cluster를 실제 production solver에 설치하지 않았다. 과거 rank5 관측량을 rank1로 바꾸면서 작은 기존 mapping error를 상속하지 않는다. 두 중심 finite-R의 interacting gap이 정확히0이라고 주장하지도 않는다.

## 2. 완료한 이론과 코드

선택자 rank 판별, metadata 기반 1s 결합, exact 저장행렬 gap/잔차 사상, 비직교 span projector, frame connection을 포함한 generator 변환, 공진을 유지한 Sylvester/integral-action 조건부 bound, 내부 reference transfer와 제거공간 오차의 분리된 합성을 구현했다. 자세한 전제·유도·단위·반례는 DERIVATION_KO.md에 있다.

분리된 block의 실제 연속 gap γ와 B/Bdot/diagonal derivative 상계가 주어질 때만 조건부 bound가 계산된다. 현 물리 입력이 없는 상태에서 γ=0.373을 실제 bridge에 대입하지 않는다. 별도 frame connection을 생략하거나 Γ를 강제0으로 투영하지 않는다. 내부 T1s↔P1s 전이를 제거공간 누출오차와 같은 것으로 읽지 않는다.

## 3. 새로운 가벼운 수치 판별

합성 3×3 상수 Hamiltonian에서 retained coupling1/4Eh, 외부 coupling1/1000Eh, 외부 gap7/4Eh, T=6ta를 사용했다. 정확 조건부 ||U−Ubd|| 상계503/437500≈0.0011497143에 대해 실제 작은 행렬 지수함수의 차이는0.00075059944였다. 그런데 P1s 전이는0.99499592618이었다. 독립70자리 고유분해 계산도 같은 확률을 확인했다.

따라서 **외부 공간의 영향이 작아도 실제 retained pair 내부 전이가 거의1일 수 있다**. 이 fixture는 누출 bound가 작다는 이유로 전체bridge5e-6를 선언하는 잘못을 차단한다. 실제 BASS 산란 예측이나 새 physical source 결과가 아니다.

## 4. 검증 범위

새 변경영역 시험72건 통과. 처음2개 rank/gap 행동은 실제 RED→GREEN을 기록했고 나머지는 추가 검증이다. 모든72개를 TDD라고 소급 표시하지 않는다. 새로운 read-only 독립 검토33조건은 S9개와 complement8개의 exact LDL pivot, exact S inverse residual, mapping 부등식, structural resonance, missing physical bound, 새합성예제의70자리 비교를 포함한다. 독립 인간/별도 agent나 전체 원자 적분기의 검토는 아니다.

새 saved-matrix/reference 실행1회, 실패0회, wall 약0.003704초다. 이는 원자실행 시간이 아니며 NCP64 성능으로 외삽하지 않는다. 외부60초 timeout은 적용했으며1GiB는 관측RSS와 비교한 계획한도이지 OS address-space hard limit을 적용했다는 뜻은 아니다.

신규 atomic/shifted/M9/center/oldR8/D/V 계산0회, 예전 scientific suite0회, memory admission 재시도0회다. 기존 source·행렬·상태·실패는 수정하지 않았다.

## 5. 닫히지 않은 것과 다음 작업

실제 continuous physical bridge gamma/B/Bdot/L, retained internal κ/그 적분, exact endpoint state, weak-H/operator 오류, whitening·selector embedding 상계가 남는다. physical_bridge_upper=null, full_stencil_total_upper=[null,null]이다. 옛 raw bridge≈504.54와 target5e-6를 변경하지 않는다.

다음local은 LOCAL_RESONANT_PAIR_WEAK_BRIDGE_ENVELOPE다. 현재 candidate와 weak generator에서 공진쌍 내부 transfer 및 rest coupling을 같은 frame/구간에 묶고 실제 계산 가능한 연속 상계 공급기를 만든다. 그것이 부족한 경우 필요한 최소 cluster 확대를 별도 판단한다. next external은 그대로 R4AH m64다. 나머지9점은 첫점 수락후 새승인이 필요하다.

DBv22는 DBv21을 복제한 뒤 별도 local-discriminator/source/workfront 테이블만 추가했다. 기존15개 view와 현재13개 과학 gap행을 모두 보존했으며 integrity_check=ok다. G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO. 여기서 가능한 연구가 모두 끝났거나 post-gap coordinator 활성화 조건을 만족했다고 보고하지 않는다.

## 6. 전달 범위

이번 새자료는 r4aj_selector_bridge 아래 추가한다. 기존 R4AI의85개 아직 미적용파일과 함께 적용 가능한 create-only 통합patch를 별도로 제공해, 원래patch를 먼저commit해서 두번째patch의부모조건을 깨뜨리는 혼동을 피한다. 통합patch와 원래R4AIpatch를 둘 다 적용하면 안 된다. 실제 branch가전진했거나 어느목표파일이이미존재하면 적용을멈추고 exactdiff를 읽는다.

완전한 Git객체이력이 없으므로 syntheticancestry의bundle을만들지않는다. Git실제게시와Cloud업로드상태는detachedreceipt에서별도로확정한다. 원R4AD차단mutation이나과거R4AA379mapping은이번통합patch에포함하지않는다. 새로운ref데이터,조건부code,번역,DBv22,fullR4AIparentarchive와수정handoff를함께제공한다.

최종 전달 코드의 신규 음성대조8건도 통과했다. 이번 변경영역 전체는 reference72+delivery8=80건이며 로그 TESTS_FINAL_WITH_DELIVERY.txt에 있다.
