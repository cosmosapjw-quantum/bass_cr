# BASS_CR adaptive q-bins, true-child-moment supplier (2026-10-15)

실행 노드: `CR_ADAPTIVE_Q_GRID_FROM_ENVELOPE_WIDTH` (부모 `bass_cr` PR70 / commit `6898f3dd0ab5acff066fb0239339ec44c8d70398`). 이 패키지의 `src/adaptive_q.py`는 실제 현재 photon packet oracle에서 정확한 자식 `N,U_ref`를 생성하여 PR70 shape-free H/He event/heat 구간을 재계산하고, 불확실성 우선순위에 따라 q-energy cell만 세분화한다.

**중요:** 현행 `rei_bianchi` C7/C8의 `N,U`만 갖는 photon stock에서는 자식 moment가 결정되지 않는다. 이 모듈은 packet/source quadrature/새로 진화시킨 진짜 subbin moment가 없으면 독립적인 refinement/admission을 하지 않는다. 본 연구의 source 및 두-age packet은 별도 오라클이며, SOURCE07의 이미 승인된 numerical variant나 old49/guard51 산출물을 바꾸지 않는다.

기본 성능·과학 실험:

```bash
python3 -m pip install -r requirements-dev.txt  # 필요한 경우, 가상환경
PYTHONPATH=src pytest -q tests
PYTHONPATH=src python3 src/adaptive_benchmark.py --base 64 --max 128 --uniform 96 128 --priority HEI
PYTHONPATH=src python3 src/adaptive_benchmark.py --base 64 --max 128 --uniform 96 128 --priority HEI --hardened
PYTHONPATH=src python3 src/prefix_benchmark.py
PYTHONPATH=src python3 src/adaptive_parallel.py --rays 4
python3 verify_package.py
```

물리 변인: reference q-energy in eV, physical `E=R Eref`, proper seconds, neutral proper cm^-3, signature (-,+,+,+), photon count per original H. Original emitted BB50k source: MD14 native48, `fesc0.2`, physical 13.6..100eV and q support13.6..433eV. Verner fit cutoffs13.60/24.59/54.42eV, physical binding13.598434599702/24.587389011/54.41776eV separate. Angular Jacobian `R J_Omega` is external owner responsibility, never introduced here.

출력 인증 범위: **이미 주어진 실제 packet의 정확한 dyadic mass/first moment 및 진짜 support를 조건으로 한 국소 고정-gas 한 단계 shape-free event/heat 포함구간**. Decimal85/mpmath interval/Fraction 경로는 원본 PR70 의존 코드로 보존했다. 정확한 원 photon 법칙/Verner fit의 물리적 불확실성·전체 H/He/Tg history 오차는 미포함. `HOLD_PRECISION_TARGET`는 failure이 아니라 목표 폭 미달을 의미한다.
