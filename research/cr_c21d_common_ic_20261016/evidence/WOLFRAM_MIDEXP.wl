ClearAll[aa, bb, cc, kk, ll, mm, t, s];
At = aa + bb s + cc s^2/2;
Kt = kk + ll s + mm s^2/2;
exact = Integrate[At Kt, {s, 0, t}];
approx = t (kk + ll t/2 + mm t^2/8) (aa + bb t/2 + cc t^2/4);
Table[FullSimplify[SeriesCoefficient[approx-exact, {t, 0, i}]], {i, 0, 3}]
(* Observed: {0, 0, 0, cc kk/12-bb ll/12-aa mm/24} *)
