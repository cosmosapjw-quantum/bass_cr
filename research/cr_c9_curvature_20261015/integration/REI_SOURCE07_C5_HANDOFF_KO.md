# 실제 `rei_bianchi` SOURCE07 C5와의 호환 수신 계약

- 2026-10-15 실제 owner HEAD `129627969dae18958ceef520c197bfa8b20b8888` (확인 시점), SOURCE07 C4가 **fixed covariant-q energy/angular grid primary** 선택. 해당 결정과 AX07/08/11/12 status를 바꾸지 않는다.
- 이번 것은 `bass_cr`의 **local reaction/heat curvature error supplier**다. 방향 다른 q-rays, source-age, proper-clock 다른 두 photon을 결코 같은 cohort로 합치지 않는다. `e_bar`만 보존하면 다른 `e^a`의 photon momentum은 보존되지 않는다.
- Owner가 이미 제공하는 `(physical_E_eV, count_per_H, ray_id, age_tag, proper_clock, signed q/H)`를 받아 **동일 ray/epoch/clock lane**에서만 compress한다. Source Jacobian `R*J_Ω`은 기존 Rust q-ray producer가 정확히 한 번 적용한다. 원 13.6..100eV source를 새로운 432.23eV physical q-ray energy와 혼동하지 않는다.
- Photon sigma fit thresholds H13.60/HeI24.59/HeII54.42eV; binding H13.598434599702/HeI24.587389011/HeII54.41776eV. `DirectedCurvatureHeap(...,binding_eV=(...))`를 사용해 실제 direct heat 차원을 유지하되 frozen-neutral BE 범위에만 쓰며, density/time/redshift forecast가 바뀌면 반드시 재심사한다. `HOLD`는 변화 없는 원 상태를 뜻하고, 허용오차를 강제로 늘리지 않는다.
- Baseline example: 48→22 accepted, 20 HOLD with `n=(1e-3,8e-5,2e-5) cm^-3`, dt1e9s, rmin.995, separate per-species event0.01count/H heat1eV/H. **이 숫자는 AXBI normalized actual n(z) or q-ray packets가 아니다.**
- 실제 owner C5 contract는 q-grid pilot128×16/reference256×32/refinement512×32, source physical energy to432.229eV, 2GiB full memory cap, R*J measure, moving threshold splits, proper n(t), signed q, all H/He inventories/temperature, C5_A/B/C prior to C5_D. Those should remain owner-managed; our local rate-error supplier cannot by itself move any C5 owner DAG node to completed.
