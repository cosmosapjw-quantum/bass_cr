from fractions import Fraction as F
import pytest
from dyadic import I,SCALE
from complex_box import C
from geometry import Triangle,Affine
from weak_kernel import Candidate,Context,Cell,kernel
from cubature import Budget,cell_enclosure

def constant_s_fixture():
    edges=(F(0),F(1,8),F(1),F(2),F(4),F(8))
    coeff=tuple((a,b-a,F(0),F(0),F(0)) for a,b in zip(edges,edges[1:]))
    return Candidate(edges,(coeff,coeff),(0,1),'constant-unnormalized-solid-fixture')

def real_contains(c,x):return c.re.contains(x) and c.im.contains(0)

@pytest.mark.parametrize('side',['origin_T','origin_P'])
def test_origin_cubature_exact_coulomb_and_volume_integrals(side):
    c=constant_s_fixture();ct=Context(3,4,0,0);a=c.edges[1]
    cell=Cell(side,0 if side=='origin_T' else 4,4 if side=='origin_T' else 0)
    r=cell_enclosure(c,cell,ct,(0,0,0,0),n=16,budget=Budget(258))
    assert real_contains(r['values']['S_TP'],a**3/3)
    expected=-a*a/2-a**3/15
    assert real_contains(r['values']['H_TP'],expected)
    assert real_contains(r['values']['K_TP'],expected)
    assert real_contains(r['values']['D_TP'],0)
    assert r['coverage']=='ONE_CELL_ONE_ENTRY_ONLY'

def test_regular_cubature_exact_polynomial_fixture():
    c=constant_s_fixture();ct=Context(3,4,0,0)
    tri=Triangle(3,4,((Affine(F(2)),Affine(F(4))),(Affine(F(3)),Affine(F(4))),(Affine(F(3)),Affine(F(5)))),(F(1),F(0),F(0)))
    r=cell_enclosure(c,Cell('regular',3,4,tri),ct,(0,0,0,0),n=16,budget=Budget(258))
    assert real_contains(r['values']['S_TP'],F(139,240))
    assert real_contains(r['values']['H_TP'],F(-7,20))
    assert real_contains(r['values']['D_TP'],0)

def test_origin_holomorphic_majorant_includes_r_zero_without_cutoff():
    from complex_box import ellipse_box
    c=constant_s_fixture();ct=Context(3,4,F(3,4),F(7,3));cell=Cell('origin_T',0,4)
    q=kernel(c,cell,ct,ellipse_box(F(1,2),F(1,2)),C(I.bounds(0,1)),1,1,1,-1).upper()
    assert all(x.lo>=0 for x in q.values())

def test_exhausted_budget_does_not_return_a_complete_result():
    c=constant_s_fixture();ct=Context(3,4,0,0)
    with pytest.raises(RuntimeError,match='budget'):
        cell_enclosure(c,Cell('origin_T',0,4),ct,(0,0,0,0),n=8,budget=Budget(4))

def test_complex_pole_refused_not_replaced_with_epsilon():
    from weak_kernel import regular_field
    from moments import P,U,V
    c=constant_s_fixture()
    with pytest.raises(ZeroDivisionError):regular_field(c,1,1,C(I.bounds(-1,1)),[U,V,P(0)],1)

@pytest.mark.parametrize('box',[(-1,1,0,1),(0,0,0,1),(0,1,1,0),(0,1,0,2)])
def test_invalid_reference_box_refused(box):
    c=constant_s_fixture()
    with pytest.raises(ValueError):cell_enclosure(c,Cell('origin_T',0,4),Context(3,4,0,0),(0,0,0,0),box=box,budget=Budget(200))
