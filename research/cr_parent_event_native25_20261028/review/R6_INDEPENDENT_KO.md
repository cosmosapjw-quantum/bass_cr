# R6 독립 이론 심사 — 부모 사건과 조건부 native25

## 판정과 범위

**PASS_SCOPED_THEORY. 열린 blocking finding은 0이다.** 고정된 PHYS02 세 기저 모형의 표적 귀속, He의 필요한 사건 제약, 저장된 RR 응답과의 합성, 별도 에너지 장부 및 명시적인 caloric fixture에 대한 수동 유도가 일관된다. 이 판정은 실제 계수 복원·conditioning 값이나 구현의 수치 통과를 선언하지 않는다. 실제 He 분기, partner 이력·에너지·응답, proton debit 및 full physical native25는 계속 null이다.

심사자는 `/root/source_qualification`이다. 현재 주 이론·production code·독립 수치 reference를 작성하지 않았다. 선행 역할은 source/provider 근거 및 metadata 정리였다. 아래 세 문서 교정을 요청했으며, 본문 수정은 root가 수행했다. 주 유도를 자기 심사한 결과가 아니다.

실제 R5 게시 commit은 `8ac0a56475e06c02e3e3e3a11417ef893fdcb4ce`이고 Dropbox/Drive R2 receipt를 읽었다. R06 fresh preflight의 local/remote HEAD 일치, 17개 source pin 및 이전 backup receipt 확인을 재사용한다. R5 본문 SHA256 `2b74ce08e992961e64306bdb7157f788e94ac838742480acdafc5ddd72ebf591`는 그 게시와 backup에 보존되어 있다. 이번 심사의 최종 본문은 그 문서에 세 교정을 적용한 SHA256 **`1a35e091aed4e2db58f4db1d355cf88ccb79a9041a57330a76bf5ff2a5857652`**다. 교정된 본문의 R6 게시 자체는 심사 시점에 아직 pending이다.

고정 CONTRACT SHA256 `01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162` 및 CONDITIONING_DEFINITION SHA256 `90f0b4e049ab289fbf0a7dd205f4dbc720dbf32547f99f3444a3d3a83b4059bc`는 바뀌지 않았다. 실제 읽은 파일의 bytes·SHA256·읽기 범위는 [R6_INDEPENDENT.json](R6_INDEPENDENT.json)에 기록한다.

## 직접 확인한 연결

| 항목 | 독립 판단과 남은 한계 |
|---|---|
| 세 기저의 독립성, Eq1–2 | H의 pole은 He의 pole과 다르고 그 분자가 소거되지 않는다. 남은 He 분자는 W의 일차식이므로 두 계수도 0이어야 한다. 실제 `rudd_factors`의 H 비율도 맞다. 별도 binary64 dot product의 차이는 실제 저장 데이터 검사 대상이며, 함수 독립성만으로 finite moment matrix가 잘 조건화됐다고 주장하지 않는다. |
| finite-M conditioning, Eq9–12 | nominal R·c·M을 고정하면 `B δz = R δb`에서 componentwise 상계가 따른다. 양의 열 scaling은 상대 sensitivity를 보존한다. 실제 rcond·positive envelope·미사용 moments 검사는 이후 새 계산에서 동결된 허용치로 수행해야 한다. |
| positive primitives, Eq3–8 | `W=a+(I+a)u`, `v=u/(1+u)` 치환으로 양의 moment 식과 F2의 양의 급수를 얻는다. 기하급수의 잔여 상계 및 `E0=I*N1`도 맞다. `a=b`의 정확한 0 처리를 포함한다. ordinary high precision을 outward arithmetic 인증으로 승격하지 않는다. |
| 원 Q8 및 ghost, Eq13–16 | 실제 `source_vectors`는 cell별 Gauss8, `selected_A_energy` 정규화, number-linear `project` 순서다. 첫 cell의 아래쪽 가중치는 0.1 eV cutoff ghost에 들어간다. Eq16은 원 normalization을 실수식에서 소거하며, canonical byte를 고치는 식이 아니다. pointwise H/total 비율이나 사후 renormalization을 허용하지 않는다. |
| finite history, Eq17–20 | `q=tA`의 적분은 `(b-a)(b+a)A/2`이고 proper clock은 한 번만 적용한다. source birth interval과 saved response observation bin을 구분한다. 앞 bin 출생자의 뒤 bin RR를 유지하며, 각 bin을 빈 초기상태로 재시작하지 않는다. |
| He의 s,p,d family, Eq21–22 | single·mixed-double·double-selected의 선택 전자 수에서 `s+p+2d=N_He` 및 표기된 charge inventory가 나온다. 이 domain은 필요한 affine 제약이다. 전체 joint kernel의 충분조건이나 실제 분기점으로 선언하지 않는다. |
| parent와 RR target, Eq23–27 | H/He 핵 수·nb 보존과 charge 식이 일치한다. 전자의 출생 표적과 capture 표적을 동일시하지 않는다. 선택 fast subset의 ζ만으로 partner p를 열전자에 채우지 않으며, same-state nb를 한 번만 나눈다. |
| energy sidecars, Eq28–35 | Eq23의 chemical inventory를 전개하면 Eq30이다. saved kinetic identity와 RR photon binding을 대입하면 Eq33의 `Rconst-Bbranch`가 나온다. mixed double에는 추가 I2_src, double-selected에는 추가 `I2_src-I1_src`가 필요하므로 Eq34–35도 맞다. 실제 I2_src·partner·excitation·donor history는 제공되지 않았으며 recipient 상수로 대신 만들지 않는다. |
| caloric prefix/bin, Eq36–37 | 명시적 ideal-gas EOS에서 유한 energy/count 변화의 식이 나온다. bin은 앞 endpoint의 Ua·Da를 쓰므로 누적 prefix와 합성 기준이 맞다. positivity와 partner/cutoff/EOS closure가 필요하며, frozen100K 결과의 postprocessing이다. 새로운 coupled thermal history가 아니다. |
| tiny increment와 RR 항 | baseline+delta가 endpoint 반올림 소실을 피하고, 별도 event-term ledger가 작은 RR 항을 보존한다. 큰 source-minus-delta로 작은 RR를 역추출하지 않는다는 요구가 타당하다. 실제 코드와 독립 출력 검사가 이 보존을 확인해야 한다. |
| once-only 및 null gate | 원 source의 proper729·neutral target·projectile speed·angle integration, 새 유한 시간 적분, eV→J, 1/nb의 소유자가 구분되어 있다. 절대 volume, 외부 T/nb, 다른 isotope/state/frame 또는 support 확대를 묵시적으로 가져오지 않는다. |

표의 항목은 수동 검토 주제이며 새로운 numerical PASS 수가 아니다. source 전체를 재계산하거나 저장 NPZ를 적분·재합산하지 않았다.

## 발견과 교정 확인

1. **He 계수 이름의 충돌.** 기존 theory의 `theta_He0/theta_He1`과 CONTRACT/R4의 `theta_He1/theta_He2`는 공통 접미사가 서로 다른 기저를 뜻했다. root가 Eq2 뒤에 `theta_He0_theory = theta_He1_contract`, `theta_He1_theory = theta_He2_contract`와 고정 열 순서를 명시했다. 이 대응으로 결속하고 이름만으로 열을 정렬하지 않아야 한다. **해결 확인.**
2. **입력 경로.** section0의 잘못된 단위 내 파일명을 실제 `inputs/SOURCE_LINEAGE_MANIFEST.json`, `inputs/INPUT_MANIFEST.json`, `literature/LITERATURE_MAP_KO.md`로 교정했다. **해결 확인.**
3. **Eq7의 닫힌 끝점.** `z=0`이면 remainder는 0이므로 strict positive 하한을 nonnegative 하한으로 바꿨다. 기존 `a=b` 분기와 맞으며, 허용치·알고리즘·물리 범위는 변하지 않았다. **해결 확인.**

R5에 대한 read-only Git diff는 local promisor blob을 가져오려다가 proxy 연결 실패로 끝났다. 이 읽기 실패를 지우지 않는다. 대신 이미 보존된 원 draft의 SHA가 R5 본문 SHA와 같음을 확인하고, 그 로컬 원문과 최종 본문을 직접 비교했다. 차이는 위 세 가지뿐이다. 추가 remote fetch, 과학 실행 또는 기존 원문 변경은 하지 않았다. root의 [R6_CORRECTION_LOG.json](R6_CORRECTION_LOG.json)도 함께 결속한다.

## 채택 경계와 다음 검증

R7의 한정 symbolic check, 실제 3×3 recovery와 canonical projection 검사, 구현 controls, 별도 저자의 reference 및 최종 C9가 남는다. 기존 517/112/46 검사는 immutable RR 응답을 재사용하는 범위만 지지하며 이번 source-parent/consumer의 새 검사 수에 더하지 않는다. 실제 fit 실패는 `MODEL_IDENTIFICATION_UNRESOLVED`로 처리해야 하고, 4계수 확대·원 source 재실행·허용치 확대를 자동 복구로 삼지 않는다.

현재 중앙 근거는 `7de02b3e05705ead4eeb313c8487a21d4e6876a6`의 **28/88**, 88 nodes/17 edges이며 이번 CR 단위의 집계 효과는 **0**이다. N4/N5는 PARTIAL_OPEN, N6/N7은 PREDECESSOR_GATED, L4는 false다. 실제 full physical native25, physical heating 완료 및 전역 completion/error/budget remaining/currency는 승격하지 않는다. PR236의 32/88 또는 별도 working count를 합산하지 않는다.

새 40 CPU-s 단위는 이전 잔여를 이월하지 않으며 실제 C4 admission과 모든 preparation·worker·coordinator·실패·tail 비용의 기록을 요구한다. 이 수동 심사는 새 과학 실행·scientific import·CAS·source/proton quadrature/G/RR/G9600 replay 모두 **0**이다. metadata 읽기·작성의 CPU를 임의로 0 또는 측정값으로 만들지 않았다. 기존 실패, UNKNOWN_NO_ACK, 개인 대화 전수 검색 unavailable 및 Drive partial inventory 한계를 바꾸지 않는다.

이번 심사는 **현재 CR_PHYS02_PARENT_EVENT_NATIVE25_V1 한 단위**만 지지한다. 후속 과학 단위를 자동으로 시작하지 않으며 `AUTO_NEXT_NODE=false`를 유지한다.
