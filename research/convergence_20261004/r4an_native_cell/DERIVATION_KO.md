# R4AN native 이식의 수학적 계약

수치 kernel은 a0, E_h, t_a=hbar/E_h 단위의 R4AM식을 사용한다. 물리식 K=H-i hbar D에서 H/E_h와 D*t_a의 수치값에 K_num=H_num-iD_num를 적용한다. S는 무차원이다.

첫 radial panel에서 u(0)=0이므로 F=u/r는 정확한 다항식이다. n=r_vector/r, p solid-harmonic 계수를 c_m이라 하면
sqrt(4pi) phi_p=F(c_m dot n),
sqrt(4pi) r grad(phi_p)=r F'(c_m dot n)n+F[c_m-(c_m dot n)n].
s 상태는 sqrt(4pi) r grad(phi_s)=rF'n이다. 이를 원점 chart의 r^2체적요소 및 Coulomb항과 먼저 결합한다. 비영p slope를 버리거나 strong Laplacian/전체H2를 가정하지 않는다. 일반cell은 양의 radial 분모를 유지한다.

각도다항식은 U,V의 총차수4까지 지원한다. Q=U^2+V^2, x=-k^2Q/4에서 Phi_n(x)=sum_j x^j/(j!(j+n)!)와 원R4AM의 도함수 항등식으로 mean을 계산한다. 홀수V모멘트는0, 짝수V모멘트는 (Q-U^2)^(b/2) 전개를 쓴다. Target conjugation은 harmonic상수 계수에만 적용한다. 복소 타원majorant는 native가 아니라 원Python provider 소유다.

실수구간은 [L,U]/2^256 GMP정수로 표현한다. 곱셈/나눗셈은 끝점조합에 floor/ceil, sqrt는 integer sqrt와 제곱비교로 외향반올림한다. 0포함 분모·negative sqrt·잘못된chart는 거절한다. Phi/sin/cos의 절단꼬리와 입력구간 widening을 포함한다. 서로 다른식의 상관관계를 임의로 만들어 구간을 축소하지 않는다.

Native 수치합 Q_N은 적분값 I 자체의 인증이 아니다. 동일fixture/cell/geometry/node/domain의 parent analytic error e가 주어진 때만 I in Q_N + [-e,e]+i[-e,e]를 적용한다. 이번 3fixture는 parent n=32 root구간과 e를 그대로 사용했다. 24개 실수/허수 numerical interval pair가 endpoint까지 같았지만, 포트와 부모는 같은수학/일부산술을 공유하므로 이것만 독립정확도 증명이라고 하지 않는다.

Exact u=r, R=5, a=1/8, v=0의 원점fixture에서 S=a^3/3, H=K=-a^2/2-a^3/15, D=0. 일반 고정triangle의 S=139/240,H=K=-7/20,D=0. 정확한 참값 포함성을 별도 Fraction/SymPy로 검사했다. 비상수radial/비영ETF의6point는 Cartesiangradient와80자리수치각도적분으로 확인했으며 이 단계는 numerical check이지 새hard-bound가 아니다.

Actual finite candidate, 18x18조립, 전체cell, 연속z나머지, bridge/capture/source는 미수락이다. 실제candidate에 fixture e나 S용M9를 복사하지 않는다. 실제새연산은 별도geometry/cell/entry/majorant/runtime계약이 필요하다. 상세식·역사증거·scope는 complete package의 DERIVATION_KO.md와 REPORT_KO.md에 있다.
