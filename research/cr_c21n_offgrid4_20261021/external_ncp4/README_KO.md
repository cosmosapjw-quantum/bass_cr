# PR94의 별도 NCP offgrid4 반환

이 디렉터리는 새 적분 없이 발견한 외부 NCP 반환의 원 bytes와 수용 근거를 보존한다.
최종 판정은 `NCP_RETURN_ACCEPTANCE.json`을 따른다. `pr94_original/`은
PR94의 고정 Git subtree를 경로만 옮긴 보관본이며, 원 source나 실행 영수증을 고치지 않았다.

## 출처와 두 실행의 관계

| 항목 | 샌드박스 실행 | 외부 NCP 실행 |
|---|---|---|
| 실행 시작 UTC | 2026-10-21 13:10:16 | 2026-10-21 13:10:24 |
| 관측 host | af4832b34a81 | s1a0e5abed09 |
| Run identity | f42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023 | a07a95f85042f9db7df2e3e465288524b458bcb6f190e9d4f01db1869c139360 |
| Python | 3.12.14 | 3.12.3 |
| 실행 code content | 5ecb8a6c4961302b7066b06278e72ecd2d77f8c9 | 같은 고정 content |
| 원 REI source | 3b85dedce84d37b3e165da00685a8a984950aafe | 같은 고정 source |

두 manifest는 동일한 네 물리 입력을 기록한다. Execution site와 Python 버전이
manifest identity의 일부이므로 두 run identity가 서로 다르다. 시작 시점의 scoped
intake는 13:06 UTC였고 PR94는 13:14:54 UTC에 공개됐다. PR95 생성 뒤 intervening
PR94라는 새 단서를 확인하여 이 반환을 추가 수용했다. 이전 intake 결과는 당시
관측 범위로 유지하며 전역 부재의 주장으로 바꾸지 않는다.

외부 원 branch는 `research/cr-c21n-offgrid4-evidence-20261021`, 확인한 HEAD는
`92b1b3f5575375580cf8de8039252ac492353b7e`다.
원 PR: https://github.com/cosmosapjw-quantum/bass_cr/pull/94

네 case는 기존 완료 입력 registry의 동일한 네 좌표다. 두 site의 실행을 각각
기록하되 고유 입력 수는 기존125+새4=129로 유지한다. 이 수용에서 새 ODE와
기존 static physics campaign 실행은 모두0이다.

## 보관 범위와 재사용

`PINNED_EXPORT.json`은 원 경로·Git blob·크기·SHA256을 고정한다.
`ARCHIVAL_COPY_MANIFEST.json`은 43개 원 파일과 이 경로 사이의 byte 대응을 기록한다.
기존125를 반복 포함하는 원 `analysis/components_campaign129.npz` 하나는
이번 네 case 수용에 필요하지 않아 가져오지 않았다. 원 output manifest는 그 파일을
계속 참조하며 역사적 원문으로 보존한다. 이 보관본을 PR94 전체의 완전한 복원본으로
부르지 않는다. 네 원 trajectory NPZ와 실행 seal·source binding은 모두 보존한다.

원 `postprocess_offgrid4.py`는 해당 PR의 역사적 분석 source다. 이 경로로 옮긴 뒤
재실행하거나 경로를 수정하지 않았다. 이번 unit의 성분별 그림과 tensor 산출물은
상위 `analysis/`와 `analyze_offgrid.py`가 제공한다.

## 원 metadata의 해석

원 `analysis/INPUT_BINDINGS.json`의 `content_tree` 이름은 실제 Git tree가 아니라
NCP run identity를 담는다. 수용 영수증은 명시된 commit과 run identity를 구분하고 17개 source bytes를
고정 실행 commit과 대조한다. 원 필드명을 근거로 source를 재지정하지 않는다.

원 SHA256SUMS와 Git CSV 사이의 줄바꿈 차이는 수용 영수증에 별도 기록한다.
원 bytes·원 checksum은 유지하고 raw NPZ/COMPLETE seal 및 실제 Git blob 검증과
분리한다. 검증 범위를 넘어 원 manifest 전체를 통과로 선언하지 않는다.

원 `BACKUP_RECEIPT.json`의 Drive·Dropbox 다운로드 검증은 외부 작성자의 반환
근거다. 이번 대화에서 수행한 provider 다운로드로 세지 않는다. 이번 통합 배송본의
실제 ACK와 byte 검증 수준은 상위 `BACKUP_RECEIPT.json` 및 최종 authority receipt를
따른다. `global_error_bound=null`을 유지한다.
