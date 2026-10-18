# Authoritative C21E release boundary

Use executable code commit **1ee8cb5a3377381de35b6b9a0e3b8dc1cfb12f41**. Initial22623f99 is retained as the43-test code checkpoint. Latest portable suite is **44/44 PASS** with a new red-green native probe-domain input test; 13.59eV was below the original q-grid minimum at a_ref and was replaced by13.61eV. Neither the original native grid nor a physical tolerance was changed. Native actual absorption parity remains NOT_RUN.

The12 manufactured source-on trajectories and their measured errors were generated before this native-only preflight change; their scientific source/fixture are unchanged. SCIENTIFIC_RESULT.json preserves that43-test historical stage, while TEST_RELEASE.log and DELIVERY_RECEIPT.json carry the44-test final release. Source files in the final archive match the complete current executable code. All remaining NCP algorithmic work is already authored; only compilation, unavoidable minor compiler/API corrections and actual bounded execution remain.

The final273890-byte archive was fully redownloaded independently from Library, Google Drive and Dropbox, SHA/CRC/62-payload manifest matched. Each Drive and Dropbox extraction passed44 tests. No Rust compiler was available in the sandbox. This receipt must not be read as native Grackle or full-EoR PASS.
