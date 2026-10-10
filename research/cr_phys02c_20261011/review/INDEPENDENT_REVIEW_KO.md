# CR-PHYS02C 독립 최종 판정

## 판정과 범위

**PROMOTE_SCOPED.** 동결한 H analytic Coulomb oscillator와 He Kim2000 인쇄 계수로 총 이온화율과 느린 딸전자 SDCS를 함께 구성한 조건부 full BED 비교를 연구 결과로 채택할 수 있다. 기존 PHYS02B 원천·bath·CCC 유효 여기 비용·Coulomb closure·수송을 유지한 2400/4800 node 비교에 한정한다. 이 판정은 실제 단면적의 실험 정확도, 원자 채널 완전성, CCC 물리 문턱 또는 production history의 승격이 아니다.

후속 `CR-PHYS02C-NCP-MATCHED-THIRD-GRID`는 **실제 payload 검증과 자원 admission을 전제로 READY로 갱신하도록 권고**한다. 현재 NCP 실행은 `PREPARED_NOT_EXECUTED`다. 과학 판정 당시 Git 게시와 두 원격 백업의 최종 영수증은 아직 생성되지 않았으며, 이 검토는 그 성공을 주장하지 않는다.

## 검토자의 독립성과 동결 대상

검토자는 `/root/phys02c_independent_decision`이며 호스트가 제공한 모델 표시는 GPT-6 Astra Pro다. 연구·코딩 harness v4.0.0의 진입점, 공통 지침, 모델 라우팅과 독립 판정 phase를 읽었다. 후보의 원문 선택, 물리 계약, 구현, A001/R001 검증 설계 또는 실행에 참여하지 않았다. 이 검토에서는 후보 코드나 허용값을 수정하지 않았고 수송을 실행하지 않았다. 작은 읽기 전용 산술 확인과 운영 반례만 수행했다. 운영 수정은 별도 작업자가 수행했다.

검토 대상은 `REVIEW_PACKET.json`, SHA256 `a039e45109112b757037ad3dec0a55230d2ee40c4007f1f6cb1f5057440a93bc`, 16,648 bytes다. **목록의 95개 파일 모두 실제 bytes/SHA256이 일치했다.** 이 검증과 별도로 부모 manifest의 40개 파일 및 새 두 spectrum NPZ의 실제 identity를 확인했다. 파일 identity 확인은 과학적 타당성 판단을 대신하지 않는다.

내용 검토는 과학 계약·유도, 후보와 부모 수송 코드, targeted runner, 소스 감사와 별도 50자리 결과, 실제 R001/프로세스 영수증, paired-delta 산술, 열 진단 코드·결과·그림, 주장 및 실패 상태, NCP 계약·실행기·복원/수집기와 운영 수정 증거에 집중했다. 이전 모든 연구를 새로 검증했다고 주장하지 않는다. 직접 열람한 주요 1차 자료는 아래에 명시했다.

## 과학·구현 판단

사용한 식은 NIST의 가산형 BED SDCS와 일치한다. 느린 전자 구간 `0 <= W <= (E-B)/2`의 적분에서 Mott 제곱 역수항은 `1-1/t`, 단일 역수항은 `ln(t)`를 주므로 계약의 총률이 도출된다. 같은 진동자 세기에서 `Ni`, `K=2-Ni/N`, 유한 상한 `D(t)`와 SDCS를 계산하는 구현을 확인했다. BEQ의 Q만 바꾸는 방식으로 대체하지 않았다. Kim2000 Eq1의 기호 불일치를 가산식 및 같은 논문의 적분 total에 맞춰 명시적으로 처리한 것은 타당하다. 출판사 정오표를 확인했다는 주장은 없다. [NIST 식](https://physics.nist.gov/PhysRefData/Ionization/Eqs/latex.html), [Kim–Johnson–Rudd2000](https://doi.org/10.1103/PhysRevA.61.034702).

H에서 `epsilon=1+w`, `k=1/sqrt(w)` 변환과 threshold limit는 원문의 식과 맞는다. He의 원래 인쇄 계수로부터 `Ni=1.61008048`, `Qdf=0.913040733333...`, `K=1.19495976`가 나오는 것도 일치한다. 양의 oscillator와 양의 Mott 괄호, `K>0`가 허용 정의역의 SDCS 양성을 지지한다. 독립 source oracle은 다른 스크립트와 50자리 계산을 사용하지만 동일하게 선택한 원자 모형에 의존한다. 이를 독립 실험 검증으로 읽지 않는다. [H 원문 Eq5/9/10 및 Table1](https://arxiv.org/pdf/2208.02111).

부모 `Cascade`를 바꾸지 않고 이온화 객체만 교체했다. 느린 전자를 반구간에서 한 번 선택해 `W`와 `E-B-W` 두 딸전자를 만들고 결합 장부에 `B`를 넣는 방식은 사건당 전자 수 증가 하나와 에너지 보존을 맞춘다. 상태가 에너지 가중 전자 수라는 점, `n*sigma*v`의 사건률, 시간 무차원화와 SI 출력 변환도 연결된다. 위 문턱에서 생기는 변화가 단방향 수송의 직접 저에너지 출생 성분에 새로운 물리 효과를 만드는 것으로 해석되지 않았다.

NIST는 SDCS를 별도 총률에 맞춰 정규화하는 구성을 설명한다. 따라서 기존 BEQ-total/normalized-BED-shape 모형을 대수적으로 무효화하지 않고 별도의 조건부 표현으로 비교한 서술을 유지해야 한다. [NIST introduction §B](https://physics.nist.gov/PhysRefData/Ionization/intro.html).

## 실제 수치 증거와 해석의 한계

R001은 실제 exit 0, 15개 scoped check 통과, 수송 호출 2회다. 원자 적분 비교 최대 상대차 `4.532381858e-9`는 고정 기준 `2e-8` 이하이고, 새 연산자·전파·terminal 장부 및 양성 검사도 계약을 만족했다. 새 4800 node의 물리적 총률/수치 sharing 적분 보정계수는 1과 최대 `9.568e-13`만큼 다르다. 기존 물리 표현 사이의 정규화와 이 수치 보정을 구분한 판단이 맞다.

저장된 legacy와 새 결과의 원천 coverage 및 Python/NumPy/SciPy 버전은 같다. 17개 핵심 output-vector 행의 두 격자 차이, paired delta와 r를 저장 JSON에서 독립 재계산해 모두 일치함을 확인했다. 최대 핵심 r는 `0.0008104320777`이고, 모두 사전 기준 `r<1/3`과 부호 일치를 만족한다. 실제 채널 격자 변화의 최대는 1.38643%, low-cross 전자 수는 1.14123%로 각각 2%, 3% 기준 이하다.

열률의 단일 모형 격자 변화 0.0489060%가 두 모형 차이 0.0258541%보다 크다는 점을 보고서가 드러낸다. 짝지은 차이의 수렴이 훨씬 안정적이라는 증거는 있으나, 두 격자로 공통 체계 오차의 상계를 얻었다고 할 수 없다. 95개 전체 행의 66개 경험적 분리, 22개 정확한 영 차이, 7개 미분리를 보존했다. 변하지 않는 직접 저에너지 성분의 roundoff는 물리 효과로 승격하지 않았다.

새 4800 node의 누적 H 이온화 +5.19218%, He 이온화 +0.516080%, 열률 +0.0258541%라는 비교는 저장 결과와 맞는다. 두 원자 표현을 함께 바꾼 결과이므로 H 또는 He 하나의 독립 민감도로 읽을 수 없다. 활성 운동에너지 98.2874%와 같은 연산자 terminal-yield 대비 유한시간 열률 3.41777%의 구분도 맞다. 부모의 독립 시간 전파 검증은 상속된 증거이며 이번 4800 node에 새 독립 시간 oracle을 실행했다는 주장은 없다.

저장 NPZ로 재구성한 Coulomb 열률은 장부와 최대 `2.31e-14` 상대차를 보인다. 고에너지 출생 성분의 전체 가열과 실제 `E<=10 eV`에서의 가열은 구별되어 있다. 후자의 직접 저에너지 출생 열률 대비 2.38893% 및 legacy 대비 +1.37618%는 4800 node 후처리 값이며, 별도 matched low-mask 격자 수렴 인증이 없다는 한계를 유지해야 한다. 그림의 단위·범례·두 격자 표시와 비인증 주석도 직접 확인했다.

## 발견한 운영 결함과 수정 확인

초기 `ncp/ops.py`는 현재 leaf cgroup만 확인해 중간 조상 제한을 놓쳤다. 읽기 전용 합성 반례에서 host128 GiB, leaf 무제한, 부모8 GiB/current1 GiB 및 0.5 CPU를 주었을 때 **잘못된 admitted=true, working104 GiB**를 반환했다. 이는 NCP admission의 실제 결함이었으며 과학 수송 결과의 결함은 아니었다.

수정본 SHA256 `86f03aac7e2aa5cc6bccc794f466eca204d524d4ef5a5a74305bbd96ff659dfa`는 cgroup v2 membership/mount를 해석하고 읽기 가능한 조상을 모두 조사한다. 각 finite memory 제한의 남은 여유와 host available의 최소값, CPU quota 최소값, affinity와 effective cpuset 교집합을 사용한다. 조상·mount 해석 실패는 typed HOLD다.

| 판별 사례 | 수정 후 결과 |
|---|---|
| 부모8 GiB/current1 GiB, quota0.5 | reserve1 GiB, working6 GiB, HOLD |
| 부모32 GiB/current25 GiB, quota2 | reserve4 GiB, working3 GiB, HOLD |
| 부모32 GiB/current1 GiB, quota2 | working27 GiB, ADMITTED_RESOURCE_ONLY |
| 불명확 membership/mount 또는 필수 조상 metadata 누락 | capacity 미확정, HOLD |

별도 작업자의 여섯 운영 fixture와 보존된 원 결함 재현을 읽었다. 검토자도 수정본의 첫 사례 산술을 독립 재계산해 일치시켰고, 실제 현재 호스트는8 GiB·quota8이며 최소12 GiB working 조건을 만족하지 않아 HOLD임을 확인했다. launcher와 과학 후보 코드의 bytes는 바뀌지 않았다. **이 운영 blocker는 최종 packet 동결 전에 해소됐다.** 지원 범위는 읽기 가능한 cgroup v2 계층이며, 필수 metadata가 없는 플랫폼에서는 실행을 추정하지 않고 HOLD한다. 이 결과는 실제 NCP 환경 검증이나 64-core 성능 측정이 아니다.

## 다음 노드와 유지할 미해결 사항

후속 NCP 노드는 같은 source·bath·CCC·Coulomb·FP64·격자 규칙·허용값에서 full BED와 legacy를 각각9600 node로 계산하는 순차 두 호출이다. root가 실제 review hash와 READY DAG를 연결하고, 최종 전체 payload manifest 및 두 저장 reference identity를 확인한 뒤 실제 자원 admission을 통과한 경우에만 실행할 수 있다. 전체 wall3600 s, 최대 호출2회, 실패·timeout 보존과 반환 collector를 유지한다. 재계산 결과에는 별도 독립 Astra 판정이 필요하다.

완결 묶음에는 부모 `tests/verify_cascade.py`도 포함해야 한다. NCP의 원자 preflight가 이 파일을 실행하지는 않지만 identity를 읽기 때문이다. 현재 실제 파일의 존재와 기록된 identity는 확인했다. 최종 archive/FILE_MANIFEST의 closure는 게시·포장 단계에서 확인할 요건이며, 아직 생성되지 않은 원격 백업의 완료를 이 review로 대체할 수 없다.

CCC 보조 조사에서 신규 원문 증거를 확보하지 못한 사실을 읽었다. 따라서27개 native marker의 Hamiltonian/분광학적 의미, NIST Q 계보 및 CGI 동등성, HeII·고준위 채널·recoil·thermal diffusion·photon transport·bath feedback·전체 source history는 미해결이다. 현재 고정 모형 비교에서 이 한계를 명시했으므로 scoped 승격을 막지는 않으며, 해당 물리 교체 또는 production 승격의 근거도 되지 않는다.

`PHYS02_DELAY OPEN`, `production_history HOLD`, `atomic_G02 UNRESOLVED`, `b_grid NO_GO`, `all_bound OPEN`, `R17B2B NO_CERTIFIED_SOURCE_SHARPENING`을 모두 유지한다. 모델 route의 상충 metadata는 `UNVERIFIED_CONFLICTING_METADATA`, 성능 비교는 `NOT_EVALUATED`로 유지한다.

검토 완료: 2026-10-10 17:44:48 UTC. 결과와 허용 후속 갱신은 `FINAL_DECISION.json`에 기계 판독 형태로 기록했다.
