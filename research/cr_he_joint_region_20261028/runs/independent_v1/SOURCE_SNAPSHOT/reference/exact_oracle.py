"""Independent exact projection oracle for at most four atoms.

This module builds the full event incidence matrix from the supplied data.
It does not import the proposed polygon, its constructor, a flow solver, or
any predecessor implementation.  Execution belongs to the root's later
bounded controls stage; importing this module performs no calculation.
"""
from fractions import Fraction
from itertools import combinations


def _exact(value, where):
    if type(value) not in (int, Fraction):
        raise ValueError(where + ": exact int/Fraction required")
    return Fraction(value)


def _atoms(values):
    if not isinstance(values, (list, tuple)):
        raise ValueError("atoms: plain sequence required")
    if len(values) > 4:
        raise ValueError("oracle is restricted to at most four atoms")
    result = []
    seen = set()
    for index, row in enumerate(values):
        if not isinstance(row, dict):
            raise ValueError("atom row must be a plain dictionary")
        key = row.get("key")
        if type(key) is not str or not key or key in seen:
            raise ValueError("nonempty distinct atom keys required")
        seen.add(key)
        energy = _exact(row.get("energy_eV"), "atom energy")
        mass = _exact(row.get("coefficient"), "atom mass")
        partition = row.get("partition")
        if energy < 0 or mass < 0 or type(partition) is not int:
            raise ValueError("nonnegative exact data and integer bins required")
        result.append((key, energy, mass, partition))
    return result


def _basic_solution(columns, chosen, right_hand_side):
    """Solve a square selected-column system with Fraction Gauss-Jordan.

    None means linearly dependent columns.  No floating rank decision or
    tolerance appears in the basis enumeration.
    """
    size = len(right_hand_side)
    matrix = [
        [Fraction(columns[column][row]) for column in chosen]
        + [right_hand_side[row]]
        for row in range(size)
    ]
    for column in range(size):
        pivot_row = next(
            (row for row in range(column, size) if matrix[row][column]),
            None,
        )
        if pivot_row is None:
            return None
        if pivot_row != column:
            matrix[column], matrix[pivot_row] = (
                matrix[pivot_row], matrix[column]
            )
        pivot = matrix[column][column]
        for entry in range(column, size + 1):
            matrix[column][entry] /= pivot
        for row in range(size):
            if row == column:
                continue
            factor = matrix[row][column]
            if not factor:
                continue
            matrix[row][column] = Fraction(0)
            for entry in range(column + 1, size + 1):
                matrix[row][entry] -= factor * matrix[column][entry]
    return tuple(matrix[row][-1] for row in range(size))


def _cross(origin, left, right):
    return (
        (left[0] - origin[0]) * (right[1] - origin[1])
        - (left[1] - origin[1]) * (right[0] - origin[0])
    )


def _convex_hull(points):
    """Exact monotone hull; collinear interior points are omitted."""
    ordered = sorted(set(points))
    if len(ordered) < 2:
        return ordered
    lower = []
    for point in ordered:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(ordered):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def enumerate_projection(atoms, K):
    """Return an independently enumerated exact full-event projection.

    atoms is a list of dictionaries with key, energy_eV, coefficient and
    partition.  Numeric inputs must be exact int/Fraction values, with
    nonnegative energies, coefficients and K; bool and float are rejected.

    points contains the distinct projections of all basic feasible
    solutions, not every point of their convex hull.  hull is a
    counterclockwise exact hull with no repeated final vertex; a segment
    has two endpoints and a singleton one.  Coordinates, dmax and cmax
    remain Fraction objects.  bases_checked includes singular and
    infeasible candidate bases.

    Singleton columns make the incidence matrix full row rank.  The
    feasible polytope is nonempty and bounded, including zero masses.
    Enumerating its full-size feasible bases therefore suffices for its
    projected convex hull; degenerate vertices may occur in many bases.
    """
    data = _atoms(atoms)
    cap = _exact(K, "K")
    if cap < 0:
        raise ValueError("K must be nonnegative")
    size = len(data)
    if size == 0:
        zero = Fraction(0)
        return {
            "points": [(zero, zero)],
            "hull": [(zero, zero)],
            "dmax": zero,
            "cmax": zero,
            "bases_checked": 1,
        }

    columns = []
    rewards = []
    for atom_index in range(size):
        column = [0] * size
        column[atom_index] = 1
        columns.append(tuple(column))
        rewards.append((0, 0))

    for left in range(size):
        for right in range(left, size):
            if data[left][1] + data[right][1] > cap:
                continue
            column = [0] * size
            column[left] += 1
            column[right] += 1       # A diagonal consumes two legs.
            columns.append(tuple(column))
            rewards.append((1, int(data[left][3] != data[right][3])))

    right_hand_side = tuple(atom[2] for atom in data)
    projected = set()
    bases_checked = 0
    for chosen in combinations(range(len(columns)), size):
        bases_checked += 1
        solution = _basic_solution(columns, chosen, right_hand_side)
        if solution is None or any(value < 0 for value in solution):
            continue
        double = Fraction(0)
        cross = Fraction(0)
        for column, value in zip(chosen, solution):
            if rewards[column][0]:
                double += value
            if rewards[column][1]:
                cross += value
        projected.add((double, cross))

    if not projected:
        # The all-single identity basis is always feasible.  Reaching this
        # point is an oracle implementation failure, never a physics no-go.
        raise ArithmeticError("oracle failed to retain the all-single basis")
    points = sorted(projected)
    return {
        "points": points,
        "hull": _convex_hull(points),
        "dmax": max(point[0] for point in points),
        "cmax": max(point[1] for point in points),
        "bases_checked": bases_checked,
    }
