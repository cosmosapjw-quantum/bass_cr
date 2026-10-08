//! Standalone research integration of the source-pinned photon and IGM point interfaces.
//! No evolution, CR-on source or FT03 theorem transfer is provided.
use rei_microphysics::igm_state::IgmGasState;
use rei_microphysics::igm_thermal::IgmPointRhs;
use rei_microphysics::{AtomicProvider, ForwardError};
#[derive(Clone, Copy, Debug)]
pub struct CountPerH {
    pub energy_ev: f64,
    pub photons_per_h: f64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CrMode {
    Off,
    On,
}
#[derive(Clone, Copy, Debug)]
pub struct PointContext {
    pub n_h_cm3: f64,
    pub n_he_cm3: f64,
    pub hubble_s: f64,
    pub t_cmb_k: f64,
}
#[derive(Clone, Debug)]
pub struct BridgePoint {
    pub gas: IgmPointRhs,
    pub gamma_s: [f64; 3],
    pub heat_per_absorber_erg_s: [f64; 3],
    pub photons_dt_per_h_s: Vec<f64>,
    pub absorbed_energy_erg_per_h_s: f64,
    pub cr_source: [f64; 4],
}

fn nn(x: f64) -> Result<f64, ForwardError> {
    if x == 0.0 || (x.is_normal() && x > 0.0) {
        Ok(x)
    } else {
        Err(ForwardError::InvalidInput(
            "CRF0_PHOTON_OR_ARITHMETIC_DOMAIN",
        ))
    }
}
fn mul(a: f64, b: f64) -> Result<f64, ForwardError> {
    nn(a)?;
    nn(b)?;
    if a == 0.0 || b == 0.0 {
        return Ok(0.0);
    }
    let v = nn(a * b)?;
    if v == 0.0 {
        Err(ForwardError::InvalidInput(
            "CRF0_POSITIVE_PRODUCT_UNDERFLOW",
        ))
    } else {
        Ok(v)
    }
}
fn add(a: f64, b: f64) -> Result<f64, ForwardError> {
    nn(a + b)
}

/// Immutable photon-to-IGM point evaluation in the GAS REST FRAME.
/// Photon numbers are bin-integrated/already angular-weighted counts per H.
/// No extra a^-3, 4*pi, dE or time-step factor is applied. No source injection.
/// This function has no CR provider handle; CR-on is rejected, not zero-filled.
fn photon_igm_core(
    mode: CrMode,
    state: &IgmGasState,
    ctx: PointContext,
    nodes: &[CountPerH],
    photo: &AtomicProvider,
) -> Result<BridgePoint, ForwardError> {
    if mode != CrMode::Off {
        return Err(ForwardError::MissingAuthority("CR_ON_SCOPE_NOT_ADMITTED"));
    }
    let _eos = state.eos(ctx.n_h_cm3, ctx.n_he_cm3)?;
    let c = rei_microphysics::HHeModel::controlled_fixture();
    let [x, y, z] = state.fractions;
    let nabs = [
        mul(ctx.n_h_cm3, 1.0 - x)?,
        mul(ctx.n_he_cm3, 1.0 - (y + z))?,
        mul(ctx.n_he_cm3, y)?,
    ];
    let species = [
        rei_microphysics::Absorber::HI,
        rei_microphysics::Absorber::HeI,
        rei_microphysics::Absorber::HeII,
    ];
    let mut gamma = [0.0; 3];
    let mut heat = [0.0; 3];
    let mut loss = Vec::with_capacity(nodes.len());
    let mut energy = 0.0;
    for node in nodes {
        nn(node.photons_per_h)?;
        if !node.energy_ev.is_normal() || node.energy_ev <= 0.0 {
            return Err(ForwardError::InvalidInput("CRF0_PHOTON_ENERGY"));
        }
        let nphot = mul(ctx.n_h_cm3, node.photons_per_h)?;
        let mut loss_k = 0.0;
        for i in 0..3 {
            // Domain checks are retained even for zero photons or absent absorbers.
            let sigma = photo.cross_section(species[i], node.energy_ev)?;
            if sigma == 0.0 {
                continue;
            } // inactive channel, not a negative heat product
            let excess = nn(node.energy_ev - c.threshold_ev[i])?;
            let g = mul(mul(c.c_cm_s, nphot)?, sigma)?;
            gamma[i] = add(gamma[i], g)?;
            heat[i] = add(heat[i], mul(mul(g, excess)?, c.ev_erg)?)?;
            let event_per_h = mul(mul(mul(c.c_cm_s, nabs[i])?, sigma)?, node.photons_per_h)?;
            loss_k = add(loss_k, event_per_h)?;
        }
        energy = add(energy, mul(mul(loss_k, node.energy_ev)?, c.ev_erg)?)?;
        loss.push(if loss_k == 0.0 { 0.0 } else { -loss_k });
    }
    let gas = rei_microphysics::igm_thermal::igm_point_rhs(
        state,
        ctx.n_h_cm3,
        ctx.n_he_cm3,
        ctx.hubble_s,
        ctx.t_cmb_k,
        rei_microphysics::igm_thermal::IgmPhotoInput {
            gamma_s: gamma,
            heat_erg_per_absorber_s: heat,
        },
    )?;
    Ok(BridgePoint {
        gas,
        gamma_s: gamma,
        heat_per_absorber_erg_s: heat,
        photons_dt_per_h_s: loss,
        absorbed_energy_erg_per_h_s: energy,
        cr_source: [0.0; 4],
    })
}

/// Deferred CR access boundary. Implementations must not load in their constructor.
/// The current adapter never admits CR-on, hence neither method is called.
/// Callers may supply instrumented witnesses; these are not atomic providers.
pub trait DeferredCrAccess {
    fn load(&mut self) -> Result<(), ForwardError>;
    fn source_callback(&mut self) -> Result<[f64; 4], ForwardError>;
}
struct UnavailableCr;
impl DeferredCrAccess for UnavailableCr {
    fn load(&mut self) -> Result<(), ForwardError> {
        Err(ForwardError::MissingAuthority("CR_ON_SCOPE_NOT_ADMITTED"))
    }
    fn source_callback(&mut self) -> Result<[f64; 4], ForwardError> {
        Err(ForwardError::MissingAuthority("CR_ON_SCOPE_NOT_ADMITTED"))
    }
}
pub fn photon_igm_point(
    mode: CrMode,
    state: &IgmGasState,
    ctx: PointContext,
    nodes: &[CountPerH],
    photo: &AtomicProvider,
) -> Result<BridgePoint, ForwardError> {
    photon_igm_with_deferred_cr(mode, state, ctx, nodes, photo, &mut UnavailableCr)
}
/// Observed entrypoint: the CR switch is resolved before any provider access.
/// Source and error values from the baseline are not changed by adding zero.
/// An error returns no partially updated gas or photon state.
pub fn photon_igm_with_deferred_cr(
    mode: CrMode,
    state: &IgmGasState,
    ctx: PointContext,
    nodes: &[CountPerH],
    photo: &AtomicProvider,
    _cr: &mut impl DeferredCrAccess,
) -> Result<BridgePoint, ForwardError> {
    photon_igm_core(mode, state, ctx, nodes, photo)
}
