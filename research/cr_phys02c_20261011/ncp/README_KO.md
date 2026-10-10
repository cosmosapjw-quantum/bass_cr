# CR-PHYS02C NCP 실행 인계

현재 상태는 `PREPARED_NOT_EXECUTED`이다. 로컬 문법·계획·자원 검사만 수행하며 NCP 실행, 64-core 성능 또는 물리 인증의 증거가 아니다.

## 복원 및 실행 순서

1. 이미 승인된 Dropbox/Drive 또는 정확히 고정된 Git 경로로 완전한 인계 묶음을 찾는다. ChatGPT 연결 인증을 NCP 인증으로 가정하지 않는다. 인증이 없으면 기존에 승인되고 설정된 경로를 확인한다. 모든 경로가 실제로 불가능하면 부족한 capability만 보고한다. 추가 사용자 첨부를 기본 해결책으로 요구하지 않는다.
2. 외부 archive SHA256이 제공되면 먼저 검사하고, 새 디렉터리에만 추출한다. archive-root의 `BUNDLE_MANIFEST.json` 전체 payload hash/size를 확인한다. 일부 실패를 무시하거나 성공한 부분만 신뢰하지 않는다. Git 대안은 exact commit과 frozen `FILE_MANIFEST.json`을 확인한다.
3. `state/SCIENTIFIC_CONTRACT.json`, 결과 보고서, 독립 검토, `state/NEXT_DAG.json`, `ncp/NCP_EXECUTION_CONTRACT.json`을 읽는다. 독립 검토와 READY admission 없이는 실행하지 않는다.
4. `python3 ncp/launch_refinement.py --plan`으로 실제 affinity/quota/cgroup RAM/current/RSS/available/free disk/topology/live process 수를 확인한다. cgroup2 membership과 mount를 실제 해석하여 leaf부터 mount root까지 보이는 모든 ancestor의 quota와 memory limit/current를 검사하고 가장 엄격한 quota 및 각 bounded ancestor headroom을 적용한다. hierarchy나 필수 metadata가 불명확하면 host capacity를 추정하지 않고 typed HOLD한다. 한 process, 모든 numerical thread=1이며 coordinator를 포함한다. bounded RAM의 12.5% 또는 1GiB 중 큰 값을 reserve로 제외한 실제 working available이 12GiB 이상이어야 한다. 추정 peak는 8GiB이다.
5. 제공된 `requirements.txt`와 runtime compatibility를 확인한다. 시스템 변경/설치 자동승인은 없다. 필요한 경우 격리 venv를 사용한다. 빠진 dependency는 계산 전 operational failure이며 transport call을 소비하지 않는다.
6. READY일 때만 `python3 ncp/launch_refinement.py --execute --run-dir evidence/ncp_runs/<새이름>`을 수행한다. fullBED와 legacy BEQ/BED의 (3200,6400) 격자를 순서대로 계산하며 transport 최대 2회, 전체 wall 최대 3600s이다. source/bath/CCC/Coulomb/FP64/threshold/metric은 그대로이다. 64-rank sweep이나 old suite 재실행은 하지 않는다.
7. 실패하더라도 `python3 ncp/ops.py collect --study . --run evidence/ncp_runs/<새이름> --out <반환폴더>`로 unique ZIP을 만든다. 실제 stderr/stdout/exit/reservation/결과 파일을 보존한다. 한 번의 범위 내 interface repair 이외에 physics/domain/tolerance 변경이나 두 번째 repair는 독립 Astra에게 반환한다.

복원 명령: `python3 ncp/ops.py extract <archive.zip> <새폴더> --archive-sha256 <외부SHA>`.
이미 추출한 payload 확인: `python3 ncp/ops.py verify <archive-root> <archive-root>/BUNDLE_MANIFEST.json`.

반환 결과는 새 9600 두 모델 각각을 저장된 4800과 비교한다. paired delta의 r=abs(Delta9600-Delta4800)/abs(Delta9600), r<1/3 및 동일 부호를 정확히 적용한다. 0 delta는 resolved로 자동표시하지 않는다. 이는 경험적 두 격자 진단이며 인증된 error bound나 significance test가 아니다. global gate는 유지되고 독립 Astra가 admission/publication을 결정한다.

일반 immutable backup 업로드는 R1 receipt/remote identity/가능한 metadata로 확인한다. 실제 NCP 복원은 R3 byte/hash 검증이며 R1 업로드 성공을 R3 복원 성공으로 바꾸어 쓰지 않는다.
