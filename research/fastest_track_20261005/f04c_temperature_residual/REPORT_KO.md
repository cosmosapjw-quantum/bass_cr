# F04C: 온도 결합을 남긴 FT03 residual scope

이번 결과는 actual `ft03_controlled.rs::ft03_rhs` 및 `ft03_rates.rs`의 **exact-real formal 구조**를 정식화하고 검산한 보조 연구다. 계수 함수는 기호로 남기며 실제 provider 값을 새로 계산하지 않았다. production consumer/stepper 수정, native 실행, root solve, 임의 parent box 생성은 없다. F04A/B의 frozen-rate 3D certificate를 새 모형에 이전하지 않는다.

## 실제 source 선택과 범위

receiver observed HEAD는 `752e360a80e8622bcbaffae54183258b2e67b810`이다. FT03 원 구현 commit은 `6279036f06c9ba4d47574beab90b48fc2c6f9ba7`이다. 새 He RCT local wrapper는 opt-in이며 이번 FT03 source에서는 비활성이다. 실제 FT03는 별도 `ft03_rhs`를 호출한다. `model.gas.alpha/beta`는 0이므로 그 gas를 옛 `hhe_rhs`에 넣어 대체하면 RR/CI/DR가 사라진다.

static/proper HHe, nH>0,nHe>0, T∈[30000,110000] K, 고정 photon energy·Verner sigma 및 Case-A escape다. nHe=0인 과거 모형의 극한을 이 API의 허용 domain으로 만들지 않는다. expansion/FLRW boundary 또는 RCT channel을 추가하지 않는다. controlled constructor에서 EOS kB와 rate module KB는 같은 리터럴이지만 사용자 변경 상수를 자동으로 같다고 가정하지 않는다.

## 남겨야 하는 네 좌표

x=(xH,xHeII,xHeIII), l=(1-xH,1-xHeII-xHeIII,xHeII), d=(nH,nHe,nHe), ne=nH*xH+nHe*(xHeII+2*xHeIII), np=nH+nHe+ne, U(x,T)=3*kB*np*T/2.

고정 s_ag=c*sigma_ag에서 κ_g=sum_a d_a*l_a*s_ag, D_g=1+hκ_g, Nbar_g=N0_g/D_g. physical simplex, nonnegative sigma와 h≥0이면 D_g≥1이다. 이 **photon 소거만** 가능하다. sigma/energy가 stage·temperature에 따라 바뀌는 다른 consumer에는 조건을 다시 읽어야 한다.

P_ag=d_a*l_a*s_ag*Nbar_g, C_a=d_a*l_a*ne*β_a(T), R_a=d_a*x_a*ne*α_a(T), DR_k=nHe*xHeII*ne*αDR_k(T).

j_a=l_a*(sum_g s_ag*Nbar_g+ne*β_a)-x_a*ne*α_a, j_HeI에서 xHeII*ne*sum_k αDR_k를 추가로 뺀다. F=(j_H,j_HeI-j_HeII,j_HeII).

Q=sum_ag P_ag*(E_g-χ_a)*ev - sum_a C_a*χ_a*ev - sum_a d_a*x_a*ne*ΛRR_a(T) - sum_k DR_k*εDR_k.

L=sum_a [R_a*χ_a*ev+d_a*x_a*ne*ΛRR_a(T)] + sum_k DR_k*(χ_HeI*ev+εDR_k).

따라서 G=(x-x0-hF, U(x,T)-u0-hQ)이고 escape=e0+hL이다. ΛRR=kB*T*αRR*(1.5+g)이며 g=dlnαRR/dlnT다. DR kinetic energy는 source의 고정 kB*B1 또는 kB*(B1+B2)다. **옛 u=B/(1+h*Rsum/np) 소거는 이 Q를 풀지 않는다.** thermal row의 sign/monotonicity 또는 해 존재는 별도 domain 증거가 필요하다. T를 네 번째 좌표로 선택하면 physical simplex 및 T guard 내부의 U는 양수지만, 그런 root가 존재한다는 결론은 아니다.

## 저장 photon 밖의 잔차 전달

native 후보가 주어진 경우 동일 (x,T)에서 r_z=(x-x0-hF(x,T,Nhat),U-u0-hQ(x,T,Nhat)), r_N=D*Nhat-N0라 둔다. M은 species photo rate의 per-capita coefficient를 H/He stoichiometry로 조합한 3×3 행렬이다. heat row H_g=sum_a d_a*l_a*s_ag*(E_g-χ_a)*ev, B=(M;H)로 두면

    G(z) = r_z + h*B*D^(-1)*r_N.

이번 source에서는 escape L이 fixed (x,T)의 photons에 직접 의존하지 않는다. 그러나 이것이 T를 버리거나 escape의 native 산술 오차를 0으로 둘 수 있다는 뜻은 아니다. actual stored u에서 source가 계산한 binary64 T와 exact-real EOS T의 차이, source coefficient rounding, event assembly는 이번 formal 기호 검산에 포함되지 않는다. stored native rate bits는 새로 수집하지 않았으며 누락된 값을 events/dt로 제조하지 않는다.

## Jacobian과 온도 미분

z=(x,T)에서 dNbar/dx_i=-h*N0*∂κ/∂x_i/D², dNbar/dT=0이다. J의 species rows는 I-h*dF/dz, thermal row는 dU/dz-h*dQ/dz다. dU/dx_i=3*kB*T*(nH,nHe,2*nHe)_i/2, dU/dT=3*kB*np/2. `chain_jacobian`은 photons를 독립 변수로 둔 미분에 dNbar/dz를 조합하며, 직접 reduced residual의 미분과 16성분이 정확히 일치했다.

특히 species의 T column은 β',α',αDR'를 포함하고 thermal T row는 ΛRR'와 CI/DR kinetic 항을 포함한다. actual source 식에서 λ=L/T, v=(λ/C)^r이면

    T β'/β = -1.5 + λ/2 - p + d*r*v/(1+v)
    T αDR'/αDR = -1.5 + B/T
    ΛRR' = kB*αRR*((1+g)*(1.5+g)+T*g').

source의 `log_slope_derivative`는 T*g'이다. RR alpha 자체의 fit와 기존 coefficient 점 검증은 owner 근거를 계승한다. 이번 테스트는 위 새로운 chain/kinetic 미분 항등식이며 물리 fit 정확도 재검증이 아니다. 상수는 native binary64 연산의 rounding을 증명한 값으로 취급하지 않는다.

## 독립 장부·검증 결과

전체 binding+thermal+photon+escaped RHS 합은 exact-real 0이다. electron+photon RHS는 sum(C)-sum(R)-sum(DR)이고, 두 DR channel은 HeII→HeI의 동일 stoichiometry를 갖는다. escape와 thermal에 kinetic moment를 같은 stage에서 반대 부호로 사용한다. 이 검산으로 native time integration positivity나 physical energy accuracy가 인증되지는 않는다.

새 Python/SymPy 시험 **10개 PASS**, 실제 기록 wall=33.753881751 s, 자식 프로세스 peak RSS=65960 KiB, affinity CPU0. 기존 F04B42/원 native10/receiver 전체116/FLRW04 reference 등은 반복하거나 합산하지 않았다. 격리된 venv의 SymPy1.14.0/mpmath1.3.0을 사용했고 전역 환경은 바꾸지 않았다. 처음 intake에서 ZIP root 경로를 잘못 읽은 FileNotFoundError는 원본을 보존한 채 경로를 정정했다. 모든73 payload SHA는 이후 일치했다.

독립 agent/human review 및 proof-assistant 검증은 수행하지 않았다. symbolic coefficient functions는 formal proof 도구이며 실제 provider나 mock production 연결물이 아니다.

## 다음 입력과 ceiling

현재 REI-F04는 partial이며 `ACTUAL_PARENT_DOMAIN_NOT_FROZEN`이다. 실제 accepted augmented parent의 initial-state/time/source uncertainty 및 상관·topology가 필요하다. owner가 이를 고정하면 FT03 source-specific J/H·coefficient rounding·root enclosure와 original parent에 대한 half composition을 진행할 수 있다. full 후보 하나의 F04B 증거로 half1→half2 old-state enclosure 및 사건수를 대신하지 않는다. 이것은 canonical owner 작업이며 이번 결과는 새 mandatory gate가 아니다.

동시 receiver 연구의 다음 노드는 FLRW05_COHERENT_SPECTRAL_MEASURE이고, source stage·birth energy·edge measure 계약과 본 static residual을 구별한다. He RCT의 RCT-STEP01도 rei_bianchi 소유다. 해당 전수 suites/stepper를 BASS에서 대신 실행·구현하지 않았다.

CR_OFF_FASTEST, precision atomic PARKED. CR-F0=WAIT_FOR_ACTUAL_CR_OFF_DISPATCH_BINDING, source/loader/callback=null. G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO 유지. 직접 ChatGPT ACK는 미확인이다. 지정 스레드 https://chatgpt.com/c/6abfa205-dbe8-83ee-969b-0e00111c9404 에 대한 Git/cloud 동기화 반환이다.
