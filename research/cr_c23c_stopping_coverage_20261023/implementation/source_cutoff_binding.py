"""C23B saved rate atoms -> frozen source predictor -> inherited KC atomic EOS.

All exactness claims concern the recorded decimal quadrature atoms and this
finite frozen-source predictor.  No thermalization time, physical heat rate,
continuous-spectrum derivative, or isotope-resolved rate is supplied here.
"""
from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from thermal_cutoff_solver import Atom, AtomicInventory, construct_atomic_root

ATOM_SHA256 = "f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3"
ATOM_BYTES = 1681578
SOURCE_ID = "277d49a9d48c94f6abf4f28fdef9e3be1d352fbb737a2edaed8ad46f1c260955"
FRAME = "bath_frame_rest_target"
RATE_UNIT = "per_absorbing_target_per_proper_second"
CHANNELS = ("HI", "HeI", "HeII")
POPULATIONS = ("HI", "HII", "HeI", "HeII", "HeIII")
REDSHIFTS = (F("2.316"), F("2.479"), F("2.649"))
THRESHOLDS = {"HI": F("13.60"), "HeI": F("24.59"), "HeII": F("54.42")}
EV_J = F("1.602176634e-19")
KB_J_K = F("1.380649e-23")
KB_EV_K = KB_J_K / EV_J
FS_LOW, FS_HIGH = F(10), F("9937.21")


def exact(value, name="value", *, positive=False):
    if isinstance(value, (float, bool)) or not isinstance(value, (str, int, F)):
        raise TypeError(name + " requires an explicit decimal/rational string or integer")
    try:
        x = F(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(name + " must be finite") from exc
    if x < 0 or (positive and not x):
        raise ValueError(name + " must be " + ("positive" if positive else "nonnegative"))
    return x


@dataclass(frozen=True)
class RateAtom:
    channel: str
    kinetic_eV: F
    weight_per_target_s: F


class SavedSupplier:
    """Only the byte-pinned C23B atom artifact is an admitted constructor input."""
    def __init__(self, raw: bytes):
        if len(raw) != ATOM_BYTES or hashlib.sha256(raw).hexdigest() != ATOM_SHA256:
            raise ValueError("C23B atom byte identity mismatch")
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
        if reader.fieldnames != ["redshift", "channel", "kinetic_eV", "number_weight_per_target_s"]:
            raise ValueError("C23B atom schema mismatch")
        epochs = {z: [] for z in REDSHIFTS}
        for row in reader:
            z = exact(row["redshift"], "redshift")
            channel = row["channel"]
            if z not in epochs or channel not in CHANNELS:
                raise ValueError("unadmitted epoch or source channel")
            k = exact(row["kinetic_eV"], "kinetic energy")
            w = exact(row["number_weight_per_target_s"], "source weight", positive=True)
            if k > F(50000) - THRESHOLDS[channel]:
                raise ValueError("outside finite photon-fit support")
            epochs[z].append(RateAtom(channel, k, w))
        if sum(map(len, epochs.values())) != 32592:
            raise ValueError("saved row count mismatch")
        self._epochs = {z: tuple(rows) for z, rows in epochs.items()}

    def atoms(self, redshift):
        z = exact(redshift, "redshift")
        if z not in self._epochs:
            raise ValueError("no redshift interpolation or unverified epoch")
        return self._epochs[z]


def normalization_counts(spec: dict):
    """Convert exactly one explicit density/abundance convention into cell counts."""
    if not isinstance(spec, dict):
        raise ValueError("explicit normalization object required")
    mode = spec.get("mode")
    fields = {"mode", "proper_volume_cm3"}
    if mode == "density":
        fields.add("values_cm3")
        pop = spec.get("values_cm3")
        scale = exact(spec.get("proper_volume_cm3"), "proper_volume_cm3", positive=True)
    elif mode == "abundance":
        fields.update(("values_per_reference", "reference_density_cm3"))
        pop = spec.get("values_per_reference")
        scale = (exact(spec.get("proper_volume_cm3"), "proper_volume_cm3", positive=True)
                 * exact(spec.get("reference_density_cm3"), "reference_density_cm3", positive=True))
    else:
        raise ValueError("normalization mode must be density or abundance")
    if set(spec) != fields or not isinstance(pop, dict) or set(pop) != set(POPULATIONS):
        raise ValueError("one normalization and all five fit-label populations are required")
    counts = {p: exact(pop[p], p) * scale for p in POPULATIONS}
    if sum(counts.values()) <= 0:
        raise ValueError("positive nucleus inventory required")
    return counts


def missing_inputs(request: dict):
    required = ("redshift", "normalization", "proper_duration_s", "initial_temperature_K", "chi",
                "frame", "rate_unit", "initial_electron_model")
    return [name for name in required if name not in request or request[name] is None]


def bind(supplier: SavedSupplier, request: dict):
    """Create a new finite inventory; never mutate/reheat an earlier trial state.

The permitted initial state has charge-neutral thermal electrons and no
pre-existing resolved nonthermal atoms.  Targets, geometry and UV are frozen
over the declared proper interval; new daughters are not reprocessed.
"""
    if not isinstance(supplier, SavedSupplier):
        raise TypeError("byte-pinned SavedSupplier required")
    if not isinstance(request, dict):
        raise ValueError("an explicit source/bath request object is required")
    fields = {"redshift", "normalization", "proper_duration_s", "initial_temperature_K", "chi",
              "frame", "rate_unit", "initial_electron_model"}
    unknown = set(request) - fields
    if unknown:
        raise ValueError("unhandled source/bath request fields: " + ", ".join(sorted(map(str, unknown))))
    missing = missing_inputs(request)
    if missing:
        return {"status": "BLOCKED_MISSING_BATH_OR_SOURCE_CONTRACT", "missing_fields": missing,
                "physical_heating_eV_per_s": None, "inventory": None}
    if request["frame"] != FRAME or request["rate_unit"] != RATE_UNIT:
        raise ValueError("explicit unchanged C23B bath frame and source-rate units required")
    if request["initial_electron_model"] != "charge_neutral_thermal_no_resolved_nonthermal":
        raise ValueError("this adapter requires the declared initial electron reservoir")
    pop = normalization_counts(request["normalization"])
    dt = exact(request["proper_duration_s"], "proper duration")
    t0 = exact(request["initial_temperature_K"], "initial temperature", positive=True)
    chi = exact(request["chi"], "chi", positive=True)
    if chi < F(3, 2):
        raise ValueError("inherited finite atomic existence requires chi >= 3/2")
    source = supplier.atoms(request["redshift"])
    rates = {p: sum((a.weight_per_target_s for a in source if a.channel == p), F(0)) for p in CHANNELS}
    exposure = {p: dt * rates[p] for p in CHANNELS}
    if any(pop[p] > 0 and exposure[p] > 1 for p in CHANNELS):
        raise ValueError("frozen source would exhaust an initially populated target")
    extents = {p: pop[p] * exposure[p] for p in CHANNELS}
    delta = {"HI": -extents["HI"], "HII": extents["HI"], "HeI": -extents["HeI"],
             "HeII": extents["HeI"] - extents["HeII"], "HeIII": extents["HeII"]}
    after = {p: pop[p] + delta[p] for p in POPULATIONS}
    if min(after.values()) < 0:
        raise ValueError("negative frozen predictor population")
    atoms = tuple(Atom(a.kinetic_eV, a.weight_per_target_s * pop[a.channel] * dt) for a in source)
    nnuc = sum(pop.values(), F(0))
    ne0 = pop["HII"] + pop["HeII"] + 2 * pop["HeIII"]
    base_count = nnuc + ne0
    base_energy = F(3, 2) * KB_EV_K * t0 * base_count
    inventory = AtomicInventory(atoms, base_count, base_energy, nnuc, KB_EV_K, chi)
    scan = construct_atomic_root(inventory)
    state = scan.state
    freed = sum(extents.values(), F(0))
    kinetic = sum((a.energy * a.count for a in atoms), F(0))
    binding = sum((THRESHOLDS[p] * extents[p] for p in CHANNELS), F(0))
    ion_charge_after = after["HII"] + after["HeII"] + 2 * after["HeIII"]
    low_n = state.thermal_count - base_count
    low_e = state.thermal_energy - base_energy
    finite_delta_t = (low_e - F(3, 2) * KB_EV_K * t0 * low_n) / (F(3, 2) * KB_EV_K * state.thermal_count)
    cells = {a+"_"+b: [F(0), F(0)] for a in ("cutoff_thermal", "cutoff_active")
             for b in ("below_fs", "inside_fs", "above_fs")}
    for a in atoms:
        own = "cutoff_thermal" if a.energy <= state.cutoff else "cutoff_active"
        support = "below_fs" if a.energy < FS_LOW else "above_fs" if a.energy > FS_HIGH else "inside_fs"
        cells[own+"_"+support][0] += a.count
        cells[own+"_"+support][1] += a.count * a.energy
    residuals = {
        "hydrogen_nucleus": delta["HI"] + delta["HII"],
        "helium_nucleus": delta["HeI"] + delta["HeII"] + delta["HeIII"],
        "charge_all_free": ion_charge_after - ne0 - freed,
        "source_atom_count": inventory.common_count - base_count - freed,
        "source_atom_energy": inventory.common_energy - base_energy - kinetic,
        "count_partition": state.thermal_count + state.active_count - inventory.common_count,
        "energy_partition": state.thermal_energy + state.active_energy - inventory.common_energy,
        "eos": F(3, 2) * KB_EV_K * state.temperature * state.thermal_count - state.thermal_energy,
        "finite_temperature_change": state.temperature - t0 - finite_delta_t,
        "cross_partition_count": sum((v[0] for v in cells.values()), F(0)) - freed,
        "cross_partition_energy": sum((v[1] for v in cells.values()), F(0)) - kinetic,
        "base_count_unchanged": inventory.common_count - freed - base_count,
        "base_energy_unchanged": inventory.common_energy - kinetic - base_energy,
    }
    if any(residuals.values()):
        raise AssertionError("exact finite binding invariant failed")
    return {
        "status": "PASS_SCOPED_FINITE_SOURCE_BINDING", "inventory": inventory, "state": state,
        "source_identity": SOURCE_ID, "source_rows": len(source), "proper_duration_s": dt,
        "initial_counts": pop, "predicted_counts": after, "channel_extents": extents,
        "target_exposure": exposure, "initial_temperature_K": t0, "chi": chi,
        "nucleus_count": nnuc, "initial_free_electron_count": ne0,
        "new_free_electron_count": freed, "all_free_electron_count": ne0 + freed,
        "cutoff_thermal_electron_count": state.thermal_count - nnuc,
        "cutoff_active_electron_count": state.active_count,
        "primary_kinetic_eV": kinetic, "binding_supply_eV": binding,
        "absorbed_photon_eV": kinetic + binding,
        "cutoff_classified_source_count": low_n, "cutoff_classified_source_eV": low_e,
        "partition_delta_temperature_K": finite_delta_t,
        "cross_partitions": cells, "exact_residuals": residuals,
        "branch_policy": "KC4 forward-from-zero fresh-inventory branch; no uniqueness or inherited-continuation claim",
        "branch_crossings": scan.crossing_count,
        "physical_heating_eV_per_s": None,
        "stopping_time_s": None, "source_time_discretization_error_bound": None,
        "global_error_bound": None, "isotope_mapping": "OPEN_FIVE_ELEMENTAL_FIT_LABELS_ONLY",
        "status_ownership": "cutoff thermal is a caloric representation; physical equilibration remains OPEN",
    }
