"""Stoichiometric source assembly for the five Verner fit labels.

This consumes saved finite-domain source moments. It does not identify HI with
all hydrogen isotopes, manufacture rates for absent channels, or thermalize the
primary electrons. The charge ledger counts all newly freed electrons; their
thermal/nonthermal partition is deliberately separate.
"""
from __future__ import annotations
from math import fsum
from boost_kernel import finite_nonnegative

POPULATIONS = ("HI", "HII", "HeI", "HeII", "HeIII")
ABSORBERS = ("HI", "HeI", "HeII")
API_GUARD_REVISION = 3
ADOPTED_THRESHOLDS_EV = {"HI": 13.6, "HeI": 24.59, "HeII": 54.42}
SUPPLIER_CONTRACT = "C23B_TAIRA_PW19_VERNER_GROUND_STATE_50KEV_V1"


def assemble(cases: list[dict], populations_per_reference: dict[str, float]) -> dict:
    if set(populations_per_reference) != set(POPULATIONS):
        raise ValueError("all five fit-label populations must be explicit")
    x = {k: finite_nonnegative(populations_per_reference[k], k) for k in POPULATIONS}
    if len(cases) != 3 or {r["channel"] for r in cases} != set(ABSORBERS):
        raise ValueError("one source for each of the three absorption channels is required")
    epochs = [finite_nonnegative(r.get("redshift"), "source redshift") for r in cases]
    if len(set(epochs)) != 1:
        raise ValueError("mixed source epochs are not admitted")
    rows = {r["channel"]: r for r in cases}
    for r in cases:
        threshold = finite_nonnegative(r.get("threshold_eV"), "source threshold")
        if threshold != ADOPTED_THRESHOLDS_EV[r["channel"]]:
            raise ValueError("source threshold differs from adopted channel fit")
        support = r.get("photon_support_eV")
        if not isinstance(support, (list, tuple)) or len(support) != 2:
            raise ValueError("explicit two-edge photon support is required")
        support = tuple(finite_nonnegative(v, "photon support edge") for v in support)
        if support != (threshold, 50000.0):
            raise ValueError("source photon support differs from the adopted finite supplier contract")
        if r["result"]["frame"] != "bath_frame_rest_target" or r["result"]["normalization"] != "per_absorbing_target_per_proper_second":
            raise ValueError("explicit bath/rest-target per-target source units required")
        for key in ("number_per_target_s", "kinetic_eV_per_target_s",
                    "binding_eV_per_target_s", "absorbed_photon_eV_per_target_s"):
            finite_nonnegative(r["result"][key], key)
    extent = {k: x[k]*rows[k]["result"]["number_per_target_s"] for k in ABSORBERS}
    dn = {"HI": -extent["HI"], "HII": extent["HI"],
          "HeI": -extent["HeI"], "HeII": extent["HeI"]-extent["HeII"],
          "HeIII": extent["HeII"]}
    def amount(name):
        return fsum(x[k]*rows[k]["result"][name] for k in ABSORBERS)
    photon = amount("absorbed_photon_eV_per_target_s")
    binding = amount("binding_eV_per_target_s")
    kinetic = amount("kinetic_eV_per_target_s")
    freed = fsum(extent.values())
    ion_charge = fsum((dn["HII"], dn["HeII"], 2*dn["HeIII"]))
    return {
        "redshift": epochs[0],
        "api_guard_revision": API_GUARD_REVISION,
        "supplier_contract": SUPPLIER_CONTRACT,
        "populations_per_reference": x,
        "population_source_per_reference_s": dn,
        "electron_number_source_per_reference_s": freed,
        "photon_absorption_eV_per_reference_s": photon,
        "binding_source_eV_per_reference_s": binding,
        "nonthermal_primary_kinetic_source_eV_per_reference_s": kinetic,
        "thermal_heating_source_eV_per_reference_s": None,
        "hydrogen_nucleus_source_residual": fsum((dn["HI"], dn["HII"])),
        "helium_nucleus_source_residual": fsum((dn["HeI"], dn["HeII"], dn["HeIII"])),
        "charge_source_residual": ion_charge-freed,
        "energy_source_residual": photon-fsum((binding, kinetic)),
        "atomic_domain": "three ground-state fit channels through 50 keV photon energy",
        "isotope_population_mapping": "OPEN; not a 21-population reaction network",
        "recoil_model": "explicit zero-recoil rest-target approximation",
        "radiation_owner": "external absorption ledger; radiation backreaction not integrated",
        "omitted_processes": ["isotope-resolved thresholds", "excited targets", "molecules", "CI", "RR", "DR", "charge_exchange", "secondary_transport", "above_fit_domain_absorption"],
        "temperature_validity": "ground-state stationary-target fit; no gas-temperature rate claim",
    }
