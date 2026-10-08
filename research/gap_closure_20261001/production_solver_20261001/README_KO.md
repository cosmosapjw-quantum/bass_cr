# R4U: 물리 연산자에서 재개 가능한 전파기까지

이 구현은 기존 B0 18채널 수치 모형을 실행하는 경로를 연결한다. 실제 산란의 오차 인증이 완료된 production solver라는 뜻은 아니다. 원래의 시간 구간·기저·연속 tail 오차 검증이 남아 있어 production=HOLD, capture=false를 유지한다.

## 연결 구조

1. `provider/precompute_cli.py plan`이 입력, native build, 소스, 정확한 query 시간, 원래 qualification ladder, CPU/RAM, 전체 시도 수와 시간 제한을 고정한다.
2. `run --execution-sha256 ...`이 해당 실행 계획만 실행한다. 각 rank의 CPU 배치를 확인한 뒤 native kernel을 로드한다. MPI에서는 rank0가 전체 raw-attempt 예산을 단독 관리하고 완전한 query ladder를 worker에 배정한다.
3. `provider/hpc_provider.py`가 R4S Fortran/OpenMP 커널을 기존 full S/H/D 조립기에 연결한다. 같은 중심 order20과 cross 적분 규칙·허용오차·FP64 누적 순서는 그대로다. C++ 기준 구현은 별도 backend/context로 남긴다.
4. 통과한 query의 원시 cross와 최종 full operator 일치까지 확인한 뒤 cache를 발행한다. 전파기는 정확히 계획된 시간의 검증된 cache만 읽는다.
5. `runtime/solver_cli.py propagate`가 기존 midpoint exponential recurrence를 실행하며 매 step의 whitened state를 저장한다. 중단 후에는 소스·환경·초기 상태·cache·checkpoint chain을 검증하여 새 출력 폴더에서 이어간다.

출력은 소스 폴더 밖의 새 경로에만 쓴다. 기존 실패·checkpoint·결과를 덮어쓰거나, cache miss를 숨기거나, 예산을 자동 재발급하지 않는다.

## 이 구현이 보존하는 수학

`S,H,D`와 시간 grid 연산은 기존 구현을 재사용한다. `c0`는 사용자가 명시적으로 제공하며 처음 한 번만 metric 정규화한다. 작은 18×18 행렬 지수는 BLAS1로 실행한다. MPI floating reduction은 사용하지 않는다. 저장되는 선택 부분공간 population은 finite-span 진단값이며 capture로 승격하지 않는다.

독립 CF4/DOP853 검증, 더 긴 incoming/outgoing window, B1–B3 및 높은 각운동량 기저, 물리 complex interval assembler와 연속 오차 인증은 이 연결 작업만으로 완료되지 않는다. 기존 N1536 ±12 결과의 정확도를 새 backend·새 초기 상태·새 시간 구간에 이전하지 않는다.

## 로컬 실제 계산의 범위

`ACCEPTANCE_SCOPE.json`에 실행 전에 고정한 B0 z=32→32.02, midpoint2 step, 명시적 e0 초기 상태로 연결을 점검한다. 이 초기 상태는 저장된 충돌 tail 상태가 아니다. 첫 시간에서 새 C++ 실행과 Fortran 실행의 full/raw 행렬을 비교한다. 전파의 전체 실행과 1 step 후 재개를 비교한다. 결과와 실패는 각각 별도 실행 증거에 남긴다.

로컬 host의 실제 CPU quota/RAM을 사용한다. NCP64 scaling, 반복 benchmark의 speedup, MPI 물리 실행을 로컬 단일-rank 실행으로 주장하지 않는다. 컨테이너의 MPI launcher root 보호는 우회하지 않는다.

## NCP 실행 순서

일반 사용자로 접속한 NCP 노드에서 R4S `resource_profile.py`로 실제 affinity·cgroup quota·RAM을 읽는다. `build_native.py --native-arch`로 해당 노드의 후보를 만들고 정확성 비교부터 수행한다. 출력한 `BUILD_HPC.json`과 새 input/source identity로 `precompute_cli.py plan`을 다시 만든다. 로컬 manifest와 checkpoint는 새 host에 자동 이전하지 않는다.

처음에는 동일 workload의 64×1, 32×2, 16×4, 8×8 중 실제 자원 한도에 맞는 조합을 비교한다. coordinator도 rank/메모리에 포함하고, 각 rank의 실제 RSS에 기반해 reserve를 남긴다. 현재 작은 커널의 OpenMP 병렬 폭에는 한계가 있으므로 많은 독립 query는 MPI로 분산한다. 수치 parity와 반복 wall-time 분산을 함께 보고해야 최적 조합을 선택할 수 있다.

구체적인 CLI 계약은 `provider/EXECUTION_CONTRACT.md`, cache와 재개 의미는 `runtime/RUNTIME_CONTRACT.md`에 있다. 구현·합성 테스트·실제 물리 operator·실제 trajectory·과학적 gate를 서로 다른 증거로 기록한다.
