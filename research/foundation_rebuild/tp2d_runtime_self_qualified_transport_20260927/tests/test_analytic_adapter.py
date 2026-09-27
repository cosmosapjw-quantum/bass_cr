from analytic_adapter import AnalyticEvaluator


def test_runtime_adapter_forces_reference_semantics_without_phase_budget():
    calls=[]
    def assemble(trajectory,channels,t,kernel,**kw):
        calls.append((trajectory,channels,t,kernel,kw))
        return {'S_tp':[[1]],'S_pt':[[1]],'H_tp':[[1]],'H_pt':[[1]],'D_tp':[[0]],'D_pt':[[0]]}, {'S':[[1]],'H':[[1]],'D':[[0]],'diagnostics':{}}
    ev=AnalyticEvaluator(assemble,trajectory='tr',channels=('c',),kernel='kernel')
    ev(1.25,40,2)
    assert calls==[('tr',('c',),1.25,'kernel',{'order':40,'subdivisions':2,'phase_budget':None,'sector':'full'})]
