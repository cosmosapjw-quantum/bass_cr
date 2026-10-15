# Actual AXBI owner ray/chemistry input handoff to rei_bianchi

Source authority: rei_bianchi@0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
C18 parent bass_cr C17 at 1c15983e86909c44620201f2da2a63dddef6b2e1.
All physical source+checkpoint IDs pinned in OWNER_LOCK.json.

C18 connects real Rust AXBI_CHECKPOINT_V2 photonic inventory at
a=.0887365 ZERO (q0) and a=.0665770 SHEAR_PLUS (q=.01).
These are actual, DIFFERENT epochs, not matched-q scientific spectra.

Original Rust, not a Python duplicate, authorizes:
- 8 source angular cells, each owner-source mu and count_fraction,
  one current-frame J and current mu via CharacteristicRay::pullback,
  native source angular weight normalized count_fraction*J.
- 49 source energy nodes and all 392 photon/H stock numbers,
  3 native HI/HeI/HeII Verner cross sections per E knot.
- Original AxbiSource::at_redshift rate and conservative energy-node
  deposition of the newly emitted nodal photons.
- Original ledger residuals with the checkpoint's gas and time.

Local fixed-gas C17 photon chemistry:
 n_abs_j/nH=[1-xHII,y*(1-xHeII-xHeIII),y*xHeII].
 Proper absorber density n_abs_j=nH*n_abs_j/nH [cm^-3].
 Rate lambda_j=c*n_abs_j*sigma_j(E).
 For frozen proper dt=1e10 s:
 N1=N0 exp(-tau)+Sdt*phi(-tau),
 A_j=[N0+Sdt-N1]*lambda_j/lambda_total.
 Physical photon heating Q_j=sum_k A_kj*(E_k-I_j) [eV/H]
 with actual HHeModel binding I=(13.598434599702,
 24.587389011,54.41776)eV, distinct from Verner fit cutoffs.

Original native IgmPhotoInput is per ABSORBER, not per H:
 gamma_s_j=(A_j/dt)/(n_abs_j/nH);
 heat_erg_per_absorber_s_j=(Q_j/dt)/(n_abs_j/nH)*EV_ERG.
 Direct Rust igm_point_rhs(state, nH_proper, nHe_proper, h=0,
 Tcmb=2.7255/a, photo) confirmed:
 photo_events_cm3_s[j]=nH*A_j/dt;
 photo_input_erg_cm3_s=nH/dt*(sum Q_j+I_j A_j)*EV_ERG.
 Owner axbi_driver::evaluate passes h=0 to its
 microphysical chemistry RHS while separate geometry_map handles
 adiabatic gas cooling. Do not apply Hubble expansion twice.

Still missing for full dynamics: actual sequence of temporal photon
states at a COMMON controlled cosmological time, moving energy/ray
support, stochastic source ages, true transfer boundary data,
non-equilibrium H/He/electron,T cooling, OTS/secondary reactions,
and independent stiff integrator comparison. Existing SOURCE07 C8,
AX08, AX11, AX12 global gates remain HOLD.
