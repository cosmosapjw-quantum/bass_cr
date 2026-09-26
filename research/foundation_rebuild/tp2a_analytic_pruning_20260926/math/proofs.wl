(* Reproducible symbolic identities. Internal radial scalars are independent. *)
ClearAll[c,s,rho,a,sep,at,bt,ap,bp,tx,ty,tz,px,py,pz,t0,p0,vtx,vty,vtz,vpx,vpy,vpz,k];
xt={rho c,rho s,a}; xp={rho c,rho s,a-sep}; qt={tx,ty,tz}; qp={px,py,pz};
vt={vtx,vty,vtz}; vp={vpx,vpy,vpz}; lt=t0+qt.xt; lp=p0+qp.xp;
gt=at qt+bt lt xt; gp=ap qp+bp lp xp;
reduced=at ap qt.qp+at bp lp qt.xp+bt ap lt xt.qp+bt bp lt lp(rho^2+a(a-sep));
remainder=Last[PolynomialReduce[Expand[gt.gp-reduced],{c^2+s^2-1},{c,s}]];
boost=Expand[reduced+I ap lp vp.gt-I at lt vt.gp+(vt.vp)at ap lt lp];
dot=Expand[-at lt vp.gp-I(vp.vp)at ap lt lp/2];
degree[f_]:=Max[Total[First[#]]& /@ CoefficientRules[Expand[f],{c,s}]];
mm={2 Pi BesselJ[0,k],2 Pi I BesselJ[1,k],Pi(BesselJ[0,k]-BesselJ[2,k]),Pi(BesselJ[0,k]+BesselJ[2,k]),I Pi(3 BesselJ[1,k]-BesselJ[3,k])/2,I Pi(BesselJ[1,k]+BesselJ[3,k])/2};
checks={FullSimplify[D[mm[[1]],k]/I-mm[[2]],k>0],FullSimplify[-D[mm[[1]],{k,2}]-mm[[3]],k>0],FullSimplify[D[mm[[1]],{k,3}]/I^3-mm[[5]],k>0],Simplify[mm[[3]]+mm[[4]]-mm[[1]]],Simplify[mm[[5]]+mm[[6]]-mm[[2]]]};
Print[<|"gradient_identity_residual"->remainder,"degrees"->{degree[at ap lt lp],degree[reduced],degree[boost],degree[dot]},"moment_identity_residuals"->checks|>];
ClearAll[r,th,ph]; rp=Sqrt[r^2+sep^2-2 r sep Cos[th]];
unit={Cos[th],Sin[th]Cos[ph],Sin[th]Sin[ph]};
u={{1/Sqrt[2],I/Sqrt[2],0},{0,0,1},{-1/Sqrt[2],I/Sqrt[2],0}};
reflection={{0,0,-1},{0,1,0},{-1,0,0}};
Print[<|"polar_jacobian_residual"->FullSimplify[r rp/sep D[rp,th]-r^2 Sin[th],r>0&&sep>0&&0<th<Pi],"angle_tangent_norm_squared"->FullSimplify[D[unit,th].D[unit,th]],"unitarity_residual"->FullSimplify[ConjugateTranspose[u].u-IdentityMatrix[3]],"reflection_in_cartesian_basis"->FullSimplify[ConjugateTranspose[u].reflection.u]|>];
