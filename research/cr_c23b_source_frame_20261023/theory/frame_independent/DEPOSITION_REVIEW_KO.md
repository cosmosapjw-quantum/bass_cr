# C23B boosted deposition 독립 검토

`boosted_deposition.py`의 유한 FS2010 보간표와 양의 이산 입력 measure
축약을 **PASS_SCOPED**로 판정한다. 이미 통과한 boost/clock suite는
재실행하지 않고 source identity를 재사용했다.

새 실행 `c23b_deposition_independent_20261023_v1`은 별도 reader로
MIT21cmFAST mirror의 실제5개 표를 읽고,80자리 정밀도로 xi를 보간한 뒤
각 energy cell의 rest-cosine 구간을 직접 계산했다. 두 Gauss 점은
선형 표 응답과 에너지의 곱(차수2)을 정확히 적분한다. reference는
producer의 AngularBox clipping, bracket, blend, Bernstein 가중치를
호출하지 않는다. 입력표 값은 producer와 같은 FP64 실수로 읽어
해당 유한 보간표의 연산을 비교했다.

| 검증 | 실제 결과 |
|---|---:|
| 양의 원자 measure 사례 | 9 |
| xi | 0.1,0.37,0.9 |
| query / channel 비교 | 27 /189 |
| 실패 query | 0 |
| 최대 channel 상대오차 | 1.6936901260821877e-14 |
| number/energy basis 합의 최대 정규화오차 | 1.5127547755287014e-16 |
| tail/covered/full moment 최대 정규화오차 | 1.6606064502579083e-16 |
| raw energy-defect 비교오차 / max(1eV,covered energy) | 7.185412856724466e-15 |
| number/energy basis 비음성 | 모두 PASS |
| 미해결 tail heat/ionization | 모두 null 유지 |

허용치는2e-12다. channel 상대오차의 분모는 max(1e-30,reference channel)
이며, basis 및 partition은 전체 입력의 대응 moment로 정규화한다.
global_error_bound=null. 표 자체의 energy-closure defect는 수정하거나
재정규화하지 않았다.

사례는 lower/upper table knot의 u0 Dirac, rest K0의 유한 boost,
표 knot에 걸친 u1e-12, finite-box의 domain/high-tail 분할,
matched-speed의 low/domain/high 분할, neutron-mean 위치의 단일 atom,
여러 atom의 양의 혼합, 전부 high-tail인 입력을 포함한다.
단일 atom과 혼합은 계산 검증 입력이며 평가된 beta spectrum으로
표현하지 않는다.

Source SHA256:

- boosted_deposition.py:8868ac9cf580a452c05827e2182f04179f36a9a86f8806e28fc914c6a9ded042 (4810bytes)
- vendor/fs2010_operator.py:53c9056908fe9a875c35bb7d8047149d3c45f5d0856aac74ebe84e4248a51809 (10012bytes)
- COMPLETE.json:3606b43af5f543ce7e549d0b87e9432ad06bce8348a8cf08c9d0c8ddc4955230

코드, 입력표 및 독립 reference의 크기와 SHA는 SOURCE_PINS.json에
있다. 실행 당시 source snapshot을 보존했다. 실제 coordinator CPU2,
worker CPU4, native1thread, worker wall1.467055773s,
outer wall1.962650338s, peak RSS20288KiB, exit0, 해당 lease RELEASED.

EXECUTION: 새 deposition 축약 독립 검사 COMPLETE_SCOPED.
PUBLICATION: PARENT_PENDING. BACKUP: PARENT_PENDING.
DAG: boost/clock identity 재사용 -> finite-source contraction 검사 완료 ->
실제 gas 조성/transport/cooling 및 source-spectrum admission 후속.
full nuclear/thermal closure 및 기존 FS2010 표의 물리 적용 조건은
이 계산 검사로 변경하지 않는다.
