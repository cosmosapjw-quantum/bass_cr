# 실제 단계 게시·백업 인덱스

현재 실제 receipt **19/20**, scoped node **1/1**, 중앙 **28/88** (`08364a6ef6f4880c9c4fff87335d167fbff9b440`). Git는 expected-SHA/force=false 후 원격 ref 확인 R1, 단계 ZIP은 양쪽 provider ID/크기와 manifest 대조 R2다. R2를 원격 본문 R3로 표기하지 않는다.

| 단계 | 실제 Git commit | 절차 | scoped | 양쪽 checkpoint | archive bytes |
|---|---|---|---|---|---:|
| R01 | [942f3412c6bd](https://github.com/cosmosapjw-quantum/bass_cr/commit/942f3412c6bd16aac0713f7b9610f666284017d7) | 1/20 | 0/1 | R2 PASS / R2 PASS | 1,491,668 |
| R02 | [8803204ffa44](https://github.com/cosmosapjw-quantum/bass_cr/commit/8803204ffa44c09d89b8c0c4551e2ed05a618889) | 2/20 | 0/1 | R2 PASS / R2 PASS | 2,320,913 |
| R03 | [5cd5ad39447b](https://github.com/cosmosapjw-quantum/bass_cr/commit/5cd5ad39447b78bbb6b0021a7b55da9f2962f37c) | 3/20 | 0/1 | R2 PASS / R2 PASS | 2,331,604 |
| R04 | [78377e7f98cf](https://github.com/cosmosapjw-quantum/bass_cr/commit/78377e7f98cf97c70ebd57c1ac4b7d6125b14129) | 4/20 | 0/1 | R2 PASS / R2 PASS | 2,338,818 |
| R05 | [dc0661e91f85](https://github.com/cosmosapjw-quantum/bass_cr/commit/dc0661e91f8562f566ba4227b4054f681733d876) | 5/20 | 0/1 | R2 PASS / R2 PASS | 2,348,222 |
| R06 | [48d1d23777a5](https://github.com/cosmosapjw-quantum/bass_cr/commit/48d1d23777a51db8411294a2ec298e53dd2c5ce8) | 6/20 | 0/1 | R2 PASS / R2 PASS | 2,365,661 |
| R07 | [f29c723b315b](https://github.com/cosmosapjw-quantum/bass_cr/commit/f29c723b315b1107e8e131c247572da1cc62d3f0) | 7/20 | 0/1 | R2 PASS / R2 PASS | 2,373,889 |
| R08 | [2db988b004b8](https://github.com/cosmosapjw-quantum/bass_cr/commit/2db988b004b8d0a731c84b613deb7961623ef394) | 8/20 | 0/1 | R2 PASS / R2 PASS | 2,381,231 |
| R09 | [13dc52569bb2](https://github.com/cosmosapjw-quantum/bass_cr/commit/13dc52569bb2ba5b995384a911408843054b3ec9) | 9/20 | 0/1 | R2 PASS / R2 PASS | 2,389,038 |
| R10 | [0db1d72042d3](https://github.com/cosmosapjw-quantum/bass_cr/commit/0db1d72042d39aec6fe77430e4ab0bbbe2d488f3) | 10/20 | 0/1 | R2 PASS / R2 PASS | 2,396,677 |
| C01 | [9d648ef10165](https://github.com/cosmosapjw-quantum/bass_cr/commit/9d648ef101652af47237fd478929929b70e0f4be) | 11/20 | 0/1 | R2 PASS / R2 PASS | 2,411,915 |
| C02 | [18f493038b4d](https://github.com/cosmosapjw-quantum/bass_cr/commit/18f493038b4d763897a5a15bfd90d5d6bb369f1d) | 12/20 | 0/1 | R2 PASS / R2 PASS | 2,425,279 |
| C03 | [d8140ffab5dc](https://github.com/cosmosapjw-quantum/bass_cr/commit/d8140ffab5dcd4ce1533e92a59eddf83c84de07b) | 13/20 | 0/1 | R2 PASS / R2 PASS | 2,433,437 |
| C04 | [ad13f0c00767](https://github.com/cosmosapjw-quantum/bass_cr/commit/ad13f0c0076777104a8a50716de3c35c22e9c92f) | 14/20 | 0/1 | R2 PASS / R2 PASS | 2,444,222 |
| C05 | [c0f7eed51e6e](https://github.com/cosmosapjw-quantum/bass_cr/commit/c0f7eed51e6ef4bf8f3089b12ac6a6bf6ea6219d) | 15/20 | 0/1 | R2 PASS / R2 PASS | 2,631,118 |
| C06 | [ccbff992546c](https://github.com/cosmosapjw-quantum/bass_cr/commit/ccbff992546ce9978e0e39298b0ce6bcc451fc31) | 16/20 | 0/1 | R2 PASS / R2 PASS | 2,704,624 |
| C07 | [949d58cf38d7](https://github.com/cosmosapjw-quantum/bass_cr/commit/949d58cf38d72a019094eccd2fec143675a53edc) | 17/20 | 0/1 | R2 PASS / R2 PASS | 4,193,897 |
| C08 | [527840221887](https://github.com/cosmosapjw-quantum/bass_cr/commit/527840221887e9777031f2a6f281d48cb1ac42ef) | 18/20 | 0/1 | R2 PASS / R2 PASS | 4,375,007 |
| C09 | [98174c29b984](https://github.com/cosmosapjw-quantum/bass_cr/commit/98174c29b98439f70f4cf14c8510f88c6a538c4f) | 19/20 | 1/1 | R2 PASS / R2 PASS | 4,671,844 |
| C10 | PENDING ACTUAL PUBLICATION | 20/20 content only | 1/1 | PENDING | — |

## Provider object identities

각 원본 파일명·hash·revision·ID·size·실제 시점은 `publication/stages/<stage>_RECEIPT.json`에 있다.

| 단계 | Dropbox ID | Drive 원본 |
|---|---|---|
| R01 | `id:BSpOijBcT10AAAAAAEGmSg` | [1jxVoi-Jrth7--fKeNADJRe1cTd1MiEJZ](https://drive.google.com/file/d/1jxVoi-Jrth7--fKeNADJRe1cTd1MiEJZ/view?usp=drivesdk) |
| R02 | `id:BSpOijBcT10AAAAAAEGmTg` | [17wWn_2DxqC7ZEoI3ux0-vo9qgbjdyiaN](https://drive.google.com/file/d/17wWn_2DxqC7ZEoI3ux0-vo9qgbjdyiaN/view?usp=drivesdk) |
| R03 | `id:BSpOijBcT10AAAAAAEGmVA` | [1fv_PXk0Rovv4CezLDtB37WJgB8-pTOQe](https://drive.google.com/file/d/1fv_PXk0Rovv4CezLDtB37WJgB8-pTOQe/view?usp=drivesdk) |
| R04 | `id:BSpOijBcT10AAAAAAEGmVw` | [1I29aATzTz-wflRi-6tg_kF7mc3ErVvuh](https://drive.google.com/file/d/1I29aATzTz-wflRi-6tg_kF7mc3ErVvuh/view?usp=drivesdk) |
| R05 | `id:BSpOijBcT10AAAAAAEGmWw` | [14vBuY8h20UpQHpWj4AttBS2LaG79yjwm](https://drive.google.com/file/d/14vBuY8h20UpQHpWj4AttBS2LaG79yjwm/view?usp=drivesdk) |
| R06 | `id:BSpOijBcT10AAAAAAEGmYA` | [1XFtS3nqxMUGI-NMlzGs2jl2CU7bxAY-h](https://drive.google.com/file/d/1XFtS3nqxMUGI-NMlzGs2jl2CU7bxAY-h/view?usp=drivesdk) |
| R07 | `id:BSpOijBcT10AAAAAAEGnQQ` | [1n9HgLixUXcnsAY1kofVYbSHv7HDnZ9qU](https://drive.google.com/file/d/1n9HgLixUXcnsAY1kofVYbSHv7HDnZ9qU/view?usp=drivesdk) |
| R08 | `id:BSpOijBcT10AAAAAAEGnQw` | [1CpPc_ukE2rNAQQUPTv-RK-bUp-iwsogq](https://drive.google.com/file/d/1CpPc_ukE2rNAQQUPTv-RK-bUp-iwsogq/view?usp=drivesdk) |
| R09 | `id:BSpOijBcT10AAAAAAEGnRQ` | [1o1KVpY-2Y294ysDgVlijrk0z0V6OpL8t](https://drive.google.com/file/d/1o1KVpY-2Y294ysDgVlijrk0z0V6OpL8t/view?usp=drivesdk) |
| R10 | `id:BSpOijBcT10AAAAAAEGnRg` | [1YTyMk6UuaKQJvXjLPQfYF_ZXAdHwNrZa](https://drive.google.com/file/d/1YTyMk6UuaKQJvXjLPQfYF_ZXAdHwNrZa/view?usp=drivesdk) |
| C01 | `id:BSpOijBcT10AAAAAAEGnSg` | [1EbSWs7Ugt6vC5XMXsSoM8falu1ukQC4K](https://drive.google.com/file/d/1EbSWs7Ugt6vC5XMXsSoM8falu1ukQC4K/view?usp=drivesdk) |
| C02 | `id:BSpOijBcT10AAAAAAEGnSw` | [1adB6YtZadh_w-4VF_QL3MqWsJAALiYnk](https://drive.google.com/file/d/1adB6YtZadh_w-4VF_QL3MqWsJAALiYnk/view?usp=drivesdk) |
| C03 | `id:BSpOijBcT10AAAAAAEGnbA` | [15W78oNu0FzKE3WVkJIZHzLsneKRutNXf](https://drive.google.com/file/d/15W78oNu0FzKE3WVkJIZHzLsneKRutNXf/view?usp=drivesdk) |
| C04 | `id:BSpOijBcT10AAAAAAEGnbQ` | [1xAI6TAvF6uYeHQyjwNexvCPGmIZPuJ8B](https://drive.google.com/file/d/1xAI6TAvF6uYeHQyjwNexvCPGmIZPuJ8B/view?usp=drivesdk) |
| C05 | `id:BSpOijBcT10AAAAAAEGneQ` | [1u_NvXm8kOkQsUw-YdW3lW9JACTouXQwW](https://drive.google.com/file/d/1u_NvXm8kOkQsUw-YdW3lW9JACTouXQwW/view?usp=drivesdk) |
| C06 | `id:BSpOijBcT10AAAAAAEGnfA` | [1OBaaxAyrxNe70kvnUw6lkNnLSwwuKRwG](https://drive.google.com/file/d/1OBaaxAyrxNe70kvnUw6lkNnLSwwuKRwG/view?usp=drivesdk) |
| C07 | `id:BSpOijBcT10AAAAAAEGngg` | [1CKy4Aa7WvnGzmmTAlU9FSGncHR4un3tv](https://drive.google.com/file/d/1CKy4Aa7WvnGzmmTAlU9FSGncHR4un3tv/view?usp=drivesdk) |
| C08 | `id:BSpOijBcT10AAAAAAEGnhg` | [1p3cI1b2LVoEGszmdcQ63iESTrpGYrjBO](https://drive.google.com/file/d/1p3cI1b2LVoEGszmdcQ63iESTrpGYrjBO/view?usp=drivesdk) |
| C09 | `id:BSpOijBcT10AAAAAAEGnjw` | [1nqE1bynL52cwfMVn4vdkfKj0oMUVKTcl](https://drive.google.com/file/d/1nqE1bynL52cwfMVn4vdkfKj0oMUVKTcl/view?usp=drivesdk) |

## Canonical immutable archives

- **SOURCE:** `BASS_CR_HE_JOINT_REGION_SOURCE_20261028_98174c29b984.zip`, 4,690,891 bytes, 265 payloads. SHA256 `87ddb7718d37895c3842b710a2af4f6419ffbc8ea38d0a55e0b1093217876311`. Dropbox `id:BSpOijBcT10AAAAAAEGnkA`, Drive `17x4Q25DQQSQTI_D16l9-3NIjUj3J8rYd`. 양쪽 original full GET·전체 SHA256·모든 payload SHA256·ZIP CRC **R3 PASS**.
- **CLOSEOUT:** 아직 실제 생성 전. 미래 hash/ID를 채우지 않는다.

SOURCE는 C09 과학 스냅샷 S에, CLOSEOUT은 실제 C10 문서 스냅샷 D에 연결한다. SOURCE를 이후 영수증으로 재작성하지 않는다. 각 archive MANIFEST는 bound-commit Git membership와 archive-only/postcommit payload를 구분한다. 최종 Git F는 이 실제 결과의 metadata acknowledgment이며 21번째 연구 단계가 아니다. F의 실제 hash는 PR116 최종 body 및 대화의 postcommit handoff에서 식별한다.
