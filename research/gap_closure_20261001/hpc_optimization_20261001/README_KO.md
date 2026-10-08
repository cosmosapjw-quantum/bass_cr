# R4S: NCP64 정확도 보존 HPC 구현

기존 s+p angular contraction의 별도 Fortran/OpenMP/SIMD backend와 OpenMPI task queue다. 이전 C++ source, 기존 quadrature·batch 순서, G02/G03 executor·승인·cache identity는 보존했다. 일반 복소 계수는 기존 C++ 공식으로 fallback하고, 사용 빈도가 높은 real Cartesian 계수 경로만 새 Fortran으로 계산한다. Python adapter는 기존 `exact_cross.cross(..., kernel=...)` seam에 연결할 수 있지만, 새로운 backend가 옛 source/native identity를 흉내 내지 않는다.

## 실제 구현

- `native/moment_kernel_real.f90`: channel pair8개씩 thread별로 소유한다. 각 output의 u 누적은 원 순서 그대로이며, 독립 pair lane만 SIMD 처리한다. coefficient·velocity dot·geometry invariant를 재사용하고 거대한 point×pair 기여 텐서는 만들지 않는다.
- `native/generate_lane_arithmetic.py`: 원 복소 연산 tree를 실수부·허수부 단계로 전개한다. `--check`가 체크인된 Fortran과의 일치를 확인한다.
- `kernel.py`, `build_native.py`: FP64, no-fast-math, no-reassociation, FMA contraction off, source+library 해시 확인. 완전한 library manifest 없이 native code를 로드하지 않는다. 객체별 thread 설정을 호출 직전에 복원한다.
- `mpi_queue.py`: coordinator의 단일 전역 예산을 raw call 전에 소비한다. query 전체 ladder는 같은 worker에서 순서대로 처리한다. 결과는 계획 순서로 모으며 floating MPI reduction은 없다. 실패·timeout과 소비된 예산을 보존한다.
- `resource_profile.py`: affinity CPU ID, 실제 core/SMT, cgroup CPU quota·memory limit·현재 가용 RAM, rank0와 여유 메모리를 포함한다. MPI rank별 실제 affinity는 native load 전 별도로 검증한다.

## NCP에서 실행할 명령

필요한 runtime은 Python3, NumPy, mpi4py, GNU C++/Fortran compiler, OpenMPI다. 이번 로컬 검증은 Python3.12.14·NumPy2.3.5·GNU13.3·OpenMPI5.0.11을 사용했다. OpenMPI4의 `vader`와5의 `sm` 명칭은 버전별로 선택하며 실제4.x 환경은 여기서 실행하지 않았다. Ubuntu 패키지로 준비할 경우 관리자가 `gfortran openmpi-bin libopenmpi-dev`를 설치하고 기존 Python 환경에 `numpy mpi4py`가 있는지 확인한다. 기존 환경을 불필요하게 업그레이드하지 않는다.

최종 전달 기록의 정확한 commit을 checkout한 repo root에서:

```bash
export OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1
python research/gap_closure_20261001/hpc_optimization_20261001/resource_profile.py
python research/gap_closure_20261001/hpc_optimization_20261001/run_validation.py \
  --native-arch --out /mnt/bass_r4s_ncp_validation
```

출력 디렉터리는 새 경로여야 한다. 이 명령은 새 backend만 빌드·검증하고 synthetic 입력을 벤치마크한다. 실제 B0 operator/transport를 실행하지 않는다. NCP에서는 기본 코어 바인딩 검사를 그대로 유지한다. container가 CPU 바인딩을 거부하는 경우에만 별도의 `--synthetic-unbound` 경로가 있으며, 그 결과는 binding PASS나 NCP 성능 증거가 아니다.

직접 build만 하려면 `build_native.py --out NEW_BUILD --native-arch`를 사용한다. 이어 `BASS_HPC_BUILD=NEW_BUILD python -m unittest discover -s research/gap_closure_20261001/hpc_optimization_20261001 -p 'test_*.py' -v`로 테스트한다. `NEW_BUILD`에는 절대 경로를 권한다. 누락된 Fortran build는 native 테스트 오류이며, MPI가 없는 skip 결과도 통합 PASS로 인정하지 않는다.

##64 CPU 사용 전략

`NCP64_PROFILE.json`의64×1,32×2,16×4,8×8은 비교 후보이며 최적값이 아니다. 많은 query는 query당1~2 thread와 많은 MPI ranks를 먼저 비교한다. 적은 query는 사용하지 않을 rank를 줄이고 커널 OpenMP를 사용한다. 현재9×9 행렬은11개 tile이므로 inner64 thread는 비효율적이다. rank0는 coordinator이며 MPI64 ranks는63 compute workers다. 64 vCPU가32 physical cores인 서버는 자동으로64 physical cores로 취급하지 않는다.

128GiB 가용 환경에서는 최소16GiB를 남기고 per-rank peak RSS를 측정한다. resource planner의 RSS 값은 사전 추정이며 OS hard limit 자체는 아니다. NUMA/binding과 실제 peak RSS는 NCP에서 기록한다. 다른 CPU용 `-march=native` binary를 재사용하지 않는다.

## 정확성·한계

정확성 기준은 deterministic synthetic suite에서 strict C++와 uint64 bit pattern의 동일성이다. static/moving target, 비정방 shape, tile 나머지, nonzero accumulator, thread 변경 및 독립적으로 계산한 상수 s-orbital limit을 포함한다. 이는 테스트한 입력의 구현 동등성 증거이며, 모든 입력에 대한 형식 증명이나 실제 B0 operator error certificate는 아니다.

MPI queue는 trusted callback을 위한 cooperative scheduler다. callback 자체의 과학적 qualification, 파일 provenance, source admission을 대체하지 않는다. 기존 G02의66query/726attempt/8worker와 G03의2query/22attempt/2worker를 자동으로 확장하지 않는다. 새 backend로 실제 계산할 때는 같은 scientific tolerance를 가진 새로운 exact-source/native/resource 계약이 필요하다.

새19개 테스트, vectorization report, kernel benchmark 및 hybrid MPI 결과는 `evidence/`를 따른다. 기존 연구·문헌 DB v5, R4R 수학적 인증과 capture/production gate는 이 패치로 변경하지 않는다. 이후 연구 구현의 기본 정책은 repo의 `AGENTS.md`와 `docs/HPC_ACCURACY_POLICY_KO.md`에 기록했다.
