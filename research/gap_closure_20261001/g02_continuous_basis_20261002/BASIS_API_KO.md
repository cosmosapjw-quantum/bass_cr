# R4X 연속 기저 후보 API

이 후보는 저장된 원래 monomial 계수로부터 만든 **별도의 함수 표현**이다. 소실된 원래 nodal 고유벡터를 복구했다고 주장하지 않는다. 원본 BASIS.npz/json, 기존 FEMRadial, native 연산자 및 production identity를 수정하지 않는다.

각 셀의 변수 s∈[0,1]에서 다음 식이 새 FP64 배열의 정확한 수학적 의미다.

`u(s) = (1-s)*L + s*R + s*(1-s)*(q0 + s*(q1+s*q2))`.

내부 shared endpoint는 오른쪽 원래 셀의 c0를 선택하고, 원점과 바깥 끝점은 정확히0이다. 원래 계수 c0…c4에서 q0=−(c2+c3+c4),q1=−(c3+c4),q2=−c4를 정확한 Fraction으로 계산한 뒤 한 번 FP64로 반올림한다. 이 bubble 반올림을 manifest에 별도 기록한다. 반올림 전에는 R4W의 affine endpoint 보정과 같은 함수이며, 실제 저장 후보는 그 반올림을 포함한다. 별도의 정규화나 고유문제 재해를 적용하지 않는다.

`build_candidate(npz_path, meta_path, output_dir, expected_npz_sha256, expected_meta_sha256)`는 원본의 두 byte SHA, 내부 identity와 행렬 binding, 모드 scalar, 배열 형상·dtype·유한성·단조 mesh를 검증한다. create-only CANDIDATE.npz/json을 쓴다. 결과는 원본 identity, 모듈·Fortran source SHA, 배열별 digest, 후보 NPZ SHA를 묶는다. 모듈 또는 kernel을 바꾸면 기존 후보를 명시적으로 다시 만들어야 한다.

`load_candidate(directory, backend='python', native_manifest=None, threads=1)`은 `tuple[ContinuousRadial]`을 반환한다. Fortran 선택 시 `native_manifest`는 NATIVE_BUILD.json 경로다. 각 모드는 l,principal_n,energy,edges,shared_endpoint_values,bubble_coefficients,reconstructed_nodal_values,original_identity,identity를 제공한다. `residual`은 **원본 메타데이터의 residual**이며 후보의 residual이 아니다. 후보 residual은 별도 진단 결과를 사용한다.

`evaluate(r)`는 임의 shape의 실수·유한·비음수 반지름에 대해 같은 shape의 `(u,du/dr)`을 반환한다. 내부 정확한 mesh boundary에서는 shared endpoint 값을 bitwise 그대로 반환하며 미분은 오른쪽 셀을 선택한다. r≥L에서는 값과 미분이0이다. 셀 사이 미분 연속성은 요구하거나 주장하지 않는다. 전체 정확한 piecewise 함수는 경계값이 이어지며 양 끝 trace가0이다.

`reconstructed_nodal_values`는 **후보의 정확한 유리수 polynomial을 j/4에서 평가한 뒤 한 번 반올림한 값**이다. 이 nodal vector와 기존 weak FEM 행렬을 이용한 residual은 유용한 독립 진단이다. 그러나 원래 고유벡터의 복구나, 재표현한 nodal interpolant와 저장 후보의 exact identity를 의미하지 않는다. 두 함수 사이의 nodal 반올림 차이를 별도로 계산해야 한다.

`exact_coefficients(mode)`는 진단 전용 Fraction monomial expansion을 반환한다. 기존 native payload로 사용하면 endpoint trace를 다시 FP64 monomial로 변환하면서 연속성 보장을 잃을 수 있으므로 legacy provider에 전달하면 안 된다. ContinuousRadial은 FEMRadial을 상속하지 않고 polynomial_coefficients 속성도 제공하지 않는다. 별도 진단 adapter만 명시적으로 허용한다.

`validate_continuous_radial(mode)` 또는 `mode.payload_fingerprint()`는 현재 배열과 scalar의 digest를 mode.identity와 비교한다. evaluate도 이 검사를 수행한다. 메타데이터·배열·source가 바뀌면 fail closed한다. native 공개 wrapper는 추가로 cell 범위·shape·dtype·s 범위·양의 h·CPU admission을 확인한 뒤 ctypes 경계를 넘는다.

`compile_kernel(output_dir, compiler)`는 strict FP64 `-O3 -fno-fast-math -ffp-contract=off -fprotect-parens -fopenmp`로 별도의 libcontinuous.so를 만든다. compiler entrypoint와 실제 f951 frontend SHA, 명령·버전·source/library SHA와 build 로그를 남긴다. OpenMP는 독립 평가점에만 사용하며 floating reduction은 없다. 호출마다 요청 thread 수와 실제 team 크기를 비교한다. SIMD evidence는 compiler가 출력한 VECTORIZATION.txt다.

실측은 `validate_evaluator.py`가 담당한다. 동일 입력의 Python/Fortran bitwise 비교, exact rational scalar 기준,1/2/4/8 thread 별 반복 wall time을 분리한다. end-to-end에는 Python 위치 탐색·메모리 할당·hash 검증이 포함된다. prelocated 측정도 ctypes·검증·출력 할당을 포함하므로 순수 kernel cycle 시간은 아니다. 현재 호스트의 결과를 NCP64/MPI scaling이나 전체 연산자·전파 검증으로 승격하지 않는다.
