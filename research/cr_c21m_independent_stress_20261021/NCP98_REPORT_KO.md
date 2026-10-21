# C21M NCP98 선택 정제 — 결과 및 상태

**EXECUTION: `COMPLETE_SCOPED` · PUBLICATION: content/document 분리 게시 · BACKUP: Dropbox·Drive ACK 및 실제 재다운로드 SHA 확인 · DAG: 독립 수렴 검증 필요**

## 실행

과학 입력은 고정 content `659c94312eb9c12ebb987de934459c12a63d67b0`, native/source owner는
`rei_bianchi@3b85dedce84d37b3e165da00685a8a984950aafe`다. 실행 직전 최신 외부 반환에서 동일한
98개 좌표의 완결 결과를 찾지 못해, 준비만 되어 있던 NCP98을 새 isolated checkout에서 실행했다.
기존 26개와 C21L 중심 1개는 재적분하지 않았다.

정제 run identity는 `7f89b12adbeee64a70832e633ae563584bc2a68f6ac2a60139b98efacb01c05a`, grid SHA-256은
`768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04`다. 고정 source commit은
`3b85dedce84d37b3e165da00685a8a984950aafe`, source manifest SHA-256은
`cf0997cbd89806dc7ec7b99982829e9b14f0612518bca56967c96e83fed5ea90`다. 실행 핵심 코드 SHA-256은
builder `7fb15e89403817812588e189c013d45d200864f0076351c7c84bf77667520f0f`, shared_resources
`ad642904d7c9334a4c650702ab792ecc49c7dcca2b542fbf8315bd318ec58795`, shared_runner
`af472ce77a12ef3bb78cec5a46ec05f4dc44324c2c28ce429d2e3c50957f0b65`다. Python 3.12.3,
NumPy 2.3.5, SciPy 1.17.0을 사용했다. 98/98 완료, 실패 0이다.
원시 per-case `history.npz`, `RESULT.json`, `COMPLETE.json`, 전체 manifest, event, resource 및 반환 영수증을
보존했다. 전체 run payload는 `runs/ncp_refinement98_20261021/`에 있다.

원본 조건은 FP64, 40-state, 101 저장점, DOP853, `rtol=3e-11`, `atol=3e-13`, 고정된 quadrature와 RHS다.
CPU55는 제외했고 coordinator는 CPU0, 실제 worker affinity는 61개 CPU였다. Numpy/SciPy thread는 1이다.
경과 13.18초, `time -v` 최대 RSS 112,792 KiB, CPU 868%로 관측됐다. 이것은 단일 실행 기록이며 benchmark나
speedup 주장이 아니다.

## 결합 분석 및 검산

완료된 기존 26점 + 신규 98점 + 재사용 중심 1점에서 중복 없는 125개 Cartesian 좌표를 결합했다.
분석은 새 ODE 적분을 하지 않았다. 최대 초기축 절대오차는 `1.7347e-18`, Hamiltonian 상대잔차는
`2.2204e-16`, massive comoving-number 상대잔차는 `4.4409e-16`이다. 배열은 `Y=(125,40,101)`과
`gamma/nu E=(125,101,9)`다. 모든 원시 case seal과 SHA, 결합 산출물 7개 manifest 항목을 독립 재검증했다.

z=4에서 signed Frobenius 범위:

| 관측량 | 최소 | 최대 |
|---|---:|---:|
| `S_signed_F` | -1.444983638e-3 | 1.444570673e-3 |
| `P_m_signed_F` | -1.243674356e-5 | 1.257478373e-5 |
| `P_r_signed_F` | -6.299231787e-5 | 6.344480065e-5 |
| `P_tot_signed_F` | -7.519532478e-5 | 7.577499571e-5 |

독립 그림 검토에서 최초 8pt 셀 라벨이 겹친 결함이 발견되어 기존 원시 결과로만 분석을 다시 수행했다.
변경은 패널 너비와 라벨 크기뿐이며 새로운 적분은 없다. 교정된 PNG의 모든 5×5×5 실제 셀, 부호,
축과 색상 범위를 시각 검토했고, 표본 셀은 CSV와 일치했다. PDF의 바이트 SHA와 output manifest는 확인했으나
별도 PDF 렌더 시각 검토는 하지 않았다.

세부 raw와 분석 산출물은 각각 `runs/ncp_refinement98_20261021/` 및 `analysis_campaign125_20261021/`에 있다.
독립 검토 결과 `NCP98_INDEPENDENT_REVIEW.json`, 실행/자원 영수증은 `NCP98_EXECUTION_RECEIPT.json`이다.

## 게시, 백업 및 범위

새 evidence는 content commit `ee62f86f7df02d7e4b9baccfa107d76254c68ac4`에만 추가한 뒤 별도 document commit에서
보고서와 DAG 및 실제 백업 영수증을 기록했다. [Draft PR](https://github.com/cosmosapjw-quantum/bass_cr/pull/92)은
기존 PR #91 위에 쌓이며 자동 병합하지 않는다.

새 아카이브 SHA-256은 `e9baa6bab57790d29a0dfb06747a3304f0449a48e7dfc2d14c6630849f9c1d0a`, 17,911,591 bytes다.
Dropbox와 Drive 모두 create-only 업로드 ACK 후 실제 다운로드했고 두 원격 파일 모두 로컬 해시와 일치했다.
상세 ID·경로·사이즈·readback 증거는 `NCP98_BACKUP_RECEIPT.json`에 기록했다.

이 연구는 정해진 collisionless LRS Bianchi I의 초기조건 grid refinement일 뿐, 시간·source-age·spectral/angular
수렴 검증이 아니다. 일반 triaxial, full reionization, CMB 및 전역 오차 상계는 계속 HOLD이며
`global_error_bound=null`이다.
