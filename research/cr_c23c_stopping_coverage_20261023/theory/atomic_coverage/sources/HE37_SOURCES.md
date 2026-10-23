# Source admission and reuse

## Primary model

Hai P. Le and Jean-Luc Cambier, Modeling of Inelastic Collisions in a Multifluid Plasma: Ionization and Recombination, Phys. Plasmas23,063505(2016), DOI10.1063/1.4953050. Author PDF https://arxiv.org/pdf/1605.06545, SHA2565ee591cde0cb90c03b5fc47a8ad439bae93bcc36bd05a4cbb4e1943fec93fc68. Read Eq7,11–12, §III.E and Eq85; source-page images checked privately. Source PDFs/screenshots are not redistributed here. Underlying Zel’dovich–Raizer book is cited by Le–Cambier, not independently audited in this unit.

`evidence/intake/PRIMARY_SOURCE_REPORT.md` and `SOURCE_ADMISSION.json` own exact source equations, domain, labeling, constants refinement, source-native I13.6eV and angular G=1/(16pi²). Isotropic angular closure is a published approximation, not measured/CCC-calibrated differential H1 data.

## CCC content reused and explicitly bounded

Author database https://atom.curtin.edu.au/CCC-WWW/index.html and inspected H1 archive https://atom.curtin.edu.au/CCC-DB/H/I/ELECTRON_IMPACT/e-H_XSEC_LS.zip . Current downloaded7010887bytes/3162members, ZIP SHA57730e72656639e92c47c1b8457db0edac5a69ae93db6c357471a93759af1fc9. README defines integrated cross sections. TICS.1S SHA7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae matches HE36. The diagnostic will compare saved HE36 scalar values only. Neither total rates nor a probability tensor from escape transport determines electron outgoing angular moments.

## Delta donor intake

See evidence/intake/INTAKE_REPORT_KO.md, INTAKE.json, READBACK_BINDINGS.json and BRANCH_DELTA.json. New PHYS81 b3ec271a96cb67e583bffa9b61533802838236f9 and C23A7643af28c671a7473754a3c2cd0c6e523bd61aac supply scalar/energy/source developments, with differential gain and thermalization left open. REC125 b28b387 and REI22173c5e00 change delivery metadata only; their earlier scientific evidence remains valid. HE36pin6403055c3d574ec0bd1ece80147f9711315902e7 is unchanged.

This is delta intake since the previous comprehensive snapshot, not another all-history or all-conversation audit. Personal Context reported unavailable. 7repos/1281branch rows,9changedtips,9updatedPRs,19selectedGitblobs,5newcomments,29backup events were actually checked. Source metadata and code were reused; donor IVPs/suites were not rerun.

## Tool/source roles

Exa and SciSpace searches locate papers; original PDF content supplies equations. Wolfram independently returned zero angular and energy residuals, normalization1 and electroncount2. Independent Cartesian angular integration and adaptive radial integration are new HE37 evidence. The author’s rounded a0=0.529Å is intentionally refined to the existing HE36 value; I=13.6eV remains source-native.
