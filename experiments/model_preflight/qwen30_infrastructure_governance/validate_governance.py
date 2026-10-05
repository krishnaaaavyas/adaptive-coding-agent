"""Static design/source/preservation checks only. No A-S gate execution.

--seal writes validation + the final artifact manifest. --verify is read-only.
Uses the already-installed jsonschema package; no dependency installation.
"""
import sys
sys.dont_write_bytecode = True
import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import re
import subprocess
from pathlib import Path
import jsonschema

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXPECTED_HEAD = '7fcdecbe26f4fd01138edf8f58c02ce4b947db0b'
EXPECTED_REPO = 'Qwen/Qwen3-Coder-30B-A3B-Instruct'
EXPECTED_REV = 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120'
EXPECTED_ORDER = ['qwen3_coder_30b_a3b', 'devstral_small2_2512', 'glm47_flash',
                  'nemotron35_lightning_bf16', 'qwen3_coder_next']
REQUIRED = ['REPORT.md', 'failure_policy.json', 'repair_policy.json', 'gate_dependency_graph.json',
    'runtime_lock.json', 'execution_profile.json', 'generation_profile.json', 'fixture_manifest.json',
    'repeatability_policy.json', 'resource_measurement_policy.json', 'adaptation_lifecycle_plan.json',
    'run_manifest_schema.json', 'hardware_requirements.json', 'pre_download_checklist.json',
    'source_manifest.json', 'artifact_manifest.json', 'validation.json']


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def row(p, root=HERE):
    b = p.read_bytes()
    return {'path': p.relative_to(root).as_posix(), 'bytes': len(b), 'sha256': sha(b)}


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')


def git(args):
    return subprocess.check_output(['git'] + args, cwd=REPO, text=True, encoding='utf-8').strip()


def literal_assignments(p):
    values = {}
    for n in ast.parse(p.read_text(encoding='utf-8')).body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    try:
                        values[t.id] = ast.literal_eval(n.value)
                    except (ValueError, TypeError):
                        pass
    return values


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def validate():
    checks = []
    def require(name, condition, evidence=None):
        assert condition, name
        checks.append({'check': name, 'status': 'PASS', 'evidence': evidence})

    head, status = git(['rev-parse', 'HEAD']), git(['status', '--short'])
    require('HEAD unchanged', head == EXPECTED_HEAD, head)
    require('Git worktree status unchanged', status == load(HERE / 'baseline_integrity.json')['status'], status)
    require('No tracked modifications', git(['diff', '--name-only']) == '' and git(['diff', '--cached', '--name-only']) == '')
    require('Required preparation artifacts exist', all((HERE / n).is_file() for n in REQUIRED if n not in {'validation.json', 'artifact_manifest.json'}))
    # All inventory is confined to the new directory; prior paths are an explicit allowlist.
    all_files = sorted(p for p in HERE.rglob('*') if p.is_file())
    parsed = [p for p in all_files if p.suffix == '.json']
    for p in parsed:
        load(p)
    require('Every JSON parses', True, {'json_files': len(parsed)})
    require('No weight/package/container layer bodies in new tree', not any(p.suffix.lower() in
        {'.safetensors', '.whl', '.gz', '.zip', '.deb', '.gguf', '.pt', '.pth', '.bin', '.tar'} for p in all_files))
    for r in load(HERE / 'baseline_integrity.json')['preserved_files']:
        p = (REPO / r['path']).resolve()
        require('Preserved prior file: ' + r['path'], p.is_relative_to(REPO) and row(p, REPO) == r)
    require('Complete historical preservation set', len(load(HERE / 'baseline_integrity.json')['preserved_files']) == 1231)
    require('Roster order unchanged', load(REPO / 'experiments/model_preflight/roster_closure/verification_order.json')['sequence'] == EXPECTED_ORDER)

    runtime = load(HERE / 'runtime_lock.json')
    require('Exact checkpoint identity', runtime['subject'] == {'repository': EXPECTED_REPO, 'revision': EXPECTED_REV})
    require('Pinned vLLM source version and commit', runtime['vllm']['version'] == '0.11.2' and runtime['vllm']['repository_commit'] == '275de34170654274616082721348b7edd9741d32')
    require('Executable lock honestly pending', runtime['status'] == 'SOURCE_LOCK_RESOLVED_EXECUTABLE_LOCK_PENDING' and not runtime['complete_executable_lock'] and runtime['final_container_image_digest'] is None)
    for match in runtime['vllm']['archived_correspondence']:
        a, b = match['historical'], match['resolved_commit_source']
        require('Source correspondence: ' + b['path'], row(REPO / a['path'], REPO) == a and row(HERE / b['path']) == b and a['sha256'] == b['sha256'])
    require('Eight archived source correspondences', len(runtime['vllm']['archived_correspondence']) == 8)
    sm = load(HERE / 'source_manifest.json')
    for r in sm['public_runtime_metadata']:
        require('Bounded metadata hash: ' + r['path'], r['status'] == 'retrieved' and r['bytes'] <= r['limit_bytes'] == 2000000 and
                row(HERE / r['path']) == {k: r[k] for k in ['path', 'bytes', 'sha256']})
    for r in sm['local_authoritative_inputs']:
        require('Authoritative input hash: ' + r['path'], row(REPO / r['path'], REPO) == r)
    require('Copied request hash', row(HERE / 'request_source.txt') == sm['request'])
    require('Base image selected by digest, not tag', re.fullmatch(r'nvidia/cuda@sha256:[a-f0-9]{64}', runtime['platform']['container_base']) is not None)
    docker_text = (HERE / 'sources/vllm-project__vllm/docker/Dockerfile').read_text(encoding='utf-8')
    require('Stock Docker defaults mismatch disclosed', 'ARG CUDA_VERSION=12.9.1' in docker_text and 'ARG PYTHON_VERSION=3.12' in docker_text and runtime['build']['reference_defaults'] == {'CUDA_VERSION': '12.9.1', 'PYTHON_VERSION': '3.12'})
    bodies = load(HERE / 'expected_checkpoint_bodies.json')
    require('16 immutable declared shard bodies; zero verified/acquired', len(bodies['shards']) == 16 and sum(r['bytes'] for r in bodies['shards']) == 61066575656 and not bodies['body_acquisition_performed'] and not any(r['local_weight_body_verified'] for r in bodies['shards']))

    policy = load(REPO / 'benchmark_design/context_policy/current-repo-v1-draft3.json')
    independent = literal_assignments(REPO / 'harness/tests/policy_fixtures.py')
    g = load(HERE / 'generation_profile.json')
    literal = g['independent_literal_expected_controls']
    require('Literal controls exactly/typed match independent conformance and normative controls',
            typed_equal(literal, independent['EXPECTED_CONTROLS']) and typed_equal(literal, policy['profile_schema']['controls']))
    require('Literal SYSTEM exactly matches independent and normative bytes', g['independent_system_literal'] == independent['EXPECTED_SYSTEM'] == policy['system'] and sha(g['independent_system_literal'].encode()) == g['SYSTEM_utf8_sha256'])
    for key, value in [('seed', 7), ('temperature', 2), ('decoding', 'sample'), ('retries', 1), ('clipping', True)]:
        changed = copy.deepcopy(literal)
        changed[key] = value
        require('Independent oracle rejects literal mutation: ' + key, not typed_equal(changed, independent['EXPECTED_CONTROLS']))
    bool_as_int = copy.deepcopy(literal)
    bool_as_int['seed'] = False
    require('Typed oracle rejects bool pretending to be integer0', not typed_equal(bool_as_int, independent['EXPECTED_CONTROLS']))
    original = load(REPO / 'experiments/model_preflight/qwen3_coder_30b_a3b/proposed_runtime.json')
    require('Historical runtime sampling/engine controls unchanged', all(typed_equal(g['requested_runtime_sampling'][k], v) for k, v in original['sampling'].items()) and all(typed_equal(g['requested_runtime_engine'][k], v) for k, v in original['engine'].items()))
    require('Context/reserve/native terminals fixed', g['requested_runtime_engine']['max_model_len'] == 32768 and g['requested_runtime_sampling']['max_tokens'] == 2048 and g['terminals']['primary_native_EOS'] == 151645 and g['terminals']['additional_native_stop_id'] == 151643)
    require('Budgets unchanged', policy['budgets']['P'] == 4096 and policy['budgets']['K'] == 12288 and policy['budgets']['H'] == 4096 and policy['budgets']['generation'] == 2048)

    prov = load(REPO / 'benchmark_design/context_policy/repair_provenance.json')
    for group in ['source_manifest', 'conformance_manifest']:
        actual = [{'path': r['path'], 'sha256': sha((REPO / r['path']).read_bytes())} for r in prov[group]]
        require('Current parser provenance rows: ' + group, actual == prov[group])
        actual.sort(key=lambda r: r['path'].encode('utf-8'))
        rootsha = sha(json.dumps(actual, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode())
        require('Current parser canonical manifest root: ' + group, rootsha == prov[group + '_sha256'])
    require('Current r2 descriptor/build identity preserved', runtime['parser']['implementation_revision'] == 'current-repo-v1-draft3-implementation-r2' and runtime['parser']['implementation_build_sha256'] == prov['implementation_build_sha256'])

    graph = load(HERE / 'gate_dependency_graph.json')
    gates = {r['historical_id']: r for r in graph['gates']}
    require('Historical A-S IDs and NOT_RUN states', list(gates) == list('ABCDEFGHIJKLMNOPQRS') and all(r['execution_status'] == 'NOT_RUN' for r in gates.values()))
    resolved = set()
    while len(resolved) < len(gates):
        ready = {g for g, r in gates.items() if g not in resolved and set(r['prerequisites']) <= resolved}
        require('DAG has ready nodes at layer' + str(len(resolved)), bool(ready), sorted(ready))
        resolved |= ready
    for g, r in gates.items():
        descendants, todo = set(), [g]
        while todo:
            current = todo.pop()
            for x, entry in gates.items():
                if current in entry['prerequisites'] and x not in descendants:
                    descendants.add(x)
                    todo.append(x)
        require('Repair invalidation closure: ' + g, r['dependent_gates_invalidated_on_repair'] == sorted(descendants) and r['rerun_set_on_repair'] == sorted(descendants | {g}))
        require('Independent criterion/evidence defined: ' + g, bool(r['independent_acceptance']) and bool(r['evidence_required']) and r['possible_failure_classes'] == ['A', 'B', 'C'])
    require('Isolation before load; no resource cycle', gates['L']['prerequisites'] == ['B'] and 'L' in gates['C']['prerequisites'] and 'M' not in gates['O']['prerequisites'])
    require('Topological declared bootstrap order', all(graph['runtime_bootstrap_order'].index(p) < graph['runtime_bootstrap_order'].index(g) for g, r in gates.items() for p in r['prerequisites']))
    fail, repair = load(HERE / 'failure_policy.json'), load(HERE / 'repair_policy.json')
    require('Failure classes/actions frozen', list(fail['classes']) == ['A', 'B', 'C'] and fail['classes']['A']['action'] == 'STOP_CONFIGURATION_TRACK' and fail['classes']['C']['action'] == 'PENDING' and fail['executed_failures'] == [])
    require('Finite repair bounds/records/invariants', repair['bounds']['implemented_attempts_per_root_cause'] == 2 and repair['bounds']['implemented_attempts_per_track_total'] == 6 and repair['invariants'] == fail['invariants'] and len(repair['required_repair_fields']) >= 13 and repair['repair_log'] == [] and repair['generation_retries'] == 0)

    fixture_manifest = load(HERE / 'fixture_manifest.json')
    fixtures = fixture_manifest['fixtures']
    require('Fixture counts/IDs unique/frozen', len(fixtures) == fixture_manifest['expected_count'] == 65 and len({r['id'] for r in fixtures}) == 65 and fixture_manifest['frozen_pre_outcome'])
    for r in fixtures:
        actual = row(REPO / r['path'], REPO)
        require('Frozen fixture hash: ' + r['id'], actual == {k: r[k] for k in ['path', 'bytes', 'sha256']} and bool(r['purpose']) and bool(r['expected_invariant']) and set(r['gates']) <= gates.keys() and r['protected_content'] is False)
    goldens = literal_assignments(REPO / 'harness/tests/test_context_policy.py')
    for key in ['P_GOLDEN', 'K_GOLDEN', 'H_GOLDEN', 'REF_GOLDEN']:
        require('Independent literal golden exact: ' + key, (HERE / f'fixtures/goldens/{key}.utf8').read_bytes() == goldens[key])
    vocab = load(REPO / 'experiments/model_preflight/qwen3_coder_30b_a3b/upstream/tokenizer.json')['model']['vocab']
    require('Operational recipe token0 ordinary exclamation mark', vocab['!'] == 0)
    qwen = REPO / 'experiments/model_preflight/qwen3_coder_30b_a3b'
    capacity_rows = load(qwen / 'capacity_checks.json')
    native_rows = capacity_rows + load(qwen / 'template_checks.json')
    require('Historical45 boundary plus6 framing goldens complete', len(capacity_rows) == 45 and len(native_rows) == 51)
    for r in native_rows:
        native = load(qwen / 'synthetic' / (r['name'] + '.json'))
        rendered = native['rendered'].encode('utf-8')
        token_hash = sha(json.dumps(native['token_ids'], ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode())
        require('Historical native golden internal byte/token integrity: ' + r['name'],
            len(rendered) == r['rendered_bytes'] and sha(rendered) == r['render_sha256'] and
            len(native['token_ids']) == r['input_tokens'] and token_hash == r['token_ids_sha256'])
        if 'generation_reserve' in r:
            require('Historical full-reserve capacity arithmetic: ' + r['name'], r['generation_reserve'] == 2048 and
                r['total_reserved_tokens'] == r['input_tokens'] + 2048 <= 32768 and
                all(r[k] <= limit for k, limit in [('p_bytes', 4096), ('k_bytes', 12288), ('h_bytes', 4096)] if k in r))
            if r['name'].startswith('capacity_'):
                require('Boundary metadata has all P/K/H byte counts: ' + r['name'], all(k in r for k in ['p_bytes', 'k_bytes', 'h_bytes']))
            if r['condition'] == 'BC' and r['h_bytes']:
                require('BC literal lane ownership arithmetic: ' + r['name'], r['lane_bytes'] == [['EPISODIC', r['h_bytes'] // 2], ['CONFIRMED_RULE', r['h_bytes'] - r['h_bytes'] // 2]])
    for label in load(HERE / 'fixtures/teacher_forced_labels.json')['labels'].values():
        data = bytes.fromhex(label['utf8_hex'])
        require('Hand-authored teacher label byte/hash integrity', len(data) == label['bytes'] and sha(data) == label['sha256'])
    rr = load(HERE / 'repeatability_policy.json')
    require('Repeat counts24 frozen before outcomes', rr['same_process_repetitions'] == 3 and rr['total_fresh_processes'] == 2 and rr['second_process_repetitions_per_fixture'] == 3 and rr['total_requests'] == 24 and len(rr['fixture_order']) == 4)
    require('Repeat fixture IDs valid', set(rr['fixture_order']) <= {r['id'] for r in fixtures})
    adapt = load(HERE / 'adaptation_lifecycle_plan.json')
    expected_targets = [f'model.layers.{i}.self_attn.{projection}' for i in range(48) for projection in ['q_proj', 'k_proj', 'v_proj', 'o_proj']]
    require('Exact conservative192/384/rank16 target census', adapt['targets'] == expected_targets and adapt['target_count'] == 192 and adapt['adapter_tensor_count'] == 384 and adapt['rank'] == 16)
    require('Adapter parameter arithmetic/state floor', adapt['adapter_parameters'] == 48 * 16 * (6144 + 2560 + 2560 + 6144) == 13369344 and adapt['optimizer']['parameter_gradient_two_moment_floor_bytes'] == 213909504)
    require('Original-only lifecycle/route frozen', adapt['selected_serving_route'] == 'REQUIRED_BF16_MERGE_EXPORT' and not adapt['direct_adapter_serving_selected'] and not adapt['second_cycle']['prior_adapter_parent_allowed'] and not adapt['second_cycle']['merged_derivative_parent_allowed'] and not adapt['optimizer']['optimizer_resume'])
    hw = load(HERE / 'hardware_requirements.json')
    require('KV/storage planning arithmetic valid', hw['KV_at32768_bytes'] == 2 * 48 * 4 * 128 * 2 * 32768 and sum(hw['storage_plan_bytes'].values()) < hw['free_storage_required_before_acquisition_bytes'] == 250000000000)
    require('Hardware estimates/provider choice honest', hw['status'] == 'PLANNING_ESTIMATES_NOT_MEASURED' and hw['target_inventory'] is None and not hw['provider_selected'] and not hw['GPU_rented'])
    checklist = load(HERE / 'pre_download_checklist.json')
    require('No-go reflects all three incomplete preparation blockers', checklist['verdict'] == 'NOT READY — RUNTIME_BUILD, TARGET_CAPACITY, RUNNER_ATTESTATION' and {r['id'] for r in checklist['items'] if r['status'] != 'PASS'} == {'STORAGE', 'RUNTIME_BUILD', 'RUNNER_ATTESTATION'} and not checklist['acquisition_authorized_by_this_step'] and not checklist['execution_authorized_by_this_step'])

    schema = load(HERE / 'run_manifest_schema.json')
    jsonschema.Draft202012Validator.check_schema(schema)
    require('External run schema valid JSONSchema2020-12', schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema')
    require('All required external receipt fields structurally mandatory', set(schema['required']) == set(schema['properties']) and len(schema['required']) >= 45)
    require('Schema preserves identity bootstrap before isolation', schema['allOf'][1]['if']['properties']['gate_id'] == {'not': {'enum': ['A', 'B']}})
    # Pure hypothetical schema sample: no generated outputs, no executed manifest written.
    partial = {k: None for k in schema['required']}
    partial.update(schema_version='qwen30-external-run-v1', run_id='qwen30-schema-only-not-an-execution',
        timestamp='2026-10-04T00:00:00Z', run_kind='identity', checkpoint_repo=EXPECTED_REPO,
        checkpoint_SHA=EXPECTED_REV, frozen_control_values=literal, isolation_result='NOT_RUN',
        gate_id='B', gate_result='PENDING', failure_classification='C', failure_id='schema-test-only',
        prerequisite_run_ids=[], provenance_artifact_hashes=[{'path': 'runtime_lock.json', 'bytes': (HERE / 'runtime_lock.json').stat().st_size, 'sha256': sha((HERE / 'runtime_lock.json').read_bytes())}],
        invocation_count=0, retry_count=0, parent_original_SHA=EXPECTED_REV, notes=['Hypothetical static schema validation only; not an executable receipt'])
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    require('Schema accepts explicit incomplete hypothetical receipt', not list(validator.iter_errors(partial)))
    rejected_input = copy.deepcopy(partial)
    rejected_input.update(run_kind='load', gate_id='C', exact_prompt_token_count=30721)
    require('Schema retains overlength original count in incomplete rejection receipt', not list(validator.iter_errors(rejected_input)))
    for name, changes in [('incomplete_PASS', {'gate_result': 'PASS', 'failure_classification': None, 'failure_id': None}),
        ('generation_missing_stream', {'run_kind': 'generation', 'gate_result': 'PASS', 'failure_classification': None, 'failure_id': None}),
        ('H_native_stop_is_not_LENGTH', {'run_kind': 'generation', 'gate_id': 'H', 'gate_result': 'PASS', 'finish_reason': 'STOP', 'generated_token_count': 2048}),
        ('wrong_checkpoint', {'checkpoint_SHA': '0' * 40}), ('retry_forbidden', {'retry_count': 1})]:
        sample = copy.deepcopy(partial)
        sample.update(changes)
        require('Schema rejects hypothetical invalid receipt: ' + name, bool(list(validator.iter_errors(sample))))
    require('Semantic cross-field/external checks explicitly separate', len(load(HERE / 'semantic_receipt_rules.json')['enforcement_before_accepting_any_future_run']) >= 12)

    owned_scripts = ['build_governance.py', 'build_details.py', 'validate_governance.py', 'collect_runtime_metadata.py']
    forbidden_imports = {'torch', 'transformers', 'peft', 'vllm', 'harness', 'numpy', 'pytest', 'tokenizers', 'jinja2'}
    for name in owned_scripts:
        tree = ast.parse((HERE / name).read_text(encoding='utf-8'))
        imported = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                imported |= {a.name.split('.')[0] for a in n.names}
            if isinstance(n, ast.ImportFrom):
                imported.add((n.module or '').split('.')[0])
        require('No model/harness/framework imports in preparation script: ' + name, not imported & forbidden_imports)
        require('No dynamic upstream code execution in preparation script: ' + name, not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {'exec', 'eval', '__import__'} for n in ast.walk(tree)))
    report = (HERE / 'REPORT.md').read_text(encoding='utf-8')
    require('Report has22 requested sections', [int(n) for n in re.findall(r'^## (\d+)\.', report, re.M)] == list(range(1, 23)))
    require('Report final repo/SHA and NO activity fields', EXPECTED_REV in report and all(s in report for s in ['Full weights downloaded: NO', 'Model instantiated: NO', 'Inference occurred: NO', 'GPU used: NO', 'Protected candidates accessed: NO', 'Protocol changed: NO', 'Commit made: NO', EXPECTED_HEAD]))
    require('No unplanned own-tree symlinks', not any(p.is_symlink() for p in HERE.rglob('*')))
    return checks, {'HEAD': head, 'worktree_status': status, 'runtime_lock_status': runtime['status'],
        'pre_download_verdict': checklist['verdict'], 'preserved_prior_files': 1231,
        'fixture_count': len(fixtures), 'public_metadata_responses': len(sm['public_runtime_metadata']),
        'all_A_S_status': 'NOT_RUN', 'execution_manifests_emitted': 0,
        'full_weights_downloaded': False, 'packages_or_layers_downloaded': False,
        'model_instantiated': False, 'adapter_instantiated': False, 'inference': False,
        'generated_model_completions': False, 'GPU_used': False, 'GPU_rented': False,
        'training': False, 'protected_candidates_accessed': False, 'protected_tasks_accessed': False,
        'benchmark_outcomes_accessed': False, 'private_scorers_accessed': False,
        'A_B_M_C_BC_experiments': False, 'Study1_2_3': False, 'protocol_changed': False,
        'product_repository_modified': False, 'commit_made': False,
        'activity_attestation_basis': 'This task tool/action trace, confined output inventory, no framework/harness imports, explicit preservation hashes and Git checks; not a claim about other processes on the host',
        'static_validation_python': sys.version, 'static_validation_jsonschema': importlib.metadata.version('jsonschema'),
        'static_validation_environment_is_not_target_runtime': True}


def main():
    assert sys.argv[1:] in [['--seal'], ['--verify']]
    checks, facts = validate()
    if sys.argv[1] == '--seal':
        # Stable seal timestamp enables a later read-only verification; no circular hashes.
        prior = load(HERE / 'validation.json') if (HERE / 'validation.json').exists() else {}
        timestamp = prior.get('sealed_at_utc', datetime.now(timezone.utc).isoformat())
        save('validation.json', {'result': 'PASS', 'validation_scope': 'STATIC_DESIGN_SOURCE_HASH_AND_PRESERVATION_ONLY_NOT_A_S_EXECUTION',
            'sealed_at_utc': timestamp, 'facts': facts, 'check_count': len(checks), 'checks': checks,
            'artifact_manifest_rule': 'Manifest seals this validation file and all other files; excludes itself. Verify manifest afterward without rewriting this file.'})
        files = [row(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name != 'artifact_manifest.json']
        save('artifact_manifest.json', {'scope': 'Entire dedicated Qwen30 governance tree', 'excluded_self': 'artifact_manifest.json', 'files': files})
    manifest = load(HERE / 'artifact_manifest.json')
    actual_paths = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p.name != 'artifact_manifest.json'}
    assert actual_paths == {r['path'] for r in manifest['files']}
    for r in manifest['files']:
        assert row(HERE / r['path']) == r, r['path']
    sealed = load(HERE / 'validation.json')
    assert sealed['result'] == 'PASS' and sealed['facts'] == facts
    print(json.dumps({'result': 'PASS', 'checks': len(checks), 'preserved_prior_files': 1231,
        'fixture_count': facts['fixture_count'], 'artifact_files': len(manifest['files']),
        'artifact_manifest_sha256': sha((HERE / 'artifact_manifest.json').read_bytes()),
        'verdict': facts['pre_download_verdict'], 'HEAD': facts['HEAD'], 'status': facts['worktree_status'],
        'execution': False}, indent=2))


if __name__ == '__main__':
    main()
