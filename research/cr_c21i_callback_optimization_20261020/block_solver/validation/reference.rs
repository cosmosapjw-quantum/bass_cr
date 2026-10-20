//! Deterministic manufactured inputs and an independent full-matrix reference.
//! This scalar dense LU is a comparison implementation, not LAPACK/Faer.
#![allow(dead_code)]
use c21i_block_solver::{BlockJacobian, LEDGERS};

pub fn dense_jacobian(block: &BlockJacobian) -> Vec<f64> {
    let m=block.cohorts();let g=block.gases();let n=block.dimension();let mut j=vec![0.0;n*n];
    for i in 0..m {for k in 0..g {j[i*n+m+k]=block.a()[i*g+k];}}
    for i in 0..g {
        for k in 0..m {j[(m+i)*n+k]=block.b()[i*m+k];}
        for k in 0..g {j[(m+i)*n+m+k]=block.c()[i*g+k];}
    }
    for i in 0..LEDGERS {
        for k in 0..m {j[(m+g+i)*n+k]=block.p()[i*m+k];}
        for k in 0..g {j[(m+g+i)*n+m+k]=block.q()[i*g+k];}
    }
    j
}

pub fn dense_jvp_into(j: &[f64], v: &[f64], output: &mut [f64]) -> Result<(),String> {
    let n=v.len();
    if output.len()!=n || j.len()!=n*n || v.iter().any(|x|!x.is_finite()) {return Err("dense JVP shape/finite".into());}
    for (i,row) in j.chunks(n).enumerate() {
        let value:f64=row.iter().zip(v).map(|(a,b)|a*b).sum();
        if !value.is_finite() {return Err("dense JVP nonfinite".into());}output[i]=value;
    }
    Ok(())
}

pub fn fixture(m: usize, g: usize) -> (BlockJacobian, Vec<f64>) {
    let mut state = 0xC21_2026_1020_u64 ^ ((m as u64) << 16) ^ g as u64;
    let mut random = || {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((state >> 11) as f64) * (2.0 / 9007199254740992.0) - 1.0
    };
    let a = (0..m * g).map(|_| 0.2 * random()).collect();
    let b = (0..g * m).map(|_| 0.12 * random() / (m.max(1) as f64)).collect();
    let mut c = vec![0.0; g * g];
    for i in 0..g { for j in 0..g { c[i * g + j] = if i == j { -0.4 - 0.1 * i as f64 } else { 0.015 * random() }; } }
    let p = (0..LEDGERS * m).map(|_| 0.03 * random() / (m.max(1) as f64)).collect();
    let q = (0..LEDGERS * g).map(|_| 0.02 * random()).collect();
    let rhs = (0..m + g + LEDGERS).map(|_| random()).collect();
    (BlockJacobian::new(m, g, a, b, c, p, q).unwrap(), rhs)
}

pub struct DenseLu { rows: Vec<Vec<f64>>, permutation: Vec<usize> }
impl DenseLu {
    pub fn factor(matrix: Vec<f64>, n: usize) -> Result<Self, String> {
        if n == 0 || matrix.len() != n.checked_mul(n).ok_or("dense size overflow")? || matrix.iter().any(|v| !v.is_finite()) {
            return Err("dense shape/finite contract".into());
        }
        let mut rows: Vec<Vec<f64>> = matrix.chunks(n).map(|r| r.to_vec()).collect();
        let mut permutation: Vec<usize> = (0..n).collect();
        for column in 0..n {
            let pivot = (column..n).max_by(|a, b| rows[*a][column].abs().total_cmp(&rows[*b][column].abs())).unwrap();
            if rows[pivot][column] == 0.0 { return Err(format!("singular dense pivot {column}")); }
            rows.swap(column, pivot); permutation.swap(column, pivot);
            let (finished, remaining) = rows.split_at_mut(column + 1);
            let upper = &finished[column];
            for row in remaining {
                row[column] /= upper[column];
                let multiplier = row[column];
                for j in column + 1..n { row[j] -= multiplier * upper[j]; }
            }
        }
        if rows.iter().flatten().any(|v| !v.is_finite()) { return Err("dense factor nonfinite".into()); }
        Ok(Self { rows, permutation })
    }

    pub fn solve(&self, rhs: &[f64]) -> Result<Vec<f64>, String> {
        let n = self.rows.len();
        if rhs.len() != n || rhs.iter().any(|v| !v.is_finite()) { return Err("dense rhs shape/finite".into()); }
        let mut x: Vec<f64> = self.permutation.iter().map(|i| rhs[*i]).collect();
        for i in 0..n {
            let sum: f64 = self.rows[i][..i].iter().zip(&x[..i]).map(|(a, b)| a * b).sum();
            x[i] -= sum;
        }
        for i in (0..n).rev() {
            let sum: f64 = self.rows[i][i + 1..].iter().zip(&x[i + 1..]).map(|(a, b)| a * b).sum();
            x[i] = (x[i] - sum) / self.rows[i][i];
        }
        if x.iter().any(|v| !v.is_finite()) { return Err("dense solve nonfinite".into()); }
        Ok(x)
    }
}

/// Third route for tests: augmented row reduction updates RHS while eliminating
/// rows, without reusing SmallLu/DenseLu's permutation/triangular-solve code.
pub fn augmented_elimination(matrix: &[f64], rhs: &[f64]) -> Vec<f64> {
    let n = rhs.len();
    let mut rows: Vec<Vec<f64>> = matrix.chunks(n).zip(rhs).map(|(r, b)| { let mut v = r.to_vec(); v.push(*b); v }).collect();
    for k in 0..n {
        let mut pivot = k;
        for i in k + 1..n { if rows[i][k].abs() > rows[pivot][k].abs() { pivot = i; } }
        rows.swap(k, pivot);
        let divisor = rows[k][k]; assert_ne!(divisor, 0.0);
        for j in k..=n { rows[k][j] /= divisor; }
        for i in k + 1..n {
            let multiplier = rows[i][k];
            for j in k..=n { rows[i][j] -= multiplier * rows[k][j]; }
        }
    }
    let mut x = vec![0.0; n];
    for i in (0..n).rev() {
        let mut value = rows[i][n];
        for j in i + 1..n { value -= rows[i][j] * x[j]; }
        x[i] = value;
    }
    x
}
