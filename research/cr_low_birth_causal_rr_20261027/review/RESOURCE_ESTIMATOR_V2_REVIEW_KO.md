# C4 file-cache 추정식 v2 독립 검토

## 판정

**새 단위의 versioned resource estimator로 채택할 수 있다. 실제 회수량의 보장이나 hard safety bound로 채택할 수는 없다.** 판단 대상은 1 GiB reserve와 worker·CPU 한도를 유지하면서, 회수 가능성이 있는 clean file cache를 추정에 반영하는 방법이다. 이 문서는 과학 결과의 수용 기준을 변경하지 않는다. 코드의 실제 최종 해시 검토와 fresh C4v2 host admission은 각각 별도 기록으로 남긴다.

검토자는 이론·독립 참조 코드 작성자이며 production/runner 비작성자다. 이 검토에서는 문헌 및 source text를 읽었고, source import·compile·control 실행·science worker·cache-pressure experiment·시스템 설정 변경·process signal을 하지 않았다.

## Linux 원문이 뒷받침하는 것

Linux의 active file LRU는 unevictable 분류와 다르다. `/proc` 문서는 active memory를 최근 사용되어 보통 유지되는 범주로 설명하며, 필요하면 회수할 수 있는 여지를 남긴다. `MemAvailable`도 file LRU를 반영하는 추정치다. 따라서 active file cache 전체를 원칙적으로 회수 불가능하다고 취급하는 inactive-only 추정은 지나치게 작아질 수 있다. [Linux /proc 문서](https://docs.kernel.org/filesystems/proc.html)

이를 source에서도 확인했다. 관찰된 host version string에 대응하는 `gregkh/linux`의 `v6.18.55`, `mm/vmscan.c`를 실제 읽었다. Provider가 반환한 Git blob은 `2c66fbcd6e84504d308e8f36be01cf5c5c60cb8f`다. `shrink_active_list`는 eligible active folio를 inactive list로 이동시키고, unevictable folio는 다른 경로로 돌린다. 이 source tag가 host의 정확한 build configuration·patches·실제 enabled reclaim path까지 식별한다는 주장은 하지 않는다. [Linux stable source](https://github.com/gregkh/linux/blob/v6.18.55/mm/vmscan.c)

`memory.stat`의 `file`은 type-based counter이며 shmem을 포함한다. `active_file`/`inactive_file`은 reclaim algorithm의 list 상태여서 두 체계의 합이 반드시 같지 않다. Dirty, writeback, mapped counter도 별도 의미를 갖는다. 이러한 차이가 아래 `min` 및 제외항의 이유다. [cgroup-v2 문서](https://docs.kernel.org/admin-guide/cgroup-v2.html)

다만 unevictable 문서는 일부 folio가 아직 분류되지 않아 일반 active/inactive list에 잠시 남을 수 있음을 명시한다. 따라서 counter에서 알려진 unevictable 값을 뺀 것만으로 나머지가 즉시 전부 회수 가능하다고 증명할 수 없다. [Unevictable LRU 문서](https://docs.kernel.org/mm/unevictable-lru.html)

원문 URL·실제 acquisition 방식·Git blob·읽은 함수·실패한 web 접근은 [동반 JSON](RESOURCE_ESTIMATOR_V2_REVIEW.json)의 acquisition receipt에 기록했다. Kernel 전체 source를 보고서에 재배포하지 않는다.

## 권고하는 고정 식

모든 counter를 bytes로 읽고 다음을 계산한다.

\[
C=\max\{0,\min[\max(0,F-S),A_f+I_f]-M_f-D_f-W_f-U\},
\]

\[
R_{\rm credit}=\lfloor C/2\rfloor,\qquad
H_{\rm group}=\max\{0,L-\mathrm{current}+R_{\rm credit}\},
\]

\[
H_{\rm estimate}=\min\{\mathrm{host\ MemAvailable},H_{\rm group}\}.
\]

여기서 `F=file`, `S=shmem`, `A_f=active_file`, `I_f=inactive_file`, `M_f=file_mapped`, `D_f=file_dirty`, `W_f=file_writeback`, `U=unevictable`, `L=memory.max`이다. `memory.max=max`이면 cgroup cache credit을 더하지 않고 host `MemAvailable`을 사용한다.

`file-shmem`과 file LRU 합 중 작은 값을 택해 shmem 또는 다른 accounting 범주를 별도 여유로 더하지 않는다. Mapped·dirty·writeback·unevictable을 모두 빼는 것은 겹치는 counter를 중복 차감할 수도 있으므로 의도적으로 작게 잡는 policy다. 정확한 disjoint-set 회수량 산식은 아니다.

**50%는 이번 새 context에서 science worker를 시작하기 전에 고정하는 policy haircut이다.** Linux가 최소 절반을 돌려준다는 보장도, 성공 확률도 아니다. 오늘의 threshold에 간신히 맞도록 비율을 조정한 값으로 사용해서는 안 된다. 남은 절반을 availability에 넣지 않는 여유를 두면서 고정1 GiB reserve도 그대로 요구한다.

Raw `L-current`는 부호를 보존한 상태에서 credit을 더한다. 처음부터0으로 잘라 현재의 limit 초과를 없애지 않는다. Host `MemAvailable`은 이미 cache를 고려하므로 그 값에 credit을 더하지 않고 cap으로 쓴다. 원 inactive-only estimate와 모든 raw counter, formula version 및 non-atomic/estimate 표지를 함께 기록한다. 필수 counter가 없거나 잘못되면0으로 보충하지 않고 admission을 닫는다.

## 유지되는 조건과 증명하지 못한 것

Named worker limit는256 MiB, 상위 worker cap은512 MiB, host reserve는1 GiB다. 따라서 요구량은1,342,177,280 bytes다. 새 failure-inclusive CPU cap40초와 frozen numerical tolerances도 그대로다. 새로운 availability proxy를 평가해도 이 한도들은 변경되지 않는다.

이 추정은 즉시 할당 가능한 physical RAM의 엄밀한 하한이 아니다. Clean unmapped cache에도 transient reference·pin·filesystem 제약·hot working-set 효과가 남을 수 있다. Counter snapshot도 원자적이지 않으며 병렬 할당과 writeback이 뒤따를 수 있다. Reclaim/refault의 지연이나 kernel background CPU도 이 식으로 제한하지 않는다. 이는 policy margin을 둔 admission estimate이고, 실제 worker peak RSS·failure·receipt와 분리해서 해석해야 한다.

그러므로 이번 판단은 원 failed context를 PASS로 바꾸는 승인이 아니다. v1 원본과 receipt를 보존하고 v2의 estimator/code/manifest/host snapshot을 새로 고정한 뒤, root가 그 실제 값을 평가해야 한다. 시스템의 read-only cgroup mount를 풀거나 resource limits/access controls를 바꾸는 조치는 필요하지 않으며 승인한 적도 없다.

## 실패 비용과 기존 근거

v1 host admission은 실제 `FAIL`이었다. 원 estimate838,250,496 bytes는 고정 요구량1,342,177,280 bytes보다 작았고, admission 자체의 charged CPU는0.251963초다. Scoped cache hint 및 실패한 `memory.reclaim` 시도를 합한 현재 same-unit resource 비용은 **1.714435 CPU-s**이며, `all_resource_attempts_pass=false`다. `memory.reclaim`은 `EROFS`로 실패했고 resource limits 변경과 process signal은0이었다. 이 수치는 [resource cost manifest](../evidence/PREWORKER_RESOURCE_COSTS.json)와 [실패 receipt](../evidence/C04_CONTAINER_CACHE_RECLAIM_V3.json)의 실제 기록이다.

v1 source/admission 원본은 [보존 manifest](../evidence/C04_ADMISSION_V1_PRESERVED/PRESERVATION_MANIFEST.json)에 남긴다. 이 비용과 다음 실제 admission 비용은 새로운 pinned preparation ledger에 한 번만 포함해야 한다. 과거20/30CPU 또는 병렬 프로젝트 잔여를 가져오는 일이 아니다. Resource admission의 실패를 scientific numerical FAIL로 바꾸지도, 비용0으로 바꾸지도 않는다.

## 후속 판정의 범위

이 문서가 채택하는 것은 **추정식 변경의 근거와 한계**다. C4v2 live admission 및 controls·science worker 실행 결과는 아직 이 문서의 근거가 아니며 실행 receipt가 나온 뒤 별도로 검토한다. 기존 hard aggregate CPU proof=false와 global completion/budget null을 유지한다.

### 최종 코드의 한정 정적 판정

`PASS_SCOPED_STATIC_PENDING_LIVE_C4_AND_RUNTIME`, 열린 지적0건으로 판정했다. 대상은 runner SHA256 `629d14ab8dd93fe0b23fb6394038f061f4a3fc0642922d110788d67922e05d9f`와 controls SHA256 `7a85e0549f1a0a8a529c2bd17d6ca242de2495f208710057b5190723fed08894`다. 보존v1에 대한 bounded diff를 직접 읽었으며 import·compile·실행은 하지 않았다.

Pure helper는 OS I/O 없이 고정50% 식을 구현하고 raw counter·signed headroom·이전 estimate를 보존한다. 여섯 counter fixture는0/negative headroom, 홀수 credit의 내림, 제외항, host cap/unlimited, 정확한256MiB+1GiB 경계, shmem clamp 및 missing counter 거절을 다룬다. 이 fixture들은 아직 실행된 PASS가 아니다.

같은 단위의 preparation 비용은 unit-local regular receipt의 실제 bytes/SHA와 charged field에 pin된다. Unique resolved path, unit identity, 이전 budget-transfer 금지, manifest 합계와 budget baseline의 일치를 initial/final admission에서 확인한다. 기존 attempt의 immutable debit·최대 누적값 중복 제거는 유지됐다. 원 scientific model, uniformization, ports, primary, prepare, plot 및 reference의 byte hashes도 보존v1과 일치한다.

새 cost manifest를 만들 때 live `C04_HOST_ADMISSION.json`을 v2에 사용한다면, 이전0.251963초 receipt는 보존v1 경로에 pin해야 한다. 이는 이전 실패의 비용을 다시 측정하거나 고치는 일이 아니라 실제 원본 경로를 안정적으로 유지하는 작업이다. 최종 manifest·fresh host 결과·worker peak RSS는 각각 실제 기록이 나온 뒤 검토한다.
