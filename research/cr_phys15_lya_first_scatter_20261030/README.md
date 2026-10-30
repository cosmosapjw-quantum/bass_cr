# BASS-CR PHYS15: source-owned H 2p spontaneous Lyα injection & first resonance scattering

**One new scoped physical computation.** Original complete PHYS14 SOURCE ZIP is byte-locked at `sources/PR139_ORIGINAL_SOURCE.zip`.

- Inputs: original 6400 RR photons, four native birth bins, 100K and n(HI)=138.6 m^-3; original measured Shah H ion and NIST BE 2p collision rates in their **shared measured support only**.
- New atomic line: 2p->1s A=6.2649e8 s^-1 (NIST Wiese/Fuhr 2009), f=0.41641, source-owned E=10.1988 eV. Fixed 100K H gas, Voigt first-scatter sigma(x).
- `x` is externally conditioned emitted Lyα frequency in Doppler widths, **not** source-predicted emission spectrum or recoil distribution.
- First inelastic H(1s)->2p event -> 2p radiative photon on same proper clock -> first HI scattering before T. Fast 2p lifetime treated by a mathematical upper bound with prompt first-scatter numerical approximation.
- **NOT** second/multiple scattering, actual Lyα escape, density/temperature feedback, full H electron stopping, physical K, globally exclusive He event kernel, or coupled cosmological radiation-chemistry IVP.

Run `bash REPRODUCE.sh` on a **complete SOURCE ZIP extraction**. Git-only checkout intentionally excludes all nested original binary source.

Scientific plots are in `figures/`; output CSVs in `results/`. Full manifest guards source bytes. Source-specific publication is Draft only.

Central DAG 28/88, extension DAG 0/3, auxiliary 1/1 scoped REVIEW_HOLD. Distinct-author R06/C09 NOT_RUN. No merge, no force-push, auto_next=false.
