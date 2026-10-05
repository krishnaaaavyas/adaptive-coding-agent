"""Validate static artifacts and the permitted preservation allowlist; no model execution."""
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
REPO = 'nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16'
SHA = 'a9904d24bcc1d289a1950fa9d2b978c47cf903b9'
SELECTED = 'NATIVE_DEFAULT_THINKING_FULL_SUFFIX_RAW_TOKEN_IDS'
REQUIRED = ['REPORT.md', 'source_manifest.json', 'identity.json', 'serialization.json',
            'capacity_checks.json', 'architecture_map.json', 'adaptation_targets.json',
            'training_serving_map.json', 'original_base_lifecycle.json', 'runtime_profile.json',
            'resource_estimates.json', 'infrastructure_test_matrix.csv']
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
    data = path.read_bytes()
    assert len(data) == row['bytes'] and digest(data) == row['sha256'], row['path']


def source_key(url):
    parsed = urlparse(url)
    path = parsed.path
    if parsed.netloc == 'huggingface.co':
        path = path.replace('/blob/', '/resolve/')
    if parsed.netloc == 'github.com' and '/blob/' in path:
        owner, repo, _, pin, *name = path.strip('/').split('/')
        return 'https://raw.githubusercontent.com/' + '/'.join([owner, repo, pin, *name])
    return parsed._replace(path=path, fragment='').geturl()


def main():
    assert all((ROOT / n).is_file() for n in REQUIRED)
    # Only the newly created output tree is enumerated. Prior preservation uses an allowlist.
    files = sorted(p for p in ROOT.rglob('*') if p.is_file())
    parsed_json = []
    for path in files:
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
            parsed_json.append(path.relative_to(ROOT).as_posix())
    assert not any(p.suffix.lower() in BODY_SUFFIXES or '__pycache__' in p.parts for p in files)
    source = read('source_manifest.json')
    assert source['subject_repository'] == REPO and source['subject_revision'] == SHA
    assert not source['weight_bodies_downloaded']
    retrieved = [r for r in source['files'] if r['status'] == 'retrieved']
    assert len({r['url'] for r in source['files']}) == len(source['files'])
    known = {source_key(r['url']) for r in retrieved}
    for row in source['files']:
        assert row['url'].startswith('https://')
        assert Path(urlparse(row['url']).path).suffix.lower() not in BODY_SUFFIXES
        assert datetime.fromisoformat(row['retrieved_at_utc']).tzinfo is not None
        assert row['status'] in {'retrieved', 'unavailable', 'size_limit'}
        if row['status'] == 'retrieved':
            check_record(row, ROOT)
            assert row['bytes'] <= row['limit_bytes'] <= (18_000_000 if row['path'] == 'upstream/tokenizer.json' else 2_000_000)
            if row['path'].startswith('upstream/'):
                assert SHA in row['url']
            elif row['url'].startswith('https://raw.githubusercontent.com/'):
                assert any(pin in row['url'] for pin in source['implementation_pins'].values())
    for repo, pin in source['implementation_pins'].items():
        assert read('sources/' + repo.replace('/', '__') + '/commit.json')['sha'] == pin
    assert len(source['local_project_inputs']) == 16
    assert len(source['reused_dependency_artifacts']) == 107
    for row in source['local_project_inputs'] + source['reused_dependency_artifacts']:
        check_record(row, WORKSPACE)

    with (ROOT / 'infrastructure_test_matrix.csv').open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
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
    prose = re.sub(r'```.*?```|`[^`]*`', '', report, flags=re.S)
    assert all(name in definitions for name in re.findall(r'\]\[([^\]]+)\]', prose))
    assert all(source_key(url) in known for url in definitions.values())
    # Every source_url field in generated summaries must point to an acquired immutable source.
    def references(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'source_urls':
                    assert all(source_key(url) in known for url in item), item
                else:
                    references(item)
        elif isinstance(value, list):
            for item in value:
                references(item)
    for n in REQUIRED:
        if n.endswith('.json') and n != 'source_manifest.json':
            references(read(n))

    identity, meta, config, index = (read(n) for n in ['identity.json', 'upstream/hub_metadata.json', 'upstream/config.json', 'upstream/model.safetensors.index.json'])
    assert identity['repository'] == meta['id'] == REPO and identity['revision'] == meta['sha'] == SHA
    assert meta['private'] is False and meta['gated'] is False and identity['license'] == 'OpenMDW-1.1'
    with (WORKSPACE / 'experiments/model_preflight/landscape_closure/landscape.csv').open(encoding='utf-8', newline='') as f:
        landscape = next(r for r in csv.DictReader(f) if r['repository'] == REPO)
    assert landscape['revision'] == SHA
    shards = identity['selected_lfs_identities']
    assert len(shards) == 14 and sum(s['size'] for s in shards) == identity['declared_weight_bytes'] == 65_827_374_264
    assert landscape['selected_weight_files'].split('; ') == [s['rfilename'] for s in shards]
    assert landscape['weight_lfs_hashes_declared'].split('; ') == [s['lfs']['sha256'] for s in shards]
    assert all(s['lfs']['size'] == s['size'] and re.fullmatch('[a-f0-9]{64}', s['lfs']['sha256']) for s in shards)
    assert config['model_type'] == 'nemotron_h' and config['architectures'] == ['NemotronHForCausalLM']
    assert config['dtype'] == 'bfloat16' and 'quantization_config' not in config
    assert not identity['weight_bodies_downloaded'] and not identity['headers_downloaded']
    architecture = read('architecture_map.json')
    order = config['layers_block_type']
    assert len(order) == 52 and architecture['layer_order'] == order
    for kind, count in [('mamba', 23), ('attention', 6), ('moe', 23)]:
        assert order.count(kind) == count
        assert architecture['layer_ids'][kind] == identity['layer_ids'][kind] == [i for i, t in enumerate(order) if t == kind]
    assert config['n_routed_experts'] == 128 and config['num_experts_per_tok'] == 6 and config['moe_latent_size'] is None
    assert config['ssm_state_size'] == 128 and config['mamba_num_heads'] == 64 and config['mamba_head_dim'] == 64
    catalog = read('weight_layout_catalog.json')
    weights = catalog['rows']
    assert len(weights) == 6513 and {r['checkpoint_tensor'] for r in weights} == set(index['weight_map'])
    assert all(r['elements'] == math.prod(r['shape_inferred']) and r['shard'] == index['weight_map'][r['checkpoint_tensor']] for r in weights)
    assert sum(r['elements'] for r in weights) == 32_913_266_240
    assert sum(r['elements'] for r in weights if r['buffer']) == meta['safetensors']['parameters']['F32'] == 3072
    assert sum(r['elements'] for r in weights if not r['buffer']) == meta['safetensors']['parameters']['BF16'] == 32_913_263_168
    main = [r for r in weights if not r['checkpoint_tensor'].startswith('mtp.')]
    assert len(main) == catalog['main_raw_entries'] == 6243
    assert len({r['training_tensor'] for r in main}) == catalog['main_stacked_tensor_buffer_entries'] == 401
    assert sum(r['elements'] for r in main) == catalog['main_elements_including_buffers'] == 31_577_940_288
    assert sum(r['elements'] for r in main if r['buffer']) == 2944
    assert sum(r['elements'] for r in main if not r['buffer']) == meta['safetensors']['total'] == index['metadata']['total_parameters'] == 31_577_937_344
    assert catalog['mtp_raw_entries'] == 270 and catalog['mtp_elements_including_buffers'] == 1_335_325_952
    assert identity['payload_bytes_from_public_dtype_counts'] == 65_826_538_624
    assert index['metadata']['total_size'] == 65_842_365_568
    assert index['metadata']['total_size'] - identity['payload_bytes_from_public_dtype_counts'] == 15_826_944
    assert not catalog['body_verified'] and catalog['shapes_inferred']

    serialization, capacity = read('serialization.json'), read('capacity_checks.json')
    assert serialization['selected_profile'] == capacity['selected_profile'] == SELECTED
    assert serialization['full_stream_Draft3_compatibility_statically_established'] and not serialization['selected_thinking_effort_changed']
    assert serialization['generation_prefix'] == '<|im_start|>assistant\n<think>\n'
    assert serialization['generation_prefix_token_ids'] == [10, 1503, 19464, 1010, 12, 1010]
    assert serialization['native_terminal_ids'] == serialization['generation_eos_ids'] == [2, 11]
    assert serialization['root_eos_id'] == config['eos_token_id'] == 2
    assert serialization['tokenizer_pad_id'] == 11 and serialization['config_pad_id'] == 0
    assert serialization['backend_vocabulary_size'] == serialization['model_vocabulary_size'] == 131072
    assert not serialization['decode_skip_special_tokens'] and serialization['terminal_allowance'] == 1
    for n, expected in serialization['tokenizer_files'].items():
        assert digest((ROOT / 'upstream' / n).read_bytes()) == expected
    assert capacity['reserve'] == 2048 and capacity['deployed_target'] == 32768
    assert capacity['maximum_synthetic_input_tokens'] == max(r['input_tokens'] for r in capacity['rows']) == 20465
    assert capacity['maximum_input_plus_2048'] == 22513 and capacity['capacity_violations'] == 0
    assert len(capacity['rows']) == 45 and len(serialization['template_checks']) == 6
    assert len(list((ROOT / 'synthetic').glob('*.json'))) == 51
    assert all(r['input_plus_reserve'] == r['input_tokens'] + 2048 <= 32768 and r['repeated_encodings'] == 4 and r['deterministic_encoding'] and r['lossless_input_byte_roundtrip'] for r in capacity['rows'] + serialization['template_checks'])
    assert all(r['p_bytes'] <= 4096 and r['k_bytes'] <= 12288 and r['h_bytes'] <= 4096 and all(b <= (2048 if r['condition'] == 'BC' else 4096) for _, b in r.get('lane_bytes', [])) for r in capacity['rows'])
    assert capacity['raw_utf8_bound_plus_reserve'] == 671 + 20480 + 2048 == 23199
    assert capacity['all_256_byte_alphabet_symbols_in_vocab'] and not capacity['measured_deployed_capacity']
    for row in capacity['rows'] + serialization['template_checks']:
        fixture = read('synthetic/' + row['name'] + '.json')
        rendered = fixture['rendered'].encode('utf-8')
        token_bytes = json.dumps(fixture['token_ids'], ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('ascii')
        assert len(rendered) == row['rendered_utf8_bytes'] and digest(rendered) == row['rendered_sha256']
        assert len(fixture['token_ids']) == row['input_tokens'] and digest(token_bytes) == row['token_ids_sha256']
        assert all(isinstance(i, int) and 0 <= i < 131072 for i in fixture['token_ids'])

    targets = read('adaptation_targets.json')
    attention, mamba, experts = (targets[k] for k in ['attention_modules', 'mamba_in_modules', 'expert_parameters'])
    assert len(attention) == 24 and len(mamba) == 23 and len(experts) == 46
    assert sum(r['rank16_parameters'] for r in attention) == 1_867_776
    assert sum(r['rank16_parameters'] for r in mamba) == 4_781_056
    assert sum(r['rank16_parameters'] for r in experts) == 428_081_152
    assert all(r['rank16_parameters'] == 16 * sum(r['weight_shape']) for r in attention + mamba)
    assert all(r['training_shape'][0] == 128 and r['rank16_parameters'] == 128 * 16 * sum(r['training_shape'][1:]) for r in experts)
    for name, count, param_count, trainables in [('conservative_attention', 24, 0, 1867776), ('hybrid_attention_mamba_in', 47, 0, 6648832), ('expert_hybrid_plus_routed', 47, 46, 434729984)]:
        scope = targets['scopes'][name]
        assert scope['module_count'] == count and scope['stacked_parameter_count'] == param_count
        assert scope['rank16_trainable_parameters'] == trainables
        assert scope['A_B_tensor_count'] == 2 * (count + param_count)
        assert scope['BF16_adapter_payload_bytes'] == 2 * trainables and scope['FP32_adapter_payload_bytes'] == 4 * trainables
        assert scope['expanded_module_names'] == [r['module'] for r in attention + (mamba if count == 47 else [])]
        assert len(scope['target_parameters']) == param_count
        assert all(re.fullmatch(scope['target_modules'], n) for n in scope['expanded_module_names'])
        assert not any(re.fullmatch(scope['target_modules'], n) for n in ['model.layers.0.mixer.out_proj', 'model.layers.52.mixer.q_proj', 'model.layers.5.mixer.gate_proj'])
    assert targets['scopes']['expert_hybrid_plus_routed']['target_parameters'] == [r['parameter'] for r in experts]
    assert targets['parameter_wrapper_restrictions']['lora_dropout'] == 0
    assert targets['training_restrictions']['USE_HUB_KERNELS'] == 'NO' and targets['training_restrictions']['experts_implementation'] == 'eager'
    assert targets['training_restrictions']['use_cache'] is False and targets['training_restrictions']['use_kernels'] is False
    lifecycle = read('original_base_lifecycle.json')
    assert lifecycle['credible_fresh_original_path'] and lifecycle['merge_export']['save_original_format'] is True
    assert set(lifecycle['MTP_policy']['exact_excluded_keys']) == {k for k in index['weight_map'] if k.startswith('mtp.')}
    assert len(lifecycle['MTP_policy']['exact_excluded_keys']) == 270
    assert all(not lifecycle[k] for k in ['protocol_modified', 'inference_occurred', 'model_instantiated', 'adapter_instantiated'])
    runtime = read('runtime_profile.json')
    assert runtime['selected_profile'] == SELECTED and not runtime['installation_success']
    assert len(runtime['frozen_control_map']) == 15 and all(r['infrastructure_status'] == 'INFRASTRUCTURE-UNVERIFIED' for r in runtime['frozen_control_map'].values())
    policy = json.loads((WORKSPACE / 'benchmark_design/context_policy/current-repo-v1-draft3.json').read_text(encoding='utf-8'))
    assert {k: v['requested'] for k, v in runtime['frozen_control_map'].items()} == policy['profile_schema']['controls']
    assert runtime['sampling_params']['max_tokens'] == 2048 and runtime['engine_args']['max_model_len'] == 32768
    assert runtime['sampling_params']['detokenize'] is False and runtime['sampling_params']['stop_token_ids'] == [2, 11]
    assert runtime['engine_args']['speculative_config'] is None and runtime['engine_args']['enable_prefix_caching'] is False
    assert runtime['engine_args']['mamba_ssm_cache_dtype'] == 'float32' and runtime['engine_args']['enable_mamba_cache_stochastic_rounding'] is False
    for name, repo in [('transformers', 'huggingface/transformers'), ('peft', 'huggingface/peft'), ('vllm', 'vllm-project/vllm')]:
        assert runtime['stack'][name]['commit'] == source['implementation_pins'][repo]
    pyproject = (ROOT / 'sources/vllm-project__vllm/pyproject.toml').read_text(encoding='utf-8')
    assert 'requires-python = ">=3.10,<3.15"' in pyproject and '"torch == 2.13.0"' in pyproject
    resources = read('resource_estimates.json')
    assert resources['main_resident_payload_bytes'] == 63_155_886_464
    assert resources['attention_KV_one_sequence_32768']['bytes'] == 6 * 32768 * 2 * 128 * 2 * 2
    assert resources['Mamba_temporal_one_state_slot']['bytes'] == 23 * 64 * 64 * 128 * 4
    assert resources['expert_effective_weights']['all23_BF16_bytes'] == 23 * 128 * 1856 * 2688 * 2 * 2

    env = read('tokenizer_environment.json')
    assert not env['torch_imported'] and not env['peft_imported'] and not env['model_libraries_imported']
    imports = []
    for path in ROOT.glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or '')
    assert not any(m.split('.')[0] in {'torch', 'transformers', 'peft', 'vllm'} for m in imports)
    baseline = read('baseline_integrity.json')
    assert len(baseline['preserved_files']) == 1069
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
        'local_project_input_hashes_verified': 16, 'reused_dependency_hashes_verified': 107,
        'csv_schema_valid': True, 'infrastructure_items': 24, 'all_infrastructure_NOT_RUN': True,
        'report_sections': 23, 'markdown_links_and_pinned_source_references_valid': True,
        'exact_identity_and_landscape_match': True, 'public_metadata_discrepancies_preserved': True,
        'all_6513_index_names_covered_by_inferred_catalog': True, 'main_stacked_tensor_buffer_entries': 401,
        'conservative_module_targets': 24, 'hybrid_module_targets': 47, 'expert_parameter_targets': 46,
        'rank16_scope_parameters': [1867776, 6648832, 434729984],
        'synthetic_capacity_checks_passed': True, 'maximum_synthetic_input_tokens': 20465,
        'all_51_synthetic_render_and_token_ID_receipt_hashes_verified': True,
        'maximum_input_plus_2048': 22513, 'capacity_violations': 0,
        'selected_profile': SELECTED, 'full_stream_Draft3_compatibility_statically_established': True,
        'selected_thinking_effort_changed': False, 'no_weight_body_files_or_weight_URL_requests': True,
        'no_inference': True, 'no_model_instantiation': True, 'no_adapter_instantiation': True,
        'no_GPU_execution': True, 'no_upstream_training_serving_recipe_execution': True,
        'protected_candidate_inventory_accessed': False, 'protected_outcomes_accessed': False,
        'candidate_blindness_evidence': 'Scope/process attestation: bounded acquisition allowlist, authored imports, permitted input hashes; not an OS-level trace certificate',
        'native_tensor_layouts_verified': False, 'deterministic_model_inference_verified': False,
        'fresh_base_lifecycle_empirically_verified': False, 'isolation_empirically_certified': False,
        'product_repositories_unchanged': True, 'protocol_modified': False,
        'preserved_existing_files_verified': 1069, 'historical_landscape_preflights_and_policy_hashes_unchanged': True,
        'git_tracked_and_staged_diff_empty': True, 'HEAD_unchanged': True, 'final_HEAD': head,
        'initial_git_status': baseline['status'], 'final_git_status': status, 'commit_made': False,
        'roster_frozen': False, 'GPU_use_or_spending_authorized': False,
        'artifact_hash_check': 'Every final file is recomputed after manifest creation; manifest excludes itself to avoid circular hashing'
    }
    dump('validation.json', validation)
    files = sorted((p for p in ROOT.rglob('*') if p.is_file() and p.name != 'artifact_manifest.json'), key=lambda p: p.relative_to(ROOT).as_posix())
    manifest = {'subject_repository': REPO, 'subject_revision': SHA,
                'scope': 'Entire dedicated Nemotron static preflight tree; pre-existing files preserved',
                'excluded_self': 'artifact_manifest.json (no circular self-hash)',
                'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())} for p in files]}
    dump('artifact_manifest.json', manifest)
    for row in read('artifact_manifest.json')['files']:
        check_record(row, ROOT)
    read('validation.json')
    assert all((ROOT / n).is_file() for n in REQUIRED + list(pending))
    print(json.dumps({'status': validation['status'], 'source_hashes': len(retrieved), 'artifact_hashes': len(files),
                      'preserved_files': 1069, 'infrastructure_NOT_RUN': 24, 'HEAD': head, 'git_status': status}, indent=2))


if __name__ == '__main__':
    main()
