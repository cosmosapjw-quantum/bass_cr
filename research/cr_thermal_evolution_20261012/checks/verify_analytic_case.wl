Module[
 {t,ts,lam,q0,eps,tt,delta0,vol,rate,theta,tau,q,u,mat,heat,w,b,xbar,x,p,qq,ass,zero,checks,b1,b2,bound},
 ass=t>0&&ts>0&&lam>0&&q0>0&&eps>0&&tt>0&&delta0>0;
 vol=1+t/ts;rate=vol^2;theta=1/(t+ts);
 tau=t+t^2/ts+t^3/(3ts^2);q=q0 vol;u=lam tau;
 mat=lam{{-1,0},{1,-1}};heat=lam eps{1,1};w={2eps,eps};b={1/(2eps),0};
 xbar=q0/(2eps lam){1-Exp[-u],1-(1+u)Exp[-u]};
 x=xbar/vol;p=q0 vol(1-(1+u/2)Exp[-u]);
 qq=q0 tau-q0/(2lam)(3-(3+u)Exp[-u]);
 zero[expr_]:=AllTrue[Flatten[{FullSimplify[expr,Assumptions->ass]}],TrueQ[#==0]&];
 b1={{-1,0},{1,0}};b2={{0,0},{0,-1}};
 bound=delta0 q0(tt^2+2tt^3/(3ts)+tt^4/(6ts^2));
 checks=<|
 "collision_clock_derivative"->zero[D[tau,t]-rate],
 "material_volume_derivative"->zero[D[vol,t]-theta vol],
 "transformed_source_jacobian"->zero[vol q/rate-q0],
 "proper_volume_ode"->zero[D[x,t]-(rate mat-theta IdentityMatrix[2]).x-b q],
 "comoving_ode"->zero[D[xbar,t]-rate mat.xbar-vol b q],
 "physical_heat_output"->zero[p-(rate/vol)heat.xbar],
 "parcel_heat_derivative"->zero[D[qq,t]-vol p],
 "parcel_total_energy"->zero[qq+w.xbar-q0 tau],
 "zero_initial_stock"->zero[xbar/.t->0],
 "zero_initial_heat"->zero[qq/.t->0],
 "reference_energy_balance"->zero[w.mat+heat],
 "source_energy_normalization"->zero[w.b-1],
 "noncommuting_reactions"->zero[b1.b2-b2.b1-{{0,0},{1,0}}],
 "noncommutator_nonzero"->TrueQ[b1.b2!=b2.b1],
 "residual_integral"->zero[2delta0 q0 Integrate[tau,{t,0,tt}]-bound],
 "endpoint_physical_heat"->zero[(p/.{lam->1/ts,t->ts})-2q0(1-(13/6)Exp[-7/3])],
 "endpoint_parcel_heat"->zero[(qq/.{lam->1/ts,t->ts})-q0 ts(5/6+(8/3)Exp[-7/3])],
 "endpoint_input_energy"->zero[(q0 tau/.t->ts)-(7/3)q0 ts],
 "relative_certificate"->zero[(bound/.tt->ts)/((7/3)q0 ts)-(11/14)delta0 ts],
 "source_jacobian_negative_control"->zero[(vol q/.t->ts)-4q0],
 "heat_prefactor_negative_control"->zero[(rate/vol/.t->ts)-2]
 |>;
 ExportString[<|"checks"->checks,"check_count"->Length[checks],"passed_count"->Count[Values[checks],True],"status"->If[And@@Values[checks],"PASS","FAIL"],"heavy_runs"->0|>,"RawJSON"]
]
