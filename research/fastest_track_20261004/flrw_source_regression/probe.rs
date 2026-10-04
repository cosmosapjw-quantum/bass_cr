//! Calls the pinned receiver's public functions; does not integrate a history.
use rei_microphysics::*;

fn local_row(id: usize, mut m: HHeModel, fractions: [f64; 3], photons: [f64; 3]) {
    let ne = m.n_h_cm3 * fractions[0] + m.n_he_cm3 * (fractions[1] + 2.0 * fractions[2]);
    let s = HHeState {
        fractions,
        u_erg_cm3: 1.5 * m.kb_erg_k * 1e4 * (m.n_h_cm3 + m.n_he_cm3 + ne),
        photon_cm3: photons,
        escaped_erg_cm3: 0.0,
    };
    // Keep all original model constants; only the declared test channels vary.
    m.c_cm_s = C_LIGHT;
    let r = hhe_rhs(&m, &s).unwrap();
    println!("L\t{id}\t{{\"n\":{:?},\"x\":{:?},\"u\":{:?},\"photons\":{:?},\"alpha\":{:?},\"beta\":{:?},\"sigma\":{:?},\"c\":{:?},\"kb\":{:?},\"ev\":{:?},\"chi\":{:?},\"energy\":{:?},\"ne\":{:?},\"temperature\":{:?},\"rhs\":{:?},\"photo\":{:?},\"collision\":{:?},\"recombination\":{:?},\"escape\":{:?}}}",
        [m.n_h_cm3,m.n_he_cm3],s.fractions,s.u_erg_cm3,s.photon_cm3,
        m.alpha_cm3_s,m.beta_cm3_s,m.sigma_cm2,m.c_cm_s,m.kb_erg_k,m.ev_erg,
        m.threshold_ev,m.photon_energy_ev,m.electron_density(&s).unwrap(),
        m.temperature(&s).unwrap(),r.derivative,r.photo_per_cm3_s,
        r.collision_per_cm3_s,r.recombination_per_cm3_s,r.escaped_energy_rate);
}

fn main() {
    let mut id = 0;
    for nh in [2f64.powi(-10), 2f64.powi(-6)] {
        for x in [0.0, 0.25, 0.5, 1.0] {
            for mode in 0..3 {
                let mut m = HHeModel::controlled_fixture();
                m.n_h_cm3 = nh;
                m.n_he_cm3 = 0.0;
                m.alpha_cm3_s[1..].fill(0.0);
                m.beta_cm3_s[1..].fill(0.0);
                if mode < 2 {
                    m.beta_cm3_s[0] = 0.0;
                }
                if mode == 0 {
                    m.sigma_cm2 = [[0.0; 3]; 3];
                }
                local_row(id, m, [x, 0.0, 0.0], [2e-5, 2e-6, 2e-7]);
                id += 1;
            }
        }
        for x0 in [0.25, 0.5, 1.0] {
            for t in [0.0, 2f64.powi(40), 2f64.powi(55)] {
                let mut m = HHeModel::controlled_fixture();
                m.n_h_cm3 = nh;
                m.n_he_cm3 = 0.0;
                m.beta_cm3_s = [0.0; 3];
                m.sigma_cm2 = [[0.0; 3]; 3];
                m.alpha_cm3_s[1..].fill(0.0);
                let x = x0 / (1.0 + m.alpha_cm3_s[0] * nh * x0 * t);
                // Evaluate the RHS at exact-curve samples; no stepping/solver.
                local_row(id, m, [x, 0.0, 0.0], [0.0; 3]);
                id += 1;
                println!("R\t{id}\t{{\"nh\":{nh:?},\"alpha\":{:?},\"x0\":{x0:?},\"t\":{t:?},\"x\":{x:?}}}",m.alpha_cm3_s[0]);
            }
        }
    }
    for x in [0.0, 0.25, 0.5, 1.0] {
        let m = HHeModel::controlled_fixture();
        local_row(id, m, [x, 0.25, 0.125], [2e-5, 2e-6, 2e-7]);
        id += 1;
    }
    let provider = AtomicProvider::default();
    for scale in [0.25, 0.5, 1.0] {
        for n in [[1e-4, 8e-6, 3e-6], [0.0; 3], [1e-4, 0.0, 0.0]] {
            for energy in [[13.7, 24.7, 54.5], [20.0, 40.0, 80.0]] {
                for empty in [false, true] {
                    let counts = if empty { [0.0; 3] } else { [4e63, 2e63, 1e63] };
                    let nodes: [PhotonNode; 3] = std::array::from_fn(|g| PhotonNode {
                        energy_ev: energy[g],
                        n_comoving_per_cmpc3: counts[g],
                    });
                    let p = homogeneous_photo_rates(&provider, n, scale, &nodes).unwrap();
                    let sigma: [[f64; 3]; 3] = [Absorber::HI, Absorber::HeI, Absorber::HeII]
                        .map(|a| energy.map(|e| provider.cross_section(a, e).unwrap()));
                    let mut m = HHeModel::controlled_fixture();
                    m.alpha_cm3_s = [0.0; 3];
                    m.beta_cm3_s = [0.0; 3];
                    m.sigma_cm2 = sigma;
                    m.photon_energy_ev = energy;
                    m.n_h_cm3 = if n[0] > 0.0 { n[0] } else { 1.0 };
                    m.n_he_cm3 = n[1] + n[2];
                    let fractions = [
                        if n[0] > 0.0 { 0.0 } else { 1.0 },
                        if m.n_he_cm3 > 0.0 {
                            n[2] / m.n_he_cm3
                        } else {
                            0.0
                        },
                        0.0,
                    ];
                    let volume = (scale * MPC_CM).powi(3);
                    let s = HHeState {
                        fractions,
                        u_erg_cm3: 1e-12,
                        photon_cm3: counts.map(|v| v / volume),
                        escaped_erg_cm3: 0.0,
                    };
                    let r = hhe_rhs(&m, &s).unwrap();
                    println!("P\t{id}\t{{\"a\":{scale:?},\"mpc\":{MPC_CM:?},\"c\":{C_LIGHT:?},\"n\":{n:?},\"energy\":{energy:?},\"counts\":{counts:?},\"sigma\":{sigma:?},\"gamma\":{:?},\"events\":{:?},\"heat\":{:?},\"binding\":{:?},\"loss\":{:?},\"absorbed\":{:?},\"hhe_photo\":{:?},\"hhe_photon_rhs\":{:?}}}",p.gamma_per_s,p.events_proper_per_cm3_s,p.heat_erg_per_cm3_s,p.binding_erg_per_cm3_s,p.photon_loss_comoving_per_cmpc3_s,p.absorbed_erg_per_cm3_s,r.photo_per_cm3_s,[r.derivative[4],r.derivative[5],r.derivative[6]]);
                    id += 1;
                }
            }
        }
    }
    // Manufactured N_nu=A exp(-nu), fixed physical edges. Upper inflow is
    // explicitly supplied through the source argument; the API has no edge hook.
    let edges = [1.0f64, 2.0, 4.0, 8.0, 16.0];
    let table = PchipTable::new(
        vec![-1.0, 1.0],
        [vec![0.0], vec![0.0], vec![0.0], vec![0.0]],
    )
    .unwrap();
    for amp in [1.0, 1048576.0] {
        let n: [f64; 4] =
            std::array::from_fn(|g| amp * ((-edges[g]).exp() - (-edges[g + 1]).exp()));
        let h = 2f64.powi(-30);
        let flux = edges.map(|e| h * e * amp * (-e).exp());
        for mode in 0..3 {
            let coefficients = if mode == 2 {
                [1.0; 4]
            } else {
                std::array::from_fn(|g| flux[g] / (h * n[g]))
            };
            let p = GroupParams {
                redshift: 0.0,
                n_h_proper_per_cm3: 1e-4,
                n_he_proper_per_cm3: 0.0,
                hubble_per_s: h,
                sigma_hi_cm2: [0.0; 4],
                sigma_hei_cm2: [0.0; 4],
                sigma_heii_cm2: [0.0; 4],
                redshift_coeff: coefficients,
                source_fraction: [1.0; 4],
                lowgroup_log_opacity: [table.clone(), table.clone()],
            };
            let s = State {
                n_comoving_per_cmpc3: n,
                x_hii: 0.5,
                helium: [1.0, 0.0, 0.0],
                u_erg_per_cm3: 1e-12,
                gamma_hi_per_s: 1e-12,
            };
            let source = [0.0, 0.0, 0.0, if mode == 0 { flux[4] } else { 0.0 }];
            let rhs = photon_rates(&s, &source, &p).unwrap();
            println!("G\t{id}\t{{\"amp\":{amp:?},\"edges\":{edges:?},\"h\":{h:?},\"mode\":{mode},\"n\":{n:?},\"flux\":{flux:?},\"coeff\":{coefficients:?},\"source\":{source:?},\"kappa\":{:?},\"rhs\":{rhs:?},\"c\":{C_LIGHT:?},\"mpc\":{MPC_CM:?}}}",opacity_cMpc_inv(&s,&p).unwrap());
            id += 1;
        }
        let s = State {
            n_comoving_per_cmpc3: [0.0; 4],
            x_hii: 0.5,
            helium: [1.0, 0.0, 0.0],
            u_erg_per_cm3: 1e-12,
            gamma_hi_per_s: 1e-12,
        };
        let p = GroupParams {
            redshift: 0.0,
            n_h_proper_per_cm3: 1e-4,
            n_he_proper_per_cm3: 0.0,
            hubble_per_s: h,
            sigma_hi_cm2: [1e-18; 4],
            sigma_hei_cm2: [0.0; 4],
            sigma_heii_cm2: [0.0; 4],
            redshift_coeff: [1.0; 4],
            source_fraction: [1.0; 4],
            lowgroup_log_opacity: [table.clone(), table.clone()],
        };
        let source = [amp, 2.0 * amp, 3.0 * amp, 4.0 * amp];
        println!(
            "E\t{id}\t{{\"source\":{source:?},\"rhs\":{:?},\"gamma\":{:?}}}",
            photon_rates(&s, &source, &p).unwrap(),
            gamma_species(&s, &p).group_hi_per_s
        );
        id += 1;
    }
}
