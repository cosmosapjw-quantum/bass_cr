//! Standalone C21I linear algebra prototype; not a C21H ODE backend.
//!
//! Ordering is (tau[M], gas[G], ledger[15]), G=2 or 4. The supplied binary64
//! Jacobian is J=[[0,A,0],[B,C,0],[P,Q,0]]. This crate does not approximate gas
//! derivatives, remove ledger state, or change an integrator's error norm.
//! All matrices are row-major. Arithmetic uses ordinary f64 operations without
//! fast-math, explicit FMA, clipping, regularization, or a fallback solver.

use std::fmt;

pub const LEDGERS: usize = 15;

#[derive(Debug, Clone, PartialEq)]
pub enum Error {
    Dimension(&'static str),
    NonFinite(&'static str),
    Singular { pivot: usize },
    IllConditioned { schur_rcond: f64, minimum: f64 },
    ResidualTooLarge { measured: f64, maximum: f64 },
    InvalidOptions,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for Error {}

type Result<T> = std::result::Result<T, Error>;

fn finite(value: f64, context: &'static str) -> Result<f64> {
    if value.is_finite() { Ok(value) } else { Err(Error::NonFinite(context)) }
}

fn vector(values: &[f64], length: usize, name: &'static str) -> Result<()> {
    if values.len() != length { return Err(Error::Dimension(name)); }
    if values.iter().any(|v| !v.is_finite()) { return Err(Error::NonFinite(name)); }
    Ok(())
}

#[derive(Clone, Debug)]
pub struct BlockJacobian {
    m: usize,
    g: usize,
    n: usize,
    a: Vec<f64>,
    b: Vec<f64>,
    c: Vec<f64>,
    p: Vec<f64>,
    q: Vec<f64>,
}

impl BlockJacobian {
    /// Own immutable, finite matrices. Empty cohort sets are allowed; G and L
    /// retain the exact gas/ledger dimensions of this prototype's contract.
    pub fn new(m: usize, g: usize, a: Vec<f64>, b: Vec<f64>, c: Vec<f64>,
               p: Vec<f64>, q: Vec<f64>) -> Result<Self> {
        if g != 2 && g != 4 { return Err(Error::Dimension("gas must be 2 or 4")); }
        let n = m.checked_add(g).and_then(|v| v.checked_add(LEDGERS))
            .ok_or(Error::Dimension("dimension overflow"))?;
        let mg = m.checked_mul(g).ok_or(Error::Dimension("M*G overflow"))?;
        let lm = m.checked_mul(LEDGERS).ok_or(Error::Dimension("L*M overflow"))?;
        vector(&a, mg, "A")?;
        vector(&b, mg, "B")?;
        vector(&c, g * g, "C")?;
        vector(&p, lm, "P")?;
        vector(&q, LEDGERS * g, "Q")?;
        Ok(Self { m, g, n, a, b, c, p, q })
    }

    pub fn cohorts(&self) -> usize { self.m }
    pub fn gases(&self) -> usize { self.g }
    pub fn dimension(&self) -> usize { self.n }
    pub fn a(&self) -> &[f64] { &self.a }
    pub fn b(&self) -> &[f64] { &self.b }
    pub fn c(&self) -> &[f64] { &self.c }
    pub fn p(&self) -> &[f64] { &self.p }
    pub fn q(&self) -> &[f64] { &self.q }
    pub fn stored_f64(&self) -> usize {
        self.a.len() + self.b.len() + self.c.len() + self.p.len() + self.q.len()
    }

    pub fn jvp(&self, input: &[f64]) -> Result<Vec<f64>> {
        let mut output = vec![0.0; self.n];
        self.jvp_into(input, &mut output)?;
        Ok(output)
    }

    /// Reusable caller-owned output; safe Rust prevents input/output aliasing.
    /// Every output is written, including all 15 ledger derivatives.
    pub fn jvp_into(&self, input: &[f64], output: &mut [f64]) -> Result<()> {
        vector(input, self.n, "JVP input")?;
        if output.len() != self.n { return Err(Error::Dimension("JVP output")); }
        for i in 0..self.m {
            let mut value = 0.0;
            for j in 0..self.g { value += self.a[i * self.g + j] * input[self.m + j]; }
            output[i] = finite(value, "JVP tau")?;
        }
        for i in 0..self.g {
            let mut value = 0.0;
            for j in 0..self.m { value += self.b[i * self.m + j] * input[j]; }
            for j in 0..self.g { value += self.c[i * self.g + j] * input[self.m + j]; }
            output[self.m + i] = finite(value, "JVP gas")?;
        }
        for i in 0..LEDGERS {
            let mut value = 0.0;
            for j in 0..self.m { value += self.p[i * self.m + j] * input[j]; }
            for j in 0..self.g { value += self.q[i * self.g + j] * input[self.m + j]; }
            output[self.m + self.g + i] = finite(value, "JVP ledger")?;
        }
        Ok(())
    }

    /// Diagnostic/reference materialization. The Schur path never calls this.
    pub fn dense_shifted(&self, shift: f64) -> Result<Vec<f64>> {
        finite(shift, "shift")?;
        let count = self.n.checked_mul(self.n).ok_or(Error::Dimension("dense size"))?;
        let mut w = vec![0.0; count];
        for i in 0..self.n { w[i * self.n + i] = 1.0; }
        for i in 0..self.m {
            for j in 0..self.g { w[i * self.n + self.m + j] = -shift * self.a[i * self.g + j]; }
        }
        for i in 0..self.g {
            for j in 0..self.m { w[(self.m + i) * self.n + j] = -shift * self.b[i * self.m + j]; }
            for j in 0..self.g {
                w[(self.m + i) * self.n + self.m + j] -= shift * self.c[i * self.g + j];
            }
        }
        for i in 0..LEDGERS {
            let row = self.m + self.g + i;
            for j in 0..self.m { w[row * self.n + j] = -shift * self.p[i * self.m + j]; }
            for j in 0..self.g { w[row * self.n + self.m + j] = -shift * self.q[i * self.g + j]; }
        }
        vector(&w, count, "shifted dense matrix")?;
        Ok(w)
    }

    /// Full-space normwise backward error for the represented W=I-shift*J.
    /// Finite inputs with unrepresentable intermediate arithmetic are rejected;
    /// this implementation does not silently normalize an infinite denominator.
    pub fn backward_error(&self, shift: f64, solution: &[f64], rhs: &[f64]) -> Result<f64> {
        finite(shift, "shift")?;
        vector(solution, self.n, "residual solution")?;
        vector(rhs, self.n, "residual rhs")?;
        let mut residual: f64 = 0.0;
        let mut matrix_norm: f64 = 0.0;
        let mut row = |value: f64, norm: f64, rhs_value: f64| -> Result<()> {
            residual = residual.max(finite(value - rhs_value, "full residual")?.abs());
            matrix_norm = matrix_norm.max(finite(norm, "matrix infinity norm")?);
            Ok(())
        };
        for i in 0..self.m {
            let mut value = solution[i];
            let mut norm = 1.0;
            for j in 0..self.g {
                let coefficient = -shift * self.a[i * self.g + j];
                value += coefficient * solution[self.m + j];
                norm += coefficient.abs();
            }
            row(value, norm, rhs[i])?;
        }
        for i in 0..self.g {
            let mut value = 0.0;
            let mut norm = 0.0;
            for j in 0..self.m {
                let coefficient = -shift * self.b[i * self.m + j];
                value += coefficient * solution[j]; norm += coefficient.abs();
            }
            for j in 0..self.g {
                let coefficient = (if i == j { 1.0 } else { 0.0 }) - shift * self.c[i * self.g + j];
                value += coefficient * solution[self.m + j]; norm += coefficient.abs();
            }
            row(value, norm, rhs[self.m + i])?;
        }
        for i in 0..LEDGERS {
            let index = self.m + self.g + i;
            let mut value = solution[index];
            let mut norm = 1.0;
            for j in 0..self.m {
                let coefficient = -shift * self.p[i * self.m + j];
                value += coefficient * solution[j]; norm += coefficient.abs();
            }
            for j in 0..self.g {
                let coefficient = -shift * self.q[i * self.g + j];
                value += coefficient * solution[self.m + j]; norm += coefficient.abs();
            }
            row(value, norm, rhs[index])?;
        }
        let xnorm = solution.iter().fold(0.0_f64, |a, b| a.max(b.abs()));
        let bnorm = rhs.iter().fold(0.0_f64, |a, b| a.max(b.abs()));
        let denominator = finite(matrix_norm * xnorm + bnorm, "residual denominator")?;
        if denominator == 0.0 {
            if residual == 0.0 { return Ok(0.0); }
            return Err(Error::NonFinite("zero residual denominator with nonzero residual"));
        }
        finite(residual / denominator, "backward error")
    }

    pub fn solve_shifted(&self, shift: f64, rhs: &[f64], options: SolveOptions,
                         cache: Option<&mut ExactFactorCache>) -> Result<SolveReport> {
        finite(shift, "shift")?;
        vector(rhs, self.n, "solve rhs")?;
        options.validate()?;
        match cache {
            Some(cache) => {
                let (factor, hit) = cache.factor(self, shift)?;
                self.solve_factored(shift, rhs, options, factor, hit)
            }
            None => {
                let factor = SchurFactor::new(self, shift)?;
                self.solve_factored(shift, rhs, options, &factor, false)
            }
        }
    }

    fn solve_factored(&self, shift: f64, rhs: &[f64], options: SolveOptions,
                      factor: &SchurFactor, hit: bool) -> Result<SolveReport> {
        if let Some(minimum) = options.minimum_schur_rcond {
            if factor.rcond < minimum {
                return Err(Error::IllConditioned { schur_rcond: factor.rcond, minimum });
            }
        }
        let mut gas_rhs = vec![0.0; self.g];
        for i in 0..self.g {
            let mut value = rhs[self.m + i];
            for j in 0..self.m { value += (shift * self.b[i * self.m + j]) * rhs[j]; }
            gas_rhs[i] = finite(value, "reduced rhs")?;
        }
        let gas = factor.lu.solve(&gas_rhs)?;
        let mut solution = rhs.to_vec();
        solution[self.m..self.m + self.g].copy_from_slice(&gas);
        for i in 0..self.m {
            let mut value = rhs[i];
            for j in 0..self.g { value += (shift * self.a[i * self.g + j]) * gas[j]; }
            solution[i] = finite(value, "tau reconstruction")?;
        }
        for i in 0..LEDGERS {
            let index = self.m + self.g + i;
            let mut value = rhs[index];
            for j in 0..self.m { value += (shift * self.p[i * self.m + j]) * solution[j]; }
            for j in 0..self.g { value += (shift * self.q[i * self.g + j]) * gas[j]; }
            solution[index] = finite(value, "ledger reconstruction")?;
        }
        let backward_error = self.backward_error(shift, &solution, rhs)?;
        if backward_error > options.max_backward_error {
            return Err(Error::ResidualTooLarge { measured: backward_error, maximum: options.max_backward_error });
        }
        Ok(SolveReport { solution, backward_error, schur_rcond_inf: factor.rcond, cache_hit: hit })
    }
}

#[derive(Clone, Copy, Debug)]
pub struct SolveOptions {
    pub max_backward_error: f64,
    /// Explicit optional policy, not a regularization or a forward-error bound.
    pub minimum_schur_rcond: Option<f64>,
}
impl Default for SolveOptions {
    fn default() -> Self { Self { max_backward_error: 1e-13, minimum_schur_rcond: None } }
}
impl SolveOptions {
    fn validate(self) -> Result<()> {
        if !self.max_backward_error.is_finite() || self.max_backward_error < 0.0 { return Err(Error::InvalidOptions); }
        if let Some(v) = self.minimum_schur_rcond {
            if !v.is_finite() || !(0.0..=1.0).contains(&v) { return Err(Error::InvalidOptions); }
        }
        Ok(())
    }
}

#[derive(Debug)]
pub struct SolveReport {
    pub solution: Vec<f64>,
    pub backward_error: f64,
    /// Computed from ||S||_inf and solves for the G columns of S^-1.
    /// This describes the reduced Schur matrix, not the full W condition number.
    pub schur_rcond_inf: f64,
    pub cache_hit: bool,
}

#[derive(Debug)]
struct SmallLu { g: usize, values: Vec<f64>, pivots: Vec<usize> }

impl SmallLu {
    fn factor(mut values: Vec<f64>, g: usize) -> Result<Self> {
        vector(&values, g * g, "Schur matrix")?;
        let mut pivots = vec![0; g];
        for k in 0..g {
            let mut pivot = k;
            for i in k + 1..g {
                if values[i * g + k].abs() > values[pivot * g + k].abs() { pivot = i; }
            }
            if values[pivot * g + k] == 0.0 { return Err(Error::Singular { pivot: k }); }
            pivots[k] = pivot;
            if pivot != k { for j in 0..g { values.swap(k * g + j, pivot * g + j); } }
            for i in k + 1..g {
                values[i * g + k] = finite(values[i * g + k] / values[k * g + k], "Schur LU multiplier")?;
                for j in k + 1..g {
                    values[i * g + j] = finite(values[i * g + j] - values[i * g + k] * values[k * g + j], "Schur LU update")?;
                }
            }
        }
        Ok(Self { g, values, pivots })
    }

    fn solve(&self, rhs: &[f64]) -> Result<Vec<f64>> {
        vector(rhs, self.g, "Schur solve rhs")?;
        let mut x = rhs.to_vec();
        // Apply the final row permutation before triangular substitution.
        for k in 0..self.g { x.swap(k, self.pivots[k]); }
        for i in 0..self.g {
            let mut value = x[i];
            for j in 0..i { value -= self.values[i * self.g + j] * x[j]; }
            x[i] = finite(value, "Schur forward solve")?;
        }
        for i in (0..self.g).rev() {
            let mut value = x[i];
            for j in i + 1..self.g { value -= self.values[i * self.g + j] * x[j]; }
            x[i] = finite(value / self.values[i * self.g + i], "Schur backward solve")?;
        }
        Ok(x)
    }
}

#[derive(Debug)]
struct SchurFactor { lu: SmallLu, rcond: f64 }

impl SchurFactor {
    fn new(block: &BlockJacobian, shift: f64) -> Result<Self> {
        let g = block.g;
        let mut s = vec![0.0; g * g];
        for i in 0..g {
            for j in 0..g {
                let mut value = (if i == j { 1.0 } else { 0.0 }) - shift * block.c[i * g + j];
                for k in 0..block.m {
                    // Algebraically shift^2 * B*A. Do not form shift^2 before
                    // multiplying zero entries; retain ordered binary64 sums.
                    value -= (shift * block.b[i * block.m + k]) * (shift * block.a[k * g + j]);
                }
                s[i * g + j] = finite(value, "Schur assembly")?;
            }
        }
        let norm = s.chunks(g).map(|row| row.iter().map(|v| v.abs()).sum::<f64>()).fold(0.0_f64, f64::max);
        finite(norm, "Schur norm")?;
        let lu = SmallLu::factor(s, g)?;
        let mut inverse_row_sums = vec![0.0; g];
        for j in 0..g {
            let mut unit = vec![0.0; g]; unit[j] = 1.0;
            let column = lu.solve(&unit)?;
            for i in 0..g { inverse_row_sums[i] = finite(inverse_row_sums[i] + column[i].abs(), "Schur inverse norm")?; }
        }
        let inverse_norm = inverse_row_sums.into_iter().fold(0.0_f64, f64::max);
        let condition = finite(norm * inverse_norm, "Schur condition product")?;
        let rcond = finite(1.0 / condition, "Schur rcond")?;
        Ok(Self { lu, rcond })
    }
}

#[derive(Debug)]
struct FactorKey { m: usize, g: usize, l: usize, shift: u64, abc: Vec<u64> }

impl FactorKey {
    fn new(block: &BlockJacobian, shift: f64) -> Self {
        Self { m: block.m, g: block.g, l: LEDGERS, shift: shift.to_bits(),
            abc: block.a.iter().chain(&block.b).chain(&block.c).map(|v| v.to_bits()).collect() }
    }
    fn matches(&self, block: &BlockJacobian, shift: f64) -> bool {
        self.m == block.m && self.g == block.g && self.l == LEDGERS && self.shift == shift.to_bits()
            && self.abc.len() == block.a.len() + block.b.len() + block.c.len()
            && self.abc.iter().copied().eq(block.a.iter().chain(&block.b).chain(&block.c).map(|v| v.to_bits()))
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct CacheStats {
    /// Valid factor requests; RHS and options are validated before this point.
    pub requests: usize,
    pub hits: usize,
    pub factorization_attempts: usize,
    pub factorization_failures: usize,
}

/// One-entry exact cache of S's factorization only. P/Q and the current RHS
/// are deliberately absent: det(W)=det(S), S=I-shift*C-shift^2*B*A. Every solve
/// reconstructs its ledger rows from the CURRENT P/Q and checks the FULL W.
/// This is not a cache of the full Jacobian, full solution, or native/provider.
#[derive(Debug, Default)]
pub struct ExactFactorCache {
    entry: Option<(FactorKey, SchurFactor)>,
    stats: CacheStats,
}
impl ExactFactorCache {
    pub fn stats(&self) -> CacheStats { self.stats }
    pub fn clear(&mut self) { self.entry = None; }
    fn factor(&mut self, block: &BlockJacobian, shift: f64) -> Result<(&SchurFactor, bool)> {
        self.stats.requests += 1;
        let hit = self.entry.as_ref().is_some_and(|(key, _)| key.matches(block, shift));
        if hit { self.stats.hits += 1; }
        else {
            self.stats.factorization_attempts += 1;
            let factor = match SchurFactor::new(block, shift) {
                Ok(factor) => factor,
                Err(error) => { self.stats.factorization_failures += 1; return Err(error); }
            };
            // Commit only a complete finite factor; preserve a previous valid
            // entry if a different singular/nonfinite candidate fails.
            self.entry = Some((FactorKey::new(block, shift), factor));
        }
        Ok((&self.entry.as_ref().expect("successful factor or exact hit").1, hit))
    }
}
