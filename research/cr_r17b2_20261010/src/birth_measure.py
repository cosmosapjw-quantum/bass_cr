"""Directed integration of actual pinned continuous+atomic companion measure.
All integrands must enclose the whole supplied birth panel. Endpoint atoms use
an explicit physical trace. Sampling callables are not accepted as proof data.
This is a range-integral bound; it does not pretend to validate a survivor flow.
"""
from interval_backend import I
from source_kernel import T,load_pins
class RangeField:
 """Interface for enclosing a physical field on closed birth panels."""
 def whole_panel(self,birth_proper_s,trace):raise NotImplementedError
class PositiveSurvivalTube(RangeField):
 """Exact positivity/absorption bound once common tube has positive opacity."""
 def whole_panel(self,birth_proper_s,trace):return I(0,1)

def integrate_previous(t_proper_s,integrand,eta,continuous_field,atomic_fields,*,trace,panels=8):
 if not isinstance(continuous_field,RangeField):raise TypeError('WHOLE_PANEL_SURVIVAL_FIELD_REQUIRED')
 if trace not in ('left','right'):raise ValueError('PHYSICAL_ATOM_TRACE_REQUIRED')
 if not isinstance(t_proper_s,I) or t_proper_s.lo!=t_proper_s.hi or not 0<=t_proper_s.lo<=T:raise ValueError('EXACT_OBSERVATION_CLOCK_REQUIRED')
 if not isinstance(eta,I) or not 0<=eta.lo<=eta.hi<=1:raise ValueError('ETA_DOMAIN')
 if not isinstance(panels,int) or isinstance(panels,bool) or panels<1:raise ValueError('PANELS')
 pin=load_pins();plan=pin['BIRTH_PLAN.json'];acc=None;t=t_proper_s.lo
 # Directed endpoint arithmetic may overlap at a zero-measure boundary only.
 for j in range(panels):
  left=I(t)*j/panels;right=I(t)*(j+1)/panels
  birth=I(left.lo,right.hi);surv=continuous_field.whole_panel(birth,trace)
  row=integrand(birth,surv);mass=I(5e-15)*(I(t)/panels)*eta
  term=[mass*v for v in row];acc=term if acc is None else [x+y for x,y in zip(acc,term)]
 for bb in plan['same_births']:
  clock=I(bb)
  if clock.lo<t or (clock.lo==t and trace=='right'):
   if str(bb) not in atomic_fields:raise ValueError('MISSING_COMPANION_ATOM_FIELD')
   field=atomic_fields[str(bb)]
   if not isinstance(field,RangeField):raise TypeError('WHOLE_PANEL_ATOM_FIELD_REQUIRED')
   row=integrand(clock,field.whole_panel(clock,trace));w=plan['same_source_weight_boxes'][str(bb)]
   mass=(1-eta)*I(w['lo'],w['hi']);acc=[x+mass*y for x,y in zip(acc,row)]
 return acc
