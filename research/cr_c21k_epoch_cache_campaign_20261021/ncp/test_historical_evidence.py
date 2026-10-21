"""Two negative checks against an already staged immutable historical archive."""
import argparse
from pathlib import Path
import tempfile
import unittest

import prepare_historical_evidence as staging

ARCHIVE = None
STAGED = None


class HistoricalEvidenceNegativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if ARCHIVE is None or STAGED is None:
            raise unittest.SkipTest('Requires explicit --archive and previously successful --staged paths')

    def test_create_only_rejects_existing_admission_root(self):
        receipt = STAGED / 'STAGING_RECEIPT.json'
        before = receipt.read_bytes()
        with self.assertRaisesRegex(staging.AdmissionError, 'CREATE_ONLY_OUTPUT_ALREADY_EXISTS'):
            staging.prepare(ARCHIVE, STAGED)
        self.assertEqual(receipt.read_bytes(), before)

    def test_one_byte_archive_tamper_rejected_before_output(self):
        raw = bytearray(ARCHIVE.read_bytes())
        raw[0] ^= 1
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            modified = root / 'modified_archive.tar.gz'
            modified.write_bytes(raw)
            output = root / 'must_not_exist'
            with self.assertRaisesRegex(staging.AdmissionError, 'ORIGINAL_ARCHIVE_IDENTITY_MISMATCH'):
                staging.prepare(modified, output)
            self.assertFalse(output.exists())
        self.assertEqual(staging.file_record(ARCHIVE), staging.ARCHIVE_PIN)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--staged', type=Path, required=True)
    arguments = parser.parse_args()
    ARCHIVE, STAGED = arguments.archive, arguments.staged
    unittest.main(argv=['test_historical_evidence.py'], verbosity=2)
