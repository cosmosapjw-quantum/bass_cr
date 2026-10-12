(* CR-THEORY-FEEDBACK-20261013. Prescribed diagonal Bianchi I geometry. *)
pp={pOne/aOne[tt],pTwo/aTwo[tt],pThree/aThree[tt]};
scale={aOne[tt],aTwo[tt],aThree[tt]};
hubble=D[scale,tt]/scale;
relenergy=Sqrt[me^2 cc^4+cc^2(pp.pp)];
kinetic=relenergy-me cc^2;
velocity=cc^2 pp/relenergy;
volume=Times@@scale;
thermal=uZero(volume/vZero)^(-2/3);
assump=me>0&&cc>0&&aOne[tt]>0&&aTwo[tt]>0&&aThree[tt]>0&&vZero>0&&uZero>0;
theta=hOne+hTwo+hThree; pm=(pXX+pYY+pZZ)/3;
checks=<|
"CG5_covariant_momentum"->Simplify[pp scale-{pOne,pTwo,pThree}],
"CG6_relativistic_kinetic_work"->FullSimplify[D[kinetic,tt]+hubble.(pp velocity),Assumptions->assump],
"CG8_thermal_pressure_work"->FullSimplify[D[thermal,tt]+(2/3)Total[hubble]thermal,Assumptions->assump],
"CG7_diagonal_stress_split"->Expand[hOne pXX+hTwo pYY+hThree pZZ-pm theta-({hOne,hTwo,hThree}-theta/3).({pXX,pYY,pZZ}-pm)],
"CG9_total_work_ledger"->Expand[(uActivePlus+uThermalPlus)+(workOld+uActiveBefore+uThermalBefore-uActivePlus-uThermalPlus)-(uActiveBefore+uThermalBefore+workOld)]
|>;
<|"Kernel"->$Version,"Checks"->checks,"AllZero"->And@@(TrueQ[#===0]&/@Flatten[Values[checks]]),"Conventions"->{"metric (-+++)","proper time tt in seconds","cc and me explicit","isotropic monatomic thermal closure","prescribed positive diagonal scale factors"}|>
