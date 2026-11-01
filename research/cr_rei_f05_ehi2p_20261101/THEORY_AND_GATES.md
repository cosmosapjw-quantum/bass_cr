# Original REI F05 e + H I(1s) -> H I(2p) collisional Ly-alpha source (R1–R10)

2026-11-01; source-scoped physical research unit in BASS-CR; immutable parent PR160 fb4f0e150aae027421fafa942abc7c09d70ae67d. Original REI accepted tick160/131072, tick161 NOT_ACCEPTED. No owner/production/main mutation.

## R1–R3 | Research contract, sources, conventions

Goal: derive and compute original 46,080-cell source-native electron-impact 1s->2p excitation, separate from already computed Case-B recombination and Ly-alpha line-centre material cross section, without inventing a line-photon distribution. Source state 46,080×27 original CSV SHA256 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d, full private input; source-native published Case-B derived 46k CSV SHA256 5aa85017b9bebb11822aca4780e9c3c248aadb87f8175575f1d8f8fd8821c154. Reuse owner-verified private proper volumes and original electron counts/temperature at t160; no private raw source in Git.

Scholz, Walters, Burke & Scott (1990), MNRAS 242 692, DOI 10.1093/mnras/242.4.692, original Maxwellian e+HI 1s->2p effective collision strength study valid from 5000K. Published Pradhan tabulation https://vo.ned.ipac.caltech.edu/level5/Pradhan/Table2a.html supplies actual HI 1s–2p Υ(T): (5000K,0.416), (10000K,0.472), (15000K,0.528), (20000K,0.585); A21=6.265e8 /s. Straight-line interpolation of Υ between published knots is OUR explicitly model-conditional interpolation, not original continuous exact atomic data. Standard conversion q12(T)=8.629e-6*Υ(T)/(g1 sqrt(T))*exp[-E12/(k_B*T)] cm³/s with g1=2, g2p=6, E12=10.198835887565243 eV, k_B=8.617333262145e-5 eV/K. See https://academic.oup.com/mnras/article/435/2/1576/1042586 and Dijkstra arxiv:1406.7292.

## R4–R5 | Physical derivation

At original tick160 per cell j, with original H count N_H, HII fraction x, electron count N_e and proper volume V (all original owner) and original gas temperature T, assume Maxwellian electron T_e=T_gas, unknown ground-state neutral fraction f1s ∈[0,1]. Define
  q12=8.629e-6*Υ_interp(T)*exp[-E12/(k_B*T)]/(2 sqrt(T)) cm³/s;
  q21=8.629e-6*Υ_interp(T)/(6 sqrt(T)) cm³/s;
  R_exc=N_H*(1-x)*f1s*(N_e/V)*q12 [1/s].
Under explicit two-level spontaneous/deexcitation closure, collisional quenching branching b21=A21/(A21+(N_e/V)*q21). Thus R_Lya,coll=b21*R_exc (produced photons per proper second), NOT escaped photons or a measured 2p level population. The f1s=1 assumption is a SOURCE-CONDITIONAL saturation, not universal observed emissivity or a bound on all Ly-alpha sources.

Original Case-B comparison on SAME material cell (with published Dijkstra/Cantalupo cascade P_B):
  R_rec,Lya=N_H*x*(N_e/V)*alpha_B(T)*P_B(T);
  R_exc/R_rec,Lya=f1s*(1-x)*q12(T)/(x*alpha_B(T)*P_B(T)).
This ratio is independent of cell proper volume and free-electron count ONLY because both source channels use same cell, clock and T. A volume does NOT cancel in summed production rates; no line-of-sight optical depth, source-time reaction integral, Ly-alpha spectral intensity or actual net radiative gas cooling is inferred. Excitation takes E12 energy from free-electron thermal pool per event, with reabsorption/redistribution unmodeled.

## R6–R7 | Domain and falsifications

Include cells only when original SOURCE T_lower>=5000 K AND T_upper<=20000 K; DO NOT extrapolate below/above the four available tabulated knots. Verified original state screening: 12,528/46,080 included; excluded 14,832 cold and 18,720 hot. The domain contains 75.83855556965159% of original neutral H count, but cannot bound the OUT-OF-DOMAIN collision luminosity. In piecewise-linear Υ_interp, Υ'(T)>=0; because E12/k_B > T/2 for T<=20000K, d ln q12/dT = Υ'/Υ -1/(2T)+E12/(k_B*T²)>0, so source endpoint T intervals bound q12 under THIS model. All source uncertainties are original interval bounds, not atomic fit confidence intervals. Other collisional channels omitted.

Independent tests: tabulated q12 at each knot; detailed balance q12/q21 = (g2p/g1)*exp[-E12/k_B T]; zero f1s; source intervals; dimension; positive rates; original row count and temperature cutoff; electron-count and volume scaling; no accidental ionization/recombination counting; original accepted vs nonaccepted tick labels. Pilot only: f1s=1 source rate ~5.028316296918783e48/s, same-domain conditional Case-B Ly-alpha ~1.3465051545657722e50/s, ratio ~0.03734346. Code must recompute before admission.

## R8–R10 | Science claim / watchdog / handoff

Deliver ONE new per-cell supported-domain 12,528-row physical output, actual rate and conservative original SOURCE interval enclosure, collisional quenching test, source-bounded comparison to PR160 Case-B, no extra atlas. Source original F05=160/131072; tick161 NOT_ACCEPTED; REI Central=28/88; REI Working=33/88; BASS-CR extension=0/3, Δ0. NO_REI_MUTATION; NO_MAIN_MERGE; NO_FORCE_PUSH; CR_OFF_UNCHANGED; PRODUCTION_HOLD. STOP optional looping after this unit; next decisive source-owner action remains tick161 versioned admission and RUX02/RUX03 line-photon/geometry source matching. Blind referee: same-author adversarial pass only; native subagents NOT_RUN; distinct-author reviewer NOT_RUN.