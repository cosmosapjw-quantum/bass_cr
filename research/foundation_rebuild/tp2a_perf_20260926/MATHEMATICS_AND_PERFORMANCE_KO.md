# 계산 의미 보존 및 성능 설계

내부 단위 a0, Eh, ta=ħ/Eh. S_ab=<χa|χb>, H_ab=ħ²/(2me)<∇χa|∇χb>+<χa|Vχb>, D_ab=<χa|∂tχb>. source 모델, 유한 기저, Coulomb, ETF, 적분차수를 유지한다.

각 고정 거리 pair의 ring에서 rT,rP는 phi에 무관하다. 따라서 동일 radial u와 u'를 모든 m,phi에 다시 평가할 필요가 없다. s는 r^0Y00=1/√(4π), p는 고정 복소 선형 Cartesian 다항식이다. a=u/r^(l+1), a_r=(u'/r^(l+1)-(l+1)u/r^(l+2))/r 로 χ의 무위상 부분 f=a solid와 ∇f=a∇solid+a_r solid rvec를 구성한다. C++는 이 유한 다항식과 gradient, dot=-v·∇f-i v² f/2만 평가한다. basis coefficients는 Python의 기존 FEM에서 그대로 받아온다.

ETF azimuth는 기존 2π i^m J_m(κ) exp(i m φ0) moments를 그대로 사용한다. 9점은 빠른 ETF 자체가 아니라 유한차수 진폭의 복원에 사용한다. rT/rP 적분 generator와 Heron 식, support intersection을 바꾸지 않는다. TP/PT는 여섯 행렬을 독립 누적한다. D는 Hermitian으로 강제하지 않는다. raw summation grouping이 달라져 bitwise 동일성 대신 엄격한 tolerance로 원본과 비교하지만, 동일 optimized backend의 process count 변경은 node 내부 reduction을 바꾸지 않는다.

GIL은 원인의 일부일 수 있으나 NumPy 자체의 많은 native operation은 이미 GIL을 놓는다. 주된 실측 비용은 반복 평가와 작은 array 조작이었다. 그 중복을 먼저 제거하고, 남은 ring 평가만 C++17+ctypes로 옮겼다. C++ 전면 재작성/새 GPU kernel은 지금의 측정 결과로 정당화되지 않는다. worker당 BLAS1 + 외부 spawn process로 oversubscription을 피한다.

출처(소프트웨어 계약): NumPy 2.3 thread safety https://numpy.org/doc/2.3/reference/thread_safety.html ; Python 3.13 concurrent.futures https://docs.python.org/3.13/library/concurrent.futures.html ; ctypes https://docs.python.org/3.13/library/ctypes.html . 이 문서들은 성능 배수의 근거가 아니며 배수는 별도 동일-host benchmark에서 측정했다.

새 TP2A 실패: z=-6의 중앙차분 Sdot-(D+D†) 상대잔차는 최적화/원본 모두 약 2.40192e-4. 원본 대조에서 여섯 cross/full 행렬 parity를 확인했으므로 새 native/vectorization 회귀와 구별된다. 원인을 pure ETF, GIL, FEM의 물리적 부적합으로 단정하지 않는다. 경계의 기하/고정차수 적분/차분 간 일관성이라는 추가 과학 질문으로 유지한다. TP1의 -12→-10 성공은 scope 안에서 유효하다.
