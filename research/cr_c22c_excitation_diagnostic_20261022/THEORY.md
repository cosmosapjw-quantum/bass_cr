# Conditional hydrogen excitation closure

The newest bass_cr science is C22B: three BDF cases and one Radau comparison with a finite UV field, thermochemical energy and a prescribed Compton bath. These calculations remain unchanged. Its missing SW91 excitation coefficients were resolved directly from Table3 on printed page305 of Scholz & Walters (1991), [doi:10.1086/170587](https://doi.org/10.1086/170587). The original equations12/13/16/17 assign b coefficients to1s→2s, c coefficients to1s→2p, and use y=ln(T/K). Three temperature ranges are2000–60000,60000–6000000,6000000–100000000K. The model threshold is0.75Ry. The authors' fit statement is not an independent validation performed here.

For each branch, implement the original functional reconstruction

\[
q_i(T)=\exp\left[P_i(\ln T)-\frac{\Delta}{k_BT}\right],\qquad
P_i(y)=\sum_{j=0}^5 a_{ij}y^j.
\]

The full cross-section convolution need not be recomputed for this conditional fit. Horner evaluation and its simultaneous polynomial derivative give

\[
\frac{\partial\ln q_i}{\partial\ln T}=P_i'(\ln T)+\frac{\Delta}{k_BT},\qquad
q_i'(T)=\frac{q_i(T)}T\left[P_i'(\ln T)+\frac{\Delta}{k_BT}\right].
\]

Wolfram Language independently simplified the difference between the symbolic derivative and this expression to0. This is algebraic verification; no xAct calculation is needed for this scalar local rate.

Under a separate prompt radiative-decay and optically-thin escape closure, let
\(F=n_en_{H,1s}\Delta(q_{2s}+q_{2p})\), in eV cm⁻³s⁻¹. A single computed flux supplies gas energy loss−F and the cumulative escaped radiation gain+F. Charge and nucleus abundance do not change in this ground→excited→ground reduced event. No net electron-particle creation term belongs to this event. If atomic excited populations or trapped radiation are evolved, the corresponding excitation-energy and radiation states must replace this immediate-escape closure. The total emitted energy is fixed; neither the Lyα transfer nor the2s two-photon spectrum is supplied by this scalar rate.

The inherited chemistry energy increment13.6eV is not silently substituted for the source convention Ry=13.605693122994eV. D/T sharing, helium/lithium, higher-n levels and collisional de-excitation require their own decisions. Below2000K the provider returns NaN with a false availability mask. Threshold Boltzmann suppression alone supplies no source-validated rate or numerical upper bound there.

The two internal polynomial boundaries are intentionally unsmoothed. Their computed rate jumps are0.05953%/0.59620% for2s and−0.27330%/0.57085% for2p at60000/6000000K. The upper interval owns the boundary, with a one-sided derivative. These jumps follow the rounded source fits and are retained as a future ODE-event/design issue. No global error certificate follows from them.

The bounded validation evaluated126 coefficient cases against80-digit decimal direct polynomials: maximum relative rate roundoff3.26255e−12 and absolute log-slope discrepancy4.74392e−13; paired energy sum0. Seven unavailable-domain inputs remain unavailable. Source coefficients were independently visually reviewed.

The frozen C22B LRS history SHA256472363d822a821e87f87a2cad6de60c9045912e00b71f243b1b0969c3d25d6c3 contains201 saved temperatures30.3958–9916.20K. Only71 points and70 adjacent intervals are within the SW91 domain, covering2.15755% of the elapsed time. Trapezoids on those available intervals give0.0489597873eV per referenceH of hypothetical H1 excitation loss. It is a conditional diagnostic on the original trajectory, not a new cooled trajectory, whole-history integral, error bound or proof that missing excitation is negligible. No gap is bridged. NewODE/RHS calls=0; elapsed validation0.106s.
