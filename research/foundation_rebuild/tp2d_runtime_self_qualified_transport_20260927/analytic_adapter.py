from __future__ import annotations

class AnalyticEvaluator:
    def __init__(self,assemble_fn,*,trajectory,channels,kernel):
        if not callable(assemble_fn):raise ValueError('callable assemble function required')
        self.assemble_fn=assemble_fn;self.trajectory=trajectory;self.channels=tuple(channels);self.kernel=kernel
        if not self.channels:raise ValueError('nonempty channels required')

    def __call__(self,t,order,subdivisions):
        return self.assemble_fn(self.trajectory,self.channels,float(t),self.kernel,
                                order=int(order),subdivisions=int(subdivisions),
                                phase_budget=None,sector='full')
