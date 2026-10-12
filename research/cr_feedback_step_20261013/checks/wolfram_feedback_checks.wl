(* CR-THEORY-FEEDBACK-20261013. Exact neutral fixture and residual integrals. *)
theta[x_]:=(1+3x)/(2+2x);
frac[x_]:=(1+x)/2;
ff[x_]:=Together[(1+theta[x])2frac[x]];
psi[x_,eta_]:=eta ff[x]/(1+2eta ff[x]);
q[eta_]:=(5eta/2)/(1+3eta)^2;
eta0=4/17; x0=1/4;
state[x_]:={1-x,1-x,1+x,2x,1+3x};
energy[x_]:={4,0,1,0,1}.state[x];
charge[x_]:={-1,0,1,-1,0}.state[x];
physical[x_]:=ff[x](1-x)^2;
aa=(Exp[ll hh]-1)/ll;
bb=((ll hh-1)Exp[ll hh]+1)/ll^2;
checks=<|
"FP7_rate_reduction"->Together[ff[x]-(3+5x)/2],
"FP7_fixed_point"->Together[psi[x0,eta0]-x0],
"FP7_temperature"->Together[theta[x0]-7/10],
"FP7_charge"->Together[charge[x]],
"FP7_energy"->Together[energy[x]-6],
"FP7_q_at_step"->Together[q[eta0]-170/841],
"FP7_global_q_bound_identity"->Together[5/24-q[eta]-5(3eta-1)^2/(24(1+3eta)^2)],
"FP7_derivative"->Together[D[psi[x,eta],x]-(5eta/2)/(1+eta(3+5x))^2],
"FP7_actual_endpoint_defect"->Together[x0/eta0-physical[x0]+17/128],
"FP7_EOS_derivative"->Together[D[theta[x],x]-1/(1+x)^2],
"FP6_A_integral"->FullSimplify[Integrate[Exp[ll(hh-ss)],{ss,0,hh},Assumptions->ll>0&&hh>0]-aa,Assumptions->ll>0&&hh>0],
"FP6_B_integral"->FullSimplify[Integrate[Exp[ll(hh-ss)](hh-ss),{ss,0,hh},Assumptions->ll>0&&hh>0]-bb,Assumptions->ll>0&&hh>0],
"FP6_A_zero_limit"->FullSimplify[Limit[aa,ll->0]-hh],
"FP6_B_zero_limit"->FullSimplify[Limit[bb,ll->0]-hh^2/2]
|>;
<|"Kernel"->$Version,"Checks"->checks,"AllZero"->And@@(TrueQ[#===0]&/@Values[checks]),"ExactEndpoint"->state[x0],"DimensionlessTemperature"->theta[x0],"ContractionBound"->q[eta0],"PhysicalExtentDefectOverKappa0"->Together[x0/eta0-physical[x0]],"ThermalNuclei"->2,"TotalEnergyOverE0"->energy[x0],"ChargeOvere"->charge[x0]|>
