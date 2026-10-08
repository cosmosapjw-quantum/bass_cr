# CR-XTHREAD-R11: 같은 spectral parent의 공동 반응률·에너지 source 전달

2026-10-08 KST. Status=SAME_PARENT_PHOTO_MATTER_SOURCE_TRANSFER_CHECKED__CONTINUOUS_JETS_OPEN.

## 새 결과와 범위

HE E4의 H4 spectral parent55개/108008sample,11mode-epoch에서 Gamma와 입사에너지 모멘트를 함께 합산하여 같은 가스 상태의 electron/binding/heat/temperature/optical source 차이로 전달했다. 비교는44개다. RAW4→ENDCUT4의11점 중9점에서 photoheat 차이와 temperature RHS 차이의 부호가 다르다. 전자 생성에 따른 입자수 희석 항을 보존해야 하며, Gamma-only 정확성으로 열오차를 승인할 수 없다.

이것은 진단 readout의 순간 RHS 차이이며 원 trajectory의 변화가 아니다. Native 원자 provider, characteristic replay, 새 IVP/root/history와 옛 suite는0이다. R10 temporal jump/nodeerror/regularM4 및 continuous tau는 여전히null이다. RAW/ENDCUT rule 차이를 시간 one-sided trace로 바꾸지 않았다.

## 고정 source

bass_cr intake와 게시직전 parent=054023a9b7651fda4a560224909425f7aff9690b, branch research/r4q-gap-closure-20261001.
HE=aedcc8134bc7aebb6ee1ffc6affd891c745b9d9f, E4 core70aaed422c695eb9b9089ccd1f20e676b1f89e16. E4의33선택rate 비교와 전체epoch OPEN을 구분한다. 다음E5는owner에남긴다.
REI=8a46b8ab8790857e49d1954e67c991a641b0cdf7, BRIDGE09. Event-mesh macro비교와 참연속오차를 구분하며 다음BRIDGE10을 반복하지 않았다.
HH Git=649ecb06321d3f7956fc13902666f062dfcde50c. Library진척을 직접 다시읽지는 않았으므로 Git무변화를 전체무진전으로 해석하지 않는다.

HE E4 archive10353822bytes,SHA256ff7bb06718e98d2c060faccc7a87253c2deb3648a9141c9c99a15d3bbcd918b2. 선택121payload를원bytes로보존하고부모manifest의size/hash와일치시켰다. H4snapshot55CSV+metadata55,gasO4history3,원scientificsource4,기타4다. R9의BASS/SYNC03 constants는별도member/hash로계승했다. 모든ancestor원문·science를재실행한것은아니다.

## 직접 유도와 구현

Gas restframe,proper time seconds,signature(-,+,+,+). h=xHII,y=xHeII,z=xHeIII,w=erg/H,f=nHe/nH의정확binary64비를유지한다. exact3/38로소급치환하지않는다.

    Xe=h+f*(y+2z), D=1+f+Xe, T=2w/(3*kB*D)
    nu=(1-h,f*(1-y-z),f*y)
    Gamma_a=c*nH*sum weight*density*sigma_a                  [/absorber/s]
    Ecal_a=c*nH*sum weight*density*sigma_a*E                  [eV/absorber/s]
    C_e=nu dot Gamma
    A=epsilon_eV*nu dot Ecal
    B=epsilon_eV*sum nu*chi*Gamma
    Qheat=A-B                                                [erg/H/s]
    Tdot_photo=2/(3*kB*D)*(Qheat-w*C_e/D).

Ecal은incidentenergy이며heat가아니다. 같은state에서moment→source는선형이고,차분의projection은projection의차분과정확히같다. 분율RHS=(1-h)GammaH,(1-y-z)GammaY-yGammaZ,yGammaZ의전자조합은C_e와일치한다. Absorber0에서나눗셈은없다. Source/birth/redshift/dt/4pi/dE를추가하지않고nonphoto는같은state에서만소거한다.

C_T=cSI*sigmaT_SI*1e6를같은BASS값으로정의하면photo의q_ell작용은C_T*nH/H²*C_e다. 이는저장affine가스경로의실제기울기가아니고원모형RHS에대한작용이다. 재구성r=hatY'-F를고정했을때residual변화는-source차이다.

Joint Gamma3/Ecal3 interval error를주면abs(L)*radius로source구간을계산한다. Gamma만같고Ecal이다른양의스펙트럼은같은electron source와다른heat를준다. Trueerror전제가없으면MissingPremise다. 같은시각두구적을temporal jump로바꾸는호출도거절한다. 실제수치차를참오차box로채우지않는다.

## 실제 OFF RAW4→ENDCUT4

소수는표시용이며정확분자/분모가ZIP의results/final정본이다.

|step|delta electron[/H/s]|deltaheat[erg/H/s]|deltaTdot_heat[K/s]|deltaTdot_particles[K/s]|deltaTdot_total[K/s]|
|---|---:|---:|---:|---:|---:|
|4|-1.3368121360e-22|-2.0013191166e-35|-7.2932897002e-20|+2.0181214728e-19|+1.2887925028e-19|
|5|-5.8242134763e-22|-3.4100018617e-35|-1.2426834629e-19|+8.7931899539e-19|+7.5505064909e-19|
|52|-1.4422532298e-22|-2.0663474789e-35|-7.5285141602e-20|+2.1983162697e-19|+1.4454648537e-19|

Step5のw/(epsilon_eV*D)=.2585787749eVとsignedratio deltaheat/(epsilon_eV*deltaelectron)=.03654323052eVの関係から、粒子数希釈減少がheat減少を上回る。このratioは物理的event平均エネルギーではない。Native Tdotは記録されておらず、ここでのTdotはexact-inputEOSから新しく計算したものだ。最終ガス温度やphysicalfeedbackが変わったと主張しない。

ENDCUT4→localrefine4のmaxabsはelectron4.0019377008e-27/H/s,heat6.3594191928e-40erg/H/s,Tdot3.7249547293e-24K/sだ。新materialaccuracy許容値を定めたり、sourceerrorの上界としてこの差を使ったりしない。E4とremoteE3の異なる既存rate許容値も混同しない。

## 検証と実行

新22unit,26artifactconditions,Python5file構文PASS。1assertionRED→GREEN/21tests-after。初期heat-only実装と失敗logを保管した。追加sciencefailureなし。全55点のcharge/energy/temperature分解、44比較のsame-state線形性とspecies合がexactly一致する。

Native metadataのGamma/heatとの同じinput算術差maxrelativeは3.3686712359e-15/3.1428724517e-15。Native sigma sampleを使用するので独立atomicfit認証ではない。Mpmath80の別経路で1155snapshot量と484paired量を確認し、maxrelative約3.365e-63。64exactjointboxes/4096cornersとsymbolic2identityもPASS。高精度の桁数は物理精度ではなく、独立human/agentreviewやproofassistantは未実施。

Actualnewnative/IVP/root/provider/characteristic/oldscience/otherrepomutations=0。標準Pythonjointsum/sourceprojectionと別経路検査を実行した。Rust添付scriptは読んだが実行していない。計算結果analysis01→finalはbyteidenticalでscienceを重複実行していない。Finaltestsはtestentry配置修正後に再実行。source hashesとargv/exitはVERIFICATION.jsonに固定した。

## コードと実際の二重バックアップ

Core code commit919cb21d32bb837e5257518ba66608dd98ea08ba:
research/fastest_rejoin_20261008/matter_source_transfer/source_transfer.py
Remote metadata blob705a628337a8b9ec737219d8deb8a56e2c9bb693,size7306は試験bytesと同じ。
SHA2561ce2e7e18425191be95722c4f4eee72a5b0cd43e6c3832e0497bba728ee28459。

Archive BASS_CR_XTHREAD_R11_20261008_v1.zip,7943856bytes,160entries/159payload.
SHA25601a80bd61baed21767a523ab167a51c33300e16fe4fb87aefb35f5dc97e674f8。
LocalCRC/manifest検査とreproduce.py --verify-only exit0。Fullsource/tests/input/REPORT/exactJSON/logsはZIP。Gitにはcoreとsummary/returnを追加した。

Drive success+metadata:id16k7OOBOle68Kl5bj16dorWY2vQ7tPXII,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size7943856一致。
Dropbox completed:id:BSpOijBcT10AAAAAAD3Xag,size7943856,modified2026-10-08T04:49:34Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_XTHREAD_R11_20261008_v1.zip。
同じimmutableZIPをcreate-onlyで保存したR1UPLOAD_VERIFIED。Remotechecksumは未露出、新ZIP全restore/独立remotebytehashは未実施。科学検証とは区別する。最終commit/treeはdetachedDELIVERY_RECEIPTに保存する。

## 次の入力と保護範囲

この55snapshotのprojectionは終了。次は同じtargetのjointGamma/Ecal真誤差またはactualone-sidedstate/ratejetsを受け取る。R10のamplitude/nodeerror/thermalregularity/M4はnullであり、raw/cut差で埋めない。HEE5,REIBRIDGE10,HHownerを別に維持し、新jointONを実行しない。
CR_OFF_FASTEST,precisionatomicPARKED,HH研究ACTIVE,canonicalS0OFFcontrol,physicalHOLD,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,capturefalse。R11ownerACK/globalCRcounter/observer_tail=null。
