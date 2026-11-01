# REI/BASS193 first source-owned scalar Thomson receiver, CR-OFF

This is a **physically sourced, time-resolved 192-interval FLRW optical-depth and finite-window visibility calculation** on a frozen BASS193 H/He/21-species plasma history. The model is *not* the evolving REI central IGM IVP, does not include Bianchi-I or finite tilt, and cannot be promoted to central node completion.

## Reproduce

1. Recover original **private** `REI_F4_CCC_HHE_FIRST_COLLISION_20261031_FULL.zip` from the authorized prior REI source and verify SHA256 `4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52`.
2. Install Python with NumPy, pandas and matplotlib. Run:

```bash
python src/receiver_tau.py --source /path/to/REI_F4_CCC_HHE_FIRST_COLLISION_20261031_FULL.zip
python -m unittest discover -s tests -p 'test_receiver.py' -v
python -O -m unittest discover -s tests -p 'test_receiver.py' -v
```

The source ZIP remains out of the public GitHub draft PR. The 192-row derived CSV, numerical result JSON, code, figures and proof/limitations are included in this research package.

## Claims and owners

- Original source: REI PR311 and its BASS193 snapshot (H/He species, full21 `xe_saved`, diagnostic `xe_star`, proper clock); no original source mutation.
- Physical result: finite-window z=20→2, `tau_saved`, `tau_star`, `tau_HHe`, per-bin visibility. Different electron closure inputs on a common frozen background and common clock.
- Upstream next action: REI complete first canonical FLRW coupled interval, then BASS-owned geometry and anisotropic receiver, using this paired scalar witness as an interface regression.
- **DAG** reported central 28/88, working 33/88, extension 0/3. Canonical delta 0, CR adapter not used, no merge/force push, production HOLD, independent author review NOT_RUN.
