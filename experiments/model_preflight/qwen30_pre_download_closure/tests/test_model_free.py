"""Only invented workers. No model imports or GPU calls; Linux OS proof stays pending."""
import sys
sys.dont_write_bytecode = True
import copy
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle
from runner.supervisor import run_synthetic, confined
from runner.semantic_validator import compare_receipts, validate_receipt
from runner.interface import native_byte_table
from runner.isolation import command


class ModelFreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = HERE / 'test_results/model_free_runs'
        cls.gov = HERE.parent / 'qwen30_infrastructure_governance'
        cls.receipts = {}
        cls.requests = {}
        # No existing output is deleted/overwritten; new batchID each invocation.
        batches = sorted(HERE.glob('test_results/model_free_batch_*.json'))
        cls.batch = len(batches) + 1
        for case in oracle.DISPOSITIONS:
            request = {'run_id': f'batch{cls.batch}_{case}', 'case': case, 'prompt_token_ids': [0, 5],
                'retry_count': 0, 'controls': copy.deepcopy(oracle.CONTROLS), 'byte_table': copy.deepcopy(oracle.TABLE)}
            cls.requests[case] = request
            cls.receipts[case] = run_synthetic(request, cls.root, cls.gov)

    def test_independent_dispositions(self):
        for case, expected in oracle.DISPOSITIONS.items():
            self.assertEqual([self.receipts[case]['mechanics_result'], self.receipts[case]['mechanics_failure_class']], expected)

    def test_normal_exact_whole_bytes(self):
        r = self.root / self.requests['normal']['run_id']
        self.assertEqual((r / 'raw_generated.bytes').read_bytes().hex(), oracle.NORMAL_RAW_HEX)
        self.assertEqual((r / 'normalized.bytes').read_bytes().hex(), oracle.NORMAL_NORMALIZED_HEX)

    def test_native_terminal_one_only(self):
        r = self.receipts['normal']['schema_payload']
        self.assertEqual(r['terminal_removal_receipt']['removed_token_ids'], [151645])
        self.assertEqual(r['terminal_removal_receipt']['removed_count'], 1)
        self.assertEqual(r['generated_token_count'], 2)

    def test_length2048(self):
        r = self.receipts['length']['schema_payload']
        self.assertEqual(len(r['raw_generated_token_ids']), oracle.LENGTH_COUNT)
        self.assertEqual(r['finish_reason'], 'LENGTH')
        self.assertEqual(r['terminal_removal_receipt']['removed_count'], 0)

    def test_native_at_cap_is_STOP(self):
        r = self.receipts['at_cap_native']['schema_payload']
        self.assertEqual(r['generated_token_count'], 2048)
        self.assertEqual(r['finish_reason'], 'STOP')
        self.assertEqual(r['terminal_removal_receipt']['removed_count'], 1)

    def test_invalid_utf8_preserved_failed(self):
        self.assertEqual(self.receipts['invalid_utf8']['mechanics_result'], 'FAIL')
        p = self.root / self.requests['invalid_utf8']['run_id'] / 'untrusted_raw.bytes'
        self.assertTrue(p.read_bytes().startswith(b'\xff'))
        self.assertIsNone(self.receipts['invalid_utf8']['schema_payload']['normalized_completion_sha256'])

    def test_only_CR_normalization(self):
        p = self.root / self.requests['line_endings']['run_id'] / 'normalized.bytes'
        self.assertEqual(p.read_bytes().hex(), oracle.LINE_NORMALIZED_HEX)

    def test_internal_special_retained(self):
        p = self.root / self.requests['internal_special']['run_id'] / 'normalized.bytes'
        self.assertEqual(p.read_bytes().hex(), oracle.INTERNAL_NORMALIZED_HEX)

    def test_one_call_zero_retry(self):
        for receipt in self.receipts.values():
            self.assertEqual(receipt['invocation_count'], oracle.ONE_CALL)
            self.assertEqual(receipt['retry_count'], oracle.RETRIES)

    def test_retry_violation_detected(self):
        self.assertEqual(self.receipts['retry_violation']['mechanics_failure_class'], 'B')

    def test_controls_mutation_detected(self):
        self.assertEqual(self.receipts['controls_violation']['mechanics_failure_class'], 'B')

    def test_no_actual_gate_pass(self):
        for receipt in self.receipts.values():
            self.assertTrue(receipt['model_free'])
            self.assertEqual(receipt['schema_payload']['gate_result'], 'PENDING')

    def test_literal_schema_required_fields(self):
        self.assertEqual(set(oracle.REQUIRED_FIELDS),set(self.receipts['normal']['schema_payload']))
        for field in oracle.REQUIRED_FIELDS:
            self.assertIn(field, self.receipts['normal']['schema_payload'])

    def test_policy_probe_decisions_and_OS_limit(self):
        p = self.root / self.requests['normal']['run_id'] / 'worker.stdout'
        event = json.loads(p.read_bytes())
        for k, v in oracle.ISOLATION_DECISIONS.items():
            self.assertEqual(event['policy_probe_results'][k], v)
        self.assertFalse(event['OS_enforcement_proven'])
        self.assertFalse(event['policy_probe_results']['acquisition_sentinel_in_child_env'])

    def test_output_path_confinement(self):
        for value in ['../escape', '/absolute', 'C:/outside', 'a\\b']:
            with self.assertRaises(ValueError):
                confined(self.root, value)

    def test_existing_run_refused_not_overwritten(self):
        p = self.root / self.requests['normal']['run_id'] / 'synthetic_receipt.json'
        before = p.read_bytes()
        with self.assertRaises(FileExistsError):
            run_synthetic(self.requests['normal'], self.root, self.gov)
        self.assertEqual(before, p.read_bytes())

    def test_missing_telemetry_pending(self):
        self.assertEqual(self.receipts['missing_telemetry']['mechanics_result'], 'PENDING')
        self.assertEqual(self.receipts['missing_telemetry']['mechanics_failure_class'], 'C')

    def test_telemetry_artifact_and_noGPU(self):
        p = self.root / self.requests['normal']['run_id'] / 'telemetry.json'
        d = json.loads(p.read_text())
        self.assertFalse(d['GPU_queries_performed'])
        self.assertTrue(d['samples'])
        self.assertEqual(d['sample_interval_ms'], 100)

    def test_injected_failure_retained_no_retry(self):
        r = self.receipts['injected_failure']
        self.assertEqual([r['mechanics_result'], r['mechanics_failure_class']], ['FAIL', 'B'])
        self.assertTrue((self.root / self.requests['injected_failure']['run_id'] / 'worker.stderr').read_bytes())

    def test_repeat_mismatch_detected(self):
        self.assertEqual(compare_receipts(self.receipts['normal'], self.receipts['mismatch']), 'FAIL')
        self.assertEqual(compare_receipts(self.receipts['normal'], self.receipts['normal']), 'PASS')

    def test_stale_state_detected(self):
        self.assertEqual(self.receipts['stale_history']['mechanics_result'], 'FAIL')

    def test_append_only_hash_chain(self):
        rows = [json.loads(b) for b in (self.root / 'provenance.jsonl').read_bytes().splitlines()]
        previous = '0' * 64
        for r in rows:
            self.assertEqual(r['previous_sha256'], previous)
            copy_r = {k: v for k, v in r.items() if k != 'entry_sha256'}
            expected = hashlib.sha256(json.dumps(copy_r, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
            self.assertEqual(r['entry_sha256'], expected)
            previous = r['entry_sha256']

    def test_semantic_receipt_mutation_fails(self):
        r = copy.deepcopy(self.receipts['normal'])
        r['schema_payload']['generated_token_count'] = 99
        event = json.loads((self.root / self.requests['normal']['run_id'] / 'worker.stdout').read_bytes())
        with self.assertRaises(ValueError):
            validate_receipt(r, self.requests['normal'], event, oracle.CONTROLS,
                bytes.fromhex(oracle.NORMAL_RAW_HEX), bytes.fromhex(oracle.NORMAL_NORMALIZED_HEX))

    def test_byte_alphabet_without_model(self):
        table = native_byte_table({'model': {'vocab': {'!': 0, 'Ġ': 1}}, 'added_tokens': [{'id': 151645, 'content': '<|im_end|>'}]})
        self.assertEqual(table['0'], '21')
        self.assertEqual(table['1'], '20')
        self.assertEqual(table['151645'], '3c7c696d5f656e647c3e')

    def test_isolation_command_is_exact_constrained(self):
        # Command construction only; no Docker/GPU execution or enforcement claim.
        roots = [self.root / name for name in ['mockmodel', 'mockinput', 'mockoutput', 'mockscratch']]
        for p in roots:
            p.mkdir(exist_ok=True)
        args = command('sha256:' + '1' * 64, *roots, HERE)
        self.assertIn('--network=none', args)
        self.assertIn('--cap-drop=ALL', args)
        self.assertIn('--user=65532:65532', args)
        self.assertEqual(args[-1], 'runner.isolation_probe')
        self.assertNotIn('--gpus=all', args)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ModelFreeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    obj = {'result': 'PASS' if result.wasSuccessful() else 'FAIL', 'tests_run': result.testsRun,
        'failures': [(str(t), trace) for t, trace in result.failures], 'errors': [(str(t), trace) for t, trace in result.errors],
        'model_free_only': True, 'actual_Qwen_runs': 0, 'GPU_calls': 0,
        'Linux_OS_enforcement': 'PENDING_TARGET_LINUX_ATTESTATION',
        'review_classification': 'Implementer model-free verification; not an assigned independent reviewer disposition'}
    (HERE / f'test_results/model_free_batch_{ModelFreeTests.batch}.json').write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
