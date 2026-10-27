
k0={{3,-1},{-2,4}}; lam={1/10,1/5}; dd=DiagonalMatrix[lam]; k1=k0+dd;
g0=Inverse[k0]; g1=Inverse[k1]; p=g1.lam; w=g0.lam; eta=Max[w];
bmat=Transpose[{{1/2,1/2},{1/2,1/2},{3/5,7/10},{2/5,3/10}}];
xx=g1.bmat; t0=g0.{1,1}; t1=g1.{1,1};
hh=g0.{3/5,7/10}+{1/1000,-1/2000}; rr={3/5,7/10}-k0.hh;
ds=-g1.dd.hh; dstar=-g1.dd.g0.{3/5,7/10};
nu={1,-1}; q={1,2}; aa={4,4};
checks=<|
"new_probability"->(p=={31/551,41/551}),
"w"->(w=={3/50,2/25}),
"lower_bound"->And@@Thread[w/(1+eta)<=p],
"upper_bound"->And@@Thread[p<=w],
"partition"->(xx.ConstantArray[1,4]+p=={1,1}),
"new_H1"->(xx[[All,3]]=={161/551,337/1102}),
"new_HeI"->(xx[[All,4]]=={99/551,173/1102}),
"time"->(t1=={260/551,255/551}),
"time_response"->(t1-t0==-p/2),
"resolvent"->(g0-g1==g0.dd.g1),
"stored_residual_identity"->(g1.{3/5,7/10}-hh==g1.rr+ds),
"stored_response_error"->(ds-dstar==g1.dd.g0.rr),
"nuclear_count"->(Total[nu]==0),
"baryon_count"->(aa.nu==0),
"thermal_electron"->(q.nu-(-1)==0),
"thermal_particle"->(({2,3}.nu)-(-1)==0),
"signed_energy"->(Simplify[-a e-a ion+a(e+ion)]==0),
"event_statistics"->(2*1/2==1),
"count_cm3_to_m3"->(10^6*2/(3*10^6)==2/3)
|>;
ExportString[<|"case"->"EXACT_RATIONAL_TWO_STATE_AND_EVENT_ALGEBRA",
"p_new"->(ToString[#,InputForm]&/@p),"t_new"->(ToString[#,InputForm]&/@t1),
"checks"->checks,"check_count"->Length[checks],"all_pass"->And@@Values[checks]|>,"RawJSON"]

