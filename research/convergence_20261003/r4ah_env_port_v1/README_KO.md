# R4AH environment adapter v1 — PREPARED_NOT_AUTHORIZED

원 R4AH runtime을 새 경로에 보존한 파생본이다. 과학 연구의 새 단계나 PASS가 아니다. 이 경로의 변경은 실제 프로세스 cgroup-v2 자원 관측과 prepare 이후 hierarchy 변경 거절에 한정한다. 원 수치 kernel, candidate, geometry/epoch, quadrature, 허용오차, 자원 기준은 변경하지 않는다.

원 `observe_environment()`는 `/sys/fs/cgroup` root의 제한 파일을 요구했다. 이번 실행 프로세스는 `/user.slice/user-0.slice/session-1.scope`에 속해 있다. 해당 leaf와 `user-0.slice`, `user.slice`에서 CPU/memory 제한과 사용량을 읽을 수 있다. global root의 제한 파일 부재를 시스템 전체의 v2 부재로 해석했던 이전 보고를 이 실제 진단으로 교정한다. 이전 실패 기록은 수정하지 않는다.

새 `resource_reader.py`는 membership과 mountinfo의 mount root/mountpoint를 함께 해석한다. escape를 해석하고 traversal, 다중 매핑, v1/hybrid, 가려진 조상을 거절한다. 실제 initial namespace의 kernel task PID2/kthreadd/Kthread=1/root membership과 self/PID1/PID2의 PID·cgroup namespace 일치, 전체 mount root `/`를 함께 확인할 때만 global root의 controller 예외를 인정한다. PID1과의 일치만으로는 승인하지 않는다. 이 보수적 증거를 관측할 수 없는 container/namespace는 `UNRESOLVED_RESOURCE_HIERARCHY`로 차단하며 별도 계약이 필요하다.

leaf부터 global root까지 모든 조상을 기록한다. CPU는 유한 quota/period의 최소와 실제 affinity를 적용한다. RAM은 host MemAvailable 및 각 유한 memory.max와 그 cgroup의 memory.current를 뺀 headroom의 최소다. non-root의 누락·권한 오류·잘못된 값은 차단한다. 명시적인 `max`와 증명한 global-root 예외를 구분하며 누락 current를 0으로 채우지 않는다. 관측 전후 membership·mountinfo·namespace·affinity가 달라져도 차단한다. 향후 실제 run 직전 관측에서도 prepare 당시 hierarchy binding과 비교한다.

원 정책은 workers=1..3, coordinator CPU 1개 reserve, worker당 536870912 bytes, coordinator/reserve 1879048192 bytes, parallel_nodes=1, point wall=1800초다. 3-worker 필요량 3489660928 bytes, 1-worker 2415919104 bytes를 그대로 유지한다. LD_PRELOAD/LD_AUDIT/LD_LIBRARY_PATH도 원대로 거절한다. 실제 관측은 전용 코어 확보나 64-core 성능 보장의 증거가 아니다.

원 lock은 contracts/ORIGINAL_SOURCE_INPUT_LOCK.json에 보존한다. runtime/r4ag/SOURCE_INPUT_LOCK.json은 새 identity다. 원 49개 pin 중 runtime_contract.py만 resource adapter로 변경했고 48개는 바이트동일하다. resource_reader.py를 추가해 새 runtime lock은 50개 pin을 가진다. 숫자 kernel과 입력을 재구현하거나 원본 lock·archive·소비한 실패 session을 수정하지 않았다. R4AM의 318-file patch도 다시 적용하지 않았다.

검증은 새 reader 20개 시험, runtime seam/자원 guard 5개 시험, prepare된 계약의 실행 전 membership/namespace/mount 변경 거절 3조건이다. RED_RESOURCE_READER는 원 fixed-root 정책을 옮긴 임시 baseline으로 정상 non-root 관측 실패를 기록한다. 추가 유효 경로가 원 guard에서 거절된 오류도 원문을 보존한다. RED_RUNTIME_PORT는 실제 프로세스 관측 실패와 hierarchy guard 부재의 assertion failure를 기록한다. 25개 시험 전부가 각각 독립 TDD cycle이었다고 주장하지 않는다. 기존 완료된 과학 suite는 재실행하지 않았다. prepared-boundary 시험의 승인 dictionary는 메모리 안의 test boundary일 뿐이며 AUTHORIZATION 파일이나 실행을 만들지 않는다.

실제 Ubuntu 표준 저장소에서 libgmp-dev/libgmpxx4ldbl을 설치하고 관련 libgmp10 패키지가 2:6.3.0+dfsg-2ubuntu6.1로 갱신됐다. package manager가 chrony/packagekit 서비스 restart를 기록했으며 원문 로그를 반환한다. cgroup 배치·mount·boot 설정은 바꾸지 않았다. 독립 gmpxx.h/mpz_class/mpq_class 프로그램의 compile/link/정확산술 실행과 ldd를 확인했다. 이 smoke는 원자 적분이 아니다. 실제 native는 별도의 새 prepare에서 빌드하고 GMP/GMPXX와 모든 linked library 바이트를 새로 pin했다.

새 session은 외부 `r4ah_prepare_session_v1`이다. 상태는 PREPARED_NOT_AUTHORIZED, actual authorization=0, scientific native integrals=0, m64/remaining9/fullK 실행=0이다. inherited prepare가 만든 10개 node 계약은 모두 미승인이다. 다음 m64 실행에는 이 정확한 새 source/native/resource/BATCH와 범위의 별도 수락·승인이 필요하다. 원 m64 launcher의 구 lock을 이 파생본에 그대로 사용하지 않는다. 현재 지시는 authorize/run/execute 권한을 제공하지 않는다.

BATCH SHA256: b879e905ff67e5799da9448be887c59258cd404d5c5dc7c0e7b26083bb10a5b0

새 source lock SHA256: 7cb66a000645a92b70d97704cbbbc3811d6cab7dd38d251629651120a8b3537e

native SHA256: f35078fa0206780effcadf97de672a458f4c5495dc5b663fae0c806b5519081c

G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO. physical_bridge_upper=null; full_stencil_total_upper=[null,null]. Bianchi 물리는 rei_bianchi 소유이며 수정·실행하지 않는다.

## 재현 범위

시험: `PYTHONDONTWRITEBYTECODE=1 /qualified/python -m unittest discover -s tests -v`.

별도 수락된 새 환경에서 prepare만: `PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 /qualified/python runtime/r4ag/source/batch.py prepare --output /absolute/new/session/batch --workers 3`. output의 parent session은 새로 만들며 이전 prepared/failed session을 재사용하지 않는다. 이번 실제 interpreter/dependency identity는 반환 ENVIRONMENT.json에 있다.

## 근거

Linux의 controller 제한은 hierarchy에 따라 적용되고 global root는 일부 controller 파일의 예외다. [Linux cgroup-v2 문서](https://docs.kernel.org/admin-guide/cgroup-v2.html). mountinfo의 root/mountpoint와 escape 규약은 [proc_pid_mountinfo(5)](https://man7.org/linux/man-pages/man5/proc_pid_mountinfo.5.html)에 따른다. global visibility 판정은 문서에서 자동 상속한 보증이 아니라 위 실제 kernel-thread/namespace 관측에 근거한 보수적인 구현 정책이다. [GMP C++ include/link 문서](https://gmplib.org/manual/C_002b_002b-Interface-General)는 독립 개발 의존성 smoke에 사용했다.
