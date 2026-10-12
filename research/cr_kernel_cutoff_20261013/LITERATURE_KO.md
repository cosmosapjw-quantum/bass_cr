# 실제 kernel 사건 표현과 온도 cutoff의 원전 대조

연구 단위: CR-THEORY-KERNEL-CUTOFF-20261013.  
작성자: /root/feedback_literature_review.  
근거 상태: **네 원전의 지정 절을 읽은 문헌 대조**. 새 후보의 직접 유도와 최종 독립 판정은 별도 기록이다.

## 이번 대조의 결론

비균일 에너지 격자의 수·에너지 보존 재배분, thermal/kinetic 성분 사이의 moment 보존 교환,
thermalization 뒤에 남는 입자의 열에너지 회계는 원전에서 확인했다.
각 논문이 사용하는 collision 모형과 thermalization 기준이 다르므로, 그 결과를 이번
온도 의존 cutoff의 implicit EOS나 실제 daughter kernel의 일반 양수성 증명으로 옮기지 않는다.
새 결과의 보존·양수성·유일성·오차식은 실제 후보의 가정과 유도에서 직접 심사한다.

## L1. Ionization의 세 에너지와 bin moment

Hai P. Le, Jean-Luc Cambier, *Conservative algorithms for non-Maxwellian plasma kinetics*,
Physics of Plasmas **24**, 122105 (2017).
[DOI: 10.1063/1.4998242](https://doi.org/10.1063/1.4998242).
읽은 [저자 원고](https://ar5iv.labs.arxiv.org/html/1711.05946):
§II.1 식 (7)–(8), §II.2, §III.1 식 (16)–(19), §III.3 식 (39)–(55), §V.

균질·등방 전자와 정지한 무거운 원자 모형이다. Ionization source는 입사 전자를 하나 빼고
산란·방출 전자를 각각 더하며, 두 daughter energy의 합과 ionization energy를 초기 energy에
맞춘다. 단일 bin count만 진화시킬 때의 에너지 불일치를 설명하고, bin마다 수와 에너지
moment를 두어 이를 해결한다. §III.3은 differential energy-transfer cross section을 적분하고
각 transfer 구간의 대표 에너지에서 daughter pair를 정한다.

이번에 적용하는 비교는 **실제 daughter 에너지와 수·에너지 moment를 함께 기록하는 구조**다.
저자의 polynomial moment 표현을 비음수 packet 표현과 동일시하지 않는다.
또한 §V의 선형화한 implicit 시간 갱신에서는 보존 오차가 작다는 수치 관측을 보고하므로,
그 문장을 일반적인 exact finite-step 보존 또는 양수성 정리로 사용하지 않는다.

## L2. 인접 수신 셀의 양의 보존 가중치

Stefan Mijin, Abetharan Antony, Fulvio Militello, Robert J. Kingham,
*SOL-KiT—Fully implicit code for kinetic simulation of parallel electron transport in the tokamak Scrape-Off Layer*,
Computer Physics Communications **258**, 107600 (2021); 저자 원고는 2020년 공개.
[DOI: 10.1016/j.cpc.2020.107600](https://doi.org/10.1016/j.cpc.2020.107600).
읽은 [저자 원고](https://ar5iv.labs.arxiv.org/html/2003.00769):
§2.1.3, §3.6.1–§3.6.3 식 (81)–(94), §4.2의 보존 검산 부분.

§3.6은 방출·수신 가중치에 입자수와 에너지의 두 moment 조건을 적용한다.
목표 에너지를 둘러싼 두 수신 셀을 선택하면 가중치의 비음성이 유지되고,
여러 수신 쌍에는 합이 1인 양의 partition을 적용한다. 역과정의 detailed balance에서
수신 격자의 빈 연결이 생길 수 있어 pair 목록을 확장하는 조건도 명시한다.

이것은 이번 양의 moment 보존 재배분과 가까운 선행 구성이다. 다만 §2.1.3의 ionization은
새 전자를 최저 velocity cell에 넣는 단순화다. 따라서 **두 daughter의 일반 differential kernel을
정확히 나타낸 선행 증거로 사용하지 않는다**. 논문의 sheath cutoff 역시 공간 경계의
전자 반사·손실 조건이며 이번 thermal/active 경계와 구분한다.

## L3. Thermalization 기준과 moment를 보존하는 Maxwellian 편입

L. F. Ricketson, M. S. Rosin, R. E. Caflisch, A. M. Dimits,
*An entropy based thermalization scheme for hybrid simulations of Coulomb collisions*,
Journal of Computational Physics **273**, 77–99 (2014).
[DOI: 10.1016/j.jcp.2014.04.059](https://doi.org/10.1016/j.jcp.2014.04.059).
읽은 [저자 보관 출판 PDF](https://www.math.ucla.edu/~caflisch/Pubs/Pubs2013-2014/RicketsonEntropyHybridJCP2014.pdf):
§3 식 (16)–(20), §4 식 (21)–(35), §6의 algorithm steps.

분포를 Maxwellian 성분과 kinetic 성분의 합으로 표현하고 같은 교환 source를 서로 반대 부호로
넣는다. Maxwellian projection은 수·평균속도·온도 moment를 맞춘다. 실제 thermalization 판단은
현재 속도만으로 결정하지 않고 상대엔트로피를 사용하며, 그 값으로 분포의 L1 차를 제한한다.
완전한 projection 오차에서 단순한 판별 조건으로 가는 단계에는 논문이 명시한 작은 particle/bulk
질량비와 근사 논증이 있다. §6은 총 운동량·에너지가 맞도록 bulk의 속도·온도를 갱신한다.

이번 비교는 **열적 편입의 moment 회계와 분포 근사 오차를 구별하는 방식**이다.
이 논문은 균질 단일종 Coulomb collision과 entropy 기준의 결과다.
Sharp $E_c(T)$ 경계의 effective heat capacity, implicit EOS의 유일성 또는 H/He ionization
사건 열에 대한 정리로 사용하지 않는다.

## L4. Thermalized 입자의 남은 에너지

Robert L. Singleton Jr., Lowell S. Brown,
*The energy partitioning of non-thermal particles in a plasma: or the Coulomb logarithm revisited* (2008).
[arXiv:0805.4402](https://arxiv.org/abs/0805.4402),
[관련 DOI: 10.1088/0741-3335/50/12/124016](https://doi.org/10.1088/0741-3335/50/12/124016).
읽은 [저자 원고](https://ar5iv.labs.arxiv.org/html/0805.4402): §I 식 (1)–(4), §III 식 (19)–(26).

단일 배경 온도와 묽은 입사 입자, 균질·등방 source의 Fokker–Planck 모형에서 에너지 분배를
유도한다. Thermalized particle은 배경에 모든 초기 운동에너지를 잃는 것이 아니라 입자당
$3T/2$를 유지한다. 원전의 $T$는 energy 단위다. 따라서 매질에 준 에너지와 최종 입자가
보유한 열에너지를 함께 세면 초기 에너지가 회복된다. Source가 일정해진 구간에서
Maxwellian 누적 성분과 정상 비열적 성분의 에너지 식으로 이를 확인한다.

이 결과는 thermal boundary에서 입자수와 잔여 kinetic energy를 함께 소유해야 한다는
물리적 회계의 근거다. 여기서는 배경 $T$가 주어져 있으므로 **변화하는 $E_c(T)$의
경계 미분이나 열용량·고정점 조건은 이번 후보의 직접 유도로 남는다**.

## 조건의 대응과 독립 심사 범위

| 이번 문제 | 문헌에서 확인한 범위 | 후보에서 직접 확인할 범위 |
|---|---|---|
| 실제 ionization daughter | L1의 세 전자 에너지와 differential transfer 적분 | 현재 kernel convention, 두 daughter의 정규화·threshold·energy ledger |
| 양의 격자 재배분 | L2의 moment 제약과 bracketed 수신 pair | 현재 finite support, 미해상 영역의 처리, 사건별 동시 증분 |
| Thermal/active 교환 | L3의 공통 교환 source와 moment matching | 선언한 sharp/분포 경계의 정확 회계와 실제 closure의 구별 |
| 온도에 따라 움직이는 경계 | L3의 상태 의존 판별과 L4의 thermal energy 소유권 | 경계 미분, implicit EOS, effective heat capacity 및 자기일관 결합의 충분조건 |

SciSpace에 두 개의 자연어 질문을 사용했고, Exa 검색 다섯 번과 본문 조회 두 번으로
필요한 원전을 좁혔다. SciSpace의 cutoff 질문에는 다른 전자·열역학 모형도 다수 나와
본문 대조에서 제외했다. 동일 논문의 repository·journal 중복과 출판연도 차이는 원전
metadata로 구분했다. 검색 결과의 짧은 초록만으로 정리의 조건을 판단하지 않았다.

검색·조회 입력과 원출력은 `inputs/literature/`에 보존했다. 지정 절의 실제 읽은 범위와
URL·DOI·원출력 identity는 `SOURCES.json`에 있다. 이 제한된 비교는 전수조사나 전역 신규성
판정이 아니다. 본 작성자는 새 후보 구성 및 작성자 검산 설계에 참여하지 않았다.
