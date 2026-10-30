# CR_PHYS07 | H/He ground-RR 광자의 화학 결합에너지 및 일차 전자 운동에너지 교환

## 범위 및 데이터 소유권

- 고정된 100 K H I/He I 중성 입자수밀도, 네 개의 proper-time 광자 발생 bin, H-origin 3200개/He-origin 3200개 전자·광자 에너지 원자별 기여.
- 모든 원본 광자 에너지·양의 weight 및 Verner (1996) H I/He I ground-state 광이온화 단면적은 PHYS06 원본 SOURCE ZIP에서 원래 owner 코드를 호출하여 읽는다.
- PHYS06 ZIP SHA-256 `6e2fe94051845612d06cbd880eb8c876a0c6692efbe6ef1f8408cd7784b0b764` 고정. 내부 PR130 ZIP 원본 해시도 PHYS06 source loader가 재검증한다.
- 광자 발생시각은 발생 bin [a,b]에서 각 weighted atom에 대해 미지이다. 현재 실험은 **earliest / latest / midpoint** 세 개의 명시적 전역 일관 이력만 계산한다. 시간별 경계값을 따로 극대화한 이력이라고 주장하지 않는다.
- 원자 내부의 전자 결합 기준 에너지는 각각 `I_H=13.60 eV`, `I_He=24.59 eV`로 원본 저장값에 고정한다. 재결합 전 전자의 운동에너지는 `epsilon=E_gamma-I_source`, 광흡수 후 *일차* 광전자의 초과 운동에너지는 `epsilon_out=E_gamma-I_target`.

## 사건별 엄밀한 에너지 항등식 [derived]

출생 종 s, 흡수종 a의 한 광자 E에서 첫 광이온화가 발생하면

    epsilon_out - epsilon_in = I_source - I_target.

이것은 단면적 근사와 무관한 결합에너지 항등식이며 eV 단위이다. 같은 종으로 되돌아가면 0, He-origin -> H I absorption은 +10.99 eV, H-origin -> He I absorption은 원본 E<24.59eV로 허용되지 않는다. `10.99 eV`는 이 포획 사건의 1차 전자 에너지 이득이며, 충돌 후 실제 열에너지가 아니다.

원래 frozen-opacity Poisson first absorption만 사용한다. 발생시각 t_b<=T, k(E)=c Σ_a n_a σ_a(E), f_a=n_aσ_a/(Σ n_bσ_b),

    P_survival=exp[-k(T-t_b)],  P_a=f_a(1-P_survival).

각 source atom weight w에 대해 t_b>T이면 unborn, 그렇지 않으면 다음 보존식이 성립한다.

    E = E P_survival + Σ_a [ I_a P_a + (E-I_a)P_a ].

이는 광자 방출 에너지 장부다. 단위 체적별로 출생 RR을 합산하면

    U_binding_released + K_preRR_selected
      = U_gamma_survivor + U_target_ion_threshold + K_post_photoelectron.

`U_binding_released=Σ_born w I_source`, `K_preRR_selected=Σ_born w (E-I_source)`와 `U_target_ion_threshold=Σ_abs w P_a I_a`, `K_post_photoelectron=Σ_abs w P_a (E-I_a)`이다. 광자 흡수 전 전자의 실제 분포함수 변화를 풀지 않으므로 이 등식은 사건-조건부 에너지 장부이지 열/온도의 진화방정식이 아니다.

같은 포획 사건에 대해 재결합 *전* 전자 운동에너지 입력분과 *후* 일차 전자 운동에너지 출력분을 비교하면

    ΔK_photo_event = Σ_{s,a} A_{s a} (I_s-I_a).

이번 원본에서는 유일한 비영(非零) 교차 채널이 He -> H I 이므로

    ΔK_photo_event = (24.59-13.60) eV × N_{He->HI}.

이는 He가 중성화되는 동시에 H가 이온화될 때 각 전자 수의 순변화 없이 결합에너지 차가 일차 자유전자 운동에너지로 전환되는 것을 뜻한다.

## 전하 및 원자수 장부 [derived]

    Δn_HI=R_H-Σ_s A_{s,HI},  Δn_HeI=R_He-Σ_s A_{s,HeI},
    Δn_e=-(R_H+R_He)+Σ_{s,a}A_{s,a}=-N_survivor.

출생/흡수된 광자만 고려하는 이벤트 수준에서 중성/이온 원자수와 전하가 정확히 보존된다. 이온화된 원자와 전자의 'net state'는 기존 원본 미량 광자 population을 스냅샷 고정된 중성 표적에 적용한 결과이지, 자연 시간에 따라 실제 자체 일관 chemical IVP를 풀었다는 의미가 아니다.

## 유효 범위와 배제

무한 우주에서의 escape, Bianchi 복사 redshift, 광자 재방출 cascade, 충돌/열화, 둘째 전자 생성, 반응계 Jacobian, 원래 physical K·exclusive He double-event kernel, native25/L4/production을 채택하지 않는다. 외부 BASS21/REI17 원본은 현재 같은 100 K 광자장/시계/화학상태라는 확인이 없다.

## 선행 문헌 범위

- Verner et al. 1996, ApJ 465, 487, DOI 10.1086/177435: source-bound 광이온화 단면적 근거.
- Switzer & Hirata 2008, PRD 77 083006, DOI 10.1103/PhysRevD.77.083006: He-origin 광자의 H I 흡수·helium feedback는 기존 물리다.
- Ercolano & Storey 2006, MNRAS 372, 1875, DOI 10.1111/j.1365-2966.2006.10988.x: free-bound 연속방출의 원전적 기준. 이번 계산은 해당 논문을 새 원본 소스로 교체하지 않는다.

## Claim gate

`derived` : 전하·광자·결합에너지·일차 e 운동에너지 항등식.  `implementation-verified` : 실제 원본에서 source-qualified 생성 후 재실행 검증.  `unresolved` : 실제 열, plasma 온도, neutral depletion/feedback IVP, expanding-universe source transport.  `R06`, `C09` : 다른 작성자 독립심사 전까지 NOT_RUN.
