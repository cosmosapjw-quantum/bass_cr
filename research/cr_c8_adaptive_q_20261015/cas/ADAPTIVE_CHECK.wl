ClearAll["Global`*"];
(* Contract: positive photon counts and genuine child photon first moments *)
mean=(n1*u1+n2*u2)/(n1+n2);
res1=Together[(n1+n2)*mean-n1*u1-n2*u2];
res2=Together[n1*(u1-mean)+n2*(u2-mean)];
res3=Together[n1*(u1-mean)^2+n2*(u2-mean)^2-(n1*n2)/(n1+n2)*(u2-u1)^2];
(* an affine response has zero refinement uncertainty; g=alpha+beta E *)
res4=Together[(n1+n2)*(alpha+beta*mean)-n1*(alpha+beta*u1)-n2*(alpha+beta*u2)];
(* Dyadic exact-global width nesting, if both old and refined intervals enclose the true g *)
lo=Max[oldlo,newlo];hi=Min[oldhi,newhi];
res5=FullSimplify[lo<=exact<=hi, Assumptions->{oldlo<=exact<=oldhi,newlo<=exact<=newhi}];
res6=FullSimplify[hi-lo<=oldhi-oldlo,Assumptions->{oldlo<=exact<=oldhi,newlo<=exact<=newhi}];
res7=FullSimplify[hi-lo<=newhi-newlo,Assumptions->{oldlo<=exact<=oldhi,newlo<=exact<=newhi}];
checks=<|"child_energy"->res1,"child_mean_zero"->res2,"two_atom_variance"->res3,"affine_invariance"->res4,"intersection_contains_truth"->res5,"width_not_greater_old"->res6,"width_not_greater_new"->res7|>;
Print[ExportString[<|"kernel"->$Version,"checks"->checks,"all_pass"->(And@@(TrueQ[#===0]&/@{res1,res2,res3,res4})&&res5&&res6&&res7)|>,"RawJSON"]];
