# Transport-angle/charge-label convention correction (blind-referee addendum)

This correction belongs to BASS-CR PR #154 and changes **no** computed original BASS193 CX rate, source identity, CSV, physics ZIP or numerical result. It narrows an ambiguous *future* momentum-transport recommendation in the initial handoff.

For incoming equal-mass proton and neutral hydrogen with center-of-mass velocity \(\mathbf U\) and incoming relative velocity \(\mathbf g=\mathbf v_p-\mathbf v_H\), let \(\mathbf g'\) be the nuclear relative velocity after a two-body scattering event, with \(\chi\) the **nuclear** angle satisfying \(\mathbf g\cdot\mathbf g'=g^2\cos\chi\). Then

\[
\mathbf v_p^{\rm in}=\mathbf U+\tfrac12\mathbf g,\quad
\mathbf v_H^{\rm in}=\mathbf U-\tfrac12\mathbf g.
\]

In **elastic scattering without electron transfer**, the outgoing charged velocity follows the same proton nucleus, \(\mathbf v_{p,el}'=\mathbf U+\tfrac12\mathbf g'\), and its forward momentum loss is \(\tfrac{m_p g}{2}(1-\cos\chi)\).

In **resonant electron capture/exchange**, the charge label belongs to the previously neutral target nucleus after the collision, \(\mathbf v_{p,cx}'=\mathbf U-\tfrac12\mathbf g'\). The forward ion-fluid momentum loss is \(\tfrac{m_p g}{2}(1+\cos\chi)\) **under this nuclear-angle convention**. This is a kinematic identity for nearly equal nuclei and channel-resolved final charge labeling. With an angle instead defined relative to the outgoing **charged particle**, the weighting convention transforms accordingly. Using \((1-\cos\chi)\) blindly for the exchange channel under the nuclear angle is physically incorrect.

Thus the standard elastic transport moment
\[
\sigma_{mt}^{el}=2\pi\int_0^{\pi}(1-\cos\chi)
\frac{d\sigma_{el}}{d\Omega}\sin\chi\,d\chi
\]
must NOT be applied without modification to a nuclear-angle-defined exchange differential cross section. The corresponding exchange contribution to first-order charge-fluid momentum transfer may involve \((1+\cos\chi)\), and an actual ion-neutral momentum/heat source requires integrating the *channel-resolved scattered charged and neutral velocity distributions* with original \(f_p,f_H\), reaction kinematics, and recoil, retaining \(Q^a_p=-Q^a_H\). It must also respect quantum indistinguishability at low energy. Elastic plus CX transport cannot be naively summed from incompatible amplitude/angle conventions; double counting is possible.

Original references (primary):
- Krstić and Schultz, *Phys. Rev. A* 60, 2118 (1999), DOI https://doi.org/10.1103/PhysRevA.60.2118, cross-section definitions and quantum indistinguishability.
- Schultz et al., *J. Phys. B* 49, 084004 (2016), DOI https://doi.org/10.1088/0953-4075/49/8/084004, quantum p+H charge transfer and elastic DCS.
- Schultz et al., *Atomic Data and Nuclear Data Tables* 154, 101601 (2023), DOI https://doi.org/10.1016/j.adt.2023.101601, updated elastic DCS/transport.

**Current result scope unchanged:** PR #154 computes only \(\langle\sigma_{cx}g\rangle\) as a source-conditional **event rate** over the documented 3–200 km/s window. It computes NO \(\sigma_{mt}\), no two-fluid force, no Bianchi tilted collision integral, no REI ionization evolution, and does not advance the original REI 28/88 central DAG. Existing exact-zero *net chemical* source remains valid for resonant exchange. Next work is to acquire the original DCS with a specific charge-label angular convention and use it to build a proper fluid transport operator, without importing it into REI before matching its source clocks and BASS geometry.
