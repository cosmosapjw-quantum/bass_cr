"""External analysis anchors; synthetic receipts do not represent native runs."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analyze_campaign as analysis
from campaign_contract import POLICY, canonical_hash, file_record, sha256


class AnalysisBindingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.baseline = self.root / 'baseline'
        records = {}
        for name in POLICY['fixtures']:
            path = self.baseline / name / 'fixture.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'synthetic_analysis_anchor': name}) + '\n')
            records[str(path.relative_to(self.baseline))] = file_record(path)
        manifest = self.root / 'EXECUTION_MANIFEST.json'
        manifest.write_text(json.dumps({'baseline_files': records,
                                       'policy_sha256': canonical_hash(POLICY)}) + '\n')
        name = 'native_source'
        self.receipt = {'status': 'COMPLETE',
                        'job': {'id': name + '_reference_L1', 'fixture': name},
                        'signature_data': {'micro': 'native', 'binary_sha256': 'a' * 64,
                            'fixture_sha256': canonical_hash({'synthetic_analysis_anchor': name}),
                            'input_manifest_sha256': sha256(manifest)}}

    def test_verified_payload_is_bound_to_external_manifest_and_fixture(self):
        result = {'synthetic_result_only': True}
        with patch.object(analysis, 'HERE', self.root), patch('run_campaign.verify_payload_record', return_value=result) as verify:
            loaded = analysis.completed_results([self.receipt], self.baseline)
            self.assertEqual(loaded, {self.receipt['job']['id']: result})
            verify.assert_called_once_with(self.receipt)
            for key, wrong in (('micro', 'manufactured'), ('fixture_sha256', 'b' * 64),
                               ('input_manifest_sha256', 'c' * 64)):
                bad = copy.deepcopy(self.receipt)
                bad['signature_data'][key] = wrong
                with self.subTest(key=key), self.assertRaises(ValueError):
                    analysis.completed_results([bad], self.baseline)

    def test_duplicate_mixed_binary_and_payload_failure_are_rejected(self):
        with patch.object(analysis, 'HERE', self.root), patch('run_campaign.verify_payload_record', return_value={}) as verify:
            with self.assertRaisesRegex(ValueError, 'DUPLICATE_JOB_ID'):
                analysis.completed_results([self.receipt, self.receipt], self.baseline)
            second = copy.deepcopy(self.receipt)
            second['job']['id'] = 'native_source_reference_L2'
            second['signature_data']['binary_sha256'] = 'd' * 64
            with self.assertRaisesRegex(ValueError, 'MIXED_NATIVE_BINARIES'):
                analysis.completed_results([self.receipt, second], self.baseline)
            verify.side_effect = ValueError('PAYLOAD_MANIFEST_MISMATCH')
            with self.assertRaisesRegex(ValueError, 'PAYLOAD_MANIFEST_MISMATCH'):
                analysis.completed_results([self.receipt], self.baseline)

    def test_changed_baseline_is_rejected_before_payload_admission(self):
        (self.baseline / 'native_source' / 'fixture.json').write_text('{}\n')
        with patch.object(analysis, 'HERE', self.root), patch('run_campaign.verify_payload_record') as verify:
            with self.assertRaisesRegex(ValueError, 'PINNED_FILE_MISMATCH'):
                analysis.completed_results([self.receipt], self.baseline)
            verify.assert_not_called()


if __name__ == '__main__':
    unittest.main()
