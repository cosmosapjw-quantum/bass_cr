# Source and scope notice

This research sidecar imports the unchanged, SHA-pinned CR-PHYS01
`injection.py`, GPL-3.0 Rudd adapter, and the SHA-pinned CR-PHYS02B kernel.
Their source notices and licenses remain in their original directories.
The P02B manifest verifies its vendored DarkHistory source before execution.

The source is Qe(W,t)=t A(W), with A obtained from the absolute Rudd SDCS and
the inherited, full-spectrum-normalized PR24 proton injection. The gas and
source snapshot remain frozen. Numerical source normalization inside the
solver is undone exactly when weighting each cohort; it does not change the
physical proton source normalization.

Only directly born 10–1000 eV electrons are evolved here. Primary binding
and secondary binding/excitation are distinct ledgers. Direct-born lower and
upper electron source partitions are reported without deposition. The P02B
cutoff retains number and kinetic energy; it is not an input to P02A. This
sidecar supplies neither gas feedback nor cosmological electron transport,
nor an uncertainty-certified full secondary history.
