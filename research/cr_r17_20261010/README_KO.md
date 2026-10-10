# BASS_CR R17A: causal CDF source-goal bound

2026-10-10 KST. Base R16B 997281e566a60c71554192a6d653aa82c29cd2f7. Status CONDITIONAL_SOURCE_GOAL_BOUND_SHARPENED, not a physical admission.

## 실제 새 결과

같은 FT03 첫 macro [0,1.25e9] proper seconds에서 기존 여섯 positive Gauss birth boxes와 연속 constant S=f64(5e-15) photons/H/s를 비교했다. 원 initial gas/photon .05/H, 원 energy/atomic family, prescribed H=f64(1e-14)/s,nH0=f64(1e-4)cm^-3,fHe=f64(.083), HH/RCT/CR OFF를 유지한다. 모든 soft photons가 HI cutoff 위, HeI cutoff 아래에 남는 donor 범위다. Grackle/R13와 섞지 않는다.

기존 source-only tau radius1.021773e-17을 2.125533135951863662132892058883214693751…e-18로 제한했다. 79.1975993% 감소다. 실제 source차의 부호는 여전히 미확정이므로 ±radius를 사용한다.

R16B time interval과 새 source radius를 한 번만 결합한 constant-S continuum minus native-defined tau:

    [1.726968178866034690190055439800249300664…e-17,
     2.219287238809879417339730677747077477803…e-17].

전체 구간의 폭은 기존 R16B+source보다 76.6757270% 좁고 하한은 양수다. 시간오차 자체는 변경하지 않았다. 새 source radius는 전체 폭의 약86.3478%를 차지한다.

## 유도

원 weight-box prefix 합 L(b),U(b)에 대해 D*(b)=max(Sb−L(b),U(b)−Sb)를 사용한다. 실제 six births와 각 midpoint-CDF crossing에서 나누면13개의 affine pieces다. 최대CDF값과 mass defect는 원 donor의 exact Fraction과 일치하고 재정규화하지 않는다.

Frozen gas path survival Rg(t,b)=exp(−∫b^t κg), A=1−Rg이면 |∂bA|≤k+(t−b)kb다. A(t,t)=0이라 Stieltjes 끝점 항이 사라진다. 이것은 mass mismatch가0이라는 가정이 아니다.

    B(t)=∫0^t D*(b)[k+(t−b)kb]db.

Primary heat derivative의 상계 [qmax*k+v(qb*k+qmax*kb+qmax*k²)+(v²/2)qmax*k*kb]/W0는 모든0≤v≤T에서 k의0.007489061368…배 이하다. 따라서 normalized gas source vector 전체도 B(t)로 감싼다.

부모의 nonphoto L*t/T 및 photon gains Ptot*a*t, Ptot*qmax*a*t(1+k*t/2)/W0에서 prefix gain≤γ*t/T를 얻는다. γ≈.001337965988060131<1, E∞≤B(T)/(1−γ)와 E(t)≤B(t)+γ*(t/T)*E∞다. 원 common positive gas tube와 원 interval-kernel 상계에 조건부다.

    U17=CT*nH0*(1+3fHe)∫0^T exp(−3Ht)[B(t)+γ*(t/T)*B(T)/(1−γ)]dt.

밀도를 잠시 constant upper로 두면 ∫B(t)dt=∫D*(b)[k(T−b)+(kb/2)(T−b)²]db다. 각 birth 뒤 남은 관측시간을 보존하는 것이 이번 개선의 핵심이다. 최종값은 actual analytic density에 대해 exact degree5/6 exponential brackets로 계산했다. 그 양의 예산 적분 bracket폭은1.87491e-48이며 실제 source차의 하한은 아니다. 직접 optical upper2.1231712854543173e-18, feedback upper2.3618504975463998e-21이다.

원 positive Decimal-upper를 float로 내보낸 scalar는 그 다음 큰 binary64를 exact Fraction으로 읽어 보수적으로 올렸다. atomic/AD 함수를 재평가하지 않는다.

## 실행과 재현

새23고유시험 PASS(1assertion RED→GREEN/22tests-after), actual64weight corners의192exact Simpson moments, 독립mpmath100 raw moments9와 optical budget1, synthetic nonzero-hazard/Stieltjes2검사 PASS. 새6Python files syntax PASS. Fresh create-only full package reproduction23tests+exactresult byte match+independent scalar check가 exit0이다. Native/physicalIVP/root/atomicprovider/parent-suite 실행0이다. Independent human/agent reviewer, proof assistant 또는 independent interval-RHS proof는 미실행이다.

Git-only 계산에는 외부 ZIP이 필요 없다:

    python -B research/cr_r17_20261010/portable.py --output NEW_RESULT.json

실제 generic core와 모든 exact scalar/birth/time 입력을 Git에 게시했다. compact input은 전체 선택 원문에서 추출한 유리수 값이며 payload들의 exact 결과4개가 full-source 경로와 일치한다. Original selected donor text/provenance, full23tests, exact long JSON, independent checker, logs와 전체 보고서는 불변 ZIP에 있다. 이 repo path의 portable.py에 cloud credential이나 미게시 local path가 필요하지 않다.

전체 archive와 provider receipt는 DELIVERY_RECEIPT.json을 따른다. R17A 완료/ R17B heavy source-kernel 계산은 미실행이며 NCP_HANDOFF_PROMPT_KO.md로 인계한다. CR_OFF_FASTEST,precisionatomicPARKED,HH ACTIVE,G02 UNRESOLVED,all_bound OPEN,b_grid NO_GO,physical/productionHOLD,ownerACK/globalCRcounter/observer_tail null 유지.
