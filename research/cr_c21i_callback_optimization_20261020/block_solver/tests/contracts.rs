use c21i_block_solver::{BlockJacobian, CacheStats, Error, ExactFactorCache, SolveOptions, LEDGERS};
#[path = "../validation/reference.rs"] mod reference;
use reference::{augmented_elimination, fixture, DenseLu};

fn copy_with(block: &BlockJacobian, a: Vec<f64>, b: Vec<f64>, c: Vec<f64>, p: Vec<f64>, q: Vec<f64>) -> BlockJacobian {
    BlockJacobian::new(block.cohorts(), block.gases(), a, b, c, p, q).unwrap()
}
fn zeros(m: usize, g: usize) -> BlockJacobian {
    BlockJacobian::new(m, g, vec![0.0; m*g], vec![0.0; m*g], vec![0.0; g*g], vec![0.0; LEDGERS*m], vec![0.0; LEDGERS*g]).unwrap()
}
fn close(a: &[f64], b: &[f64], tolerance: f64) {
    assert_eq!(a.len(), b.len());
    for (i, (a, b)) in a.iter().zip(b).enumerate() {
        assert!((a-b).abs() <= tolerance * (1.0 + b.abs()), "component {i}: {a:?} != {b:?}");
    }
}

#[test]
fn input_dimension_and_finite_contracts() {
    assert!(matches!(BlockJacobian::new(1,3,vec![],vec![],vec![],vec![],vec![]), Err(Error::Dimension(_))));
    assert!(matches!(BlockJacobian::new(usize::MAX,2,vec![],vec![],vec![],vec![],vec![]), Err(Error::Dimension(_))));
    assert!(matches!(BlockJacobian::new(1,2,vec![0.0],vec![0.0;2],vec![0.0;4],vec![0.0;15],vec![0.0;30]), Err(Error::Dimension("A"))));
    for which in 0..5 {
        let mut arrays = [vec![0.0;2], vec![0.0;2], vec![0.0;4], vec![0.0;15], vec![0.0;30]];
        arrays[which][0] = f64::NAN;
        let [a,b,c,p,q] = arrays;
        assert!(matches!(BlockJacobian::new(1,2,a,b,c,p,q), Err(Error::NonFinite(_))));
    }
    let block = zeros(1,2); let mut rhs = vec![0.0;block.dimension()];
    assert!(matches!(block.solve_shifted(f64::INFINITY,&rhs,SolveOptions::default(),None), Err(Error::NonFinite("shift"))));
    assert!(matches!(block.solve_shifted(1.0,&rhs[..2],SolveOptions::default(),None), Err(Error::Dimension(_))));
    rhs[block.dimension()-1] = f64::INFINITY;
    assert!(matches!(block.jvp(&rhs), Err(Error::NonFinite(_))));
    assert!(matches!(block.solve_shifted(1.0,&rhs,SolveOptions::default(),None), Err(Error::NonFinite(_))));
}

#[test]
fn analytic_solution_and_every_ledger_preserved() {
    let mut p = vec![0.0;30]; p[0]=2.0; p[1]=-1.0;
    let mut q = vec![0.0;30]; q[0]=3.0; q[1]=2.0;
    let block=BlockJacobian::new(2,2,vec![1.0,2.0,-1.0,0.0],vec![0.0;4],vec![-1.0,0.0,0.0,-1.0],p,q).unwrap();
    let mut rhs=vec![0.0;block.dimension()]; rhs[..4].copy_from_slice(&[3.0,5.0,2.0,4.0]);
    for i in 0..LEDGERS {rhs[4+i]=7.0+i as f64;}
    let solution=block.solve_shifted(1.0,&rhs,SolveOptions::default(),None).unwrap();
    assert_eq!(&solution.solution[..5],&[8.0,4.0,1.0,2.0,26.0]);
    assert_eq!(&solution.solution[5..],&rhs[5..]);
    assert_eq!(solution.backward_error,0.0);
    let jv=block.jvp(&[vec![8.0,4.0,1.0,2.0],vec![999.0;15]].concat()).unwrap();
    assert_eq!(&jv[..5],&[5.0,-1.0,-1.0,-2.0,19.0]);
}

#[test]
fn jvp_matches_independent_dense_and_rewrites_all_outputs() {
    for g in [2,4] {for m in [0,1,9,64] {
        let (block,v)=fixture(m,g); let n=block.dimension();
        let w=block.dense_shifted(-1.0).unwrap(); // I+J
        let mut reference=vec![0.0;n];
        for i in 0..n { for j in 0..n { let coefficient=w[i*n+j] - if i==j {1.0} else {0.0}; reference[i]+=coefficient*v[j]; } }
        let mut actual=vec![f64::NAN;n]; block.jvp_into(&v,&mut actual).unwrap();
        close(&actual,&reference,5e-15);
        let mut other=v.clone(); other[m+g..].fill(-1234.5);
        assert_eq!(block.jvp(&v).unwrap(),block.jvp(&other).unwrap());
        assert!(matches!(block.jvp_into(&v,&mut actual[..n-1]),Err(Error::Dimension(_))));
    }}
}

#[test]
fn schur_matches_full_dense_lu_and_augmented_elimination() {
    for g in [2,4] {for m in [0,1,9,64] {for shift in [0.0,0.01,0.7,-0.3] {
        let (block,rhs)=fixture(m,g); let w=block.dense_shifted(shift).unwrap();
        let full=DenseLu::factor(w.clone(),block.dimension()).unwrap().solve(&rhs).unwrap();
        let augmented=augmented_elimination(&w,&rhs);
        let actual=block.solve_shifted(shift,&rhs,SolveOptions::default(),None).unwrap();
        close(&actual.solution,&full,5e-13); close(&actual.solution,&augmented,5e-13);
        assert!(actual.backward_error<=1e-13);
        assert!(block.backward_error(shift,&full,&rhs).unwrap()<=1e-13);
        assert!(actual.schur_rcond_inf>0.1);
    }}}
}

#[test]
fn multiple_row_pivots_are_applied_correctly() {
    for g in [2,4] {
        let permutation=if g==2 {vec![1,0]} else {vec![2,0,3,1]};
        let mut c=vec![0.0;g*g];
        for i in 0..g {c[i*g+i]=1.0;c[i*g+permutation[i]]-=1.0;}
        let block=BlockJacobian::new(0,g,vec![],vec![],c,vec![],vec![0.0;15*g]).unwrap();
        let rhs:Vec<_>=(0..block.dimension()).map(|k|(k+1) as f64).collect();
        let actual=block.solve_shifted(1.0,&rhs,SolveOptions::default(),None).unwrap();
        for i in 0..g {assert_eq!(actual.solution[permutation[i]],rhs[i]);}
        assert_eq!(&actual.solution[g..],&rhs[g..]);assert_eq!(actual.backward_error,0.0);
    }
}

#[test]
fn exact_cache_reuses_factor_with_new_rhs_and_current_pq() {
    let (block,rhs)=fixture(9,4);let mut cache=ExactFactorCache::default();
    let initial=block.solve_shifted(0.7,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap();assert!(!initial.cache_hit);
    let mut rhs2=rhs.clone();rhs2[0]+=0.03;
    let second=block.solve_shifted(0.7,&rhs2,SolveOptions::default(),Some(&mut cache)).unwrap();assert!(second.cache_hit);
    for which in [0,1] {
        let mut p=block.p().to_vec();let mut q=block.q().to_vec();
        if which==0 {p[0]+=0.25;} else {q[0]+=0.25;}
        let changed=copy_with(&block,block.a().to_vec(),block.b().to_vec(),block.c().to_vec(),p,q);
        let actual=changed.solve_shifted(0.7,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap();
        assert!(actual.cache_hit);assert_ne!(actual.solution[13].to_bits(),initial.solution[13].to_bits());
        let dense=DenseLu::factor(changed.dense_shifted(0.7).unwrap(),changed.dimension()).unwrap().solve(&rhs).unwrap();
        close(&actual.solution,&dense,5e-13);assert!(actual.backward_error<=1e-13);
    }
    assert_eq!(cache.stats(),CacheStats {requests:4,hits:3,factorization_attempts:1,factorization_failures:0});
}

#[test]
fn every_abc_entry_and_shift_one_ulp_invalidate() {
    let (block,rhs)=fixture(3,2);
    for which in 0..3 {
        let length=if which==2 {4} else {6};
        for index in 0..length {
            let mut a=block.a().to_vec();let mut b=block.b().to_vec();let mut c=block.c().to_vec();
            let target=match which {0=>&mut a,1=>&mut b,_=>&mut c};
            target[index]=f64::from_bits(target[index].to_bits()+1);
            let changed=copy_with(&block,a,b,c,block.p().to_vec(),block.q().to_vec());
            let mut cache=ExactFactorCache::default();
            block.solve_shifted(0.7,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap();
            assert!(!changed.solve_shifted(0.7,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap().cache_hit);
            assert!(changed.solve_shifted(0.7,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap().cache_hit);
            assert_eq!(cache.stats().factorization_attempts,2);
        }
    }
    let mut cache=ExactFactorCache::default();
    block.solve_shifted(0.7,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap();
    assert!(!block.solve_shifted(f64::from_bits(0.7_f64.to_bits()+1),&rhs,SolveOptions::default(),Some(&mut cache)).unwrap().cache_hit);
}

#[test]
fn signed_zero_and_dimensions_are_part_of_cache_identity() {
    let block=zeros(1,2);let rhs=vec![1.0;block.dimension()];let mut cache=ExactFactorCache::default();
    block.solve_shifted(0.0,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap();
    assert!(!block.solve_shifted(-0.0,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap().cache_hit);
    let mut a=block.a().to_vec();a[0]=-0.0;
    let changed=copy_with(&block,a,block.b().to_vec(),block.c().to_vec(),block.p().to_vec(),block.q().to_vec());
    assert!(!changed.solve_shifted(-0.0,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap().cache_hit);
    for (m,g) in [(2,2),(2,4)] {
        let (b,r)=fixture(m,g);assert!(!b.solve_shifted(-0.0,&r,SolveOptions::default(),Some(&mut cache)).unwrap().cache_hit);
    }
    cache.clear();let (b,r)=fixture(2,4);assert!(!b.solve_shifted(-0.0,&r,SolveOptions::default(),Some(&mut cache)).unwrap().cache_hit);
}

#[test]
fn singular_and_near_singular_are_distinguished_without_regularization() {
    let z=zeros(1,2);let mut rhs=vec![0.0;z.dimension()];rhs[1]=1.0;
    let mut c=vec![0.0;4];let eps=2.0_f64.powi(-50);c[0]=1.0-eps;
    let near=copy_with(&z,z.a().to_vec(),z.b().to_vec(),c.clone(),z.p().to_vec(),z.q().to_vec());
    let result=near.solve_shifted(1.0,&rhs,SolveOptions::default(),None).unwrap();
    assert_eq!(result.solution[1],1.0/eps);assert_eq!(result.backward_error,0.0);assert_eq!(result.schur_rcond_inf,eps);
    assert!(matches!(near.solve_shifted(1.0,&rhs,SolveOptions {max_backward_error:1e-13,minimum_schur_rcond:Some(1e-12)},None),Err(Error::IllConditioned{..})));
    c[0]=1.0;let singular=copy_with(&z,z.a().to_vec(),z.b().to_vec(),c,z.p().to_vec(),z.q().to_vec());
    let mut cache=ExactFactorCache::default();z.solve_shifted(1.0,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap();
    assert!(matches!(singular.solve_shifted(1.0,&rhs,SolveOptions::default(),Some(&mut cache)),Err(Error::Singular{pivot:0})));
    assert!(z.solve_shifted(1.0,&rhs,SolveOptions::default(),Some(&mut cache)).unwrap().cache_hit);
    assert_eq!(cache.stats().factorization_failures,1);
}

#[test]
fn positive_diagonal_similarity_preserves_the_full_solution() {
    for g in [2,4] {
        let (block,rhs)=fixture(9,g);let m=block.cohorts();let n=block.dimension();
        let d:Vec<_>=(0..n).map(|i|2.0_f64.powi((i%21) as i32-10)).collect();
        let scale=|values:&[f64],rows:usize,cols:usize,ro:usize,co:usize|->Vec<f64>{
            let mut out=values.to_vec();for i in 0..rows {for j in 0..cols {out[i*cols+j]=values[i*cols+j]*d[co+j]/d[ro+i];}}out
        };
        let scaled=BlockJacobian::new(m,g,scale(block.a(),m,g,0,m),scale(block.b(),g,m,m,0),scale(block.c(),g,g,m,m),scale(block.p(),15,m,m+g,0),scale(block.q(),15,g,m+g,m)).unwrap();
        let actual=block.solve_shifted(0.7,&rhs,SolveOptions::default(),None).unwrap();
        let rhs_z:Vec<_>=rhs.iter().zip(&d).map(|(r,d)|r/d).collect();
        let z=scaled.solve_shifted(0.7,&rhs_z,SolveOptions::default(),None).unwrap();
        let expected:Vec<_>=actual.solution.iter().zip(&d).map(|(u,d)|u/d).collect();
        close(&z.solution,&expected,5e-12);assert_eq!(z.solution.len(),m+g+15);
    }
}

#[test]
fn full_residual_detects_each_corrupted_ledger_and_zero_problem() {
    let (block,rhs)=fixture(9,2);let solved=block.solve_shifted(0.7,&rhs,SolveOptions::default(),None).unwrap();
    for i in 0..15 {let mut x=solved.solution.clone();x[11+i]+=1.0;assert!(block.backward_error(0.7,&x,&rhs).unwrap()>1e-6);}
    let zero=vec![0.0;block.dimension()];assert_eq!(block.solve_shifted(0.7,&zero,SolveOptions::default(),None).unwrap().backward_error,0.0);
    assert!(matches!(block.solve_shifted(0.7,&rhs,SolveOptions{max_backward_error:-1.0,minimum_schur_rcond:None},None),Err(Error::InvalidOptions)));
    assert!(matches!(block.solve_shifted(0.7,&rhs,SolveOptions{max_backward_error:0.0,minimum_schur_rcond:None},None),Err(Error::ResidualTooLarge{..})));
}

#[test]
fn nonfinite_intermediate_is_an_explicit_error() {
    let z=zeros(1,2);let mut a=z.a().to_vec();let mut b=z.b().to_vec();a[0]=1e308;b[0]=1e308;
    let huge=copy_with(&z,a,b,z.c().to_vec(),z.p().to_vec(),z.q().to_vec());
    let rhs=vec![1.0;huge.dimension()];let mut cache=ExactFactorCache::default();
    assert!(matches!(huge.solve_shifted(1.0,&rhs,SolveOptions::default(),Some(&mut cache)),Err(Error::NonFinite(_))));
    assert_eq!(cache.stats().factorization_failures,1);assert_eq!(cache.stats().hits,0);
    let mut v=rhs.clone();v[1]=2.0;assert!(matches!(huge.jvp(&v),Err(Error::NonFinite(_))));
}
