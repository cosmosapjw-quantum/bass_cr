# CR-PHYS02C 연속 crossing source의 age-cohort 합성

Astra가 동결한 `CR-PHYS02C-CONTINUOUS-CROSSING-CONVOLUTION01` 계약을 하위 tier가 구현했다. 초기 1000.001 eV 전자 한 개, 고정 `Gas()` 100 K, gas-proper 시간 0..10^10 s의 조건부 계산이다.

첫 crossing의 source는 NIST HI 2p / HeI singlet rate를 이용한 해석적 지수함수다. 기존 packet은 source identity와 끝점 비교에만 사용한다. 989.797 / 978.783 eV 두 잔여 에너지를 각 P02B grid에 새로 투영하고, birth time별로 서로 다른 나이의 cohort를 실제 진화시킨다. 각 cohort의 이동 energy grid에서 observable을 먼저 계산한 뒤 source quadrature weight로 합한다.

상류 NIST HI 2p / HeI singlet excitation과 하류 old HI / HeI23s / HeII excitation energy 및 event count를 각각 유지한다. cutoff 에너지는 배분하지 않는다. boundary energy를 별도 reservoir로 다시 더하지 않는다. 전체 number/energy ledger와 각 branch ledger를 해석적 누적 crossing 수에 대해 검사한다.

동결 campaign은 sparse 진화 1,392회와 SSPRK2 160회, 합계 1,552회이며 각 호출은 두 energy column을 포함한다. Gauss-Legendre birth order16/32 비교는 grid512의 같은 19 panel에서만 한다. temperature나 gas 상태의 피드백, cosmological history, full physical/global admission은 HOLD다.

5개 zero-science control test가 통과했다. 최초 campaign은 1,552회 호출을 완료하고 exit 0으로 끝났다. `evidence/VALIDATION.json`과 별도의 `evidence/GROUP_ACCEPTANCE.json` 모두 수치 `PASS_SCOPED`다. 최초 실패나 재실행은 없다. 활성 bounded harness 파일은 접근 불가하여 `HARNESS_UNAVAILABLE`로 기록했다. 독립 Astra review도 `PASS_SCOPED`다. 검토자는 저장된 source, ledger, birth/grid/time 지표를 재계산하고 zero-science control만 확인했으며, 추가 비영시간 진화는 수행하지 않았다.

birth order16→32 최대 상대차는 1.8235208721e-8이다. grid H group 최대 오차는 1.1060814526e-7→4.2050684607e-8, He는 1.2437158617e-7→3.6506117976e-8, total은 1.1088309439e-7→4.1939922013e-8이다. 시간법 비교 최대 오차는 3.5393677442e-9이며, source / number / energy ledger 상대오차는 각각 1.3083275420e-15 / 1.0902729517e-15 / 1.0375315920e-15다. 모든 cohort 최종 state에서 finite/nonnegative 검사를 통과했다.

campaign elapsed wall은 1512.941277945 s, summed core process wall은 1874.047419678 s, measured core CPU는 1872.656966182 s다. Astra가 명확히 한 1800 s 제한은 첫 번째 campaign elapsed wall에 적용하며 외부 timeout command가 exit 0으로 끝났다.

Astra는 grid 오차를 H / He / total 세 group의 최대값으로 각각 판정하도록 명확히 했다. 실행 당시 validator의 전체 최대값 판정은 원자료로 보존하고, 추가 진화 없이 `analyze_groups.py`가 더 정확한 group 판정을 작성한다. 각 energy channel 자체가 모두 개선될 필요는 없으며 각 group 최대값이 개선되어야 한다.

실제 topology는 science worker 4개와 coordinator 1개, 합계 Python process 5개였다. Astra는 원래 cap의 뜻을 science worker 4개로 명확히 하고 이미 시작한 campaign을 완료하도록 지시했다. 4개 이하 total process였다고 주장하지 않는다. per-case CPU timer는 generator assembly 뒤부터 측정하므로 `CORE_CPU_MEASURED`, assembly/coordinator는 `UNKNOWN_NOT_ZERO`, 전체 process CPU 3600 s 이하는 `NOT_CERTIFIED`, 실행 accounting은 `PARTIAL_EXECUTION_ACCOUNTING`으로 유지한다. 수치 판정과 모든 실행 계약 조건 충족은 별개다.

재현 명령: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 1800s python3 validate.py`, 이어서 `python3 analyze_groups.py`로 필수 group acceptance를 판정한다. 기존 evidence가 있으면 실행기는 덮어쓰기를 거부한다. 이미 완료한 이 campaign을 현재 작업에서 재실행하지 않는다.

이 승인은 고정 bath에서 초기 upstream 전자 한 개당 계산되는 조건부 hybrid convolution에 한정된다. 연속체 오차 상계, volumetric CR injection, evolving gas, Bianchi/cosmological history 또는 global physical admission을 뜻하지 않으며 모두 HOLD다.
