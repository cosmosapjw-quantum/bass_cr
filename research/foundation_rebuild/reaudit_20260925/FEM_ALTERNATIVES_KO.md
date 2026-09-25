# FEM의 대안과 이번 선택

## 결론

현재 FEM을 폐기해야 한다는 근거는 얻지 못했다. 동일 18-channel FEM basis에서 실패하던 cross integral이 새 적분으로 수렴했다. 따라서 당장의 최단 수정 경로는 **현재 basis를 유지한 적분 backend 교체**다. 그러나 향후 높은 n, 많은 continuum modes, 긴 시간구간에서 계산비용과 hard-wall 민감도가 다시 문제가 될 수 있으므로, **smooth infinite-support Laguerre L2 basis를 독립 비교 경로로 병행**하는 것이 가장 합리적이다. 두 경로가 같은 typed finite-span observable에서 비교되기 전에는 어느 쪽도 production winner로 선언하지 않는다.

다음 설명에서 '문헌상 존재'와 '이번 실제 구현'을 구별한다. 외부 문헌은 기법의 실재성과 적용 분야를 확인하는 용도다. 이번에는 해당 논문들의 단면적 데이터를 추출하거나 완전한 코드 재현을 하지 않았다.

## 1. 현재 C0 radial FEM + 경계 적응·위상 분리 quadrature

**이번 실제 구현 및 수치 확인.** 기존 radial states, energies, mesh, weak Hamiltonian을 유지한다. TP/PT 지원 영역, element/geometry breakpoint, 정확한 azimuthal Bessel moments를 이용한다. p16→20→24에서 z=-12, b2의 S/H/D relative changes가 최종 2.4e-11 이내다. 원래 p10 실패행렬과도 8e-13 이내로 일치하므로 문제를 다른 물리로 바꾸지 않았다.

장점은 기존 연구와 비교가 가장 직접적이고 이전 실패에서 원인과 수정의 대응이 선명하다는 점이다. 한계는 고차 mode와 다른 geometry의 비용, hard-wall을 가진 continuum approximation 자체의 완비성이다. 적분이 정확해졌다는 사실이 continuum representation의 정확도를 대신하지 않는다.

## 2. Infinite-support Laguerre L2 / exponential radial basis

**이번에 작은 원자 구성품을 실제 구현했다.** `repair/laguerre_reference.py`는

\[
u_{nl}(r)=\sqrt{\frac{2\zeta n!}{\Gamma(n+2l+3)}}(2\zeta r)^{l+1}e^{-\zeta r}L_n^{2l+2}(2\zeta r)
\]

를 사용한다. domain은 [0,∞), zeta=1/a0를 사전에 고정했다. mass와 Coulomb/kinetic 행렬을 weighted polynomial quadrature로 구성한다. N16/24/32, l0/1에서 spectrum을 비교했다. N32의 n≤3 최대 에너지 절대차는 약 3.79e-13 Eh이고, mass-I Frobenius 오차는 1.22e-13 이하이다. l2 원자상태도 신규 단위시험에 포함했다.

수소 1s는 zeta=1인 첫 primitive에 정확히 포함되므로 1s 성공만은 독립적인 성능 증거가 약하다. n2/n3 refinement와 mass identity도 함께 본 이유다. n4 등은 아직 더 많은 functions를 필요로 하며 결과 JSON에 모든 에너지를 남겼다. 양의 고유값도 존재하지만 이들의 energy distribution은 물리적 continuum quadrature로 검증되지 않았다.

장점은 finite-radius zero extension에서 생기는 derivative jump를 없앤다는 점이다. 원자/두 중심 exponential basis의 기존 이론과 연결하기도 쉽다. 한계는 global dense coupling, exponent scale 선택, continuum coverage, 두 중심 oscillatory integrals가 사라지는 것은 아니라는 점이다. 이 구현을 Coulomb-Sturmian의 특정 가중 정규직교 체계와 동일시하지 않는다. 아직 two-center propagation은 없다.

## 3. Gaussian AOCC 유지·개선

이 저장소의 `cr_repro/aocc.py`와 `vendor_w1r/gaussian_cartesian.py`는 기존 독립 경로다. analytic Gaussian integrals와 electron translation factors를 재사용할 수 있다는 장점이 있다. 그러나 Gaussian primitive는 Coulomb cusp를 한 함수로 정확하게 표현하지 못하고, 극단적인 exponent ladder는 Gram conditioning을 악화시킬 수 있다. 현재 s+p-only span은 n≤3 complete hydrogen basis가 아니다.

따라서 이것은 'FEM이 실패했으니 AOCC는 자동 정답'이 아니라 다른 representation의 독립 comparator다. 같은 지평, 같은 초기상태 의미, 같은 P1/P2 span과 projector로 맞춰야 한다. 이번에는 Gaussian collision을 새로 실행하지 않았다.

## 4. 높은 연속성의 B-spline / spectral-element / FEM-DVR

높은 continuity의 B-spline은 내부 knot에서 u' jump를 줄일 수 있다. 다만 **B-spline이나 FEM-DVR는 넓게 보면 여전히 finite-element/Galerkin 계열**이며, 완전히 다른 물리 solver라고 과장해서는 안 된다. hard-wall을 유지하면 마지막 경계에서의 zero-extension regularity 문제도 자동으로 없어지지 않는다.

지금 C0 basis의 동일 Hamiltonian 적분을 닫은 상태에서 바로 이 경로로 전면 변경하면 basis approximation과 quadrature 변경을 다시 혼합하게 된다. 장기 성능 후보로는 타당하지만 현재 blocker를 찾기 위한 필수 선행 단계는 아니다.

참고로 fully numerical atomic/diatomic electronic-structure 방법의 정리에는 Gaussian, Slater, numerical radial, finite-difference, FEM, DVR의 서로 다른 장단점이 논의된다. 이 문헌의 정적 Hartree–Fock/DFT 결과를 이동 핵 충돌 검증으로 전용하지 않는다. [R1]

## 5. Coulomb-wave DVR + partial waves

Coulomb 함수에 맞춘 DVR는 원점과 continuum radial wave를 함께 표현하기 위한 후보이다. Peng–Starace는 강한 레이저장 속 원자 ionization에 이 경로와 Arnoldi 전파를 사용했다. 이 결과는 Coulomb radial representation이 실제로 사용 가능한 방법이라는 근거이지 현재 moving two-center collision의 벤치마크는 아니다. [R2]

단일 중심 partial-wave expansion에서는 두 번째 이동 Coulomb singularity와 translation/각운동량 절단이 새로운 병목이 될 수 있다. 두 중심 또는 moving coordinate를 쓰면 기저미분/metric 처리를 다시 검증해야 한다. 따라서 이 경로는 radial 대안이지 S/H/D 전체를 즉시 제거하는 해법이 아니다.

## 6. Two-center basis-generator method (BGM)

Leung–Kirchner는 semiclassical two-center BGM으로 proton-H의 excitation, capture, ionization을 1–300 keV에서 다뤘다. 사용자가 다루는 물리계와 직접적으로 겹치는 독립 방법이라는 점에서 외부 comparator 후보 중 우선순위가 높다. [R3]

다만 이번에 확인한 것은 원 논문의 서지·초록이며, 세부 pseudo-generator 또는 실험과의 비교값을 이 저장소에 이미 이식했다는 뜻은 아니다. 기존 model/observable contract와 충돌하지 않는지 읽고 맞추는 별도의 작업이 필요하다.

## 7. Wave-packet continuum discretization

이는 '격자 대신 다른 연산자를 택한다'는 문제와 달리 continuum을 어떤 유한 상태 집합으로 근사할 것인가의 대안이다. Coulomb continuum을 energy bin으로 packet화하면 원하는 에너지 분포를 설계할 수 있지만, packet width, long-range tail, rearrangement couplings와 완비성의 검증은 남는다. 지금의 수치 적분 실패를 해결하지 않은 채 basis까지 바꾸면 원인 구분이 다시 어려워진다.

두 중심 continuum 배치에 관한 문헌에서 서로 다른 truncation의 수렴 속도와 spurious structure에 관한 결과가 있었으므로, 특정 center allocation을 보편적인 정답으로 단정하지 않는다. 작은 100 keV/u pilot의 수치 적분을 확보한 뒤 물리적 basis completeness 연구에 포함한다. 문헌상 가능성이 있다는 이유만으로 '새로운 의무 audit gate'를 끝없이 추가하지 않는다.

## 8. Fourier–Galerkin / pseudospectral / adaptive real-space

원래 GPU TDL과 최대한 독립적으로 wavefunction을 표현할 수 있다. 이전 CP3의 exact Fourier-Galerkin 진단은 sampled Coulomb보다 좋은 원자 에너지와 translation covariance를 보였지만, spherical cutoff/periodized potential이었다. 원래 full-space Coulomb과 같은 Hamiltonian이라고 취급하지 않는다.

현재 B3 350×300×600에서 순진한 2n-1 circulant embedding의 complex128 배열은 약 7.51 GiB 하나가 필요하며, 세 배열만으로 약22.53 GiB다. 이는 알고리즘적 메모리 산정이며 현재 GPU memory 측정이 아니다. GPU를 바꾸거나 큰 full run을 먼저 실행하는 것이 mathematical representation mismatch의 해결책은 아니다.

## 선택과 종료 기준

현재 권고는 ① 수정된 FEM cross integral을 full S/H/D에 일관되게 통합, ② 동일한 finite-span pilot에서 smooth Laguerre 또는 기존 AOCC와 비교하는 두 경로다. 정확한 적분이 확보된 뒤에도 geometry당 비용이 물리적 pilot에 지나치게 크거나 basis convergence가 개선되지 않으면 smooth global basis/BGM 경로를 주전략으로 승격한다. 이 결정은 아직 실측하지 않은 collision 정확도나 GPU 속도를 근거로 미리 확정하지 않는다.

## 문헌과 확인 범위

[R1] S. Lehtola, *A review on non-relativistic fully numerical electronic structure calculations on atoms and diatomic molecules*, IJQC119,e25968 (2019), arXiv:1902.01431v2. 서지·초록 확인. https://arxiv.org/abs/1902.01431

[R2] L.-Y. Peng, A. F. Starace, *Application of Coulomb wave function discrete variable representation to atomic systems in strong laser fields*, JCP125,154311 (2006). 저자 기관 원문 소개/초록 확인. https://digitalcommons.unl.edu/physicsstarace/99/

[R3] A. C. K. Leung, T. Kirchner, *Proton impact on ground and excited states of atomic hydrogen*, EPJD73,246 (2019), arXiv:1907.08234v2. 서지·초록 확인. https://arxiv.org/abs/1907.08234

[R4] NIST DLMF10.12, Jacobi–Anger expansions. 실제 방위각 integration 유도에 사용. https://dlmf.nist.gov/10.12

[R5] SciPy1.17.0 `roots_laguerre` 공식 문서. 이번 실행 환경의 weighted polynomial integration contract 확인. https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.special.roots_laguerre.html