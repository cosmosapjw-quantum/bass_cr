#!/usr/bin/env python3
"""One independent scalar reference; no candidate module is imported.

Exact toy atomic delay integrals and an open calorimeter are independently
defined here.  Recorded J1/J2 and event ledgers provide a separate arithmetic
route to the pinned output.  This never runs the historical physical model.
"""
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent
EV = Q("1.602176634e-19")
KB = Q("1.380649e-23")
C = Q(3, 2) * KB


def read(path):
    return json.loads(path.read_text(), parse_float=str)


def decimal(x):
    with localcontext() as context:
        context.prec = 80
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def pack(x):
    if isinstance(x, Q):
        return {"numerator": str(x.numerator), "denominator": str(x.denominator), "decimal80": decimal(x)}
    if isinstance(x, list):
        return [pack(v) for v in x]
    if isinstance(x, dict):
        return {k: pack(v) for k, v in x.items()}
    return x


checks = []


def verify(label, condition, evidence=None):
    checks.append({"id": label, "passed": bool(condition), "evidence": evidence})


def near(label, observed, reference, tolerance=Q("1e-12")):
    observed, reference = Q(observed), Q(reference)
    error = abs(observed-reference)
    relative = error / abs(reference) if reference else error
    verify(label, relative <= tolerance, {"observed": observed, "reference": reference, "relative_error": relative, "tolerance": tolerance})


def atom_integrals(atoms, end, slope):
    # Each atom releases its energy at birth+lag.  Integrate the birth rate
    # slope*birth over 0 <= birth <= end-lag without calling a moment evaluator.
    endpoint = sum((mass * slope * max(end-lag, Q(0)) for lag, mass in atoms), Q(0))
    cumulative = sum((mass * slope * max(end-lag, Q(0))**2 / 2 for lag, mass in atoms), Q(0))
    return endpoint, cumulative


fixture = read(HERE / "ATOMIC_FIXTURE.json")
end = Q(fixture["T_s"])
qstar = Q(fixture["qstar"])
slope = qstar/end
bands = [[(Q(lag), Q(mass)) for lag, mass in band["atoms"]] for band in fixture["bands"]]
atoms = [pair for band in bands for pair in band]
yield_total = sum((m for _, m in atoms), Q(0))
early_mass = sum((m for lag, m in atoms if lag <= end), Q(0))
first = sum((m * max(1-lag/end, Q(0)) for lag, m in atoms), Q(0))
second = sum((m * max(1-lag/end, Q(0))**2 for lag, m in atoms), Q(0))
p, r, s = early_mass/yield_total, first/yield_total, second/yield_total
power, heat = atom_integrals(atoms, end, slope)
verify("atomic/ramp_endpoint", power == qstar*yield_total*r, {"direct": power, "moment": qstar*yield_total*r})
verify("atomic/ramp_cumulative_half_factor", heat == qstar*end*yield_total*s/2, {"direct": heat, "moment": qstar*end*yield_total*s/2})
verify("atomic/horizon_atom_has_zero_ramp_contribution", atom_integrals([(end, Q(9, 80))], end, slope) == (0, 0) and early_mass > sum((m for lag, m in atoms if lag < end), Q(0)))
verify("atomic/source_off", atom_integrals(atoms, end, Q(0)) == (0, 0))
band_outputs = [atom_integrals(band, end, slope) for band in bands]
verify("atomic/birth_linear_sum", sum(v[0] for v in band_outputs) == power and sum(v[1] for v in band_outputs) == heat)
wrong_power = sum(Q(band["energy_fraction"])*output[0] for band, output in zip(fixture["bands"], band_outputs))
verify("atomic/double_birth_weight_negative_control", wrong_power != power, {"correct": power, "double_weighted": wrong_power})
verify("atomic/p_is_not_ramp_response_negative_control", qstar*yield_total*p != power, {"pulse_fraction_formula": qstar*yield_total*p, "ramp_power": power})
verify("atomic/passive_energy_bounds", Q(0) <= heat <= qstar*end/2 and r*r <= s <= r <= p <= 1)

# Exact open calorimeter, with a deliberately appreciable population increment.
# Two cutoff arrivals have actual energies 0.01 and 0.1 eV.
n0, nc, tg = Q(153), Q(2), Q(100)
nb, ns, na = Q(5), Q(3), Q(6)
eh, ec = Q(1, 4)*EV, Q(11, 100)*EV
cv0, final_cv = C*n0, C*(n0+nc)
initial_u = cv0*tg
final_temperature = (initial_u+eh+ec)/final_cv
increment = final_temperature-tg
candidate_form = (eh+ec-C*tg*nc)/(cv0+C*nc)
verify("thermal/particle_ledger", nb+ns == na+nc)
verify("thermal/exact_energy_temperature", increment == candidate_form and final_cv*final_temperature == initial_u+eh+ec)
verify("thermal/frozen_denominator_is_only_linearized", increment != (eh+ec-C*tg*nc)/cv0)
verify("thermal/actual_cutoff_energy_negative_control", ec != Q(1, 10)*EV*nc)
verify("thermal/all_free_population_negative_control", (initial_u+eh+ec)/(C*(n0+nb+ns)) != final_temperature)
cold_increment = initial_u/final_cv-tg
verify("thermal/nonnegative_energy_does_not_imply_temperature_lower_bound", cold_increment < 0)
out_energy = Q(3)*EV
thermal_upper = (eh+ec+out_energy)/cv0
actual_out_increments = [((initial_u+eh+ec+out_energy)/(C*(n0+nc+extra)))-tg for extra in [Q(0), Q(2), Q(1000)]]
verify("thermal/energy_only_upper", all(value <= thermal_upper for value in actual_out_increments))

# Stored-record route: original pulse integrator states J1/J2, not the owner's
# H0*R/S function.  The model records share all physical-source inputs.
pulse = read(UNIT / "inputs/PULSE_RECORD.json")
paired = read(UNIT / "inputs/PAIRED_RECORD.json")
candidate = read(UNIT / "results/SOURCE_BOUND_RESPONSE.json")
contract = read(UNIT / "CONTRACT.json")["selected_scenario"]
T = Q(contract["time_s"])
nH, y, xi = (Q(contract[k]) for k in ["n_H_m3", "helium_mass_fraction_Y", "xi"])
nHe = nH*y/(4*(1-y))
cv = C*(1+xi)*(nH+nHe)
near("record/heat_capacity", candidate["gas_calorimeter"]["C_V_J_m3_K"], cv, Q("1e-48"))
record_results = []
for model in pulse["models"]:
    label = model["model"]
    scale = Q(model["physical_energy_scale_eV_m3"])
    ustar = scale*EV
    j1 = sum((Q(col["J1"]) for col in model["birth_columns"]), Q(0))
    j2 = sum((Q(col["J2"]) for col in model["birth_columns"]), Q(0))
    from_integrators = {"power": ustar*j1/T, "heat": ustar*j2}
    old = next(row for row in paired["grid_results"] if row["label"] == label)["final"]["components"]["selected_total"]
    row = next(row for row in candidate["rows"] if row["model"] == label and row["representation"] == "birth_defined")
    near(label+"/J1_power_units", row["heat_power_J_m3_s"], from_integrators["power"])
    near(label+"/J2_cumulative_units", row["cumulative_heat_J_m3"], from_integrators["heat"])
    near(label+"/original_paired_power", from_integrators["power"], old["heat_power_J_m3_s"])
    near(label+"/original_paired_heat", from_integrators["heat"], old["heat_J_m3"])
    cut_n, cut_e = Q(old["cutoff_number_m3"]), Q(old["cutoff_energy_J_m3"])
    final_temp = (cv*100+from_integrators["heat"]+cut_e)/(cv+C*cut_n)
    near(label+"/thermal_prescribed_temperature", row["cutoff_thermal_join"]["delta_T_prescribed_energy_algebra_K"], final_temp-100)
    ledger_left = Q(old["injected_number_m3"])+Q(old["ionizations_HI_m3"])+Q(old["ionizations_HeI_m3"])
    ledger_right = Q(old["active_electron_number_m3"])+cut_n
    near(label+"/free_active_thermal_balance", ledger_left, ledger_right)
    record_results.append({"model": label, "source_energy_scale_eV_m3": scale, "J1_sum": j1, "J2_sum": j2, **from_integrators, "thermal_delta_T_K": final_temp-100})

coverage = read(UNIT / "inputs/SOURCE_COVERAGE_RECORD.json")["coverage"]
all_energy = Q(coverage["all_direct_A_energy_eV_m3_s2"])*T*T*EV/2
selected_energy = Q(pulse["models"][0]["physical_energy_scale_eV_m3"])*EV/2
outside = all_energy-selected_energy
near("record/outside_cumulative_budget", candidate["cumulative_energy_envelope"]["omitted_birth_energy_J_m3"], outside, Q("1e-48"))
verify("record/consumer_budget_unprovided", all(candidate["consumer_budget"][k] is None for k in ["observable", "absolute_tolerance", "relative_tolerance", "reference_denominator"]))

result = {"schema": "independent-source-binding-reference.v1", "status": "PASS" if all(x["passed"] for x in checks) else "FAIL", "independence": "Own exact atomic fixture and open-system calorimeter; raw pulse integrator J1/J2 route; candidate code not imported or executed", "toy": {"T": end, "H0": yield_total, "p": p, "R": r, "S": s, "direct_power": power, "direct_cumulative_heat": heat, "thermal_increment": increment, "cold_particle_increment": cold_increment}, "stored_record_results": record_results, "checks": checks, "counts": {"checks": len(checks), "failed": sum(not c["passed"] for c in checks), "new_generator": 0, "new_source_quadrature": 0, "new_transport": 0, "new_pulse": 0, "old_suite_reruns": 0}, "scope": "Exact fixture algebra and arithmetic of recorded numbers; does not certify physical parameters, continuum, mesh, frozen-bath validity, consumer adoption or input uncertainty"}
(HERE / "REFERENCE_RESULT.json").write_text(json.dumps(pack(result), ensure_ascii=False, indent=2)+"\n")
print(json.dumps({"status": result["status"], "checks": len(checks), "failed": [x["id"] for x in checks if not x["passed"]], "candidate_imported": False}))
sys.exit(0 if result["status"] == "PASS" else 1)
