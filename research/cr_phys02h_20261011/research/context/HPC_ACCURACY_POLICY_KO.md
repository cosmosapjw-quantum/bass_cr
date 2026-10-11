# 정확도를 보존하는 NCP64 연구 코드 기본 규칙

사용자 지시 적용일: 2026-10-01. 앞으로 bass_cr 연구 코드의 구현·성능 검토에는 아래 기준을 기본 적용한다. 목표는 64 CPU·128GB NCP의 실제 topology와 자원 한도 안에서 계산 시간을 줄이는 것이다. 광고된 CPU 수를 물리 코어 수로 간주하지 않는다.

계산은 독립 query/parameter/적분 구간, compiled kernel, SIMD의 계층으로 나눈다. 많은 독립 query는 OpenMPI로 배분하고 각 query의 qualification ladder는 원 순서로 유지한다. query가 적으면 독립 행렬 원소를 Fortran/OpenMP로 병렬화한다. 모든 계층을 동시에 최대 thread 수로 실행하지 않는다. Python은 admission·계획·캐시·증거·작은 행렬 조립을 맡고 계산량이 큰 검증된 루프를 Fortran/C ABI로 보낸다. 수학적으로 다른 알고리즘을 단순 성능 패치에 섞지 않는다.

FP64·기존 quadrature·기존 tolerance·batch 경계·원소별 누적 순서를 유지한다. `-Ofast`, `-ffast-math`, 부동소수 재결합, mixed precision과 비결정적인 MPI floating reduction을 기본 금지한다. FMA는 이번 backend에서 `-ffp-contract=off`로 고정한다. 순서 변경/새 근사/정밀도 변경은 별도의 오차 분석과 독립적인 정확도 계약 없이는 채택하지 않는다. 기존 C++ 기준 구현은 보존하고 성능 개선판을 구별되는 source/native/context identity로 기록한다. synthetic parity를 실제 operator·trajectory·capture 인증으로 승격하지 않는다.

OpenMPI rank 수×OpenMP thread 수는 affinity·cgroup quota·실제 topology로 허용된 CPU 수 이하여야 한다. BLAS/NumExpr는 기본1 thread, OpenMP nested parallelism은 끈다. 초기 비교 후보는64×1,32×2,16×4,8×8이지만 최적값은 같은 workload의 wall time과 peak RSS로 결정한다. MPI queue의 rank0 coordinator도 core와 RAM 예산에 포함한다. 현재9×9 커널은8-pair tile11개이므로 내부64 thread를 주어도64개가 모두 일하지 않는다.

128GiB 사용 가능 환경에서는 최소16GiB를 OS·orchestration·buffer 여유로 둔다. 실제 한도가 더 작으면 비례 reserve와 최소1GiB를 적용한다. per-rank RSS×rank 수를 사전 계산하고, pilot의 peak RSS·page fault·I/O를 확인한다. NUMA first-touch와 rank binding을 적용한다. `-march=native`는 실행할 노드에서 재빌드한 후보에만 사용하고 해당 노드의 정확도 검증을 통과해야 한다.

전체 raw-attempt budget은 coordinator 한 곳에서만 소비한다. 각 call 전에 durable reservation을 남기며 rank별로 동일 예산을 복제하지 않는다. 실패와 timeout은 보존하고, 사용된 승인을 자동 재사용하지 않는다. query별 payload를 분리하고 scientific result는 계획 순서로 모은다. 운영 timestamp·PID·reservation 도착 순서는 scientific byte identity와 구별한다.

새 최적화의 완료 조건은 (1) 같은 입력에서 정확성 검증, (2) 실행된 SIMD/병렬 경로의 증거, (3) 같은 workload·반복 측정·분산을 담은 속도 비교, (4) resource/failure 테스트, (5) 실제로 측정한 환경과 미검증 NCP scaling의 구분이다. 소스/환경이 바뀐 영향 범위만 재검증한다. NCP에서 아직 실행하지 않은64-core speedup을 외삽하여 완료로 보고하지 않는다.

구현: `research/gap_closure_20261001/hpc_optimization_20261001/`. 이 규칙은 이후 이 프로젝트 연구에 지속 적용한다. 기존 G02/G03의 물리 실행 승인을 자동 확장하지 않으며, backend 교체와64-core 물리 실행에는 새로운 정확한 source/native/resource 계약이 필요하다.

참조: [OpenMPI5 process mapping](https://docs.open-mpi.org/en/v5.0.10/man-openmpi/man1/mpirun.1.html), [GNU Fortran code generation](https://gcc.gnu.org/onlinedocs/gfortran/Code-Gen-Options.html), [GCC optimization options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html). 설치된 compiler/MPI 버전과 실제 실행 결과가 해당 build의 기준이다.
