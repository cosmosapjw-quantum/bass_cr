# BASS-CR PHYS23 | 실행 결과 보고

## 실제 수행한 연구

원본 PHYS22의 2,066개 source event에서 얻은 10개 조건부 방향·6CCO 계수 세트(5 E1 각도분포×35/40 eV 상단 앵커), earliest/latest 광자 수를 새로 조작하지 않고 대각 Bianchi-I의 source-to-observer null-geodesic 전달 연산자에 넣었다. 배경은 *원본 CR Einstein 해가 아닌* 네 개의 명시적 무차원 trace-free 누적 shear: (0,0,0), (2,2,−4)×10^-6, (−2,−2,4)×10^-6, (3,−3,0)×10^-6이다. 각 ray의 출발방향·관측자 적색편이·화면 평행이동, PHYS15 A21/100K 자연폭과 Doppler Voigt를 연결했다. 앞선 PHYS22는 방향마다 각 시점 광자 방출 Stokes를 만들었지만 시공간 전달을 계산하지 않았다. 따라서 이번 신규 물리 성과는 source-authentic photon count를 새로운 Bianchi-I 자유전파 연산자에 넣은 것이다.

## 신규 산출물

- `results/BIANCHI_3D_SKY_STOKES_92160.csv`: 92,160개의 세분된 조건부 Stokes I/Q/U/V, emission ray n_e, 관측주파수 ν_o, Jacobian r^3 및 100K line-centre Doppler offset. 24 GL theta×48 phi의 공간상 1,152 ray ×80 physical scenario combinations.
- `results/BIANCHI_ANGULAR_LYA_SPECTRA.csv`: 46,800개의 angle-frequency I/Q/U spectra with Voigt natural broadening and geometric redshift. 80 combinations ×9 observer rays ×65 Doppler offsets x∈[−16,16]. **유한 관측 window는 Voigt wing의 전량을 포함하지 않는다.**
- `results/BIANCHI_ANGLE_NORMALIZATION_80.csv`: 80개의 photon-number, angular-quadrupole, energy and screen checks, original-source earliest/latest totals retained.
- 네 과학 그림, reproducible code, 19/19 normal and 19/19 `python -O` tests, one same-author blind-referee pass, 20 R/C stage snapshots.

## 대표 수치 결과

- nu_Lyα=2.4660588682175665×10^15 Hz, Δν_D=1.0566205589679062×10^10 Hz, natural Voigt a=0.004718296433444188 (100K, PHYS15 A21).
- `max |N_obs/N_em−1|` 4.4408920985×10^-16 (80 scenarios); `max |R^T R−1|` 1.7763568394×10^-15.
- 등방 광전자 조건부 source의 축대칭 shear Δβ=(2,2,−4)×10^-6에서 관측 intensity angular quadrupole q20=<P2(nz)>=+2.400002058×10^-6, 부호 반전 shear에서 −2.399997942×10^-6. 이 경우 Q=U=V=0 정확히. 1차 유도 <P2>=6s/5와 일치.
- triaxial shear에서 화면 평행이동의 최대 기저 회전 약 2.98556166×10^-6 rad. 관측 line-centre offset 범위는 최악 shear에서 약 x∈[-0.920,+0.920] Doppler units, 원본 Lyα 중심에서 양방향으로 shift.
- 원본 PHYS22 관측자 atlas의 420 pole-free source directions와 정확히 zero-shear 회귀 검증, 직접 좌표계 4-vector 평행수송 ODE 대조 시험 PASS. 19개 표준 및 19개 최적화 테스트 모두 PASS.
- [12×24,24×48,32×64] 각도격자에서 sky quadrupole와 energy ratio consistency: 등방 축대칭 s=2e−6에 대한 <P2> 2.400002057e−6, 2.400002058e−6, 2.400002058e−6; 이는 검산 범위이며 연속 각도 해의 전역 오차 상한이 아니다.

## 가장 중요한 경계

- 이번 배경 계수는 합성 shear이다. 검증된 원본 Einstein–Boltzmann/REI-BASS 물리적 background shear나 source epoch이 아니다. 따라서 “source-owned Bianchi sky”나 관측량·통계 추론으로 승격하지 않는다.
- source photon emission의 원본 지리 방향, 편광, emission age 및 Bianchi tetrad owner 아직 미결합. 입력 PHYS22 E1 방향장 자체는 조건부 초기값이다.
- PHYS16 recoil/Fokker-Planck/atomic full RII scattered redistribution and opacity/balance not injected. Voigt source is a **bounded microphysical diagnostic**, not photon escape or a complete transfer function.
- 중앙 DAG 28/88 Δ0, 확장 DAG 0/3 Δ0, PHYS23 scoped auxiliary 1/1 CONSTRUCTED_REVIEW_HOLD, production/native25/L4 HOLD, no merge/force push/auto-next. Different-author R06/C09 and native subagent NOT_RUN.

## 다음 실제 생산 연결

PHYS15의 원본 누적 2p event 시간 이력과 원본 광자 birth epoch을 확보해 각 source event의 실제 injection u 및 tetrad를 정의한 뒤, 원본 CR-compatible Einstein–Bianchi `a_i(u)`로 null-ray geodesic을 구동한다. 일치하지 않는 BASS KM2N source ray는 외부 조건부 geometry validation에만 사용한다. 이후 source emission×direction×time field를 물리적 HI-resonance cross sections and RII에 넣어 첫 산란을 계산하고, 총광자 수/양성/공변량/선폭 보존 및 구간 통계 불확실성을 재검증해야 한다.