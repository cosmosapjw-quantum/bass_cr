# REI/BASS193 source-owned z20→2 Thomson receiver: 신규 물리 수치 결과

원본: `rei_bianchi` PR #311의 F4 CCC 첫 충돌 보존 아카이브에 포함된 이전 BASS193 plasma/species/time 장부. CCC 단면적/충돌 계산은 **사용하지 않음**. BASS-CR은 스냅샷 소비자 역할이고 실제 CMB/전자화학 owner는 REI/BASS에 유지.

## 동일 source clock의 193개 snapshot / 192개 구간

- **full21 saved**: `tau_trap=0.0693424244241088`; `tau_right=0.06891244972346135`; integrated probability `0.06699285906060412`; conditional mean scatter redshift `6.144596111100775`.
- **full21 instant static**: `tau_trap=0.07240148692225536`; `tau_right=0.07194856611276355`; integrated probability `0.06984262518730161`; conditional mean scatter redshift `6.324495093282358`.
- **H/He-only**: `tau_trap=0.06933986095899207`; `tau_right=0.06890990198176913`; integrated probability `0.0669904673262791`.
- static vs saved `Delta tau = 0.003059062498146553` (relative `4.4115309257675595%`); HHe vs full21 saved `Delta tau = -2.5634651167338873e-6`.
- Source H/He crosswalk endpoint relative residual max `7.879740832637817e-13`, full21-vs-HHe endpoint max relative `3.871556080000964e-5`.
- Finite-window discrete visibility conservation: `sum_j P_j = 1-exp(-tau)` absolute residual 0 in reported NumPy double computation.

## Interpretive correction

These are *two source-specified approximations* evaluated on the **same BASS193 frozen source history and proper clock**. They are neither independent cosmologies nor uncertainty confidence limits. The saved/full21 lane should not be replaced by the HHe proxy outside this dataset. The window ends at z=2 and starts at z=20, so no full CMB Thomson tau, cosmic large-scale CMB, spatial patchiness, Bianchi photon screen, tau total, or empirical likelihood is calculated.

The saved FLRW source can be sent as a **conditional scalar receiver regression** to BASS; the next central item remains the complete first canonical REI thermochemical interval, not this optional receiver output. Canonical/working/extension progress unchanged (`28/88` reported, `33/88` reported, `0/3`), `PRODUCTION=HOLD`.
