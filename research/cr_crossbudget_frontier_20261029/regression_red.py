"""The original no-edge result must carry the constructive low-loop witness."""
from fractions import Fraction
from frontier import Atom, solve

out=solve([Atom.parse('low',0,3,0)],4,0)
if out['low_diagonal'] != (('low',Fraction(3,2)),):
    raise RuntimeError('missing exact constructive diagonal witness')
