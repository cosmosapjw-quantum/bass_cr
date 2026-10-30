# CR_PHYS07 | 실제 원본 H/He RR 광자 결합에너지·일차 광전자 교환

**Source owner:** BASS-CR PR #131, HEAD `c61857bd99dcc69d1224c8da4432569084f657ea`. Immutable SOURCE archive SHA-256 `6e2fe94051845612d06cbd880eb8c876a0c6692efbe6ef1f8408cd7784b0b764`. Frozen original 100 K H/He, 6400 native photon energy atoms × 4 source birth-time bins, same original Verner (1996) fits. Original parent data/branches/main unchanged.

## 실제 새 물리 데이터

임의 근사 스펙트럼이나 새로운 재결합율을 대입하지 않았다. 원래 PHYS06 `recycling.py`와 PR130 nested source-loader가 참조하는 원본 E, w, n, σ, t를 사용해 **재결합에 참여한 전자의 원래 운동에너지, photon fate, 실제 첫 광전자의 초과 운동에너지, 흡수종의 결합에너지 요구량**을 각 photon atom에 대해 분리하였다.

| T=10^10 s | latest birth (최소 cross absorption) | earliest birth (최대 cross absorption) |
|---|---:|---:|
| He-origin → H I first absorption (m^-3) | 1.33022037584981039e-28 | 3.53378275615920308e-28 |
| **해당 포획의 결합에너지 차이에 따른 일차 전자 kinetic gain** (J m^-3) | **2.34224155667873307e-46** | **6.22225683354388381e-46** |
| 원래 source RR 결합에너지 방출 (J m^-3) | 6.36024263075295633e-43 | 6.36024263075295633e-43 |
| 재결합에 선택된 전자의 원래 kinetic (J m^-3) | 1.23118771765835987e-43 | 1.23118771765835987e-43 |
| survivor photon energy (J m^-3) | 7.42441145734601080e-43 | 7.15094681952624373e-43 |
| target ionization threshold energy (J m^-3) | 1.43732139900146177e-44 | 3.78116021919805757e-44 |
| primary photoelectron kinetic (J m^-3) | 2.32867511651599636e-45 | 6.23675069652670207e-45 |
| energy-ledger residual (J m^-3) | -7.437e-59 | -3.112e-59 |

원본 threshold 값 `I_H = 13.60 eV`, `I_He = 24.59 eV`이므로 He→H first absorption 한 사건의 광전자 추가 kinetic은 **10.99 eV**. H→He channel은 원래 H-origin source photon energies <24.59 eV라 정확히 0. 같은 종의 RR 재흡수는 (epsilon_out-epsilon_in)=0. 원래 photon energy 보존량 7.59143034841131660e-43 J m^-3를 각 branch에서 복원한다.

9 snapshot × earliest/midpoint/latest 27개 globally consistent histories, 4 source→target channels ×27=108 event-energy rows, 4 source birth bins ×4 channels ×23 source-energy bins=368 spectral rows 생성. 전자수·양성원자수/전하/에너지 항등식의 실제 27개 이력 잔차 모두 검사. 각 이력은 bin별 동일 선택 규칙으로 구성하므로 과학적 시간 순서가 일관된다. 임의 서로 다른 시간별 extrema를 합쳐 하나의 이력이라고 주장하지 않는다.

## 재현·검증

- Original PHYS06 source ZIP 6,269,177 bytes, 45/45 SHA manifest + ZIP CRC PASS. Nested ORIGINAL PR130 ZIP SHA checked through original owner loader.
- `bash REPRODUCE.sh` Python unittest normal 15/15, `python -O` 15/15, `compileall` PASS.
- 동일 작성자의 **독립 기호/수치 표현 검사** `mpmath` 80-dps 128 point controls, maximum relative probability error 2.3576e-16, event binding identity MP80 error 0 eV. 다른 연구자의 R6/C9은 NOT_RUN.
- Wolfram symbolic energy/probability identities 3개 exact zero. 초기 수정: 구현 내부 `net_selected_electron_kinetic_change` 부호 검사에서 검출된 부호 오류와 test code NameError를 별도 진단/수정한 후 재시험 성공. 원본 source/threshold/tolerance 수정 없음.
- 바이트 재현은 새 최종 SOURCE ZIP에서 clean extract 후 검사할 것. 본 내용은 현재 local source verified scope이며 Git/cloud 검증은 별도 영수증을 요구한다.

## 물리적 의미와 제한

**derived + implementation-verified** (source-conditional) : cross-species He ground-RR photon이 H I을 이온화하는 사건의 결합에너지 차이(10.99 eV)는 첫 광전자의 초과 운동에너지로 이동한다. 이온·전자 수 장부는 exact eventwise. 다만 target ionization threshold `I`는 원자 내부 결합에너지 차이이지 평형 열역학적 chemical potential이 아니다.

**NOT established:** 실제 누적 가열률, 전자열화와 secondary ionization, 재방출 cascade, 시간에 따른 neutral fractions, 동적 복사 수송, BASS21/REI17와 동일 물리상태, physical exclusive He double-event kernel/K, native25, L4, production. 실제 plasma temperature change 없음. 유한 시간 frozen-gas 모델에서 first-absorption 집계만 수행했다.

## DAG

CENTRAL DAG **28/88 (+0)**; EXTENSION **0/3 (+0)**; 신규 보조 연구 물리자료 **1/1 SCOPED_REVIEW_HOLD**. R/C theory/coding 18/20 scoped, genuine different-author R06/C09 NOT_RUN, native subagent NOT_EXPOSED. PR131/earlier branches, source and main readonly, no merge.

## 문헌 원전

1. Verner et al. 1996, ApJ 465, 487, DOI 10.1086/177435.
2. Switzer & Hirata 2008, PRD 77, 083006, DOI 10.1103/PhysRevD.77.083006.
3. Ercolano & Storey 2006, MNRAS 372, 1875-1878, DOI 10.1111/j.1365-2966.2006.10988.x.
