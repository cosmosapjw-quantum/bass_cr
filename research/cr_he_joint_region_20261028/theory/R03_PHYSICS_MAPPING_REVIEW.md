# R03 — source-parent observable mapping 정적 대조

**판정: full-selected mapping 일치; 아래 선택·정규화·inventory 조건부.** 기존 `cr_he_event_union_20261028/implementation/event_union.py`의 `evaluate_event_set`, `consume_event_union`, `known_window_factor`와 새 `CONTRACT.json`만 읽었다. 과학 실행 0회이며 새 joint polygon의 정리·증명은 검토하지 않았다.

## 1. 전체 선택과 단위

먼저 모든 기호를 시간 적분 **이전 coefficient**로 정의한다. `N=sum_i w_i`, `d`는 모든 double-event mass, `C`는 서로 다른 birth bin의 double-event mass다. 네 partition을 모두 선택하면 outside-selected partner가 없어 `p=0`이고 다음 식이 기존 consumer와 일치한다.

\[
s=N-2d,\quad P=N-d,\quad
\Delta(n_{\mathrm{HeI}},n_{\mathrm{HeII}},n_{\mathrm{HeIII}})
=(-N+d,N-2d,d),
\]
\[
\Delta Q=N,\qquad
U=I_1N+(I_2-I_1)d,
\quad I_1=24.59\ {\rm eV},\ I_2=54.42\ {\rm eV}.
\]

이는 source의 조건부 증분이다. 원자핵 수는 보존되고 ionic charge는 선택한 birth electron 수와 같다. `d`가 chemical bookkeeping을 결정하며 `C`는 partition별 반환을 합칠 때의 중복 교정량을 결정한다. 고정 electron marginal의 수와 운동에너지는 `d,C`에 의존하지 않는다.

`q_i(t)=t w_i`, proper window `[a,b]`에서 `W=(b^2-a^2)/2`를 **한 번만** 곱해야 위 coefficient가 density가 된다. 기존 `evaluate_event_set` 반환값은 이미 `W`를 포함한다. native species·charge·birth number로 바꿀 때는 같은 상태의 `n_b=8750/47 m^-3`로 **한 번만** 나눈다. 운동에너지의 native J/baryon에는 eV→J 변환도 한 번 적용한다. 코드에 없는 native chemical 출력 필드를 기존 반환값처럼 주장하지 않는다.

전체 선택의 partition-sum→union 교정은

\[
\delta\mathbf n=W(C,0,-C),\quad
\delta Q=-2WC,\quad
\delta U=-(I_1+I_2)WC.
\]

electron-number·선택 운동에너지·RR·retained-photon 교정은 기존 consumer에서 0이다. union source **또는** corrected partition sum을 한 번 채택하고 같은 source를 다시 더하지 않아야 한다.

## 2. 부분 선택에서는 추가 기호가 필요하다

선택한 bin 집합 `S`에 대해 `N_S`는 선택 electron marginal, `d_S`는 두 electron이 모두 선택된 double mass, `p_S`는 double 중 정확히 하나만 선택된 mass다. 그러면

\[
s_S=N_S-p_S-2d_S,\quad P_S=N_S-d_S,
\]
\[
\Delta\mathbf n_S=(-N_S+d_S,N_S-p_S-2d_S,p_S+d_S),\quad
\Delta Q_S=N_S+p_S,
\]
\[
U_S=I_1N_S+I_2p_S+(I_2-I_1)d_S.
\]

각 식에 `W`를 한 번 적용한다. `p_S=0`을 보장하지 않은 partial selection에 full-selected 공식을 대입하면 안 된다. 중복 교정에는 **두 끝이 모두 S에 있고 서로 다른 bin에 속하는** `C_S`만 사용한다. 한 끝만 선택된 event는 선택 claims에서 한 번만 나타나므로 `C_S`에 포함하지 않는다. `C_S=C`는 전체 선택일 때 성립하며 임의 mask에 전역 `C`를 넣을 수 없다. 외부 partner의 physical response는 여전히 미지정이다.

## 3. 소비자 수용 조건과 제한

동일 source·atom digest·state·frame·proper window, 중복 없는 selected partitions, 일치하는 event ID 내용, 선택 marginal의 exact 복원이 필요하다. 고정 neutral He inventory 조건은

\[
W(N_S-d_S)\le H_{\rm neutral},\qquad
H_{\rm neutral}=\frac{1085}{94}\frac{99}{100}\ {\rm m}^{-3}.
\]

전체 선택에서는 `W(N-d)`를 검사한다. 따라서 inventory는 `C`만의 제한으로 대체할 수 없고, joint event-feasible 영역의 각 소비자 입력이 별도로 이 조건을 만족해야 한다. 기존 구현은 **호출별** inventory를 검사하며 `previous_windows`는 시간 중복을 거절할 뿐 누적 depletion을 계산하지 않는다. 새 계약의 단일 full window에는 이 차이가 충돌하지 않지만 다중 창의 누적 inventory 보증으로 확장하면 안 된다.

실제 `K`, exclusive He kernel, 실제 `d,C`, donor work, outside response, EOS/T, 절대 부피 및 full physical native25는 이 mapping으로 식별되지 않는다. `physical_activation=false`와 계약의 null 항목을 유지한다.
