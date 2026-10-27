# 다음 CR 단위용 공급자 조사

관찰 기준은 **2026-10-27 12:20:04 UTC**의 root ref 조사이며, 각 원문을 읽은 시각·URL·Git blob·SHA256은 `EVIDENCE_MANIFEST.json`에 보존했다. WU는 실제 연구가 진행 중이므로 다음 노드 전 새 HEAD를 확인한다. 이 보고서는 새 공급자 내용을 읽은 기록이다. Root가 별도로 수행하는 전체 저장소·branch·백업 폴더 조사를 대신하지 않는다.

**조사한 최신 인계·계약에서는 PHYS02 100 K와 같은 상태로 승인된 새 RR 응답, 실제 recipient nb, source와 호환되는 유한 RR history가 확인되지 않았다.** 다음 단위는 보존된 PHYS02 H/He 밀도 정의로 조건부 H1/He4 baryon inventory를 명시하고, 그 상태에서 finite source의 밀도량을 per-baryon 진단량으로 연결하는 작업이 직접적이다. 기존 PR109의 nb/null 판정과 10000 K RR 연결 보류는 그대로 보존한다.

## 관찰한 identity

| 대상 | 실제 관찰 HEAD | 의미 |
|---|---|---|
| WU provider-registry / PR150 | `b81c668abd903faecaf913213937c378970f3458` | 이전 `35bb7f29`에서 3 commits 전진; R6 시작 |
| REC program-expansion / PR138 | `4a8e541030ee2cbd02e26ba671083b705d309d49` | 고정 programme branch는 그대로 |
| REC source-synthesis / PR139 | `d6dbe39a4923439547c01695d9020ba39367ea90` | 별도 후속 branch를 직접 읽음 |
| HE program-expansion / PR102 | `ac6042a6b0610b09d0576538767ee0299389a5eb` | 변경 없음 |
| 중앙 sandbox | `152b82cac23fedcb75a9effe0c159bae3d800c01` | CR의 M=`1a38f94f` 이후 BASS 반환 1 commit |
| REI causal-prefix / PR240 | `fbb55bcd0c77990b62470862a9f4a70647d0c5c9` | affine-history 이론/정적 구현 후속; 수치 실행 HOLD |

REC 두 ref에서 root `AGENTS.md`는 실제 404였다. WU AGENTS SHA256은 `aa819204f62805caad7f1689fe64a07c4876d88d73332cfe2b285a431cd044a0`, HE는 `32d09d1e6262e1eb3579de1a66e325afd2ba181a8de69313d907b6fb1e8aebfb`, 중앙은 `ab29a05cac922bd393dc04f7f280a0d4e1d7289ae6ea24291f48fd7cf7b2e8eb`다.

## 새로 채택할 관찰과 남은 입력

### WU R6

[고정 계약](https://github.com/cosmosapjw-quantum/WU088_HH/blob/b81c668abd903faecaf913213937c378970f3458/research/provider_registry_molecular_r6_20261027/CONTRACT.json)은 literal native 100 K의 Gibbs interval과 forced finite-block certificate를 대상으로 한다. 입력은 **HD + para-H2**, J=0…8, vibrational state `UNSPECIFIED`, 선택한 downward edge 9개다. 누락 channel은 `MISSING_NOT_ZERO`다.

같은 숫자 100 K라는 사실만으로 CR bath와 같은 물리 상태가 되지 않는다. WU clock은 `tau = n_coll × (1e-11 cm³/s) × t`이며 **n_coll, physical consumer, GL2022 destruction payload는 null**이다. 원문 에너지 literal의 관측 불확실성도 미공급이다. 따라서 WU 상태/밀도/clock을 PHYS02에 대입할 근거가 없다.

고정 `WORKFLOW_RECORD.json`은 R1–R3/C1–C3 **6/20**, local DAG **11/28**이다. 고정 execution ledger의 primary/reference/Wolfram 실행 목록은 비어 있다. 새 primary 60 CPU-s, reference 60 CPU-s, Wolfram time limit 30 s는 WU의 별도 유한 allowance이며 CR 예산이 아니다. PHYS91 remaining `[0,0,0]`, global remaining null, HH_R10 OFF, production NOT_ISSUED, L4 false를 유지한다. Primary reference 28/28은 source 접근성 범위다.

### REC 후속 branch

[최종 handoff](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/d6dbe39a4923439547c01695d9020ba39367ea90/research/rec_source_synthesis_20261027/HANDOFF_KO.md)는 source synthesis의 실제 20/20 전달을 기록한다. HD의 24 actual cases와 21 controls, 1,240 exact retimings·313 Peano chords·30 history controls가 추가되었고, 원 35 Hz gate의 **7/8 FAIL**과 12 causal-prefix skips는 보존된다.

HD native 온도는 50/100/200 K이며 p/o-H2 혼합이나 외삽은 승인되지 않았다. 실제 REC history는 그 owner의 native recombination source다. PHYS02의 상태·밀도·proper clock·electron birth measure를 대신하지 않는다. `physical_epsilon`과 outgoing bound는 null, physical coverage는 **0/313**, H6/H7 OPEN, L4 false다. 새 단위 측정 CPU 14.113983738 s와 그 별도 1,020 CPU-s 한도, unknown symbolic/metadata 비용을 CR에 합산하거나 이월하지 않는다.

### HE

[고정 handoff](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ac6042a6b0610b09d0576538767ee0299389a5eb/research/program_expansion_20261025/continuation_20261025/HANDOFF_KO.md)의 범위는 18 scalar providers, 27 transport pairs/243 thermal-Q expressions, H–He 9Q행과 조건부 finite-mass/Maxwell heat/linear-drift drag 구현이다. Tstar 50–50000 K는 source 유효범위다. 실제 isotope/state/mass 대응, 선택 Qbar11 값과 calibrated source uncertainty가 여전히 열린 입력이다.

검증 CPU 0.282464889 s와 8 CPU/30 wall cap은 원 측정 범위를 유지한다. HE101은 C8 PARTIAL_EXPORT, 19/20, reserve0, 실제 PASS/FAIL/FAIL이다. 새로운 100 K CR RR 응답이나 recipient nb를 공급했다고 읽지 않는다.

### REI와 최신 중앙 BASS 반환

[REI affine-history handoff](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/fbb55bcd0c77990b62470862a9f4a70647d0c5c9/research/rei_expanded_event_consumer/affine_history_enclosure_20261027/HANDOFF_KO.md)는 interval-monotonicity 정보집합에서 affine-history의 lower/minimum 및 upper/supremum과 가법성을 유도한다. 새 16 test methods는 작성·정적 검토되었으나 **실행 0, NOT_RUN_BUDGET_HOLD**다. 기존 3,189/3,189 검사는 재사용 근거이며 새 구현 실행으로 세지 않는다. Planning 15.077490885/원 cap10, presentation known+reserves 43.787562494/원 cap30, main 595.225063/600 NO_MORE_IVPs를 그대로 보존한다. `b=1.4e6 m^-3`는 normalization fixture이며 actual nb가 아니다.

[중앙 새 BASS 반환](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/152b82cac23fedcb75a9effe0c159bae3d800c01/research/orchestration_expansion_20261025/returns/BASS_B3H_NATIVE_HISTORY_INVERSION_20261027.json)은 실제 represented REC-native H Lyalpha history의 reconstruction과 finite photon return이다. Source S는 `0bdbd2ad1357c4b3141d3488a94534d082d1a0cf`; reference nH는 약 2.5025e8 m^-3다. 이것을 PHYS02 nH=140 m^-3 상태로 옮기지 않는다. QSS/non-Lyalpha physical energy owner와 full physical transaction은 아직 미승인이다. 새 photon 공급 후보로 조사할 수 있지만, 실제 clock/volume/frame/history/ownership을 별도 결속해야 한다.

`CENTRAL_COMPARISON.json`은 M=`1a38f94f`와 `152b82ca`를 직접 비교한다. 변경 original node는 B3h 하나이고, **다른 87 nodes·17 edges·전체 top metadata·CR proper S/D 링크는 동일**하다. 원 중앙 **27/88, 효과 0**, N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4 false를 유지한다. Literal `COMPLETE` prefix 수 18과 선언된 scoped 완료 27은 다른 counter다. 별도 미병합 working 32/88은 합산하지 않는다.

## 실제 백업 근거의 수준

| 공급자 근거 | 읽은 실제 receipt | 해석 |
|---|---|---|
| WU R6 S01/S02 | 각각 361224/429230 bytes; 양쪽 original-byte SHA/CRC/member/Git-blob 일치 기록 | 새 실제 dual 원문 readback이 기록됨; 이 조사에서 다운로드를 반복하지 않음 |
| WU R4/R5 | `BACKUP_INTAKE_SUMMARY.json` | R4 S10 및 R5 S01…S10 backfill **in progress**; 완료 ACK를 추정하지 않음 |
| REC final source | 39996332 bytes, 480 members, SHA256 `b4d74d7beb8ca9fd1bda1dcdbc4997685c2436f80bf85f4ab7f14e2805376c61` | 실제 dual ACK/size와 local CRC/SHA; remote whole-ZIP SHA 재다운로드 주장은 없음 |
| HE source | 1013057 bytes, 89 members, SHA256 `0405ee8803dfaa72a6a54a8bc005376c79c15e5eecf95f23a50582ec0fc49ef9` | 실제 dual ACK/size; 원격 전체 ZIP cryptographic readback 주장은 없음 |
| REI affine source/metadata | 73259/24100 bytes, 실제 dual ACK/size | local CRC와 source Git-blob 검증; 새 remote ZIP restore를 주장하지 않음 |

WU S02의 실제 provider ID는 Dropbox `id:BSpOijBcT10AAAAAAEDHfQ`, Drive `1t6qcRL0qGx7vzXPguEaYSeqM8XiVl7bw`이며 ZIP SHA256은 `afbd8356f97c183fd96cf99df2e173b3831134eab19b198f3eb2d19b136d7b5f`다. 다른 provider ID와 원문 evidence는 각각 raw receipt에 보존했다.

## 제안하는 좁은 다음 과학 단위

보존된 PHYS02 정의 `nH=140 m^-3`, `YHe=0.248`, `nHe=nH*YHe/[4*(1-YHe)]`, T=100 K를 사용한다. **H1/He4만을 포함한 명시적 조건부 inventory**를 새 계약으로 채택하면 `nb=nH+4*nHe=nH/(1-YHe)`를 같은 모델에서 구성할 수 있다. 이는 외부 bath의 nb를 빌리는 작업이 아니다. 기존 source가 처음부터 nb를 명시했다고 소급하지 않고, 다른 baryonic species가 물리적으로 존재하지 않는다는 관측 주장도 하지 않는다.

이 inventory와 정확히 같은 recipient state/frame/proper-volume/clock/support를 명시하고, 새 bounded 예산 아래 finite source density의 per-baryon number/kinetic-energy 진단을 구현·검증하는 것이 다음 실행 가능한 조각이다. 같은 scalar denominator만으로 donor/recipient 상태의 동등성이 증명되지는 않는다.

원 저장 electron source_vectors는 HI/HeI secondary births를 집계한다. 그것만으로 HI→HII와 HeI→HeII daughter counts를 추정하거나 neutral closed chemical event를 만들 수 없다. Fast electron count/energy normalization과 화학 abundance update를 구별하고, 후자는 실제 species-resolved event ledger가 있을 때 결속한다. Actual RR·retained photon은 맞는 응답과 유한 horizon이 생기기 전까지 null을 유지한다. 후속 unit은 원 20 CPU-s의 잔여를 자동 이월하지 않는다.

이번 조사에는 기존 과학 재실행, solver/import/quadrature 실행, 기존 파일 수정, Git mutation이 없다. 개인 대화 전체 검색 unavailable과 Drive partial inventory 한계를 유지한다. 확인하지 않은 branch에 대한 전역 부재나 strong no-go 결론은 내리지 않았다.
