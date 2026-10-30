# PHYS14 | H(1s) electron impact first-inelastic competition on identical photon source

## Definition / scope

Signature (-,+,+,+). Proper time s,t,T in seconds; frozen H I=138.6 m^-3, He I=11.427... m^-3, original neutral 100K H/He ground-RR photon spectrum (6400 original energy atoms across four birth bins). Original photon index j has source E_gamma,j [eV], weight w_j [m^-3], source birth s_j [s], first target H hazard a_j(E_gamma)=c n_H sigma_gamma_H(E_gamma) [s^-1] and combined photon first absorption hazard k_j=a_j+c n_He sigma_gamma_He. No photon geometry, redshift, interaction feedback or cosmological IVP is added.

After a first H photoabsorption the primary electron's initial kinetic energy is e_j = E_gamma,j-I_H, with original fixed source I_H=13.60 eV. H(1s)->2p excitation energy from the NIST current electron-impact database: D=10.1988 eV; NIST cross section sigma_2p(e) is 12-point linearly interpolated BE-scaled theoretical source on e in [11,21] eV, sigma_2p in m^2. The measured H collision ionization sigma_i(e) is linearly interpolated from 26 primary Shah (1987) measurements on [14.6,21.4] eV; it is NOT defined as a physical zero outside. Relative electron speed v(e)=sqrt(2 e eV_to_J/m_e) [m/s] assumes stationary H target, NR, no acceleration. The two source-matched microscopic first-inelastic rates are q_i=n_H v sigma_i and q_p=n_H v sigma_2p [s^-1].

## Constructive formula

For the common overlapping support 14.6 <= e_j <= 20.99 eV and observation duration d=T-s_j>0, treat ionization and 2p excitation as two mutually exclusive absorbing first-inelastic channels with q=q_i+q_p. Conditional on photoabsorption at u from source birth, first subsequent electron event m in {i,p} occurs before T with probability q_m/q[1-exp(-q(T-u))]. Hence (for d>0):

P_m(d|j)=a_j ∫_0^d exp(-k_j τ) [q_m/q] (1-exp(-q(d-τ))) dτ.

For k != q this equals

P_m=(a_j q_m/q)[(1-exp(-k d))/k - (exp(-q d)-exp(-k d))/(k-q)].

For k=q use continuous limit: the second bracket equals [(1-exp(-k d))/k - d exp(-k d)]. For d<=0 set zero. Numerical production uses 24-point Gauss-Legendre quadrature over the physical time ordering; independent SciPy quad checks selected original source energies.

Sum identity: P_i+P_p <= a_j(1-exp(-k_j d))/k_j = P_firstH. For q_i,q_p>0, P_i/P_p=q_i/q_p for each original ray. As d -> 0, P_m = (a_j q_m d^2)/2 + O(d^3). New source moments N_m(T)=Σ_j Σ_birth w_j P_m(T-s_j) [m^-3]. Source-matched energy transfers are 13.60 eV per H ionization and 10.1988 eV per 2p excitation; max residual electron e after the first 2p is 10.7912eV, and after ionization is 7.39eV. These are not a gas temperature or thermal deposition rate.

## Supported classes / precise gaps

**Measured overlap:** e>=14.6 eV with Shah original total ionization cross section and NIST BE-scaled 2p model. This defines a physically input-qualified **conditional two-channel model**, not a claim that all inelastic processes were included.

**Ionization forbidden:** 11<=e<13.60eV, NIST 2p is supported while H ionization is energetically forbidden. Other excitation processes, elastic transport and gas feedback remain unspecified. Our isolated 2p-only process produces a channel-model upper scenario, not guaranteed observed Ly-alpha photons.

**Ionization data gap:** 13.60<=e<14.6eV, 2p source is available but Shah ionization is unmeasured. We report only 2p-only **upper scenario**, not a competing event rate. This range must not be silently treated as true sigma_ion=0.

**Potential repeated 2p excitation:** if e>=2D=20.3976eV, a second 2p excitation is energetically possible. There are 192 original source energy atoms satisfying this condition. The residual electron kinetic energy after the first excitation is below 11 eV even for e_max=20.99eV, beyond the current NIST numerical table. Therefore the PHYS14 model stops at the first inelastic event. It does NOT prove that one primary electron can produce at most one Ly-alpha photon.

**Radiation:** a 2p excitation creates an excited atom with 10.1988 eV excitation energy, which can radiatively produce Ly-alpha on decay. The reported equivalent energy D N_2p eV_to_J is a candidate photon emission reservoir, **not observed Ly-alpha, escaped radiation, photon reabsorption, or a solved Einstein-Boltzmann intensity**. There is no physical global K, ionization IVP, or electron energy distribution closure.

## Validation acceptance

- Parent original full PR138 SHA256 and 46/46 member manifest exact; source 6400 unchanged and PHYS13 27/27 photon first-absorption+Shah ion-only parity.
- 26 focused unittest cases in regular and Python -O; frozen original NIST transcript SHA + tamper rejection, energy threshold, negative-time, vacuum, branch proportionality, 2-event small-time asymptotic, energy conservation and nonnegative event counts.
- Wolfram direct-integral vs closed form =0, branching ratio identity=0, small-time coefficient a q_m/2. Same author, not distinct-author R06/C09.
- Separate SciPy QUADPACK integral comparisons at source energies; no requirement to enlarge tolerance for production.
