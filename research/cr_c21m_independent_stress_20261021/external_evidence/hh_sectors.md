# Matter / radiation 응력 분리: 사용자 요청 반영

주 관측량은 Sigma, Pi_m, Pi_r다. 이전 total-Pi 그림은 역사적 보조 결과로 보존한다. 원 방정식·source·63개 적분 결과는 변경하지 않았다.

## 정의

공통 normal orthonormal frame에서 pi=pi_m+pi_r다. H와 sigma는 proper-time s^-1, stress는 J/m^3이며 kappa_t=8*pi*G/c^2=c^2*kappa_E다. 기하학적 H_geom=H/c를 쓰는 kappa_E||pi||/H_geom^2와 같다.

Sigma_F=||sigma||_F/H,
Pi_m=kappa_t||pi_m||_F/H^2,
Pi_r=kappa_t||pi_r||_F/H^2.

각 sector의 signed work W_X=kappa_t sigma:pi_X/H^3를 별도로 저장한다. Total은 보조다. W_total=W_m+W_r이고
Pi_total^2=Pi_m^2+Pi_r^2+2 Pi_m Pi_r C_mr,
C_mr=(pi_m:pi_r)/(||pi_m||_F ||pi_r||_F).
한 norm이0이면 alignment는 undefined다. 두 norm을 단순히 더하지 않는다. 서로 반대인 유한응력은 total에서 상쇄될 수 있다.

LRS에서는 sigma=diag(-s,-s,2s), pi_X=diag(-p_X,-p_X,2p_X), p_X=(P_parallel,X-P_perp,X)/3다. S=sqrt(6)s/H, P_X=sqrt(6)kappa_t p_X/H^2, Pi_X=|P_X|, W_X=S P_X. 원 shear식 dot s+3Hs=kappa_t(p_m+p_r)는 유지한다. Non-tilted라는 이유로 pi_m=0을 강제하지 않는다.

## 현재 sector와 실행

Matter는 원 finite-mass nonbaryonic canonical Vlasov 성분이며 나머지 pressureless dust 응력은 원 모형에서0이다. Radiation은 photons+원 massless-neutrino 모형이다. 개별 photon/nu 압력은 CSV에 유지한다. 다른 owner는 species map을 명시하고 중복배정하거나 unknown channel을0으로 채우지 않는다. 동일 H/시점/frame으로 두 sector를 정규화한다. Full와 half norm을 모두 보존한다.

새 observer와 source-bound postprocessor를 추가했다. 63histories/5103samples를 재적분 없이 분리했다. 새 IVP/NCP/benchmark는0. 새 focused tests7개 PASS이며 cancellation의 RED→GREEN을 보존했다. 원 source/raw77파일의 hash는 불변이다. Native independent subagent는 NOT_RUN이다.

Scaled norm-square 잔차 최대1.0563197566626204e-15, work additivity 잔차5.977934429078968e-16. 이전 total Pi와의 절대차 최대4.336808689942018e-19는 signed species 합산의 roundoff 수준이며 continuum 오차경계가 아니다.

최종 Pi_m 범위[7.548594495683588e-21,4.288791630829764e-7], Pi_r 범위[4.9579330164210775e-20,2.40217968546317e-4]. 극값은 다른 case일 수 있으므로 합산하지 않는다.

## 중요한 sweep 구분

기존63case는 초기 A_m=0을 고정했다. Pi_m0 약2.11115e-19의 finite-quadrature residual은 그대로 남겼다. 새 (Sigma(t),Pi_m(t))와 (Sigma(t),Pi_r(t)) 그림은 sector 분리 후처리이며 독립 matter-initial-stress sweep이 아니다. Matter y축은10^-6, radiation은10^-3이고 원 표식은초기시점이다.

다음 독립 scan은 (signed Sigma0,signed Pi_m0,signed Pi_r0)와 원 admissible distribution을 입력으로 둔다. 첫pilot은 Pi_m0고정 (Sigma0,Pi_r0) 단면과 Pi_r0고정 (Sigma0,Pi_m0) 단면을 구별한다. LRS 부호 또는 일반tensor alignment도 보존한다. 기존63을 독립3Dscan 완료로 표기하지 않는다. Coupled C15의 closed stellar/escape budget, cold full EoR 및 continuum HOLD는 유지한다.

## Codex 인계

새 FULL sector archive의 manifest를 검증한 뒤 package에서 다음 후처리만 재현한다. 원63case는 다시 적분하지 않는다.

```sh
python -m unittest -v test_sector_diagnostics
python split_sectors.py --input results/control63 --out sector_check_new
python -c 'from split_sectors import plot_saved; plot_saved("sector_check_new", "sector_figures_new")'
```

REI PR213/current coupled owner에는 실제 matter/radiation tensor, 같은시각의 H, pi_s 또는 DeltaP와 단위를 확인한 뒤 lrs_sector_norms 또는 sector_tensor_norms를 연결한다. Warm81과 collisionless63을 같은모형으로 합산하지 않는다. 새case가 필요할때만 가용CPU/RAM을 나눠 실행하고 다른Codexsession을 veto로 삼거나 foreignjob에 signal을 보내지 않는다. 기존tol/deadline/완료job을 보존한다. HH_R10=OFF.

## 새 대화 인계

사용자가 matter와 radiation pi_ab를 별도로 요청했다. 주관측량은 Sigma/Pi_m/Pi_r이고 total은 보조다. SECTOR_DAG와 최신Git/backupreceipt를 읽고 실제coupledraw의 species분리와 초기조건자유도부터 확인한다. 이번수정은관측량·CSV·그림분리이며 독립3Dscan은 NOT_RUN이다. 원PHYS73/63case를 재실행하지 않는다. 원ownerPR147과source56db9f2는 그대로다.
