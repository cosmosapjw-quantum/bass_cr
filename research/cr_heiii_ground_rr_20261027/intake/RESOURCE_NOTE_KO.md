# C4 자원 환경 확인 — 제한된 read-only 관측

**결론:** CPU8(coordinator)·CPU0(worker)·CPU2(independent) 배치는 관측된 affinity와 quota에 들어간다. RAM은 launch 직전의 보수적 clean-cache 계산과 소유한 모든 process의 메모리 합산을 적용해야 하는 **조건부 채택**이다. 이번 관측만으로 실행용 자원 예약이나 512MiB 주소공간 적합성을 인증하지 않았다.

관측 시각: **2026-10-27 03:41:59 UTC**. 실제 명령, exit0 및 원문 proc/cgroup 값은 [ENVIRONMENT.json](ENVIRONMENT.json)에 기록했다. 환경 probe는 한 번 수행했고 scientific import·test·solver·affinity/limit 변경·lease 생성·process 종료는 하지 않았다.

## 정책과 실제 계약

physmath-research-loop1.3.0의 기존 main context를 재사용하고 CODING_LOOP C4 및 POLICY_INTEGRATION를 실제 읽었다. 현재 bass_cr AGENTS와 docs/HPC_ACCURACY_POLICY_KO.md는 coordinator까지 CPU/RAM에 포함하고, affinity·cgroup quota에 맞는 병렬성, library1thread, reserve, 실제 환경만을 대상으로 한 성능 서술을 요구한다.

현재 FROZEN_CONTRACT.md와 RESOURCE_SCOPE.json을 실제 읽고 SHA256로 결속했다. 새 unit은 30 CPU-s이며 controls5, primary8, independent10, plot5, misc2의 subcap과 invocation wall60s를 가진다. 실패·coordinator 비용을 포함하고 기존 H1/HeI/C23E/REC 예산을 가져오지 않는다. 두 파일은 현재 working tree의 untracked 파일이므로 local HEAD b11b2e…의 내용이라고 표시하지 않았다.

## 관측한 자원

| 항목 | 실제 값 | 해석 |
|---|---:|---|
| affinity / effective cpuset | 0–8 | 계획한8/0/2가 모두 포함됨 |
| cpu.max | 800000 / 100000 | cgroup의8 CPU equivalent 상한 |
| 노출된 core_id | CPU0→0, CPU2→2, CPU8→8 | 서로 구분되는 노출 topology; 전용 자원 또는 물리 host scaling 증거는 아님 |
| memory.max | 8,589,934,592B =8GiB | 실제 cgroup memory ceiling |
| memory.current | 8,143,036,416B | 다른 작업과 cache를 포함한 관측값 |
| raw cgroup headroom | 446,898,176B ≈426.20MiB | 512MiB+1GiB reserve를 그대로 넣기에는 부족 |
| inactive_file | 3,729,686,528B | clean-cache estimator 입력; 즉시 전용 할당 가능한 RAM으로 간주하지 않음 |
| file_dirty / file_writeback | 2,699,264B /0B | dirty/writeback credit를 피하기 위한 입력 |
| host MemAvailable | 8,179,416KiB | cgroup 제한을 대신하지 않음 |
| 현재 RLIMIT_AS / RLIMIT_CPU | unlimited / unlimited | 실행 wrapper가 계획값을 적용하고 readback해야 함 |
| 현재 지정 thread environment | 모두 unset | 실제 one-thread 설정은 아직 관측되지 않음 |

CPU quota만 비교하면 최대 세 소유 single-thread 역할을 동시에 두는 경우도8 이하다. 그러나 다른 작업의 사용량과 공유 cgroup은 남아 있으며, affinity가 허용된다는 사실은 해당 CPU가 예약되었다는 뜻이 아니다. create-only own lease는 이번 관측에서 만들지 않았다.

memory.stat에는 file=6,338,654,208B, shmem=0, file_mapped=3,031,040B도 있다. 원 계약은 “conservative clean-cache estimate”를 요구하지만 두 frozen 파일에 정확한 산식은 지정하지 않았다. 따라서 cache 전체나 inactive_file 전체를 가용 RAM으로 확정하지 않았다. 실제 estimator가 dirty/writeback·shared/mapped·unevictable 항목을 어떻게 제외하는지와 그 산출값을 launch receipt에 남기면 된다. cgroup raw headroom이 작다는 이유만으로 영구적 실행 불가능을 선언하지 않는다.

memory.events의 max51835, oom0, oom_kill0은 공유 cgroup의 누적 counter다. 이번 unit의 실행 결과로 귀속하지 않는다.

## 실행 직전에 확인할 구체 항목

- 최신 affinity·cpuset·quota와 역할별 mask8/0/2, coordinator를 포함한 실제 동시 process 수 및 own lease.
- 최신 memory.max/current·MemAvailable와 file/inactive_file/shmem/mapped/dirty/writeback/unevictable. 보수적 cache credit 산식·값과 coordinator/worker/reviewer가 실제 겹치는 단계의 aggregate peak allowance에1GiB reserve를 더한 조건.
- scientific import 전에 BLAS·OpenMP·NumExpr를1thread로 설정하고 nested/dynamic OpenMP를 끈 뒤 실제 library thread 수를 기록.
- RLIMIT_AS512MiB를 어느 process에 적용하는지 선언하고 readback. AS는 virtual address 제한이며 RSS와 같지 않다. 이번 metadata probe의 작은 RSS를 실제 SciPy worker peak로 재사용하지 않는다.
- 과거 attempt 비용·durable reservation·subcap 및 aggregate30CPU-s·wall60s. 미확정 prior cost는 UNKNOWN으로 유지하고, 취소가 필요하면 소유한 process만 다룬다.

## runtime과 수행 범위

Python3.12.14, NumPy2.3.5, SciPy1.17.0, Matplotlib3.10.8, threadpoolctl3.6.0의 설치 metadata를 읽었다. scientific module은 import하지 않았다. 현재 PATH에서 mpirun/mpiexec/gfortran은 발견되지 않았으며, 이것은 계획된 작은 Python 경로의 MPI 실행 증거나 병렬 성능 결과가 아니다.

**새 과학 실행0, test0, implementation code 변경0, remote mutation0**이다. 새 source/정책/host 변경은 없으며 메타데이터 관측 비용은 미계측으로 남긴다. CPU/RAM scaling이나 NCP64 성능 주장은 없다. 이 두 파일만 작성하고 C4 관측을 종료한다.

