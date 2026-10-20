"""C21H: reuse the private, source-pinned C21G RHS with a Rust solver callback.

Only the private module's solve_ivp binding changes. Scientific source files,
event ordering, state reduction, original RHS and ledger accumulation remain.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time
from types import SimpleNamespace
import uuid
import numpy as np

REFERENCE_SHA256 = "714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0"
VIGILODE_COMMIT = "8a8bd409b1d96c7b7421f496d229e119fd3d284e"
METHODS = ("vigilode-rodas5p", "diffsol-bdf")

class AdapterError(RuntimeError):
    pass

def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def write_new_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + "." + uuid.uuid4().hex + ".partial")
    try:
        with part.open("x") as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.link(part, path)
    finally:
        part.unlink(missing_ok=True)

def private_reference(source_dir):
    source_dir = Path(source_dir).resolve()
    path = source_dir / "src/reference_tau.py"
    if file_hash(path) != REFERENCE_SHA256:
        raise AdapterError("C21G_REFERENCE_SOURCE_MISMATCH")
    src = str(source_dir / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    for name in ("event_coupler", "native_micro", "run_experiment"):
        if name in sys.modules and Path(sys.modules[name].__file__).resolve() != source_dir / "src" / (name + ".py"):
            raise AdapterError("IMPORTED_SOURCE_DIRECTORY_MISMATCH " + name)
    spec = importlib.util.spec_from_file_location("_c21h_reference_" + uuid.uuid4().hex, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def derivative_weights(offsets):
    """Derivative at zero of the quadratic through actual represented nodes."""
    d1, d2 = map(float, offsets)
    if not (math.isfinite(d1) and math.isfinite(d2)) or d1 == 0 or d2 == 0 or d1 == d2:
        raise AdapterError("FD_DISTINCT_REPRESENTED_NODES_REQUIRED")
    w = np.array([-(d1+d2)/(d1*d2), -d2/(d1*(d1-d2)), d1/(d2*(d1-d2))])
    if not np.isfinite(w).all():
        raise AdapterError("FD_WEIGHT_NONFINITE")
    return w

class CellCallbacks:
    """Original RHS; analytic tau columns, exact passive zeros, gas/time FD."""
    def __init__(self, fun, fixture, lo, hi, scales, dynamic, reference,
                 fd_relative=np.finfo(float).eps**(1/3), time_fd_fraction=1e-4):
        from event_coupler import state_valid
        self.fun, self.f, self.lo, self.hi = fun, fixture, float(lo), float(hi)
        self.scales, self.dynamic = np.asarray(scales, float), np.asarray(dynamic, int)
        self.ref, self.state_valid = reference, state_valid
        self.m, self.n = len(fixture.q), len(dynamic)
        self.active = np.asarray(fixture.birth) <= lo
        self.left, self.right = lo+1e-9*(hi-lo), hi-1e-9*(hi-lo)
        self.fd_relative, self.time_fd_fraction = float(fd_relative), float(time_fd_fraction)
        if not (0 < self.fd_relative < .01 and 0 < self.time_fd_fraction < .1):
            raise AdapterError("FD_CONTROL_DOMAIN")
        # The original 1e-9 inset can round to an endpoint on a short cell.
        # Preserve that represented clamp exactly; require a nonempty interior.
        if not lo <= self.left < self.right <= hi:
            raise AdapterError("EVENT_CELL_TIME_RESOLUTION")
        self.counts = {k: 0 for k in ("rhs_requests", "jacobian_requests", "partial_t_requests",
            "original_rhs_evaluations", "gas_fd_columns", "gas_fd_one_sided_columns",
            "time_fd_one_sided", "time_flat_branch", "analytic_tau_columns", "exact_passive_columns")}
        self.fd_nodes = []

    def physical(self, t, z):
        z = np.asarray(z, float)
        if z.shape != (self.n,) or not np.isfinite(z).all() or not math.isfinite(t):
            raise AdapterError("CALLBACK_SHAPE_OR_FINITE")
        if not self.lo <= t <= self.hi:
            raise AdapterError("CALLBACK_OUTSIDE_EVENT_CELL")
        with np.errstate(over="ignore", invalid="ignore"):
            u = z*self.scales
        if not np.isfinite(u).all() or not self.state_valid(self.full(u)[self.m:self.m+4],self.f.Y):
            raise AdapterError("PHYSICAL_CALLBACK_STATE_DOMAIN")
        return u

    def original(self, t, u):
        self.counts["original_rhs_evaluations"] += 1
        result = np.asarray(self.fun(float(t), np.asarray(u, float)), float)
        if result.shape != (self.n,) or not np.isfinite(result).all():
            raise AdapterError("ORIGINAL_RHS_RESULT_DOMAIN")
        return result

    def full(self, u):
        full = np.zeros(self.m+19); full[self.dynamic] = u
        return full

    def rhs(self, t, z):
        self.counts["rhs_requests"] += 1
        return self.original(t, self.physical(t, z))/self.scales

    def gas_nodes(self, u, j):
        desired = self.fd_relative*max(abs(float(u[j])), self.scales[j])
        for k in range(24):
            nodes = {}
            for multiple in (-2, -1, 1, 2):
                v = u.copy(); v[j] = float(u[j])+multiple*math.ldexp(desired, -k)
                if v[j] != u[j] and np.isfinite(v[j]) and self.state_valid(self.full(v)[self.m:self.m+4], self.f.Y):
                    nodes[multiple] = v
            if -1 in nodes and 1 in nodes:
                return nodes[-1], nodes[1], "central"
            for sign in (1, -1):
                if sign in nodes and 2*sign in nodes:
                    return nodes[sign], nodes[2*sign], "one_sided"
        raise AdapterError("NO_ADMISSIBLE_GAS_FD_STENCIL")

    def jacobian(self, t, z):
        from event_coupler import H, BIND_EV, alpha, event_fractions
        from run_experiment import opacity
        self.counts["jacobian_requests"] += 1
        u = self.physical(t, z); full = self.full(u); base = self.original(t, u)
        out = np.zeros((self.m+19, self.m+19))
        xx = min(max(t, self.left), self.right)
        energy, k = opacity(self.f, xx)
        pop, _ = self.ref.reconstruct_population(self.f.amounts, full[:self.m], self.active)
        rates = pop[:,None]*k*alpha(full[self.m:self.m+4], self.f.Y)[None,:]
        hubble = H(xx)
        for j in range(self.m):
            species = -rates[j]
            heat = float(np.sum(species*(energy[j]-np.asarray(BIND_EV))))
            out[self.m:self.m+3,j] = event_fractions(species, self.f.Y)/hubble
            out[self.m+3,j] = out[self.m+18,j] = heat/hubble
            out[self.m+4:self.m+7,j] = species/hubble
            out[self.m+16,j] = -pop[j]*energy[j]
        reduced = out[np.ix_(self.dynamic, self.dynamic)]
        for j, full_index in enumerate(self.dynamic):
            if not self.m <= full_index < self.m+4:
                continue
            first, second, kind = self.gas_nodes(u, j)
            offsets = (float(first[j]-u[j]), float(second[j]-u[j]))
            w = derivative_weights(offsets)
            reduced[:,j] = w[1]*(self.original(t, first)-base)+w[2]*(self.original(t, second)-base)
            self.counts["gas_fd_columns"] += 1
            self.counts["gas_fd_one_sided_columns"] += int(kind == "one_sided")
            self.fd_nodes.append({"kind":"gas", "time":t, "full_index":int(full_index),
                                  "offsets":list(offsets), "stencil":kind})
        self.counts["analytic_tau_columns"] += self.m
        self.counts["exact_passive_columns"] += 15
        result = reduced*self.scales[None,:]/self.scales[:,None]
        if not np.isfinite(result).all():
            raise AdapterError("JACOBIAN_NONFINITE")
        return result

    def partial_t(self, t, z):
        self.counts["partial_t_requests"] += 1
        u = self.physical(t, z)
        if t <= self.left or t >= self.right:
            self.counts["time_flat_branch"] += 1
            return np.zeros(self.n)
        desired = self.time_fd_fraction*(self.hi-self.lo)
        for k in range(24):
            candidates = {}
            for multiple in (-2, -1, 1, 2):
                node = t+multiple*math.ldexp(desired,-k)
                if self.left < node < self.right and node != t:
                    candidates[multiple] = node
            if -1 in candidates and 1 in candidates:
                nodes, kind = (candidates[-1],candidates[1]), "central"; break
            signs = (1,-1) if self.right-t >= t-self.left else (-1,1)
            found = next((s for s in signs if s in candidates and 2*s in candidates),None)
            if found is not None:
                nodes, kind = (candidates[found],candidates[2*found]), "one_sided"; break
        else:
            raise AdapterError("NO_INTERIOR_TIME_FD_STENCIL")
        offsets = [node-t for node in nodes]; w = derivative_weights(offsets)
        base = self.original(t,u)
        result = (w[1]*(self.original(nodes[0],u)-base)+w[2]*(self.original(nodes[1],u)-base))/self.scales
        self.counts["time_fd_one_sided"] += int(kind == "one_sided")
        self.fd_nodes.append({"kind":"time", "time":t, "nodes":list(nodes), "offsets":offsets, "stencil":kind})
        if not np.isfinite(result).all():
            raise AdapterError("PARTIAL_T_NONFINITE")
        return result

def run_segment(binary, config, callbacks, output, timeout=300., rpc_limit=200000,
                log_byte_limit=256*1024*1024):
    """A fresh, bounded process group; each request/response is preserved."""
    output = Path(output); output.mkdir(parents=True,exist_ok=False)
    write_new_json(output/"config.json",config)
    binary = Path(binary).resolve()
    identity = {"path":str(binary),"sha256":file_hash(binary),"bytes":binary.stat().st_size}
    write_new_json(output/"binary.json",identity)
    start = time.monotonic(); process = None; buffer = bytearray(); seq = logged = 0; terminal = None
    with (output/"stderr.log").open("x") as stderr, (output/"rpc.jsonl").open("x") as log:
        selector = selectors.DefaultSelector()
        def record(direction,value):
            nonlocal logged
            row = json.dumps({"direction":direction,"message":value},allow_nan=False)+"\n"
            logged += len(row.encode())
            if logged > log_byte_limit: raise AdapterError("RPC_RAW_BYTE_BUDGET")
            log.write(row); log.flush()
        def receive():
            while b"\n" not in buffer:
                remaining = timeout-(time.monotonic()-start)
                if remaining <= 0 or not selector.select(remaining): raise AdapterError("RUST_SEGMENT_WALL_TIMEOUT")
                block = os.read(process.stdout.fileno(),65536)
                if not block: raise AdapterError("RUST_PROTOCOL_EOF")
                buffer.extend(block)
                if len(buffer) > 64*1024*1024: raise AdapterError("RUST_PROTOCOL_LINE_BUDGET")
            raw,_,tail = buffer.partition(b"\n"); buffer[:] = tail
            value = json.loads(raw,parse_constant=lambda token: (_ for _ in ()).throw(AdapterError("NONFINITE_JSON "+token)))
            if not isinstance(value,dict): raise AdapterError("RUST_PROTOCOL_OBJECT_REQUIRED")
            record("rust_to_python",value); return value
        def send(value):
            record("python_to_rust",value)
            process.stdin.write((json.dumps(value,allow_nan=False)+"\n").encode()); process.stdin.flush()
        try:
            process = subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                       stderr=stderr,bufsize=0,start_new_session=True)
            selector.register(process.stdout,selectors.EVENT_READ)
            hello = receive()
            if hello.get("type") != "hello" or hello.get("protocol") != "C21H_V1" or hello.get("vigilode_commit") != VIGILODE_COMMIT:
                raise AdapterError("RUST_HANDSHAKE_IDENTITY")
            send(config)
            while True:
                message = receive()
                if message.get("type") == "result": terminal = message; break
                seq += 1
                if seq > rpc_limit or message.get("type") != "request" or message.get("id") != seq:
                    raise AdapterError("RPC_SEQUENCE_OR_BUDGET")
                op = message.get("op")
                if op not in ("rhs","jacobian","partial_t"): raise AdapterError("RPC_OPERATION")
                try:
                    value = getattr(callbacks,op)(message["t"],message["y"])
                    send({"id":seq,"ok":True,"value":np.asarray(value).tolist()})
                except Exception as error:
                    send({"id":seq,"ok":False,"error":type(error).__name__+": "+str(error)}); raise
            process.wait(timeout=max(.001,timeout-(time.monotonic()-start)))
            if not terminal.get("ok") or not terminal.get("success") or process.returncode != 0:
                raise AdapterError("RUST_SOLVER_FAILED "+json.dumps(terminal))
            if file_hash(binary) != identity["sha256"]: raise AdapterError("RUST_BINARY_CHANGED_DURING_JOB")
            write_new_json(output/"result.json",terminal)
            write_new_json(output/"receipt.json",{"status":"COMPLETE","exit_code":process.returncode,
                "rpc_requests":seq,"raw_bytes":logged,"wall_s":time.monotonic()-start,
                "binary":identity,"callbacks":callbacks.counts})
            return terminal
        except BaseException as error:
            write_new_json(output/"failure.json",{"status":"FAILED","error_class":type(error).__name__,
                "error":str(error),"terminal":terminal,"rpc_requests":seq,"wall_s":time.monotonic()-start,
                "callbacks":callbacks.counts})
            raise
        finally:
            if process is not None:
                # This pinned bridge does not launch child processes. Signal
                # only a still-running owned process group, before reaping it.
                if process.poll() is None:
                    try: os.killpg(process.pid,signal.SIGTERM)
                    except ProcessLookupError: pass
                    try: process.wait(timeout=.5)
                    except subprocess.TimeoutExpired:
                        try: os.killpg(process.pid,signal.SIGKILL)
                        except ProcessLookupError: pass
                process.wait()
                for stream in (process.stdin,process.stdout):
                    if stream is not None: stream.close()
            selector.close()
            write_new_json(output/"process_exit.json",{"exit_code":None if process is None else process.returncode,
                "wall_s_after_cleanup":time.monotonic()-start,"process_started":process is not None})

class RustIVP:
    def __init__(self,fixture,reference,binary,out,full_scales,alpha,method="vigilode-rodas5p",
                 fd_relative=None,time_fd_fraction=1e-4,wall_s=300.,max_steps=200000):
        if method not in METHODS: raise AdapterError("RUST_METHOD")
        self.f,self.reference,self.binary,self.out = fixture,reference,binary,Path(out)
        self.method,self.alpha = method,float(alpha)
        m = len(fixture.q)
        self.dynamic = np.array([j for j in range(m+19) if not(fixture.Y == 0 and j in(m+1,m+2))])
        self.scales = np.asarray(full_scales,float)[self.dynamic]
        if self.scales.shape != (len(self.dynamic),) or not np.isfinite(self.scales).all() or np.any(self.scales<=0):
            raise AdapterError("FIXED_DIAGONAL_SCALE_DOMAIN")
        self.fd_relative = fd_relative if fd_relative is not None else np.finfo(float).eps**(1/3)
        self.time_fd_fraction,self.max_steps = time_fd_fraction,max_steps
        self.deadline = time.monotonic()+wall_s; self.segments = []
    def __call__(self,fun,t_span,y0,*,method,rtol,atol,max_step,**kwargs):
        if kwargs or method != "Radau" or not np.array_equal(np.asarray(atol),self.alpha*self.scales):
            raise AdapterError("ORIGINAL_SOLVE_IVP_CALL_CONTRACT")
        lo,hi = map(float,t_span)
        callback = CellCallbacks(fun,self.f,lo,hi,self.scales,self.dynamic,self.reference,
                                 self.fd_relative,self.time_fd_fraction)
        output = self.out/("segment_%03d"%len(self.segments))
        config = {"protocol":"C21H_V1","dimension":len(self.dynamic),"t0":lo,"t1":hi,
            "y0":(np.asarray(y0)/self.scales).tolist(),"rtol":float(rtol),"atol":self.alpha,
            "h0":min(float(max_step),(hi-lo)/32),"h_min":math.ulp(max(abs(lo),abs(hi))),
            "h_max":float(max_step),"max_steps":self.max_steps,"method":self.method}
        remaining = self.deadline-time.monotonic()
        if remaining <= 0: raise AdapterError("RUST_JOB_WALL_BUDGET")
        try:
            result = run_segment(self.binary,config,callback,output,timeout=remaining)
        finally:
            write_new_json(output/"derivative_nodes.json",callback.fd_nodes)
        if not result.get("accepted_grid_complete"): raise AdapterError("INCOMPLETE_ACCEPTED_TRACE")
        times,states = np.asarray(result["accepted_times"],float),np.asarray(result["accepted_states"],float)
        if times.ndim != 1 or len(times)<2 or states.shape != (len(times),len(self.dynamic)):
            raise AdapterError("RUST_RETURN_GRID_SHAPE")
        if not np.isfinite(times).all() or not np.isfinite(states).all() or not np.all(np.diff(times)>0):
            raise AdapterError("RUST_RETURN_GRID_DOMAIN")
        if times[0] != lo or times[-1] != hi or not np.array_equal(states[0],np.asarray(config["y0"])):
            raise AdapterError("RUST_RETURN_ENDPOINT_OR_INITIAL_IDENTITY")
        if len(times) != result["internal_steps"]+1: raise AdapterError("ACCEPTED_STEP_COUNT_MISMATCH")
        self.segments.append({"raw_result":result,"callbacks":dict(callback.counts),"config":config})
        counters = result.get("counters",{})
        counter_key = "direct_factorizations" if self.method == "vigilode-rodas5p" else "number_of_linear_solver_setups"
        nlu = counters.get(counter_key)
        if type(nlu) is not int or nlu < 0:
            raise AdapterError("MISSING_OR_INVALID_LINEAR_WORK_COUNTER "+counter_key)
        return SimpleNamespace(t=times,y=(states*self.scales[None,:]).T,success=True,status=0,
            message=self.method+" completed",nfev=callback.counts["rhs_requests"],
            njev=callback.counts["jacobian_requests"],
            nlu=nlu)

def run_rust_reference(fixture,provider,source_dir,binary,out,scale_contract,rtol=2e-11,
                       alpha=2e-14,max_step_divisor=8.,method="vigilode-rodas5p",
                       fd_relative=None,time_fd_fraction=1e-4,max_evaluations=200000,wall_s=300.):
    reference = private_reference(source_dir)
    backend = RustIVP(fixture,reference,binary,out,scale_contract["values"],alpha,method,
                     fd_relative,time_fd_fraction,wall_s)
    reference.solve_ivp = backend
    result = reference.run_reference_tau(fixture,provider,rtol=rtol,
        atol=[alpha*x for x in scale_contract["values"]],max_step_divisor=max_step_divisor,
        max_evaluations=max_evaluations)
    result.update(schema="C21H_SOURCE_REUSED_RUST_OPTICAL_REFERENCE_V1",
        status="CANDIDATE_CONTINUOUS_IVP_COMPLETED",rust_method=method,vigilode_commit=VIGILODE_COMMIT,
        original_reference_source_sha256=REFERENCE_SHA256,
        rhs_reuse="UNCHANGED_PRIVATE_IMPORTED_C21G_FUNCTION_AND_EVENT_LOOP",
        global_error_bound=None,rust_segments=backend.segments,accepted_state_trace_complete=True)
    result["solver_diagnostics"]["method"] = method
    result["solver_diagnostics"]["counter_note"] = "nfev=Rust RHS RPC requests; njev=Python Jacobian RPC requests; nlu=Vigilode direct_factorizations attempts or Diffsol number_of_linear_solver_setups, not identical work definitions; actual original RHS count includes explicit gas/time FD; raw Rust counters retained."
    result["independence"] = "Same original continuous RHS, event cells, kernel and tau coordinates; a separately pinned Rust integration method. Different methods and local error estimators do not imply identical accepted trajectories."
    result["tolerance_contract"].update(fixed_diagonal_scaling=scale_contract,rust_scalar_atol=alpha,
        gas_fd_relative=backend.fd_relative,time_fd_fraction=backend.time_fd_fraction,
        partial_t_policy="Original cell-clamped RHS: zero flat branches, zero branch convention at clamp corners, represented-node FD strictly inside; no cross-cell samples.",
        jacobian_policy="Analytic tau columns, exactly zero 15 passive-ledger columns, admissible represented-node quadratic FD for gas columns.")
    if file_hash(Path(source_dir)/"src/reference_tau.py") != REFERENCE_SHA256:
        raise AdapterError("C21G_REFERENCE_CHANGED_DURING_JOB")
    return result
