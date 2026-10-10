# CR-PHYS02C-NIST-EXCITATION-KERNEL01

결과는 Astra 독립 리뷰가 승인한 `PASS_SCOPED`다. Astra가 정한
100 K 고정 bath에서 NIST HI 1s→2p(10.204 eV), HeI singlet
1s²→1s2p(21.218 eV) 두 여기 채널만 실제 proper-second rate로
진화했다. 속도·He/H 변환의 누락은 구현 전에 Astra로 반환했고,
승인된 amendment를 계약에 먼저 기록했다. 구체 구현과 검증은 하위
tier가 수행했다. 기존 HeI 23s provider와 연결·교체하지 않았다.

활성 전자 에너지는 `(1000,3000] eV`다. `E=E0−10.204m−21.218n`을
정수 meV로 계산하여 projection 없이 유한 event graph를 만든다.
1000 eV 이하에 도달한 상태는 흡수 상태로 보관하며 실제 잔여 에너지와
전자 수, HI/HeI event counts를 보존한다. crossing 에너지는 열로
배분하지 않는다. gas 수밀도와 온도·이온분율은 진화하지 않는다.

초기 impulse 1000.001, 1015, 1500, 2000, 3000 eV 각각에 대해
proper time 0, 10¹⁰, 10¹¹, 10¹², 10¹³ s를 검증했다. 독립적인
sparse exponential과 Poisson uniformization을 비교했고 1000.001 eV의
한 번 충돌 뒤 crossing에 도달하는 analytic oracle도 비교했다.
25개 행 모두 조건을 만족했다. graph 크기는 3, 5, 665, 2482, 9581로
각 impulse당 최대 10000 상태를 만족한다.

최대 상대 전자 수 ledger 오차는 1.6653345369377348e−15,
`Uactive+Ucrossing+10.204CH+21.218CHe` 에너지 ledger 오차는
1.4432899320127035e−15다. 두 방법의 최대 observable/E0 차이는
7.504451356993373e−15이고 최대 uniformization tail은
6.42262147813232e−16이다. 음의 population은 없고 OFF/t0도 통과했다.
집중 unittest 5개를 통과했고, 독립 Astra reviewer도 같은 5개 test를 재실행해
PASS를 확인했다. reviewer는 승인 amendment의 속도/neutral-target convention,
NIST IDs/energies, graph/reservoir ledger와 25행 evidence를 대조했다. 최초 campaign 1회, repair 0회이며
내부 wall 0.191234601 s, 관측 process wall 0.736491194 s다.
나머지 overhead는 측정하지 않았다.

입력 NIST PDF/table/provider는 기존 로컬 bytes를 재사용했다.
계약·입력·실행 결과는 CONTRACT.json, SOURCE_MANIFEST.json,
evidence/VALIDATION.json, evidence/EXECUTION.json에 기록했다.
Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0에서 실행했다.

검증 범위는 두 채널의 고정 bath 조건부 이산 kernel이다. 물리 cross
section/table interpolation 모델 오차와 생략 채널 효과는
`UNKNOWN_NOT_MEASURED`다. ionization, Coulomb, HeII excitation,
다른 전이, gas feedback은 포함하지 않았다. crossing reservoir의
잔여 에너지·수만으로 P02B 입력 spectrum을 정하지 않으므로
`P02B_INTERFACE=HOLD`다. source convolution, 전체 CR/IGM history와
global admission도 HOLD다. 다음 실행은 독립 Astra scoped 리뷰다.

재현 명령:

```bash
python3 -m unittest discover -s research/cr_phys02c_nist_kernel_20261010/tests -v
timeout 120s python3 research/cr_phys02c_nist_kernel_20261010/validate.py
```

validate.py는 stdout으로만 출력하므로 기존 evidence를 덮어쓰지 않는다.
Git commit/push와 backup/publication은 controller의 리뷰 후 결정에 맡겼다.
