# Full S,H,D: same-center weak form

Internal numerical units are a0, Eh, ta=hbar/Eh. Physical definitions: S_ab=<chi_a|chi_b>, H_ab=hbar^2/(2m)<grad chi_a|grad chi_b>+<chi_a|V|chi_b>, D_ab=<chi_a|partial_t chi_b>. The evolution is i hbar S dc/dt=(H-i hbar D)c.

chi_a=exp[i m v_c.r/hbar-i m v_c^2 t/(2hbar)] phi_a(r-R_c(t)). For a common center define A_ab=<phi_a|grad phi_b>. Zero extension is H1 with vanishing Dirichlet trace; A+A^dagger=0 follows from integration by parts. No second derivative or unaccounted surface delta is used.

H_cc=H0_cc+Vother_cc-i hbar v_c.A+(m v_c^2/2)S_cc;
D_cc=-v_c.A-i(m v_c^2/(2hbar))S_cc.
Consequently H_cc-i hbar D_cc=H0_cc+Vother_cc. This algebra is checked numerically, not used to overwrite raw H or D.

For u_a(r) and Y_lm(n), integrate on the entire own sphere:
S_ab=delta_la,lb delta_ma,mb int u_a u_b dr;
H0_ab=delta_la,lb delta_ma,mb int [u'_a u'_b/2+(l(l+1)/(2r^2)-Zc/r)u_a u_b]dr (atomic units).
With N_ab=int Y_a* n Y_b dOmega and G_ab=int Y_a* grad(solid_harmonic_b)(n)dOmega,
A_ab=int u_a u'_b dr N_ab + int u_a u_b/r dr [G_ab-(l_b+1)N_ab].

Other-center potential at displacement Rvec has exact projected multipoles:
Vother_ab=-Zother sum_{L=0}^{la+lb} C_L_ab int u_a u_b r_<^L/r_>^{L+1} dr,
C_L_ab=int Y_a* Y_b P_L(n.Rhat) dOmega.
Selection by finite angular polynomial degree makes the projection finite; this is not a truncated approximation to the pointwise Coulomb field. r=R is explicitly a radial split. The angular singular point at r=R,n=Rhat is measure zero; the radial branches agree there. At R=0 the potential is -Zother/r and only L=0 remains for same-center integrals, although the inherited two-center cross chart rejects coincident centers.

Primary identities: NIST DLMF 18.12.11 https://dlmf.nist.gov/18.12.E11 and spherical-harmonic addition theorem 14.30.9 https://dlmf.nist.gov/14.30.E9. New derivation combines these with the declared finite angular basis. No physical model change is made.

Full matrices are assembled in the original channel order. Cross terms have intersection support; TT and PP use their own sphere. D is NOT Hermitian and cannot be reconstructed by symmetrization. Identity dot(S)=D+D^dagger is tested by an independent time difference of freshly integrated S on a small basis. This does not by itself determine the skew part of D; direct fixed-point differentiation of the basis supplies an additional test.

No continuum completeness, capture error, cross section, or production admission follows from these static tests.
