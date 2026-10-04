# BASS-CR-CHAT-F04A-20261005: 제한된 BE root 인증과 thermal obstruction

## 판정

RESTRICTED_EXACT_REAL_BE_CERTIFICATES_PASS__THERMAL_OBSTRUCTION_PROVED.

CR_OFF_FASTEST를 유지하며, F03 source를 정확 실수 연산으로 해석한 3변수 backward-Euler 잔차와 해석 Jacobian을 유도했다. exact-rational interval contraction으로 고정 fixture-like 입력의 단일 dt와 ±1% dt 구간에서 상자 내 해 존재·유일성과 양의 thermal 상태를 인증했다. 이 결과는 canonical REI-F04의 actual joint-parent sparse nonlinear remainder certification 전체가 아니다. 원자 lane PARKED, 새 선행 gate 없음.

원 F03가 이미 photon/thermal 변수를 구조적으로 소거한다. 이번 기여를 기존 7D Newton solver의 새 3D 최적화라고 부르지 않는다. 기존 소거를 명시적 reduced residual/Jacobian과 별도 root/thermal 판정으로 만든 보조 연구다.

## 소스·동시 진행 수신

bass_cr 시작 HEAD=4a1db971e51bcd0fa00a6c526ed7de19b0821b12; 게시 직전 HEAD=9253ed4eef7582816bbfd0f21575d132b66cd819. 같은 research/r4q-gap-closure-20261001 branch에 새 문서만 추가한다.

rei_bianchi에서 aa3e98d7a4f90105c4ac9712ba71c955f9b53cea의 다음 원문을 읽었다. 세 blob은 c1d7f89c8abc90a6adf971390f2bce7ae7530a23 F03와 일치한다.

- rust/rei_microphysics/src/hhe_events.rs: 57a63eee1e9d8c4aa2b5ed663dbea15619359f71
- rust/rei_microphysics/src/microstep.rs: 3a78b40d1823a1e1c8541538bd94481b4cab0277
- rust/rei_microphysics/src/thermal.rs: d43a09450f2b2ed17f7032d4a3aecc3ff3f5d365

Static/proper HHe, 3group photons, 고정 합성 alpha/beta/sigma, Case-A energy escape scope다. Rust full bytes를 이번 ZIP에 넣거나 local byte round-trip 검증했다고 주장하지 않는다.

게시 준비 중 bass_cr의 새 commit9253ed4를 수신했다. research/fastest_track_20261004/flrw_source_regression/OWNER_PROBE_RETURN_KO.md 및 evidence/owner_probe/NATIVE_RESULT.json을 읽어, 정본 FLRW02 native probe의 build/run exit0와 CHECKS7, 세 source blob 일치를 확인했다. 두 문서 blob은 각각9aab3f95768f53457f959ee8a4fca172bfa6e958와1a20b7e60a244436c12062036d59f599052e3aff다. 반환 읽기·수신 ACK이며 native/archive 재실행·restore는 하지 않았다. 따라서 이전 probe의 native 실행 자체가 전무하다는 blocker는 더 이상 유지하지 않는다. 그 finite probe와 이번 exact-real certificate의 input/endpoint binding은 별개다.

receiver는3dceea736f9aaa363617a9a6a5bb2854d9ff9986까지 전진했다. aa3e98d7 이후 두 commit의 changed-path 목록과 docs/fastest_track_chat/REI-CHAT-FLRW02-20261005/publication/NEXT_HANDOFF_KO.md(blob b74d7cfc7651928271d2f86c56af014ef1f7561f)를 읽었다. FLRW reference module/example/tests/lib exports 및 별도 packet이 추가되었지만 위 세 F03 source path는 변하지 않았다. 새 handoff의84 tests 등은 보고로 수신하며 여기서 재검증하거나 합산하지 않았다. 새 모듈 전체 재감사 없음. REI-F04와 REI-CHAT-FLRW03은 owner의 별도 pending 작업으로 유지한다.

## 축약식과 인증

x=(xH,xHeII,xHeIII), d=(nH,nHe,nHe), l=(1-xH,1-xHeII-xHeIII,xHeII), ne=nH*xH+nHe*(xHeII+2*xHeIII), np=nH+nHe+ne, s_ag=c*sigma_ag.

    kappa_g(x)=sum_a d_a*l_a*s_ag
    N_g(x,h)=N_g0/(1+h*kappa_g(x))
    Gamma_a=sum_g s_ag*N_g
    j_a=l_a*(Gamma_a+ne*beta_a)-x_a*ne*alpha_a
    G_h(x)=x-x0-h*(j0,j1-j2,j2).

nH/nHe로 나누지 않으므로 한 species density가0인 per-capita 극한을 보존한다. Jacobian은 opacity와 ne feedback를 모두 미분한다. rate를 frozen으로 둔 iteration Jacobian이 아니다.

photo/collision/recombination event rates를 P_ag,C_a,R_a로 두면

    Hph=ev*sum(P_ag*(E_g-chi_a))
    Cion=ev*sum(C_a*chi_a)
    B=u0+h*(Hph-Cion)
    u=B/(1+h*sum(R_a)/np).

물리 분율 영역에서 분모>=1, np>0이므로 u>=0 iff B>=0; log-temperature adaptive 평가에는 B>0이 필요하다.

X=center+[-rho,rho]^3가 물리 simplex에 포함되고 H가 dt구간일 때, A=DG(center,mid(H))의 정확 역행렬을 잡는다. q>=sup||I-A*DG||inf, b>=sup||A*G(center)||inf를 유리수 구간으로 계산한다. q<1과 b+q*rho<=rho이면 모든 h∈H에 대해 X 내부 유일한 BE root가 존재하며 root-distance<=b/(1-q)다. 증명은 T=x-A*G의 contraction 및 X→X 포함으로 보고서에 직접 제시했다. 상자 밖 다른 root를 배제하는 전역 정리가 아니다.

## 실제 결과

공통 중심점 표시값=(0.010361381081316618,0.019041680970143936,0.0010000171246828974).

| 항목 | dt=1e8 s | dt∈[9.9e7,1.01e8] s |
|---|---:|---:|
| fraction cube radius | 1e-8 | 1e-5 |
| q 상계 표시값 | 1.304206429314642e-14 | 3.6569290452349e-6 |
| b 상계 표시값 | 2.8667507392340134e-19 | 3.6188980477631907e-6 |
| b+q*rho 표시값 | 2.868054945663328e-19 | 3.618934617053643e-6 |
| root-distance 상계 표시값 | 2.8667507392340505e-19 | 3.6189112818649696e-6 |
| B 하한 표시값 [erg cm^-3] | 2.2673539065737397e-16 | 2.267352201687199e-16 |
| root / thermal / positive-T | PASS / PASS / PASS | PASS / PASS / PASS |

모형 리터럴·초기 분율·광자는 binary64 값의 정확 유리수상이며, 초기 u0는 fixture 공식의 exact-real evaluation이다. native Rust가 연산 중 반올림한 초기 u의 bit identity는 검사하지 않았다. 따라서 native fixture의 bit-for-bit 인증이 아니다. 두 번째 인증도 dt만 interval-valued이고 physical coefficient uncertainty는 포함하지 않는다. NumPy3회 Newton은 중심점 제안용일 뿐이고, 모든 proof inequality는 Fraction/Interval로 정확 비교했다. 표의 소수는 display only; 정본 proof endpoint는 JSON의 분자·분모다.

## 정확 thermal 반례

normalized pure H에서 nH=1,nHe=0, alphaH=betaH=1, sigma=0, ev*chiH=1, xH0=1/2, N0=0,u0=0로 둔다. He계수0. 분율 RHS=x-2*x^2이며 BE의 유일한 물리 root는 x=1/2이다(다른 root=-1/(2h)). C=R=1/4,np=3/2이므로

    u(h)=(u0-h/4)/(1+h/6).

h=1에서 세 fraction residual이 정확0인데 u=-3/14<0이다. 연속 벡터장도 u=0에서 du/dt=-1/4로 물리영역 밖을 향한다. 따라서 frozen beta 모형의 모든 nonnegative 초기 상태가 물리 thermal 해를 갖는다고 증명할 수 없다. 이 equilibrium에서는 nonnegative thermal에 h<=4*u0, strict positive T에는 h<4*u0가 필요하다.

기존 endpoint_thermal은 이미 u<0을 HHE_THERMAL_DOMAIN으로 거절한다. 누락된 safeguard나 임의로 고칠 bug라고 부르지 않는다. 본 반례는 허용된 입력영역을 F04가 무조건 확대할 수 없다는 제한이다. u clipping/계수교체/합성모형 소급 수정 없음.

## 검증 범위

새 focused tests27 PASS, 별도 두 root certificate PASS, exact counterexample PASS, Python syntax PASS. 처음6 tests는 두 batch의 assertion RED→GREEN을 기록했고 나머지21은 tests-after다. 9 Jacobian components의 SymPy 미분 대조, 직접 사건 기반 BE·에너지 항등식, interval/guard/zero-species/thermal 분리 검사를 포함한다. 독립 human/agent review나 proof-assistant verification은 없다.

이번 채팅의 native runs0, old suite replays0, atomic integrations0, cosmological histories0. 수신한 외부 native probe는 별도이고 그 존재를 인정한다. 이번 exact-real certificate가 native float execution·continuous ODE error·uniform full-half acceptance·actual joint-parent 전체 box를 인증한 것은 아니다.

G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO. 기존 S-only 두 window bounds5.599633283869504e-17 및7.49726779045559e-17 ta^-1을 상속한다. CR-F0=WAIT_FOR_ACTUAL_CR_OFF_DISPATCH_BINDING. source/loader/callback관측=null, CR_OFF_ACCEPTANCE.json 미생성. 정밀원자/CR-on/full-K/R4AQ/318patch/소비된 승인 재사용 없음.

## 정본 패키지와 실제 이중백업

- 파일: BASS_CR_CHAT_F04A_20261005_v1.zip
- bytes:125346
- SHA256:3dad0c3e0ef3b147c0550aa419f5ec287bf1ccafe1acbd48b4ff1c06033e2cc3
- ZIP33 members /32 payload SHA +CRC local검증
- Drive id:1q6qOyGp4vLXBKGVkSAwAdrssTNbU-D7E; parent:1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ; success ACK 및 metadata size125346/name/parent 확인
- Dropbox id:id:BSpOijBcT10AAAAAADyNag; completed, size125346
- Dropbox path:/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04A_20261005_v1.zip
- Dropbox modified_time:2026-10-04T15:36:31Z

같은 local archive를 두 provider에 create-only로 저장했다. R1 UPLOAD_VERIFIED(id/name/size/parent 또는 path). Remote checksum은 도구 응답에 노출되지 않았고 full restore 및 독립 remote byte-hash 검증은 하지 않았다. UPLOAD_VERIFIED!=RESTORE_VERIFIED.

코드·시험·전체 보고서·정확 결과·logs의 정본은 이 immutable ZIP이다. Git의 이 문서는 요약/동기화다. ZIP 안에는 자신의 미래 업로드 성공을 미리 주장하지 않고 외부 delivery receipt를 보도록 표시했다. 과학 검증과 저장 검증을 구분한다.

## 다음 보조 노드

BASS-CR-CHAT-F04B_RESIDUAL_SENSITIVITY_AND_SELECTED_BOX_EXTENSION.

실제 native old.u/endpoint coordinates/dt/model identity가 기존 결과에 있는지 먼저 확인한다. 부족한 bits만 owner의 제한적 exporter로 확보하고 exact-real residual/root-distance에 연결한다. 원 joint-parent box는 owner가 지정한 범위만 확장하며 simplex, denominators, thermal B를 명시한다. 새 source/목적 없이 같은27 tests·동일 상자·old suite·ZIP을 반복하지 않는다. 실제 off-hook이 생기면 해당 entrypoint의 source/loader/callback만 focused 검증한다. Canonical REI-F04와 FLRW03 진행을 대체하거나 중단하지 않는다.

방법론 참고: S. M. Rump, Acta Numerica19(2010)287–449, DOI10.1017/S096249291000005X. 출판사 abstract/metadata만 확인했으며 특정 본문 theorem을 읽었다고 주장하지 않는다. 적용 충분조건과 contraction 증명은 정본 REPORT_KO.md에 직접 적었다.
