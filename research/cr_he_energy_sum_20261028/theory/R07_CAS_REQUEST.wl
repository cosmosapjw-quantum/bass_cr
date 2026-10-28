ClearAll[n,d,p,i1,i2,a,b,x,lp];
lp[en_List, wt_List, cap_] := Module[{pairs, v, c},
 pairs = Select[Flatten[Table[{ii,jj},{ii,Length[en]},{jj,ii,Length[en]}],1], Total[en[[#]]] <= cap &];
 If[Length[pairs] == 0, Return[0]];
 v = Array[x,Length[pairs]];
 c = Join[Thread[v >= 0], Table[Sum[Count[pairs[[j]],ii] v[[j]],{j,Length[pairs]}] <= wt[[ii]],{ii,Length[en]}]];
 First[Maximize[{Total[v],And@@c},v]]
];
<|
 "FullSupportSpeciesSum" -> Simplify[(-n+d)+(n-2d)+d],
 "FullSupportIonicChargeMinusLegs" -> Simplify[(n-2d)+2d-n],
 "FullSupportChemicalResidual" -> Simplify[i1(n-2d)+(i1+i2)d-(i1 n+(i2-i1)d)],
 "PartialSupportChemicalResidual" -> Simplify[i1(n-p-2d)+(i1+i2)(p+d)-(i1 n+i2 p+(i2-i1)d)],
 "ProperFactor" -> Integrate[x,{x,a,b}],
 "NativeBindingDifference_eV" -> (5442-2459)/100,
 "ExactCutoffGap_eV" -> (2*3602879701896397/2^55-1/5),
 "IndependentSmallLPOptima" -> {lp[{1,2},{1,1},3/2],lp[{1,2},{1,1},3],lp[{0,1,3},{1,2,4},4],lp[{3602879701896397/2^55},{2},1/5],lp[{3602879701896397/2^55},{2},2*3602879701896397/2^55]}
|>
