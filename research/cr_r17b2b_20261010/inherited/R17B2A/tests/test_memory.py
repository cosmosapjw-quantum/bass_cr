import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from response import blocks
class MemoryTests(unittest.TestCase):
    def test_existing_photons_must_respond_to_reduced_absorption(self):
        # A larger HII fraction lowers kappa; preexisting photon population rises.
        J=blocks(np.zeros((1,1)), np.array([.05]),np.array([.2]),np.array([[-2.]]),np.array([[1.]]))
        self.assertAlmostEqual(float(J[1,0]),.1,places=15)
        self.assertAlmostEqual(float(J[:,0].sum()),0,places=15)
if __name__=='__main__': unittest.main()
