"""One authorized output materialization, not an acceptance campaign."""
import hashlib
import json
import time
from crossing_flux import ROOT, K, KERNEL_PATH, packet_row


def main():
    started=time.monotonic()
    frozen={"CONTRACT.json":"49f9abaa01c9385cc3708b930489f3ea3b633878ba30378f60b7b2b533b41287",
            "crossing_flux.py":"6e76afb5da9976e2aeae29eef532708c3598e533d2aa26c082571acf41384830",
            "validate.py":"6cbfd97e72e716493c61b426f26e7f2b5391b59fe17b94886e83cbdf78b35a69",
            "evidence/VALIDATION.json":"8b07ce80179608de8f004200e6ad9198052a660de11f1ec79b409509897eddc8",
            "SOURCE_MANIFEST.json":None}
    verified={}
    for name,expected in frozen.items():
        actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if expected is not None and actual!=expected:raise ValueError("FROZEN_BYTE_MISMATCH:"+name)
        verified[name]=actual
    manifest=json.loads((ROOT/"SOURCE_MANIFEST.json").read_text())
    for source in manifest["sources"]:
        actual=hashlib.sha256((ROOT/source["path"]).read_bytes()).hexdigest()
        if actual!=source["sha256"]:raise ValueError("SOURCE_BYTE_MISMATCH")
        verified[source["path"]]=actual
    contract=json.loads((ROOT/"CONTRACT.json").read_text())
    validation=json.loads((ROOT/"evidence/VALIDATION.json").read_text())
    rows=[]
    for impulse in contract["impulses_eV"]:
        graph=K.make_graph(impulse)
        if len(graph.states)>10000:raise ValueError("STATE_BUDGET")
        for epoch in contract["epochs_s"]:
            if time.monotonic()-started>120:raise ValueError("WALL_BUDGET")
            rows.append(packet_row(graph,epoch,K.sparse_evolve(graph,epoch)))
    result={"id":contract["id"],"identity":validation["identity"],
            "materialization":"RECOMPUTED_SAME_PINNED_METHOD","original_full_packet_bytes":"NOT_RETAINED",
            "clock":"elapsed gas-proper seconds","crossing_energy":"unallocated",
            "HeI_channel":"NIST singlet 2^1P; separate from 23s","rows":rows}
    payload=json.dumps(result,separators=(",",":"),allow_nan=False).encode()+b"\n"
    path=ROOT/"evidence/BOUNDARY_PACKET_RECOMPUTED.json"
    with path.open("xb") as output:output.write(payload)
    readback=path.read_bytes()
    parsed=json.loads(readback)
    observed={(r["initial_energy_eV"],r["proper_time_s"]):len(r["boundary"]) for r in parsed["rows"]}
    expected={(r["impulse_eV"],r["epoch_s"]):r["boundary_states"] for r in validation["rows"]}
    if len(parsed["rows"])!=25 or len(observed)!=25 or observed!=expected:raise ValueError("PACKET_PAIRS_OR_BOUNDARY_COUNTS")
    if readback!=payload:raise ValueError("OUTPUT_BYTE_READBACK")
    print(json.dumps({"status":"MATERIALIZED_SAME_PINNED_METHOD","output":str(path.relative_to(ROOT)),"bytes":len(readback),"sha256":hashlib.sha256(readback).hexdigest(),"verified_input_sha256":verified,"exporter_sha256":hashlib.sha256((ROOT/"materialize_packet.py").read_bytes()).hexdigest(),"readback_pairs":25,"boundary_counts_match_retained_validation":True,"acceptance_campaigns":1,"scientific_repairs":0,"packet_materialization_runs":1,"sparse_evolve_calls":25,"nonzero_time_calls":20,"wall_s":time.monotonic()-started},indent=2,allow_nan=False))


if __name__=="__main__":main()
