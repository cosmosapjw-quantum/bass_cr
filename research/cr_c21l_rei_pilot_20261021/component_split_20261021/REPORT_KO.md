# C21L 물질·복사 응력 분리 결과

## 결과와 원자료

고정 content `60a3f1cb0d8f0875820d18c0d10c448d480334c4`에 게시된 81개 LRS collisionless trajectory, 총 8,181개 저장 시점을 후처리했다. 원 Einstein–Vlasov / photon / massless-neutrino source는 REI `3b85dedce84d37b3e165da00685a8a984950aafe`이며 40성분 state, FP64, 원 quadrature, DOP853 허용오차를 그대로 재사용한다. 이 단계의 물리 ODE 실행은 **0회**다. 미게시 추가분 원파일은 확인한 저장처에서 회수되지 않아 새 postprocessor를 작성했으며, 이전 파일의 byte-identical 복원으로 주장하지 않는다.

Drive와 Library에서 실제 회수한 원 배송 ZIP은 5,476,701 bytes, SHA256 `ca1a806e50be55a3743182d1dd580c8654c9d795a1fcc5e51d09f77385789e7f`다. 352개 archive payload, 340개 게시 content의 SHA256 및 Git blob SHA1, REI source manifest의 9개 파일이 일치했다. Dropbox는 원 ZIP metadata만 확인했다. 상세 범위는 `RECOVERY_INTAKE.json`에 있다.

## 정의와 source 대응

Metric signature는 (-,+,+,+), source의 H_t와 s는 s^-1이다. 각 LRS tensor를

\[
\sigma_{\hat i\hat j}=\operatorname{diag}(-s,-s,2s),\qquad
\pi^X_{\hat i\hat j}=\operatorname{diag}(-\pi_{s,X},-\pi_{s,X},2\pi_{s,X})
\]

로 쓴다. 원 `Pi_*_J_m3`는 tensor norm이 아니라 signed scalar \(\pi_{s,X}=(p_{\parallel,X}-p_{\perp,X})/3\)다. 따라서

\[
\mathcal S=\sqrt6\,s/H_t,\quad \Sigma=|\mathcal S|,\qquad
\mathcal P_X=\sqrt6\,\frac{8\pi G}{c^2}\frac{\pi_{s,X}}{H_t^2},\quad
\Pi_X=|\mathcal P_X|.
\]

\(\kappa=8\pi G/c^4\)를 사용하면 \(H_{\rm geom}=H_t/c\)로 두어 \(\Pi_X=\kappa|\pi_X|/H_{\rm geom}^2\)와 같다. source의 half-contraction norm은 모든 성분에서 full Frobenius norm의 \(1/\sqrt2\)다. CSV/NPZ에는 두 norm과 signed coordinate를 별도 보존한다.

\[
\pi_{s,r}=\pi_{s,\gamma}+\pi_{s,\nu},\quad
\mathcal P_{\rm tot}=\mathcal P_m+\mathcal P_r,\quad
\Pi_{\rm tot}=|\mathcal P_m+\mathcal P_r|.
\]

Tensor 합을 먼저 계산한다. 상쇄율은 \(C=1-|\pi_{s,m}+\pi_{s,r}|/(|\pi_{s,m}|+|\pi_{s,r}|)\)이며 분모가 정확히 0이면 undefined로 남긴다. `cancellation_defined`와 raw NaN을 함께 저장한다. 그림에서만 \(\Pi_m+\Pi_r>10^{-12}\)를 적용해 수치 영점의 색 표시를 제외하며, 데이터는 clipping하지 않는다. 각 성분의 대각 tensor, pressure difference, signed amplitude, norm, \(\sigma:\pi_X=6s\pi_{s,X}\)도 보존했다.

물질 응력은 기존 massive nonbaryonic Vlasov species(f_m=0.1, m/T_ref=30)에서 온다. Cold dust는 모델에 존재하며 isotropic이다. Photon과 massless neutrino는 각각 존재한다. UV는 이 source에 없고 thermochemical reionization gas는 진화하지 않는다. 이 absent/unavailable 성분의 가상 zero 배열은 만들지 않는다.

## 정량 결과

초기 조건은 원 \(A=0\), signed \(\mathcal S_0\in[-0.04,0.04]\), signed total \(\mathcal P_{\rm tot,0}\in[-0.001,0.001]\)의 9×9 격자다. 적분 구간은 z=20→4다.

| z=4 endpoint | 이 81-case ensemble 최대값 |
|---|---:|
| \(\Sigma\) | 0.00481987955610218 |
| \(\Pi_m\) | 3.828814781835141e-6 |
| \(\Pi_\gamma\) | 1.728772226437296e-4 |
| \(\Pi_\nu\) | 1.1928604521942512e-4 |
| \(\Pi_r\) | 2.9216326786315474e-4 |
| \(\Pi_{\rm tot}\) | 2.9587955662661403e-4 |

40/81 endpoint에서 물질과 복사의 stress 부호가 반대다. 최대 상쇄 case `s08_p05`는 \(\mathcal S_0=0.04\), \(\mathcal P_{\rm tot,0}=0.00025\)이며,

\[
\mathcal P_{m,f}=-3.714216702960396\times10^{-6},\quad
\mathcal P_{r,f}=4.21102496639887\times10^{-6},\quad
\mathcal P_{{\rm tot},f}=4.968082634384734\times10^{-7},\quad C_f=0.9373131717409648.
\]

초기 isotropic massive 분포도 이방적 팽창에 따라 응력이 생긴다. 이 때문에 총 stress의 norm만 저장하면 matter/radiation의 상대 부호와 상쇄를 잃는다. 위 최대값은 지정 ensemble의 관측치이며 보편적 상계가 아니다. 이 단계에는 독립 \((\Pi_{m,0},\Pi_{r,0})\) 격자가 포함되지 않는다.

## 검증과 그림

새 tensor·SI 변환·상쇄·정확한 zero·missing species·부호 반전·입력 오류·create-only·결정적 NPZ 검사는 5개 그룹을 실제 실행했다. 모든 원 history SHA와 receipt identity를 확인하고 원 total signed 출력과 대조한 최대 절대차는 3.2526065174565133e-19, 정규화 component closure 잔차는 2.168404344971009e-19다. 원 Sigma와는 저장 샘플 전체에서 정확히 일치한다.

Git의 raw를 읽은 후처리와 독립 회수한 Drive raw를 다른 input/output 경로에서 읽은 후처리의 CSV·NPZ·PNG·PDF 및 manifest 11개 파일은 byte-identical하다. `PATH_REPRODUCTION_CHECK.json`이 실제 증거다. 별도 reviewer의 원자료·수식·그림 검토는 `REVIEW_COMPONENTS.json`에 기록한다. 기존 science suite는 재실행하지 않았다. `global_error_bound=null`을 유지한다.

- `results_final_v4/component_endpoints.png/.pdf`: 공통 signed 색상축의 물질·복사·총 응력. 세로축은 비균일 물리 격자의 **표본 행**을 동일 높이로 표시한다.
- `results_final_v4/signed_component_histories.png/.pdf`: radiation-only seed 및 shear-only seed의 양·음 branch. 각 행은 같은 대칭 세로축을 쓴다.
- `results_final_v4/norms_and_cancellation.png/.pdf`: nonnegative norm과 signed stress에서 계산한 상쇄율. 오른쪽 색은 초기 total signed coordinate다.

첫 시각 검토에서 상쇄 colorbar 누락과 양·음 이력의 개별 autoscale을 교정했다. full Frobenius signed coordinate와 nonnegative norm의 축 이름을 구별했다. 최종 파일은 `results_final_v4`만 채택하며 이전 local candidate는 게시 대상에서 제외했다.

## 외부 결과와 다음 작업

현재 일곱 관련 저장소의 advertised heads 1,224개를 확인했다. 이는 branch metadata 조사이며 모든 branch의 scientific 결과를 일괄 검증한 뜻은 아니다. REI PR198의 추가 물질600+혼합6 case는 같은 원 물리 source의 후속 결과로 수용할 수 있으며 재실행하지 않는다. 다만 reduced8/65 sample 및 half-contraction 입력을 원40state/101 sample의 C21L과 구별한다. REI PR213/BASS PR176의729 case는 warm a=0.1999→0.2의 UV 포함 lane이고, REC PR116은 그 저장 결과의 후처리다. 별도 provenance를 유지한다. 접근 불가능한 다른 대화는 UNAVAILABLE이다.

다음 C21M에서는 원40state를 유지하는 독립 초기응력 builder를 구현·검증한다. \(A\)를 바꿀 때 원 massive distribution과 normalization을 함께 재생성하고 초기 stress를 역산한다. 이미 완료된81·606·729 case는 실행 목록에서 제외한다. NCP는 이번 환경에 지정 SSH key가 없어 실제 접속·실행하지 않았으며, 공유 자원 admission과 준비된 신규 실행만 인계한다.
