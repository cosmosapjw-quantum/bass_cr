# Repair01 observed outcome

The single approved campaign exited 0. Original RESULTS.json, validate.py and CONTRACT.json hashes remained unchanged. The driver imports the original calculation without editing it and reuses saved sparse512 and SSPRK4096 observations.

The prescribed order completed: constant512, shared-timeline legacy512, sparse1024, sparse2048, daughter order12/2048. Constant/legacy maximum energy-channel difference normalized by initial impulse was 7.605027718682322e-15. Errors against saved SSPRK4096 decreased from 0.0013005337775715692 (512) to 0.00027616669288110796 (1024) to 7.32986996518914e-05 (2048), meeting the 2e-4 terminal criterion. Daughter quadrature difference was 3.853476537862832e-09, within 1e-8. All original observation checks for finite nonnegative states, number/energy ledgers and HeII structural zero passed.

Measured CPU was 155.365482809 s; process wall was 157.5595795280533 s. Exactly 6144 macro/block actions and 18432 column actions were recorded. Overhead outside the process is not measured. Syntax was checked with ast.parse before the campaign. No rerun, additional repair, commit or push was performed.

Status is IMPLEMENTED_VALIDATION_PASS_PENDING_ASTRA. Independent scientific admission remains pending. This remains the retained100K prescribed-density numerical experiment; cold physical validity, thermal feedback, continuum and global admission remain HOLD. Original first failure is preserved in the parent directory.
