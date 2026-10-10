"""Source-bound NIST 2002 two-transition cross sections, 1000--3000 eV only.

This component is not connected to any production or causal-kernel provider.
In particular the HeI singlet transition is NOT the existing old 23s closure.
Only Python's standard library is required. No network access occurs at runtime.
"""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_PDF_SHA256 = "2492e6923503515bc6bf310da043eb64f72f3b2e609991fa037065a8afc966d1"
ANGSTROM2_TO_CM2 = 1e-16


class EnergyDomainError(ValueError):
    """The requested kinetic energy is not in the closed table domain."""


class UnknownTransitionError(ValueError):
    """The named transition is not one of the two source-table channels."""


def verify_sources() -> dict[str, str]:
    """Check the two local research inputs for accidental identity drift."""
    manifest = json.loads((ROOT / "SOURCE_MANIFEST.json").read_text())
    expected = manifest["files_sha256"]
    if expected["sources/j74sto.pdf"] != SOURCE_PDF_SHA256:
        raise ValueError("NIST_SOURCE_PDF_IDENTITY_MISMATCH")
    for relative, digest in expected.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"SOURCE_BYTES_MISMATCH:{relative}")
    return dict(expected)


@dataclass(frozen=True)
class Transition:
    transition_id: str
    initial_state: str
    final_state: str
    excitation_energy_eV: float
    cross_sections_angstrom2: tuple[float, ...]


@dataclass(frozen=True)
class CrossSection:
    transition_id: str
    initial_state: str
    final_state: str
    excitation_energy_eV: float
    incident_energy_eV: float
    cross_section_cm2: float
    cross_section_angstrom2: float
    cross_section_unit: str = "cm^2"
    source_pdf_sha256: str = SOURCE_PDF_SHA256
    claim: str = "SOURCE_BACKED_ATOMIC_COMPONENT_ONLY"


@dataclass(frozen=True)
class NistTableProvider:
    incident_energies_eV: tuple[float, ...]
    transitions: tuple[Transition, ...]

    @classmethod
    def from_local_sources(cls) -> NistTableProvider:
        """Load the exact eight-entry table after verifying local source bytes."""
        verify_sources()
        table = json.loads((ROOT / "sources/table.json").read_text())
        if table["source_sha256"] != SOURCE_PDF_SHA256:
            raise ValueError("TABLE_SOURCE_IDENTITY_MISMATCH")
        return cls(
            tuple(float(value) for value in table["incident_energy_eV"]),
            tuple(Transition(
                transition_id=row["id"],
                initial_state=row["initial_state"],
                final_state=row["final_state"],
                excitation_energy_eV=float(row["excitation_energy_eV"]),
                cross_sections_angstrom2=tuple(float(value) for value in row["cross_section"]),
            ) for row in table["transitions"]),
        )

    def evaluate(self, transition_id: str, energy_eV: float) -> CrossSection:
        """Linearly interpolate sigma(E); no clipping or extrapolation.

        The result is a cross section in cm^2, NOT a gas-density-weighted
        collision rate. Excitation energy is the printed NIST channel value,
        not a silently substituted P02B/DarkHistory effective energy.
        """
        transition = next((item for item in self.transitions
                           if item.transition_id == transition_id), None)
        if transition is None:
            raise UnknownTransitionError(f"UNKNOWN_NIST_TRANSITION:{transition_id}")
        if isinstance(energy_eV, bool) or not isinstance(energy_eV, (int, float)):
            raise EnergyDomainError("INCIDENT_ENERGY_MUST_BE_A_FINITE_REAL_NUMBER")
        try:
            energy = float(energy_eV)
        except OverflowError as error:
            raise EnergyDomainError("INCIDENT_ENERGY_OUTSIDE_1000_3000_EV") from error
        energies = self.incident_energies_eV
        if not math.isfinite(energy) or not energies[0] <= energy <= energies[-1]:
            raise EnergyDomainError("INCIDENT_ENERGY_OUTSIDE_1000_3000_EV")

        upper = bisect_left(energies, energy)
        values = transition.cross_sections_angstrom2
        if energy == energies[upper]:
            sigma = values[upper]
        else:
            fraction = ((energy - energies[upper - 1])
                        / (energies[upper] - energies[upper - 1]))
            sigma = values[upper - 1] + fraction * (values[upper] - values[upper - 1])
        return CrossSection(
            transition_id=transition.transition_id,
            initial_state=transition.initial_state,
            final_state=transition.final_state,
            excitation_energy_eV=transition.excitation_energy_eV,
            incident_energy_eV=energy,
            cross_section_cm2=sigma * ANGSTROM2_TO_CM2,
            cross_section_angstrom2=sigma,
        )
