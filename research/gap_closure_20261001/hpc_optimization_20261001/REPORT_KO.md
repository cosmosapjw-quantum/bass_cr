# R4S NCP64 성능 최적화 결과

새 Fortran/OpenMP/SIMD kernel과 OpenMPI queue를 구현했고, 이후 bass_cr 연구 코드의 기본 HPC 규칙을 AGENTS.md 및 docs/HPC_ACCURACY_POLICY_KO.md에 기록했다. 정확한 이전 기준은 commit82cac33a2ad1b938db6a89d63a8ac0ac8a2414a1이다. 변경은 새 HPC 경로와 지침뿐이며 기존 물리 executor·문헌 DB·수학 인증을 대체하지 않는다.

## 실제 성능 측정

동일한 artificial1024-point9×9 moving-target 입력과 같은 strict-FP 옵션으로 C++/Fortran을 비교했다. 7회 측정, 각10call의 median이며 Python 입력 검증·wrapper 비용도 포함한다. 호스트 CPU는 AMD EPYC9V74로 표시되지만 이 작업의 CPU quota는8, RAM 한도는8GiB다. NCP64-core 측정이 아니다.

| 빌드 | C++1thread | Fortran1thread | Fortran8threads | 속도비1thread /8threads |
|---|---:|---:|---:|---:|
| portable | 6.803ms | 1.851ms | 0.736ms | 3.67× / 9.24× |
| -march=native | 5.995ms | 0.875ms | 0.399ms | 6.85× / 15.01× |

portable의 static/moving 주요 루프에16-byte SIMD가 실제 생성됐고, native-arch 후보에는32/64-byte vector 경로가 생성됐다. 이 값은 kernel 성능이며 전체 operator 생성·시간 전파·NCP64 전체 job의 속도비를 뜻하지 않는다. 먼저 phase/geometry/radial 전처리와 I/O를 포함한 실제 workload를 프로파일링해야 전체 성능을 알 수 있다.

## 정확성 및 병렬 실행

새19개 테스트는 skip0으로 통과했다. native-arch flag 변경에 영향을 받는 kernel7개도 다시 통과했다. 선언된 입력들의 결과는 strict C++와 **uint64 bit pattern이 동일**하며 portable/native build 사이에도 benchmark 결과 hash가 같다. static/moving, 비정방 shape, 나머지 tile, nonzero 초기 accumulator,1/2/4thread, complex fallback, 잘못된 입력·manifest를 포함한다. 원소별 u 누적 순서·batch 경계·FP64·기존 scientific tolerance를 유지했다. 모든 실수 입력에 대한 형식적 등가성 증명이나 B0 물리 오차 인증을 주장하지 않는다.

OpenMPI의1/2/4rank 순서·단일 전역 예산·잘못된 ladder·worker failure·timeout을 실제 subprocess로 검증했다. 추가4ranks×2threads(3compute workers+1coordinator) 통합에서24개4096-point 작업의 결과 hash가 직렬 기준과 전부 같았다. queue wall=0.118875s, 직렬 reference=0.731814s로 약6.16×다. 이는 한 번의 기능 통합 timing으로, 반복 kernel benchmark와 구별한다. 합산 peak RSS 상계는153.0MiB였으며 실제 물리 workload의 per-rank RSS를 대신하지 않는다.

## 실행환경 한계와 보존된 실패

이 container는 PRTE의 hwloc_set_cpubind를 거부했다. 기본 binding 검사 실패를 보존했고, 전체8 CPU thread budget을 유지하는 명시적 **synthetic-only unbound** 경로로 MPI/Fortran 결합만 검증했다. NCP에서는 기본 바인딩을 유지하고 실제 rank CPU masks가 계획한 CPU IDs 안에 있으며 서로 겹치지 않는지 native load 전에 검사해야 한다. NCP binding 및64-core scaling은 UNVERIFIED다. 승인 기준을 완화하거나 실패를 PASS로 바꾸지 않았다.

설치 초기 apt의 권한 전환 실패와 Fortran 환경변수의 C++ compiler 간섭도 별도 runtime 문제로 보존했다. 검증한 공식 패키지를 scratch에만 풀고 Fortran 전용 wrapper로 환경변수를 제한하여 컴파일을 완료했다. 시스템 전역 설정이나 접근 제어를 바꾸지 않았다. 전달 source는 정상 NCP GNU/OpenMPI 설치에서도 빌드하도록 구성했다.

## 다음 연구의 구현 기준

독립 query가 많으면 MPI를 먼저 사용하고 query 내부 qualification ladder는 원 순서를 유지한다. query가 적으면 Fortran pair tile 병렬화로 접근한다. 후보64×1/32×2/16×4/8×8의 실제 우열은 동일 workload와 measured RSS로 정한다. rank0 비용·실제 SMT topology·cgroupquota·NUMA와 메모리 여유를 포함하고 BLAS는1thread로 제한한다. 현재81pair는11tile이므로 inner64thread를 사용하는 것은 유효한64코어 활용이 아니다.

NCP 검증 명령과 구현 API는 README_KO.md에 완성했다. cloud Codex는 새 기능을 다시 구현할 필요 없이 정확한 commit을 확인하고 제공된 validation runner를 실행하면 된다. 기존 G02/G03의 source/native 승인과8/2worker 한도를 새 backend에 자동 상속하지 않는다. 실제 B0 계산에는 별도 source/native/resource 계약이 필요하다. 이번 physical query·전파는0회이고, capture=false/production=HOLD/all_bound=OPEN/b_grid=NO_GO를 유지한다.
