# BASS_CR C23E — D43K source binding

**COMPLETE_SCOPED / NUMERICALLY_CHECKED_SCOPED**, independent PASS_SCOPED. 실제3개 PW19 광원에 대해 저장H 모멘트에서 D43K 문턱 모멘트를 구성하고,21species 순간 source의 PI/RR/CX·thermal/fast electron·에너지 장부를 결속했다. 새ODE0, 완료 계산 재실행0.

읽는 순서: [RESULTS_KO.md](RESULTS_KO.md), [THEORY_KO.md](THEORY_KO.md), [FROZEN_CONTRACT.md](FROZEN_CONTRACT.md), [독립 검토](review/INDEPENDENT_REVIEW_KO.md), [DAG](NEXT_DAG.json), [handoff](HANDOFF_KO.md).

기존 완료 근거를 복원하기 위해 아래 실행을 반복하지 않는다. 결과는 `runs/C23E_D43_SOURCE_BINDING_20261024T021612Z_v1/`에서 직접 읽는다. 새로운 입력/코드 변경으로 별도 검증을 허용받은 경우에만 다음 portable entry point가 새 create-only output을 만든다.

```bash
python implementation/dispatch_d_binding.py
```

필요 환경은 Python3.12, NumPy2.3.5, SciPy1.17.0, Matplotlib이며 실제 source/환경/자원은 run의 manifest와 preflight에 있다. 모든 입력은 상대경로로 포함되어 있다. 원 실행 source와 배송용 경로 교정 source는 별도 identity로 보존한다. 배송 교정29checks와 원 과학104checks는 다른 검사 집합이다.

선택된 근사는 D threshold-gated H-equality 및 조건부 VF RR moment다. 실제 동위원소별 PI/RR Milne·full21 rate coverage·full stopping·우주론적 열진화는 OPEN이다. 고에너지 핵 전체 campaign과 general triaxial/tilted/polarized CMB는 HOLD이다. 소유권·유효영역·source identity가 다른 REI/WU 계산을 단일 ensemble로 합치지 않는다.


## C10 복구·배송 현재 기록

# C23E C10 복구·배송 종료 기록

선택 범위는 이미 독립 검토된 C23E의 C10 기계적 복구·배송이다. 새 과학 계산·수치 재실행·새 과학 판정은 0이다. 과학 COMPLETE_SCOPED / NUMERICALLY_CHECKED_SCOPED와 기존 PASS_SCOPED를 재사용한다. 변경은 배송 메타데이터뿐이므로 새 독립 과학 검토는 필요하지 않다.

Science S: `8e4e06361d714939513a11f64a27f02822bde2fa`; historical central M: `4d78d35da27c8fc1a6fb291c748e7406e2ad9d7c`. Draft PR100은 main merge 없이 additive 문서 D로 이어진다. D와 후속 central M2의 실제 SHA는 게시 후 별도 external terminal authority에서 확인한다. 이 문서 자체의 미지 SHA를 실제 값으로 표기하지 않는다.

원 canonical ZIP `BASS_CR_C23E_D43_SOURCE_BINDING_DELIVERY_20261024T025351Z.zip`은 1337923 bytes, SHA256 `d124964d6c36f40bced91a5d123a00082bd3a9d512f66e89c092fd47a1248e49`, 116 members / 115 payloads이다. Library와 Dropbox의 실제 전체 바이트를 회수해 size/SHA256/CRC/115개 payload size·digest를 확인했다. 원 ZIP과 그 MANIFEST는 변경하지 않았다. 상세 provider 영수증은 [BACKUP_RECEIPTS.json](BACKUP_RECEIPTS.json), compact R3 결과는 [BYTE_READBACK_VERIFICATION.json](BYTE_READBACK_VERIFICATION.json), 원 inventory는 [CANONICAL_MANIFEST.json](CANONICAL_MANIFEST.json)에 있다.

Library+Dropbox actual BYTE_IDENTITY R3 PASS; Drive UNKNOWN_NO_ACK; historical UNKNOWN_NO_ACK unchanged


최신 재개 순서는 [FINAL_CLOSEOUT_KO.md](delivery/FINAL_CLOSEOUT_KO.md)를 따른다.
