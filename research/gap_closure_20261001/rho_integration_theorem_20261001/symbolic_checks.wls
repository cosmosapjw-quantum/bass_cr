ClearAll[t,h1,h2,r,s,lam];
ass=Element[{t,h1,h2,r,s,lam},Reals]&&r!=0;
simp[x_]:=FullSimplify[x,Assumptions->ass];
dag[x_]:=simp[ConjugateTranspose[x]];
zero[x_]:=TrueQ[simp[x]==ConstantArray[0,Dimensions[x]]];
b={{1,t},{0,1}}; sd=dag[b].b; dd=dag[b].D[b,t];
hh=dag[b].DiagonalMatrix[{h1,h2}].b; jj={{1},{1}};
gg=dag[jj].sd.jj; pp=jj.Inverse[gg].dag[jj].sd; qq=sd.pp;
aa=-I Inverse[sd].hh-Inverse[sd].dd;
qdot=simp[D[sd,t].jj.Inverse[gg].dag[jj].sd+sd.jj.Inverse[gg].dag[jj].D[sd,t]-sd.jj.Inverse[gg].(dag[jj].D[sd,t].jj).Inverse[gg].dag[jj].sd];
ww=simp[qdot+dag[aa].qq+qq.aa];
tt={{r,s},{0,1/r}}; sp=dag[tt].sd.tt; hp=dag[tt].hh.tt; dp=dag[tt].dd.tt;
jp=Inverse[tt].jj; gp=dag[jp].sp.jp; pip=jp.Inverse[gp].dag[jp].sp; qp=sp.pip;
ap=-I Inverse[sp].hp-Inverse[sp].dp; wp=simp[D[qp,t]+dag[ap].qp+qp.ap];
checks=<|
"metric_compatibility"->zero[D[sd,t]-dd-dag[dd]],
"norm_generator_identity"->zero[D[sd,t]+dag[aa].sd+sd.aa],
"Pi_idempotence"->zero[pp.pp-pp],
"Pi_metric_self_adjoint"->zero[dag[pp].sd-sd.pp],
"Q_Hermitian"->zero[dag[qq]-qq],
"Q_metric_idempotence"->zero[qq.Inverse[sd].qq-qq],
"Qdot_product_inverse_formula"->zero[D[qq,t]-qdot],
"W_Hermitian"->zero[dag[ww]-ww],
"A_similarity"->zero[ap-Inverse[tt].aa.tt],
"Pi_similarity"->zero[pip-Inverse[tt].pp.tt],
"Q_congruence"->zero[qp-dag[tt].qq.tt],
"W_congruence"->zero[wp-dag[tt].ww.tt],
"generalized_characteristic_polynomial"->TrueQ[simp[Det[wp-lam sp]/Det[sp]-Det[ww-lam sd]/Det[sd]]==0],
"Q_not_ordinary_idempotent_example"->TrueQ[(simp[qq.qq-qq]/.t->1)!={{0,0},{0,0}}]
|>;
<|"assumptions"->ToString[ass,InputForm],"scope"->"Exact parametric 2x2 checks, not a general proof", "checks"->checks,"all_passed"->And@@Values[checks],"selected_gram"->simp[gg],"Pi"->simp[pp],"Q"->simp[qq],"Qdot"->qdot,"W"->ww|>
