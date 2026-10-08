import copy
import json
from pathlib import Path
import unittest
import numpy as np
from semantic_selection import select_projectile_bound, selection_identity

ROOT=Path(__file__).resolve().parents[3]
FIX=ROOT/'research/foundation_rebuild/ncp_shared_research_20260928/r4p0_tail_basis_preflight_20260930/receipts/B0_B3_BASIS_REGISTRY_CONTRACT.json'
class SemanticTests(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads(FIX.read_text())['registries'][0]['resolved_channels']
    def test_b0_exact_current_selection(self):
        self.assertEqual(select_projectile_bound(self.rows,projectile_center=1),[9,10,12,13,14])
    def test_reorder_preserves_actual_subspace(self):
        p=np.random.default_rng(923).permutation(18);rows=[self.rows[i] for i in p]
        idx=select_projectile_bound(rows,projectile_center=1)
        self.assertEqual(set(p[idx]),{9,10,12,13,14})
        self.assertEqual(selection_identity(rows,1),selection_identity(self.rows,1))
        j=np.eye(18)[:,idx];u=np.eye(18)[:,p]
        np.testing.assert_array_equal(u@j@j.T@u.T,np.diag([int(i in [9,10,12,13,14]) for i in range(18)]))
    def test_projectile_mapping_must_be_explicit(self):
        with self.assertRaises(TypeError):select_projectile_bound(self.rows)
    def test_nonnegative_bound_energy_rejected(self):
        rows=copy.deepcopy(self.rows);rows[9]['energy_Eh']=0.0
        with self.assertRaises(ValueError):select_projectile_bound(rows,projectile_center=1)
    def test_negative_pseudostate_rejected(self):
        rows=copy.deepcopy(self.rows);rows[11]['energy_Eh']=-0.1
        with self.assertRaises(ValueError):select_projectile_bound(rows,projectile_center=1)
    def test_missing_identity_and_duplicate_rejected(self):
        rows=copy.deepcopy(self.rows);rows[9].pop('radial_identity')
        with self.assertRaises(ValueError):select_projectile_bound(rows,projectile_center=1)
        with self.assertRaises(ValueError):select_projectile_bound(self.rows+[self.rows[9]],projectile_center=1)
    def test_kind_and_quantum_numbers_must_agree(self):
        rows=copy.deepcopy(self.rows);rows[9]['principal_n']=None
        with self.assertRaises(ValueError):select_projectile_bound(rows,projectile_center=1)
    def test_identity_changes_if_radial_state_changes(self):
        rows=copy.deepcopy(self.rows);rows[9]['radial_identity']='0'*64
        self.assertNotEqual(selection_identity(rows,1),selection_identity(self.rows,1))
    def test_duplicate_physical_state_with_aliased_label_rejected(self):
        alias=copy.deepcopy(self.rows[9]);alias['principal_n']=5
        with self.assertRaises(ValueError):select_projectile_bound(self.rows+[alias],projectile_center=1)
if __name__=='__main__':unittest.main()
