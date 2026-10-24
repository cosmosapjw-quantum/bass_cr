ClearAll["Global`*"];
gd=gh-gl; kd=kh-d*gh+(ch+d)*gl-al; ad=ah-al;
<|"photoMomentEnergyResidual"->Expand[(ch+d)*gd+kd-ad]/.ah->ch*gh+kh,
"PI"->Simplify[-eg+cd+(eg-cd)],"RR"->Simplify[-cd-ek+(cd+ek)],
"CX"->Simplify[(cd-ch)-(cd-ch)],
"cyclePotentialResidual"->Simplify[ch+(cd-ch)-cd],
"hybridEqualThresholdResidual"->Simplify[ch+delta-ch],
"Dshift_eV"->N[43*(1380649/10^29)/(1602176634/10^28),17]|>
