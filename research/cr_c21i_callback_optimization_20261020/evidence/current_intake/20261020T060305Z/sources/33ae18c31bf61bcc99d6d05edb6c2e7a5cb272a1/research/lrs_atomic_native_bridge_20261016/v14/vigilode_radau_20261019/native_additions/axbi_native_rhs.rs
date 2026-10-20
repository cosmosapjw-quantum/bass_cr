//! Direct native reconstructed-node derivatives for opt-in external ODE adapters.
use super::*;
#[derive(Clone, Debug)]
pub struct NativeAbsorptionRates {
    pub number_dt: Vec<f64>,
    pub energy_ref_dt: Vec<f64>,
    /// Derivative of Uref - support_lo*N, accumulated directly at nodes.
    pub energy_offset_dt: Vec<f64>,
    pub photo: IgmPhotoInput,
    pub absorbed_per_h_s: [f64; 3],
    pub binding_ev_per_h_s: f64,
    pub heat_ev_per_h_s: f64,
}
impl PreparedAbsorption {
    /// No finite-step subtraction, attenuation, CFL, or state projection.
    pub fn native_rates(
        &self,
        absorber_cm3: [f64; 3],
        n_h_cm3: f64,
    ) -> Result<NativeAbsorptionRates, ForwardError> {
        if !absorber_cm3.iter().all(|&x| nonnegative(x)) || !n_h_cm3.is_finite() || n_h_cm3 <= 0.0 {
            return Err(bad("AXBI_COVARIANT_OPACITY_DOMAIN"));
        }
        let m = HHeModel::controlled_fixture();
        let cells = self.template.number.len();
        let mut r = NativeAbsorptionRates {
            number_dt: vec![0.; cells],
            energy_ref_dt: vec![0.; cells],
            energy_offset_dt: vec![0.; cells],
            photo: IgmPhotoInput::default(),
            absorbed_per_h_s: [0.; 3],
            binding_ev_per_h_s: 0.,
            heat_ev_per_h_s: 0.,
        };
        let mut cn = vec![0.; cells];
        let mut cu = vec![0.; cells];
        let mut co = vec![0.; cells];
        for node in &self.nodes {
            let mut total = 0.;
            for j in 0..3 {
                let photo = m.c_cm_s * n_h_cm3 * node.sigma[j] * node.number;
                r.photo.gamma_s[j] += photo;
                r.photo.heat_erg_per_absorber_s[j] += photo * node.excess_ev[j] * m.ev_erg;
                let event = m.c_cm_s * absorber_cm3[j] * node.sigma[j] * node.number;
                r.absorbed_per_h_s[j] += event;
                r.binding_ev_per_h_s += event * m.threshold_ev[j];
                r.heat_ev_per_h_s += event * node.excess_ev[j];
                total += event;
            }
            compensated_add(&mut r.number_dt[node.cell], &mut cn[node.cell], -total);
            compensated_add(
                &mut r.energy_ref_dt[node.cell],
                &mut cu[node.cell],
                -node.q * total,
            );
            compensated_add(
                &mut r.energy_offset_dt[node.cell],
                &mut co[node.cell],
                -(node.q - self.template.support_lo[node.cell]) * total,
            );
        }
        if !r
            .number_dt
            .iter()
            .chain(&r.energy_ref_dt)
            .chain(&r.energy_offset_dt)
            .all(|v| v.is_finite())
            || !r
                .photo
                .gamma_s
                .iter()
                .chain(&r.photo.heat_erg_per_absorber_s)
                .chain(&r.absorbed_per_h_s)
                .all(|&v| nonnegative(v))
            || !nonnegative(r.binding_ev_per_h_s)
            || !nonnegative(r.heat_ev_per_h_s)
        {
            return Err(bad("AXBI_NATIVE_RHS_NONFINITE"));
        }
        Ok(r)
    }
}

/// Segment-scoped geometry and Jacobian-local photon reconstruction cache.
/// No cached cell may be reused after its state or support changes.
pub struct NativeCellCache<'a> {
    transport: &'a CovariantTransport,
    base: PhotonState,
    cells: Vec<PreparedCell>,
    ray_scales: Vec<f64>,
}
impl CovariantTransport {
    pub fn native_cell_cache<'a>(&'a self, state: &PhotonState, now: &GeometrySnapshot)
        -> Result<NativeCellCache<'a>, ForwardError> {
        self.validate_state(state)?;
        let ray_scales = self.ray_geometry(now)?.iter().map(|r| r.scale).collect::<Vec<_>>();
        let cells = (0..self.cell_count()).map(|k| prepare_cell(k, state, ray_scales[k / self.n_energy()])).collect::<Result<Vec<_>, _>>()?;
        Ok(NativeCellCache { transport: self, base: state.clone(), cells, ray_scales })
    }
}
impl NativeCellCache<'_> {
    pub fn prepare(&self, state: &PhotonState, changed: Option<usize>) -> Result<PreparedAbsorption, ForwardError> {
        self.transport.validate_state(state)?;
        if changed.is_some_and(|k| k >= self.cells.len()) { return Err(bad("NATIVE_CACHE_CHANGED_CELL")); }
        for k in 0..self.cells.len() {
            if state.support_lo[k] != self.base.support_lo[k] || state.support_hi[k] != self.base.support_hi[k]
                || (changed != Some(k) && (state.number[k] != self.base.number[k] || state.energy_ref[k] != self.base.energy_ref[k])) {
                return Err(bad("NATIVE_CACHE_STALE_CELL_OR_SUPPORT"));
            }
        }
        let replacement = changed.map(|k| prepare_cell(k,state,self.ray_scales[k / self.transport.n_energy()])).transpose()?;
        let mut prepared = PreparedAbsorption { template: state.clone(), nodes: Vec::new(), diagnostics: QuadratureDiagnostics::default() };
        for k in 0..self.cells.len() {
            let cell = if changed == Some(k) { replacement.as_ref().unwrap() } else { &self.cells[k] };
            let d = &cell.diagnostics;
            prepared.diagnostics.max_count_relative_defect = prepared.diagnostics.max_count_relative_defect.max(d.max_count_relative_defect);
            prepared.diagnostics.max_energy_relative_defect = prepared.diagnostics.max_energy_relative_defect.max(d.max_energy_relative_defect);
            prepared.diagnostics.max_asymptotic_mean_defect_ev = prepared.diagnostics.max_asymptotic_mean_defect_ev.max(d.max_asymptotic_mean_defect_ev);
            prepared.diagnostics.omitted_tail_number_bound_per_h += d.omitted_tail_number_bound_per_h;
            prepared.diagnostics.omitted_tail_energy_bound_ev_per_h += d.omitted_tail_energy_bound_ev_per_h;
            prepared.diagnostics.omitted_tail_endpoint_moment_bound_ev_per_h += d.omitted_tail_endpoint_moment_bound_ev_per_h;
            prepared.nodes.extend(cell.nodes.iter().cloned());
        }
        Ok(prepared)
    }
}
