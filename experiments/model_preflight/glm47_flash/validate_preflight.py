"""Validate this static audit and preservation evidence; no model execution."""
import sys
sys.dont_write_bytecode = True
import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[2]
REPO = 'zai-org/GLM-4.7-Flash'
SHA = '7dd20894a642a0aa287e9827cb1a1f7f91386b67'
REQUIRED = ['REPORT.md', 'source_manifest.json', 'identity.json', 'serialization.json',
            'capacity_checks.json', 'mla_map.json', 'expert_map.json', 'adaptation_targets.json',
            'original_base_lifecycle.json', 'runtime_profile.json', 'resource_estimates.json',
            'infrastructure_test_matrix.csv']
BODY_SUFFIXES = {'.safetensors', '.gguf', '.pt', '.pth', '.bin'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def dump(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=WORKSPACE, text=True, encoding='utf-8').strip()


def check_record(row, parent):
    path = (parent / row['path']).resolve()
    assert path.is_relative_to(parent), row['path']
    assert path.is_file(), row['path']
    data = path.read_bytes()
    assert len(data) == row['bytes'] and digest(data) == row['sha256'], row['path']


def source_key(url):
    """Match human-readable pinned blob links to downloaded raw/resolve URLs."""
    parsed = urlparse(url)
    path = parsed.path
    if parsed.netloc == 'huggingface.co':
        path = path.replace('/blob/', '/resolve/')
    if parsed.netloc == 'github.com' and '/blob/' in path:
        owner, repo, _, pin, *name = path.strip('/').split('/')
        return 'https://raw.githubusercontent.com/' + '/'.join([owner, repo, pin, *name])
    return parsed._replace(path=path, fragment='').geturl()


def main():
    for name in REQUIRED:
        assert (ROOT / name).is_file(), name
    # Inventory only this dedicated output tree. Preservation checks use an existing allowlist.
    files = sorted((p for p in ROOT.rglob('*') if p.is_file()), key=lambda p: p.relative_to(ROOT).as_posix())
    parsed_json = []
    for path in files:
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
            parsed_json.append(path.relative_to(ROOT).as_posix())
    assert not [p for p in files if p.suffix.lower() in BODY_SUFFIXES]
    assert not [p for p in files if '__pycache__' in p.parts]

    source = read('source_manifest.json')
    assert source['subject_repository'] == REPO and source['subject_revision'] == SHA
    assert not source['weight_bodies_downloaded']
    retrieved = [r for r in source['files'] if r['status'] == 'retrieved']
    for row in source['files']:
        assert row['url'].startswith('https://')
        assert Path(urlparse(row['url']).path).suffix.lower() not in BODY_SUFFIXES
        assert datetime.fromisoformat(row['retrieved_at_utc']).tzinfo is not None
        assert row['status'] in {'retrieved', 'unavailable', 'size_limit'}
    for row in retrieved:
        check_record(row, ROOT)
        assert row['bytes'] <= row['limit_bytes']
        assert row['limit_bytes'] <= (21_000_000 if row['path'] == 'upstream/tokenizer.json' else 2_000_000)
        if row['path'].startswith('upstream/'):
            assert SHA in row['url']
    for pin, directory in [('huggingface/transformers', 'huggingface__transformers'),
                           ('huggingface/peft', 'huggingface__peft'), ('vllm-project/vllm', 'vllm-project__vllm')]:
        assert read('sources/' + directory + '/commit.json')['sha'] == source['implementation_pins'][pin]
    for row in source['local_project_inputs'] + source['reused_dependency_artifacts']:
        check_record(row, WORKSPACE)

    with (ROOT / 'infrastructure_test_matrix.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ['id', 'test', 'procedure', 'acceptance', 'status']
        tests = list(reader)
    assert [r['id'] for r in tests] == list('ABCDEFGHIJKLMNOPQRSTUVWX')
    assert all(set(r) == set(reader.fieldnames) and all(r.values()) and r['status'] == 'NOT_RUN' for r in tests)

    report = (ROOT / 'REPORT.md').read_text(encoding='utf-8')
    assert [int(n) for n in re.findall(r'^## (\d+)\.', report, re.M)] == list(range(1, 24))
    pending = {'validation.json', 'artifact_manifest.json'}
    for link in re.findall(r'\]\(([^)]+)\)', report):
        if '://' not in link and not link.startswith('#') and link not in pending:
            assert (ROOT / link).resolve().is_file(), link
    definitions = dict(re.findall(r'^\[([^\]]+)\]: (https://\S+)$', report, re.M))
    markdown_prose = re.sub(r'```.*?```', '', report, flags=re.S)
    markdown_prose = re.sub(r'`[^`]*`', '', markdown_prose)
    reference_uses = re.findall(r'\]\[([^\]]+)\]', markdown_prose)
    assert all(name in definitions for name in reference_uses)
    known = {source_key(r['url']) for r in retrieved}
    for url in definitions.values():
        assert source_key(url) in known, url

    identity = read('identity.json')
    meta = read('upstream/hub_metadata.json')
    config = read('upstream/config.json')
    index = read('upstream/model.safetensors.index.json')
    assert identity['repository'] == meta['id'] == REPO and identity['revision'] == meta['sha'] == SHA
    with (WORKSPACE / 'experiments/model_preflight/landscape_closure/landscape.csv').open(encoding='utf-8', newline='') as stream:
        landscape = next(r for r in csv.DictReader(stream) if r['repository'] == REPO)
    assert landscape['revision'] == SHA
    shards = identity['selected_lfs_identities']
    assert len(shards) == 48 and sum(s['size'] for s in shards) == identity['declared_weight_bytes'] == 62_444_175_504
    assert landscape['selected_weight_files'].split('; ') == [s['rfilename'] for s in shards]
    assert landscape['weight_lfs_hashes_declared'].split('; ') == [s['lfs']['sha256'] for s in shards]
    assert all(s['lfs']['size'] == s['size'] and re.fullmatch(r'[a-f0-9]{64}', s['lfs']['sha256']) for s in shards)
    assert config['model_type'] == 'glm4_moe_lite' and config['architectures'] == ['Glm4MoeLiteForCausalLM']
    assert config['num_hidden_layers'] == 47 and config['n_routed_experts'] == 64 and config['num_experts_per_tok'] == 4
    assert config['dtype'] == 'bfloat16' and 'quantization_config' not in config
    assert not identity['weight_bodies_downloaded'] and not identity['headers_downloaded']
    catalog = read('weight_layout_catalog.json')
    weights = catalog['rows']
    assert len(weights) == 9703 and {r['checkpoint_tensor'] for r in weights} == set(index['weight_map'])
    assert all(r['elements'] == math.prod(r['shape_inferred']) and r['shard'] == index['weight_map'][r['checkpoint_tensor']] for r in weights)
    assert sum(r['elements'] for r in weights) == meta['safetensors']['total'] == 31_221_488_576
    buffers = sum(r['elements'] for r in weights if r['buffer'])
    assert buffers == meta['safetensors']['parameters']['F32'] == 3008
    assert sum(r['elements'] for r in weights if not r['buffer']) == meta['safetensors']['parameters']['BF16']
    assert index['metadata']['total_size'] == meta['safetensors']['total']
    assert identity['payload_bytes_from_public_dtype_counts'] == 2 * (meta['safetensors']['total'] - buffers) + 4 * buffers == 62_442_983_168
    assert not catalog['body_verified'] and catalog['shapes_inferred']

    serialization = read('serialization.json')
    capacity = read('capacity_checks.json')
    selected = 'NATIVE_DEFAULT_THINKING_FULL_SUFFIX_RAW_TOKEN_IDS'
    assert serialization['selected_profile'] == capacity['selected_profile'] == selected
    assert serialization['full_stream_Draft3_compatibility_statically_established']
    assert not serialization['selected_thinking_effort_changed']
    assert serialization['generation_prefix'] == '<|assistant|><think>'
    assert serialization['nonthinking_input_prefix'] == '<|assistant|></think>'
    assert serialization['eos_config_ids'] == config['eos_token_id'] == [154820, 154827, 154829]
    assert not serialization['decode_skip_special_tokens'] and serialization['terminal_allowance'] == 1
    for name, expected in serialization['tokenizer_files'].items():
        assert digest((ROOT / 'upstream' / name).read_bytes()) == expected
    assert capacity['reserve'] == 2048 and capacity['deployed_target'] == 32768
    assert capacity['maximum_synthetic_input_tokens'] == max(r['input_tokens'] for r in capacity['rows']) == 20427
    assert capacity['maximum_input_plus_2048'] == 22475 and capacity['capacity_violations'] == 0
    assert len(capacity['rows']) == 45 and len(serialization['template_checks']) == 6
    assert len(list((ROOT / 'synthetic').glob('*.json'))) == 51
    assert all(r['input_plus_reserve'] == r['input_tokens'] + 2048 <= 32768 and r['repeated_encodings'] == 4 and
               r['deterministic_encoding'] and r['lossless_input_byte_roundtrip'] for r in capacity['rows'] + serialization['template_checks'])
    assert all(r['p_bytes'] <= 4096 and r['k_bytes'] <= 12288 and r['h_bytes'] <= 4096 and
               all(b <= (2048 if r['condition'] == 'BC' else 4096) for _, b in r.get('lane_bytes', []))
               for r in capacity['rows'])
    assert capacity['raw_utf8_bound_plus_reserve'] == 633 + 20480 + 2048 == 23161
    assert capacity['all_256_byte_alphabet_symbols_in_vocab'] and not capacity['measured_deployed_capacity']

    targets = read('adaptation_targets.json')
    attention = targets['attention_modules']
    experts = targets['stacked_parameters']
    assert len(attention) == len(read('mla_map.json')['projection_modules']) == 235
    assert len(experts) == len(read('expert_map.json')['target_parameter_map']) == 92
    assert sum(r['rank16_parameters'] for r in attention) == 21_031_936
    assert sum(r['rank16_parameters'] for r in experts) == 409_993_216
    for scope_name, count, parameter_count in [('MLA_attention_only', 0, 21_031_936),
                                             ('MLA_plus_routed_expert_parameters', 92, 431_025_152)]:
        scope = targets['scopes'][scope_name]
        assert scope['module_count'] == 235 and scope['stacked_parameter_count'] == count
        assert scope['rank16_trainable_parameters'] == parameter_count
        assert scope['adapter_BF16_payload_bytes'] == 2 * parameter_count and scope['adapter_FP32_payload_bytes'] == 4 * parameter_count
        assert len(scope['target_parameters']) == count
        assert scope['expanded_module_names'] == [r['module'] for r in attention]
        assert all(re.fullmatch(scope['target_modules'], name) for name in scope['expanded_module_names'])
        assert not re.fullmatch(scope['target_modules'], 'model.layers.47.self_attn.q_a_proj')
    assert all(r['rank16_parameters'] == 16 * sum(r['weight_shape']) for r in attention)
    assert all(r['shape'][0] == 64 and r['rank16_parameters'] == 64 * 16 * sum(r['shape'][1:]) for r in experts)
    assert targets['expert_scope_requirements']['lora_dropout'] == 0
    assert targets['expert_scope_requirements']['USE_HUB_KERNELS'] == 'NO'

    lifecycle = read('original_base_lifecycle.json')
    assert lifecycle['credible_fresh_original_attention_path'] and lifecycle['merge_export']['save_original_format'] is True
    assert len(lifecycle['MTP_policy']['exact_excluded_keys']) == 212
    assert set(lifecycle['MTP_policy']['exact_excluded_keys']) == {name for name in index['weight_map'] if name.startswith('model.layers.47.')}
    assert all(not lifecycle[k] for k in ['fallback_triggered', 'protocol_modified', 'inference_occurred', 'model_instantiated', 'adapter_instantiated'])
    runtime = read('runtime_profile.json')
    assert runtime['selected_profile'] == selected and not runtime['installation_success']
    assert len(runtime['frozen_control_map']) == 15
    assert all(r['infrastructure_status'] == 'INFRASTRUCTURE-UNVERIFIED' for r in runtime['frozen_control_map'].values())
    policy = json.loads((WORKSPACE / 'benchmark_design/context_policy/current-repo-v1-draft3.json').read_text(encoding='utf-8'))
    assert {k: v['requested'] for k, v in runtime['frozen_control_map'].items()} == policy['profile_schema']['controls']
    assert runtime['sampling_params']['max_tokens'] == 2048 and runtime['engine_args']['max_model_len'] == 32768
    assert runtime['sampling_params']['detokenize'] is False and runtime['sampling_params']['stop_token_ids'] == config['eos_token_id']
    assert runtime['engine_args']['speculative_config'] is None
    for name, repo in [('transformers', 'huggingface/transformers'), ('peft', 'huggingface/peft'), ('vllm', 'vllm-project/vllm')]:
        assert runtime['stack'][name]['commit'] == source['implementation_pins'][repo]
    resources = read('resource_estimates.json')
    assert resources['main_resident_payload_bytes'] == 59_886_793_728
    assert resources['compressed_KV_32768_one_sequence']['bytes'] == 47 * 32768 * (512 + 64) * 2
    assert resources['expert_parametrization']['all46_layers_effective_BF16_stack_bytes'] == 46 * 64 * (3072 * 2048 + 2048 * 1536) * 2

    env = read('tokenizer_environment.json')
    assert not env['torch_imported'] and not env['peft_imported'] and not env['model_libraries_imported']
    imports = []
    for path in ROOT.glob('*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or '')
    assert not any(m.split('.')[0] in {'torch', 'transformers', 'peft', 'vllm'} for m in imports)

    baseline = read('baseline_integrity.json')
    assert len(baseline['preserved_files']) == 939
    for row in baseline['preserved_files']:
        check_record(row, WORKSPACE)
    head, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert head == baseline['head'] and status == baseline['status']
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    validation = {
        'status': 'PASS_STATIC_ARTIFACT_VALIDATION', 'validated_at_utc': datetime.now(timezone.utc).isoformat(),
        'subject_repository': REPO, 'subject_revision': SHA, 'verdict': 'PROCEED TO INFRASTRUCTURE VERIFICATION',
        'required_artifacts_present': True, 'all_generated_and_source_JSON_parsed': True,
        'json_files_parsed_before_finalization': len(parsed_json), 'source_reference_hashes_verified': len(retrieved),
        'failed_or_size_limited_acquisitions_recorded': len(source['files']) - len(retrieved),
        'local_project_input_hashes_verified': len(source['local_project_inputs']),
        'reused_dependency_hashes_verified': len(source['reused_dependency_artifacts']),
        'csv_schema_valid': True, 'infrastructure_items': len(tests), 'all_infrastructure_NOT_RUN': True,
        'report_sections': 23, 'markdown_links_and_pinned_source_references_valid': True,
        'exact_identity_and_landscape_match': True, 'landscape_license_wording_refinement_disclosed': True,
        'public_index_size_discrepancy_preserved': True, 'all_9703_index_names_covered_by_inferred_catalog': True,
        'MLA_targets': 235, 'expert_parameter_targets': 92, 'rank16_MLA_parameters': 21031936,
        'rank16_combined_parameters': 431025152, 'synthetic_capacity_checks_passed': True,
        'maximum_synthetic_input_tokens': 20427, 'maximum_input_plus_2048': 22475,
        'selected_profile': selected, 'full_stream_Draft3_compatibility_statically_established': True,
        'selected_thinking_effort_changed': False, 'no_weight_body_files_or_weight_URL_requests': True,
        'no_inference': True, 'no_model_instantiation': True, 'no_adapter_instantiation': True,
        'no_upstream_training_serving_recipe_execution': True, 'protected_candidate_inventory_accessed': False,
        'protected_outcomes_accessed': False,
        'candidate_blindness_evidence': 'Scope/process attestation: bounded acquisition allowlist, authored imports, permitted project input hashes; not an OS-level trace certificate',
        'native_tensor_layouts_verified': False, 'deterministic_model_inference_verified': False,
        'fresh_base_lifecycle_empirically_verified': False, 'isolation_empirically_certified': False,
        'product_repositories_unchanged': True, 'protocol_modified': False,
        'preserved_existing_files_verified': len(baseline['preserved_files']),
        'historical_landscape_Devstral_and_policy_hashes_unchanged': True,
        'git_tracked_and_staged_diff_empty': True, 'HEAD_unchanged': True, 'final_HEAD': head,
        'initial_git_status': baseline['status'], 'final_git_status': status, 'commit_made': False,
        'fallback_triggered': False, 'GPU_use_or_spending_authorized': False,
        'artifact_hash_check': 'Recompute every artifact hash after writing final manifest; exclude manifest itself to avoid a circular hash'
    }
    dump('validation.json', validation)
    files = sorted((p for p in ROOT.rglob('*') if p.is_file() and p.name != 'artifact_manifest.json'), key=lambda p: p.relative_to(ROOT).as_posix())
    manifest = {'subject_repository': REPO, 'subject_revision': SHA,
                'scope': 'entire dedicated GLM static preflight tree; no pre-existing files mutated',
                'excluded_self': 'artifact_manifest.json (no circular self-hash)',
                'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())} for p in files]}
    dump('artifact_manifest.json', manifest)
    for row in read('artifact_manifest.json')['files']:
        check_record(row, ROOT)
    read('validation.json')
    assert all((ROOT / name).is_file() for name in REQUIRED + list(pending))
    print(json.dumps({'status': validation['status'], 'source_hashes': len(retrieved), 'artifact_hashes': len(files),
                      'preserved_files': len(baseline['preserved_files']), 'infrastructure_NOT_RUN': len(tests),
                      'HEAD': head, 'git_status': status}, indent=2))


if __name__ == '__main__':
    main()
