import datetime as dt
import unittest
from vigilancia import external_opening_authority


class ExternalOpeningTests(unittest.TestCase):
    def test_cutover_never_claims_passed_or_failed_without_external_evidence(self):
        for state in ('PASSED', 'FAILED', 'PENDING'):
            for health in ('HEALTHY', 'INCOMPLETE_CAPTURE', 'STALE_OR_MISSING', 'CLOSED'):
                original = {'opening_acceptance': state, 'health': health}
                result = external_opening_authority(original, dt.datetime(2026, 9, 29, 14, tzinfo=dt.timezone.utc))
                self.assertEqual(result['opening_acceptance'], 'EXTERNAL_AUDIT_REQUIRED')
                self.assertEqual(result['health'], health)
                self.assertFalse(result['opening_evidence_verified_here'])
                self.assertEqual(original['opening_acceptance'], state)

    def test_historical_native_results_preserved(self):
        original = {'opening_acceptance': 'FAILED', 'health': 'CLOSED'}
        self.assertIs(external_opening_authority(original, dt.datetime(2026, 9, 28, 22, tzinfo=dt.timezone.utc)), original)
