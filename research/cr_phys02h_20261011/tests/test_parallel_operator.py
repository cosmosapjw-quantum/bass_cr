"""Targeted restriction/partition/process cleanup/value persistence checks only."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import parallel_operator as op
import multiprocessing as mp
import tempfile
import unittest

class ExactColumns(unittest.TestCase):
    def test_partition_rejects_missing_duplicate_and_unsorted(self):
        self.assertEqual(op.partition_columns((0,1,4,8),2,20),((0,1),(4,8)))
        for tiles in [((0,1),(4,)),((0,1),(1,4,8)),((4,8),(0,1))]:
            with self.assertRaises(ValueError):op.validate_partition((0,1,4,8),tiles,20)
        with self.assertRaises(ValueError):op.partition_columns((1,0),1,20)

    def test_ast_exact_restriction_csc_rates_diagnostics_and_persist(self):
        parent,_=op.dependencies('legacy');E=parent.energy_grid(80,160)
        columns=(0,79,80,100,120,239)
        for model in ('legacy','fullBED'):
            reference=op.serial_build(model,E,(80,160),columns)
            candidate=op.parallel_build(model,E,(80,160),2,columns)
            self.assertTrue(all(op.parity(reference,candidate).values()))
            self.assertTrue(reference.identity['restored_AST_exact'])
            self.assertTrue(op.np.any(candidate.G.data<0))
            with tempfile.TemporaryDirectory() as tmp:
                directory=Path(tmp)/'values';op.persist(candidate,directory)
                restored=op.load_persisted(directory)
                self.assertTrue(all(op.parity(candidate,restored).values()))
                # A changed persistent value fails before use; original bytes restored.
                p=directory/'data.npy';raw=p.read_bytes();p.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
                with self.assertRaisesRegex(ValueError,'FILE_HASH'):op.load_persisted(directory)

    def test_failed_child_cancels_and_cleans_all_owned_processes(self):
        parent,_=op.dependencies('legacy');E=parent.energy_grid(80,160)
        prior={p.pid for p in mp.active_children()}
        with self.assertRaisesRegex(RuntimeError,'CHILD_FAILURE'):
            op.parallel_build('legacy',E,(80,160),2,(0,79,80,239),_fail_tile=0)
        self.assertEqual({p.pid for p in mp.active_children()},prior)

    def test_full_grid_guard_has_no_generator_call(self):
        E,_=op.saved_energy()
        with self.assertRaisesRegex(ValueError,'FORBIDDEN'):
            op.parallel_build('legacy',E,(3200,6400),4)
        with self.assertRaisesRegex(ValueError,'FORBIDDEN'):
            op.serial_build('legacy',E,(3200,6400))

if __name__=='__main__':unittest.main(verbosity=2)
