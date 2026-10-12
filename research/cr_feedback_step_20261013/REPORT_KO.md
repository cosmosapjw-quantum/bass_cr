# 이번 연구에서 완성한 것

이번 연구는 직전 DAG의 **온도·H/He 조성 피드백을 포함하는 양의 보존적 한 step**을 구성했다. 사건마다 하나의 공통 extent를 사용하고, 같은 저장고를 소비하는 모든 사건의 부하를 분모에 공유한다. 이 map의 각 반복 단계에서 비음성과 핵수·전하·총 에너지가 유지된다. 여기에 온도와 조성에 따라 변하는 반응 계수를 넣고, 정의역의 보존·고정점 존재·수렴·온도 오차까지 유도했다.

연구 단위는 **CR-THEORY-FEEDBACK-20261013**이다. 날짜는 2026년 10월 13일 KST이며, 실제 작업 기록의 UTC 날짜는 2026년 10월 12일이다. 요청한 SciSpace와 Exa를 사용해 가까운 원전 네 편을 비교했고, Wolfram Language와 xAct로 공변 텐서 식 및 정확한 유리수 사례를 실제 계산했다.

이 결과의 대상은 현재 사건 열과 각 열의 실제 에너지가 고정된 유한 collision stage이다. 반응 계수의 온도·조성 의존성은 그 stage의 endpoint와 자기일관적으로 갱신된다. 주어진 Bianchi I geometry와의 합성에는 동일한 packet 상태를 만드는 angular lift와 에너지 장부를 명시했다. 가정은 다음 절과 CONTRACT.json에 모았다.

## 결과 지도

| 결과 | 완성한 내용 | 본문의 근거 |
|---|---|---|
| FB1 | 공통 사건 extent의 양수성·보존량과 양의 재고 하한 | ES-A/ES-B, FP1 |
| FB2 | 12개 상태·10개 사건의 H/He family와 유한 EOS | 사건 구성의 H/He 표 |
| FB3 | 양의 온도 정의역, 존재, 계산 가능한 수축 조건 | FP2–FP3 |
| FB4 | 반복·계수 근사·실제 시간 오차의 온도 전달 | FP4, FP6 |
| FB5 | 실제 반응 ODE에 대한 일차 일관성과 나머지 상계 | FP5 |
| FB6 | 공변 투영, Bianchi momentum/thermal map과 Lie step | CG.1–CG.11 |
| FB7 | 중성 비선형 사례의 정확한 endpoint와 실행 가능한 반복 | FP7, driver 검산 |

핵심 계산식은 다음과 같다. $S_{ir}$는 사건 하나가 상태 $i$에 주는 증분, $f_r(z;y^n)$는 초기 donor와 trial endpoint 계수로 평가한 비음 반응률이다.

$$
C_{ir}=(-S_{ir})_+,\qquad
c_i(z)=\sum_r C_{ir}f_r(z),\qquad
d_r(z)=\sum_{i:C_{ir}>0}\frac{c_i(z)}{y_i^n},
$$

$$
\boxed{
\xi_r(z)=\frac{h f_r(z)}{1+h d_r(z)},\qquad
\Phi_h(z)=y^n+S\xi(z).
}
$$

초기에 0인 저장고를 소비하는 사건은 그 step에서 비활성화한다. 활성 사건은 각 소비 저장고의 총 부하를 공유하므로

$$
\sum_r C_{ir}\xi_r
\le\frac{h c_i}{1+h c_i/y_i^n},\qquad
[\Phi_h(z)]_i\ge\frac{y_i^n}{1+h c_i/y_i^n}>0
$$

를 만족한다. 임의의 보존 행 $\ell^TS=0$에는 $\ell^T\Phi_h=\ell^Ty^n$이 성립한다. 따라서 수렴 전 iterate도 동일한 물리 장부 안에 머문다.

# 현재 가정과 재사용한 근거

## 물리적 상태와 closure

공행 셀의 수 상태는 active 전자, H/He 원자·이온, thermal 전자를 구분한다. 에너지 상태는 thermal kinetic energy $U$, 현재 active packet의 실제 kinetic energy, 원자의 누적 ionization energy, 방출 복사 에너지를 함께 센다. Thermal EOS는

$$
T=\frac{U}{c_v(N_H+N_{He}+N_{e,\mathrm{th}})},\qquad
c_v=\frac32k_B
$$

다. 열적 원자핵 수 $N_H+N_{He}>0$는 이 EOS의 양의 분모 하한이다. Active 전자는 자신의 에너지와 입자수 상태에 유지한다.

이번 H/He 예시는 ground-state family와 무거운 원자핵의 반동 에너지 생략을 사용한다. Recombination은 양의 고정 captured-energy node로 분해하고 그 rate weight에 온도 의존성을 넣는다. 이 표현 덕분에 동일 사건 열이 kinetic, chemical, radiation 장부를 정확히 연결한다. 표의 무차원 유리수 검산 입력은 이 구조를 판별하기 위한 것이다.

계수에 저온 특이성이 있으면 양의 초기 열에너지 $U^n$에서 온도 하한을 구성한다. Coulomb-log 형태를 사용하는 경우에는 지정한 $0<n_{\rm lo}\le n\le n_{\rm hi}<C^2$의 양의 구간과 실제 count functional, 부피, 미분 상계를 함께 결속한다. 이 조건은 정칙한 일반 계수에 필요한 가정과 구별해 본문에 기록했다.

Geometry에는 metric $(-,+,+,+)$, 주어진 양의 diagonal scale factor, 초 단위 고유시간을 사용한다. Thermal sector는 유지된 등방 단원자 ideal-fluid closure로 운반하고, active sector는 실제 비등방 응력과 운동량을 운반한다. $c$와 $k_B$는 계산식에 남겨 두었다. 현재 collision의 angular chart는 초기 packet 상태를 그대로 표현하고, 연속 collision field와 이산 map에 동일하게 사용한다.

## 직전 루프에서 유지한 결과

직전의 과학 commit은 \texttt{2495662e86a69ed822ec192685c3e9e0e68e1255}이며, 확인한 branch head는 \texttt{3bac8c6d00da0ae2eabc3cb7ba16acd64ec1c54e}다. 그 단계의 proof·코드·결과 중 이번 유도에 필요한 8개 과학 파일의 SHA-256을 원 근거와 대조해 재사용했다.

| 재사용한 결과 | 이번 사용 |
|---|---|
| 이동 cutoff의 signed number·energy moment | Geometry 후 실제 packet energy의 thermal 편입 |
| Thermal/all-free 표현의 정확한 동치 | Active와 thermal count의 EOS 소유권 |
| 유한 입자 편입의 EOS | Impact·재결합·terminalization의 온도 갱신 |
| 상태·에너지·입자수 오차의 온도 전달 | FP4와 FP6의 온도 certificate |
| 실제 Coulomb 밀도 변화의 분해 | 양의 density domain과 rate perturbation 연결 |
| 충돌 시계 및 prescribed expansion | 현재 고유시간 반응률과 geometry의 연결 |

현재 결과는 위 증명을 다시 실행하지 않고 새로운 nonlinear 연결을 유도한 것이다. 동일 identity를 가진 이전 과학 검산의 재실행은 0회다. 전체 이력과 정확한 파일 대응은 inputs/PRIOR_REUSE.json 및 원 단위의 HANDOFF.json에 있다.

# 피드백을 닫는 계산 절차

입력은 현재의 사건 열 $S$, 보존 행, 초기 상태, 부피와 고유시간 step, 계수 evaluator 및 유효 정의역이다. 이 자료에서 각 계수의 상계와 미분 상계를 구한 뒤 다음 순서로 계산한다.

1. 보존된 핵수·전하·에너지로 상태와 thermal count의 유한 상계를 구한다.
2. $T_{\rm floor}=U^n/(2c_vN_{\max})$와 $T_{\rm ceil}=E_{\rm tot}/(c_vN_{\min})$로 coefficient domain을 구성한다.
3. $h\overline c_U\le U^n$를 만족시켜 thermal energy가 $U^n/2$ 이상 남게 한다.
4. EOS, fraction, density의 변화에서 rate Lipschitz 상계를 계산하고 본문의 $q<1$ 조건으로 step을 정한다.
5. 초기 상태에서 $\Phi_h$를 반복하고, 실제 반환 상태의 residual을 새로 평가해 온도 허용오차를 확인한다.
6. 실제 ODE의 endpoint defect도 평가할 경우, FP6의 재구성 적분으로 시간 이산화까지 포함한 온도 오차를 얻는다.

$z$에서 측정한 residual을 $\rho=\|\Phi_h(z)-z\|_{\infty,a}$라 하면 이산 endpoint까지의 오차는

$$
\|y^\star-z\|_{\infty,a}\le\frac{\rho}{1-q}
$$

다. 실제 연속 반응계의 endpoint에는 별도로

$$
D_{\rm end}
=\left\|\frac{z-y^n}{h}-G(z,t_n+h)\right\|_{\infty,a}
$$

를 사용한다. FP6은 $D_{\rm end}$와 상태·시간 Lipschitz 상계에서 실제 한 step 오차를 직접 구성한다. 두 식은 구현의 서로 다른 출력 필드에 대응한다.

# 정확한 비선형 사례와 해석

전하 중성인 hydrogen 사례에서 active 전자 하나의 kinetic energy를 $4E_0$, ionization threshold를 $E_0$로 둔다. 사건과 초기 상태는

$$
A(4E_0)+H^0\longrightarrow H^++2e_{\rm th},
\qquad \Delta U=3E_0,
$$

$$
(A,H^0,H^+,N_e,U/E_0)^n=(1,1,1,0,1)
$$

다. Extent $x$에 대해 $\vartheta=c_vT/E_0=(1+3x)/(2+2x)$이고, 온도와 ion fraction에 의존하는 계수를 선택하면 proposal이 $f/\kappa_0=(3+5x)/2$로 단순해진다. $\eta=h\kappa_0=4/17$에서

$$
\boxed{
x^\star=\frac14,\qquad
\frac{c_vT^\star}{E_0}=\frac7{10},\qquad
q=\frac{170}{841}.
}
$$

최종 상태는 $(3/4,3/4,5/4,1/2,7/4)$다. 전체 에너지는 처음과 같은 $6E_0$, 전하는 0이다. 실제 연속 질량작용률을 같은 endpoint에서 평가하면 extent defect는 $-17\kappa_0/128$이다. 이 값은 이산 고정점의 정확한 해를 구한 뒤에도 시간 이산화의 잔차를 정량적으로 계산할 수 있음을 보여 준다.

![정확한 feedback map과 같은 extent가 연결하는 energy 장부. 점은 x=1/4의 정확한 고정점이다.](../figures/feedback_construction.pdf)

Reference driver는 이 사례를 SI $k_B$를 유지한 $E_0=(3/2)k_B(1\,\mathrm K)$로 실행했다. 15회의 accepted update, 16회의 map 평가 후 다음 결과를 얻었다.

| 항목 | 실제 결과 |
|---|---:|
| 정확한 해에 대한 온도 오차 | $6.290324474015892\times10^{-14}\,\mathrm K$ |
| 반환한 온도 오차 상계 | $2.31157671764639\times10^{-13}\,\mathrm K$ |
| 종료 허용오차 | $10^{-12}\,\mathrm K$ |
| 검사한 방문·인증 상태 | 17개 |
| 각 상태의 핵수·전하·에너지 잔차 | 정확히 0 |

Fraction 계산으로 위 상계를 유리수 그대로 보존했다. 별도 제한 종료 사례에서는 한 번의 update만 허용해, 양의 상태와 보존량을 유지하면서 \texttt{MAX\_ITERATIONS}와 실제 오차 상계를 반환했다.

# 전체 유도

다음 세 장은 공통 사건 구성, nonlinear feedback의 정리, 공변 geometry 연결의 전체 유도다. 정리의 조건·계산식·유효범위와 구현 대응을 포함한다.

<!-- DERIVATIONS -->

# 새 검산과 독립 검토

## 실제 실행 결과

| 실행 | 검사 수 | 결과와 대상 |
|---|---:|---|
| 사건 reference, Python Fraction | 9 | 양수성, 공유 energy capacity, 40개 invariant column residual, EOS, local-order 사례 |
| 피드백 driver, Python Fraction | 2 | 정확한 해에 대한 종료 certificate, 제한 종료의 실제 상태 |
| Wolfram, feedback 대수·적분 | 14 | 정확한 endpoint, 수축 상계, 물리적 defect, Grönwall 적분과 극한 |
| Wolfram+xAct | 4 | 공간 응력 직교성·무흔적성, 에너지 투영, 입자수 current |
| Wolfram, prescribed geometry | 5 | 운동량·상대론적 energy·thermal work·응력 분해·장부 |

Wolfram의 23개 named check는 모두 0 residual을 반환했다. Momentum check의 세 성분을 세면 scalar residual은 25개다. Python의 새 연결 검산은 합계 11개다. 이 숫자는 각 실행 파일에서 정한 검사 그룹 수이며, 문서나 검색 건수는 포함하지 않는다.

Wolfram kernel은 15.0.1 for Linux x86 (64-bit), xTensor는 1.3.0, xPerm은 1.2.4다. 공식 xAct 사이트의 xCore/xPerm/xTensor 파일을 내려받아 SHA-256을 확인한 뒤 불러왔다. $xpermQ=False$인 지원 Wolfram Language backend로 tensor canonicalization을 실행했다.

xAct에 입력한 응력은 임의의 대칭 $S^{ab}$를 공간 projector로 투영한 뒤 trace를 뺀 구성이다. 최종 energy identity를 simplification rule로 삽입하지 않았다. 입력 규칙은 metric compatibility, unit timelike normalization, 그 미분 및 응력의 정의다.

초기 external permutation 경로에서는 metric의 covariant derivative 정의가 끝나지 않는 오류가 발생했다. 같은 공식 소스의 지원 backend를 바꾸어 문제를 해결했고, canonical 원출력에는 정상 버전·hash와 네 개의 0 residual을 기록했다. Scalar 극한 계산 중 발생한 \texttt{Power::infy}/\texttt{Infinity::indet} 메시지도 원출력에 보존했다. 최종 극한값과 독립적인 해석 전개가 FP.40의 연속 정의와 일치한다.

## 독립 검토와 반영

후보를 작성하지 않은 검토자가 사건 구성, feedback proof, geometry, 코드와 실제 원출력을 읽고 독립적인 논증으로 검토했다. 검토 중 발견한 참조 경로 한 건, 시간 정확도에 필요한 Lipschitz 조건, bin-to-packet angular lift의 연결을 원문과 계약에 반영했다. 최종 판정은 PROMOTE_SCOPED / PASS이며, FB1–FB7과 두 reference 구현을 승인했다. 열린 차단 지적은 0개다. 각 지적의 해결 상태와 채택 범위는 review/DECISION.json 및 review/REVIEW_KO.md에 결속했다.

사건 소비량의 양수성은 실제 전체 donor load를 사용한 상계로 검토했고, FP6은 선형 경로의 residual을 직접 적분해 확인했다. Geometry에서는 $c$의 위치, 상대론적 pressure work, signed work ledger 및 $h=0$에서 항등인 angular chart를 확인했다. 기존 과학 실행을 독립 검토자가 반복한 횟수는 0회다.

# 구현과 재현

작은 유한 입력의 exact reference는 Python 표준 라이브러리만 사용한다. 핵심 함수는 \texttt{capacity\_step}와 \texttt{solve\_feedback}이다. 전자는 공통 사건 extent, 새 상태, 총 donor load와 잔여 하한을 반환한다. 후자는 주어진 $q$ 및 domain 근거에 따라 반복하고, 반환 상태와 그 상태의 residual을 측정한 다음 map image를 각각 보관한다.

Driver의 계약은 입력된 수축 상계와 domain이 별도로 검증되었다는 것이다. 방문 상태가 domain 안에 있는지와 수치 범위는 실행 중 확인한다. 계수 표나 부동소수점 evaluator를 사용할 때에는 그 평가 오차 상계를 함께 제공한다. 실제 continuous rate evaluator를 전달하면 physical endpoint defect가 추가로 반환된다.

재현 자료에는 다음이 포함된다.

- 전체 Markdown 유도, 계약, 가정과 error map.
- H/He event family, exact reference code와 두 실행 파일.
- 실제 Wolfram/xAct 코드, package SHA-256, 원출력과 정규화한 결과.
- 독립 검토, 이전 근거의 identity, 새 DAG와 계획.
- LaTeX 전체 원고, PDF, figure와 사용 폰트 정보.

Python 검산은 제공한 \texttt{checks/run\_event\_checks.py} 및 \texttt{checks/run\_feedback\_checks.py}로 재현한다. 이론을 읽거나 다음 연구를 재개할 때에는 유지된 결과와 identity를 먼저 재사용한다. Wolfram 코드는 stateless kernel에서 각 파일을 독립적으로 평가하도록 작성했다. xAct bootstrap에는 공식 다운로드 URL와 hash가 들어 있다.

# 다음 연구 지점

완료한 feedback node 다음에는 두 이론 연결을 병행할 수 있다.

첫째는 **현재 실제 에너지 격자와 atomic daughter 자료를 사건 열에 결속하는 adapter**다. 현재 식 $L_{\rm current}S=0$을 유지하는 양의 분해와 interpolation의 미분 상계를 구성하면, FP3의 step 조건과 FP4의 rate-table 오차를 실제 kernel 입력으로 평가할 수 있다. 기존 원자 계산을 다시 실행하는 작업에 앞서 이 연결을 수행한다.

둘째는 **온도 의존 cutoff의 implicit 경계 응답**이다. 이전 moving-boundary moment와 이번 EOS map을 이용해, cutoff의 변화가 thermal count와 energy에 주는 미분을 구성하고 self-map 조건에 포함한다. 현재의 고정 cutoff와 정칙 channel branch는 그 계산의 출발점이다.

선택된 물리 scenario에 적용하는 경로에는 source, 초기 상태, 관측량과 허용오차를 결속한다. 이 입력을 요구하는 기존 application node는 그 의미를 유지한다. 이번 단계에서 일반 조건부 유도와 유한 예제, reference 구현, 공변 검산을 완성했다.

# 문헌과 원전 비교

<!-- LITERATURE -->

## xAct 실행 근거

xAct의 공식 [xTensor](https://www.xact.es/xTensor/)와 [xPerm](https://www.xact.es/xPerm/) 자료, [설치 안내](https://www.xact.es/download/install)를 확인했다. xPerm의 tensor canonicalization 배경은 J. M. Martín-García, “xPerm: fast index canonicalization for tensor computer algebra,” Computer Physics Communications 179 (2008) 597–603, [arXiv:0803.0862](https://arxiv.org/abs/0803.0862)에 있다.


