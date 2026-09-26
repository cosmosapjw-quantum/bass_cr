from pathlib import Path
import numpy as np
from task_plan import numerical_key

def test_identical_effective_quadrature_is_computed_once_not_once_per_role():
    # At z=0 the old longitudinal phase rule adds no edges; raw quadrature is identical.
    a={'role':'reference','order':56,'integration_edges':[0.,.5,1.],'time_hex':float(0).hex(),'sector':'full'}
    b={**a,'role':'candidate'}
    assert numerical_key(a,'same-frozen-physical-basis-and-engine')==numerical_key(b,'same-frozen-physical-basis-and-engine')

def test_order_time_mesh_engine_and_sector_are_not_aliased():
    a={'role':'reference','order':56,'integration_edges':[0.,.5,1.],'time_hex':float(0).hex(),'sector':'full'}
    key=numerical_key(a,'base')
    for changes in [{'order':64},{'time_hex':float(1e-4).hex()},{'integration_edges':[0.,.25,.5,1.]},{'sector':'even'}]:
        assert key!=numerical_key({**a,**changes},'base')
    assert key!=numerical_key(a,'other-engine')
