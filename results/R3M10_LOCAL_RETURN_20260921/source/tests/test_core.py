import sys,math,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from cr_repro.observables import projectile_speed_au,finite_time_threshold_eV,capture_cross_section_a0sq
from cr_repro.grid import GridSpec
from cr_repro.hydrogen import one_s

def test_units_100kevu():
 assert abs(projectile_speed_au(100)-2.00798106651023)<1e-12
 assert abs(finite_time_threshold_eV(100)-13.714497726622685)<1e-12

def test_cell_grid_avoids_origin():
 s=GridSpec((-30,40),(-30,30),(-30,90),.4);x,y,z=s.axes(np)
 assert s.shape()==(175,150,300)
 assert min(abs(x))>.19 and min(abs(y))>.19 and min(abs(z))>.19

def test_h1s_norm_numeric():
 s=GridSpec((-8,8),(-8,8),(-8,8),.25);x,y,z=s.axes(np);X=x[:,None,None];Y=y[None,:,None];Z=z[None,None,:]
 psi=one_s(X,Y,Z);n=np.sum(abs(psi)**2)*s.dv
 assert abs(n-1)<2e-4

def test_b_integral():
 a=.7;b=np.linspace(0,7,7001);p=np.exp(-a*b*b);got=capture_cross_section_a0sq(b,p)
 assert abs(got/(math.pi/a)-1)<2e-6
