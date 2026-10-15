# SOURCE07 C8 적응형 q-grid 공급자 인계, 별도 owner 승인 전용

현재 SOURCE07 owner head는 2026-10-15 약12:56 KST `a950711f9cf57eea065d2ce30b15aba54b60bf53`. 기존 C7 실제 z20/z4 two-age q-ray 실험에서 pooled N/U He보다 HI가 먼저 오차를 보인 것과 고정-q support만으로 age shape을 복원할 수 없음은 확인됨. AX08 IN_PROGRESS, AX11/AX12 PENDING. 원래 `axbi_driver.rs`,`axbi_sources.rs`,`atomic_provider.rs`,`bianchi_i.rs`, OLD49/guard51 상태와 source identity는 수정하거나 재해석하지 않는다.

새 `adaptive_q.py`는 SOURCE07 C8의 완성된 adaptive grid가 아니다. 새 source quadrature에서 직접 얻은 양의 sample packet이나, 별도로 진화되어 provenance와 양성·moments가 검증된 child-bin moment가 실제로 제공되었을 때만 정확한 dyadic partition과 6개 종별 한 단계 moment-envelope 상·하한을 재평가한다. 원래 부모 N,U만 주어졌으면 기존 2-moment envelope는 유지하고 cell split을 **HOLD**한다.

추천 실제 owner trial: 새 versioned q-grid numerical source에서 하나의 q-ray·한 current proper clock·한 source/age component를 고정한다. 실제 k_i 방향과 R,J_Omega는 SOURCE07 owner가 계산하고 source Jacobian은 한 번만 적용한다. 13.6/24.59/54.42eV fit cutoff와 각 물리 결합에너지는 별도 장부. Child moment oracle을 얻고 각 energy bin마다 fraction-exact mass/first moment를 기록한 다음 HEI target 또는 다종 budget 기반 refinement를 실행한다. Equal-cell-count uniform grid, packet oracle 종별 photoevents/photoheat, feedback-gas coupled short source identities를 별도로 비교한다. Error goal 미달은 명시적으로 `HOLD_PRECISION_TARGET`; global cosmological EoR 오차 인증이 아니다.

조건부 예비 수치: 원 source GL sample N96 adaptive HeI width1.67212e-10 vs uniform1.17761e-9 count/H; N128 adaptive5.48788e-11 vs uniform6.73281e-10. 제조 hardened N96 adaptive3.50586e-11 vs uniform7.32052e-11. 부모와 다른 추가 packet corpus를 가정하므로 SOURCE07 기존 N/U 정확도와 동일 조건이라고 확대하지 않는다.

Owner C8_A age memory 보관, C8_B shape bounds, C8_C variable proper neutral gas, C8_D matched driver는 별도 의무다. fixed-q primary branch 보존; CR/RCT/HH OFF. 실제 owner source/checkpoints/active jobs 변경 0회.
