# C4 자원 admission의 보존과 v2 교정

첫 admission은 BLOCKED_C4_HOST_MEMORY였다. 고정256MiB worker와1GiB hostreserve를 요구했지만, 기존 clean-inactive-only 추정은838250496bytes였다. 이 시도는0.251963CPU초를 charge했고 scientificworker는0이었다. 그때의 budget·host·code manifest·preflight·실행 source14파일을 evidence/C04_ADMISSION_V1_PRESERVED에 byte-identical로 보존했다.

작업 파일 및 설치 runtime에 대한 read-only POSIX_FADV_DONTNEED는 backingfilebytes·설정·프로세스를 바꾸지 않았다. 별도 memory.reclaim 요청은 read-only filesystem의EROFS로 실행되지 않았다. 이 failure와 각 실제processCPU/receipt-tail은 모두 유지하며 자동승인심사거절이라고 바꿔 쓰지 않는다. 초기admission 및 세cache조치의 합계는1.714435CPU초이고, 새40CPU단위 안에서 차감한다. Metadata discovery/외부research도구CPU는 미계측이며0으로 주장하지 않는다.

Linux원문은 active_file과inactive_file을 page-reclaim관리목록으로 구분하며, active가unevictable을 뜻하지 않는다. 관측host와같은v6.18.55 소스의shrink_active_list도 eligiblefilefolio를inactive로이동시키는경로를 제공한다. 이 일반기작은 특정현재counter의전부가즉시회수된다는증명이 아니다.

독립검토에따라 이번새unit에서만 admission추정기를명시적으로v2로고정한다. C=max(0,min(max(0,file−shmem),active_file+inactive_file)−file_mapped−file_dirty−file_writeback−unevictable)에서 정수floor(C/2)만credit으로쓴다. 이50%는고정정책haircut이며Linux가보장한fraction/probability가아니다. Available=min(hostMemAvailable,max(0,limit−current+credit)). 원rawheadroom의부호,모든counter,기존inactive-only추정도같은snapshot에기록한다.

256MiB namedworker,RLimitAS상한512MiB,최소1GiBreserve,1thread,CPU40및모든물리허용치는변하지않는다. v2는자원가용성estimate이며hardreservation/lower-boundcertificate가아니다. 실제workerpeak와비용,실패는별도실측한다. 과거unit의메모리정책·실패·예산은수정하지않는다.

또한새preparation비용을0으로요구하던guard는실제비용보존과양립하지않았다. 새guard는새unit에속한immutable비용receipt의유일경로,bytes,SHA256,각chargedCPU와합계가budget baseline과일치하는지검사한다. 다른unit의비용·잔여예산을가져오는것은계속거절한다. 기존attempt최대누적debit중복제거와UNKNOWN_NO_ACK조건은유지한다.

최초실패를PASS로승격하지않는다. Freshv2code/host/preparationledger가고정되고독립정적검토를통과한경우에만새scientificworker를시작한다. 새C4v2admission의실제결과와추가비용은별도영수증이권위다. 원중앙27/88,집계효과0이다.
