# NCP local Codex: bass_cr R17B1 수신과 다음 R17B2

담당은 cosmosapjw-quantum/bass_cr만이다. 먼저 research/cr-r17-recovery-r17b1-20261010 HEAD, docs/cr_r17b1_20261010/RETURN_KO.md, research/cr_r17_recovery_20261010/RECOVERED_ARCHIVES.json을 읽는다. 사용자 dirty worktree와 기존 branch는 보존하고 새 worktree/branch에서 진행한다.

이번 새 자체재현 패키지:
BASS_CR_R17B1_20261010_v1.zip
bytes40194
SHA25695b2cba70b84c3cb53df6f5747504d48a82105389acc464e0421f4711ee11374
Drive id1kuHg5j5AISsfWaM7yGVQwnSqFGL3kccS
Dropbox id:BSpOijBcT10AAAAAAD3tPA
Dropbox path /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_R17B1_20261010_v1.zip

원 provider 연결로 ZIP을 수신해 SHA/size/CRC와 MANIFEST26payload를 확인한다. 이 새 패키지의 모든 선택 입력과 실행기·시험·결과는 ZIP 안에 있으므로 재현에 원 donor 다운로드가 필요 없다. 기본 Git에는 core와 이 계약·요약이 있고 원 ZIP은 위 provider에 있다. 사용자가 별도 파일을 첨부했다고 추정하지 않는다. NCP의 연결이 없으면 BLOCKED_INPUT_AUTH이며 현재 ChatGPT의 인증이 NCP로 전달됐다고 가정하지 않는다.

BASS_CR_R17B1_20261010 디렉터리에서 python -B reproduce.py --verify-only를 먼저 실행한다. 필요한 새 환경 재현은 python -B reproduce.py --output NEW_EMPTY_DIRECTORY 한 번이다. 기존 R16B/REI/R17 science suite를 다시 실행하지 않는다. 새 R17B1의 19개 시험·계수 계산은 이미 완료됐으며 이를 다시 구현하지 않는다.

다음 중량 연구의 목표는 R17B2_FULL_COUPLED_SOURCE_KERNEL이다. 같은 FT03 first macro, 원6birth clock/weight box, source rate, 초기 photon/state, 동적 밀도·redshift·원자상수를 고정한다. source homotopy mu_eta=(1-eta)mu_Q+eta mu_S의 전체 해에 대해 arbitrary birth probe와 gas·existing-photon response 및 opacity-survival memory를 포함한다. 7-cohort 기존 adjoint 보간이나 frozen-gas kernel을 검증된 arbitrary-birth kernel이라고 하지 않는다.

첫 source 구간 [0,885031998.4547119]proper s부터 진행한다. R17B1의 regular-fourth-derivative 계수 중99.7754%를 차지하기 때문이며 이는 true error분담률이 아니다. 다음을 실제 interval proof로 공급해야 한다:
(1) 전체 eta homotopy 또는 그 정당한 averaged kernel의 anchor derivatives0..3,
(2) source birth와 thermal/cutoff 등 모든 내부 regularity 경계 및 실제 one-sided jump0..3,
(3) 각 regular piece의 fourth derivative bound,
(4) 같은 상태·source·clock·normalization과 common solution tube.

L(f)=M int f-sum wi*f(xi), 부호는 continuous-minus-discrete. source_peano.py의 moment_defects는1/k!가 이미 들어 있다. Local x=(birth-left)/(right-left)미분과 global u=birth/T 미분의 차이는((right-left)/T)^r이다. r=0 jump가 source atom에 있으면 right/left trace를 명시한다. 실제 d0..d3를 이상적 Gauss exactness로0으로 만들지 않는다. 누락된 regularity/jump/homotopy bounds를0으로 채우지 않는다.

일치하는 검증 입력이 있으면 conditional interface로 signed/absolute source interval을 산출한다. 현재 기록된 C4≈2.579987776092595e-10와 illustrative M4 target7.4129479e-9는 새로운 FT03 error bound가 아니다. 새 결과가 합당하게 개선되지 않으면 NO_CERTIFIED_SOURCE_SHARPENING으로 종료하고 기존 R17A 두 별도 유도를 보존한다. 원 source 구간 budget과 time R16B를 중복해서 합하지 않는다.

새 코드만 focused RED→GREEN, 잘못된 clock/source/birth와 missing-jump 거절시험을 포함한다. 전방 tangent와 후방 adjoint의 독립 검산을 수행하되 고정밀 point대조를 whole-interval증명으로 쓰지 않는다. 실제 cgroup/CPU/RAM을 측정하고 coordinator1CPU와16–24GiB memoryreserve, boundedworker를 유지한다. fastmath/tolerance완화 금지.

R16B와 Grackle는 다르다. Grackle owner입력 및 G02 bank 부재는 기존BLOCKED상태다. 다른 repo의 workstream이나 production을 수정하지 않는다. CR_OFF_FASTEST,precisionatomicPARKED,HH_ACTIVE,G02UNRESOLVED,b_gridNO_GO,all_boundOPEN,physical/productionHOLD를 유지한다.

완료 단위마다 source SHA, 실제 명령/exit/RSS, 수치·증명 구분, failure로그, 재현ZIP을 봉인하고 bass_cr 새 branch에 nonforce push한다. 기존 Drive parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ와 Dropbox 위폴더에 create-only백업. 실제ACK/name/size확인전 성공선언금지, R1과fullrestore분리. 반환은 BASS_CR_NCP_R17B2_RETURN_KO.md, RETURN.json, SOURCE_BINDING.json, VERIFICATION.json, CLAIM_GATE.json, RECOVERY_INVENTORY.json과불변ZIP/실제배포receipt다.
