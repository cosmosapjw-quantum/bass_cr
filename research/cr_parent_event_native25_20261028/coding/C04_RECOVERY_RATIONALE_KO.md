# C4 v1 거절과 고유 v2 준비

실제 c4_v1은 source·정책·review pin을 확인한 뒤 raw memory gate에서 거절됐다. scientific worker 및 PID probe는 시작하지 않았다. 순수 preparation CPU 0.139732 s와 tail0.05 s, 합계 **0.189732 s**를 terminal receipt에 기록했다. admitted budget은 생성되지 않았다. 원 helper·runtime·preflight·실패 receipt를 모두 보존한다.

관찰된 cgroup limit은 8,589,934,592 bytes, current는 7,926,816,768 bytes였고 raw 여유는 663,117,824 bytes였다. 필요한 worker256MiB+host reserve1GiB는 1,342,177,280 bytes이므로 v1 판정은 맞다. 동시에 memory.stat의 file cache는 6,121,648,128 bytes였다. 이 관찰은 raw 여유와 reclaim 가능한 cache를 구분할 필요를 보여준다.

Linux 원문 [cgroup-v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)의 memory.stat과 [proc](https://docs.kernel.org/filesystems/proc.html)의 MemAvailable 정의를 직접 읽고 Exa 검색/읽기와 대조했다. file type counter와 active/inactive list counter는 같지 않으며, shmem·mapped·dirty/writeback 등은 겹칠 수 있다. 아래 계수와 상한은 이 문서에서 주어지는 kernel 공식이 아니라 현재 단위의 명시적 입장 판단이다.

새 제안 `CAPPED_CLEAN_FILE_LRU25_V2`는 min(file,active_file+inactive_file)에서 shmem,mapped,dirty,writeback,unevictable을 모두 빼고 음수는0으로 둔다. 그 값의1/4만 고려하며 credit 상한은1GiB다. 관찰된 memory.min 또는 memory.low가0이 아니면 credit은0이다. available 추정값은 host MemAvailable와 max(0,signed raw+credit) 중 작은 값이다. **유한 cgroup의 raw 여유 자체도 worker256MiB 이상이어야 한다.** 최종 worker+reserve 기준과 CPU40 s, preparation4 s, 한 thread,512MiB upper/256MiB selected 제한은 그대로다.

이것은 과거50% file-LRU 정책을 자동 이월한 결과가 아니다. 현재 실패를 근거로 별도 source·policy·review를 결속하는 새 버전이다. snapshot과 cache accounting은 비원자적이며 lower-bound certificate 또는 kernel 메모리 보장이 아니다. OS 제한, cache 설정, pressure는 조작하지 않는다. 모든 worker의 최초 및 launch 직전 입장에서 같은 새 식을 사용한다.

v2는 별도 `ops/admit_c4_v2.py`, 고유 c4_v2 intent/receipt, fresh C04_V2 preflight와 독립 memory-diff review가 있어야 시작한다. preparation ledger는 v1 실패와 v2 비용을 각각 보존하며 같은 attempt 안의 누적 amendment는 최대값만 한 번 합산한다. 원 science source와 허용치는 변경하지 않는다. 실제 v2 admission 결과는 이 문서 이후 생성될 receipt로만 판정한다.

현재 확정 게시·이중 백업은 C03까지 **13/20**, 중앙 **28/88**, 이번 CR 효과0이다. 후속 과학 노드는 시작하지 않는다.
