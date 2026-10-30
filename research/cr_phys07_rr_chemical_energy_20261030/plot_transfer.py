#!/usr/bin/env python3
"""Plot source-conditional He->HI binding-transfer energy trajectories."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
rows=list(csv.DictReader((p/'results/TIME_ENERGY_LEDGER.csv').open()))
for name in ('earliest','midpoint','latest'):
    d=[r for r in rows if r['policy']==name]
    plt.plot([float(r['time_s'])*1e-9 for r in d],[float(r['He_to_H_primary_electron_kinetic_boost_J_m3']) for r in d],marker='o',label=name)
plt.xlabel('Proper time (10^9 s)');plt.ylabel('He-origin -> HI primary-e gain (J m$^{-3}$)')
plt.title('Source-locked first photoionization energy transfer')
plt.legend();plt.tight_layout();plt.savefig(p/'results/HE_TO_H_CHEMICAL_ENERGY_TRANSFER.png',dpi=160);plt.close()
