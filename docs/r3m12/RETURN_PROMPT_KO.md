# R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN

입력 repo: cosmosapjw-quantum/bass_cr
입력 commit: 77237751bdd2aed5934bf7fc3bc626d631a09058
코드 commit: 0b0090bc217ef62b27f709de803660b13bc64148
결과 commit: aa733718a07f8ce00619a36b74c49560114a85bf
전용 branch: cr/r3m11-fixed-cap-gram-20260921

패키지 SHA256SUMS 90/90, 저장 archive SHA/manifest를 검증했다. addition-only patch 10파일, targeted tests 35/35 및 CPU/GPU parity 두 경로가 통과했다. 별도 reviewer dispatch는 CLIENT_WORKTREE_MISMATCH로 차단돼 독립 리뷰는 NOT_RUN이다.

먼저 저장 baseline/dx03125의 Gram 후처리를 완료했다. 보정 후 공간 변화 10.419207%. 새 100 keV/u,b=2 실행 10개와 11개 attempt가 완료됐다. fixed-CAP dt 변화 0.407404%, 초기 imaginary-time step/기간 변화 0.013703%/0.007307%. 같은 refined preparation에서 dx .4→.3125는 10.411148%, .3125→.25는 2.289941%. AOCC dt 0.010804%, radial-only 4.732602%, exponent-only 14.508513%. 1% screen은 그대로다.

b-grid NO_GO 유지. 50/225 keV/u, 적분 단면적, physical rate, all-bound/continuum 및 과학적 승격은 미실행/미인정. TDL finite n<=3 span과 AOCC s+p aggregate는 같은 truncation이 아니므로 cross-lane equality 미평가.

전체 archive: /mnt/sn850x2t/BASS_CR_R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921_v1.tar.gz
크기: 1,231,876,036 bytes; 내부 166개 파일 검증.
SHA256: 3be00617f99387ffec406de5fa47000c5d2b8f56a9e9767f4fdcb1b6bc790fa6
Drive: BACKUP_PENDING — 19조각 중 1개만 원격 SHA 검증. 512MiB 상한과 blob 60초 timeout의 실제 실패 receipt 보존. 원격 부분 manifest: https://drive.google.com/file/d/1XDOKIFQpfOcNFHWpVZ473oMfjfy7Hskj/view
Dropbox: 전체 archive 업로드 및 raw readback SHA/size 검증 완료.
경로: dbx:BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN_20260921_v1.tar.gz
최종 dual_backup_complete=false: Google Drive 전체 archive는 보류. 성공·실패는 DELIVERY_SUCCESS_RECEIPT.json / DELIVERY_FAILURE_RECEIPT.json 및 DUAL_BACKUP_RECEIPT.json에 분리.

다음 최소 수치 작업: dx=.25, physical dt=.05, CAP 고정하에 imaginary dt=.0125×2400과 기존 .025×1200을 비교한다(총 준비시간30). 초기 stationary residual 및 finite-span 확률을 함께 확인한 후 추가 공간 정련을 판단한다. 이 실행은 이번 반환에서 수행하지 않았다. AOCC radial/exponent 수렴 문제도 남아 있으며 b-grid로 넘어가지 않는다.
