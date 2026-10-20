"""Independent C21H callback algebra and boundary tests; no ODE/native run.

The authoritative C21G RHS is captured before solve_ivp starts by a sentinel
exception. Manufactured microphysics and explicit synthetic polynomials are
labelled below. The old C21F/C21G regression suites are not invoked.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import importlib
import math
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ["C21F_SOURCE_DIR"]).resolve()
CONTRACT_DIR = Path(os.environ["C21G_UNIT_DIR"]).resolve()
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CONTRACT_DIR))

import optical_adapter as adapter
from campaign_contract import fixture_scales

METRICS = {}


class CapturedBeforeIntegrator(RuntimeError):
    """Control sentinel: reaching this point is not an integration attempt."""


def capture(fixture=None, provider=None):
    reference = adapter.private_reference(SOURCE)
    from run_experiment import make_fixture
    from event_coupler import ManufacturedMicro
    fixture = fixture or make_fixture(a0=.09, dx=1e-4, opacity_scale=.0003)
    provider = provider or ManufacturedMicro()
    scale_contract = fixture_scales(asdict(fixture))
    captured = {}

    def stop(fun, t_span, y0, **kwargs):
        captured.update(fun=fun, t_span=tuple(t_span), y0=np.array(y0, copy=True),
                        controls=kwargs)
        raise CapturedBeforeIntegrator()

    reference.solve_ivp = stop
    try:
        reference.run_reference_tau(fixture, provider, rtol=2e-11,
            atol=np.asarray(scale_contract["values"])*2e-14)
    except CapturedBeforeIntegrator:
        pass
    else:
        raise AssertionError("Capture did not stop before the integrator")
    m = len(fixture.q)
    dynamic = np.array([j for j in range(m+19)
                       if not (fixture.Y == 0 and j in (m+1, m+2))])
    scales = np.asarray(scale_contract["values"])[dynamic]
    callback = adapter.CellCallbacks(captured["fun"], fixture,
        *captured["t_span"], scales, dynamic, reference)
    return fixture, reference, captured, callback, scale_contract


def changed_state(callback, original):
    """Feasible gas and positive optical depths, including inactive slots."""
    u = np.array(original, copy=True)
    u[:callback.m] = np.linspace(.025, .175, callback.m)
    for j, full_index in enumerate(callback.dynamic):
        if full_index == callback.m:
            u[j] = .31
        elif full_index == callback.m+1:
            u[j] = .12
        elif full_index == callback.m+2:
            u[j] = .025
        elif full_index == callback.m+3:
            u[j] *= 1.07
    return u


def error_metric(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    delta = float(np.max(np.abs(actual-expected)))
    scale = float(max(np.max(np.abs(actual)), np.max(np.abs(expected))))
    return {"maximum_absolute_difference":delta,
            "maximum_magnitude":scale,
            "difference_over_maximum_magnitude":delta/scale if scale else 0.}


class OpticalAdapterTests(unittest.TestCase):
    def test_derivative_weights_represented_quadratic_and_invalid_nodes(self):
        for offsets in [(-.0000101, .0000097), (.0000101, .0000203),
                        (-.0000103, -.0000201)]:
            with self.subTest(offsets=offsets):
                weights = adapter.derivative_weights(offsets)
                nodes = np.array([0., *offsets])
                # Difference form avoids cancellation of a large constant.
                value = 7.0 + 3.25*nodes - 1.8*nodes**2
                derivative = weights[1:] @ (value[1:]-value[0])
                self.assertAlmostEqual(float(derivative), 3.25, delta=2e-10)
                self.assertLess(abs(float(weights @ nodes)-1.), 4e-15)
        for offsets in [(0.,1.), (1.,1.), (math.inf,1.), (math.nan,1.)]:
            with self.subTest(invalid=offsets):
                with self.assertRaises(adapter.AdapterError):
                    adapter.derivative_weights(offsets)

    def test_analytic_tau_jacobian_against_original_rhs_centered_difference(self):
        f, _, captured, cb, _ = capture()
        u = changed_state(cb, captured["y0"])
        z = u/cb.scales
        t = cb.lo+.43*(cb.hi-cb.lo)
        jacobian = cb.jacobian(t, z)
        expected = np.zeros_like(jacobian[:, :cb.m])
        # This central difference does not call gas_nodes or derivative_weights.
        step = 2e-5
        for j in range(cb.m):
            plus, minus = z.copy(), z.copy()
            plus[j] += step; minus[j] -= step
            expected[:,j] = (captured["fun"](t, plus*cb.scales)
                             -captured["fun"](t, minus*cb.scales))/(2*step)/cb.scales
        np.testing.assert_allclose(jacobian[:,:cb.m], expected, rtol=2e-7, atol=2e-9)
        METRICS["tau_jacobian"] = error_metric(jacobian[:,:cb.m], expected)
        self.assertEqual(cb.counts["analytic_tau_columns"], len(f.q))

    def test_gas_jacobian_against_independent_original_rhs_stencil(self):
        _, _, captured, cb, _ = capture()
        u = changed_state(cb, captured["y0"]); z = u/cb.scales
        t = (cb.lo+cb.hi)/2
        jacobian = cb.jacobian(t,z)
        indices = [j for j,k in enumerate(cb.dynamic) if cb.m <= k < cb.m+4]
        expected = np.zeros((cb.n,len(indices)))
        for column,j in enumerate(indices):
            # Fixed larger normalized step gives an independent truncation scale.
            step = 2e-5
            plus,minus = z.copy(),z.copy()
            plus[j] += step; minus[j] -= step
            expected[:,column] = (captured["fun"](t,plus*cb.scales)
                -captured["fun"](t,minus*cb.scales))/(2*step)/cb.scales
        np.testing.assert_allclose(jacobian[:,indices],expected,rtol=2e-6,atol=2e-7)
        METRICS["gas_jacobian"] = error_metric(jacobian[:,indices], expected)
        self.assertEqual(cb.counts["gas_fd_columns"],4)

    def test_fifteen_passive_columns_are_exact_and_rhs_invariant(self):
        _, _, captured, cb, _ = capture()
        z = changed_state(cb,captured["y0"])/cb.scales
        t = (cb.lo+cb.hi)/2
        passive = [j for j,k in enumerate(cb.dynamic) if k >= cb.m+4]
        self.assertEqual(len(passive),15)
        jacobian = cb.jacobian(t,z)
        self.assertTrue(np.array_equal(jacobian[:,passive],np.zeros((cb.n,15))))
        displaced = z.copy(); displaced[passive] = np.linspace(-3.5,7.2,15)
        self.assertTrue(np.array_equal(cb.rhs(t,z),cb.rhs(t,displaced)))
        self.assertEqual(cb.counts["exact_passive_columns"],15)

    def test_y_zero_removes_exact_helium_unknowns_and_tolerances(self):
        adapter.private_reference(SOURCE)
        from run_experiment import make_fixture
        f = make_fixture(a0=.09,dx=1e-4,opacity_scale=.0003,Y=0.)
        _,reference,captured,cb,scale_contract = capture(f)
        self.assertEqual(cb.n,cb.m+17)
        self.assertNotIn(cb.m+1,cb.dynamic); self.assertNotIn(cb.m+2,cb.dynamic)
        full = cb.full(captured["y0"])
        self.assertEqual(full[cb.m+1],0.);self.assertEqual(full[cb.m+2],0.)
        np.testing.assert_array_equal(captured["controls"]["atol"],
                                     2e-14*np.asarray(scale_contract["values"])[cb.dynamic])
        with tempfile.TemporaryDirectory() as temp:
            backend = adapter.RustIVP(f,reference,"not_executed",temp,
                                      scale_contract["values"],2e-14)
            np.testing.assert_array_equal(backend.dynamic,cb.dynamic)
            np.testing.assert_array_equal(backend.scales,cb.scales)
        cb.jacobian((cb.lo+cb.hi)/2,captured["y0"]/cb.scales)
        self.assertEqual(cb.counts["gas_fd_columns"],2)

    def test_inactive_and_zero_amount_cohorts_have_exact_zero_tau_columns(self):
        f,_,_,_,_ = capture()
        amounts = list(f.amounts); amounts[0]=0.
        f=replace(f,amounts=tuple(amounts)).validate()
        _,_,captured,cb,_ = capture(f)
        z=changed_state(cb,captured["y0"])/cb.scales;t=(cb.lo+cb.hi)/2
        selected=np.flatnonzero((~cb.active)|(np.asarray(f.amounts)==0.))
        self.assertGreater(len(selected),1)
        jacobian=cb.jacobian(t,z)
        self.assertTrue(np.array_equal(jacobian[:,selected],np.zeros((cb.n,len(selected)))))
        displaced=z.copy();displaced[selected] += 13.
        self.assertTrue(np.array_equal(cb.rhs(t,z),cb.rhs(t,displaced)))
        rhs=cb.rhs(t,z)
        self.assertTrue(np.array_equal(rhs[:cb.m][~cb.active],np.zeros(np.sum(~cb.active))))
        # Active zero amounts retain tau'=hazard/H, without affecting stocks.
        self.assertGreater(rhs[0],0.)

    def test_gas_boundary_uses_admissible_one_sided_nodes(self):
        _,_,captured,cb,_=capture()
        t=(cb.lo+cb.hi)/2
        gas_cases=[(0.,.12,.025), (1.,.12,.025), (.31,0.,.025),
                   (.31,.12,0.), (.31,.75,.25)]
        for gas in gas_cases:
            with self.subTest(gas=gas):
                u=changed_state(cb,captured["y0"]);u[cb.m:cb.m+3]=gas
                before=len(cb.fd_nodes)
                jacobian=cb.jacobian(t,u/cb.scales)
                self.assertTrue(np.isfinite(jacobian).all())
                nodes=cb.fd_nodes[before:]
                self.assertTrue(any(x["stencil"]=="one_sided" for x in nodes))
                for row in nodes:
                    j=int(np.flatnonzero(cb.dynamic==row["full_index"])[0])
                    for offset in row["offsets"]:
                        point=u.copy();point[j]+=offset
                        self.assertTrue(cb.state_valid(cb.full(point)[cb.m:cb.m+4],cb.f.Y))
        METRICS["one_sided_gas_columns"]=cb.counts["gas_fd_one_sided_columns"]

    def test_partial_time_flat_branches_and_interior_polynomial(self):
        _,reference,captured,base,_=capture()
        center=(base.lo+base.hi)/2
        linear=np.linspace(.5,2.,base.n);quadratic=np.linspace(-.25,.75,base.n)
        def polynomial(t,u):
            dt=min(max(t,base.left),base.right)-center
            return (linear*dt+quadratic*dt*dt)*base.scales
        cb=adapter.CellCallbacks(polynomial,base.f,base.lo,base.hi,
                                  base.scales,base.dynamic,reference)
        z=captured["y0"]/cb.scales
        for t in (cb.lo,cb.left,cb.right,cb.hi):
            self.assertTrue(np.array_equal(cb.partial_t(t,z),np.zeros(cb.n)))
        self.assertEqual(cb.counts["original_rhs_evaluations"],0)
        desired=cb.time_fd_fraction*(cb.hi-cb.lo)
        for t in (center,cb.left+.5*desired,cb.right-.5*desired):
            actual=cb.partial_t(t,z);expected=linear+2*quadratic*(t-center)
            np.testing.assert_allclose(actual,expected,rtol=2e-9,atol=2e-10)
        self.assertEqual(cb.counts["time_fd_one_sided"],2)
        for row in cb.fd_nodes:
            self.assertTrue(all(cb.left<x<cb.right for x in row["nodes"]))

    def test_partial_time_matches_independent_original_rhs_difference(self):
        _,_,captured,cb,_=capture()
        u=changed_state(cb,captured["y0"]);z=u/cb.scales
        t=cb.lo+.47*(cb.hi-cb.lo)
        actual=cb.partial_t(t,z)
        step=.003*(cb.hi-cb.lo)
        expected=(captured["fun"](t+step,u)-captured["fun"](t-step,u))/(2*step)/cb.scales
        np.testing.assert_allclose(actual,expected,rtol=3e-5,atol=2e-5)
        METRICS["partial_time"]=error_metric(actual,expected)

    def test_short_cell_endpoint_rounding_preserves_original_rhs(self):
        adapter.private_reference(SOURCE)
        from run_experiment import make_fixture
        f=make_fixture(a0=.09,dx=1e-7,opacity_scale=.0003,Y=0.)
        _,reference,captured,cb,_=capture(fixture=f)
        self.assertEqual(cb.left,cb.lo)
        self.assertEqual(cb.right,cb.hi)
        u=captured["y0"];z=u/cb.scales
        for t in (cb.lo,cb.lo+.37*(cb.hi-cb.lo),cb.hi):
            np.testing.assert_array_equal(cb.rhs(t,z),captured["fun"](t,u)/cb.scales)
        calls=cb.counts["original_rhs_evaluations"]
        for t in (cb.lo,cb.hi):
            np.testing.assert_array_equal(cb.partial_t(t,z),np.zeros(cb.n))
        self.assertEqual(cb.counts["original_rhs_evaluations"],calls)
        for t in (cb.lo+.5*(cb.hi-cb.lo),np.nextafter(cb.lo,cb.hi)):
            self.assertTrue(np.isfinite(cb.partial_t(t,z)).all())
        nodes=[row for row in cb.fd_nodes if row["kind"]=="time"]
        self.assertEqual(len(nodes),2)
        self.assertTrue(all(cb.left<node<cb.right
                            for row in nodes for node in row["nodes"]))
        # One represented interior point is insufficient for a quadratic
        # stencil. Preserve the explicit failure; never cross the cell edge.
        interior=float(np.nextafter(cb.lo,cb.hi))
        tiny_hi=float(np.nextafter(interior,cb.hi))
        tiny=adapter.CellCallbacks(cb.fun,f,cb.lo,tiny_hi,cb.scales,
                                  cb.dynamic,reference)
        with self.assertRaisesRegex(adapter.AdapterError,"NO_INTERIOR_TIME_FD_STENCIL"):
            tiny.partial_t(interior,z)
        self.assertEqual(tiny.counts["original_rhs_evaluations"],0)
        METRICS["short_cell_represented_clamp"]={
            "fixture_dx":f.dx,"first_cell_width":cb.hi-cb.lo,
            "left_equals_lo":cb.left==cb.lo,"right_equals_hi":cb.right==cb.hi,
            "original_rhs_equal_at_three_points":True,
            "endpoint_partial_time_zero":True,"fd_nodes_strictly_interior":True,
            "insufficient_represented_nodes_explicitly_rejected":True,
            "ode_integration":False}

    def test_fixed_scaling_preserves_wrms_and_return_trace_contract(self):
        f,reference,captured,cb,scale_contract=capture()
        u0=captured["y0"].copy();u1=u0+1e-8*np.linspace(0.,1.,cb.n)*cb.scales
        error=1e-10*np.cos(np.arange(cb.n))*cb.scales
        alpha=2e-14;rtol=2e-11
        physical=error/(alpha*cb.scales+rtol*np.maximum(abs(u0),abs(u1)))
        normalized=(error/cb.scales)/(alpha+rtol*np.maximum(abs(u0/cb.scales),abs(u1/cb.scales)))
        np.testing.assert_allclose(physical,normalized,rtol=5e-16,atol=0.)
        np.testing.assert_array_equal(cb.rhs((cb.lo+cb.hi)/2,u0/cb.scales),
            captured["fun"]((cb.lo+cb.hi)/2,u0)/cb.scales)
        # Only return-shape plumbing is mocked; this is not a Rust solve.
        with tempfile.TemporaryDirectory() as temp:
            backend=adapter.RustIVP(f,reference,"not_executed",temp,scale_contract["values"],alpha)
            def fake_segment(binary,config,callbacks,output,**kwargs):
                output.mkdir()
                return {"accepted_grid_complete":True,"accepted_times":[cb.lo,cb.hi],
                    "accepted_states":[config["y0"],(u1/cb.scales).tolist()],"internal_steps":1,
                    "counters":{"direct_factorizations":3}}
            with mock.patch.object(adapter,"run_segment",side_effect=fake_segment):
                result=backend(captured["fun"],(cb.lo,cb.hi),u0,method="Radau",
                    rtol=rtol,atol=alpha*cb.scales,max_step=(cb.hi-cb.lo)/8)
            np.testing.assert_allclose(result.y[:,0],u0,rtol=2e-16,atol=0.)
            np.testing.assert_allclose(result.y[:,1],u1,rtol=2e-16,atol=0.)
            np.testing.assert_array_equal(result.t,[cb.lo,cb.hi])
            self.assertEqual(result.nlu,3)

    def test_private_import_preserves_public_module_and_pinned_source(self):
        before=adapter.file_hash(SOURCE/"src/reference_tau.py")
        first=adapter.private_reference(SOURCE)
        public=importlib.import_module("reference_tau")
        binding=public.solve_ivp
        first.solve_ivp=object()
        second=adapter.private_reference(SOURCE)
        self.assertIs(public.solve_ivp,binding)
        self.assertIs(second.solve_ivp,binding)
        self.assertIsNot(first,second)
        self.assertEqual(adapter.file_hash(SOURCE/"src/reference_tau.py"),before)
        with mock.patch.dict(sys.modules,{"native_micro":SimpleNamespace(__file__="/wrong/native_micro.py")}):
            with self.assertRaisesRegex(adapter.AdapterError,"IMPORTED_SOURCE_DIRECTORY_MISMATCH"):
                adapter.private_reference(SOURCE)
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp);(source/"src").mkdir();(source/"src/reference_tau.py").write_text("# altered\n")
            with self.assertRaisesRegex(adapter.AdapterError,"C21G_REFERENCE_SOURCE_MISMATCH"):
                adapter.private_reference(source)

    def test_invalid_states_nodes_and_provider_errors_are_not_fallbacks(self):
        _,_,captured,cb,_=capture()
        z=captured["y0"]/cb.scales
        for t,point in [(cb.lo-1.,z),(cb.lo,np.full(cb.n,np.nan)),
                        (cb.lo,np.zeros(cb.n)),(cb.lo,z[:-1])]:
            with self.subTest(t=t,shape=np.shape(point)):
                with self.assertRaises(adapter.AdapterError):cb.partial_t(t,point)
        overflow=z.copy();overflow[-1]=np.finfo(float).max
        with np.errstate(over="ignore",invalid="ignore"):
            with self.assertRaises(adapter.AdapterError):cb.partial_t(cb.lo,overflow)
        # Inherited FP64 boundary limitation: (0.8+0.2)==1 passes the
        # declared state domain, while ((1-0.8)-0.2)<0 in alpha(). The pinned
        # manufactured provider rejects this; the adapter must preserve it.
        from event_coupler import ProviderFailure
        inherited=z.copy();inherited[cb.m+1]=.8;inherited[cb.m+2]=.2
        self.assertTrue(cb.state_valid(cb.full(inherited*cb.scales)[cb.m:cb.m+4],cb.f.Y))
        with self.assertRaisesRegex(ProviderFailure,"MICRO_NEGATIVE_EVENT_OR_ESCAPE"):
            cb.rhs((cb.lo+cb.hi)/2,inherited)
        METRICS["inherited_fp64_helium_boundary"]={
            "y":.8,"z":.2,"left_associative_neutral_fraction":1.-.8-.2,
            "state_valid":True,"provider_failure_preserved":True,
            "source_modified":False,"clipping_or_fallback":False}
        class ProviderExploded(RuntimeError):pass
        class BrokenProvider:
            kind="EXPLICIT_UNIT_TEST_FAILURE"
            def __call__(self,*args):raise ProviderExploded("preserve this failure")
        _,_,failed,broken,_=capture(provider=BrokenProvider())
        with self.assertRaisesRegex(ProviderExploded,"preserve this failure"):
            broken.jacobian((broken.lo+broken.hi)/2,failed["y0"]/broken.scales)
        self.assertEqual(broken.counts["original_rhs_evaluations"],1)
        with self.assertRaises(adapter.AdapterError):
            adapter.CellCallbacks(cb.fun,cb.f,cb.lo,cb.hi,cb.scales,cb.dynamic,cb.ref,fd_relative=0.)


if __name__ == "__main__":
    unittest.main(verbosity=2)
