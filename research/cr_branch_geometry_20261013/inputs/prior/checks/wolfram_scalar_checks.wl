ClearAll[tt,dd,xx,yy,ww,tbed,nn,alpha,nref,ll0,cv,kap,rho,ec,nuN,nuU,xip,aa0,aa1,bb0,bb1,ee,bind];
nfun[tt_] := 5/2 - Integrate[1/4, {xx, 4 tt, 6}];
ufun[tt_, dd_] := 11/2 + dd - Integrate[xx/4, {xx, 4 tt, 6}];
ff = Expand[3 tt nfun[tt]/2 - ufun[tt,dd]];
phi = ufun[tt,dd]/(3 nfun[tt]/2);
dom = 3/4 <= tt <= 5/4 && -5/32 <= dd <= 3/32;
qp = 824012/100000 - (104769/10000) yy + (396496/100000) yy^2 - (445976/10000000) yy^3;
dphi = Together[D[phi,tt]]; dqp = Expand[D[qp,yy]];
bedY = 1/(1+ww); bedR = 1/(tbed-ww);
lamA = {(aa1-ww)/(aa1-aa0), (ww-aa0)/(aa1-aa0)};
lamB = {(bb1-(ee-bind-ww))/(bb1-bb0), ((ee-bind-ww)-bb0)/(bb1-bb0)};
stop = alpha nn (ll0 - Log[nn/nref]/2);
residuals = <|
 "SmoothNumberMoment" -> Simplify[nfun[tt]-(1+tt)],
 "SmoothEnergyMoment" -> Simplify[ufun[tt,dd]-(1+dd+2tt^2)],
 "SmoothEOSPolynomial" -> Simplify[ff-(3tt/2-tt^2/2-1-dd)],
 "EffectiveCapacitySlope" -> Simplify[D[ff,tt]-(3/2-tt)],
 "PicardDerivative" -> Simplify[D[phi,tt]-(4/3-2(3+dd)/(3(1+tt)^2))],
 "HeatingRootAndMoments" -> Simplify[{ff,nfun[tt]-11/5,ufun[tt,dd]-99/25}/.{tt->6/5,dd->2/25}],
 "CoolingRootAndMoments" -> Simplify[{ff,nfun[tt]-9/5,ufun[tt,dd]-54/25}/.{tt->4/5,dd->-3/25}],
 "ZeroStepIdentity" -> Simplify[ff/.{tt->1,dd->0}],
 "LocalImplicitSlope" -> Simplify[(D[(3-Sqrt[1-8dd])/2,dd]/.dd->0)-2],
 "BEDPositiveDecomposition" -> Together[bedY^2+bedR^2-(bedY+bedR)/(tbed+1)-((bedY-bedR)^2+bedY bedR)],
 "HeliumMinimumValue" -> Simplify[(qp/.yy->1)-1052239/625000],
 "PairProjectionCount" -> Together[Total[lamA]+Total[lamB]-2],
 "PairProjectionEnergy" -> Together[{aa0,aa1}.lamA+{bb0,bb1}.lamB+bind-ee],
 "CoulombFirstDerivative" -> Simplify[D[stop,nn]-alpha(ll0-Log[nn/nref]/2-1/2),Assumptions->nn>0&&nref>0],
 "CoulombSecondDerivative" -> Simplify[D[stop,{nn,2}]+alpha/(2nn),Assumptions->nn>0&&nref>0],
 "CutoffShapeDerivative" -> Expand[cv nn+cv tt kap rho-kap ec rho-(cv nn-kap(ec-cv tt)rho)],
 "EventImplicitResponse" -> Together[(nuU-cv tt nuN)xip/(cv nn-kap(ec-cv tt)rho)*(cv nn-kap(ec-cv tt)rho)+(cv tt nuN-nuU)xip]
|>;
inequalities = <|
 "RootBracketAllParameters" -> Resolve[ForAll[{dd},-5/32<=dd<=3/32, (ff/.tt->3/4)<=0 && (ff/.tt->5/4)>=0],Reals],
 "PositiveCapacityLowerBound" -> Resolve[ForAll[{tt},3/4<=tt<=5/4,3/2-tt>=1/4],Reals],
 "PicardSelfMap" -> Resolve[ForAll[{tt,dd},dom,3/4<=phi<=5/4],Reals],
 "PicardContractionBound" -> Resolve[ForAll[{tt,dd},dom,0<dphi<=233/243],Reals],
 "HeliumMonotonePositive" -> Resolve[ForAll[{yy},0<=yy<=1,dqp<0&&qp>=1052239/625000],Reals]
|>;
<|"Kernel"->$Version,"Residuals"->residuals,"Inequalities"->inequalities,
"ResidualCount"->Length[Flatten[Values[residuals]]],"GroupCount"->Length[residuals]+Length[inequalities],
"AllZero"->And@@(TrueQ[#===0]&/@Flatten[Values[residuals]]),
"AllInequalitiesTrue"->And@@(TrueQ/@Values[inequalities])|>
