#!/usr/bin/env python3
"""Scientific and source-provenance tests of finite-L 1980 quantum angular DCS."""
from __future__ import annotations
import csv
import gzip
import json
import math
import tempfile
import unittest
from pathlib import Path

from numpy.polynomial.legendre import leggauss
import numpy as np
import hk_angular_grid as ag
import hk_primary_joint as hk


class AngularPrimaryPhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig,cls.phase_sha=hk.read_original_phases(ag.SOURCE_DEFAULT)

    def test_same_original_primary_archive(self):
        self.assertEqual(hk.sha_file(ag.SOURCE_DEFAULT),hk.SOURCE_SHA)
        self.assertEqual(self.phase_sha,"ae2b3159eaefc699ec8763f3153dddfd3a3ce2aca6151a9a1718ab67997ca6c2")

    def test_source_energy_and_phase_counts(self):
        self.assertEqual([(E,len(g),len(u)) for E,(g,u) in self.orig.items()],
                         [(0.1,147,147),(1.,190,190)])

    def test_real_integrals_from_angular_source(self):
        for E,(g,u) in self.orig.items():
            rows,notes=ag.channel_grid(E,g,u)
            self.assertEqual(len(rows),1536)
            self.assertEqual([sum(r[1]=="elastic" for r in rows),
                              sum(r[1]=="CX" for r in rows)],[768,768])
            for kind in ("elastic","CX"):
                reported=notes[kind]
                self.assertGreater(reported["sigma_total_a0_sq"],0)
                self.assertLess(reported["relative_error_vs_finite_l_recursion"],8e-11)
                self.assertGreater(reported["sigma_mt_charge_a0_sq"],0)
                self.assertLessEqual(reported["sigma_mt_charge_a0_sq"],
                                      2*reported["sigma_total_a0_sq"]*(1+1e-12))
                self.assertGreaterEqual(reported["sigma_viscosity_a0_sq"],0)

    def test_charge_reversal_is_physical(self):
        rows,_=ag.channel_grid(.1,*self.orig[.1])
        for row in rows[::157]:
            x_n,x_c=row[4:6]
            if row[1]=="elastic":
                self.assertAlmostEqual(x_n,x_c)
            else:
                self.assertAlmostEqual(x_n,-x_c)
            self.assertAlmostEqual(row[6]+row[7],math.pi if row[1]=="CX" else 2*row[6],places=11)

    def test_quadrature_integrates_each_finite_l_moment(self):
        for E,(g,u) in self.orig.items():
            rows,notes=ag.channel_grid(E,g,u)
            for channel in ("elastic","CX"):
                subset=[r for r in rows if r[1]==channel]
                for idx,label in ((12,"sigma_total_a0_sq"),(13,"sigma_mt_charge_a0_sq"),
                                  (14,"sigma_viscosity_a0_sq")):
                    self.assertTrue(math.isclose(
                       math.fsum(r[idx] for r in subset),notes[channel][label],rel_tol=4e-15))

    def test_gauss_768_and_1024_independent_grid(self):
        for E,(g,u) in self.orig.items():
            _,q768=ag.channel_grid(E,g,u,n=768)
            _,q1024=ag.channel_grid(E,g,u,n=1024)
            for ch in ("elastic","CX"):
                for k in ("sigma_total_a0_sq","sigma_mt_charge_a0_sq",
                          "sigma_viscosity_a0_sq"):
                    self.assertLess(abs(q768[ch][k]/q1024[ch][k]-1),2e-9)

    def test_no_nuclear_spin_claims(self):
        with tempfile.TemporaryDirectory() as td:
            report=ag.run(ag.SOURCE_DEFAULT,Path(td))
            self.assertEqual(report["nuclear_spin"],
                             "UNBOUND_NOT_PHYSICAL_SPIN_SYMMETRIZED")
            self.assertEqual(report["REI_BASS193_kinetic_source"],"NOT_SOURCE_MATCHED")
            self.assertEqual(report["REI_central_DAG"],"28/88_REPORTED_DELTA0")
            self.assertEqual(report["derived_angular_rows"],3072)

    def test_sampled_four_channel_units(self):
        with gzip.open(ag.HERE/ag.OUTPUT_NAME,"rt",newline="") as z:
            rows=list(csv.DictReader(z))
        self.assertEqual(len(rows),3072)
        self.assertEqual(list(rows[0]),list(ag.COLUMNS))
        self.assertTrue(all(float(r["dSigma_dOmega_a0_sq_per_sr"])>=0 for r in rows))
        for r in rows[::127]:
            d=float(r["dSigma_dOmega_a0_sq_per_sr"])
            cm=float(r["dSigma_dOmega_cm2_per_sr"])
            self.assertTrue(math.isclose(cm,d*hk.A0_CM**2,rel_tol=3e-15))
            w=float(r["GL_weight_dx"])
            self.assertGreater(w,0)
            self.assertAlmostEqual(float(r["dSigma_dX_preweighted_a0_sq"]),
                                   2*math.pi*d,delta=3e-11)

    def test_source_free_outputs_are_bitwise_reproducible(self):
        with tempfile.TemporaryDirectory() as td:
            re=ag.run(ag.SOURCE_DEFAULT,Path(td))
            a=ag.HERE/ag.OUTPUT_NAME
            b=Path(td)/ag.OUTPUT_NAME
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(re["angular_output_sha256"],ag.sha(a))
            self.assertEqual((ag.HERE/"ANGULAR_SCIENCE_RESULT.json").read_bytes(),
                             (Path(td)/"ANGULAR_SCIENCE_RESULT.json").read_bytes())

    def test_private_original_not_in_published_source(self):
        for bad in ("HK1980_FIRST_SLICE_PHASES.csv","HK1980_p298.png",
                    "WU088_P0_R12_HK_NATIVE_RECONSTRUCTION_AND_ANGLE_CONTRACT_20260921.zip"):
            self.assertFalse((ag.HERE/bad).exists())
        self.assertFalse(any(p.suffix==".npz" for p in ag.HERE.glob("*")))

    def test_incorrect_original_zip_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            archive=Path(td)/"tampered.zip"
            archive.write_bytes(b"fake archive")
            with self.assertRaises(ValueError):
                ag.run(archive,Path(td))

    def test_optically_consistent_channels(self):
        for E,(g,u) in self.orig.items():
            ae,ac=hk.amplitudes(g,u)
            bg=np.exp(1j*g)*np.sin(g);bu=np.exp(1j*u)*np.sin(u)
            diff=abs(ae)**2+abs(ac)**2-2*(abs(bg)**2+abs(bu)**2)
            self.assertLess(max(abs(diff)),2e-14)
            _,rep=ag.channel_grid(E,g,u)
            cx=rep["CX"]["sigma_mt_charge_a0_sq"]
            sm=rep["charge_labelled_sum_diagnostic"]["sigma_mt_elastic_plus_CX_a0_sq"]
            self.assertAlmostEqual(cx/sm,rep["charge_labelled_sum_diagnostic"]
                                   ["CX_charge_labelled_mt_fraction"],places=14)


if __name__=="__main__":
    unittest.main(verbosity=2)
