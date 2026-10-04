# F04C: 온도의존 FT03의 4변수 BE 잔차와 해석 미분

## 판정과 scope

SCOPED_TEMPERATURE_COUPLED_RESIDUAL_AND_DERIVATIVES_COMPLETE.

CR_OFF_FASTEST에서 실제 온도의존 FT03 source를 읽고, 세 분율+로그 온도의 4변수 BE 잔차, 해석 Jacobian/Hessian, photon Schur 전달식을 구현·검산했다. 수소 RR kinetic coefficient의 온도 미분이 소스 guard 안에서 부호를 바꾼다는 제한된 결과도 정확 유리수 enclosure로 확인했다. Production Rust 변경·native FT03 실행·root solve·owner box 확장·canonical REI-F04 종결은 하지 않았다.

시작 및 게시 직전 확인한 bass_cr HEAD=da8b174267e27f0a70ee7ff12fb130179c1abfab, tree08622203a1827d787071764cb22c2feb1e68543f. 같은 research/r4q-gap-closure-20261001 branch의 새 문서만 추가한다. 이전 F04A/B, native F03 결과 및 전체 reference campaign은 재실행하지 않았다.

## Source와 owner box intake

고정 receiver snapshot=cosmosapjw-quantum/rei_bianchi@7a15daa38b60a5174315747b9194564dc2d4eb8b, branch forward/rust-reion-kernels-20260922.

- rust/rei_microphysics/src/ft03_controlled.rs blob370fd2fa60521f2dc121ee81c7d24013a3b0d1e5: RHS, event, domain, solver 원문 읽음. Full local bytes는 미보관.
- rust/rei_microphysics/src/ft03_rates.rs blobb8a85ff37de160ecc576a168e4259ed23920a499: 2755 full bytes 보관 및 blob/SHA256 검증. SHA256=1a97cd7a3555deeb4d8700376cd84580c5102127773bc3a235a29c33b0c1542f.
- hhe_events.rs blob57a63eee1e9d8c4aa2b5ed663dbea15619359f71: 실제 EOS·energy 구간 읽음.
- atomic_provider.rs blob62211d8910cd332fffa8f94c6989cae77128916e: reference constructor·Verner cross_section 구간 읽음.
- docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_successor_binding.json blob37af0db4699bdd39c79c0ed6ce8bfb014f5571f3: 전체 읽음.
- 같은 prefix의 runtime_returns/REI-F04.json blob7c0e3f514a16d6fdf435ee27f672e5315b01b58e: claim/blocker/validation/unresolved/sync 읽음.

Model ID=REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1. Proper/static gas, 양의 nH/nHe, 3개의 고정 에너지 광자군, 온도의존 RR/CI와 두 HeII DR 채널, Case-A escape. T guard는30000–110000 K inclusive이며 물리적 rate 정확성 인증 범위가 아니다. F03의 zero-nuclear-density per-capita 극한을 FT03 API에 임의 이식하지 않는다.

Owner는 ACTUAL_PARENT_DOMAIN_NOT_FROZEN 및 augmented_parent_domain=NOT_FROZEN_FOR_ACTUAL_FT03_SUCCESSOR를 명시한다. Uniform parent/source uncertainty, root inclusion, implicit J/H, same-parent full/half remainder, checker/public width는 미완료다. 임의 상자를 만들지 않았고 source temperature guard를 owner joint-parent box로 바꾸지 않았다.

종료 단계 receiver752e360a80e8622bcbaffae54183258b2e67b810를 수신했다. 비교 결과 한 commit, REI-CHAT-FLRW04-20261005 아래 새 문서8개이며 FT03 code/binding 변경은 없다. 이 독립 연구를 재실행하거나 현재 성과에 합산하지 않았다. 이전 actual native F03 bits의 부재 blocker는 폐기된 상태를 유지하며 그 값을 FT03 결과로 재명명하지 않는다.

## 4변수 exact-real reduction

x=(xHII,xHeII,xHeIII), l=(1-xHII,1-xHeII-xHeIII,xHeII), d=(nH,nHe,nHe), ne=nH*xHII+nHe*(xHeII+2*xHeIII), p=nH+nHe+ne. eta=ln(T/Tstar), Tstar=1K.

    U(x,eta)=1.5*kB_EOS*p*Tstar*exp(eta)
    s_ag=c*sigma_ag
    kappa_g=sum_a d_a*l_a*s_ag
    D_g=1+h*kappa_g
    Nbar_g=N_g0/D_g

h>=0と物理分率領域ではD_g>=1。固定sigma、光子再注入なし、static geometryがこの消去の条件である。温度依存RR/CI/DRだけではNbarのeta依存は生じない。

A_a(T)=alpha_RR,a+indicator(a=HeII)*sum_k(delta_DR,k), Gamma_a=sum_g s_ag*Nbar_g と置く。

    j_a=l_a*Gamma_a+ne*(l_a*beta_a-x_a*A_a)
    F=(j0,j1-j2,j2)
    K_a=kB_rate*T*alpha_a*(1.5+g_a)
    g_a=d ln(alpha_a)/d eta
    H_g=ev_erg*sum_a d_a*l_a*s_ag*(E_g-chi_a)
    P=sum_g H_g*Nbar_g
    W=sum_a d_a*(l_a*beta_a*chi_a*ev_erg+x_a*K_a)
      +nHe*xHeII*sum_k delta_k*E_DR,k
    L=ne*W
    Q=P-L
    R(z)=(x-x0-h*F, (U-u0-h*Q)/Ustar), z=(x,eta).

Ustarは固定正のresidual scale。Referenceのstate derivativeではold.uを固定数として用いた。将来initial stateのparent derivativeを取るときscaleの扱いを別途明示する。Native residual_normのmax floorsを微分したものではない。

EOSのkBはgas.kb_erg_k、rate kinetic/DR momentのkBはmodule内部定数であり、defaultで一致するが一般public gas設定でも同一と仮定しない。c,kB,eV-to-ergを保持した。Nはproper cm^-3、Uはerg cm^-3、hは秒。RR kinetic Kはderived controlled coefficientでraw Grackle cooling parityではない。

Escapeはroot zからRRのbinding+kinetic、各DRのbinding+E_DRを積分した補助値として復元する。元solverは7座標とescapeのactual endpoint residualを再評価しており、今回の4変数表現はexact-real等価式である。単純な新production solverや温度固定反復の正当化ではない。

## J/Hと必要なrate微分次数

Nbar_i=-h*N0*kappa_i/D^2, Nbar_ij=2*h^2*N0*kappa_i*kappa_j/D^3。EOSとne feedback、HeIIのj1-j2、CI/RR/DRおよびmoment温度微分を全て含む4x4 Jacobianと4x4x4 Hessianをsrc/thermal_residual.pyに実装した。

g'=dg/deta,g''=d2g/deta2とすると

    alpha_eta=alpha*g
    alpha_etaeta=alpha*(g*g+g')
    K_eta=kB*T*alpha*((1+g)*(1.5+g)+g')
    K_etaeta=kB*T*alpha*((1+g)^2*(1.5+g)+(3.5+3*g)*g'+g'').

したがってthermal residual Hessianにはln(alpha)の3次log-temperature微分が必要である。Sourceが返すg/g'だけでK_etaetaを埋めてはならない。HII/HeIIIのv=(lambda/0.522)^r、a=1.503,b=1.923,r=0.470では

    g=-a+b*r*v/(1+v)
    g'=-b*r^2*v/(1+v)^2
    g''=b*r^3*v*(1-v)/(1+v)^3.

HeII pure power lawはg'とg''が0。CIおよび各DRのlog-slope/2次微分もsourceから解析的に導いた。現時点のコードはstate-z微分までであり、R_parent/R_z,parent/R_parent,parentのAPIは次の作業として残す。

## 正確な符号結果

水素RR kineticのK_eta=kB*T*alpha*Phi、Phi=(1+g)*(1.5+g)+g'を評価した。

|T[K]|Phi表示値|判定|
|---|---:|---|
|30000|+0.09493740758406525315|exact interval lower>0|
|50000|+0.05173459970477654396|高精度diagnosticのみ|
|110000|-0.01585101975280847647|exact interval upper<0|

両端でK>0。連続性によりsource guard内部に少なくとも1つstationary pointがあり、Kはその区間で単調ではない。Root探索は実行0である。この性質は当該RR kinetic coefficientのもので、total cooling非単調性、BEの多重解、solver不安定性、実際の原子冷却の観測事実を意味しない。

証明計算はsource binary64 literalsの正確有理数像からなる実数式を対象にした。lnのatanh級数とexpのTaylor級数について明示したremainderをFraction intervalで伝播させた。Native powf/expのrounding経路を囲ったものではない。Exact JSONはsigned hexadecimal numerator/denominator strings、Fraction(int(num,16),int(den,16))で可逆に読める。

## Schurと温度feedback

Candidateのexact EOS Tを固定してrN=D*Nhat-N0とすれば、温度依存sourceでも光子に関して線形なので

    R_x=r_x+h*M*D^(-1)*rN
    R_E=(r_u+h*H^T*D^(-1)*rN)/Ustar.

F04Bのlinear thermal denominatorをここへ移植しない。Nativeで丸めたTとexact EOSのTの差も別途扱う必要がある。今回はnative FT03 bitsの再観測や結合は実行していない。

Jを[[A,b],[c^T,d]]と分割するとAが可逆な場合の熱結合判定はS=d-c^T*A^(-1)*bであり、dだけでは不十分。Actual rootかつ固定scaleではeta_u0=1/(Ustar*S), x_u0=-A^(-1)*b/(Ustar*S)。F03のx_u0=0を一般FT03へ移植しない。Sのuniform符号やroot可逆性は未認証である。

同じoriginal parent上のimplicit derivativesとhalf compositionの公式を報告書に記載した。Half1 root enclosureとその依存をhalf2のold-stateへ渡し、各半stepのendpoint events/temperatureを保持する。Full候補や最後のendpointで代用しない。Mixed parent derivativesと実際のhalf assemblyの実装・認証は今回未実行。

## 検証、失敗、実行範囲

新focused tests23 PASS、symbolic11条件True、Python syntax PASS。Jacobian48成分・Hessian128成分・rate derivative66値を高精度数値微分と対照した。有限点のimplementation検証でありuniform certificateや65桁保証ではない。実行ログとargv/exitをZIPに保存した。

2試験はassertion RED→GREEN、20試験はtests-after、1試験は実際のserialization exceptionの再現・修正である。最後の1件をassertion TDDと再分類しない。独立human/agent review、proof-assistant検証はない。

初回diagnosticsでは微分結果JSON保存後に、巨大有理数の十進文字列化がPython4300桁制限で失敗した。数学的な符号失敗ではない。元serializerと失敗ログを保存し、lossless signed hexadecimal保存に変更した。Derivative JSONを保持したままserializationを復旧し、最終23試験と構文検査を再実行した。許容誤差・式・proof inequalityの変更はない。

raw GitHub direct networkはDNS失敗、rustcはPATHにない。Sourceはconnectorで読んだ。新native実行0、root solve0、原子積分0、cosmological history0、owner box expansion0、旧27/42suiteやreference campaign再実行0。Arbitrary precision referenceの成功をnative checked_productのunderflow許可に転用しない。

## 正本packageと実際の二重backup

File=BASS_CR_CHAT_F04C_20261005_v1.zip
bytes=2596825
SHA256=bd39f3e8de95d48115a425211580d412f820f751d0ea773ce33f90c1c7419b85
ZIP48 members、47payload SHA256/CRCをlocal検証。

Drive: success ACK、id1Fm8x-NwlyuzaWcypvOFs3b-CyuSSrL_b、parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ。Metadata readbackでname/size2596825/parent確認。
Dropbox: completed、id:BSpOijBcT10AAAAAADyUQg、size2596825、modified2026-10-04T16:37:31Z。
Dropbox path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04C_20261005_v1.zip

同じimmutable archiveをcreate-onlyで両providerに保存した。R1 UPLOAD_VERIFIED(ID/name/size/pathまたはparent)であり、remote checksumは応答に非公開、full restore/独立remote bytehashは未実行。UPLOAD_VERIFIED!=RESTORE_VERIFIED。Gitの本書はsummary/sync、code/tests/詳細証明/exact JSONの正本はZIPである。ZIP内に未来のupload成功を記録していない。

## 次のnodeと保存した制限

次はBASS-CR-CHAT-F04D_ORIGINAL_PARENT_DERIVATIVES_AND_TWO_HALF_ASSEMBLY。Live owner contractを読み、必要なmixed parent derivativesとsame-parent half compositionを実装・検算する。Actual boxが未定義なら形式的導出/実装を進めるが任意boxでuniform certificationを宣言しない。今回のJ/H/sign proof/23tests、以前のnative probeや旧suiteを同じ目的で繰り返さない。Conditional formulaとactual runtime certificationを区別する。

CR_OFF_FASTEST、precision atomic PARKED、G02=UNRESOLVED、production=HOLD、capture=false、all_bound=OPEN、b_grid=NO_GO。CR-F0=WAIT_FOR_ACTUAL_CR_OFF_DISPATCH_BINDING、source/loader/callback観測=null。旧S-only2window上界5.599633283869504e-17と7.49726779045559e-17 ta^-1を相続。CR-on/full-K/R4AQ/318patch/消費済承認は再使用していない。本結果をcanonical REI-F04完了や新mandatory gateにしない。
