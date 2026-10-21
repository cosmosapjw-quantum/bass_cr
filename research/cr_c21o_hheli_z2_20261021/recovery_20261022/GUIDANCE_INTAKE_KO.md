# C21O 재개: 첨부 지침과 역사 자료의 한정 조사

## 판정과 단계

현재 사용자 지시는 중단 작업의 재개다. 이 조사 범위는 `stage:C10`의 복구·배송·인계와 그 선행 자료 확인이며, 첨부 05 실행기의 `J. Packaging / docs / release`에 대응한다. 첨부된 범용 감사 프롬프트가 전체 low-ell/11-family 재감사, 새 Rust 포팅, 새 ODE sweep를 자동으로 시작시키지는 않는다. 기존 C21O의 실행/검증을 다시 확인할 때에는 복원한 권위 영수증·source·raw를 사용해야 하며, 이전 대화 요약은 복구 주소 역할만 한다.

이번 lane은 과학 코드·기존 raw·provider·Git을 수정하지 않았다. ODE 실행 0회, 빌드 0회, Rust 설치 0회, 새 plot 생성 0회다. 이전 C21O 과학·plot 검토를 재실행하거나 새 검증으로 승격하지 않았다.

## 실제 읽은 지침과 적용

| 첨부 | 읽은 범위 | C10에서 적용하는 사항 |
|---|---|---|
| 01 Low-ell Bianchi Einstein–Boltzmann Solver | 전문 | 실제 사용된 코드와 결과만 구현 근거로 인정한다. non-tilted LRS background pilot을 11-family/CMB map/likelihood ready로 승격하지 않는다. same-physics/tolerance/output 없는 가속 배율을 채택하지 않는다. 문서 자체의 감사 대상은 htt/bass이며 현재 BASS_CR에 전체 8역할 감사를 기계적으로 이식하지 않는다. |
| 04 Adaptive CMB Code Development Protocol | 전문 | 정의·단위·부호·source path·observable contract를 복구한다. 변경 없는 suite를 재실행하는 대신 복원 bytes와 기존 근거를 확인한다. 실제 mismatch가 발견될 때 최소 수정과 그에 맞는 검산을 수행한다. |
| 05 DAG-Governed Research Executor | 전문 | completed/partial/failed/unknown 상태를 먼저 재구성하고 다음 실제 미완료 node 하나를 선택한다. C10에서는 문서/백업 상태와 과학 완료 상태를 분리한다. |
| 07 Figure Residual Error Pass | 전문 | 기존 v2 plot가 복구되면 동일 byte identity로 기존 검토를 재사용한다. 새 그림/새 표기 수정이 있을 때에만 겹침·축소 가독성·semantic drift를 제한적으로 확인한다. |
| 08 Figure Hostile Audit | 전문 | 그림이 본문보다 강한 물리 주장을 암시하지 않게 한다. generic isotope panel을 all nuclear reactions 완성으로 표현하지 않는다. 새 plot 변경이 없으면 기존 independent review를 반복하지 않는다. |

첨부 04/05가 참조하는 별도 `PHYS-MATH AUDIT`, `PHYS-MATH-CODE AUDIT` 제목의 독립 preset 파일은 제공된 20개 목록에서 식별되지 않았다. 두 파일 안에 명시된 실제 체크리스트는 읽고 적용했다. 이 한정 확인을 독립 preset 원본의 전문 열람으로 표시하지 않는다.

## 파일·archive 조사 근거

`ATTACHMENT_BYTE_INVENTORY.json`은 제공된 20개 일반 파일의 현재 크기·mtime·실제 SHA256을 담는다. `ARCHIVE_HEADERS.json`은 9개 관련 ZIP/tar의 전체 member 이름·크기를 보존한다. Rust toolchain tar.xz의 192 MB byte SHA는 계산했지만 설치하거나 전체 header를 풀어 보지는 않았다. archive header 해석은 성공했으나 모든 archive의 모든 payload CRC/압축 원문 재검증을 했다는 의미는 아니다.

- 16번 checksum에 기록된 `f30a4da90c68819d16df44632da91fa76e443df3b8dcf1d55c843bede1e1fb29`가 17번 실제 ZIP SHA256과 일치한다. 파일명과 과거 절대 경로가 달라도 정확한 ZIP bytes의 동일성을 확보했다.
- 9개 archive의 member 이름에서 `c21[l-z]`, `20261021`, `20261022`, `hheli_z2` 표식은 검출되지 않았다. 이는 제목 기반 한정 결과이며 archive 전체에 새 과학 결과가 절대로 없다는 판정은 아니다.
- 20번 PDF는 36쪽 `HTT 수학·물리·통계 종합 이론 보고서`다. 처음 두 쪽과 metadata를 실제 읽었으며 표지 날짜는 2026-09-13, 기존 근거 종합으로 새 계산/증명 판정은 수행하지 않았다고 명시한다. 전체 36쪽을 새로 감사하지 않았다.
- 앞선 메시지에 나왔던 `원시 광핵반응 및 재이온화 네트워크(3).png`는 이번 20개 제공 파일에 포함되어 있지 않다. 그 이미지의 내용·species·reaction list는 이번 조사에서 회수하지 못했으며 추정하지 않았다.

## 실제 source 열람과 재사용 판정

| 자료 | 실제 확인한 source/내용 | 현재 수용 |
|---|---|---|
| 14번 bianchireview87 | `bianchi/thermo/recombination.py`: H-only Peebles ODE, H/He Saha, H(z) callback, optical depth/visibility. 함수 목록과 source anchors 저장. 해당 파일에 lithium/Li6/Li7/LiIII/LiIV 표식 없음. | 고적색편이 재결합의 역사적 코드 참조. C21O의 z20→2 H/D/T/He3/He4/Li6/Li7 + prescribed UV/T chemistry를 대체하지 않는다. |
| 14번 bianchireview87 | `bianchi/q/species.py`: component별 moment 합산과 대칭 교환 coupling. | 성분 분리 설계의 역사적 참조. 현재 source와 tolerance를 유지한 이식·검증 근거는 이번 조사에 없다. |
| 11번 automation kit | README, CURRENT_STATE_PATCH80R_AND_NEXT_STEPS: PATCH80R Type-II CSR 및 후속 GateBundleDraft 문서 작업. runtime solver/fitting gates 닫힘. | 새 C21O 실행 결과로 수용하지 않는다. 백업/manifest 패턴 참고 가능. |
| 10번 R-DAG archive | 23 member: 광선/광학/chart/ODE Rust와 Python dispatcher/tests. | 다른 계산 경로의 역사 source. C21O 가속 검증으로 수용하지 않는다. |
| 17번 locked Rust | 실제 `src/lib.rs`, `src/ode/charts.rs`, `src/ode/solve.rs`의 함수와 anchors 확인. 오래된 README보다 실제 source 범위가 넓고 11-state tilted chart, kinetic/collision/Thomson/grid transport binding도 존재. | 재사용 후보는 존재하나 C21O 62/78-state 경로와의 동일 물리 binding 및 같은 출력 검사가 없다. 읽은 README의 속도 배율을 C21O 배율로 전용하지 않는다. |
| 18·19번 문헌 ZIP | 각각 7·8 PDF member 이름만 열람. | 원천 문헌 보관함으로 분류. 이번 C10을 위해 전권을 재검색·재번역하지 않았다. |
| 13번 xAct | 693 member header. | symbolic tool archive. 설치/실행 근거 없음. |

`SELECTED_ATTACHMENT_EVIDENCE.json`은 위 source member SHA256, 실제 함수 목록·줄 anchors, PDFinfo 및 처음 두 쪽 텍스트 열람 결과를 담는다. archive 추출 또는 소스 실행 없이 읽었다.

## 현재 남은 구체적 의무

1. C21O content/document/source/raw를 영수증의 digest로 복원하고 GitHub 실제 ref와 대조한다. 이 작업은 parent 및 다른 intake lane의 범위다.
2. 이전 Google Drive main archive upload의 `UNKNOWN_NO_ACK`는 known folder에서 exact name으로 조정한다. 결과가 불명확하면 부재/실패로 단정하거나 무조건 재업로드하지 않는다.
3. 기존 45+6 결과는 conditional prescribed-UV/T photoionization+Case-A RR→electrons→Thomson LRS pilot으로만 전달한다. 모든 핵반응·thermal/stellar/UV transfer coupling 완료는 별도 OPEN/HOLD다. atomic population coverage와 active reaction coverage를 구분한다.
4. H/He/Li 전체 nuclide/isotope/ion 목표를 새 physics task로 진행할 경우 실제 species/charge-state/reaction 목록, 열적 closure, source spectrum, energy accounting을 먼저 결속해야 한다. 없는 이미지에서 reaction list를 복원했다고 쓰지 않는다.
5. 복원된 v2 plots를 사용하고 signed amplitude/Frobenius norm 및 photon/neutrino/matter tensor 합성의 표기를 유지한다. 원 결과의 error ceiling(`global_error_bound=null`)을 바꾸지 않는다.

C10의 다음 실제 행동은 **과학 원본과 최신 원격 상태를 확인한 뒤 미확정 백업 상태를 닫고 복구 가능한 인계 자료를 확정하는 것**이다. 이 자료 조사에서 새 물리 P0가 발견되었다는 주장은 하지 않는다. 기존 C21O 과학 채택 판정 역시 이 lane에서 새로 수행하지 않았다.

## skill_context_used

- `c39/physmath-research-loop`, PhysMath Research Loop 1.3.0, SKILL.md 전문.
- 같은 package의 `references/CODING_LOOP.md`, 특히 stage:C10 release readiness/수행 범위/재개 가능한 package 계약.
- 같은 package의 `references/POLICY_INTEGRATION.md`: 선택 단계, 완료 근거 재사용, 유한 검토, typed identity, blind retry와 생산적 repair 구분.
- Parent가 부여한 read-only C10 자료 조사 범위와 지정 write path를 준수했다.
