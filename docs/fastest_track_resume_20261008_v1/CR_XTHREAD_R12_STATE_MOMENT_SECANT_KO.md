# CR-XTHREAD-R12: 서로 다른 가스 상태의 공동 모멘트 source 전달

2026-10-08 KST. 상태: EXACT_TWO_STATE_PHOTO_SOURCE_DECOMPOSITION__TOTAL_RHS_AND_TRUE_ERROR_OPEN.

## 새 결과

R11의 source_transfer.py를 변경하지 않고, HE E5의 서로 다른 H2/H4 가스 상태와 Endpoint Q2/Q4 스펙트럼에 정확 유한차분을 적용했다. 96개 snapshot, 176400개 분광 row, 24개 mode/epoch 사각형을 읽었다. 같은 Q4에서 H2→H4 광온도 RHS 변화는 24점 모두에서 모멘트 변화보다 물질 상태/EOS 계수 변화가 컸다. 15점에서는 두 기여의 부호가 반대였다. 반면 전체 H2Q2→H4Q4 대각 차이는 여전히 reader 항이 지배한다. 순간 photo-only source의 결과이며 실제 종단온도나 전체 열 RHS를 계산한 것은 아니다.

## 정확한 두 상태 식

G=(h,y,z,w), w[erg/H], f=nHe/nH, Xe=h+f(y+2z), D=1+f+Xe다. 두 상태는 같은 proper nH,nHe,H와 물리상수를 사용한다. m=(Gamma3,Ecal3)는 같은 spectral sample의 공동 모멘트이며 각각 /absorber/s와 eV/absorber/s다. Ecal은 입사에너지 모멘트로 excess heat와 다르다. Source는 S(G,m)=A(G)m이고 A는 EOS 분모 때문에 G에 비선형이다.

정확한 차분은

    Delta S = (A_a+A_b)/2 * (m_b-m_a)
              +(A_b-A_a) * (m_a+m_b)/2.

첫 항은 moment 변화, 둘째는 matter-state 변화다. Taylor 항을 버린 선형화가 아니며 Ga=Gb이면 R11으로 환원한다. 상태와 모멘트를 바꾸는 두 순서를 평균한 명시적 대칭 귀속 규칙이다. 혼합점 S(Ga,mb)는 대수적 평가이지 독립적인 물리진화나 유일한 인과기여가 아니다.

온도 source에서 Hphoto=eV_erg*nu·(Ecal-chi*Gamma), Ce=nu·Gamma, nu=(1-h,f(1-y-z),fy)를 유지한다. r=1/D, v=w/D², K=2/(3kB)라 두면

    Tdot_photo=K*(r*Hphoto-v*Ce)
    Delta Tdot=K*(rbar*Delta Hphoto+Hphoto_bar*Delta r
                  -vbar*Delta Ce-Ce_bar*Delta v)
    Delta r=-Delta D/(Da*Db)
    Delta v=(ra²+rb²)/2*Delta w+wbar*(ra+rb)*Delta r.

이것도 정확 유한차분이다. kB=1.380649e-16 erg/K, c=29979245800 cm/s, eV_erg=1.602176634e-12 및 chi=(13.598434599702,24.587389011,54.41776)eV의 원 binary64 값을 유지한다. Fit cutoff를 결합에너지로 바꾸지 않았다. Natural units를 도입하지 않았다.

V_hq=S(G_h,m_hq)에 대해 reader=((V24-V22)+(V44-V42))/2를 정의한다. 나머지 두 history 차이를 위 식으로 각각 나눠 평균하면

    V44-V22=reader+spectral_history+matter_state

가 정확히 성립한다. History 항을 순수 시간절단오차로 재명명하지 않는다.

## 실제 수치

OFF step384의 H2Q2→H4Q4 광온도 RHS 차이[K/s]:

- reader: -4.390249938917027e-19
- spectral_history: -6.351408867066448e-24
- matter_state: +9.112266197913055e-22
- total: -4.381201186807785e-19

같은 Q4의 H2→H4 부분만 보면 moment=-6.350009741356306e-24, state=+9.112266166895360e-22, total=+9.048766069481797e-22 K/s다. 동일-state 기여만 가져오면 이 부분의 부호를 놓친다. 24점의 |state/moment|는 약6.37060~154.79133이다.

OFF384 전체의 Delta Ce=+3.7859163353932825e-22 electron/H/s, Delta Hphoto=+5.766641777279012e-35 erg/H/s지만 Delta Tdot_photo는 음수다. 24개 대각비교 모두 photoheat와 photo Tdot 차이의 부호가 반대다. R11 RAW→ENDCUT와 이번 Endpoint Q2→Q4는 다른 비교이므로 값을 혼합하지 않는다. 소수는 표시값이며 정본은 ZIP의 정확 분자·분모다.

## 수신·source identity

bass_cr 시작 HEAD=a45c8404b341c0595a2c429c8c4be8ad61a3ae89.
HE science=91218a1d496fad1b7231f96488a8df56e4fd532a. E5 held-out 8시각은 유한비교 통과, all-epoch/true-error는 OPEN, 다음 E6다. HE terminal47fc37087a99f36dab4f0bfa65be8285fdd32ca1은 E4 backup receipt만 추가했으며 새 과학 결과가 아니다.
REI=42db9791eceab6988c9700682b7a2cd6edd614db의 BRIDGE10을 수신만 했다. 다음 BRIDGE11은16→32 order/box-floor이며 continuous error는 OPEN이다.
HH Git=649ecb06321d3f7956fc13902666f062dfcde50c. 별도 Library 진행은 재조회하지 않았으므로 Git 무변화를 전체 무진전으로 표현하지 않는다.

HE E5 ZIP10400054bytes,SHA256 d61cda1248a709ecfc3721fd7ef14ba89f6fd49320d346d800088081a1cb56b8에서115개 선택 payload를 부모 manifest size/SHA와 대조했다. E5의 E4 parent45bbdd9...와 R11의 ff7bb067...는 별도 archive다. 같은 Q의 H2/H4는 eta/weight/E/sigma가 bit-identical이고 F만 다르며, 같은 H의 Q2/Q4는 gas와 epoch가 같음을 검사했다.

## 검증과 한계

새18고유시험 PASS, 1 assertion RED→GREEN/17 tests-after다. 동일 moments에 다른 state의 영향을 0으로 버리는 초기 구현은 예상값 -187408/1167615에 실패했고 수정 후 통과했다. 원 baseline과 로그를 보존했다. 정확 3way output 합264개와 EOS secant24개가 성립한다. 새 source5파일과 불변R11 core1파일의 문법검사6개, 최종 산출물426조건도 통과했다.

별도100자리 경로는 hexword를 직접 해석하고 부피밀도 EOS로 모멘트·source·차분2688개를 대조했다. 최대상대차 약4.55e-88, 합성128사례1536항등식과 기호식3개도 확인했다. 이는 같은 작성자의 독립 계산 방식이지 독립 인간/agent 심사나 proof-assistant가 아니다. 물리 정확성 자릿수나 참오차 상계로 쓰지 않는다. Native Gamma와의 유한 산술 차이 최대는4.57609424947e-15이며 native sigma를 그대로 사용했다.

새 native/IVP/root/atomic-provider/characteristic replay/old-suite/다른 repo 변경은0이다. 실제 새 실행은96snapshot 공동합·유한차분·별도검산1회다. 상태가 다르므로 nonphoto CI/RR/DR/냉각/RCT가 취소되지 않지만 이번에는 그 전체 RHS를 평가하지 않았다. True state/moment-error region, R10 one-sided jumps, continuous tau는 null이다. 유한 구적 차이를 이들 전제로 대신하지 않는다.

## 실제 게시·백업

새 core: research/fastest_rejoin_20261008/matter_source_transfer/state_moment.py
Code commit=e2113da8a96148c3b4a604d1419f12646344c125
Blob=a516742b1131e25cd0ac096e6cbea3f80efdb258, bytes4419
SHA256=ddd371ce9debcbbc1f7bf56897ef38657585e77110650e8f48d54c1ce63a2b63
원격 directory blob/size가 시험한 core와 일치한다. R11 원파일은 불변이다.

Full archive=BASS_CR_XTHREAD_R12_20261008_v1.zip
bytes=10331973,159entries/158payload
SHA256=71a08718b421509d7b27d728bcdbebcbba0842f51cbbe89913d31535ca817f77
모든 payload size/SHA와 ZIP CRC, reproduce.py --verify-only exit0을 확인했다. Full96snapshot 분석을 wrapper 검사 목적으로 재실행하지 않았다.

Google Drive upload success 및metadata:id1POVJkXGZy_6tTZZjPIMcPGiuYAx7gRwP,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size10331973 일치.
Dropbox completed:id:BSpOijBcT10AAAAAAD3YMw,size10331973,modified2026-10-08T05:34:55Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_XTHREAD_R12_20261008_v1.zip.

동일 immutable ZIP의 create-only R1 UPLOAD_VERIFIED다. Remote checksum 미노출, 새 원격 전체복원/독립 remote bytehash 미수행이다. Git은 새 core와 요약/반환, fullcode/tests/선택입력/정확결과/실패로그는 ZIP이다. 최종commit/tree는 외부 DELIVERY_RECEIPT에 기록한다.

## 다음 경계

이96snapshot의 두-state photo 분해는 종료한다. 다음은 동일 target의 검증된 joint state/moment 영역 또는 실제 producer의 전체 RHS/one-sided 경계자료다. 같은 분석·E5/REI 과학을 반복하지 않는다. HE E6, REI BRIDGE11, HH owner연구를 독립적으로 유지하며 이 분해를 새 필수 gate로 만들지 않는다.

CR_OFF_FASTEST,precisionatomicPARKED,HH ACTIVE,physicalHOLD,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,capturefalse,globalCR/새ownerACK/observer-tailnull 유지. 새 jointON/생산default 변경/원자승인 재사용은 없다.
