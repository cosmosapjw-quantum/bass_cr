# R4AH 10점 S-only 수신검토 종결 및 백업 복구

2026-10-04. 이 문서는 이미 끝난 수신검토의 게시 기록이다. 원자적분, 원시 collector, M9, 두 window 합산 또는 기존 시험을 재실행한 기록이 아니다.

수락 범위: 동일 유한 s+p 18채널 candidate, b=2a0, 100 keV/u에 대응하는 저장 속도, z0=-32a0의 S-only 미분. 두 고정 window의 full-cross Frobenius total_upper는 H=1/64에서 5.599633283869504e-17 ta^-1, H=1/128에서 7.49726779045559e-17 ta^-1이다. 기존 1e-12 ta^-1 기준을 유지했다. 과거 준비 단계 null로 되돌리지 않는다.

직전 수신검토가 실제 원본 ZIP의 344개 member CRC와 343개 payload, capsule 원본 연결, 새 9점의 원시 정수 합 및 두 window의 정확한 중점 행렬을 확인했다. 원본 archive 복원 SHA-256: 2d5de9369518e11bd9d54c93533995a3e2790bbd55853a9631b5074174d8a2e4. 전체 원시증거 Dropbox ID id:BSpOijBcT10AAAAAADx4QQ; Drive는 검증된 byte-part set을 보유한다. 아래 작은 검토 패키지는 전체 원시증거의 대체물이 아니다.

이번에 재시도하여 실제 저장 완료한 검토 패키지:
- BASS_CR_R4AH_WINDOWS_INTAKE_CLOSEOUT_20261004_v1.zip
- 1091822 bytes
- SHA-256 085135f463b6dc53715576d6fade86b2fff50b091d219432d787c7fbffb36595
- Dropbox ID id:BSpOijBcT10AAAAAADx4yA
- Google Drive ID 1W-wtXVQDzfcpL0FHv54MLVE1fqx6Uzpl
- Drive parent 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
- Dropbox path /bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/provenance/NCP_F1_DUAL_BACKUPS/BASS_CR_R4AH_WINDOWS_INTAKE_CLOSEOUT_20261004_v1.zip

새 업로드 검증은 완료 ACK/remote ID/이름/크기의 R1 UPLOAD_VERIFIED다. 새 업로드를 재다운로드하지 않았으므로 이번 업로드의 RESTORE_VERIFIED는 false다. 직전 원본의 실제 복원검증과 구별한다.

G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO. physical_bridge_upper, precise_K_cubature_error, K_window_derivative_bound는 미확립이다. D+Ddagger 독립 비교, H/K 정확도, 전 궤도, basis/capture/b/energy는 이 수락으로 닫지 않는다.

다음 로컬 연구: R4AN_WEAK_K_NATIVE_SINGLE_CELL_PARITY. R4AM 참조식을 native 단일 cell에 이식하여 일반 cell과 두 원점 cell을 비교한다. Full-K 또는 새로운 산란 batch를 자동 실행하지 않는다. Bianchi 물리와 재이온화 동역학은 rei_bianchi 소유다. 기존 318개 patch를 재적용하지 않는다.
