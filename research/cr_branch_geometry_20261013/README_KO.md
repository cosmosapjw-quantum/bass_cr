# BASS_CR — 실제 반응 branch와 Bianchi geometry

**CR-THEORY-BRANCH-GEOMETRY-20261013**

실제 HI kernel의 조성·thermal electron feedback을 가진 endpoint, 반응으로 생긴 원자의 thermal cutoff 교차, 지정된 Bianchi I geometry 이후의 실제 에너지와 HI/HeI kernel 재결속을 구성한 연구 단위다. 직전 KC1–KC7의 source와 보존 근거를 재사용했다. 최신 판정·정확한 가정·claim별 근거는 [RESULTS.json](RESULTS.json), [CONTRACT.json](CONTRACT.json), [CLAIMS.json](CLAIMS.json), [review/](review/)의 심사 기록을 따른다.

## 결과와 읽는 순서

[전체 PDF](latex/report.pdf)를 먼저 읽고, [보고서 원고](REPORT_KO.md)와 네 상세 유도를 확인한다. 실제 입력과 출력은 examples/ 및 results/에 있고, 다음 재개 지점은 [HANDOFF.json](HANDOFF.json)과 [NEXT_DAG.json](NEXT_DAG.json)에 있다.

| Claim | 이번 연구 범위 |
|---|---|
| BG1 | 실제 HI sharing contribution과 별도 stopping edge의 fixed-branch endpoint. 명시한 extent domain에서 self-map과 \(\bar q=0.00031<1\)을 구성한다. |
| BG2 | 유한 source parameter 모형의 exact rational log enclosure와 residual을 통한 endpoint·temperature·cutoff 오차증명. |
| BG3 | 반응이 atomic weights를 바꿀 때 inherited branch에서 시작하는 유한 repair scan과 conservative threshold jump. |
| BG4 | 실제 HI node 4762/sharing 38을 사용하는 \(\chi=4\) construction. 생성된 첫 node가 extent \(s=1/4\)에서 cutoff로 편입되며, 복수 EOS branch에서는 이전 branch가 continuation을 선택한다. |
| BG5 | Geodesic synchronous Bianchi normal에서 massive kinetic-energy/work 법칙과 diagonal Bianchi I의 유한 momentum map. |
| BG6 | 이동 후 실제 parent energy에서 원래 HI/HeI sharing·threshold·rate를 다시 평가하고 같은 parent의 사건 열에 결속한다. |
| BG7 | 양의 barycentric energy projection의 count·first moment 보존과 지정한 cell/regular observable의 weak-error bound. |

자세한 증명은 [COUPLED_BRANCH_KO.md](derivations/COUPLED_BRANCH_KO.md), [REACTION_BRANCH_KO.md](derivations/REACTION_BRANCH_KO.md), [COVARIANT_GEOMETRY_KO.md](derivations/COVARIANT_GEOMETRY_KO.md), [GEOMETRY_REBIND_KO.md](derivations/GEOMETRY_REBIND_KO.md)에 있다. 선별 원전 비교와 서지는 [LITERATURE_KO.md](derivations/LITERATURE_KO.md), [SOURCES.json](SOURCES.json)에 있다.

## 먼저 기록된 결과 읽기

다음 명령은 이 연구 단위 디렉터리를 작업 위치로 두고 실행한다. 결과를 읽는 데 science 재실행은 필요하지 않다.

```bash
python3 - <<'PY'
import json
from pathlib import Path

for name in (
    "results/COUPLED_BRANCH_CHECKS.json",
    "results/REACTION_BRANCH_CHECKS.json",
    "results/GEOMETRY_REBIND_CHECKS.json",
):
    record = json.loads(Path(name).read_text())
    print(name, record.get("status", "recorded"))
PY
```

각 JSON에는 해당 실행의 수치·exact values·입력/source identity·검증 범위가 들어 있다. Coupled-branch 실행 뒤 이루어진 `KC1-KC8` → `KC1-KC7` 재사용 라벨 교정은 [COUPLED_BRANCH_METADATA_PATCH.json](results/COUPLED_BRANCH_METADATA_PATCH.json)에 별도로 기록했다. 원래 실행 당시 hashes는 [COUPLED_BRANCH_CHECKS.json](results/COUPLED_BRANCH_CHECKS.json)에 그대로 남아 있다. Metadata 교정을 scientific rerun으로 해석하지 않는다.

## 문서 재빌드

문서 빌드에는 Python의 NumPy·Matplotlib, Pandoc, XeLaTeX와 아래 폰트가 필요하다. 작업 복사본에서 다음 명령을 사용한다.

```bash
python3 build_report.py
```

[build_report.py](build_report.py)에는 추가 CLI 옵션이 없다. REPORT_KO.md, 네 유도 문서, 선별 문헌 노트, **이미 저장된** reaction/geometry 결과와 증명된 닫힌 식을 읽어 그림과 CSV, LaTeX 본문, PDF를 만든다. Research solver, 과학 check, 원 kernel generator 또는 ODE를 호출하지 않는다.

이 명령은 figures/의 두 그림과 CSV, latex/manuscript.md, latex/body.tex, latex/report.tex, latex/report.pdf 및 컴파일 로그를 갱신한다. 기존 결과 JSON은 문서 입력으로 읽는다. 이미 만들어진 LaTeX만 다시 컴파일하려면 latex/ 디렉터리에서 다음을 실행한다.

```bash
xelatex -interaction=nonstopmode -halt-on-error report.tex
xelatex -interaction=nonstopmode -halt-on-error report.tex
```

LaTeX 그림 경로는 `../figures/reaction_branch.pdf`, `../figures/geometry_energy.pdf`이고, font 경로는 `fonts/`다. 따라서 latex/와 figures/의 상대 위치를 유지한다. 빌드 도구·폰트·TeX 환경이 달라질 때 생성 PDF가 byte 단위로 같다고 전제하지 않는다.

## 선택적인 새 reference 검사 실행

아래는 이번 단위의 실제 세 entry point다. 코드·입력·환경 변경으로 새 검사가 필요한 경우, **동결본을 보존한 작업 복사본**에서 해당 명령을 실행한다. 이 README 작성 과정에서는 실행하지 않았다.

```bash
python3 checks/check_coupled_branch.py
python3 checks/check_reaction_branch.py
python3 checks/check_geometry_rebind.py
```

| Entry point | 검사 범위 | 기본적으로 새로 쓰는 파일 |
|---|---|---|
| `checks/check_coupled_branch.py` | Exact extent self-map·수축률·log enclosure·endpoint·보존 및 unchanged capacity-map 대응 | `results/COUPLED_BRANCH_CHECKS.json`, `examples/COUPLED_BRANCH_ENDPOINT.json`, `examples/COUPLED_BRANCH_WOLFRAM_INPUT.json` |
| `checks/check_reaction_branch.py` | 실제 생성 atom의 branch 교차, 선택 규칙, energy/count 및 extent 관계 | `results/REACTION_BRANCH_CHECKS.json` |
| `checks/check_geometry_rebind.py` | 실제 momentum 이동, moved-energy HI/HeI 재결속, finite event 장부와 projection/weak error | `results/GEOMETRY_REBIND_CHECKS.json`, `examples/GEOMETRY_REBIND_WITNESS.json` |

기본 경로에 파일이 있으면 **덮어쓴다**. 새 실행은 당시 runtime과 source에 대한 새 근거이며, 배포된 historical execution identity를 대체하여 해석하지 않는다. 앞의 두 entry point에는 사용자 CLI 옵션이 없다. Coupled check는 저장된 construction input과 Python 표준 라이브러리의 Fraction 연산을 사용한다. Reaction 및 geometry check는 원 adapter를 통해 NumPy·SciPy와 보존된 실제 source inputs를 사용한다.

Geometry check에는 실제 `--output`, `--examples` 옵션이 있다. 별도 결과 경로를 지정하려면 다음처럼 사용할 수 있다. 지정한 파일이 이미 있으면 이 경로에서도 덮어쓴다.

```bash
python3 checks/check_geometry_rebind.py \
  --output repro/GEOMETRY_REBIND_CHECKS.json \
  --examples repro/GEOMETRY_REBIND_WITNESS.json
```

계산 라이브러리는 coupled_branch_solver.py, reaction_branch_continuation.py, geometry_kernel_rebind.py다. 이 라이브러리 파일 자체에 별도 사용자 실행 CLI를 가정하지 않는다. tests 실행이나 문서 빌드에 포함되지 않는 추가 물리 suite를 자동으로 호출하지 않는다.

### 저장된 Wolfram/xAct 근거

실제 scalar 실행 입력은 `checks/wolfram_branch_geometry_scalar.wl`의 **일반기호식·전제**이고, 원 결과와 실행기록은 `results/WOLFRAM_SCALAR_RAW.json`, `results/WOLFRAM_SCALAR_EXECUTION.json`에 있다. 실행 범위는 scalar identities 24개와 부등식 4개다. `examples/COUPLED_BRANCH_WOLFRAM_INPUT.json`은 숫자 결속용 보조 자료이며 그 숫자를 실제 Wolfram 세션에 주입했다는 의미가 아니다.

새 xAct 실행은 `checks/wolfram_xact_branch_geometry.wl`과 `checks/xact_branch_geometry_body.wl`에, 결과 및 실행기록은 `results/WOLFRAM_XACT_RAW.json`, `results/WOLFRAM_XACT_EXECUTION.json`에 있다. 실제 새 tensor identities 8개의 근거다. Wolfram/xAct 코드를 별도로 재평가하려면 해당 실행 환경과 script에 명시된 package 의존성이 필요하다. 문서 빌드와 세 Python check는 이 외부 실행을 시작하지 않는다.

## Source와 finite arithmetic의 적용 범위

상태 energy는 SI J이고 eV 표시는 명시적인 source coordinate다. \(c,\hbar,k_B\)와 기본 metric \((-+++ )\)를 유지한다. Counts·energy는 선택된 comoving cell에 대해 해석하고, thermal electron count, 핵종까지 포함한 thermal particle count, raw retained atom inventory를 구별한다. Base thermal energy와 retained thermal atoms의 moment를 중복 합산하지 않는다.

이 단위의 초기 재고와 geometry ratios는 **CONSTRUCTION**으로 표시했다. 선택 source channels와 정한 branch/domain의 수학적 endpoint가 연구 대상이다. 예를 들어 coupled 사례의 \(T\simeq100.35047956\) K와 매우 작은 residual certificate는 해당 유한 parameter map의 해와 계산오차이며, 큰 시간 간격의 실제 time-accuracy 또는 BASS_CR 전체 scenario의 물리 예측으로 확장하지 않는다.

Fraction 기반 보존은 finite input event columns에 대해 exact다. Source float coefficient, massive momentum/energy의 유한 표현, 원자 모형, 시간 이산화 오차는 각각의 기록과 가정대로 구별한다. Energy projection이 보존하는 것은 count와 first energy moment이며, 일반적인 momentum·anisotropic stress까지 exact라는 주장은 추가하지 않는다. Threshold를 가로지르는 단계에는 branch/event 처리가 필요하고, 하나의 regular cell에 대한 smooth error bound를 그대로 확장하지 않는다.

## 패키지 구조와 원 입력

| 위치 | 내용과 유지 조건 |
|---|---|
| `REPORT_KO.md`, `latex/` | 보고서 원고, 생성 LaTeX, PDF와 컴파일 로그 |
| `derivations/` | 네 이론 유도 및 선별 문헌 비교 |
| 최상위 세 solver 모듈, `checks/` | Scoped reference 구현과 실제 실행 entry points |
| `examples/`, `results/` | Construction input·raw event/endpoint·실제 검증 결과와 provenance |
| `inputs/prior/` | 직전 KC에서 채택한 source/evidence 복사본. 상대경로와 bytes는 `inputs/PRIOR_REUSE.json`을 따른다. |
| `inputs/prior/inputs/kernel_sources/` | 원래 상대경로를 유지한 atomic source, CCC 자료, 저장된 9600-node NPZ. 결속은 `inputs/prior/inputs/KERNEL_SOURCE_BINDING.json`에 있다. |
| `review/`, 최상위 계약·claim·DAG JSON | 심사 범위, identity, 채택 상태와 다음 연구 의무 |
| `figures/` | 기록된 결과로 만든 두 그림과 CSV |
| `latex/fonts/`, `licenses/` | Noto CJK/DejaVu font identity와 원 license |

Prior adapter는 **원래 inputs/prior/ 위치에서** 불러 상대 ROOT를 유지한다. 폴더를 평탄화하거나 saved grid를 새로 생성해 대체하지 않는다. 원 코드와 CCC 자료의 출처·단위·권리 조건도 원 입력 기록을 유지한다.

완전한 source ZIP에는 NotoSansCJKkr-Regular.otf, NotoSansCJKkr-Bold.otf, DejaVuSansMono.ttf 세 font bytes를 포함한다. Git 배포에는 font 바이너리를 제외하고 [font README](latex/fonts/README.md)와 [Noto license](licenses/Noto-OFL.txt), [DejaVu license](licenses/DejaVu-LICENSE.txt)를 남긴다. Bundled fonts가 없으면 LaTeX가 시스템의 `Noto Sans CJK KR`, `DejaVu Sans Mono`를 사용하므로 같은 이름의 폰트를 설치한다.

## 외부 원문 cache와 배포 index

이번 단위의 외부 raw retrieval cache **10개**는 Git/source ZIP에서 제외하고 로컬 evidence에 보존한다. [EXTERNAL_REFERENCE_INDEX.json](EXTERNAL_REFERENCE_INDEX.json)에는 해당 외부 자료의 요청·source URL·retrieval identity와 scope를 기록한다. [SOURCES.json](SOURCES.json) 및 문헌 노트에는 실제 논증에 사용한 원전과 비교 범위가 있다.

외부 cache의 bytes/SHA256은 저장된 MCP/web 응답 envelope를 식별한다. 그 값을 원본 논문 PDF 바이너리의 hash로 읽지 않는다. 배포본에는 외부 초록·본문을 재수록하지 않고 index를 제공한다. 문서 빌드와 위 세 Python check는 이 raw retrieval cache를 읽지 않는다. 원문을 다시 취득한 응답은 retrieval 시점·서비스 표현이 달라질 수 있으므로 기존 response hash와 동일하다고 가정하지 않는다.

## Source snapshot 포장

배포 포장 entry point `package_source.py`의 명령 계약은 두 필수 인자다.

```bash
python3 package_source.py \
  --science-commit "$BASS_CR_SCIENCE_COMMIT" \
  --archive-path "$BASS_CR_ARCHIVE_PATH"
```

`BASS_CR_SCIENCE_COMMIT`에는 실제 science commit SHA를, `BASS_CR_ARCHIVE_PATH`에는 source 작업 디렉터리 밖의 새 ZIP 절대경로를 지정한다. 이 명령은 문서 빌드 및 과학 검사 명령과 구별되는 **source snapshot 포장** 단계다. 실제 포함·제외 및 byte identities는 생성되는 SOURCE_MANIFEST.json과 최종 배포 기록을 따른다.

외부 cache를 제외한 배포 ZIP에서 문서와 reference 계산을 재현하는 작업과, 원 evidence를 보유한 작업본에서 배포 snapshot을 다시 포장하는 작업을 구별한다. 후속 delivery receipt가 기록되어도 이미 만든 ZIP과 해당 snapshot manifest의 원래 identity를 소급해 바꾸지 않는다.

## 다음 연구 노드

[NEXT_DAG.json](NEXT_DAG.json)의 다음 두 이론 단위를 우선한다.

1. **CR_THEORY_MULTI_FAMILY_BRANCH_CONTINUATION:** 둘 이상의 실제 sharing family와 stopping을 연결하고, branch 변경이 thermal electron feedback과 extent를 함께 바꾸는 crossing을 구성한다. 인접 branch의 domain·호환성·선택 규칙과 오차를 함께 확인한다.
2. **CR_THEORY_GEOMETRY_COLLISION_COMPOSITION:** geometry → actual energy 재결속 → collision → cutoff 분류의 순서를 명시하고, 하나의 work/energy 장부 및 local splitting-error budget과 연결한다.

추가 선택 노드는 **CR_THEORY_ANGULAR_MOMENT_REMAP**이다. Count·energy 보존을 유지하면서 massive momentum/stress observable의 양의 remap 조건을 다룬다. 이 후속 범위와 현재 seven scoped claims의 완료 범위를 구별해 재개한다.
