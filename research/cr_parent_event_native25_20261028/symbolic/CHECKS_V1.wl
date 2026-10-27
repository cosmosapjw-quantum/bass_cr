Module[{ii,a,b,kk,zz,f0,f1,f2,mn0,mn1,me0,me1,
  jh,nhe,pp,dd,ch,che,ihs,i1s,ih,i1,i2,irh,irhe,
  dua,qc,uc,kh,khe,ugamma,db,l0,rconst,bbranch,
  hvec,hevec,ua,qq,da,nn,cv,t0,np0,nc,zv,checks,flat},
 kk=ii+a;zz=(b-a)/(ii+b);
 f0=zz(1-zz/2);f1=zz^2/2;
 f2=Log[(ii+b)/(ii+a)]-zz-zz^2/2;
 mn0=ii^3/kk^2*f0;
 mn1=ii^2/kk^2*(a*f0+kk*f1);
 me0=ii*mn1;
 me1=ii^2/kk^2*(a^2*f0+2*a*kk*f1+kk^2*f2);
 hvec={-jh+ch,jh-ch};
 hevec={-nhe+dd+che,nhe-pp-2dd-che,pp+dd};
 ugamma=kh+khe+irh*ch+irhe*che;
 db=ih*(jh-ch)+i1*(nhe-che)+i2*pp+(i2-i1)*dd;
 l0=dua+qc+uc+kh+khe+ihs*jh+i1s*nhe;
 rconst=(ihs-ih)*jh+(i1s-i1)*nhe+(ih-irh)*ch+(i1-irhe)*che;
 bbranch=i2*pp+(i2-i1)*dd;
 checks=<|
  "upper_moment_derivatives" -> (Together /@ {
    D[mn0,b]-(1+b/ii)^(-3),
    D[mn1,b]-(b/ii)*(1+b/ii)^(-3),
    D[me0,b]-b*(1+b/ii)^(-3),
    D[me1,b]-b*(b/ii)*(1+b/ii)^(-3)}),
  "lower_moment_derivatives" -> (Together /@ {
    D[mn0,a]+(1+a/ii)^(-3),
    D[mn1,a]+(a/ii)*(1+a/ii)^(-3),
    D[me0,a]+a*(1+a/ii)^(-3),
    D[me1,a]+a*(a/ii)*(1+a/ii)^(-3)}),
  "zero_width_moments" -> (Simplify /@ ({mn0,mn1,me0,me1}/.b->a)),
  "nuclei_baryon_charge" -> (Together /@ {
    Total[hvec],Total[hevec],Total[hvec]+4Total[hevec],
    hvec[[2]]+hevec[[2]]+2hevec[[3]]-(jh+nhe+pp-ch-che)}),
  "energy_sidecar" -> {Together[l0-(dua+qc+uc+ugamma+db)-(rconst-bbranch)]},
  "finite_bin_EOS" -> {Together[(ua+qq)*da/(ua*(da+nn))-1-(qq*da-ua*nn)/(ua*(da+nn))]},
  "prefix_EOS" -> {Together[(np0*t0+qq/cv)/((np0+nc)*t0)-1-(qq/(cv*t0)-nc)/(np0+nc)]},
  "proper_clock" -> (Together /@ {D[(b-a)*(b+a)/2,b]-b,D[(b-a)*(b+a)/2,a]+a}),
  "positive_series_derivative" -> {Together[D[-Log[1-zv]-zv-zv^2/2,zv]-zv^2/(1-zv)]}
 |>;
 flat=Flatten[Values[checks]];
 ExportString[<|"schema"->"CR_PARENT_EVENT_SYMBOLIC_CHECK_V1",
 "checks"->checks,"check_count"->Length[flat],"all_zero"->And@@(TrueQ[#==0]& /@ flat),
 "scope"->"algebraic identities only; ii>0,0<=a<=b,positive EOS denominators; no numeric source, rates, exclusive He branch or physical completion"|>,"RawJSON"]
]
