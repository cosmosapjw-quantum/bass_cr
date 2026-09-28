# NCP → GitHub execution-evidence publication policy

목표: NCP에서 생성된 실행 산출물을 ChatGPT/GitHub connector가 후속 감사에 읽을 수 있는 검증된 Git evidence로 게시한다.

## 원칙

- 기존 source worktree와 cloud output을 수정·삭제하지 않는다.
- main 직접 push, force push, reset --hard, git clean, 자동 stash/rebase를 금지한다.
- 게시 전 각 파일의 bytes/SHA-256을 계산하고, 사용자 보고 SHA가 있으면 정확히 일치시킨다.
- ZIP은 CRC와 내부 manifest가 있으면 hash/size까지 검증한다.
- scientific status와 claim ceiling은 원 RETURN_REPORT 값을 그대로 보존한다.
- missing artifact를 screenshot/대화/요약으로 합성하지 않는다.

## 게시 허용 파일

RETURN_REPORT.json, RETURN ZIP, *_RETURN_HANDOFF.json, sanitized HOST/ENV receipts, sanitized logs/PROGRESS, SHA256SUMS, benchmark/admission JSON·CSV·MD, evidence manifest만 허용한다.

SSH key, cloud access/secret key, API token, .env, Authorization/Bearer header, password/cookie/session, signed temporary URL, metadata credential은 게시하지 않는다. HOST receipt의 IP/VPC/subnet/account/project/resource IDs가 재현성에 필요하지 않으면 공개본에서 제거한다.

최소 secret scan 패턴: PRIVATE KEY, Authorization:, Bearer, ACCESS_KEY, SECRET_KEY, access_key, secret_key, password, token=, x-ncp-apigw-signature.

## Git destination

공통 root:
research/foundation_rebuild/ncloud_c64g3_20260928/execution_evidence/

단계별:
execution_evidence/F0/<run_id>/
execution_evidence/F1/<run_id>/
execution_evidence/F2/<run_id>/
execution_evidence/F3/<run_id>/

현재 F0는 기존 contract와 맞춰 다음을 사용한다:
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/

## 현재 F0 source

/root/.local/state/bass_f0/runs/tp2e_cache_20260928T045058Z/RETURN_REPORT.json
/root/.local/state/bass_f0/runs/tp2e_cache_20260928T045058Z_RETURN.zip
/root/.local/state/bass_f0/receipts/f0_20260928T045058Z/F0_RETURN_HANDOFF.json
/root/.local/state/bass_f0/receipts/f0_20260928T045058Z/ENVIRONMENT_RECEIPT.json
/root/.local/state/bass_f0/receipts/HOST_F0_20260928T045058Z.json
/root/.local/state/bass_f0/receipts/F0_RUN_20260928T045058Z.log
/root/.local/state/bass_f0/receipts/f0_20260928T045058Z/SHA256SUMS.txt

Expected RETURN identities:
RETURN_REPORT.json: 6336 bytes, SHA256 a074daa3a5c3a87939c52d41984a78ca5059e932ac9f07983bee2e78b6f22986
RETURN ZIP: 11426 bytes, SHA256 fd5e5a7543dd60ba2711ff5189324c116c8c9a1595c8c106744f2cf1aad0a440

## Sanitization

원 receipt/log를 수정하지 말고 public copy를 만든다. 제거한 field와 이유를 SANITIZATION.json에 기록한다. 원본 SHA는 EVIDENCE_MANIFEST.json에 남기되 raw secret-bearing file을 GitHub에 올렸다고 주장하지 않는다.

## EVIDENCE_MANIFEST.json

stage, run_id, actual host_kind, source path, published path, source/public SHA256와 bytes, sanitized 여부, scientific_status, claim_ceiling, secret-scan 결과를 기록한다.

## Large-file policy

80 MiB 미만은 normal Git blob을 허용한다. 80 MiB 이상은 원본을 건드리지 않고 64 MiB deterministic parts로 복사해 MULTIPART_MANIFEST.json에 원 SHA/size, part 순서/SHA/size, 복원 명령을 기록한다. Git LFS는 자동 도입하지 않는다.

## Commit/push

승인된 stage branch에 evidence만 commit한다. F0→F1의 target은 research/fnd-ncloud-f1-engine-admission-20260928 이다.
권장 commit: data(ncloud): import verified F0 execution evidence
push는 non-force만 허용한다.

## Remote verification

push 후 remote ref SHA==local HEAD, remote tree==local tree, approved parent descendant, intended evidence path 외 변경 0을 확인한다. local SHA + Git blob identity + remote tree/ref가 일치하면 R1 publication verification으로 닫는다.

## 종료 출력

NCP_EVIDENCE_PUBLISHED
branch = ...
head = ...
tree = ...
parent = ...
stage = ...
run_id = ...
scientific_status = ...
published_file_count = ...
total_published_bytes = ...
manifest_sha256 = ...
return_report_sha256 = ...
return_archive_sha256 = ...
secrets_scan = PASS
remote_ref_verified = true
remote_tree_verified = true

이 출력과 GitHub 경로가 있으면 ChatGPT가 connector로 JSON/MD/log를 직접 읽어 후속 감사를 수행할 수 있다.