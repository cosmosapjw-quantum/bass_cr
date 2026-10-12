$DefInfoQ=False;
DefManifold[M,4,{a,b,c1,d,e,f,i,j}];
DefMetric[-1,g[-a,-b],CD,{";","D"}];
DefTensor[u[a],M];DefTensor[rho[],M];DefTensor[press[],M];
DefTensor[S[a,b],M,Symmetric[{a,b}]];
DefTensor[pi[a,b],M,Symmetric[{a,b}]];
DefTensor[num[],M];
norm=MakeRule[{u[a]u[-a],-1},MetricOn->All,ContractMetrics->True];
dnorm=MakeRule[{u[a]CD[-b][u[-a]],0},MetricOn->All,ContractMetrics->True];
project=MakeRule[{pi[a,b],(g[a,c1]+u[a]u[c1])(g[b,d]+u[b]u[d])S[-c1,-d]-(1/3)(g[a,b]+u[a]u[b])(g[c1,d]+u[c1]u[d])S[-c1,-d]},MetricOn->All,ContractMetrics->True];
simp[expr_]:=FixedPoint[ToCanonical[ContractMetric[Expand[#]]] /.Join[norm,dnorm]&,expr,8];
ortho=simp[(u[-a]pi[a,b])/.project];
trace=simp[(g[-a,-b]pi[a,b])/.project];
energyRaw=-u[-b]CD[-a][rho[]u[a]u[b]+press[](g[a,b]+u[a]u[b])+pi[a,b]];
energyExpected=u[a]CD[-a][rho[]]+(rho[]+press[])CD[-a][u[a]]+pi[a,b]CD[-a][u[-b]];
energyResidual=simp[(energyRaw-energyExpected)/.project];
currentResidual=simp[CD[-a][num[]u[a]]-u[a]CD[-a][num[]]-num[]CD[-a][u[a]]];
<|"Kernel"->System`$Version,"xTensorVersion"->xAct`xTensor`$Version,"xPermVersion"->xAct`xPerm`$Version,"MathLink"->xAct`xPerm`$xpermQ,"PackageSHA256"->(IntegerString[FileHash[#,"SHA256"],16,64]&/@paths),"OrthogonalityResidual"->ToString[ortho,InputForm],"TraceResidual"->ToString[trace,InputForm],"EnergyProjectionResidual"->ToString[energyResidual,InputForm],"NumberCurrentResidual"->ToString[currentResidual,InputForm],"AllZero"->And@@(TrueQ[#===0]&/@{ortho,trace,energyResidual,currentResidual})|>
