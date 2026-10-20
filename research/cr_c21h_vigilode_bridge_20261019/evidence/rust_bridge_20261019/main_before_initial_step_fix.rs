//! One-segment, synchronous, fail-closed solver bridge.
//!
//! The parent owns the scientific RHS, state scaling, finite differences, and
//! native provider. This executable owns only the selected integration method.
#![forbid(unsafe_code)]
#[cfg(not(panic = "unwind"))]
compile_error!("C21H requires panic=unwind to return typed Diffsol callback failures");

use std::io::{self, BufRead, BufReader, Read, Write};
use std::panic::{AssertUnwindSafe, catch_unwind, panic_any};
use std::process::ExitCode;
use std::sync::{Arc, Mutex};

use diffsol::{FaerLU, FaerMat, OdeBuilder, OdeSolverMethod, OdeSolverStopReason};
use rodas5p_core::{CoreError, DenseMatrix};
use rodas5p_integrators::{
    AdaptiveStepConfig, MaxStepPolicy, OdeProblem, OutputSchedule, integrate_rodas5p_fast_observed,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};

const PROTOCOL: &str = "C21H_V1";
const VIGILODE_COMMIT: &str = "8a8bd409b1d96c7b7421f496d229e119fd3d284e";
const DIFFSOL_VERSION: &str = "0.17.1";
const MAX_LINE_BYTES: usize = 4 * 1024 * 1024;
const MAX_DIMENSION: usize = 256;

#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Config {
    protocol: String,
    dimension: usize,
    t0: f64,
    t1: f64,
    y0: Vec<f64>,
    rtol: f64,
    atol: f64,
    h0: f64,
    h_min: f64,
    h_max: f64,
    max_steps: usize,
    method: String,
    #[serde(default)]
    output_times: Option<Vec<f64>>,
}

impl Config {
    fn validate(&self) -> Result<(), String> {
        if self.protocol != PROTOCOL {
            return Err("unsupported protocol".into());
        }
        if self.dimension == 0 || self.dimension > MAX_DIMENSION {
            return Err(format!("dimension must be in 1..={MAX_DIMENSION}"));
        }
        valid_vector(&self.y0, self.dimension, "initial state")?;
        if !self.t0.is_finite() || !self.t1.is_finite() || self.t0 >= self.t1 {
            return Err("time span must be finite and strictly increasing".into());
        }
        for (name, value) in [
            ("rtol", self.rtol),
            ("atol", self.atol),
            ("h0", self.h0),
            ("h_min", self.h_min),
            ("h_max", self.h_max),
        ] {
            if !value.is_finite() || value <= 0.0 {
                return Err(format!("{name} must be finite and strictly positive"));
            }
        }
        if self.h_min > self.h0 || self.h0 > self.h_max {
            return Err("step controls must satisfy h_min <= h0 <= h_max".into());
        }
        if self.max_steps == 0 {
            return Err("max_steps must be positive".into());
        }
        if !matches!(self.method.as_str(), "vigilode-rodas5p" | "diffsol-bdf") {
            return Err("method must be vigilode-rodas5p or diffsol-bdf".into());
        }
        let times = self.times();
        if times.len() < 2
            || times.len() > 100_000
            || times.first() != Some(&self.t0)
            || times.last() != Some(&self.t1)
            || times.iter().any(|t| !t.is_finite())
            || times.windows(2).any(|a| a[1] <= a[0])
        {
            return Err(
                "output times must be finite, increasing, and include exact span endpoints".into(),
            );
        }
        Ok(())
    }

    fn times(&self) -> Vec<f64> {
        self.output_times
            .clone()
            .unwrap_or_else(|| vec![self.t0, self.t1])
    }
}

fn valid_vector(value: &[f64], n: usize, label: &str) -> Result<(), String> {
    if value.len() != n || value.iter().any(|x| !x.is_finite()) {
        return Err(format!("{label} must contain exactly {n} finite values"));
    }
    Ok(())
}

fn read_line<R: BufRead>(reader: &mut R) -> Result<String, String> {
    let mut bytes = Vec::new();
    let size = reader
        .take((MAX_LINE_BYTES + 1) as u64)
        .read_until(b'\n', &mut bytes)
        .map_err(|e| format!("read: {e}"))?;
    if size == 0 {
        return Err("unexpected EOF".into());
    }
    if size > MAX_LINE_BYTES {
        return Err("JSON line exceeds transport limit".into());
    }
    if bytes.last() != Some(&b'\n') {
        return Err("unterminated JSON line".into());
    }
    String::from_utf8(bytes).map_err(|e| format!("invalid UTF-8: {e}"))
}

fn write_json<W: Write>(writer: &mut W, value: &Value) -> Result<(), String> {
    serde_json::to_writer(&mut *writer, value).map_err(|e| format!("JSON write: {e}"))?;
    writer
        .write_all(b"\n")
        .and_then(|_| writer.flush())
        .map_err(|e| format!("flush: {e}"))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Response {
    id: u64,
    ok: bool,
    #[serde(default)]
    value: Option<Value>,
    #[serde(default)]
    error: Option<String>,
}

fn response_value(line: &str, id: u64) -> Result<Value, String> {
    let response: Response =
        serde_json::from_str(line).map_err(|e| format!("invalid RPC response: {e}"))?;
    if response.id != id {
        return Err(format!(
            "RPC id mismatch: expected {id}, received {}",
            response.id
        ));
    }
    if !response.ok {
        return Err(format!(
            "parent rejected request {id}: {}",
            response.error.unwrap_or_else(|| "unspecified error".into())
        ));
    }
    if response.error.is_some() {
        return Err("successful RPC response also supplied an error".into());
    }
    response
        .value
        .ok_or_else(|| "successful RPC response omitted value".into())
}

#[derive(Default, Clone, Debug, Serialize)]
struct RpcCounters {
    requests_attempted: u64,
    responses_validated: u64,
    rhs_requests: u64,
    jacobian_requests: u64,
    partial_t_requests: u64,
    diffsol_jvp_calls: u64,
    diffsol_jacobian_cache_hits: u64,
}

struct Channel<R, W> {
    reader: R,
    writer: W,
    dimension: usize,
    t0: f64,
    t1: f64,
    counters: RpcCounters,
    failure: Option<String>,
    pending_request: Option<Value>,
}

impl<R: BufRead, W: Write> Channel<R, W> {
    fn request(&mut self, op: &str, t: f64, y: &[f64]) -> Result<Value, String> {
        if let Some(error) = &self.failure {
            return Err(error.clone());
        }
        let result = self.request_inner(op, t, y);
        if let Err(error) = &result {
            self.failure = Some(error.clone());
        }
        result
    }

    fn request_inner(&mut self, op: &str, t: f64, y: &[f64]) -> Result<Value, String> {
        valid_vector(y, self.dimension, "callback state")?;
        if !t.is_finite() || t < self.t0 || t > self.t1 {
            return Err("callback time lies outside frozen segment".into());
        }
        let id = self
            .counters
            .requests_attempted
            .checked_add(1)
            .ok_or("RPC id overflow")?;
        self.counters.requests_attempted = id;
        match op {
            "rhs" => self.counters.rhs_requests += 1,
            "jacobian" => self.counters.jacobian_requests += 1,
            "partial_t" => self.counters.partial_t_requests += 1,
            _ => return Err("unsupported callback operation".into()),
        }
        let request = json!({"type":"request", "id":id, "op":op, "t":t, "y":y});
        self.pending_request = Some(request.clone());
        write_json(&mut self.writer, &request)?;
        let value = response_value(&read_line(&mut self.reader)?, id)?;
        // Shape and finiteness belong to the same transaction as its response.
        if op == "jacobian" {
            matrix_value(&value, self.dimension)?;
        } else {
            vector_value(&value, self.dimension)?;
        }
        self.counters.responses_validated += 1;
        self.pending_request = None;
        Ok(value)
    }
}

fn vector_value(value: &Value, n: usize) -> Result<Vec<f64>, String> {
    let out: Vec<f64> =
        serde_json::from_value(value.clone()).map_err(|e| format!("invalid vector: {e}"))?;
    valid_vector(&out, n, "callback result")?;
    Ok(out)
}

fn matrix_value(value: &Value, n: usize) -> Result<Vec<Vec<f64>>, String> {
    let out: Vec<Vec<f64>> =
        serde_json::from_value(value.clone()).map_err(|e| format!("invalid matrix: {e}"))?;
    if out.len() != n {
        return Err("Jacobian row count mismatch".into());
    }
    for row in &out {
        valid_vector(row, n, "Jacobian row")?;
    }
    Ok(out)
}

type SharedChannel = Arc<Mutex<Channel<BufReader<io::Stdin>, io::Stdout>>>;

fn request(rpc: &SharedChannel, op: &str, t: f64, y: &[f64]) -> Result<Value, String> {
    rpc.lock()
        .map_err(|_| "RPC channel mutex poisoned".to_string())?
        .request(op, t, y)
}

fn fatal_input(error: String) -> CoreError {
    CoreError::InvalidInput(error)
}

#[derive(Default)]
struct AcceptedPath {
    times: Vec<f64>,
    states: Vec<Vec<f64>>,
}

impl AcceptedPath {
    fn observe(&mut self, t: f64, y: &[f64]) -> Result<(), String> {
        if let Some(&previous) = self.times.last() {
            if t == previous {
                if !self
                    .states
                    .last()
                    .expect("paired path")
                    .iter()
                    .zip(y)
                    .all(|(a, b)| a.to_bits() == b.to_bits())
                {
                    return Err(
                        "accepted-base observer saw two states at one represented time".into(),
                    );
                }
                return Ok(());
            }
            if t < previous {
                return Err("accepted-base observer time went backwards".into());
            }
        }
        self.times.push(t);
        self.states.push(y.to_vec());
        Ok(())
    }
}

fn run_vigilode(config: &Config, rpc: &SharedChannel) -> Result<Value, String> {
    let n = config.dimension;
    let accepted_path = Arc::new(Mutex::new(AcceptedPath::default()));
    let accepted_observer = Arc::clone(&accepted_path);
    let rhs_rpc = Arc::clone(rpc);
    let jac_rpc = Arc::clone(rpc);
    let ft_rpc = Arc::clone(rpc);
    let rhs = Arc::new(move |t: f64, y: &[f64], out: &mut [f64]| {
        let value = request(&rhs_rpc, "rhs", t, y)
            .and_then(|v| vector_value(&v, n))
            .map_err(fatal_input)?;
        out.copy_from_slice(&value);
        Ok(())
    });
    let jacobian = Arc::new(move |t: f64, y: &[f64]| {
        // At the pinned fast driver this callback is called only at its current
        // accepted base state. Rejected attempts may repeat the same base.
        accepted_observer
            .lock()
            .map_err(|_| fatal_input("accepted observer mutex poisoned".into()))?
            .observe(t, y)
            .map_err(fatal_input)?;
        let value = request(&jac_rpc, "jacobian", t, y)
            .and_then(|v| matrix_value(&v, n))
            .map_err(fatal_input)?;
        DenseMatrix::new(n, n, value.into_iter().flatten().collect())
    });
    let partial_t = Arc::new(move |t: f64, y: &[f64], out: &mut [f64]| {
        let value = request(&ft_rpc, "partial_t", t, y)
            .and_then(|v| vector_value(&v, n))
            .map_err(fatal_input)?;
        out.copy_from_slice(&value);
        Ok(())
    });
    let problem = OdeProblem::new(
        "C21H frozen scaled segment",
        n,
        rhs,
        None,
        Some(jacobian),
        None,
        Some(partial_t),
        false,
        None,
        None,
    )
    .map_err(|e| e.to_string())?;
    let adaptive = AdaptiveStepConfig {
        atol: config.atol,
        rtol: config.rtol,
        initial_step: config.h0,
        min_step: config.h_min,
        max_step: config.h_max,
        max_attempts: config.max_steps,
        max_step_policy: MaxStepPolicy::StrictRepresentedCap,
        ..Default::default()
    };
    let result = integrate_rodas5p_fast_observed(
        &problem,
        (config.t0, config.t1),
        &config.y0,
        &adaptive,
        &OutputSchedule::new(config.times()).map_err(|e| e.to_string())?,
    )
    .map_err(|e| e.to_string())?;
    let mut accepted = accepted_path
        .lock()
        .map_err(|_| "accepted observer mutex poisoned")?;
    if result.observed.success {
        let final_state = result
            .observed
            .y
            .last()
            .ok_or("successful Vigilode solve returned no output")?;
        accepted.observe(config.t1, final_state)?;
        if accepted.times.len() != result.observed.internal_steps + 1 {
            return Err(
                "accepted-base observer count differs from the solver's accepted-step count".into(),
            );
        }
    }
    Ok(json!({
        "type":"result", "ok":true, "method":config.method,
        "vigilode_commit":VIGILODE_COMMIT,
        "times":result.observed.t, "states":result.observed.y,
        "success":result.observed.success, "message":result.observed.message,
        "counters":result.observed.counters,
        "internal_steps":result.observed.internal_steps,
        "attempts":result.attempts, "rejected_steps":result.rejected_steps,
        "jacobian_reuses":result.jacobian_reuses, "driver":result.driver,
        "accepted_times":accepted.times, "accepted_states":accepted.states,
        "accepted_grid_complete":result.observed.success,
        "accepted_grid_origin":"pinned fast-driver accepted-base Jacobian callback observer plus final endpoint; count checked",
        "output_clipped_steps":result.observed.output_clipped_steps,
        "max_steps_semantics":"adaptive_attempts", "h_max_policy":"strict represented-step cap",
        "output_policy":"exact requested-time landings", "precision":"binary64",
    }))
}

#[derive(Debug)]
struct CallbackAbort(String);

fn callback_or_abort<T>(result: Result<T, String>) -> T {
    match result {
        Ok(value) => value,
        Err(error) => panic_any(CallbackAbort(error)),
    }
}

struct CachedJacobian {
    t_bits: u64,
    y_bits: Vec<u64>,
    matrix: Vec<Vec<f64>>,
}

fn run_diffsol_inner(config: &Config, rpc: &SharedChannel) -> Result<Value, String> {
    let n = config.dimension;
    let rhs_rpc = Arc::clone(rpc);
    let jac_rpc = Arc::clone(rpc);
    let initial = config.y0.clone();
    let cache: Mutex<Option<CachedJacobian>> = Mutex::new(None);
    let problem = OdeBuilder::<FaerMat<f64>>::new()
        .t0(config.t0)
        .h0(config.h0)
        .rtol(config.rtol)
        .atol(vec![config.atol; n])
        .rhs_implicit(
            move |y, _p, t, out| {
                let value = callback_or_abort(
                    request(&rhs_rpc, "rhs", t, y).and_then(|v| vector_value(&v, n)),
                );
                out.copy_from_slice(&value);
            },
            move |y, _p, t, v, out| {
                callback_or_abort(valid_vector(v, n, "Diffsol JVP direction"));
                let mut cache = callback_or_abort(
                    cache
                        .lock()
                        .map_err(|_| "Jacobian cache mutex poisoned".into()),
                );
                let y_bits: Vec<u64> = y.iter().map(|v| v.to_bits()).collect();
                let matched = cache
                    .as_ref()
                    .is_some_and(|c| c.t_bits == t.to_bits() && c.y_bits == y_bits);
                {
                    let mut channel = callback_or_abort(
                        jac_rpc
                            .lock()
                            .map_err(|_| "RPC channel mutex poisoned".into()),
                    );
                    channel.counters.diffsol_jvp_calls += 1;
                    if matched {
                        channel.counters.diffsol_jacobian_cache_hits += 1;
                    }
                }
                if !matched {
                    let matrix = callback_or_abort(
                        request(&jac_rpc, "jacobian", t, y).and_then(|v| matrix_value(&v, n)),
                    );
                    *cache = Some(CachedJacobian {
                        t_bits: t.to_bits(),
                        y_bits,
                        matrix,
                    });
                }
                let matrix = &cache.as_ref().expect("initialized Jacobian cache").matrix;
                for i in 0..n {
                    out[i] = matrix[i].iter().zip(v).map(|(a, b)| a * b).sum();
                }
                callback_or_abort(valid_vector(out, n, "Diffsol JVP result"));
            },
        )
        .init(move |_p, _t, out| out.copy_from_slice(&initial), n)
        .build()
        .map_err(|e| e.to_string())?;
    let mut solver = problem.bdf::<FaerLU<f64>>().map_err(|e| e.to_string())?;
    solver.config_mut().minimum_timestep = config.h_min;
    let requested = config.times();
    let mut times = vec![config.t0];
    let mut states = vec![config.y0.clone()];
    let mut accepted = AcceptedPath::default();
    accepted.observe(config.t0, &config.y0)?;
    let mut next_output = 1usize;
    let mut steps = 0usize;
    let mut max_observed_step = 0.0_f64;
    let mut message = "maximum step count reached".to_string();
    while solver.state().t < config.t1 && steps < config.max_steps {
        let before = solver.state().t;
        // Diffsol exposes stop times, not a maximum-step field. This explicit
        // rolling stop is independent of the observation grid.
        let mut stop = (before + config.h_max).min(config.t1);
        if stop - before > config.h_max {
            stop = stop.next_down();
        }
        if stop <= before {
            return Err("h_max does not advance represented time".into());
        }
        solver.set_stop_time(stop).map_err(|e| e.to_string())?;
        let reason = solver.step().map_err(|e| e.to_string())?;
        steps += 1;
        let after = solver.state().t;
        if !after.is_finite() || after <= before || after > config.t1 {
            return Err("Diffsol did not advance inside the frozen segment".into());
        }
        if after - before > config.h_max {
            return Err("Diffsol represented step exceeded h_max".into());
        }
        max_observed_step = max_observed_step.max(after - before);
        let accepted_state = (0..n).map(|i| solver.state().y[i]).collect::<Vec<_>>();
        valid_vector(&accepted_state, n, "Diffsol accepted state")?;
        accepted.observe(after, &accepted_state)?;
        if matches!(reason, OdeSolverStopReason::RootFound(..)) {
            return Err("unexpected Diffsol root event without a registered root".into());
        }
        while next_output < requested.len() && requested[next_output] <= after {
            let t = requested[next_output];
            let value = if t == after {
                (0..n).map(|i| solver.state().y[i]).collect::<Vec<_>>()
            } else {
                let y = solver.interpolate(t).map_err(|e| e.to_string())?;
                (0..n).map(|i| y[i]).collect::<Vec<_>>()
            };
            valid_vector(&value, n, "Diffsol output")?;
            times.push(t);
            states.push(value);
            next_output += 1;
        }
        if after == config.t1 {
            message = "success".into();
        }
    }
    let success = solver.state().t == config.t1 && next_output == requested.len();
    let counters = serde_json::to_value(solver.get_statistics()).map_err(|e| e.to_string())?;
    Ok(json!({
        "type":"result", "ok":true, "method":config.method, "diffsol_version":DIFFSOL_VERSION,
        "times":times, "states":states, "success":success, "message":message,
        "counters":counters, "internal_steps":steps, "output_clipped_steps":0,
        "accepted_times":accepted.times, "accepted_states":accepted.states,
        "accepted_grid_complete":success,
        "accepted_grid_origin":"direct Diffsol state after each successful step call",
        "max_steps_semantics":"outer accepted-step calls; internal retries in solver counters",
        "h_max_policy":"rolling hard-stop cap, independent of output grid",
        "max_observed_step":max_observed_step,
        "output_policy":"BDF interpolation of accepted intervals; exact final stop",
        "precision":"binary64", "jacobian_policy":"parent full Jacobian; exact (t,y) bit cache for JVP",
    }))
}

fn run_diffsol(config: &Config, rpc: &SharedChannel) -> Result<Value, String> {
    match catch_unwind(AssertUnwindSafe(|| run_diffsol_inner(config, rpc))) {
        Ok(result) => result,
        Err(payload) => {
            if let Some(abort) = payload.downcast_ref::<CallbackAbort>() {
                Err(format!("Diffsol callback aborted: {}", abort.0))
            } else {
                Err("Diffsol panicked; inspect retained stderr".into())
            }
        }
    }
}

fn validate_complete(result: &Value, config: &Config) -> Result<bool, String> {
    if result["ok"] != true {
        return Ok(false);
    }
    let times: Vec<f64> =
        serde_json::from_value(result["times"].clone()).map_err(|e| e.to_string())?;
    let states: Vec<Vec<f64>> =
        serde_json::from_value(result["states"].clone()).map_err(|e| e.to_string())?;
    if times.len() != states.len() {
        return Err("solver output time/state count mismatch".into());
    }
    for state in &states {
        valid_vector(state, config.dimension, "solver output")?;
    }
    if times
        != config
            .times()
            .into_iter()
            .take(times.len())
            .collect::<Vec<_>>()
    {
        return Err("solver output is not an exact requested-grid prefix".into());
    }
    if result["success"] == true && times != config.times() {
        return Err("solver success omitted requested outputs".into());
    }
    Ok(result["success"] == true && times == config.times())
}

fn main() -> ExitCode {
    // This hook suppresses only the deliberately caught typed RPC abort.
    let old_hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |info| {
        if !info.payload().is::<CallbackAbort>() {
            old_hook(info);
        }
    }));
    let mut writer = io::stdout();
    if write_json(
        &mut writer,
        &json!({"type":"hello", "protocol":PROTOCOL,
        "vigilode_commit":VIGILODE_COMMIT, "diffsol_version":DIFFSOL_VERSION,
        "methods":["vigilode-rodas5p","diffsol-bdf"]}),
    )
    .is_err()
    {
        return ExitCode::FAILURE;
    }
    let mut reader = BufReader::new(io::stdin());
    let parsed = read_line(&mut reader)
        .and_then(|line| {
            serde_json::from_str::<Config>(&line).map_err(|e| format!("invalid config: {e}"))
        })
        .and_then(|config| {
            config.validate()?;
            Ok(config)
        });
    let config = match parsed {
        Ok(config) => config,
        Err(error) => {
            let _ = write_json(
                &mut writer,
                &json!({"type":"result","ok":false,"error":error}),
            );
            return ExitCode::FAILURE;
        }
    };
    let rpc = Arc::new(Mutex::new(Channel {
        reader,
        writer,
        dimension: config.dimension,
        t0: config.t0,
        t1: config.t1,
        counters: RpcCounters::default(),
        failure: None,
        pending_request: None,
    }));
    let result = if config.method == "vigilode-rodas5p" {
        run_vigilode(&config, &rpc)
    } else {
        run_diffsol(&config, &rpc)
    };
    let mut complete = false;
    let mut result = match result {
        Ok(value) => match validate_complete(&value, &config) {
            Ok(ok) => {
                complete = ok;
                value
            }
            Err(error) => json!({"type":"result","ok":false,"error":error}),
        },
        Err(error) => json!({"type":"result","ok":false,"error":error}),
    };
    let mut channel = match rpc.lock() {
        Ok(channel) => channel,
        Err(poisoned) => poisoned.into_inner(),
    };
    result["rpc_counters"] = json!(channel.counters);
    result["pending_request"] = json!(channel.pending_request);
    result["callback_failure"] = json!(channel.failure);
    result["complete_output"] = json!(complete);
    result["protocol"] = json!(PROTOCOL);
    let written = write_json(&mut channel.writer, &result).is_ok();
    if complete && written {
        ExitCode::SUCCESS
    } else {
        ExitCode::FAILURE
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Cursor;

    fn config() -> Config {
        Config {
            protocol: PROTOCOL.into(),
            dimension: 2,
            t0: 0.0,
            t1: 1.0,
            y0: vec![1.0, 1.0],
            rtol: 1e-8,
            atol: 1e-11,
            h0: 1e-4,
            h_min: 1e-15,
            h_max: 0.1,
            max_steps: 10000,
            method: "vigilode-rodas5p".into(),
            output_times: None,
        }
    }

    #[test]
    fn rejects_invalid_time_and_control_contract() {
        let mut c = config();
        assert!(c.validate().is_ok());
        c.t1 = c.t0;
        assert!(c.validate().is_err());
        let mut c = config();
        c.h0 = 2.0 * c.h_max;
        assert!(c.validate().is_err());
        let mut c = config();
        c.atol = 0.0;
        assert!(c.validate().is_err());
        let mut c = config();
        c.y0[0] = f64::NAN;
        assert!(c.validate().is_err());
    }

    #[test]
    fn output_grid_must_include_both_exact_endpoints() {
        let mut c = config();
        c.output_times = Some(vec![0.0, 0.3, 1.0]);
        assert!(c.validate().is_ok());
        c.output_times = Some(vec![0.0, 0.3, 0.3, 1.0]);
        assert!(c.validate().is_err());
        c.output_times = Some(vec![0.0, 0.999]);
        assert!(c.validate().is_err());
    }

    #[test]
    fn response_identity_and_failure_are_strict() {
        assert!(response_value(r#"{"id":2,"ok":true,"value":[1]}"#, 1).is_err());
        assert!(
            response_value(r#"{"id":1,"ok":false,"error":"native refused"}"#, 1)
                .unwrap_err()
                .contains("native refused")
        );
        assert!(response_value(r#"{"id":1,"ok":true,"value":[1],"error":"bad"}"#, 1).is_err());
        assert!(response_value(r#"{"id":1,"ok":true,"value":[1],"extra":0}"#, 1).is_err());
    }

    #[test]
    fn validates_matrix_shape_and_finiteness() {
        assert!(matrix_value(&json!([[1.0, 0.0], [0.0, 1.0]]), 2).is_ok());
        assert!(matrix_value(&json!([[1.0], [0.0]]), 2).is_err());
        assert!(matrix_value(&json!([[1.0, 0.0]]), 2).is_err());
        assert!(vector_value(&json!([null, 1.0]), 2).is_err());
    }

    #[test]
    fn failed_rpc_is_preserved_and_never_retried() {
        let mut rpc = Channel {
            reader: Cursor::new(
                b"{\"id\":1,\"ok\":false,\"error\":\"provider failure\"}\n".to_vec(),
            ),
            writer: Vec::new(),
            dimension: 2,
            t0: 0.0,
            t1: 1.0,
            counters: RpcCounters::default(),
            failure: None,
            pending_request: None,
        };
        assert!(rpc.request("rhs", 0.5, &[1.0, 2.0]).is_err());
        let bytes = rpc.writer.len();
        assert!(rpc.request("rhs", 0.5, &[1.0, 2.0]).is_err());
        assert_eq!(rpc.writer.len(), bytes);
        assert_eq!(rpc.counters.requests_attempted, 1);
        assert!(rpc.pending_request.is_some());
        assert_eq!(rpc.counters.responses_validated, 0);
    }

    #[test]
    fn outside_segment_callback_fails_before_io() {
        let mut rpc = Channel {
            reader: Cursor::new(Vec::<u8>::new()),
            writer: Vec::new(),
            dimension: 2,
            t0: 0.0,
            t1: 1.0,
            counters: RpcCounters::default(),
            failure: None,
            pending_request: None,
        };
        assert!(rpc.request("partial_t", -1e-12, &[1.0, 2.0]).is_err());
        assert!(rpc.writer.is_empty());
        assert_eq!(rpc.counters.requests_attempted, 0);
    }

    #[test]
    fn output_completeness_does_not_zip_truncate() {
        let c = config();
        let bad = json!({"ok":true,"success":true,"times":[0.0,1.0],"states":[[1.0,1.0]]});
        assert!(validate_complete(&bad, &c).is_err());
        let bad = json!({"ok":true,"success":true,"times":[0.0],"states":[[1.0,1.0]]});
        assert!(validate_complete(&bad, &c).is_err());
        let partial = json!({"ok":true,"success":false,"times":[0.0],"states":[[1.0,1.0]]});
        assert_eq!(validate_complete(&partial, &c).unwrap(), false);
    }

    #[test]
    fn diffsol_callback_abort_returns_no_dummy_value() {
        let result = catch_unwind(|| callback_or_abort::<Vec<f64>>(Err("test failure".into())));
        let payload = result.expect_err("callback must abort before returning a value");
        assert_eq!(
            payload.downcast_ref::<CallbackAbort>().unwrap().0,
            "test failure"
        );
    }

    #[test]
    fn line_protocol_requires_newline_and_preserves_binary64_roundtrip() {
        assert!(read_line(&mut Cursor::new(b"{}".to_vec())).is_err());
        let x = f64::from_bits(0x3fefffffffffffff);
        let line = serde_json::to_string(&vec![x, -0.0]).unwrap();
        let v: Vec<f64> = serde_json::from_str(&line).unwrap();
        assert_eq!(v[0].to_bits(), x.to_bits());
        assert_eq!(v[1].to_bits(), (-0.0f64).to_bits());
    }

    #[test]
    fn accepted_observer_deduplicates_retries_without_changing_grid() {
        let mut path = AcceptedPath::default();
        path.observe(0.0, &[1.0, 0.0]).unwrap();
        path.observe(0.0, &[1.0, 0.0]).unwrap();
        path.observe(0.25, &[0.8, 0.1]).unwrap();
        assert_eq!(path.times, vec![0.0, 0.25]);
        assert!(path.observe(0.25, &[0.8, 0.2]).is_err());
        assert!(path.observe(0.1, &[0.9, 0.05]).is_err());
    }
}
