# CR-PHYS01 독립 최종 검토

2026-10-10 UTC · reviewer `/root/axi_independent_review` · 실제 모델 식별 `UNKNOWN` · 선택 하네스 GPT-6 Astra v4.0.0.

**판정: `PROMOTE — CONDITIONAL_PHYSICAL_COMPONENT_AVAILABLE`.** 실제 출처가 있는 비영(非零) proton 주입–무충돌 수송–H/He impact ionization–secondary cascade–REI 국소 미분 연결이 존재한다. 따라서 “실제 charged-particle provider가 없다”는 blocker는 이 범위에서 해소됐다. 완전한 CR 손실망, 인과적 turn-on 침적 역사, 진화하는 IGM production admission은 **HOLD**다. 이 구분은 component의 존재를 부정하거나 전체 역사를 이미 검증했다는 뜻으로 바꾸지 않는다.

이 reviewer는 이번 후보 구현과 검증 설계에 참여하지 않았다. 고정 후보, 원 코드, 원문과 실행 영수증을 읽고 문제를 owner에게 전달했으며 직접 구현이나 테스트를 수정하지 않았다. 이전 axisymmetric/nuclear 보고서 판정을 이번 구현의 인증으로 재사용하지 않았다. 정확한 검토 파일·증거의 SHA256과 판정 범위는 `INDEPENDENT_REVIEW.json`을 따른다. 해시는 바이트 식별이며 과학적 타당성 자체의 증명이 아니다.

검토 중 발견한 실질적 결함은 **receiver의 background binding 누락**이었다. 종전에는 H=3.3e-17 s⁻¹, s=3.3e-18 s⁻¹로 만든 packet을 같은 가스·시각에서 임의 geometry로 ON 호출할 수 있었다. owner가 H, s와 source-birth 정규화에 따른 a=exp(Ht), β=st를 함께 검사하도록 수정했다. 변경된 7개 테스트와 native example이 통과했다. source-only 온도 항은 이제 반환된 source 원장에서 따로 계산하며, ON/OFF는 같은 geometry를 사용한다. 수정 전 영수증은 `evidence/rei_native/before_geometry_binding_fix/`에 남아 있다.

그 밖의 수정은 과도한 주장과 단계별 문서 충돌을 해소했다. 원 FS10 abundance의 정확한 복원 대신 YHe=.248의 명시적 primordial transplant를 쓰고, 단순 출력 반올림 대신 bounded numerical heat projection이라고 기록한다. 과거 MEDEA 3000 eV 후보와 raw-data 무보정 감사 문서는 최종 FS10 선택에 의해 대체된 부분을 표시한다. 손실/age 진단도 trajectory supremum이 아닌 quadrature-node 표본 추정으로 바로잡았다.

검토를 통과한 범위는 다음과 같다.

| 항목 | 판정 근거와 범위 |
|---|---|
| 실제 주입 | Leite Eq.23–24의 kinetic-energy spectrum을 전체 10 keV–1 PeV에서 정규화한다. MD14 Eq.15–16의 Salpeter SFRD와 kCC=.0068/Msun을 일관되게 사용한다. fescape=1은 시나리오다. |
| Bianchi 수송 | 일정 H,s의 massive collisionless characteristic과 exp(-3H age) proper-volume dilution이 일치한다. birth 좌표 적분에 final-angle Jacobian을 중복 적용하지 않는다. active band 밖 에너지는 CR storage다. |
| primary kernel | 실제 CRIPTIC commit의 원자 H/He 계수를 확인했다. SDCS 적분의 F2·w² 항 수정은 수학적으로 맞고 stopping moment와 일치한다. 1–4 MeV는 이번 합성의 선택 구간이며 측정 정확도 인증 구간은 아니다. |
| secondary 및 원장 | FS10 xi=.01의 종별 사건수를 사용한다. primary binding 비용을 다시 전자 에너지에 넣지 않으며, 표 안의 He photon 재흡수를 새 source로 중복 주입하지 않는다. Lyα는 excitation의 부분집합이다. |
| 수치 합성 | 다른 적분법에 의한 30개 비교의 최대 상대차 2.06e-13, 48/8/8→64/12/12 refinement의 최대 상대차 1.44e-6으로 선언된 2e-6 조건을 통과했다. 물리 계수/표는 공유하므로 독립 물리 calibration이 아니다. |
| REI 연결 | 모든 packet 수치를 compiled fixture와 대조하며 가스·시각·geometry를 검사한다. 원 ambient baryon/charge source와 기존 128ε 원장을 유지한다. OFF는 provider를 호출하지 않는다. frozen warm-HM12 경로를 바꾸지 않는다. |

native 결과의 총 온도 미분은 −6.5999996188813456e-15 K s⁻¹이며 source-only 기여는 +3.811186545594215e-22 K s⁻¹이다. 두 값을 혼동하지 않는다. 매우 작은 source를 ON−OFF로 빼면 상쇄오차가 있으므로 source 원장으로 계산한 값을 기준으로 쓴다. 실행한 evolution interval은 **0**이다.

남은 HOLD의 이유는 명확하다. 10¹⁰ s 후의 zero-initial CR snapshot에 적용한 terminal operator는 그 짧은 turn-on 안에서 실제로 침적된 인과적 역사에 해당하지 않는다. cooling·He photon delay, 공간 이동, ICS 및 누락된 proton 손실, gas feedback, arbitrary H/He fractions, 정확한 원표 YHe, 전 영역 stopping은 이번에 해결하지 않았다. 표와 수치 원장의 작은 오차는 이 물리 근사들의 오차 상한이 아니다. 별도 primary/secondary 근사 threshold를 유지하므로 `internal_power`는 provider별 사건 원장이며 하나의 정확한 원자 χ로 정의한 화학 상태함수의 미분 인증도 아니다. 전체 source baryon/전하 저장고를 닫은 것도 아니며 ambient-gas 사건 보존을 검증한 것이다.

재확인한 원전: [Leite et al.](https://arxiv.org/pdf/1703.09337), [Madau & Dickinson v3](https://arxiv.org/html/1403.0007v3), [Furlanetto & Stoever v1](https://arxiv.org/pdf/0910.4410v1), [CRIPTIC 고정 원 코드](https://bitbucket.org/krumholz/criptic/src/e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92/Src/Losses/Ionization.H). CRIPTIC 웹 뷰 직접 취득은 실패했지만 해당 commit의 실제 로컬 원 코드를 읽었다. GPL/MIT notices와 원 tar의 별도 license 미확인 상태를 유지한다. 이 판정은 push/merge 수행 영수증이나 재배포 법률 인증을 대신하지 않는다.
