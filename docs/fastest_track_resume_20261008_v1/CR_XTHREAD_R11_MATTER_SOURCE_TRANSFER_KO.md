# CR-XTHREAD-R11: 같은 spectral parent의 공동 반응률·에너지 전달

2026-10-08 KST.
Status: SAME_PARENT_PHOTO_MATTER_SOURCE_TRANSFER_CHECKED__CONTINUOUS_JETS_OPEN.

## 결과와 범위

HE RCT03E4의 H4 snapshot55개, spectral sample108008개, mode/epoch11개를 읽어 Gamma와 입사에너지 모멘트를 함께 합산했다. 같은 가스 상태에서 전자생성, 결합에너지, 광가열, 온도 변화율과 optical source의 차이를 계산했다. 비교는44개다. RAW4→ENDCUT4의11점 중9점에서 가열률 차이와 온도 변화율 차이의 부호가 반대였다. 전자 증가에 따른 입자수 희석을 포함해야 하며 Gamma만으로 열오차를 제한할 수 없다.

순간 RHS 차이를 실제 가스 이력 변화로 해석하지 않는다. 새 native, IVP, root, 원자 provider, characteristic replay, 과거 suite와 다른 저장소 변경은 모두0이다. R10의 실제 시간 jump, node error, regular fourth derivative와 연속 tau는 계속 null이다.

## 입력과 다른 owner의 진척

bass_cr 시작 및 코드 게시 직전 HEAD: 054023a9b7651fda4a560224909425f7aff9690b.
branch: research/r4q-gap-closure-20261001.
HE: aedcc8134bc7aebb6ee1ffc6affd891c745b9d9f, E4 core70aaed422c695eb9b9089ccd1f20e676b1f89e16. E4의33개 선택 rate 비교와 전체 epoch gate OPEN을 구분한다. 다음 E5는 원 담당에 남긴다.
REI: 8a46b8ab8790857e49d1954e67c991a641b0cdf7, BRIDGE09. 매개변수 포함 macro 비교와 참 연속 오차는 별도이며 다음 BRIDGE10을 대신 실행하지 않았다.
HH Git: 649ecb06321d3f7956fc13902666f062dfcde50c. 별도 Library 진척을 직접 다시 읽지 않았으므로 Git 무변화를 전체 무진전으로 판단하지 않는다.

HE E4 archive는10353822bytes, SHA256ff7bb06718e98d2c060faccc7a87253c2deb3648a9141c9c99a15d3bbcd918b2다. 필요한121payload를 원 bytes로 복사하고 해당 부모 manifest의 size/hash를 확인했다. H4 snapshot CSV/metadata55쌍, gas history3개, 과학 원문4개, 기타4개다. R9의 BASS/SYNC03 상수는 별도 member/hash로 보존했다. 기존 전체 과학 검사를 재실행하지 않았다.

E4의 선택 rate 허용량1e-22/s+1e-6relative와 remoteE3의2.5e-23/s+1e-6relative를 섞지 않았다. 이번 물질 source에 새 허용량이나 정확성 PASS를 부여하지 않았다.

## 같은 상태의 직접 유도

Gas rest frame, proper time seconds, signature(-,+,+,+)를 사용한다. h=xHII,y=xHeII,z=xHeIII,w=erg/H,f=nHe/nH다. f는 공급된 두 binary64 밀도의 정확 비이며 exact3/38로 바꾸지 않는다.

    Xe=h+f*(y+2z), D=1+f+Xe, T=2w/(3*kB*D)
    nu=(1-h,f*(1-y-z),f*y)
    Gamma_a=c*nH*sum weight*density*sigma_a
    Ecal_a=c*nH*sum weight*density*sigma_a*E
    C_e=nu dot Gamma
    absorbed=epsilon_eV*nu dot Ecal
    binding=epsilon_eV*sum nu*chi*Gamma
    heat=absorbed-binding
    Tdot_photo=2/(3*kB*D)*(heat-w*C_e/D).

Gamma는 absorber당s^-1, Ecal은 absorber당eV/s, heat는erg/H/s다. Ecal은 입사에너지이지 초과가열이 아니다. c,kB,eV환산은 원 source를 유지한다. 분율 source의 전자 조합은 C_e와 같고 absorbed=binding+heat도 정확히 닫힌다. 추가dt/4pi/dE/a^-3를 적용하지 않는다. 같은 상태에서만 nonphoto source가 차분상 소거된다.

동일 state에서 이 전달은 Gamma3개와 Ecal3개에 선형이다. 조건부 moment 오차 box의 중앙과 반경을 m,r라 하면 source의 구간은 Lm±abs(L)r이다. 실제 참오차 전제를 이 계산이 증명하는 것은 아니다. Gamma가 같더라도 Ecal이 다르면 전자 source는 같고 heat는 다를 수 있다. 따라서 공동 error box가 없으면 MissingPremise로 거절한다.

## 실제 수치

OFF RAW4→ENDCUT4의 표시값이다. 정확 분자·분모는 ZIP의 results/final에 있다.

|step|전자 source 차이[/H/s]|가열 차이[erg/H/s]|가열에 의한 온도 항[K/s]|입자수 온도 항[K/s]|전체 온도 RHS 차이[K/s]|
|---|---:|---:|---:|---:|---:|
|4|-1.3368121360e-22|-2.0013191166e-35|-7.2932897002e-20|+2.0181214728e-19|+1.2887925028e-19|
|5|-5.8242134763e-22|-3.4100018617e-35|-1.2426834629e-19|+8.7931899539e-19|+7.5505064909e-19|
|52|-1.4422532298e-22|-2.0663474789e-35|-7.5285141602e-20|+2.1983162697e-19|+1.4454648537e-19|

Step5의 w/(epsilon_eV*D)는 약0.2585787749eV이고 signed 비 deltaheat/(epsilon_eV*deltaelectron)는 약0.03654323052eV다. 입자수 희석의 감소가 가열 감소보다 커 온도 RHS는 증가한다. 이 signed 비를 양의 사건분포의 물리적 평균에너지로 부르지 않는다. 실제 가스 시간해나 native 내부 Tdot를 관측한 결과도 아니다.

ENDCUT4→국소세분화4의11점 최대 절대차는 electron4.0019377008e-27/H/s,heat6.3594191928e-40erg/H/s,Tdot3.7249547293e-24K/s다. 이 유한차를 참오차 상계나 연속해 인증에 사용하지 않는다.

## Optical residual과 시간 jump의 구분

C_T=cSI*sigmaT*1e6, q=C_T*nH*Xe/H라 쓰면 photo의 q_ell RHS 기여는 C_T*nH*C_e/H²다. OFF step5의 읽기 변화는 약-1.502802924745e-6이다. 이는 무차원 ln(a) 도함수 성분으로 proper-time 전자율과 단위가 다르다. 저장된 가스 보간의 실제 기울기가 아니다.

같은 재구성에서 r=hatY'-F의 변화는 source 변화의 반대 부호다. 실제 one-sided 동일target 상태가 주어지면 이 전달을 활용할 수 있지만, 같은 시각의 RAW/ENDCUT 구적 차이는 좌우 시간극한이 아니다. 이를 R10 jump로 바꾸는 호출은 거절한다. R10 atlas와 기존 optical 값은 불변이다.

## 실행·검증

새22unit,26산출물 조건,Python5파일 문법 검사가 통과했다. 1개 assertion RED→GREEN과21개 tests-after를 구분했다. 불완전한 heat-only 코드와 의도적 실패 로그를 보존했다. 모든55점의 charge/energy/temperature 항등식과44개 비교의 선형·종별 합산이 정확히 일치했다.

동일 입력의 native metadata Gamma/heat 상대차 최대는3.3686712359e-15/3.1428724517e-15다. Native sigma를 입력으로 사용하므로 독립 원자 fit 인증은 아니다. 별도 mpmath80 계산에서1155개 snapshot 양과484개 차분 양을 대조했고 최대 상대차는 약3.365e-63이다. 64개 exact joint box의4096corner와 symbolic2식도 확인했다. 작업 정밀도는 물리적 정확성 자릿수가 아니다. 독립 인간·에이전트 심사와 proof-assistant 검증은 수행하지 않았다.

표준 Python의 유리수 합산·source 투영과 별도 검산을 실제 실행했다. Rust 첨부 스크립트는 읽었으나 실행하지 않았다. 원 native/IVP/root/provider/characteristic/과거 과학 suite 실행과 다른 저장소 변경은0이다. 최종 결과는 검산한 analysis01과 바이트 단위로 동일하며, 코드 hash와 명령/종료값은 VERIFICATION.json에 있다.

## 코드·정본·백업

Core commit:919cb21d32bb837e5257518ba66608dd98ea08ba.
Path:research/fastest_rejoin_20261008/matter_source_transfer/source_transfer.py.
시험한 bytes와 원격 metadata의 blob705a628337a8b9ec737219d8deb8a56e2c9bb693,size7306이 일치한다.
Core SHA256:1ce2e7e18425191be95722c4f4eee72a5b0cd43e6c3832e0497bba728ee28459.

Archive:BASS_CR_XTHREAD_R11_20261008_v1.zip.
Size:7943856bytes,160entries/159payload.
SHA256:01a80bd61baed21767a523ab167a51c33300e16fe4fb87aefb35f5dc97e674f8.
Local CRC/manifest와 reproduce.py --verify-only exit0을 확인했다. 전체 code/tests/input/REPORT/정확JSON/logs는 ZIP에 있다.

Drive 성공 응답과 metadata:id16k7OOBOle68Kl5bj16dorWY2vQ7tPXII,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size7943856일치.
Dropbox completed:id:BSpOijBcT10AAAAAAD3Xag,size7943856,modified2026-10-08T04:49:34Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_XTHREAD_R11_20261008_v1.zip.
동일 immutable ZIP의 create-only 이중백업이며 R1 UPLOAD_VERIFIED다. Remote checksum은 응답에 없고 새 ZIP의 전체 원격복원·독립 원격 bytehash는 수행하지 않았다. 실제 최종 commit/tree는 별도 DELIVERY_RECEIPT에 기록한다. 앞 요약의 문체 교정은 code/input/science/ZIP 변경이 아니다.

## 다음 경계

이55snapshot의 순간 source 투영은 종료했다. 다음은 같은 target의 검증된 공동 Gamma/Ecal 오차 또는 실제 one-sided rate/state다. R10의 amplitude/nodeerror/thermalregularity/M4는 계속 null이다. HE E5,REI BRIDGE10,HH의 원 담당을 유지하며 새 jointON을 실행하지 않는다.
CR_OFF_FASTEST,precisionatomicPARKED,HH연구ACTIVE,canonicalS0OFFcontrol,physicalHOLD,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,capturefalse를 유지한다. R11 ownerACK/globalCRcounter/observer_tail은 null이다.
