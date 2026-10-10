CR_NONAUTONOMOUS_PRESCRIBED_DENSITY01 — implementation return

Status: FIRST_FAILURE_HOLD; independent Astra review PENDING.

The single authorized campaign exited1 at main_refinement. Maximum normalized energy-channel errors against the4096-step SSPRK2 reference were0.01905545742242143,0.005234131789404135,0.0013005337775715692 at sparse128,256,512. They decrease, but the512 value exceeds the frozen2e-4 criterion. No tolerance/model change, repair or rerun was made. Constant-bath continuation and legacy P02B were not executed because the first-failure stopping rule applied.

Completed cases: two analytic equal-age cohorts with absolute bath clocks, main sparse128/256/512, daughter-order12 sparse512, independent SSPRK2 order8 steps4096. The daughter quadrature difference was3.8535095114866635e-9 (criterion1e-8). Recorded SSPRK2 maximum collision CFL was0.3047241433572126 (cap0.4). Completed observations passed finite/nonnegative, exact-HeII-zero and ledger checks. The initial t0/OFF, zero deposited-energy and cold-temperature rejection controls passed. These component results do not admit the experiment.

Accounting:5536 macrosteps,9634 block actions,3 response columns per action; wall137.62257255095756s, CPU137.241904729s. The process was observed at PID3521037 with NLWP1. Requested runtime identity was a lower-tier implementation worker; model identity was not measured. One campaign launched, zero repairs and zero reruns.

CONTRACT_CLARIFICATION_R1 preserves the original7000-stage ambiguity and records Astra's explicit resolution: count RHS/exponential block actions; full campaign maxima6560 macrosteps/10658 actions; SSPRK2 reference8192 RHS actions. Legacy uses a shared512-step timeline and the original generator grid for absolute characteristic times. The legacy implementation remains unexecuted.

All frozen CR/REI input hashes matched; causal_generator.verify_sources completed. Bath input is exactly native id0,n32,physical epochs0/1 from PR109 stored RESULTS, interpolated in absolute proper seconds. The frozen old-method Gas stays100K; stored cold thermal fields are NOT_USED. No source, production, guard, or REI files were changed; only this research directory was created. No commit or push.

Raw observations, acceptance evidence and first traceback are in RESULTS.json; exact captured terminal output is in CAMPAIGN_STDOUT.log. global admission, physical thermal coupling, feedback, radiation transport, and physical continuum remain HOLD.
