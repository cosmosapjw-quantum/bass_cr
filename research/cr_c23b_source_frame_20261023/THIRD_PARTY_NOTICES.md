# C23B attribution and reuse

The original BASS_CR repository license governs this repository's newly authored work. The following dependencies keep their own notices and identities.

1. Taira, Kopenhafer & O'Shea (2025), data release DOI 10.5281/zenodo.15367103, Git 863c3b7fa73a8510fbf57ee7b75ad1e8c34086de. Retrieved release metadata declares CC0. See `source_providers/THIRD_PARTY_NOTICES.md` and `evidence/zenodo_record.json` there. The research paper's license is distinct. Converter code is read for provenance, not executed.
2. Verner et al. (1996), ApJ 465,487, DOI 10.1086/177435. Numerical ground-state fit parameters from https://www.pa.uky.edu/~verner/photo.html are attributed and pinned. C23B implements the published formula; it does not copy or run the original Fortran routine and does not infer a software license for the website.
3. Furlanetto & Stoever (2010), MNRAS 404,1869, arXiv:0910.4410. Five unambiguous high-ionization tables are reused from the 21cmFAST MIT mirror, upstream commit 72d8a2d23702f1b69fbc85abd25d4592a7bcd3f5. The MIT notice is retained at `implementation/vendor/21cmFAST/LICENSE`, with table pins in `REUSE.json`. The byte-identical BASS_CR C23A Python interpolation operator and resource controller are documented in `implementation/REUSE_MANIFEST.json`. Original unlicensed C interpolation source and the full paper are excluded.
4. Standard Lorentz kinematics and proper-time decay are cited to the PDG 2025 Kinematics review. The massive isotropic boost representation is compared with Agashe et al., arXiv:1512.02265. Symbolic checks and independent numerical implementations do not constitute a global novelty claim.
5. Selected text and code from the user's BASS/REI/HE/HH/REC/VigilODE repositories are retained as commit-bound research evidence. They are not silently incorporated as an executed ensemble. `intake/ALL_SELECTED_TEXT_BINDINGS.json` identifies each source. Full source-license scope must be checked again before adopting any additional external component.

No aggregate manifest overrides an upstream license, a historical execution identity, or a physical domain restriction.
