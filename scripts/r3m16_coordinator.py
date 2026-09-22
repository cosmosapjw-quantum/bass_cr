"""Finite R3M16 orchestration for target-only diagnostics and A1/B1 collisions."""
import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time

SOURCE = "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b"
SCIENCE = "/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python"
REPO = Path(__file__).resolve().parents[1]
R3M15_ROOT = Path("/mnt/sn850x2t/bass_cr_r3m15_20260922")
JOBS = {"A1": ("A", 0.25), "B1": ("B", 0.20)}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def validate_config(job, cfg):
    if job not in JOBS:
        raise ValueError("only A1/B1 are authorized")
    old, dx = JOBS[job]
    expected = json.loads((REPO / "configs/r3m15" / f"{old}.json").read_text())
    expected["dt"] = 0.025
    if expected["grid"]["dx"] != dx or cfg != expected:
        raise ValueError("frozen A1/B1 config mismatch")


def preparation_config(cfg):
    return json.loads(json.dumps(cfg))


def collision_argv(config, prepared, output, max_steps):
    return [SCIENCE, "scripts/r3m14_collision_initial_witness.py", "--config", str(config),
            "--prepared", str(prepared), "--out", str(output), "--max-steps", str(max_steps)]


def assert_fresh_job(path):
    if Path(path).exists():
        raise FileExistsError("preserve existing failed/partial/completed job; reconcile before continuation")


def gpu_memory():
    text = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"], text=True)
    return tuple(map(int, text.strip().splitlines()[0].split(",")))


def verify_seal(output):
    seal = json.loads((output / "r3m11_checkpoint_seal.json").read_text())
    if seal["source_digest"] != SOURCE or set(seal["files"]) != {"state.npy", "state.json"}:
        raise ValueError("checkpoint seal identity mismatch")
    for name, digest in seal["files"].items():
        if sha(output / name) != digest:
            raise ValueError("corrupted checkpoint: " + name)
    state = json.loads((output / "state.json").read_text())
    if not math.isfinite(state["norm"]):
        raise ValueError("nonfinite checkpoint norm")
    return state


def command(label, argv, jobroot, *, timeout=7200, memory_guard=True):
    import mlflow
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(REPO), OPENBLAS_NUM_THREADS="1",
               OMP_NUM_THREADS="1", LD_LIBRARY_PATH="/home/cosmosapjw/cosmo_lab/.venv/lib/python3.12/site-packages/nvidia/cufft/lib")
    baseline = gpu_memory()[0] if memory_guard else 0
    start = time.time(); peak = baseline; stop_reason = None
    with mlflow.start_span(name=label) as span:
        span.set_inputs({"argv": argv, "cwd": str(REPO)})
        with (jobroot / (label + ".stdout")).open("x") as stdout, (jobroot / (label + ".stderr")).open("x") as stderr:
            process = subprocess.Popen(argv, cwd=REPO, env=env, stdout=stdout, stderr=stderr)
            while process.poll() is None:
                if memory_guard:
                    used, total = gpu_memory(); peak = max(peak, used)
                    if total - used < 1536:
                        stop_reason = "RESOURCE_HEADROOM_BREACH"
                if time.time() - start > timeout:
                    stop_reason = "BOUNDED_COMMAND_TIMEOUT"
                if stop_reason:
                    process.terminate()
                    try: process.wait(timeout=15)
                    except subprocess.TimeoutExpired: process.kill(); process.wait()
                    break
                time.sleep(2)
            returncode = process.wait()
        record = {"label": label, "argv": argv, "returncode": returncode,
                  "seconds": time.time() - start, "gpu_baseline_used_mib": baseline,
                  "gpu_peak_total_used_mib_sampled": peak, "stop_reason": stop_reason,
                  "scientific_interpreter": SCIENCE, "trace_id": span.trace_id}
        span.set_outputs(record)
    mlflow.flush_trace_async_logging()
    trace = mlflow.get_trace(record["trace_id"])
    record["verified_trace_spans"] = len(trace.data.spans) if trace else 0
    write_new(jobroot / "receipts" / (label + ".json"), record)
    print(json.dumps(record), flush=True)
    if returncode or stop_reason:
        raise RuntimeError(f"{label}: exit={returncode}; {stop_reason}")


def run_target_only(root):
    target = root / "target_only"
    assert_fresh_job(target); target.mkdir(); (target / "receipts").mkdir()
    cases = {
        "A": (REPO / "configs/r3m15/A.json", R3M15_ROOT / "A/preparation", R3M15_ROOT / "A/collision/result.json"),
        "B": (REPO / "configs/r3m15/B.json", R3M15_ROOT / "B/preparation", R3M15_ROOT / "B/collision/result.json"),
        "B_refined": (REPO / "configs/r3m15/B.json", R3M15_ROOT / "B_preparation_refinement/preparation", R3M15_ROOT / "B/collision/result.json"),
    }
    try:
        for case, (config, prepared, result) in cases.items():
            argv = [SCIENCE, "scripts/r3m16_target_only_hdt.py", "--config", str(config),
                     "--prepared", str(prepared), "--collision-result", str(result),
                     "--out", str(target / (case + ".json")), "--horizon", "1.0"]
            if case == "B_refined": argv.append("--one-step-only")
            command("target_only_" + case, argv, target)
        summaries = {case: json.loads((target / (case + ".json")).read_text()) for case in cases}
        if any(summaries[case]["status"] != "COMPLETE" or summaries[case]["fixed_horizon"]["empirical_order"]["status"] in {"INVALID", "NONMONOTONE", "UNRESOLVED"} for case in ("A", "B")):
            raise ValueError("target-only temporal ladder structurally unresolved")
        if summaries["B_refined"]["status"] != "COMPLETE" or summaries["B_refined"]["fixed_horizon"] is not None:
            raise ValueError("B refined control must remain one-step-only")
        write_new(target / "COMPLETE.json", {"status": "COMPLETE", "cases": list(cases),
                  "collision_execution_authorized_by_this_receipt": False})
    except BaseException as exc:
        if not (target / "FAILURE.json").exists():
            write_new(target / "FAILURE.json", {"type": type(exc).__name__, "message": str(exc), "retry_executed": False})
        raise


def run_collision(job, root):
    config_path = REPO / "configs/r3m16" / f"{job}.json"
    config = json.loads(config_path.read_text()); validate_config(job, config)
    jobroot = root / job; assert_fresh_job(jobroot); jobroot.mkdir(); (jobroot / "receipts").mkdir()
    shutil.copy2(config_path, jobroot / "config.json")
    write_new(jobroot / "start.json", {"job": job, "config_sha256": sha(config_path),
              "numerical_source_digest": SOURCE, "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
              "instrumentation": {path.name: sha(path) for path in [Path(__file__), REPO / "scripts/r3m13_initial_state_pair.py", REPO / "scripts/r3m14_collision_initial_witness.py"]}})
    try:
        command("resource_preflight", [SCIENCE, "scripts/r3m15_resource_probe.py", "--config", str(config_path), "--out", str(jobroot / "resource.json")], jobroot)
        command("prepare", [SCIENCE, "scripts/r3m13_initial_state_pair.py", "prepare", "--config", str(config_path), "--out", str(jobroot / "preparation")], jobroot)
        for name in ("initial.npy", "receipt.json", "attempt.json"):
            (jobroot / "preparation" / name).chmod(0o444)
        for chunk in range(1, 16):
            output = jobroot / "collision"; label = f"collision.chunk{chunk:03d}"
            if chunk > 1: verify_seal(output)
            command(label, collision_argv(config_path, jobroot / "preparation", output, 128), jobroot)
            state = verify_seal(output)
            witness = json.loads((output / "r3m14_initial_binding.json").read_text())
            if witness["status"] != "PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED":
                raise ValueError("initial binding failure")
            write_new(jobroot / "receipts" / f"{label}.checkpoint.json",
                      {name: {"sha256": sha(output / name), "content": json.loads((output / name).read_text())}
                       for name in ["state.json", "r3m11_checkpoint_seal.json", "r3m14_initial_binding.json", "r3m14_witness_run_receipt.json"]})
            if (output / "result.json").exists():
                result = json.loads((output / "result.json").read_text())
                if result["status"] != "completed" or state["done"] != state["nstep"]:
                    raise ValueError("invalid completion")
                write_new(jobroot / "COMPLETE.json", {"job": job, "chunks": chunk, "restarts": chunk - 1,
                          "nstep": state["done"], "result_sha256": sha(output / "result.json")})
                return
        raise RuntimeError("fifteen chunk maximum reached")
    except BaseException as exc:
        if not (jobroot / "FAILURE.json").exists():
            write_new(jobroot / "FAILURE.json", {"type": type(exc).__name__, "message": str(exc), "retry_executed": False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["target-only", "collision"], required=True)
    parser.add_argument("--job", choices=list(JOBS))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(); root = args.root.resolve(); root.mkdir(exist_ok=True)
    import mlflow
    if not (os.environ.get("MLFLOW_TRACKING_URI") and os.environ.get("MLFLOW_EXPERIMENT_ID")):
        mlflow.set_tracking_uri("sqlite:///" + str(root / "mlflow.db")); mlflow.set_experiment("R3M16_HDT_REPRESENTATION")
    with (root / "gpu.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.phase == "target-only":
            run_target_only(root)
        else:
            if not args.job: raise ValueError("--job is required for collision")
            if not (root / "target_only/COMPLETE.json").is_file(): raise ValueError("target-only diagnostics must complete first")
            if args.job == "B1" and not (root / "A1/COMPLETE.json").is_file(): raise ValueError("A1 must complete first")
            run_collision(args.job, root)


if __name__ == "__main__":
    main()
