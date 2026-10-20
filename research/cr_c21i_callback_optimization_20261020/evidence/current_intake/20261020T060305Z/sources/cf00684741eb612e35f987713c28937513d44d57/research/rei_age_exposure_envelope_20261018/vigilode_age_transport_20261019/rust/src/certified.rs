//! Exact-input rational Taylor enclosure of exp(-tau), followed by directed squaring.
use crate::directed::{mul_down, mul_up, Interval};
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, ToPrimitive, Zero};

#[cfg(feature = "reference-check")]
static REFERENCE_CHECKS: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);

pub fn reference_check_count() -> usize {
    #[cfg(feature = "reference-check")]
    { REFERENCE_CHECKS.load(std::sync::atomic::Ordering::Relaxed) }
    #[cfg(not(feature = "reference-check"))]
    { 0 }
}

pub fn exact(value: f64) -> BigRational {
    BigRational::from_float(value).expect("finite binary64 input")
}

/// Convert a rational to binary64, then compare its exact value and adjust.
/// The direction of `to_f64` is deliberately not assumed.
pub fn rational_interval(value: &BigRational) -> Interval {
    let candidate = value.to_f64().expect("rational outside finite binary64 range");
    assert!(candidate.is_finite());
    let mut lo = candidate;
    let mut hi = candidate;
    while exact(lo) > *value { lo = lo.next_down(); }
    while exact(hi) < *value { hi = hi.next_up(); }
    Interval::new(lo, hi).unwrap()
}

/// The same Taylor partial sums with one common integer denominator.
/// At step j, D=j! q^j, P=(-p)^j and N/D=sum_{k=0}^j (-p/q)^k/k!.
fn taylor_bounds(reduced: &BigRational) -> (BigRational, BigRational) {
    let p = -reduced.numer();
    let q = reduced.denom();
    let mut denominator = BigInt::one();
    let mut power = BigInt::one();
    let mut numerator = BigInt::one();
    let mut upper = BigRational::one();
    for j in 1..=19 {
        let factor = q * BigInt::from(j);
        denominator *= &factor;
        power *= &p;
        numerator = numerator * factor + &power;
        if j == 18 { upper = BigRational::new(numerator.clone(), denominator.clone()); }
    }
    (BigRational::new(numerator, denominator), upper)
}

pub fn exp_negative(tau: &BigRational) -> Interval {
    let interval = exp_negative_integer(tau);
    #[cfg(feature = "reference-check")]
    {
        use std::sync::{atomic::Ordering, OnceLock};
        static ENABLED: OnceLock<bool> = OnceLock::new();
        if *ENABLED.get_or_init(||std::env::var_os("REI_EXP_REFERENCE_PARITY").is_some()) {
            let reference = exp_negative_reference(tau);
            assert_eq!([interval.lo.to_bits(), interval.hi.to_bits()],
                       [reference.lo.to_bits(), reference.hi.to_bits()], "exact exponential endpoint parity");
            let count = REFERENCE_CHECKS.fetch_add(1, Ordering::Relaxed) + 1;
            if count % 10000 == 0 { eprintln!("REFERENCE_EXP_PARITY_CHECKS={count}"); }
        }
    }
    interval
}

fn exp_negative_integer(tau: &BigRational) -> Interval {
    assert!(*tau >= BigRational::zero());
    if tau.is_zero() { return Interval::point(1.0).unwrap(); }
    // exp(7/10) > 1+7/10+(7/10)^2/2+(7/10)^3/6
    // =12013/6000>2, hence ln(2)<.7 and 1074 ln(2)<751.8<752.
    if *tau >= BigRational::from_integer(BigInt::from(752)) {
        return Interval::new(0.0, f64::from_bits(1)).unwrap();
    }
    let half = BigRational::new(1.into(), 2.into());
    let mut reduced = tau.clone();
    let mut halvings = 0;
    while reduced > half { reduced /= BigInt::from(2); halvings += 1; }
    let (lower, upper) = taylor_bounds(&reduced);
    let mut interval = Interval::new(rational_interval(&lower).lo.max(0.0),
                                    rational_interval(&upper).hi.min(1.0)).unwrap();
    for _ in 0..halvings {
        interval = Interval::new(mul_down(interval.lo, interval.lo).unwrap().max(0.0),
                                 mul_up(interval.hi, interval.hi).unwrap().min(1.0)).unwrap();
    }
    interval
}

#[cfg(any(test, feature = "reference-check"))]
fn reference_taylor(reduced: &BigRational) -> (BigRational, BigRational) {
    let mut term = BigRational::one();
    let mut sum = term.clone();
    let mut upper = sum.clone();
    for j in 1..=19 {
        term = -term * reduced / BigInt::from(j);
        sum += &term;
        if j == 18 { upper = sum.clone(); }
    }
    (sum, upper)
}

#[cfg(any(test, feature = "reference-check"))]
fn exp_negative_reference(tau: &BigRational) -> Interval {
    assert!(*tau >= BigRational::zero());
    if tau.is_zero() { return Interval::point(1.0).unwrap(); }
    if *tau >= BigRational::from_integer(BigInt::from(752)) {
        return Interval::new(0.0, f64::from_bits(1)).unwrap();
    }
    let half = BigRational::new(1.into(), 2.into());
    let mut reduced = tau.clone();
    let mut halvings = 0;
    while reduced > half { reduced /= BigInt::from(2); halvings += 1; }
    let (lower, upper) = reference_taylor(&reduced);
    let mut interval = Interval::new(rational_interval(&lower).lo.max(0.0),
                                    rational_interval(&upper).hi.min(1.0)).unwrap();
    for _ in 0..halvings {
        interval = Interval::new(mul_down(interval.lo, interval.lo).unwrap().max(0.0),
                                 mul_up(interval.hi, interval.hi).unwrap().min(1.0)).unwrap();
    }
    interval
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::affine_transport::{parallel_error_prefix, AffineErrorMap, AffinePrefixWorkspace};
    #[test]
    fn integer_lift_matches_general_rational_partial_sums_and_endpoints() {
        let mut inputs = vec![BigRational::zero(), exact(f64::from_bits(1)), exact(0.5),
            exact(0.5f64.next_up()), exact(0.5f64.next_down()), exact(752.0f64.next_down()),
            exact(752.0), exact(752.0f64.next_up()), exact(10000.0)];
        for j in 1..=100 { inputs.push(BigRational::new((j*7919).into(), (j*31+7).into())); }
        for j in 0..11 { let x=0.5*2f64.powi(j); inputs.extend([exact(x.next_down()),exact(x),exact(x.next_up())]); }
        for tau in inputs {
            let mut reduced=tau.clone();
            while reduced>BigRational::new(1.into(),2.into()) { reduced/=BigInt::from(2); }
            assert_eq!(taylor_bounds(&reduced),reference_taylor(&reduced));
            let a=exp_negative_integer(&tau); let b=exp_negative_reference(&tau);
            assert_eq!([a.lo.to_bits(),a.hi.to_bits()],[b.lo.to_bits(),b.hi.to_bits()]);
        }
    }
    #[test]
    fn conversion_proves_normal_subnormal_and_midpoint_bounds() {
        let eta = exact(f64::from_bits(1));
        let cases = [BigRational::new(1.into(),3.into()), &eta/BigInt::from(2),
            exact(1.0)+exact(f64::EPSILON)/BigInt::from(2),
            exact(f64::MIN_POSITIVE)-&eta/BigInt::from(2), BigRational::zero()];
        for value in cases {
            let i = rational_interval(&value);
            assert!(exact(i.lo)<=value && value<=exact(i.hi));
            assert!(i.lo==i.hi || i.lo.next_up()==i.hi);
        }
    }
    #[test]
    fn zero_and_underflow_enclosures_retain_positive_upper_bounds() {
        assert_eq!(exp_negative(&BigRational::zero()).as_pair(),[1.0,1.0]);
        for x in [752.0,1e6] {
            assert_eq!(exp_negative(&exact(x)).as_pair(),[0.0,f64::from_bits(1)]);
        }
    }
    #[test]
    fn original_prefix_bounds_exact_rational_all_prefixes_and_thread_parity() {
        for n in [0,1,2,3,7,19,33] {
            let maps:Vec<_> = (0..n).map(|j|AffineErrorMap::new(
                ((j*17+3)%101) as f64/128.0, ((j*29+7)%97) as f64/1024.0).unwrap()).collect();
            let mut rational=exact(0.125);
            let mut reference=vec![rational.clone()];
            for m in &maps { rational=exact(m.gain())*rational+exact(m.defect());reference.push(rational.clone()); }
            let mut baseline=None;
            for threads in [1,2,4] {
                let pool=rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap();
                let prefix=pool.install(||parallel_error_prefix(&maps,0.125)).unwrap();
                assert!(prefix.radii().iter().zip(&reference).all(|(f,r)|exact(*f)>=*r));
                let mut workspace=AffinePrefixWorkspace::new(n).unwrap();
                assert_eq!(workspace.evaluate(&maps,0.125).unwrap(),prefix.radii());
                let bytes:Vec<_>=prefix.radii().iter().map(|f|f.to_bits()).collect();
                if let Some(ref b)=baseline { assert_eq!(&bytes,b); } else { baseline=Some(bytes); }
            }
        }
    }
}
