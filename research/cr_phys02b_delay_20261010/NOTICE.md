# Source and scope notice

The six vendored DarkHistory Python files are unmodified source at commit
`b556d0f0418a0665719fd6da26dcc303466b9659`. The upstream LICENSE at that same
commit is included unchanged (Git blob `2ed13ac7771c6c8f7753dd4ed37243ab495adfb3`).
See SOURCE_MANIFEST.json for byte identities. Upstream copyright and license
terms are retained in vendor/darkhistory/LICENSE.

The sidecar transcribes only the old-method raw excitation/ionization cross
sections and Coulomb energy-loss formula from physics.py. Its old conditional
two-electron shape uses exponent 2.1 and eps=(8,15.8,32.6) eV. The continuous-time
generator, paired energy-conserving quadrature/projection, and unresolved cutoff
reservoirs are new. They are not upstream DarkHistory's complete-cooling solver.
The upstream normalized transfer matrix, Cosmology defaults and cooling-table
databases are not executed by this sidecar. Source parity is tested by extracting
only the three upstream rate function definitions and supplying explicit local
densities, without executing upstream initialization or importing its databases.
