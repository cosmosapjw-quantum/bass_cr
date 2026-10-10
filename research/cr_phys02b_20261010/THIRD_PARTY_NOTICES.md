# Third-party data and dependencies

The new Python code is provided under GPL-3.0-only as stated in its SPDX headers and
LICENSE. This statement does not relicense third-party data or papers.

## Curtin CCC numeric tables

Selected HI and HeI electron-excitation numerical tables were retrieved from the
[official Curtin CCC distribution](https://atom.curtin.edu.au/CCC-WWW/). Raw selected
tables and original README files are retained for exact scientific reproducibility.
Attribution, archive/file SHA256, publication status, units and adopted channel names
are in inputs/CCC_USED_CHANNELS.json and research/literature/CCC_SOURCE_AUDIT*.
No explicit open-data license was identified in the inspected archive documentation;
we do not assert a GPL license or unrestricted redistribution license for these data.
Users should consult the original distributor regarding further data reuse. HeI's
README identifies the 2026 calculation as unpublished at its stated release date.

## NIST and published atomic parameters

Numerical parameter facts and equations are attributed in DERIVATION_KO.md to NIST
and Müller et al.2009. The full paper PDF is not redistributed in this package. The
printed polynomial coefficients are a documented transcription; its SHA is not a
hash of the original article. No claim of exact NIST CGI reproduction is made.

## Software dependencies

Python, NumPy, SciPy and Matplotlib retain their respective licenses. They are runtime
dependencies, not vendored library source. Exact versions used for each actual run
are in that run's evidence. Parent bass_cr modules are retained by original path/hash
and their existing licensing; this study does not change them.
