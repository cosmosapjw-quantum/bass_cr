# BASS-CR 새 물리 데이터: 시간별 누적 광이온화·광전자 스펙트럼

**단위:** `CR_PHYS03_RR_TEMPORAL_FIRST_ABSORPTION_V1` · 2026-10-30

## 연구 동기와 성과

최신 GitHub 조사에서 부모 PR127을 확인했으며, PR125의 원본 SOURCE ZIP을 ChatGPT Library에서 materialize하여 전체 SHA-256을 직접 재확인했다. PR127은 최종 `T=1e10 s`에서만 누적 첫 광흡수의 sharp interval을 제공했다. 새 모델은 **새 원본 광자나 새로운 관측치를 생성한 것이 아니라**, 기존 source-locked 원자별 photon birth measure를 모든 관측 시각에 전파하여 정확한 시각별 absorption envelope와 primary photoelectron-energy spectrum을 계산한다. 기존 Ferrers dual-oracle PR126과 별개이다.

## 실제 생성한 물리량

`T=0..10e9 s`, 1.25e9 s 간격의 9개 관측시각에서 36개 photon-source × absorber × time 행, 9개 전체 time 행, 792개 광전자 1-eV-bin spectral 행을 생성했다. 매 행은 주어진 freezing contract의 실제 Verner HI/HeI 단면적과 PR125의 원본 원자별 발생가중치로 구성하며, 발생 시각의 미지 자유도에 대해 rigorous sharp interval을 제공한다.

| T [s] | first absorption lower [m^-3] | upper [m^-3] | primary e- kinetic-energy lower [J m^-3] | upper [J m^-3] |
| ---: | ---: | ---: | ---: | ---: |
| 1.25e9 | 0 | 1.0602488697643456e-28 | 0 | 3.5548315679292356e-47 |
| 5e9 | 2.095156546517316e-28 | 1.7404049556024497e-27 | 7.050023255186708e-47 | 6.058583374717195e-46 |
| 7.5e9 | 1.7404049556024497e-27 | 6.536559924836172e-27 | 6.058583374717195e-46 | 2.3286751165159964e-45 |
| 1e10 | 6.536559924836172e-27 | 1.7193913666048543e-26 | 2.3286751165159964e-45 | 6.236750696526702e-45 |

최종 `T=1e10`의 전체 광흡수 fraction은 PR127과 같은 약 2.394834556%–6.299426469%이며, 4개 channel: H→HI, H→HeI, He→HI, He→HeI 중 H→HeI만 정확히 0이다. 전체 발생광자는 `2.729441124610644e-25 m^-3`. 최종 광자 흡수 에너지 `[1.6701889106530614e-44, 4.404835288850727e-44] J m^-3`와 그 안의 threshold/primary-electron kinetic-energy 분할을 검증했다.

## 주요 과학적 해석

이 데이터는 허용된 미지의 photon emission times에 대한 *sharp conditional time envelope*이다. 특정 시점의 평균 반응률 `dN/dt` 또는 살아있는 가스의 heating rate로 재해석하면 안 된다. 특히 물리적 동시해를 갖는다는 것은 pointwise envelope의 모든 관측시각/observable extrema를 동시에 갖는다는 의미가 아니다. 부모 자료의 100 K 고정 HI/HeI 밀도를 유지했으며 다른 BASS/REI/WU 프로젝트의 epoch, bin, clock 또는 parent-ion inventory를 섞지 않았다.

## 검증과 실패 기록

- `bash REPRODUCE.sh /path/to/original_PR125_SOURCE.zip`: Python unittest **14/14** regular, **14/14** with `-O`; `compileall` PASS.
- 독립 high precision `mpmath` 75 dps 직접 Verner fitting 구현의 **120 controls**, `sigma` 최대 상대 차이 약 `2.202e-15`, first probability 약 `2.295e-15`. 이는 별도 수학구현의 대조이며 **다른 사람 R6/C9**로 오인하지 않는다.
- 원본 PR127 끝점의 absorption lower/upper 동일성, 인과·시간 단조성, energy split, H→HeI zero, 모든 1-eV bins 합 검산.
- Wolfram Language에서는 `dP_a/ds = -c alpha_a exp[-c alpha(T-s)] <=0`, `(E-I_a)+I_a=E`, survival+absorption=1을 기호적으로 확인했다.
- PR125 원본 ZIP SHA256 `8e9b58236819146f4929aa4647dafdb1dc21b97b2f129ec4035291bb73a1ed2e`; PR125 원본 NPZ SHA256 `e171824cf5fc3ba232fbbd4def6fc8cf6c855ca9e7d05506e4e4426c9416688f`; 원본 PR127 Python Git blob `19beccce93e91e98c771c04d04d220a9cde45504` 및 Table Git blob `4990865d7c314c26ebcb7d5a66d3cb4cf2e0511f` 로컬/원격 일치.

## 별도 repo와의 관계

BASS PR259는 방향 의존 Bianchi-I photon sky, VigilODE PR118은 BASS21 이력 및 원래 rate source, REI PR272는 71-bin radiation budget 조건부 LP, BASS_HE PR114는 EXFOR nuclear data이다. 이들 자료는 source/density/energy/clock authority가 다르므로 이번 PR125의 고정 HI/HeI ground-RR source에 물리적으로 합성하지 않는다. 이들의 존재는 후속 clock/energy compatibility 연구의 입력 후보로만 기록했다.

## DAG 및 선언

`CENTRAL_DAG=28/88 (delta0)`, `EXTENSION_DAG=0/3 (delta0)`, `NEW_SCOPED_AUXILIARY=1/1_REVIEW_HOLD`, 새 이론·코딩 workflow `18/20`(직접 별도 작성자 R6/C9 NOT_RUN). 원본 PR127·PR126·PR125·PR124·main 수정 없음. `physical_K`, exclusive He kernel, chemistry feedback, photon redshift/transfer, native25, L4, production은 UNBOUND/HOLD.

### 재현 순서

1. 바이트 고정 원본 PR125 ZIP을 복구하고 SHA 검증한다. PR127 부모 브랜치 코드 및 `source/VERNER1996_HI_HEI_TABLE1.dat`가 변경되지 않았음을 검증한다.
2. `bash research/cr_phys03_rr_time_envelope_20261030/REPRODUCE.sh /absolute/path/to/BASS_CR_PHYS02_RR_IONIZING_PHOTON_SOURCE_20261029.zip`.
3. `results/RESULT.json`, `TIME_TOTAL.csv`, `TIME_CHANNEL_TARGET.csv`, `TIME_ELECTRON_SPECTRUM.csv`, `INDEPENDENT_MP75.json`, 두 PNG를 점검한다. Snapshot csv는 Git에 게시하고 전체 원본 ZIP은 binary SOURCE archive로 별도 백업한다.

**기타**: 이번 실행의 산출물은 physical-source-derived conditional data이고, 실제 우주 물리 이력 또는 관측 적합도는 아니다. `R06=NOT_RUN_DISTINCT_AUTHOR`, `C09=NOT_RUN_DISTINCT_AUTHOR`, native_subagent=NOT_AVAILABLE.
