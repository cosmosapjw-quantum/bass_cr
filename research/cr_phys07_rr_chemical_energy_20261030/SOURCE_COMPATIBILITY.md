# Foreign-owner source compatibility (read-only survey)

The new physical H/He RR photon source is owner-locked PR131 at 100 K, four proper seconds bins and constant neutral populations. It has no proven common state with:

- REI PR278 BASS193 saved-epoch self-consistent ionization equilibrium. Different source state, epochs, chemistry inventory and radiation bath; no implicit transport.
- BASS PR267 Bianchi-I two-time angular power. Different geometry/clock and photon source.
- VigilODE PR126 native-stage audit. Numerical solver and F/J source ownership are not interchangeable with RR photon energy.
- BASS_HE PR120 EXFOR DD MeV photons and REC PR166 HD spectra: physically distinct energy/species channels.

All sibling PRs are read-only. No physical K, exclusive-He kernel, native25, L4 or production activation.
