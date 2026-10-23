# In this directory

It should be noted that the data files are not binned in consistent redshifts, nor are the files themselves binned in consistent energy between models. This is a result of each UVB model originating from different authors who binned their data differently.

If you want to interpolate to compare intensities at similar energies, you can use the [numpy interp](https://numpy.org/doc/stable/reference/generated/numpy.interp.html) function. An example on how to run this is shown below

```
import numpy
import pandas as pd

uvb_z = pd.read_csv(path/to/uvb/z_###.csv, usecols = ["E (eV)",  "I (erg/s/cm**2)"])

energy_bins = uvb_z["E (eV)"]
intens = uvb_z["I (erg/s/cm**2)"]
interp_energy = np.linspace(7.5, 7.9, 100)
interp_intensity = np.interp(interp_energy, energy_bins, intens)

print(interp_intensity)
```