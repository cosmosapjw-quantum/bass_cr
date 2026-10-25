ClearAll["Global`*"];
a = kf-kr; b = kf (d0+hp)+kr (dp+h0); c = kf d0 hp-kr dp h0;
f[x_] = kf (d0-x) (hp-x)-kr (dp+x) (h0+x);
flow[t_] = 2 cc (1-Exp[-s t])/((bb+s)-(bb-s) Exp[-s t]);
odeResidual = Factor[(D[flow[t],t]-(aa flow[t]^2-bb flow[t]+cc)) /. cc -> (bb^2-s^2)/(4aa)];
matrixInvariants = {{1,1,0,0},{0,0,1,1},{0,1,0,1},{1,1,1,1}} . {-1,1,1,-1};
energyResidual = FullSimplify[chi x+ (3/2) kb nt (-2 chi x/(3 kb nt))];
rates[T_] := {2*10^-10 T^(402/1000) Exp[-(371/10)/T]-(331/100)*10^-17 T^(148/100), (206/100)*10^-10 T^(396/1000) Exp[-33/T]+(203/100)*10^-9 T^(-332/1000)};
grid = {27/10,10,43,100,300,1000,10000,11000,30000,200000};
<|"stoichiometryInvariants"->matrixInvariants,"extentPolynomialIdentity"->Expand[f[x]-(a x^2-b x+c)],"flowODEResidual"->odeResidual,"flowInitialValue"->FullSimplify[flow[0]],"thermalEnergyResidual"->energyResidual,"rateDiagnostic"->Table[With[{r=rates[T]}, {T,N[r,16],N[r[[1]]/r[[2]],16],N[Exp[-43/T],16]}],{T,grid}]|>
