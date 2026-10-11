# PHYS02E 최종 전달 기록

Science `eceec9a0c65f44c3d8b785194b9e40c8ee23b590`와 독립 PASS_SCOPED를 바탕으로 완전 ZIP 및 정확-ID NCP 시작문서를 두 기존 백업에 create-only 발행했다.

- Draft PR: https://github.com/cosmosapjw-quantum/bass_cr/pull/34
- ZIP: `CR_PHYS02E_20261011_eceec9a0_HANDOFF.zip`, 10510880B, SHA256 `28f91c7bccb0649124b71d51313f9d278fdc5ab48b1f9a1f3c3037de205ea133`
- 시작문: `CR_PHYS02E_20261011_eceec9a0_NCP_START_KO.md`, 19002B, SHA256 `8a75a787fafbd7191ec34286ab854ced31b8a2e8c578dbcd3ac790c2ff252c21`
- Drive ZIP: https://drive.google.com/file/d/1vXrURpI15GfezJShUkoY-S72WwV8prPM/view?usp=drivesdk
- Drive 시작문: https://drive.google.com/file/d/1rZdkamzBbtj1NsFpPFY1QCuvrKsz4Ort/view?usp=drivesdk
- Dropbox ZIP ID `id:BSpOijBcT10AAAAAAD4AjQ`, rev `65d865de55df20af03d47`
- Dropbox 시작문 ID `id:BSpOijBcT10AAAAAAD4Ang`, rev `65d86632850350af03d47`

`NCP_START_WITH_BACKUP_IDS_KO.md`를 복사해 실행자에게 넘긴다. 추가 사용자 첨부가 필요없으며, complete ZIP 하나에 새 단위68파일/필수의존409파일/원본실패ZIP/두harness를 포함한다.

`LOCAL_RESTORE_SMOKE_RECEIPT.json`은 최종 ZIP의483entry actual local cleanrestore와 stdlib plan1회, exit0/admissionREADY를 기록한다. local 자원은 false이므로 NCP resource/runtime certification으로 쓰지 않는다. 원격 업로드는 provider ID/size/rev 기준R1이고 rawremote restore를 주장하지 않는다.

준비과정 actualG/pulse0/0,15targetedtests와13exact identities, priorDactualexit1/HOLD 유지. 새2G2pulse3600s는 별도 PHYS02E task이며 실제 NCP input/runtime/resource와 이후독립과학심사가 필요하다.

이 경로의 후기 영수증은 science FILEmanifest에서 명시적으로 제외된다. 이미 발행한 ZIP이나 동결코드를 덮어쓰지 않았다. 전체 manifest는 `PUBLICATION_FILE_MANIFEST.json`에 있고 자기파일hash는 순환방지로 제외한다.
