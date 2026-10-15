# bass_cr C12: rei_bianchi SOURCE07 물리 방출률 가중 age와 H/He 동역학

## 연구 목표 및 authority

2026-10-15 KST. 연구 기준 bass_cr C11 43db96b8457842c4bbc945f5b9e4c14f2f831d9f,
rei_bianchi code 기준 codex/rux-science-delivery-20261014 at
0fcb2dddf5de6b583c2e00f150abff0b2afb6315. C11과 동일한
owner-source SHA 3개를 검사하며, owner의 약 351개 변경·미추적
경로를 수정하거나 staging하지 않았다. SHA 변경 시 fallback 없이 실패한다.

한 번의 국소 광자저장고 계산에서 실제 owner Scenario.rate(a)/
H(a,q) dln(a) source-age 방출 가중치를 적용하고,
HI/HeI/HeII photon absorption, HI/HeI/HeII/HeIII 분율과
ideal-monatomic gas thermal energy를 함께 진화시켰다. Source 초기
photon은 z20->z4 방출 광자 전부가 미흡수로 z4까지 도착했다고
놓은 별도 counterfactual surrogate이다. 전체 reionization
역사가 아니다. 초기 gas xHI=.7, HeI=.6, HeII=.35, HeIII=.05,
Tg=1200 K는 controlled test state이고 observed initial condition이
아니다. 8e10초 동안 receiver proper density는 z4 값으로 고정한다.

## 재현 실행

최신 사용자 Ubuntu 로컬 컴퓨터에서 독립 worktree branch를 checkout한 후:

    export REI_BIANCHI_ROOT=/home/cosmosapjw/Dropbox/bianchi/rei_bianchi
    export P=$PWD/research/cr_c12_physical_age_20261015
    export PYTHONPATH="$P/src:$PWD/research/cr_c11_heii_age_20261015/src"
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
    python3 -m pytest "$P/tests" -q -p no:cacheprovider
    python3 "$P/src/validate.py" --owner "$REI_BIANCHI_ROOT" --out /tmp/c12_validation.json
    python3 "$P/src/compare_ode.py" --owner "$REI_BIANCHI_ROOT" --age 48 --workers 3 --out /tmp/c12_physics.json
    python3 "$P/src/benchmark_parallel.py" --owner "$REI_BIANCHI_ROOT" --age 48 --repeats 3 --out /tmp/c12_benchmark.json

Dependency: Python 3.12, NumPy 2.4, SciPy 1.17, pytest.
Requirements: no new external code or API, no Codex. Native
subagent NOT_RUN, OS-process parallelism measured separately.
Source and code in research/cr_c12_physical_age_20261015.
Theory, validity/units and exact proof: docs/THEORY_KO.md.

## 실수치 연구 결과

Owner 2026-10-15 source-rate parametrization: N_emitted =
4.446590310533 photons per original H for q=0. Source-age GL16/32/64
matches owner independent QUADPACK to max relative 2.60e-15.
Separate QUADPACK emitted-energy integrals at three emission ages q=.01
agree with the original threshold-split GL16 quadrature to max relative
3.16e-15 while retaining the shared angular GL12 nodes.

Under the above z4 counterfactual local experiment at q=0, full
48-age independent DOP853 gives:
    xHI 0.4232132376558603
    Tg 5250.356771602446 K
with nonzero HeII->HeIII photoevents. 1-state and 3-state numerical
positive moment reduction have 8 and 13 age nodes. At q=0, 3-state
DOP853 deviations relative to all 48 ages are |Delta xHI|=1.07e-12,
|Delta Tg|=1.39e-8 K. Across three signed q values the maximum
|Delta xHI| is 1.22e-12 and max |Delta Tg| about1.4e-8K. This is
only a *discrete source/receiver one-short-window* approximation.
Original source-redshift photon attenuation, finite angular quadrature
error and evolving expansion could dominate these small numbers.

One-state compression is less accurate on the sampled short window:
max |Delta xHI| about1.07e-8, max |Delta Tg| about4.35e-4K.
SVD-based nonnegative nullspace pruning is used because the
multi-state constraint matrix has near-dependent rows and HiGHS can
return false infeasible. Each original training response row is
rechecked at relative numeric budget 1e-10; observed residual
below ~3e-13 across tested signed q cases. The reduction is a
finite-dimensional constructive approximation, not a universal error
enclosure.

Same exact radiation packet absorption with explicit gas:
photon count residual around 5e-16 photon/H,
photon-energy+binding+gas thermal ledger residual around 6e-15 eV/H.
H nuclei, helium nuclei, electron charge all conserved. Stable
packet population and fraction checks are in tests.

Independent adaptive DOP853 for the same local ODE gives time
convergence order frozen-opacity ~1.00 and exponential midpoint
~2.00 for 8–128 proper-time steps. Midpoint is the preferred local
short-interval prototype, not a replacement of the full Rust solver.

## Efficiency and memory

Physical 48-age source yields about 31k photon packets (q0: 31104),
with 1,244,544 bytes in three main packet arrays plus age starts.
The 3-state positive age representation retains 13 ages, ~9024 packets,
361,064 bytes; 1-state retains 8 ages, 5760 packets and230,464 bytes.
This is **packet-array memory** only, not full Rust solver RSS or
source/chemistry snapshot RAM. Exact zero-age packet pruning has no
effect on the fixed compression outcome.

OS-process scheduling for 3 independent signed q reference jobs
is benchmarked with fresh spawn and BLAS threads fixed at 1, three
repeats each: median 1-worker2.5706s, 2-workers2.2091s,
3-workers1.6900s (1.52x vs one process). Outputs were compared
at rtol2e-12 and atol1e-11. This timing is specific to this C12
workload, not source07 production Rust transport.

## Scientific stop condition / next

No default rei_bianchi Rust attachment is justified: the
unattenuated source-age reservoir is a major physics surrogate,
and the owner radiation Jacobian R*J was not recomputed inside this
reactor. Need actual source-age optical-depth/absorption along
rays and proper variable gas, electron, temperature, recombination
and cooling with spectrum evolution. Need independent continuum
multi-angle energy integration error and real receiver memory budget,
then owner-controlled SOURCE07 scientific gate. Existing AX08/
AX11/AX12 checkpoints unchanged. Release/admission HOLD.

Machine-readable next status is in NEXT_DAG.json and the
REI_SOURCE07_C8_HANDOFF_KO.md receiver guide. Evidence: results
folder JSON, figure and fresh test log.
