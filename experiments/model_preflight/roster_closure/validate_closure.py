"""Independent static closure consistency/hash checks; standard library, no model or network."""
import sys
sys.dont_write_bytecode = True
import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
WORKSPACE = ROOT.parents[2]
REQUIRED = ['REPORT.md', 'model_status_matrix.csv', 'mechanism_coverage_matrix.csv',
            'infrastructure_roster.json', 'verification_order.json', 'fallback_resolution.json',
            'closure_decision.json', 'source_manifest.json', 'artifact_manifest.json', 'validation.json']
ORDER = ['qwen3_coder_30b_a3b', 'devstral_small2_2512', 'glm47_flash', 'nemotron35_lightning_bf16', 'qwen3_coder_next']
VERDICT = 'PROCEED TO INFRASTRUCTURE VERIFICATION'
DROP = 'DROP — CURRENT PROTOCOL INCOMPATIBLE'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name, parent=ROOT):
    return json.loads((parent / name).read_text(encoding='utf-8'))


def dump(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def rows(name, parent=ROOT):
    with (parent / name).open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        values = list(reader)
        assert values and all(set(r) == set(reader.fieldnames) and all(v is not None for v in r.values()) for r in values), name
        return reader.fieldnames, values


def verify_record(row, parent):
    path = (parent / row['path']).resolve()
    assert path.is_relative_to(parent), row['path']
    data = path.read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256'], row['path']


def git(*args):
    return subprocess.check_output(['git', *args], cwd=WORKSPACE, text=True, encoding='utf-8').strip()


def main():
    assert all((ROOT / n).is_file() for n in REQUIRED if n not in ['artifact_manifest.json', 'validation.json'])
    # Enumerate only the dedicated new closure output tree, never protected inventories.
    files = [p for p in ROOT.rglob('*') if p.is_file()]
    assert not any(p.suffix.lower() in {'.safetensors', '.gguf', '.pt', '.pth', '.bin'} or '__pycache__' in p.parts for p in files)
    parsed_json = []
    for path in files:
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
            parsed_json.append(path.name)
    source = read('source_manifest.json')
    assert source['network_requests'] == 0 and source['new_checkpoint_introduced'] is False
    assert source['frozen_landscape_cutoff'] == '2026-10-03, Asia/Calcutta'
    assert source['review_date_local'] == '2026-10-04' and source['timezone'] == 'Asia/Calcutta'
    assert len(source['files']) == len({r['path'] for r in source['files']}) == 71
    for row in source['files']:
        verify_record(row, WORKSPACE)
    request = source['request']
    data = (ROOT / request['copy']).read_bytes()
    assert len(data) == request['bytes'] and sha(data) == request['sha256']
    assert Path(request['original_path']).read_bytes() == data
    known_inputs = {r['path'] for r in source['files']}
    report = (ROOT / 'REPORT.md').read_text(encoding='utf-8')
    assert [int(n) for n in re.findall(r'^## (\d+)\.', report, re.M)] == list(range(1, 19))
    assert '**STOP MODEL SHOPPING: YES**' in report
    for link in re.findall(r'\]\(([^)]+)\)', report):
        assert '://' not in link, 'Closure adds no remote refreshed source link'
        if link in ['artifact_manifest.json', 'validation.json']:
            continue
        assert (ROOT / link).resolve().is_file(), link
        if link.startswith('../'):
            assert (ROOT / link).resolve().relative_to(WORKSPACE).as_posix() in known_inputs, link

    _, landscape_rows = rows('landscape.csv', BASE / 'landscape_closure')
    landscape = {r['repository']: r for r in landscape_rows}
    fields, statuses = rows('model_status_matrix.csv')
    assert fields == ['model', 'repository', 'revision', 'static_verdict', 'verdict_source',
                      'full_stream_Draft3_status', 'fresh_original_adaptation_status', 'architecture_adaptation_regime',
                      'remaining_empirical_blockers', 'fallback_status', 'redundancy_classification', 'eligible_for_infrastructure_verification']
    assert len(statuses) == 6 and len({r['repository'] for r in statuses}) == 6
    assert all(all(r.values()) for r in statuses)
    status_map = {r['repository']: r for r in statuses}
    eligible = {r['repository'] for r in statuses if r['eligible_for_infrastructure_verification'] == 'YES'}
    assert len(eligible) == 5
    for r in statuses:
        assert r['revision'] == landscape[r['repository']]['revision']
        assert re.fullmatch('[a-f0-9]{40}', r['revision'])
        authority = (BASE / r['verdict_source']).read_text(encoding='utf-8')
        if r['repository'] == 'openai/gpt-oss-20b':
            assert r['eligible_for_infrastructure_verification'] == 'NO' and r['static_verdict'] == DROP
            assert DROP in authority and 'Final-only Harmony extraction' in authority
        else:
            assert r['static_verdict'] == VERDICT and VERDICT in authority
            assert r['redundancy_classification'] == 'NON-REDUNDANT'
            assert r['full_stream_Draft3_status'] == 'STATICALLY COMPATIBLE; raw full suffix'

    roster = read('infrastructure_roster.json')
    order = read('verification_order.json')
    decision = read('closure_decision.json')
    fallback = read('fallback_resolution.json')
    assert roster['candidate_count'] == len(roster['candidates']) == 5
    assert [c['configuration_id'] for c in roster['candidates']] == order['sequence'] == ORDER
    assert {c['repository'] for c in roster['candidates']} == eligible
    assert order['priority_rule'] == ['coverage gain', 'fresh-original adaptation testability', 'verification burden', 'resource burden', 'retain both if still tied']
    assert order['Qwen30_before_Next_preserved'] and ORDER.index('qwen3_coder_30b_a3b') < ORDER.index('qwen3_coder_next')
    assert order['minimum_first_configuration'] == order['minimum_required_path']['configurations'][0] == ORDER[0]
    assert order['minimum_required_path']['source_gate_ids'] == list('ABCDEFGHIJKLMNOPQRS')
    assert order['extended_mechanism_coverage_path']['configurations'] == ORDER[1:]
    assert len(order['ordering_decisions']) == 4
    for i, pair in enumerate(order['ordering_decisions']):
        assert (pair['before'], pair['after']) == (ORDER[i], ORDER[i + 1])
        assert all(pair[k] for k in ['coverage', 'adaptation_testability', 'verification_burden', 'resource_burden'])
    count = 0
    for c in roster['candidates']:
        directory = c['configuration_id']
        assert c['repository'] in landscape and c['revision'] == landscape[c['repository']]['revision']
        assert c['static_verdict'] == status_map[c['repository']]['static_verdict'] == VERDICT
        identity = read(c['identity_source'], BASE)
        assert identity['repository'] == c['repository'] and identity['revision'] == c['revision']
        assert c['remaining_static_execution_blocker'] is None and c['redundancy'] == 'NON-REDUNDANT'
        assert c['runtime_is_proposal_not_verified_environment'] and c['resources_are_descriptive_not_measured_or_hardware_ceiling']
        contract = c['common_contract']
        assert (contract['P_bytes'], contract['K_bytes'], contract['H_bytes'], contract['BC_owned_lane_bytes']) == (4096, 12288, 4096, 2048)
        assert contract['deployed_context'] == 32768 and contract['generated_token_reserve'] == 2048
        assert contract['entire_emitted_textual_suffix'] and contract['verified_final_native_terminal_removal_only'] and contract['CRLF_CR_to_LF_only']
        assert contract['no_reasoning_parser_or_final_projection'] and contract['retries'] == 0
        assert all(contract[k] is False for k in ['clipping', 'context_shifting', 'prompt_truncation', 'protocol_change', 'model_execution_authorized_by_this_step'])
        _, original_tests = rows(c['infrastructure_matrix_source'], BASE)
        if directory.startswith('qwen'):
            label = 'Qwen3-Coder-30B-A3B' if directory == 'qwen3_coder_30b_a3b' else 'Qwen3-Coder-Next'
            original_tests = [r for r in original_tests if r['model'] == label]
            assert c['proposed_runtime'] == read(directory + '/proposed_runtime.json', BASE)
            assert len(original_tests) == 19
            assert [r['id'] for r in original_tests] == list('ABCDEFGHIJKLMNOPQRS')
            regex = c['conservative_adaptation']['target_regex']
            assert re.fullmatch(regex, 'model.layers.0.self_attn.q_proj')
            assert not re.fullmatch(regex, 'model.layers.48.self_attn.q_proj')
            assert not re.fullmatch(regex, 'model.layers.0.mlp.gate')
            if directory == 'qwen3_coder_next':
                assert re.fullmatch(regex, 'model.layers.0.linear_attn.in_proj_qkvz')
                assert c['conservative_adaptation']['rank16_parameter_estimate'] == read(directory + '/adapter_parameter_estimates.json', BASE)['examples'][1]['all_attention'] == 17141760
            else:
                cfg = read(directory + '/upstream/config.json', BASE)
                h, q, kv = cfg['hidden_size'], cfg['num_attention_heads'] * cfg['head_dim'], cfg['num_key_value_heads'] * cfg['head_dim']
                assert c['conservative_adaptation']['rank16_parameter_estimate'] == cfg['num_hidden_layers'] * 16 * (2 * (q + h) + 2 * (kv + h)) == 13369344
        else:
            assert c['proposed_runtime'] == read(directory + '/runtime_profile.json', BASE)
            assert len(original_tests) == 24 and [r['id'] for r in original_tests] == list('ABCDEFGHIJKLMNOPQRSTUVWX')
            targets = read(directory + '/adaptation_targets.json', BASE)
            scope_name = {'devstral_small2_2512': 'attention_only', 'glm47_flash': 'MLA_attention_only', 'nemotron35_lightning_bf16': 'conservative_attention'}[directory]
            assert c['conservative_adaptation'] == targets['scopes'][scope_name]
            serialization = read(directory + '/serialization.json', BASE)
            assert c['selected_native_profile']['input'] == serialization['canonical_render']
            assert c['selected_native_profile']['generation_prefix'] == serialization['generation_prefix']
            if directory != 'devstral_small2_2512':
                assert c['selected_native_profile']['name'] == serialization['selected_profile']
                assert serialization['full_stream_Draft3_compatibility_statically_established'] and not serialization['selected_thinking_effort_changed']
            else:
                assert c['original_conversion'] == read(directory + '/reconstruction_analysis.json', BASE)
                assert c['original_conversion']['static_path_established'] and not c['original_conversion']['prequantization_BF16_recovered']
            assert c['resource_regime'] == read(directory + '/resource_estimates.json', BASE)
        assert c['NOT_RUN_infrastructure_checks'] == original_tests
        assert c['NOT_RUN_infrastructure_count'] == len(original_tests)
        assert all(r['status'] == 'NOT_RUN' for r in original_tests)
        assert c['conservative_verification_gate_ids'] == [r['id'] for r in original_tests if r['id'] not in c['deferred_extended_scope_test_ids']]
        assert all(s['required_for_minimum'] is False for s in c['optional_conditional_scopes'])
        count += len(original_tests)
    assert count == roster['NOT_RUN_total_source_matrix_rows'] == 110
    _, coverage = rows('mechanism_coverage_matrix.csv')
    assert {r['required_mechanism'] for r in coverage} == set(decision['required_core_gaps_resolved']) == {
        'ordinary_dense_attention_MLP', 'ordinary_attention_routed_MoE', 'hybrid_recurrent_DeltaNet', 'MLA', 'Mamba2_state_space'}
    assert len(coverage) == 5
    assert all(all(r.values()) for r in coverage)
    assert all(r['static_gap_resolved'] == 'YES' and r['infrastructure_verified'] == 'NO' and r['repository'] in eligible and r['revision'] == status_map[r['repository']]['revision'] for r in coverage)
    assert fallback['triggered'] == decision['fallbacks_triggered'] == [] and fallback['nemotron_fallback'] is None
    assert len(fallback['predeclared_fallbacks']) == 2
    for f in fallback['predeclared_fallbacks']:
        assert f['status'] == 'NOT TRIGGERED' and f['fallback_revision'] == landscape[f['fallback_repository']]['revision']
        assert f['fallback_repository'] not in eligible and not f['admitted_to_infrastructure_roster'] and not f['fallback_work_executed_in_closure']
        assert read(f['primary_configuration_id'] + '/original_base_lifecycle.json', BASE)['fallback_triggered'] is False
    assert decision['decision'] == 'STOP MODEL SHOPPING: YES' and decision['static_landscape_closed']
    assert decision['bounded_queue_complete'] and decision['static_infrastructure_roster_frozen']
    assert not decision['optional_regimes_made_mandatory']
    for key in ['final_experimental_roster_frozen', 'final_protocol_external_freeze', 'infrastructure_success_claimed', 'Study1_readiness_claimed',
                'protocol_modified', 'new_model_search', 'new_checkpoint_introduced', 'weight_bodies_acquired', 'model_instantiated',
                'adapter_executed', 'inference_occurred', 'GPU_execution', 'protected_candidates_accessed', 'benchmark_outcomes_used', 'commit_made', '1G2A_started']:
        assert decision[key] is False, key
    assert not roster['final_experimental_model_roster_frozen'] and not roster['complete_executable_profiles_frozen']
    assert not roster['final_current_repo_v1_protocol_externally_frozen'] and not roster['Study1_ready'] and not roster['execution_authorized']
    failure = order['failure_policy_handoff']
    assert failure == roster['failure_policy_handoff']
    assert [failure[k]['class'] for k in 'ABC'] == ['PROTOCOL/MODEL INCOMPATIBILITY', 'INFRASTRUCTURE/CONFIGURATION DEFECT', 'MEASUREMENT/VERIFICATION INCOMPLETE']

    # Authored code never imports model/network/runtime libraries. No downloaded code is executed.
    imports = []
    for path in ROOT.glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Import):
                imports.extend(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append((node.module or '').split('.')[0])
    assert not set(imports) & {'torch', 'transformers', 'peft', 'vllm', 'tokenizers', 'requests', 'urllib', 'socket', 'http', 'httpx'}
    baseline = read('baseline_integrity.json')
    assert len(baseline['preserved_files']) == len({r['path'] for r in baseline['preserved_files']}) == 1217
    for row in baseline['preserved_files']:
        verify_record(row, WORKSPACE)
    head, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert head == baseline['head'] == '7fcdecbe26f4fd01138edf8f58c02ce4b947db0b'
    assert status == baseline['status'] == '?? experiments/model_preflight/'
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    validation = {'status': 'PASS_STATIC_CLOSURE_VALIDATION', 'validated_at_utc': datetime.now(timezone.utc).isoformat(),
        'decision': decision['decision'], 'all_required_artifacts_present': True, 'JSON_parses': True,
        'JSON_files_parsed_before_finalization': len(parsed_json), 'CSV_schema_and_rows_valid': True,
        'source_input_hashes_verified': 71, 'preserved_existing_file_hashes_verified': 1217,
        'report_sections': 18, 'local_source_references_valid': True, 'all_six_checkpoint_identities_and_SHAs_match_sources': True,
        'all_final_verdicts_match_controlling_sources': True, 'historical_Harmony_supersession_explicit': True,
        'frozen_stop_criterion_satisfied_for_core_scope': True, 'five_mechanisms_statically_represented': True,
        'five_infrastructure_candidates': True, 'lineage_rule_and_Qwen_order_preserved': True,
        'exact_runtime_and_conservative_scopes_retained': True, 'matrix_rows_and_statuses_match_sources': True,
        'source_infrastructure_NOT_RUN_count': 110, 'fallbacks_triggered': [], 'minimum_first_configuration': ORDER[0],
        'protocol_unchanged': True, 'Draft2_Draft3_and_policy_hashes_unchanged': True, 'product_repositories_unchanged': True,
        'no_model_search_or_release_refresh': True, 'no_new_checkpoint': True, 'no_weight_acquisition': True,
        'no_model_instantiation': True, 'no_adapter_execution': True, 'no_inference': True, 'no_GPU_execution': True,
        'protected_candidate_inventory_or_task_accessed': False, 'benchmark_outcomes_used': False,
        'candidate_blindness_evidence': 'Scope/process attestation, local input and preservation allowlists, authored imports; not an OS-level isolation/no-read trace certificate',
        'infrastructure_success_claimed': False, 'final_experimental_model_roster_frozen': False,
        'final_protocol_external_freeze_claimed': False, 'Study1_readiness_claimed': False, '1G2A_started': False,
        'HEAD_unchanged': True, 'git_tracked_and_staged_diff_empty': True, 'final_HEAD': head,
        'initial_git_status': baseline['status'], 'final_git_status': status, 'commit_made': False,
        'artifact_manifest_method': 'Hash every dedicated closure file after validation; exclude only the manifest itself to avoid circular hashing'}
    dump('validation.json', validation)
    files = sorted((p for p in ROOT.rglob('*') if p.is_file() and p.name != 'artifact_manifest.json'), key=lambda p: p.relative_to(ROOT).as_posix())
    dump('artifact_manifest.json', {'scope': 'Entire dedicated roster closure tree', 'excluded_self': 'artifact_manifest.json',
         'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in files]})
    for row in read('artifact_manifest.json')['files']:
        verify_record(row, ROOT)
    assert all((ROOT / n).is_file() for n in REQUIRED)
    read('validation.json')
    print(json.dumps({'status': validation['status'], 'source_inputs': 71, 'preserved_files': 1217,
        'artifact_hashes': len(files), 'NOT_RUN': 110, 'candidate_count': 5, 'HEAD': head, 'git_status': status}, indent=2))


if __name__ == '__main__':
    main()
