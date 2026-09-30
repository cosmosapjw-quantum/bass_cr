# B0 literature source acquisition

Owner request (2026-10-01): acquire the papers/code from the completed B0 static-tail literature report and back up the actual sources.

This isolated branch adds a bounded download-only job because the conversation container has no outbound DNS/network access. It does not check out or execute the BASS scientific solver, execute downloaded code, consume scientific authorization, launch NCP resources, change gates, merge, or overwrite another branch. Existing foundation CI is pull-request-only; no pull request is created.

Only public material is requested. A denial/paywall remains a failed acquisition. No purchased access, login bypass or third-party private data is used. Original paper files are encrypted with a one-use public certificate before the GitHub transfer artifact is uploaded; the private key remains in the requesting conversation runtime. The public artifact is not the permanent backup. The final archival destination remains the user's existing Google Drive and Dropbox backup folders.

The report-derived target set includes 31 works (including the original handoff anchors and an erratum), four named code projects, official documentation, and original author expmv code when linked. A GitHub source archive is a pinned source tree, not a full-history clone; dependency/submodule and licensing limitations remain explicit. A fetched PDF is not counted as the correct cited paper until local identity review.

Collector syntax compilation and an OpenSSL encrypt/decrypt roundtrip were checked before publication. The scientific claim ceilings remain unchanged.
