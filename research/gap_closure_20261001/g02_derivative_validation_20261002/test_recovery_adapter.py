"""Targeted interruption federation checks; never invoke physical workers."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import recovery_adapter as recovery

WORKSPACE = Path(__file__).resolve().parents[5]
ROOT = WORKSPACE / 'runs_r4z'


class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = recovery.collect_original(ROOT / 'central_v1', recovery.ORIGINAL_CONTEXT_SHA,
                                                 ROOT / 'RECOVERY_INVENTORY.json')
        cls.plan = recovery.runner.read_json(ROOT / 'RECOVERY_PLAN.json')

    def args(self):
        _, _, observations, _, _, _, ledger, missing = self.original
        return missing, [x['task']['task_id'] for x in observations.values()], ledger

    def test_original_payload_inventory_and_partial_batch(self):
        _, _, observations, terminal, partial, bindings, ledger, missing = self.original
        self.assertEqual((len(observations), len(ledger), len(missing), len(bindings)), (25, 28, 15, 100))
        self.assertEqual([x['name'] for x in terminal], ['pilot'])
        self.assertIsNone(partial[0]['wall_seconds'])
        self.assertFalse((ROOT / 'central_v1/batches/main/COMPLETED.json').exists())

    def test_plan_exactly_missing_includes_three_interrupted(self):
        tasks = recovery.assert_missing_plan(self.plan, *self.args())
        self.assertEqual(len(tasks), 15)
        ledger_ids = {x['task']['task_id'] for x in self.args()[2]}
        self.assertEqual(len({x['task_id'] for x in tasks} & ledger_ids), 3)

    def test_completed_task_reexecution_rejected(self):
        plan = copy.deepcopy(self.plan)
        task = next(iter(self.original[2].values()))['task']
        plan['tasks'][0] = {k: task[k] for k in plan['tasks'][0]}
        with self.assertRaises(ValueError):
            recovery.assert_missing_plan(plan, *self.args())

    def test_duplicate_recovery_task_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['tasks'][1] = copy.deepcopy(plan['tasks'][0])
        with self.assertRaises(ValueError):
            recovery.assert_missing_plan(plan, *self.args())

    def test_changed_scientific_resolution_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['tasks'][0]['order'] = 56
        with self.assertRaises(ValueError):
            recovery.assert_missing_plan(plan, *self.args())

    def test_tamper_byte_binding_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'data.json'
            path.write_text('{"a":1}')
            binding = recovery.file_binding(path)
            path.write_text('{"a":2}')
            with self.assertRaises(ValueError):
                recovery.validate_file(binding)

    def test_create_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'record.json'
            recovery.create_json(path, {'a': 1})
            with self.assertRaises(FileExistsError):
                recovery.create_json(path, {'a': 2})
            self.assertEqual(json.loads(path.read_text()), {'a': 1})

    def test_frozen_original_analyzer_identity(self):
        self.assertEqual(recovery.runner.sha(recovery.HERE / 'derivative_analyzer.py'), recovery.ORIGINAL_ANALYZER_SHA)


if __name__ == '__main__':
    unittest.main()
