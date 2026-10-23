# C21O 중단 복구와 외부 결과 수용 — 2026-10-22 KST

## 이번 재개의 완료 범위

`physmath-research-loop 1.3.0`의 C10(판정·인계)에서 중단 복구와 미확정 보존 상태를 처리했다.
기존 C21O 과학은 45개 독립응력 격자와 6개 비교 실행으로 완료되어 있었다.
이번에는 새 ODE 적분 없이 실제 백업을 복원하고, 원 소스·raw·그림·영수증을 다시 연결했다.
이 기록은 이전 시점의 기록을 덮어써서 당시의 미완료 상태를 지우지 않는다.

| 구분 | 확인한 결과 |
|---|---|
| Science content | `6b6db06e8148e6826a2d5bf7dbc53d362126ca62` 유지 |
| 기존 document head | `f7ca6905729f7d8d36ca0605f7b1dd7ad5595819` 실제 PR96/ref와 일치 |
| 원 REI source | `3b85dedce84d37b3e165da00685a8a984950aafe` 유지 |
| 실행 identity | `c60d734b0ed8cc7d1a147e181da27c282e3f47be90f8b0eb1d65c030faabea0f` 유지 |
| 신규 ODE / benchmark / NCP 실행 | 모두 0 |
| 후처리 재현 | 15개 출력 모두 원 `analysis_v2`와 BYTE_IDENTITY |
| 새로운 코드 | 고정 배송본의 create-only 복원 도구 `restore_c21o.py` |
| 전역 오차 상계 | `null` 유지 |

원 작업 폴더의 일부만 남았고 Git metadata와 최종 배송본이 사라져 있었다.
이는 이 환경의 자동 작업공간 정리 이후 관측한 상태다. 사용자 삭제나 과학 실패로 해석하지 않았다.
남은 부분 파일을 새 실행으로 메우지 않고 원 보존본을 가져왔다.

## 실제 복원과 구현 검증

Library의 main ZIP, document ZIP, final authority JSON을 실제 다운로드했다.
세 파일의 크기와 SHA256은 기존 권위 기록과 정확히 일치했다. Dropbox는 두 ZIP의 ID·크기·revision을
metadata로 재확인했다. Library의 새 다운로드 byte 검증과 Dropbox의 metadata 확인은 서로 다른 수준이다.

`restore_c21o.py`는 정확한 archive SHA256·크기, 내부 manifest, CRC, 가능한 Git blob identity를 확인한 후
새 디렉터리만 생성한다. 원 ZIP은 수정하지 않는다. Main ZIP의 322개 연구 파일에 후속 문서 11개를
반영하면 6개 교체와 5개 추가로 최종 327개 연구 파일이 복원된다. 원 문서 overlay는 과학 source나
raw를 수정하지 않는다. Archive 경로 탈출·symlink·중복 member와 이미 존재하는 목적지를 거부한다.

독립 검토에서 검증한 파일 경로를 다시 여는 사이 bytes가 바뀔 수 있는 작은 source-binding 결함을 찾았다.
검증한 바로 그 bytes를 `io.BytesIO`로 읽도록 고쳤다. 수정한 helper의 복원 결과 327개는 첫 복원과 모두
동일했고, 기존 목적지는 쓰기 전에 거부했다. 새 helper SHA256과 검증은 `RESTORE_HELPER_V2_CHECK.json`에 있다.
이는 배송·복원 코드의 수정이며 물리 solver 변경이 아니다.

복원된 환경에서 6개 실행·물리 module을 순수 import했다. 이어서 원 `analyze.py`를 외부 입력·출력 경로로
실행했다. NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, Python 3.12.14였으며 51개 raw의 case/source/receipt
binding을 검사하면서 후처리했다. 결과는 CSV 2개, NPZ 1개, PNG 5개, PDF 5개, JSON 2개 모두 byte identity다.
명령과 실제 exit 0은 `REANALYSIS_COMMAND.json`, 비교는 `REANALYSIS_BYTE_COMPARISON.json`에 있다.
이 후처리 시간은 solver 성능 benchmark로 사용하지 않는다.

## 물리 결과와 해석의 유지

정규직교 LRS frame에서

\[
\sigma_{ab}=\operatorname{diag}(-s,-s,2s),\qquad
\pi_{X,ab}=\operatorname{diag}(-p_X,-p_X,2p_X)
\]

이므로 full norm은 각각 \(\sqrt6|s|\), \(\sqrt6|p_X|\)이고 \(\Delta p_X=3p_X\)다.
H를 proper-time 단위 s⁻¹로, pressure를 J m⁻³로 쓰면 signed coordinate는
\(S_F=\sqrt6s/H\), \(P_X=\sqrt6(8\pi G/c^2)p_X/H^2\)다.
이는 \(\kappa_E=8\pi G/c^4\), \(H_{\rm geom}=H/c\)와 같다.
\(\Pi_r=|P_\gamma+P_\nu|\), \(\Pi_{\rm tot}=|P_m+P_r|\)이며 norm을 먼저 더하지 않는다.

초기 signed 격자는 \(S_0=\{-0.6,-0.3,0,0.3,0.6\}\),
\(P_{m,0}=\{-5\times10^{-4},0,5\times10^{-4}\}\),
\(P_{r,0}=\{-1.2\times10^{-3},0,1.2\times10^{-3}\}\)다.
이 45개 격자의 원 결과는 다음과 같다. 최대값은 저장된 이 ensemble의 값이다.

| 관측량 | 저장 시간 전체의 최대 | z=2 endpoint 최대 |
|---|---:|---:|
| Σ | 0.6000000000 | 0.0319656558864 |
| Πm | 5.77877595407e-4 | 4.05334097045e-5 |
| Πr | 2.19512829035e-3 | 7.42838273771e-4 |
| Πtot | 2.69854256593e-3 | 7.82659413288e-4 |

그림의 dip은 signed 성분의 영점 통과나 성분 상쇄를 norm으로 표현한 결과다.
서로 반대인 초기 응력이 이후에도 계속 상쇄된다는 뜻은 아니다. 초기 영 shear에서도 이후 shear가 생기는
사례가 있다. 두 cancellation control에서는 z=2 Σ가 약 5.064e-5다.

채택된 핵종은 n, H1, D, T, He3, He4, Li6, Li7이고, 전하 상태는 원자 20개와 자유 neutron을 합해
21 populations다. 전자는 대수적 charge closure다. n과 T의 0은 선언한 초기 inventory이며,
모형에 없는 다른 핵종·반응을 0으로 대신한 것이 아니다. 원자 기체 응력은 등방 closure,
matter anisotropic stress는 별도 비바리온 Vlasov 성분이다. Photon과 neutrino는 별도로 저장한다.

물리는 prescribed UV/T, photoionization + Case-A RR, electron → photon Thomson → LRS 결합이다.
원 C21O에는 DR/CI/CX/분자/전체 핵반응/thermal·UV·stellar feedback이 완성되어 있지 않다.
원 결과의 HeIII 시점과 LiI peak는 그 처방 입력의 응답이다. 관측 재이온화 이력으로 승격하지 않는다.

기존 검증 범위도 유지한다. 51개 저장 궤적의 보존·유한 angular positivity·norm 검사는 PASS_SCOPED였고,
전체 연속계 양성이나 전역 오차 보증은 아니다. BDF/Radau max absolute 1.8418e-9와 local-scale ratio858.47,
L8/L12의 작은 stress 차이와 큰 common-mode 차이 최대2.0780e-4를 함께 남긴다. 이번 복구는 이 과학 검증을
다시 수행하거나 확장한 것이 아니다.

## 새 외부 결과와 최적화의 수용

최신 7개 관련 repo의 advertised heads, 갱신된 PR과 고정 source/contract/manifest/receipt를 조사했다.
정확한 수와 출처·조사 범위는 `EXTERNAL_INTAKE.json`과 `EXTERNAL_INTAKE_KO.md`를 따른다.
Personal Context는 실제 unavailable 오류여서 다른 대화 전체를 조사했다고 표시하지 않는다.
백업 검색도 query·폴더·pagination이 확인된 범위에 한정한다.

핵심 새 결과는 REI PR220 / BASS PR180의 127개 compact 사례와 두 full62 oracle다.
이들의 62→33 축약은 고정 lift P와 restriction R를 통해

\[
RP=I,\qquad f_{33}(v)=R f_{62}(Pv),\qquad J_{33}(v)=R J_{62}(Pv)P
\]

로 구현되어 있다. 반사대칭의 even multipole과 동일 전자율·동일 초기 전하분율을 가진 isotope의
공통 분율을 사용한다. 비영 n/T, isotope-specific rate나 서로 다른 초기 분율, 홀수 multipole이 있으면
현재 축약을 자동 적용할 수 없다. 62→33은 좌표 수의 46.77% 감소이며 dense 행렬 원소 수는
3844→1089다. 이것만으로 wall-time speedup이나 NCP64 scaling을 주장하지 않는다.

대표 high-corner와 cancellation 사례의 compact/full62 raw 네 개를 실제 내려받아 source/result/COMPLETE
SHA binding을 확인했다. NumPy-only 비교로 두 paired saved history를 다시 계산했으며 ODE는 0이다.
Signed 관측량 최대 차이는 각각1.2075369732e-9,1.0450911755e-10;
isotope fraction 차이는2.0900165314e-8,2.9287067020e-8이었다. 고정 수용 한계를 통과했다.
전체127개 raw를 새로 감사한 것으로 표현하지 않는다.

외부 모델은5–200eV UV,100–12000K 처방 T와 RR/DR을 쓰며 허용오차·저장 시점도 C21O와 다르다.
따라서 완료 결과의 출처와 재사용 가능한 축약 방법을 수용하고, C21O51과 같은 ensemble로 합치지 않는다.
최초127개는 마지막 JSON 직렬화 실패 후 재적분된 이력이 원 보고서에 명시돼 있다. 127+2=129는
권위 있는 완료 집합의 수이며 그 외부 작업의 전체 시도 수가129라는 뜻이 아니다.

## 첨부 자료

제공된20개 파일의 SHA/크기,9개 archive header 목록과 필요한 source를 조사했고 개발·감사 지침 전문을
읽었다. 오래된 H-only Peebles/H-He Saha, Rust tilted/kinetic/transport 경로는 역사적 참조로 보존한다.
C21O와 같은 문제·같은 출력을 입증하지 않은 가속 주장을 도입하지 않았다. 요청에 언급됐던
`원시 광핵반응 및 재이온화 네트워크(3).png`는 현재 첨부20개에 없어 직접 확인하지 못했다.
외부 source의 network19 catalog를 원본 이미지의 독립 검증으로 대체하지 않는다.

## 백업·게시와 다음 DAG

원 main ZIP SHA256은 `5741bcac7943e91cdacd8ca15cd8c34ff8a83b7b08b6d8a6bfad31cdb5b2c781`,
28,473,836bytes다. 원 document ZIP은 `a8cf3cd2431332becd39465010e121ebc4ff172feab81a81c9da948883e79b1c`,
40,319bytes다. 두 ZIP은 덮어쓰지 않았다. 이번 복구 묶음과 provider 응답은 별도 archive/authority로 남긴다.

Drive의 exact-name·known-folder 조사에서는 대상이 발견되지 않았다. 이후 원 main ZIP을 한 번 create-only로
다시 요청했지만 ACK가 돌아오지 않아 coordinator가 대기를 중단했다. 실제 도구 대기73.3초를 기록했으며
remote 성공·실패·존재는 UNKNOWN이다. 추가 retry/cancel/delete는 하지 않았다. 문서 ZIP 재요청은 하지 않았다.
이 상태를 triple-backup 완료라고 표시하지 않는다.

외부 PHYS78 검색에서도 Drive 이름 검색은0개였지만 배송 영수증의 정확한 ID를 직접 조회하자
10,562,602-byte 파일이 확인됐다. 검색 결과0개를 부재 증명으로 사용하지 않는 실제 근거다.
PHYS78 source/backup영수증은 별도 lane으로 수용했고 archive byte검증을 새로 수행하지 않았다.

| EXECUTION | PUBLICATION | BACKUP | DAG / 다음 단계 |
|---|---|---|---|
| 원51개 재사용, 신규ODE0, 복원327파일/후처리15출력PASS | 원C/D·PR96확인, recovery delta는 별도 commit/authority에 결속 | 원Library다운로드byte검증,Dropbox metadata,Drive UNKNOWN | C10복구 완료; Drive보존은 OPEN |
| 외부compact 두 saved pair검증, 신규ODE0 | 실제 외부commit별 수용 | query별 백업 metadata 별도 영수증 | 물리·허용오차 차이를 유지하며 다음 연구에 재사용 |

다음 물리 단계는 full thermochemical·radiative energy closure와 실제 rate coverage의 계약이다.
기존 pilot을 더 실행하는 작업이 아니다. 추가 반응을 넣을 때 에너지·전하·핵종 장부, 유효 온도,
전자율 isotope equality와 compact 불변부분공간의 성립을 다시 결정해야 한다. Nuclear high-energy source와
일반 triaxial/tilted/polarized CMB 확장은 기존 HOLD를 유지한다.

NCP에서 기존51개를 다시 돌릴 필요는 없다. 새 물리 입력의 실행에는 당일 affinity/cgroup CPU quota,
memory limit/available RAM, CPU usage, 기존 lease, disk와 inode를 확인한다. CPU55와 coordinator를
예약하고 worker당 numerical thread1, pending task 이하 worker, create-only run directory를 사용한다.
이 sandbox의 실제 quota는8CPU/8GiB였으며 NCP의 live 상태를 여기서 관측한 것은 아니다.

