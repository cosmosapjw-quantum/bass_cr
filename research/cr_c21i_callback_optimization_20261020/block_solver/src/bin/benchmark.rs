//! Fixed, bounded manufactured-kernel benchmark. All records are create-only.
use c21i_block_solver::{BlockJacobian, ExactFactorCache, SolveOptions, LEDGERS};
use std::{error::Error, fs::{self, File, OpenOptions}, hint::black_box, io::{BufWriter, Write}, path::Path, time::Instant};
#[path = "../../validation/reference.rs"] mod reference;
use reference::{dense_jacobian, dense_jvp_into, fixture, DenseLu};

const SHIFT:f64=0.7;
const COLD_REPEATS:usize=5;
const WARM_REPEATS:usize=20;

fn new_file(path:&Path)->std::io::Result<BufWriter<File>> {
    Ok(BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path)?))
}

fn input_record(path:&Path,block:&BlockJacobian,rhs:&[f64])->std::io::Result<()> {
    let mut f=new_file(path)?;
    writeln!(f,"block,index,binary64_hex,value")?;
    writeln!(f,"shift,0,{:016x},{:.17e}",SHIFT.to_bits(),SHIFT)?;
    for (name,array) in [("A",block.a()),("B",block.b()),("C",block.c()),("P",block.p()),("Q",block.q()),("rhs",rhs)] {
        for (i,v) in array.iter().enumerate() {writeln!(f,"{name},{i},{:016x},{:.17e}",v.to_bits(),v)?;}
    }
    f.flush()
}

fn emit(f:&mut impl Write,solutions:&mut impl Write,block:&BlockJacobian,phase:&str,method:&str,iteration:usize,
        ns:u128,x:&[f64],eta:f64,rcond:Option<f64>,hit:bool)->std::io::Result<()> {
    writeln!(f,"{},{},{},{},{phase},{method},{iteration},{ns},{eta:.17e},{},{hit},1",
        block.cohorts(),block.gases(),LEDGERS,block.dimension(),rcond.map(|v|format!("{v:.17e}")).unwrap_or_default())?;
    writeln!(solutions,"{{\"m\":{},\"g\":{},\"phase\":\"{phase}\",\"method\":\"{method}\",\"iteration\":{iteration},\"solution\":{:?}}}",block.cohorts(),block.gases(),x)
}

fn checked_dense(block:&BlockJacobian,rhs:&[f64],lu:&DenseLu)->Result<(Vec<f64>,f64),Box<dyn Error>> {
    let x=lu.solve(rhs)?;let eta=block.backward_error(SHIFT,&x,rhs)?;
    if eta>SolveOptions::default().max_backward_error {return Err(format!("dense residual failed {eta}").into());}
    Ok((x,eta))
}

fn main()->Result<(),Box<dyn Error>> {
    let args:Vec<String>=std::env::args().collect();
    if args.len()!=2 {return Err("usage: block-benchmark NEW_OUTPUT_DIRECTORY".into());}
    let out=Path::new(&args[1]);fs::create_dir(out)?;
    let mut csv=new_file(&out.join("solve_repeats.csv"))?;
    let mut solutions=new_file(&out.join("solutions.jsonl"))?;
    let mut jvp_csv=new_file(&out.join("jvp_repeats.csv"))?;
    let mut jvp_solutions=new_file(&out.join("jvp_outputs.jsonl"))?;
    let mut stats=new_file(&out.join("cache_stats.csv"))?;
    let mut meta=new_file(&out.join("contract.json"))?;
    writeln!(meta,"{{\"schema\":\"C21I_BLOCK_KERNEL_BENCH_V1\",\"kind\":\"manufactured linear algebra prototype\",\"integrated_c21h_backend\":false,\"native_chemistry\":\"NOT_RUN\",\"native_performance\":\"NOT_EVALUATED\",\"global_error_bound\":null,\"shift\":0.7,\"cohorts\":[9,64,256],\"gases\":[2,4],\"ledgers\":15,\"max_backward_error\":1e-13,\"cold_factorization_repeats\":{COLD_REPEATS},\"warm_repeats\":{WARM_REPEATS},\"worker_count\":1,\"input_construction_timed\":false,\"full_residual_timed\":true,\"cold_definition\":\"reassemble and refactor every solve; CPU cache not flushed\",\"warm_definition\":\"fixed matrix factor reused; Schur exact key check included\",\"dense_reference\":\"standalone scalar partial-pivot dense LU; not Faer/LAPACK or ODE backend\",\"order\":\"paired alternating method order by iteration\",\"jvp_definition\":\"preallocated full output, input validation included, comparison outside timer\"}}")?;
    writeln!(csv,"M,G,L,N,phase,method,iteration,elapsed_ns,full_backward_error,schur_rcond_inf,cache_hit,workers")?;
    writeln!(jvp_csv,"M,G,L,N,method,iteration,elapsed_ns,max_absolute_difference,workers")?;
    writeln!(stats,"M,G,requests,hits,factorization_attempts,factorization_failures,structured_f64,dense_f64")?;
    for g in [2,4] {for m in [9,64,256] {
        let (block,rhs)=fixture(m,g);let n=block.dimension();
        input_record(&out.join(format!("input_m{m}_g{g}.csv")),&block,&rhs)?;
        for iteration in 0..COLD_REPEATS {
            for order in 0..2 {
                if (iteration+order)%2==0 {
                    let start=Instant::now();let result=black_box(&block).solve_shifted(SHIFT,black_box(&rhs),SolveOptions::default(),None)?;
                    let ns=start.elapsed().as_nanos();black_box(&result.solution);
                    emit(&mut csv,&mut solutions,&block,"cold_factorization","schur",iteration,ns,&result.solution,result.backward_error,Some(result.schur_rcond_inf),result.cache_hit)?;
                } else {
                    let start=Instant::now();let lu=DenseLu::factor(black_box(&block).dense_shifted(SHIFT)?,n)?;
                    let (x,eta)=checked_dense(&block,black_box(&rhs),&lu)?;let ns=start.elapsed().as_nanos();black_box(&x);
                    emit(&mut csv,&mut solutions,&block,"cold_factorization","dense_reference",iteration,ns,&x,eta,None,false)?;
                }
            }
        }
        let mut cache=ExactFactorCache::default();
        let start=Instant::now();let initial=block.solve_shifted(SHIFT,&rhs,SolveOptions::default(),Some(&mut cache))?;
        emit(&mut csv,&mut solutions,&block,"warm_setup","schur",0,start.elapsed().as_nanos(),&initial.solution,initial.backward_error,Some(initial.schur_rcond_inf),initial.cache_hit)?;
        let start=Instant::now();let dense=DenseLu::factor(block.dense_shifted(SHIFT)?,n)?;let (x,eta)=checked_dense(&block,&rhs,&dense)?;
        emit(&mut csv,&mut solutions,&block,"warm_setup","dense_reference",0,start.elapsed().as_nanos(),&x,eta,None,false)?;
        for iteration in 0..WARM_REPEATS {
            for order in 0..2 {
                if (iteration+order)%2==0 {
                    let start=Instant::now();let result=black_box(&block).solve_shifted(SHIFT,black_box(&rhs),SolveOptions::default(),Some(&mut cache))?;
                    let ns=start.elapsed().as_nanos();black_box(&result.solution);
                    if !result.cache_hit {return Err("expected exact fixed-matrix factor hit".into());}
                    emit(&mut csv,&mut solutions,&block,"warm_reuse","schur",iteration,ns,&result.solution,result.backward_error,Some(result.schur_rcond_inf),result.cache_hit)?;
                } else {
                    let start=Instant::now();let (x,eta)=checked_dense(&block,black_box(&rhs),&dense)?;let ns=start.elapsed().as_nanos();black_box(&x);
                    emit(&mut csv,&mut solutions,&block,"warm_reuse","dense_reference",iteration,ns,&x,eta,None,true)?;
                }
            }
        }
        let s=cache.stats();writeln!(stats,"{m},{g},{},{},{},{},{},{}",s.requests,s.hits,s.factorization_attempts,s.factorization_failures,block.stored_f64(),n*n)?;
        let j=dense_jacobian(&block);let mut reference=vec![0.0;n];dense_jvp_into(&j,&rhs,&mut reference)?;
        let mut output=vec![0.0;n];
        for iteration in 0..WARM_REPEATS {for order in 0..2 {
            let method;if (iteration+order)%2==0 {
                method="structured_jvp_into";let start=Instant::now();black_box(&block).jvp_into(black_box(&rhs),&mut output)?;let ns=start.elapsed().as_nanos();black_box(&output);
                let difference=output.iter().zip(&reference).map(|(a,b)|(a-b).abs()).fold(0.0_f64,f64::max);
                if difference>1e-13 {return Err(format!("JVP parity failed {difference}").into());}
                writeln!(jvp_csv,"{m},{g},{LEDGERS},{n},{method},{iteration},{ns},{difference:.17e},1")?;
            } else {
                method="dense_matvec_into";let start=Instant::now();dense_jvp_into(black_box(&j),black_box(&rhs),&mut output)?;let ns=start.elapsed().as_nanos();black_box(&output);
                writeln!(jvp_csv,"{m},{g},{LEDGERS},{n},{method},{iteration},{ns},0.0,1")?;
            }
            writeln!(jvp_solutions,"{{\"m\":{m},\"g\":{g},\"method\":\"{method}\",\"iteration\":{iteration},\"output\":{:?}}}",output)?;
        }}
    }}
    for writer in [&mut csv,&mut solutions,&mut jvp_csv,&mut jvp_solutions,&mut stats,&mut meta] {writer.flush()?;}
    println!("BLOCK_BENCH_COMPLETE cases=6 solve_rows=312 jvp_rows=240 workers=1 native=NOT_RUN");
    Ok(())
}
