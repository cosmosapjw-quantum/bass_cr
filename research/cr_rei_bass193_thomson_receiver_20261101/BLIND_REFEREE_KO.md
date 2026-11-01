# 적대적 자기 검토 (one bounded same-author pass)

1. **전체 CMB optical depth로 오인 위험 (BLOCK scientific claim).** 적분은 z=20→2만 포함하며 z<2와 recombination residual 등을 포함하지 않는다. 수정: 파일·축·논문 표현 전체를 finite-window contribution으로 한정. Full CMB tau NOT_COMPUTED.
2. **static star vs saved의 해석 (BLOCK).** `xe_star`는 BASS193의 정적평형 closure이고 독립적으로 진화시킨 우주론이 아니다. 4.4115% 차이는 모델 closure effect이지 추정 오차/관측적 유의도가 아니다. 수정: label과 interpretation 한정.
3. **whole21 vs H/He (FIX in claim).** HHe 전자밀도와 `xe_saved`는 매우 가깝지만 정확히 같지 않다. 실제 21-charge plasma `xe_saved`로 primary tau 계산, HHe는 별도 component crosswalk.
4. **source identity (PASS scoped).** Private PR311 ZIP 전체 SHA256, member 3 SHA256, 원본 public 192-row Git blob SHA1 모두 독립적으로 확인. 원본은 GitHub 새 PR에 싣지 않는다.
5. **수치 후처리 (FIX).** 192개 우측 끝점만 쓰는 기존 witness와 양끝점 사다리꼴 구적의 차이 약 0.62%. 구적차를 물리 오차 상계로 부르지 않고 둘 다 저장.
6. **표현 오류 (FIX).** Cumulative tau is tied to interval high-z boundary; plot initially used low-z endpoint. x-axis changed to high-z. Probability density uses bin midpoint. (새 과학 방정식 수정 없음)
7. **CSV 재읽기 오차 (FIX).** pandas 기본 파서가 `%.17g`의 마지막 비트를 다르게 읽어 192 중 130개 요소의 극미량 상대 불일치를 야기. Round-trip readback parser로 테스트 교정. 수치 물리 모델 입력/결과 바이트는 보존.
8. **소유자와 DAG (BLOCK canonical promotion).** REI 최초 full coupled interval, source-compatible Bianchi background, BASS Thomson screen, z<2/tail integration 미완료. 본 결과는 RUX10용 **실제 source-backed scalar receiver precursor**일 뿐 RUX10 또는 REI 88-node PASS가 아니다.

결론: SOURCE_OWNED_FINITE_WINDOW_SCALAR_RECEIVER_NUMERICALLY_CHECKED, canonical delta0, independent-author R6/C9 NOT_RUN, native subagent NOT_RUN, production HOLD. 추가 재귀 감사 금지. 다음 실물 작업은 첫 canonical REI interval 또는 BASS geometry owner에게 이 소비자 contract 전달.
