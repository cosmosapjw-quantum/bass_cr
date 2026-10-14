# BASS_CR: 유한율 thermalization의 해 선택과 오차

2026-10-14, Asia/Seoul. Selected R5 node NT_FINITE_RATE_ANGULAR_THERMALIZATION. Exact parent PR57 head ef27d056b2f65e46fca3ba1bc8729015877b6f54. Original report/contract/handoff/DAG read; no whole ten-stage replay.

## Full immutable source

ZIP BASS_CR_FINITE_RATE_20261014_SOURCE.zip,1081034bytes,57members/56payloads. SHA256 5362f211ceb18260c70ca44a6e765f9c0c69bc2c838ec7f15624ffcfee1e8ac6. Manifest SHA256 cec39f8da8806815138163ce77d77e976b25ace1303911127da67e3d73e923c2.

[Complete Korean proof, tested code, original inputs, results, failures and DAG](https://drive.google.com/file/d/1_iszmI2X6qe7eM1Sk1uNkzJg_X0I2LcQ/view?usp=drivesdk). Drive ID1_iszmI2X6qe7eM1Sk1uNkzJg_X0I2LcQ, existing parent1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI. Upload success and follow-up name/ID/parent/1081034byte metadata matched. Dropbox completed same1081034bytes at /BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_FINITE_RATE_20261014_SOURCE.zip, ID id:BSpOijBcT10AAAAAAD5Qvw. R1 ACK/metadata, not remote full restoration. All56new payloads,30preserved parent payloads, recursive CRC/font absence and relocated verification passed; altered-copy negative control failed and restored copy passed.

Git contains this compact proof/entrypoint; full executable source and REPORT_KO.md are inside the immutable ZIP, not all expanded into Git. No originals or permissions changed. Publication encountered two404 file-create responses because the new branch had not been created; those writes made no mutation. Creating the branch from the verified parent repaired the precondition before this successful write. This administrative failure occurred after the science archive was frozen and is not hidden as a scientific rerun.

## Conservative finite-rate definition

Keep smooth P1/S.999/A23.001, thermal1,nuclei13,HI7/HeI3/HII3,H=(2,4,6)e-15/s,h100000proper seconds, actual HI15600/HeI6812 paired sharing and4739total-rate coordinates. Regularize shell23 only. All original donor reactions, including competing Coulomb23->thermal, remain. Future-born shell23 electrons also wait; no duplicate heat.

Use(-,+,+,+), explicit c/kB and eV/J, count/cell and proper volume. B=Nnuc+Nth,q=eta U/B,eta40/3:

    k_tau=tau^-1 a((q-W)/delta_tau),
    a=0(x<=0),3x²-2x³(0<x<1),1(x>=1),
    f23'=b23-(nu23+k_tau)f23,
    Nth'=R_N+integral k_tau f23,
    U'=R_U+integral W k_tau f23,
    q'=(eta R_U-qR_N)/B+integral(eta W-q)k_tau f23/B.

Actual heat is W, not cutoff q. Original birth-time characteristic/angular Jacobian remains with exp(-integral k_tau) survival. For fixed positive tau/delta, the bounded Lipschitz gate and positive source tube give a regular finite-source integral problem. This is a partition regularization, not a calibrated microscopic collision channel.

## Driven selection and noncommuting limits

Frozen exact contact/zero drive has eligible mass0 for an angular-AC shell. With a(0)=0, zero transfer persists. Positive overdrive and persistent positive drive are different. An exact monotone hard-gate control has tau A'=F(q)-A, tau K'=Kcum(q)-K, q=eta(U0+Q+K)/(B0+A). For uniform[1,2],B0=10,eta4,mass4, take tau->0 then overdrive epsilon->0: q->17/7. Reverse the limits: q->1. Separate numerical controls retain both. A leaky gate at fixed width may remove particles before contact; arbitrary regularizations need not select one limit.

For this source the new gate vanishes identically before first contact, so only the SAME-prehistory bracket[11965.71473542306,11966.01640502353]s and m0 upper are reused. New directed source constants yield q'>=v+k A_fast', v>2.71216066481167e-11eV/s, k=(eta Wlo-E24)/26>0. The drive is surviving original S stopping heat minus maximal ionization/geometry-work terms, not an invented external source.

The massive angular cap bound W(t0,n)-wmin<=dbar sin²(theta), dbar=2(Hmax-Hmin)E23*15000, gives cap mass>=c_cap*x, c_cap=a_survive/(2dbar)>2.3174809e7count/eV. Then beta=c_cap*k-1>1.9128027e6. Select delta_tau=v_lower*tau/1000. After delta_tau/v, fully activated caps alone imply

    A_fast'>=(c_cap*v*u+beta*A_fast)/tau,
    A_fast>=c_cap*v*tau/beta²*(exp(beta*u/tau)-1-beta*u/tau).

The first upper t_g with v*u+k*A_fast>=dbar gives all-gate activation t_a=delta_tau/v+t_g=O(tau)+O(tau log(1/tau)/beta)->0. Activation is not complete absorption: a pending tail and future births remain.

## Completion removes the stiff term

All shell23 influx is bounded by bplus=13lambda24_bar+2Imax<2.692795825914e-5count/s. Once all gates are1, m'<=bplus-m/tau. With H=h-t0:

    I_m=integral m<=m0(t_a+tau)+bplus*t_a²/2+tau*bplus*H,
    m(h)<=(m0+bplus*t_a)exp[-(H-t_a)/tau]+tau*bplus.

R completes current shell23 energy to the bath. R²=R,||R||1=1 and R*T_tau=0. At fixed gas, future-born completion gives R F23=F24 R. For Y_tau=RZ_tau, the remaining residual is density feedback and stress-work:

    ||R F(Z_tau)-F24(Y_tau)||1<=chi*m,
    chi_C=13/V0 max_(j!=23)2Ej*sup(d_n lambda_j),
    chi_G=(ag+2Hmax)E23,
    chi<2.844796975211e-5eV/(s count).

Only chi_G*m contributes to its total-energy sum. Direct full/full convergence uses L_full=13maxGamma<0.000163259510949/s, yielding ||Y_tau-Z_infty||<=chi exp(L_full*h)I_m and ||Z_tau-Y_tau||<=2E23*m. This proves the specified driven, one-sided, shrinking-width family's convergence after the vanishing layer and for integrated observables. No uniform pointwise convergence across a finite jump or universal kinetic selection is asserted.

The tight stored-reference forward bound uses a DIFFERENT L_ref=1.75880002147704e-5/s from reference occupancy. Reassemble E_base from its actual polynomial residual/time/reset coefficients and add

    E_Yadd<=chi exp(L_ref*h)I_m,
    E_add<=E_Yadd+2E23*m(h),
    R_T=[1/(14cv)+102/(14Wlo)]*(E_base+E_add).

These are majorant contributions to finite/reference error, not measured finite-minus-instantaneous errors. Original2Eparent event cost and nonzero work remain.

## Actual source-bound results

For tau=1e-6,1e-5,1e-4,1e-3,1e-2,.1,1s,100000s temperature radii are below7.554706e-6,9.700248e-6,3.115567e-5,2.457099e-4,2.391252e-3,.02384667,.2384009K. Thus1e-3s meets unchanged.001K budget;1e-2s sufficient bound exceeds it. This does not prove the actual error exceeds the budget. At1e-3s Tfull(h) is in[101.20647769212073,101.20696911179812]K. All-gate activation is bounded by1.011038e-6s, distinct from1e-3s mass-drain time.

All seven rows pass a separate no-shell24 first-exit test. During the short asynchronous strip use full heat/pending energy,T<101.27719435918K. Later completedY is bounded by whole reference tubes; cv*T(Y)<Wlo gives T(Z)<=T(Y), below the next-shell cutoff. Endpoint m(h) is not an all-time pending bound.

R preserves total free count. New current majorants:

    E_Yadd,1<=chi*h*phi1(L_ref*h)*I_m,
    Delta_add,1<=2Hmax*h*E_Yadd,1+chi_G*h*I_m,
    R_column_add<=c*(E_Yadd,1+Delta_add,1)/(2V0 BH).

Do not add pending2E23*m again to chemical/current error. Apply sigma once with the same source/age/volume/current; foregroundnull. At tau1e-4s extra depth radius<1.342935790322e-24 and full depth in[5.9472799033627068,5.9472799065391615]e-15. At1e-3s extra radius<1.342935789640e-23 cannot resolve the small ionization excess from the raw lower bound; intersect the exact initial3-electron baseline. Temperature and ionization-excess resolution are distinct.

## Evidence and physical boundary

New directed7-row evaluation and independent Fraction/mpmath90/NumPy126checks passed;243angular samples are supplementary.19uniform-energy controls each used DOP853/Radau, maximum numerical discrepancy<1.921e-14. Eight helper tests pass with actual wrong-q-heat RED->GREEN. No full source finite-rate IVP/cascade,old suite,9600generator,native/HPC.

Actual Wolfram15.0.1:22groups/57scalar components. First56literalzeros and one equivalent exponential unsimplified,AllZeroFalse preserved; targeted FullSimplify closed it. Actual xTensor1.3.0:7tensor zeros, official hashes matched. Same author separate CAS/arithmetic; external reviewer/native subagents NOT_RUN. Control finite-horizon expectation and checker source-key repairs are recorded without science/tolerance changes.

SciSpace/Exa were used. Baker-Shkolnikov2003.07239 Theorem1.2 was read and assumes a bounded-density continuous-limit regime, not this supercritical shell. Le-Cambier1711.05946 and implicit Stefan2206.14641 provide comparison context.

Read HE46 full warm P01 R1_RESULT atd9a60904225f90d0e139c9b220dbd583413ccb51,HH63 detailedPR at13869fbd0ab6849613be694af3b0841c85a68b14,and REI116 actualREADME at2df18a7238b3e52d0eb844fd45aa706dbf883ab3. Reuse proper-density/current and single-event ownership, not foreign rates/numbers.

Original node23 discrete-edge wait6.22710478836e6s and W/b_Coulomb3.50730669696e8s are NOT microscopic calibration of tau. Passing the budget at.001s does not establish physical validity.

Next READY:NT_COULOMB_MATCHED_PARTITION_DECISION, matching actual stopping/energy diffusion and bath interface while retaining20kBT and this parametric family as separate baselines. F/G/atomic/b-grid/globalREI and CR/RCT/HH OFF unchanged. No merge, force push or original overwrite.