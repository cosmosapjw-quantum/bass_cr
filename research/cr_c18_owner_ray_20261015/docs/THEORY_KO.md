# C18 physical AXBI checkpoint to H/He photoheating bridge

## Actual user-owned data, no synthetic photon stock

Baseline bass_cr branch C17 commit 1c15983e86909c44620201f2da2a63dddef6b2e1.
Read-only rei_bianchi owner HEAD 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
AXBI_CHECKPOINT_V2 genuinely validated by the original Rust
Driver::read_checkpoint, with SOURCE07 geometry clock, initial energy,
gas state, and 8 ray by 49 energy photon node contract.
FLRW ZERO a=.088736547 and Bianchi-I q=+0.01 a=.066577011
are at DIFFERENT physical times. No matched-a anisotropy inference.
Owner source SHA-256s and original checkpoints in OWNER_LOCK.json.

Original rust AXBI source inject formula is reconstructed with public
AxbiSource::at_redshift, native CharacteristicRay::solid_angle_jacobian
and Driver::deposit in the C18 Rust exporter. Source weights are
count_fraction*J / sum(count_fraction*J). Do NOT apply R J again in
the receiving photon / gas code.
Rust exports native physical energy nodes E_i and sigma_HI,HeI,HeII(E_i),
and all 392 stock N_ki per original H, and positive newly emitted
source rates S_ki [photons per original H per proper second].
The exact Rust checkpoint N and U inventories and residuals are preserved.

## H/He species absorption and photo heat

Original owner gas fractions [xHII,xHeII,xHeIII] are ION fractions,
not neutral fractions. Proper absorber/H:
 HI 1-xHII; HeI (nHe/nH)*(1-xHeII-xHeIII);
 HeII (nHe/nH)*xHeII. Species proper densities are nh*absorber/H.
For a locally frozen gas/energy/source over dt=1e10 proper seconds:
 lambda_ki,j = c*n_abs,j*sigma_j(E_i).
 N_after = N_old exp(-tau)+Sdt*(1-exp(-tau))/tau,
 A_ki,j=(N_old+Sdt-N_after)*lambda_j/lambda_tot.
Species events A_j=sum_ki A_ki,j, photon photoheat
 Q_j=sum_ki A_ki,j*(E_i-I_j) [eV/H],
 binding B_j=I_j*A_j. Physical owner binding energies are
 I=(13.598434599702,24.587389011,54.41776) eV.
The Verner FIT thresholds (13.60,24.59,54.42)eV differ.
All accumulated species rates and heat remain nonnegative.
C17 positive time source quadrature is tested against independent
C14 exponential formula at these constant coefficients.

## Actual Rust igm_point_rhs interface

The C18 Python adapter converts events/H to the user-owned
IgmPhotoInput arrays:
 Gamma_j = (A_j/dt)/(n_abs,j/nH) [s^-1 per absorber],
 heat_j = (Q_j/dt)/(n_abs,j/nH)*EV_ERG [erg/absorber/s].
Native owner_photo_rhs.rs loads the same validated checkpoint,
constructs IgmPhotoInput and calls igm_thermal::igm_point_rhs with
h=0 and Tcmb=2.7255/a, matching axbi_driver::evaluate where
Bianchi geometry/adibatic work is a separate owner stage.
The genuine Rust RHS photo_events_cm3_s equals
nH*A_j/dt; photo_input_erg_cm3_s equals
nH*(sum_j Q_j+B_j)*EV_ERG/dt. The observed correspondence is at
floating point precision, and it returns original Rust CI, RR,
DR, CMB and thermal derivative point rates without replacing them.

It does NOT validate an integrated full chemistry evolution.
The original AXBI code employs backward Euler with nonlinear
gas updates; C18 freezes gas/energy/rates during the deliberately
isolated local chemical input check. The actual source deposit is
reconstructed using public owner APIs, not by invoking private
Driver::inject. All owner input files remain unchanged.

## Actual numerical evidence

ZERO at a=.08873655, q=0:
 native N=1.649933353054249e-6/H, U=4.112729537699338e-5 eV/H.
 for dt1e10: events HI=2.339162941403897e-7/H,
 HeI=2.0425434764630007e-8/H, HeII=1.4338060867592457e-11/H.
 photon count residual=1.5881867761018131e-22/H,
 energy residual=1.0164395367051604e-20 eV/H.

SHEAR_PLUS at a=.06657701, q=.01:
 native N=2.7963611369316e-7/H, U=6.97237524890475e-6 eV/H.
 dt1e10 events HI=1.0249253480799078e-7/H,
 HeI=8.9118843946562e-9/H, HeII=1.4561774415762537e-12/H.
 mass residual=-1.3234889800848443e-23/H,
 energy residual=8.470329472543003e-22 eV/H.

Native Rust and C11 Python Verner rates at all 49 energies agree
within 1.41e-15 relative; q=0 angular J=1, q=.01 J spans
0.992913..1.014047, and angular source weights normalize to unity.
Source photon rate per original H/s matches original native source
rate within rounding.

## Research status and next constructive gate

SCOPED actual checkpoint/ray/J/source/chemical photo input VERIFIED.
NOT DONE: owner full source-age ray photon temporal history,
time-varying spatial radiative transfer, full thermal/CI/RR/DR
coupled integration, optical depth hardening along actual rays,
OTS and secondary ionizations. Physical EoR xHI(z),HeII(z),
HeIII(z),Tgas(z) error budget and AX08 global admission HOLD.

Primary context:
Friedrich et al. 2012 MNRAS 421 2232,
DOI 10.1111/j.1365-2966.2012.20449.x,
and Norman et al. 2015 ApJS 216 16,
DOI 10.1088/0067-0049/216/1/16.
