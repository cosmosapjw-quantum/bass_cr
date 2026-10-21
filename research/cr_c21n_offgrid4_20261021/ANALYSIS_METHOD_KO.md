# C21N off-grid 4: 실행 반환의 제한된 분석 방법

이 하위 단계는 이미 준비된 네 입력의 새 실행 반환을 분석한다. 기존 C21L 81개와 C21M 125개 궤적, C21N 정적 검증은 다시 계산하지 않는다. `analyze_offgrid.py`는 ODE 적분을 호출하지 않으며, 고정된 원 source의 `fields`와 `rhs`를 저장 상태에서만 평가한다. 독립적인 원 solver 궤적 재실행에 의한 일치 검증은 `NOT_RUN`이다.

## 입력과 경계

물리 source는 REI `3b85dedce84d37b3e165da00685a8a984950aafe`, 실행 content는 BASS_CR `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9`이다. 실행 manifest의 canonical SHA256은 `f42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023`이다. 분석기는 정확한 네 입력, source·grid·code hash, 실제 sandbox 실행 표지, 각 case의 raw/receipt/complete seal을 확인한다. 기존 C21M loader는 변경하지 않고 C21N의 실행 코드 경로를 명시적으로 검사한다.

| Signed full-Frobenius $S_0$ | $P_{m,0}$ | $P_{r,0}$ |
|---:|---:|---:|
| 0 | $-1.75\times10^{-4}$ | $+1.75\times10^{-4}$ |
| 0 | $-7.5\times10^{-5}$ | $+7.5\times10^{-5}$ |
| 0 | $+7.5\times10^{-5}$ | $-7.5\times10^{-5}$ |
| 0 | $+1.75\times10^{-4}$ | $-1.75\times10^{-4}$ |

각 경우는 $z=20$에서 $4$까지 40성분 FP64 상태를 101점에 저장한다. 원 solver·허용오차·L8·momentum grid·species는 고정돼 있다. 이 네 입력은 기존 125개 Cartesian 격자 사이에 추가된 불규칙 표본이다. 합계 129개를 새로운 Cartesian sweep라고 부르지 않는다.

## 성분과 정규화

원 source의 `Pi_*_J_m3`는 signed scalar $\pi_{s,X}=\Delta p_X/3$이다. 원 LRS 축에서 $\sigma_{\hat i\hat j}=\mathrm{diag}(-s,-s,2s)$, $\pi^{(X)}_{\hat i\hat j}=\mathrm{diag}(-\pi_{s,X},-\pi_{s,X},2\pi_{s,X})$이다. 따라서

$$S=\sqrt6\,s/H_t,\qquad P_X=\sqrt6\,(8\pi G/c^2)\,\pi_{s,X}/H_t^2,$$

$$\Sigma=|S|,\qquad\Pi_X=|P_X|.$$

여기서 $H_t$의 단위는 $\mathrm{s}^{-1}$이다. 에너지 단위 Einstein coupling $\kappa_E=8\pi G/c^4$를 사용할 때는 $H_{\mathrm{geom}}=H_t/c$와 대응한다. Full Frobenius 값은 원 half-contraction 값의 $\sqrt2$배이다. 물질, photon, massless neutrino, radiation 합, total의 signed scalar·tensor 대각·norm·shear 수축을 모두 보존한다. Radiation과 total은 성분 tensor를 더한 뒤 norm을 취한다.

상쇄 지표는 $C=1-|P_m+P_r|/(|P_m|+|P_r|)$이며 분모가 0이면 정의되지 않는다. 실제 FP 잔여응력과 상쇄값은 clipping하거나 물리적 0으로 치환하지 않는다. Source의 massive matter와 isotropic dust, 실제 photon·massless neutrino, absent UV와 unmodeled baryonic anisotropic stress 표지를 그대로 보존한다.

## 404개 저장 상태에서 수행하는 검산

1. 원 C21L 성분 분해와 C21M 물리 검사를 그대로 재사용한다. Hamiltonian constraint, massive 입자수, radiation monopole/입자수, 초기 target, full/half convention, signed closure와 상쇄 범위를 검사한다.
2. 각 새 입력을 C21N builder로 재구성하고 mapping dictionary와 초기 40성분 bytes를 실행 receipt/raw에 대조한다. 원 uncached M template에 기록된 $A_m$, 공통 radiation $k$, source shear parameter와 orientation을 넣어 원 분포·정규화를 다시 만들고 초기 상태 bytes를 대조한다.
3. 네 궤적의 모든 404개 저장 상태에서 prepared/cached source와 원 uncached source의 전체 fields 및 RHS를 FP64 bytes로 비교한다. 원 fields와 raw 저장 fields의 비교는 정확한 수치 일치와 byte 일치를 별도 기록한다. 이 결과를 모든 adaptive solver 단계나 독립 적분 궤적의 동등성으로 확대하지 않는다.
4. 동결된 C21N analytic derivative 모듈로 massive energy, radiation energy, signed shear 항등식과 SI component/source forcing의 FP grouping 잔차를 계산한다. 이전 경우의 packet 배열을 보관하여 다른 $A_m$를 만든 뒤에도 그 bytes가 유지되는지 확인한다.
5. 원 radiation operator의 64개 Gauss 각도 노드에서 L8 $E_\gamma,N_\gamma,E_\nu,N_\nu$를 복원하여 최솟값을 기록한다. 이는 103,424개 이산 값의 표본 검사이며 연속 각도 전체에 대한 양성 정리가 아니다.

## 초기 jet과 기존 네 경우의 문맥

네 새 경우의 초기 actual jet는 실제 source의 작은 $P_{\mathrm{tot},0}$와 source forcing grouping offset을 보존한다. 이상적인 정확 상쇄 조건에서의 quadratic coefficient는 별도 필드이다. 최초 상태와 처음 일곱 양의 저장 시각에서 $S_{\mathrm{saved}}-S_{\mathrm{jet}}$ 및 상대 잔차를 측정한다. $\eta=0$에서 $S/\eta^2$를 계산하지 않는다. 3차 계수, 유한 구간 remainder 및 전역 오차 상계는 모두 `null`이다.

기존 네 opposing 경우 $P_{m,0}=\pm10^{-4},\pm2\times10^{-4}$의 곡선과 endpoint는 hash가 고정된 125개 결과 NPZ에서 읽는다. 기존 초기 jet는 동결된 C21N CSV에서 읽는다. 이전 궤적·초기 source·검사를 재실행하지 않는다. 그림은 새 경우와 이전 경우를 서로 다른 행/표식으로 나타내고, local jet 비교 열의 축을 공유한다. Parameter 공간의 보간 격자는 만들지 않는다.

## 실행과 산출물

```bash
python research/cr_c21n_offgrid4_20261021/analyze_offgrid.py \
  --input research/cr_c21n_offgrid4_20261021/raw_offgrid4 \
  --output research/cr_c21n_offgrid4_20261021/analysis
```

출력 경로는 create-only이며 존재하면 중단한다. `--repo`, `--context`, `--expected-identity`는 명시적인 외부 경로/승인된 실행 identity 결속을 지원한다. 소스와 모든 입력의 크기·SHA256을 분석 전후 비교하고 `INPUT_BINDINGS.json`에 기록한다. 분석기는 자체 임시 Matplotlib 설정 경로를 쓰고 정리한다. 과학 worker의 numeric thread 설정과 프로세스 전체 thread 수를 동일시하지 않는다.

NPZ에는 전체 40성분 $Y$, 다섯 응력 sector의 tensor·signed·norm 값, radiation multipoles, 저장점에서 평가한 원 RHS와 항등식 잔차를 보존한다. CSV에는 네 endpoint, initial jet, 404개 residual과 초기 표본 residual, 읽기 전용 기존 네 endpoint를 저장한다. PNG/PDF 세 쌍과 manifest·범위 제한 영수증을 함께 생성한다. PNG 직접 독립 검토와 PDF 별도 raster 검토 상태는 후속 review 영수증으로만 갱신하며, 분석 산출 manifest를 사후 덮어쓰지 않는다.

이 분석은 성능 벤치마크가 아니다. 실행 시간은 실행 receipt의 provenance이며 speedup·메모리 개선·64-core scaling의 측정 근거로 쓰지 않는다. 모든 결과의 해석 범위는 preliminary non-tilted collisionless LRS Bianchi I이다.
