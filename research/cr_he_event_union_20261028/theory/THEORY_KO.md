# He 사건 합집합과 birth-energy 분할 중복: 유한 원자 측도의 구성

단위: CR_PHYS02_HE_EVENT_UNION_V1. 이 문서는 호스트 리셋 전에 실제 작성·검토된 유도를 대화에 남은 산출물에서 복원한 것이다. 새 파일의 byte identity는 새로 부여하며 손실된 파일과 byte-identical하다고 주장하지 않는다. 수학적 내용을 아래에서 완결해 재사용한다. 이 복원에서 과학 runtime·CAS·기존 source fit·RR 재실행은 없다.

## 1. 고정된 입력과 질문

직전 PR111은 S=5c50071412964cb42fc06b96acf778ccd1a93e44, D=65e20e40e3c1d9e8384101017dc8940b3d09de09, M=ed6a899fa87ad42fbbb3569e96779bc3af716620이다. Retained PHYS02 revision=4ca5a90de79c8fb82a25fd9e83615bec0dfa870b; canonical source JSON SHA256=8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf. 저장 He attribution NPZ SHA256=1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47. 원본 bytes의 복구·검증은 별도 root receipt로 결속한다.

원 source는 q_j(t)=t A_j, proper t∈[0,10^10]s이며 구간 밖은 unknown이다. Gas-rest nonrelativistic scalar, zero recoil, fixed proper-volume density, absolute volume=null을 유지한다. Source neutral factor/proper729/angle/projectile speed/clock/energy normalization은 원 A에 한 번 포함돼 있다.

저장 low-birth source는 3200 active atoms와 E=0.1eV의 별도 cutoff ghost로 이루어진다. 저장 atom labels를 다음 네 disjoint 집합으로 나눈다.

| 집합 | 저장 label의 의미 |
|---|---|
| A0 | 별도 direct-cutoff ghost 한 row |
| A1 | active 0.1<E≤1eV |
| A2 | active 1<E≤3eV |
| A3 | active 3<E≤10eV |

Ghost는 미지의 E<0.1 연속 spectrum이 아니다. 이 분할은 birth-energy label 분할이며, 기존 네 observation-time bin과 다른 축이다. High-born cohort나 transport support를 추가하지 않는다. q=tA의 birth history와 saved RR response의 survivor history를 혼합하지 않는다.

질문은 하나의 double-ionization 사건에서 나온 전자가 서로 다른 birth-energy 집합에 속할 때, partition별 부모 이온 반환을 정확히 합성하는 방법과 marginal만으로 얻는 교차 중복량의 최대치다.

## 2. 유한 원자 사건 측도

Ω를 유한 electron-label 집합, U=∪A_i라 하자. S는 single-ionization 사건 측도, D는 Ω×Ω의 대칭 double-ionization 사건 측도다. D의 전체 질량은 double 사건 수 밀도이며

    μ = S + 2 π_1 D

가 inclusive electron marginal이다. Unordered pair record (x,y,w)는 사건 밀도 w를 뜻한다. x≠y이면 D(x,y)=D(y,x)=w/2, x=y이면 D(x,x)=w이다. 두 경우 모두 electron incidence는 두 leg를 센다. 이 1/2는 표현 convention이며 새로운 단면적 factor가 아니다.

임의의 A⊂U에서

    s_A=S(A), d_A=D(A×A), p_A=2D(A×A^c),
    N_A=μ(A)=s_A+p_A+2d_A,
    ν_A=s_A+p_A+d_A=N_A-d_A,
    δ_A=p_A+d_A.

ν_A는 A와 만나는 부모 사건 수, δ_A는 그중 double 사건 수다. Source-parent 종 increment는

    Δ_A n_HeI=-ν_A,  Δ_A n_HeII=s_A,  Δ_A n_HeIII=δ_A.

핵 수 합은 0이고 ionic charge 증가량은 N_A+p_A다. p_A의 partner를 thermal pool로 자동 배정하지 않는다. 실제 S,D 및 partner 분포는 입력되지 않았으므로 actual 값은 null이다.

## 3. 합집합 공식과 소유권

서로 겹치지 않는 A_i에서

    C_cross = 2 Σ_{i<j} D(A_i×A_j)

를 정의한다. 이는 두 서로 다른 partition을 지나는 double 사건의 밀도다. 한 double 사건의 leg는 두 개이므로 이 사건은 partition별 부모 반환에서 두 번, 합집합에서는 한 번 나타난다. Single 사건, within-partition double, U-밖 partner가 있는 사건은 한 번이다. 따라서

    ν_U = Σ_i ν_i − C_cross,
    δ_U = Σ_i δ_i − C_cross,
    S(U) = Σ_i S(A_i).

종 반환의 exact correction은

    Δ_U n_HeI   = Σ_i Δ_i n_HeI   + C_cross,
    Δ_U n_HeII  = Σ_i Δ_i n_HeII,
    Δ_U n_HeIII = Σ_i Δ_i n_HeIII − C_cross.          (1)

보정벡터는 (+C,0,−C)다. 핵 수와 baryon 수를 보존하고 ionic charge correction은 −2C다. Selected electron marginal과 selected kinetic energy는 이미 disjoint partition에서 additive하므로 correction이 0이다. Charge correction을 selected-electron ζ correction으로 오매핑하지 않는다.

PR111 언어로 d_int=ΣD(A_i×A_i), p_U=2D(U×U^c)라 하면

    d_U=d_int+C_cross,  Σ_i p_i=p_U+2C_cross.

이를 기존 affine 종식에 넣어도 (1)이 나온다. 따라서 C_cross와 전체 d_U는 다른 양이다.

명시적 같은 상태의 n_b가 있을 때만 native species로 옮긴다. 현재 단위의 조건부 H1/He4 inventory는 n_b=8750/47m^-3이므로

    δY=(C/n_b)(e_He4I−e_He4III).                     (2)

Species21의 He4 indices10,11,12는 직전 static native order를 유지한다. Recipient chemical convention B(HeI)=0, B(HeII)=I1*, B(HeIII)=I1*+I2*이면

    δB=−(I1*+I2*)C.                                (3)

현재 literal I1*=24.59eV, I2*=54.42eV는 recipient representation의 상수다. (3)은 중복 chemical storage 제거이며 실제 proton donor work 또는 heating이 아니다. Saved RR·cutoff·Coulomb·retained photon을 이 교정과 함께 반복 가산하지 않는다.

## 4. Sharp cross bound

n_i=μ(A_i), N=Σn_i, M=max n_i라 하자. 허용 family는 이 유한 원자 marginal을 보존하는 모든 nonnegative S와 symmetric D다. 추가 FDCS, angular, spin, projectile-energy joint constraint는 입력되지 않았다.

**정리.** 이 family에서

    0 ≤ C_cross ≤ C_max := min(N/2,N−M).            (4)

양 endpoint와 모든 중간값을 같은 atomwise marginal에서 달성할 수 있다. 이는 주어진 measure family의 sharpness이며 실제 산란 단면적의 physical sharpness나 source-error confidence bound가 아니다.

### 상한

모든 cross 사건에는 selected leg 두 개가 필요하므로 2C≤N이다. 최대 질량 partition A_m을 고르면 cross 사건의 최소 한 leg가 U\A_m에 있으므로 C≤N−M이다. Within-bin pairs와 outside partners는 사용 가능한 selected leg를 줄일 뿐 두 부등식을 무효화하지 않는다.

### 하한

S=μ, D=0인 all-single witness는 C=0을 달성한다. 또한 각 atom 내부에 weight μ_x/2인 double pair를 놓으면 같은 C=0이지만 d_U=N/2인 다른 witness가 된다. 이 예가 C와 d_U의 구별을 직접 보인다.

### 모든 경우를 처리하는 half-shift 구성

N>0에서 각 partition의 atom들을 연속 block으로 모아 길이 N의 원 [0,N)에 배치한다. 각 atom의 interval 길이는 그 atom의 marginal weight다. f:[0,N)→Ω를 이 finite atomic mass map이라 하면 f_#du=μ이다. T(u)=u+N/2 mod N을 쓰고

    D = (1/2)(f,f∘T)_#du,   S=0                     (5)

로 둔다. T는 measure-preserving involution이므로 D는 대칭이고 2π_1D=μ이다. 전체 double-event mass는 N/2다.

길이 n_i인 contiguous block과 half-turn shifted block의 겹침 길이는 max(0,2n_i−N)이다. 그러므로 within-partition event mass는 max(0,n_i−N/2)다. n_i>N/2인 partition은 최대 하나이므로

    d_within=max(0,M−N/2),
    C_cross=N/2−d_within=min(N/2,N−M).

이로써 balanced M≤N/2와 dominant M>N/2 모두 상한을 달성한다. Dominant case의 half-shift witness에는 within-bin double 사건이 포함될 수 있고 d_U=N/2다.

Unordered sparse 구현은 u∈[0,N/2)만 순회하여 f(u),f(u+N/2)를 한 event record로 저장한다. Original cumulative boundaries와 half-shifted boundaries가 바뀌는 지점에서만 record를 분할하므로 record 수는 O(K)다. 정렬을 사용하는 구현의 계산시간을 O(K)라고 별도로 단정하지 않는다.

Dominant case의 별도 star witness도 가능하다. R=N−M인 dominant submeasure ν를 고르고 remainder μ_r와 coupling하여

    D=(ν⊗μ_r+μ_r⊗ν)/(2R),  S=μ|A_m−ν

로 두면 C=R, d_U=R이다. R=0이면 all-single로 둔다. 이는 half-shift와 같은 Cmax를 달성하지만 전체 ion branch는 다를 수 있음을 보인다.

### 중간값과 퇴화 경계

최대 witness (S*,D*)와 all-single witness를 convex mixing하면

    D_α=αD*,   S_α=αS*+(1−α)μ,   0≤α≤1

이고 μ는 그대로, C=αCmax다. N=0이면 모든 질량과 C가0이다. Zero bins와 단일 positive bin에도 (4)가 성립한다. 경계 M=N/2는 두 경우가 정확히 일치한다.

## 5. 실제 source의 proper history 보존

Coefficient measure μ_A를 먼저 위 방법으로 분해하여 S_A,D_A를 만든다. 알려진 proper history에서 S_t=tS_A,D_t=tD_A로 두면 q=tA를 정확히 유지한다. a,b가 0≤a<b≤10^10인 경우

    F[a,b]=(b²−a²)/2=(b−a)(b+a)/2,
    μ_[a,b]=F[a,b]μ_A,
    Cmax[a,b]=F[a,b]min(A_N/2,A_N−max_i A_i).        (6)

양의 scaling과 구성이 교환되므로 동일 witness history가 네 prefix 및 네 disjoint birth-time intervals를 동시에 만족한다. Prefix 합산은 겹친 history를 반복 가산하므로 허용하지 않는다. 서로 겹치지 않는 birth-time windows는 additive하다. Saved response의 observation-time bins는 이전 cohort의 survivor/RR를 포함하므로 이 birth-time 분할로 대체하지 않는다.

## 6. 식–구현 계약

1. 실제 pinned NPZ를 읽어 저장 binary64 atom weights를 Fraction.from_float로 exact lift한다. Canonical total source를 model-identified H/He split으로 교체하지 않고 기존 residual admission을 별도로 재사용한다.
2. Three witnesses: all-single, same-atom double, half-shift. 각각 모든 atom marginal equality를 검사한다. Ghost label과 energy boundary를 한 번씩만 소유한다.
3. Event identity와 electron atom identity를 구별한다. 같은 event가 여러 partition claim에 존재할 때 identical content만 한 번 합친다.
4. 모든 selected incident partition이 그 event를 claim해야 한다. Union 및 partition의 electron/energy 합이 같아야 한다.
5. 실제 verified loader가 source NPZ와 atom-content identity를 결속한다. Algebraic fixtures는 별도 provenance로 표시한다. Source SHA 문자열만 맞고 coefficient가 다른 입력을 source-matched로 인정하지 않는다.
6. 이미 사용한 time window 또는 겹친 prefix는 재가산을 거절한다. 같은 proper history/frame/isotope/state/support를 요구한다.
7. 같은 상태 nb가 없으면 native species/per-baryon fields는 null이다. Density-level bookkeeping은 명시된 입력 범위에서만 계산한다.
8. 이 결과는 source ion union 또는 naive source sum에 가하는 correction 중 하나로 소비한다. 전체 기존 source return에 새 전체 source term을 다시 더하지 않는다. RR response는 기존8unique additive returns를 한 번만 포함한다.
9. Actual exclusive D, selected-outside partner state/energy/history/response, residual excitation, proton debit, coupled EOS/T와 full-source physical native25는 null로 유지한다. Retained photons는 별도 port이며 새 spectrum/history를 만들지 않는다.

## 7. 이전 독립 검토의 보존

리셋 전 /root/backup_survey_next가 실제 반환한 R6 판정은 PASS_DERIVED_SCOPED였다. 이는 현재 agent의 독립 검토로 세지 않는다. 그 실제 메시지에서 다음 finding이 나왔다.

| Finding | 구체적 관찰 | 필요한 교정 |
|---|---|---|
| F01 | event weight가 input atom marginal과 달라도 내부 event algebra만 통과 가능 | selected atom마다 exact marginal equality |
| F02 | cross event가 한 incident partition claim에만 있어도 ion identity 통과 가능 | incident claim completeness와 electron/energy additivity |
| F03 | source SHA 문자열만으로 arbitrary atom payload의 provenance를 보장 못함 | pinned loader + atom-content digest, fixtures 분리 |
| F04 | 일반 임의 measure-space로의 무조건 quantile-map 확대는 추가 가정 필요 | 이 정리를 실제 finite atomic source로 제한 |

F01/F02의 정적 교정은 당시 관측됐고 runtime 검사는 아직 수행되지 않았다. 현재 재구성 코드의 최종 수용은 root가 수행하는 실제 bounded execution과 해당 C9 검증으로 결속한다. Strong no-go 또는 절대 novelty를 주장하지 않는다.

## 8. 근거 상태

수학은 정의와 위 constructive proof로 derived이다. 새로운 산란 데이터나 실험 branch inference는 수행하지 않았다. 이 문서 자체는 numerical PASS, CAS PASS, publication ACK 또는 전체 workflow 완료를 뜻하지 않는다. 과학 의미와 예산·게시·복구 상태는 각각 실제 영수증을 따른다.

