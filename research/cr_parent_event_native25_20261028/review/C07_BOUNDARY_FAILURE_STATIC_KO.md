# C07 primary_v1 실패의 한정 정적 검토

**경계 fixture의 exact 표현 수리를 지지한다.** 원인은 과학 허용치나 He branch 선택의 문제가 아니라, 80자리 Decimal 문맥에서 `d=NHe/2`를 반올림한 뒤 `p+2d<=NHe`를 다시 반올림하여 판단하는 코드 경로에 있다. 실제 traceback은 이 guard의 거절을 보여 준다. 실패 당시의 정확한 operands·fixture label은 저장되지 않았으므로 특정 prefix나 rounding 방향을 실측 재현했다고 주장하지 않는다.

80자리 round-half-even의 수동 반례는 N=7+3×10^-79이다. 정확한 N/2는3.5+1.5×10^-79지만80자리 d는3.5+2×10^-79이고,2d=7+4×10^-79>N이다. 이 식은 정적 수학 설명이며 프로그램/CAS로 평가하지 않았다.

## 최소 수리

- d와 prior_d의0·1/4·1/2 fixture는 Decimal integer coefficient/exponent tuple 또는 exact terminating-rational 변환으로 만든다. 현재 D(Fraction)는80자리 나눗셈이므로 exact 변환기가 아니다.
- 유한 Decimal로 표현된 p,d,NHe를 각각 Fraction으로 들어 올려 필요조건을 정확히 판정한다. 이미 잘못 반올림한 d에 Fraction 판정만 붙이면 올바르게 계속 거절되므로 생성·판정 두 부분 모두 필요하다.
- 출력 s=NHe-p-2d 역시 같은 exact remainder에서 유한 Decimal로 직렬화한다. 경계 clipping, 허용치 확대, 전역 precision 변경이나 물리 branch 선택은 필요하지 않다.
- Native affine Y 계산의 기존80자리와 scientific tolerances는 유지할 수 있다. exact domain 판정이 나머지 수치 연산 전체의 exactness를 뜻하지는 않는다.

## 준비 결과 재사용

실제 prepare_v1의 producer는69e7068573401db41f8c37797b47e455b684979b4094424d2156c05a126bcc81이다. PREPARATION.json은 SHA da5c18c810f47d501648faf77c398f4f0f91c9da9066c7f38c196e989d2eb39f, ATTRIBUTION_ARRAYS.npz는233050 bytes·SHA1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47로 남긴다. 기존 실행 receipt와 executed source snapshot도 변경하지 않는다.

새 consumer를 위해 기존 producer equality를 지우거나 준비 파일의 source hash를 바꾸면 안 된다. 원 producer snapshot·preparation·NPZ·receipt·17 source pins와 실제 새 consumer SHA/검토된 diff를 묶은 명시적 reuse manifest를 둔다. Source fit·원 Q8 projection 생성부가 변하지 않았다는 독립 검토가 그 경로를 허용해야 하며, 다른 pin으로 바뀌면 거절한다. 준비 계산을 반복할 이유는 없다.

## 실패와 다음 승인

primary_v1은 실제 FAILED이며 worker0.154997+coordinator0.142928+tail0.05=0.347925 CPU-s를 보존한다. 관측 ledger는3.032469/40이고 all_runtime_attempts_pass=false다. root가 수리 source/재사용 계약을 심사하고 예산·새 namespace를 고정한 뒤에만 targeted controls_v2 및 primary_v2를 실행할 수 있다. 미래 성공이나 PASS 수를 이 검토에서 미리 정하지 않는다.

이번 검토는 production/reference 비작성자의 정적 원인·수리 설계 검토다. production 수정·import·compile·수치 재계산·CAS·old source/projection/RR replay는0이다. 현재 단위 하나만 유지하고 후속 단위를 시작하지 않는다.
