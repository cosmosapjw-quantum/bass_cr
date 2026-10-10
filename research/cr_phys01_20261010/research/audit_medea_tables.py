"""Audit acquired upstream table values, not an IGM evolution calculation."""
from pathlib import Path
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / 'vendor/darkhistory/darkhistory/low_energy'
channels = ['heat', 'Ly_alpha', 'ion_H', 'ion_He_aggregate', 'continuum']
output = {'status': 'DATA_ONLY_AUDIT', 'channels': channels, 'tables': []}
grids = []
for p in sorted(TABLES.glob('results-*.dat'), key=lambda p: float(re.search(r'results-([0-9.]+)ev', p.name)[1])):
    lines = p.read_text().splitlines()
    rows = [[float(x) for x in line.split()] for line in lines[2:] if line.strip()]
    assert len(rows) == 26 and all(len(row) == 6 for row in rows)
    assert all(math.isfinite(x) for row in rows for x in row)
    xs = [row[0] for row in rows]
    assert all(a < b for a, b in zip(xs, xs[1:]))
    grids.append(xs)
    energy = float(re.search(r'results-([0-9.]+)ev', p.name)[1])
    output['tables'].append({
        'path': str(p.relative_to(ROOT)), 'energy_eV': energy,
        'header': lines[0:2], 'rows': len(rows),
        'fraction_min': min(min(row[1:]) for row in rows),
        'fraction_max': max(max(row[1:]) for row in rows),
        'max_abs_sum_residual': max(abs(sum(row[1:])-1) for row in rows),
        'first_row': dict(zip(['xHII']+channels, rows[0])),
        'all_zero_channels': [channels[i] for i in range(5) if all(row[i+1] == 0 for row in rows)],
        'fully_ionized_row': dict(zip(['xHII']+channels, rows[-1])),
    })
assert len(grids) == 8 and all(x == grids[0] for x in grids)
output['ionization_grid_xHII'] = grids[0]
output['legacy_column_order_audit'] = {
    'raw_order': channels,
    'compute_fs_return_indices': [4, 1, 2, 3, 0],
    'returns_section_declared_order': channels,
    'opening_docstring_order': ['continuum', 'Ly_alpha', 'ion_H', 'ion_He_aggregate', 'heat'],
    'consequence': 'raw header is heat-first; return is continuum-first, agreeing with the opening docstring but disagreeing with Returns section; callers must use explicit order',
    'scope': 'static pinned source audit; complete DarkHistory execution not performed',
    'zero_floor': 0.0001,
    'floor_consequence': 'exact zero channels acquire positive fractions before normalization',
}
output['threshold_audit'] = {
    '14_to_30_eV_interpolation': 'positive He ionization below HeI threshold if ordinary interpolation is used without a threshold-aware closure',
    '10.2_and_13.6_eV_rows': 'auxiliary energies beyond the six physical knots described in the 2023 paper; 10.2 eV is pure heat, while 13.6 eV includes excitation and continuum with ionization set to zero',
    'He_aggregate': 'single ion-He energy channel cannot by itself identify separate HeI and HeII ionization counts',
}
dest = ROOT / 'research/TABLE_AUDIT.json'
dest.write_text(json.dumps(output, indent=2)+'\n')
print(json.dumps({'tables':len(output['tables']), 'max_sum_residual': max(x['max_abs_sum_residual'] for x in output['tables']), 'output':str(dest)}, indent=2))
