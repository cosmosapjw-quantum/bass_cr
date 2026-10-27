# C09 독립 통합 심사 — PHYS02 부모 사건과 조건부 native25

## 판정과 독립성

**판정: `PASS_SCOPED_PARTIAL_RETURN`. 열린 차단 사항은 0개다.** 이 판정은 고정된 `CR_PHYS02_PARENT_EVENT_NATIVE25_V1`의 모델 귀속, 유한 proper-time 부모 사건 장부, 명시적 동일상태 native affine 반환 및 조건부 EOS 표현에 적용한다. 실제 full physical native25, exclusive He 사건 측정, 미지 partner 응답, 실제 proton debit 또는 physical heating 완료를 뜻하지 않는다.

심사자는 `/root/source_qualification`이며 production, 원 독립 numerical reference, 네 검사 recovery의 작성자가 아니다. 원 이론 작성자도 아니다. 이 심사자는 source/provider qualification, R6 독립 이론 심사, C07/C08 한정 수리의 독립 정적 검토를 수행했다. 별도로 root가 승인한 C4 admission 및 release metadata helper의 좁은 수리를 작성했으므로 그 metadata 코드를 스스로 독립 승인했다고 주장하지 않는다. 해당 source는 root의 별도 실제 acceptance에 결속되며, 실제 중앙 후보 심사는 후속 별도 작업이다.

검토 방법은 과학 코드의 정적 읽기, 실제 저장 JSON·실행 source snapshot·영수증·해시 대조와 실제 PNG 육안 검사다. 이번 심사에서 science worker, scientific import/compile, CAS, source quadrature, fit/projection, RR 전파 또는 그림 재생성을 수행하지 않았다. 저장된 검사 Boolean의 집계와 기록된 CPU counter 합산은 metadata inspection이며 새로운 과학 검사 수에 넣지 않는다. 정밀한 파일 pins와 최종 판정은 `C09_INDEPENDENT.json`, 저장 증거의 대조 결과는 `C09_SAVED_EVIDENCE_CHECKS.json`에 둔다.

## 1. 입력과 고정 범위

현재 source record의 SHA는 `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`, 17-file manifest의 SHA는 `2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3`다. C09 실제 preflight가 17개 source pins와 직전 backup receipt를 확인했고 원 source는 그대로다. `4ca5a90…`는 보존 snapshot이지 첫 실행 commit이라는 주장이 아니다.

새 모형의 계수 식별에는 고정된 세 moment bands를 사용한다. 넓은 식별 bands가 실제 transport support를 넓히지는 않는다. 반환의 birth tag는 `direct_0p1_10`, native birth support는 0.1–10 eV이고, 3200 active atoms와 별도 cutoff ghost를 유지한다. 고에너지에서 태어나 나중에 내려온 전자를 현재 에너지 기준으로 섞지 않는다.

알려진 source law는 proper clock의 `q_j(t)=t A_j`, 구간은 [0,10¹⁰] s다. 마지막 endpoint rate는 알려진 이력의 left limit이며 그 이후 continuation/shutoff를 추정하지 않는다. fixed proper-volume density를 사용하고 절대 volume이 없으므로 worldtube 총 N/E는 null이다. 원 source의 neutral-target factor, proper729 및 angle/speed 적분을 다시 적용하지 않는다. source 적분의 시간 인자, 같은 상태의 nb 나눗셈, eV→J 변환은 각 출력에 한 번만 적용한다.

새 조건부 H1/He4-only inventory는 T=100 K, total-nuclei nH=140 m⁻³, nHe=1085/94 m⁻³, nb=8750/47 m⁻³다. 동위원소 매핑은 명시적 조건이다. PR107/108의 10000 K 또는 PR236/PW19의 상태·nb를 이식하지 않았고, PR109의 기존 nb/native25 null을 소급 변경하지 않는다. 누락 history·nb·동일 recipient 상태를 null로 유지하는 실제 controls와, 혼합 상태·frame·clock·중복 인자·확장 support를 거절하는 controls가 저장 결과에 존재한다.

## 2. 모형 식별과 원 projection

`positive_moments`, 고정 3×3 scaled solve와 `recovery_metrics`를 원 R6 유도 및 고정 conditioning 정의에 대조했다. 작은 band에는 양의 series를 사용하며, 중간 반올림을 outward interval certificate라고 주장하지 않는다. holdout bands는 fit에 쓰이지 않는다. 원 Q8 cell rule과 number-linear projector를 각 basis에 적용하며, 이미 투영된 atom에 점별 H/He 비율을 곱하는 shortcut을 사용하지 않는다.

실제 preparation은 15/15다. 저장된 rcond∞는 약 0.05765736, 최대 componentwise sensitivity는 약 1.5684×10⁻¹⁰이고 선언 envelope의 양수 하한을 유지한다. 최대 holdout 상대오차는 약 5.1287×10⁻¹⁴, 3201 canonical atom의 최대 상대오차는 5.3532333465297213×10⁻¹⁴로 고정 기준 안에 있다. 이 값은 저장 산출물의 관측값이며 이번 심사가 다시 계산한 값이 아니다.

계수는 고정 모형에서 저장 moments로 식별한 결과다. 원 coefficient bytes를 복원했다거나 물리적 uncertainty를 닫았다는 뜻이 아니다. 원 canonical A를 교체·재정규화하거나 재구성 잔차를 다른 표적·heat·thermal count에 넣지 않는다. `prepare_v1/ATTRIBUTION_ARRAYS.npz`와 최종 primary의 동명 파일은 233,050 bytes 및 SHA `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`로 같다. preparation은 실제 root-pinned reuse admission을 통해 재사용됐으며 fit/projection 재실행은 0이다.

## 3. 부모 사건, 작은 RR 항과 에너지 장부

H-parent source extent와 He electron marginal을 구분했다. He는 `s+p+2d=N_eHe`, `p>=0`, `d>=0`, `p+2d<=N_eHe`라는 필요한 affine 영역을 제공한다. 이 영역은 exclusive energy/time joint distribution의 충분조건이나 실제 분기 측정이 아니다. 실제 s/p/d와 밖의 partner state·energy·history·pool·response는 null이다.

native species의 H1I/II 및 He4I/II/III 증분은 parent event와 저장된 RR capture 항을 합성한다. source parent target을 RR capture target과 동일시하지 않는다. 선택된 direct collision 장부에서 Δnb=0을 쓰는 것은 전체 외부 proton injection의 baryon history를 닫는 주장이 아니다. p의 추가 partner charge와 d의 exact stoichiometric 계수는 별도로 유지한다. 큰 baseline+작은 증분의 두 부분 표현과 개별 RR capture·binding·photon scalar 및 원 binary64 hex를 보존하여 작은 RR를 큰 source 차감으로 역산하지 않는다.

`energy_sidecars`는 source H threshold 13.605693122994 eV와 native/RR 13.60 eV의 차이, native branch lift 및 저장 numerical residual을 서로 다른 필드에 둔다. `L0`는 selected kinetic-plus-binding functional이며 실제 proton debit가 아니다. 미제공 I₂src를 native 54.42 eV로 자동 대체하지 않는다. actual donor work와 external work는 null이다. retained-photon 기여를 w_ext/heating으로 옮기지 않으며, 이 기여가 0이라는 것은 actual 전체 w_ext가 0이라는 뜻이 아니다.

retained-photon port는 이전 유한 RR 산출물의 실제 discrete capture atoms·energy members와 그 hashes를 참조한다. photon moments를 역변환해 spectrum이나 continuous time history를 만들지 않는다. transport/absorption/deposition과 absolute worldtube count는 계속 미결이다.

## 4. 유한 bin과 조건부 caloric 표현

네 cumulative prefix는 비가산 진단이며 네 disjoint observation bin이 부분 장부의 가산 단위다. bin에는 앞 시점에 태어난 생존 cohort가 포함된다. source birth interval과 response observation interval을 구별하고, 다음 bin을 빈 초기상태로 다시 시작하지 않는다. 16개 component claims와 기존 RR 채택의 중복 거절 규칙은 source alias나 누적 prefix를 별도의 새 사건으로 세지 않는다.

caloric 결과는 명시적 p=d=0, partner closure 및 monatomic ideal-gas EOS fixture다. retention과 instantaneous cutoff assimilation을 구분한다. bin의 energy/count baseline은 해당 이전 prefix의 조건부 endpoint이며, 구현은 Ua·Da를 사용한 안정적인 증분식과 log1p를 적용한다. independent reference는 별도의 EOS ratio를 대조했고 작은 증분은 자기 scale에서 검사됐다. 양의 Q만으로 heating을 단정하지 않는다. frozen100K response에 대한 postprocessing이며 coupled thermal history, rate feedback 또는 실제 온도 점이 아니다.

## 5. 실제 검사 수와 두 실패의 처리

| 증거 | 현재 수용된 범위 | 원 이력 보존 |
|---|---:|---|
| Preparation | 15/15 flags | 원 producer69e706… 및 실제 preparation 그대로 |
| Primary v2 | 58/58 flags | primary_v1의 domain exception과 charge0.347925 보존 |
| Controls | 51 unique / 52 evaluations | 원50개 중 변경 없는49개 재사용, affected control1개와 새 경계 control1개를 v2에서 검사 |
| Independent reference | 3450 unique accepted / 3454 actual evaluations | 원3446 PASS+4 FAIL, 새4 PASS; 원 FAILED result·source·cost 보존 |

C07 failure는 실제 `HE_SELECTED_MARGINAL_DOMAIN_REFUSED`다. 원 실패 operand/정확한 prefix가 기록되지 않아 그 값을 사후 실측 사실로 보충하지 않는다. 최소 수리는 finite Decimal의 exact dyadic d/prior_d/s 구성과 Fraction domain 비교였다. 전역 precision·tolerance·threshold·모형·원 projection은 바꾸지 않았으며, 실제 독립 review와 root admission 뒤 unique controls_v2/primary_v2가 수행됐다.

C08의 원 reference는 실제로 FAILED였고 네 실패는 half fixture의 s_m3 oracle에 한정됐다. 원 90자리 `d=N/2; s=N-2d`의 중간 반올림 잔차를 expected로 삼은 것이 원인이다. 새 script는 자체 원 reference의 저장 N과 명시적 p=0,f=1/2에서 `s=N*(1-2f)-p=0`을 exact Fraction으로 네 번만 평가한다. 비영 관측값을 작은 floor로 허용하는 경로는 없다. 실제 targeted4/4 뒤 composite가 생겼고, 원3446 PASS rows와 새4 replacements의 전체 JSON 값·순서가 정확히 일치함을 확인했다. 원 네 실패 행과 charge0.548229는 그대로 남았다.

선행 PR110의46/112/517이나 다른 단위의 검사를 이번 수에 더하지 않는다. 이번 numerical acceptance도 physical error certificate, 실제 He branch 또는 full consumer activation으로 승격하지 않는다.

## 6. 실제 그림과 보고서

`PARENT_EVENT_DIAGNOSTICS.png`를 실제로 열어 세 panel을 확인했다. H/He model attribution과 별도 cutoff ghost가 분명하고, stored residual panel은 symlog로 literal zero를 보존하며 epsilon/floor를 데이터에 더하지 않는다. 고정2×10⁻¹¹ 기준이 표시돼 있다. 마지막 panel은 네 proper endpoints에서 저장된 ΔlogT를 보여 주고 p=d=0·EOS의 조건부 결과임을 명시한다. 전체 제목도 실제 full state가 미결임을 표시한다. label clipping이나 의미를 바꾸는 축 표기는 발견하지 않았다. 그림은 재생성하지 않았다.

`C09_SCIENCE_REPORT_KO.md` SHA `5f814a5e4c3329b24b8c972939518672569824190e766ce475834af420a8f5dd`를 실제 산출물과 대조했다. preparation·primary·controls·reference·실패·비용·scope가 일치한다. 이 source 보고서는 C08 실제18/20 시점의 기록이어서 C9와 미래 S/D/M/R3를 PENDING/null로 남긴다. 본 독립 판정은 후속 파일이며 그 역사적 문구를 덮어쓰지 않는다. 최종 D 보고서의 실제 게시 필드는 root가 별도 admission으로 결속한다.

## 7. 예산·실패·runtime 한계

실제 최종 ledger와 `BUDGET_CLOSEOUT.json`의 24개 pins, 8개 immutable debit/receipt byte 동일성, 5개 preparation receipt를 대조했다. 현재8개 bounded attempts 모두 terminal accounting ACK가 있으며, 41개 실행 source snapshot도 각 manifest의 byte/SHA와 일치한다. 같은 attempt의 receipt 사본을 비용으로 두 번 더하지 않는다.

**charge10.45384/40 CPU-s = pure measured9.80384 + conservative tails0.65**다. preparation 실패3건과 worker 실패2건을 포함한다. 기록된 decimal counter의 독립 metadata 합계와 표시 총계 차이는1e-12 CPU-s 이내이며 과학 허용치와 무관하다. `all_runtime_attempts_pass=false`, remaining29.54616은 NONTRANSFERABLE이다. publication/metadata CPU는 미측정 null이고 0으로 바꾸지 않는다. 과거·병렬 unit 예산과 UNKNOWN_NO_ACK도 합치거나 지우지 않는다.

현재8개 worker receipt는 실제 known-owned PID를 관측했고 각 worker/coordinator reservation 초과를 기록하지 않았다. 이것이 예방적 aggregate kernel hard-cap 증명을 만들지는 않는다. 해당 proof flag는 false다. 검토된 admission·namespace 수리와 직접 worker limits는 그 고유한 범위에서만 재사용한다. 외부 science 또는 후속 node를 실행할 허용량으로 남은 예산을 넘기지 않는다.

## 8. 실제 게시 상태와 남은 delivery gate

C09 preflight 관측은 2026-10-27T17:33:52.588995Z다. own HEAD는 실제 C08 `d84de9418a135b093a589af8dfc35d8d40c0d821`, 중앙은 qualified `b99a9468abd53de77ddae36d93180e60072885bc`다. source/직전 backup 검사는 PASS이며 root의 owner 변경 점검과 일치한다. C08의 실제 dual R2까지18/20이다. 이를 canonical SOURCE의 full-GET R3나 미래20/20으로 쓰지 않는다.

중앙 **28/88**, 88 nodes/17 edges, 이번 CR 집계 효과0을 유지한다. 역사적27→28은 외부 B3h 기여이고 PR236의32/88·REI working33을 더하지 않는다. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4false를 유지한다. global physical completion/error/budget remaining/currency는 null이다. 개인 전체 대화 검색 unavailable 및 Drive partial inventory 한계도 유지한다.

본 과학 판정 후 실제 C09 S 게시, canonical SOURCE 봉인·이중 full-GET R3, C10 D 게시, 최신 중앙 부모에 대한 실제 두 파일 후보 심사·expected-SHA non-force M 게시, CLOSEOUT·다음 복사용 handoff가 별도 delivery gate로 남는다. 이 gate를 미래 성공으로 적지 않는다. 현재 단위의 그 마무리만 수행하며 **automatic_next_node=false**다.
