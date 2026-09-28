NCP 실행 산출물을 GitHub에 검증된 execution evidence로 게시해줘.

Repository: cosmosapjw-quantum/bass_cr
Target branch: research/fnd-ncloud-f1-engine-admission-20260928

현재 source checkout은 변경하지 마. target branch를 fetch하고 이미 생성된 F1 detached worktree가 있으면 사용해. 없으면 별도 detached worktree를 만들어.

authoritative policy:
research/foundation_rebuild/ncloud_c64g3_20260928/NCP_GITHUB_EVIDENCE_UPLOAD_KO.md

현재 우선 게시할 run:
stage = F0
run_id = 20260928T045058Z

source files:
/root/.local/state/bass_f0/runs/tp2e_cache_20260928T045058Z/RETURN_REPORT.json
/root/.local/state/bass_f0/runs/tp2e_cache_20260928T045058Z_RETURN.zip
/root/.local/state/bass_f0/receipts/f0_20260928T045058Z/F0_RETURN_HANDOFF.json
/root/.local/state/bass_f0/receipts/f0_20260928T045058Z/ENVIRONMENT_RECEIPT.json
/root/.local/state/bass_f0/receipts/HOST_F0_20260928T045058Z.json
/root/.local/state/bass_f0/receipts/F0_RUN_20260928T045058Z.log
/root/.local/state/bass_f0/receipts/f0_20260928T045058Z/SHA256SUMS.txt

필수 identity:
RETURN_REPORT.json: bytes=6336, SHA256=a074daa3a5c3a87939c52d41984a78ca5059e932ac9f07983bee2e78b6f22986
RETURN ZIP: bytes=11426, SHA256=fd5e5a7543dd60ba2711ff5189324c116c8c9a1595c8c106744f2cf1aad0a440

destination:
research/foundation_rebuild/ncloud_c64g3_20260928/f0_evidence/20260928T045058Z/

절차:
1. source 존재 여부, size, SHA256을 확인해.
2. RETURN ZIP CRC와 내부 manifest가 있으면 검증해.
3. 실제 F0_RETURN_HANDOFF/RETURN_REPORT에서 STOP_F0_COMPLETE, tests 32/32, M4 N96, spatial eval 0, reference_reintegrated=false를 확인해.
4. HOST/environment/log에 secret scan을 수행해.
5. credential/token/private key/signed URL/password/불필요한 IP·resource ID가 있으면 원본은 보존하고 sanitized public copy를 만들어.
6. EVIDENCE_MANIFEST.json과 SANITIZATION.json을 작성해.
7. 원 TP2D TEMPORAL_REFINEMENT_UNRESOLVED와 claim ceiling은 그대로 유지해.
8. evidence 파일만 stage하고 commit message는 data(ncloud): import verified F0 execution evidence 로 해.
9. target F1 branch에 non-force push해.
10. remote ref/tree/blob identity를 검증해.

금지: main 직접 push, force push, reset/clean, source code 수정, science/F0 재실행, F1 native run, threshold 변경, secrets 공개, missing receipt 합성.

완료 시 policy에 정의된 NCP_EVIDENCE_PUBLISHED 블록과 게시한 GitHub 경로 목록을 출력해.