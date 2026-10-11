# CR-PHYS02E 실제 NCP 반환

지정 wrapper를 새 run 경로에서 한 번 실행했다. launcher/child/execute/collection/wrapper exit는 모두 0이다. launcher wall 2720.582633553 s, 외부 wrapper wall 2721.685590796 s로 coordinator 3600 s 이내다. fullBED → legacy 순서로 BUILD 예약 2, 완료 G 2, PULSE 예약 2, 실제 expm 호출·완료 결과 2를 확인했다. 실패·물리 retry·oldD 실행·다른 grid/suite 실행은 없다.

고정 ZIP 10510880 bytes / SHA256 28f91c7bccb0649124b71d51313f9d278fdc5ab48b1f9a1f3c3037de205ea133을 기존 Drive 인증으로 받아 새 위치에 복원했다. 정확한 entry483와 BUNDLE482/FILE67/dependency409 파일의 bytes/SHA256, 독립 준비 판정 및 여섯 코드 binding을 검증했다. 기존 dirty 작업과 이전 실패를 보존했다. science eceec9a0c65f44c3d8b785194b9e40c8ee23b590 및 publication receipt 3bb1bc143486417e58234d51e9ea76d786ecfc25 기반 additive branch다. source·physics·tolerance·grid·precision 변경은 없다.

기존 pinned venv를 재사용해 Python3.12.3/NumPy2.4.2/SciPy1.17.0과 numerical pool1을 실제 확인했다. plan exit0 외 admission_status READY 및 resource_probe.admitted true를 각각 확인했다. reserve 후 working memory 115729534464 bytes, disk 52777283584 bytes, CPU affinity64이며 실제 계산은1 numerical thread다. 양쪽 NPZ preflight가 원 file identities·14개 배열·exact E·shape/dtype/finite/time/source heat 등을 통과했다. NCP64 scaling은 평가하지 않았다.

| 실제 selected 결과 | fullBED | legacy |
|---|---:|---:|
| CDF(T=1e10 s) | 0.06390638042977166 | 0.06376934057435844 |
| frozen mean lag_s | 464527679141.6159 | 475674661882.6113 |
| frozen second moment_s2 | 6.799207767364772e23 | 7.182009121564077e23 |
| 저장 ramp 최대 상대 잔차 | 7.624010312135936e-15 | 4.103504407401098e-14 |
| 에너지 장부 최대 절대 잔차 | 2.5646151868841116e-14 | 5.218048215738236e-15 |
| 최소 state | 0 | 0 |
| 저장 endpoint CDF bounds | true | true |

두 birth column과 selected의 전체17개 CDF/kernel·uncapped/clipped moments 및 SI 환산은 actual_run/RESULT_*.json과 NPZ에 보존됐다. 저장 ramp 비교는 같은 operator의 대수 점검이며 독립 물리 검증이 아니다. frozen infinite moments는 고정 operator 연장에 조건부이며 cosmic history나 mesh convergence를 인증하지 않는다.

수치 return ZIP은8993823 bytes, SHA2565048c325175a1c472a252ff1eddcea3c4d622c7611f5bd261c4a9b3258c24b4a, 정확521 entries(manifest payload520 + self1) 전체 bytes/hash를 검증했다. RETURN_FAMILY_MANIFEST.json SHA25656273489b960aaa28f92f6571ea700d205141252687d5482647d4ec6c8fcde6d가 수치 ZIP, ZIP 밖 WRAPPER_COLLECTION_EXIT/WRAPPER_ACTUAL_EXIT, 외부 logs/env 기록을 결속한다. 추가 family ZIP8910030 bytes SHA256ba2241b95c591acaafe09bc181395bb65840d12f366e41f2e3df97d2cb333fc1는 이 전체 family를 포함한다.

수치 ZIP·family ZIP·필수 sidecars·family manifest를 지정 Drive/Dropbox에 create-only 백업했다. BACKUP_RECEIPTS.json은 실제 ID·size·provider success와 최초 Dropbox manifest FETCH_FAILED 및 후속 completed를 보존한다. 백업은 R1/R2 metadata 검증이며 raw remote content readback이 아니다. 제공되지 않은 provider SHA256은 UNAVAILABLE이다. 복구 원본은 R3 실제 bytes/hash를 검증했다.

새 독립 심사는 이번 frozen9600 fullBED/legacy 수치 node를 PASS_SCOPED로 판정했다. 판정 원본은 review/에 보존한다. kernel_per_s는 비정규화 heat response이며 조건부 CDF의 미분은 H0로 나눠야 한다. 실행 exit0을 scientific PASS로 간주하지 않는다. reviewer 요청 backend와 관측 가능한 host metadata는 구분한다. PHYS02_DELAY OPEN; production_history HOLD; atomic_G02 UNRESOLVED; b_grid NO_GO; all_bound OPEN; R17B2B NO_CERTIFIED_SOURCE_SHARPENING; CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED를 유지한다.
