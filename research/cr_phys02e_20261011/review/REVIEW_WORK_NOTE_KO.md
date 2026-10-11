# PHYS02E 독립 검토 작업 메모

상태: 최종 패킷 문서 대기. 이 메모는 최종 판정이나 실행 허가가 아니다.

## 역할 및 적용 범위

이 reviewer는 이전에 최신 PR33와 두 백업의 source fact만 intake했다. 후보 생성, saved-grid 경로 선택, acceptance 구성, 과학 코드 구현 또는 local validation 실행에 참여하지 않았다. 별도의 theory contributor, 두 implementation worker와 root의 계약을 읽고 결과를 심사한다. 호스트 라벨은 GPT-6 Astra Pro이며 실제 backend를 독립 검증했다는 주장은 하지 않는다. physmath-research-loop의 Astra v4 연구/코딩 하네스 core와 현재 고정 계약을 읽었다.

## 현재까지 확인한 내용

원 Cascade의 `__init__`는 E 생성 뒤 n/size/ix/atomic/sharing_order/quantum_constant/mesh/normalization_diagnostics를 정하고 generator를 한 번 호출한다. 새 subclass는 E 생성을 pinned saved E의 검증·immutable copy로 대체하고 나머지 실제 사용값을 같은 순서로 설치한다. parent initializer와 energy_grid를 호출하지 않는다. 모든 상속된 수치 메서드는 parent method object를 그대로 사용한다. generator 이전 및 이후 E를 확인한다.

저장 입력 preflight는 양쪽 NPZ 전체 bytes와 hash를 모두 읽은 다음에만 어느 NPZ도 load한다. 전체 필드와 shape/dtype/finite, E 단조성·cutoff/split/top 및 raw digest, 시간·birth tag·heat0·scale가 검증된다. source/cutoff/counter 전체를 immutable copy로 보존한다. worker의 해당 preflight가 atomic import, constructor와 최초 BUILD reservation보다 먼저 실행됨을 source 및 SG06 mock event 검사에서 확인했다.

에너지 좌표 U_i=E_iN_i, 전역 에너지 가중치1과 보정 수 가중치1/E_i, 이온화 counter의 -1 부호가 원본 functionals와 맞는다. barycentric count 투영은 에너지와 수를 함께 보존하며 cutoff ghost와 실제 below-cutoff 에너지를 구분한다. drift·이온화·여기 열의 정확산술 장부 등식과 사후 E 치환 반례는 타당하다. 2 eV에서 epsilon=2^-51 eV인 예의 수 장부 계수 잔차는 1/(2^53+2) (eV s)^-1이다. 이 수치는 실제 9600 G 잔차가 아니다.

새 launcher는 exact runtime, source·dependency·review·DAG identity 및 자원 검사, 두 모형 고정 순서, one coordinator 3600초, unique run, private pipe capability를 유지한다. completed G receipt가 예약과 구분된다. pulse response와 ops 전체 byte, pulse 이후 원 계산 본문은 D와 동일하다. wrapper execute1/collect0 및 execute0/collect1이 각각 nonzero를 유지한다. collect 이후 두 wrapper receipt가 archive 밖에 있다는 사실과 별도 return family 요구가 README/start에 드러나 있다.

19개 direct input과 409개 dependency의 실제 bytes/SHA256/Git blob을 independently 확인했다. 원 validation evidence는 saved-grid 7개 test exit0/0.678532955초, NCP plumbing8개 test exit0/1.139337197초이며 두 worker에서 repair0이다. 별도 theory Fraction oracle은13개 항등식, one invocation exit0/0.028147148초다. reviewer는 과학 코드, physical G/pulse 및 과거 suite를 실행하지 않았고 기존 test를 반복하지 않았다.

## 남은 문서 및 범위

D1 inline math delimiter 문제는 root/theory writer에게 전달했다. 현재까지 material blocker는 발견되지 않았다. 최종 보고서·문서·current state가 완료되면 identity를 고정하여 결론을 발행한다. SG10 최종 ZIP의 실제 clean restore와 stdlib --plan은 root의 post-freeze publication gate로 남긴다. exactE가 old/new G parity 또는 물리 정확성을 증명하지 않으며 actual pulse 결과/원인SIMD 추정/상위7개 gate를 승격하지 않는다.
