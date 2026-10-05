"""Closure over allowlisted completed static evidence; standard library only, no network."""
import sys
sys.dont_write_bytecode = True
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
REQUEST = Path('C:/Users/admin/.codex/attachments/472706c1-17e8-4c15-a42d-a8274b4159d7/Pasted text.txt')
PROCEED = 'PROCEED TO INFRASTRUCTURE VERIFICATION'
DROP = 'DROP — CURRENT PROTOCOL INCOMPATIBLE'
QUEUE = [
    ('qwen3_coder_30b_a3b', 'Qwen3-Coder-30B-A3B-Instruct', 'Qwen/Qwen3-Coder-30B-A3B-Instruct', 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120'),
    ('qwen3_coder_next', 'Qwen3-Coder-Next', 'Qwen/Qwen3-Coder-Next', 'a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb'),
    ('gpt_oss_20b', 'gpt-oss-20b', 'openai/gpt-oss-20b', '6cee5e81ee83917806bbde320786a8fb61efebee'),
    ('devstral_small2_2512', 'Devstral-Small-2-24B-Instruct-2512', 'mistralai/Devstral-Small-2-24B-Instruct-2512', '55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128'),
    ('glm47_flash', 'GLM-4.7-Flash', 'zai-org/GLM-4.7-Flash', '7dd20894a642a0aa287e9827cb1a1f7f91386b67'),
    ('nemotron35_lightning_bf16', 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16', 'nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16', 'a9904d24bcc1d289a1950fa9d2b978c47cf903b9')]
ORDER = ['qwen3_coder_30b_a3b', 'devstral_small2_2512', 'glm47_flash', 'nemotron35_lightning_bf16', 'qwen3_coder_next']
INPUTS = {
    'landscape_closure': ['REPORT.md', 'landscape.csv', 'source_manifest.json', 'artifact_manifest.json', 'validation.json'],
    'cross_model_audit': ['REPORT.md', 'infrastructure_test_matrix.csv', 'source_manifest.json', 'artifact_manifest.json', 'sources/draft2.txt', 'sources/draft3.txt'],
    'qwen3_coder_30b_a3b': ['REPORT.md', 'upstream_manifest.json', 'weight_manifest.json', 'proposed_runtime.json', 'source_manifest.json', 'artifact_manifest.json', 'tokenizer_identity.json', 'upstream/config.json'],
    'qwen3_coder_next': ['REPORT.md', 'upstream_manifest.json', 'weight_manifest.json', 'proposed_runtime.json', 'source_manifest.json', 'artifact_manifest.json', 'tokenizer_identity.json', 'upstream/config.json', 'adapter_parameter_estimates.json'],
    'gpt_oss_20b': ['REPORT.md', 'upstream_manifest.json', 'weight_manifest.json', 'proposed_runtime.json', 'source_manifest.json', 'artifact_manifest.json', 'adapter_parameter_estimates.json'],
    'devstral_small2_2512': ['REPORT.md', 'identity.json', 'serialization.json', 'adaptation_targets.json', 'runtime_profile.json', 'resource_estimates.json', 'original_base_lifecycle.json', 'reconstruction_analysis.json', 'infrastructure_test_matrix.csv', 'source_manifest.json', 'artifact_manifest.json', 'validation.json'],
    'glm47_flash': ['REPORT.md', 'identity.json', 'serialization.json', 'adaptation_targets.json', 'runtime_profile.json', 'resource_estimates.json', 'original_base_lifecycle.json', 'infrastructure_test_matrix.csv', 'source_manifest.json', 'artifact_manifest.json', 'validation.json'],
    'nemotron35_lightning_bf16': ['REPORT.md', 'identity.json', 'serialization.json', 'adaptation_targets.json', 'runtime_profile.json', 'resource_estimates.json', 'original_base_lifecycle.json', 'infrastructure_test_matrix.csv', 'source_manifest.json', 'artifact_manifest.json', 'validation.json', 'baseline_integrity.json']}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(directory, name):
    return json.loads((BASE / directory / name).read_text(encoding='utf-8'))


def dump(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def csv_rows(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(name, fields, rows):
    with (ROOT / name).open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def record(path):
    data = path.read_bytes()
    return {'path': path.relative_to(WORKSPACE).as_posix(), 'bytes': len(data), 'sha256': sha(data)}


def section(text, number):
    return re.search(r'^## ' + str(number) + r'\..*?(?=^## |\Z)', text, re.M | re.S).group()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    landscape = {r['repository']: r for r in csv_rows(BASE / 'landscape_closure/landscape.csv')}
    # Extend the existing permitted integrity allowlist, without enumerating product/candidate trees.
    baseline_path = ROOT / 'baseline_integrity.json'
    if not baseline_path.exists():
        previous = load('nemotron35_lightning_bf16', 'baseline_integrity.json')
        preserved = list(previous['preserved_files'])
        for row in load('nemotron35_lightning_bf16', 'artifact_manifest.json')['files']:
            preserved.append(dict(row, path='experiments/model_preflight/nemotron35_lightning_bf16/' + row['path']))
        preserved.append(record(BASE / 'nemotron35_lightning_bf16/artifact_manifest.json'))
        assert len(preserved) == len({r['path'] for r in preserved}) == 1217
        for row in preserved:
            assert record(WORKSPACE / row['path']) == row, row['path']
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=WORKSPACE, text=True).strip()
        status = subprocess.check_output(['git', 'status', '--short'], cwd=WORKSPACE, text=True).strip()
        assert head == previous['head'] and status == previous['status']
        dump('baseline_integrity.json', {'head': head, 'status': status, 'preserved_files': preserved,
             'scope': 'Prior N1 permitted 1069-file allowlist plus all 148 completed N1 files; no protected directory enumeration'})

    paths = [BASE / directory / name for directory, names in INPUTS.items() for name in names]
    paths += [WORKSPACE / 'benchmark_design/context_policy/current-repo-v1-draft3.json']
    request_bytes = REQUEST.read_bytes()
    (ROOT / 'request_source.txt').write_bytes(request_bytes)
    dump('source_manifest.json', {
        'review_date_local': '2026-10-04', 'timezone': 'Asia/Calcutta', 'frozen_landscape_cutoff': '2026-10-03, Asia/Calcutta',
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Existing local static evidence only; exact hashes, no source/model refresh or network acquisition',
        'files': [record(p) for p in paths],
        'request': {'original_path': str(REQUEST), 'copy': 'request_source.txt', 'bytes': len(request_bytes), 'sha256': sha(request_bytes)},
        'network_requests': 0, 'new_checkpoint_introduced': False,
        'decision_authority': {'completion_contract': 'cross_model_audit/REPORT.md sections 1–7 plus Draft2/Draft3',
                              'stop_redundancy_and_order_rule': 'landscape_closure/REPORT.md sections 12–15 and 22–23',
                              'bounded_queue_completion': 'D1/G1/N1 REPORT section 1 plus identity/lifecycle/validation artifacts',
                              'failure_policy': 'User closure instruction section 10; handoff only, no 1G2A execution'},
        'historical_supersession': 'The earlier gpt-oss uncertainty was explicitly resolved by the later cross-model boundary audit; its path-specific DROP is retained. This is not a new contradiction or reopening.'})

    common = {'deployed_context': 32768, 'generated_token_reserve': 2048,
              'P_bytes': 4096, 'K_bytes': 12288, 'H_bytes': 4096, 'BC_owned_lane_bytes': 2048,
              'entire_emitted_textual_suffix': True, 'verified_final_native_terminal_removal_only': True,
              'CRLF_CR_to_LF_only': True, 'no_reasoning_parser_or_final_projection': True,
              'retries': 0, 'clipping': False, 'context_shifting': False, 'prompt_truncation': False,
              'protocol_change': False, 'model_execution_authorized_by_this_step': False}
    regimes = {
        'qwen3_coder_30b_a3b': 'Ordinary full GQA attention + routed MoE; indexed expert Linear modules at the selected training pin',
        'qwen3_coder_next': 'Hybrid full attention + Gated DeltaNet recurrence + routed/shared MoE; larger resident original and sharded lifecycle',
        'gpt_oss_20b': 'Full/sliding attention with sinks + raw-parameter MoE; native MXFP4/BF16 and Harmony analysis/final channels',
        'devstral_small2_2512': 'Ordinary dense attention/MLP; Tekken/Mistral text-only path from the same native FP8 multimodal original to BF16',
        'glm47_flash': 'MLA projections + stacked routed expert parameters; GLM default-thinking serialization',
        'nemotron35_lightning_bf16': 'Mamba2 selective state-space + occasional GQA + non-gated ReLU2 experts; Nemotron default-thinking ChatML'}
    reasons = {
        'qwen3_coder_30b_a3b': 'Full-attention MoE is the ordinary routed-expert baseline. Next changes recurrent architecture and resource/reset burden; shared Qwen serialization does not establish redundancy.',
        'qwen3_coder_next': 'Gated DeltaNet/full-attention hybrid changes projection/state and distributed original-base lifecycle. Mamba2 is a different recurrent mechanism. It is not removed for sharing Qwen serialization.',
        'devstral_small2_2512': 'Dense attention/MLP, Tekken/Mistral serialization and same-original FP8-to-BF16 reconstruction differ from the sparse BF16 originals. Frozen modality exclusions remain explicit.',
        'glm47_flash': 'MLA low-rank attention projection/latent-KV and stacked-parameter experts plus GLM framing differ from ordinary GQA and both recurrent mechanisms.',
        'nemotron35_lightning_bf16': 'Selective SSM A/dt/conv/state kernels, input projection coverage, non-gated experts and Nemotron framing differ from DeltaNet, MLA and ordinary GQA.'}
    blockers = {
        'qwen3_coder_30b_a3b': 'Exact bodies; 0.11.2 source/build/container lock against archived hashes; effective controls/terminals/raw capture; capacity/isolation/repeats/resources; attention backward/save/reload/serve-or-merge; second original cycle.',
        'qwen3_coder_next': 'Independent exact bodies; 0.16.0 distributed lock/load; full/linear projection gradients and recurrent/KV reset; sharded save/reload/export; notice packaging; controls/capacity/isolation/repeats/resources; second original cycle.',
        'gpt_oss_20b': 'Known static incompatibility: proposed final-only projection deletes substantive analysis. Infrastructure cannot authorize that transformation; no verification track is admitted.',
        'devstral_small2_2512': 'Official FP8 reconstruction scale/layout/key coverage, two pristine roots, BF16 serving attention-scale/YaRN alias parity, original-format export disabled, complete lock/output/control/isolation/lifecycle/resource certificates.',
        'glm47_flash': 'Body/index discrepancy; expert stacking/MTP exclusions; MLA/cache/kernel parity; default-thinking full-suffix retention; environment/control/isolation/repeat/resource/lifecycle certification. Expert and direct adapter serving remain separate.',
        'nemotron35_lightning_bf16': 'Body/index discrepancy; stack/MTP exclusions; fresh SSM/conv/KV state; training-vs-serving dt clamp parity; reference dispatch/gradients, environment/control/isolation/repeats/resources/lifecycle. Fused out_proj and full direct adapter serving unresolved.'}
    statuses, admitted = [], {}
    cross_tests = csv_rows(BASE / 'cross_model_audit/infrastructure_test_matrix.csv')
    for directory, name, repository, revision in QUEUE:
        source_row = landscape[repository]
        assert source_row['revision'] == revision
        identity_name = 'upstream_manifest.json' if directory in ['qwen3_coder_30b_a3b', 'qwen3_coder_next', 'gpt_oss_20b'] else 'identity.json'
        identity = load(directory, identity_name)
        assert identity['repository'] == repository and identity['revision'] == revision
        eligible = directory != 'gpt_oss_20b'
        authority = 'cross_model_audit/REPORT.md' if directory in ['qwen3_coder_30b_a3b', 'qwen3_coder_next', 'gpt_oss_20b'] else directory + '/REPORT.md'
        authoritative_text = (BASE / authority).read_text(encoding='utf-8')
        assert (PROCEED if eligible else DROP) in authoritative_text
        fallback = 'NOT TRIGGERED' if directory in ['devstral_small2_2512', 'glm47_flash'] else 'NOT APPLICABLE'
        fresh = 'SOURCE-SUPPORTED; empirical lifecycle NOT_RUN' if eligible else 'BF16 dequantized LoRA is source-credible; does not rescue incompatible projection'
        statuses.append({'model': name, 'repository': repository, 'revision': revision,
            'static_verdict': PROCEED if eligible else DROP, 'verdict_source': authority,
            'full_stream_Draft3_status': 'STATICALLY COMPATIBLE; raw full suffix' if eligible else 'INCOMPATIBLE proposed final-only extraction',
            'fresh_original_adaptation_status': fresh, 'architecture_adaptation_regime': regimes[directory],
            'remaining_empirical_blockers': blockers[directory], 'fallback_status': fallback,
            'redundancy_classification': 'NON-REDUNDANT' if eligible else 'NOT APPLICABLE; excluded on protocol gate',
            'eligible_for_infrastructure_verification': 'YES' if eligible else 'NO'})
        if not eligible:
            continue
        entry = {'configuration_id': directory, 'model': name, 'repository': repository, 'revision': revision,
                 'static_verdict': PROCEED, 'verdict_source': authority, 'identity_source': directory + '/' + identity_name,
                 'regime': regimes[directory], 'redundancy': 'NON-REDUNDANT', 'non_redundancy_reason': reasons[directory],
                 'frozen_lineage_evidence': {k: source_row[k] for k in ['lineage_group', 'serialization', 'eligibility', 'license_gate', 'product_relevance', 'adaptation_reason', 'decision_reason']},
                 'lineage_rule': ['architecture/base', 'documented checkpoint/training lineage', 'tokenizer/serialization', 'runtime/adaptation'],
                 'remaining_static_execution_blocker': None, 'remaining_empirical_blockers': blockers[directory],
                 'fresh_original_path': fresh, 'fallback_status': fallback, 'common_contract': common,
                 'runtime_is_proposal_not_verified_environment': True}
        if directory.startswith('qwen'):
            runtime = load(directory, 'proposed_runtime.json')
            entry['proposed_runtime'] = runtime
            entry['selected_native_profile'] = {'name': 'HISTORICAL_QWEN_TEXT_ONLY_SYSTEM_USER_FULL_RAW_SUFFIX',
                'input': 'Exact immutable Qwen system/user template, add_generation_prompt=True, no history/tools',
                'output': 'Entire emitted suffix; no new thinking-mode override or output parser',
                'source': directory + '/REPORT.md sections 6–9 and proposed_runtime.json'}
            pattern = r'^model\.layers\.(?:[0-9]|[1-3][0-9]|4[0-7])\.'
            if directory == 'qwen3_coder_30b_a3b':
                pattern += r'self_attn\.(?:q_proj|k_proj|v_proj|o_proj)$'
                entry['conservative_adaptation'] = {'status': 'SOURCE-SUPPORTED / NOT_RUN', 'target_type': 'ordinary Linear module',
                    'target_regex': pattern, 'scope': '48 main layers, q/k/v/o attention only; router, experts, norms, embedding/head frozen',
                    'module_count': 192, 'rank16_parameter_estimate': 13369344,
                    'count_evidence': '48 * 16 * ((4096+2048)+2*(512+2048)+(2048+4096)); config + existing source inventory',
                    'training': 'Transformers 4.57.6 + PEFT 0.18.0, original BF16; save/reload fresh same original; verified direct serving or separate safe merged derivative'}
                entry['optional_conditional_scopes'] = [{'name': 'routed-expert gate/up/down Linear LoRA', 'status': 'SOURCE-CREDIBLE / NOT_RUN',
                    'required_for_minimum': False, 'note': 'All indexed experts; no active-residency shortcut; direct serving coverage and wider gradients/lifecycle need a separately declared scope-specific matrix.'},
                    {'name': 'derived QLoRA/quantized route', 'status': 'NOT SELECTED / binary stack and numerical conversion unverified', 'required_for_minimum': False}]
                resources = {'original_declared_bytes': 61066575656, 'BF16_base_GiB_approx': 56.87,
                    'inference_planning_GiB': [65, 75], 'starting_topology': 'One 80 GB class GPU; separate alternatives need verification',
                    'host_RAM_start_GiB': [96, 128], 'disk_with_derivatives_start_GB': [150, 250]}
                test_model = 'Qwen3-Coder-30B-A3B'
            else:
                pattern += r'(?:self_attn\.(?:q_proj|k_proj|v_proj|o_proj)|linear_attn\.(?:in_proj_qkvz|in_proj_ba|out_proj))$'
                entry['conservative_adaptation'] = {'status': 'SOURCE-SUPPORTED / NOT_RUN', 'target_type': 'ordinary Linear module',
                    'target_regex': pattern, 'scope': 'Historical all-attention set: full q/k/v/o plus DeltaNet in_proj_qkvz/in_proj_ba/out_proj; recurrent vectors/conv/router/experts frozen',
                    'rank16_parameter_estimate': load(directory, 'adapter_parameter_estimates.json')['examples'][1]['all_attention'],
                    'training': 'Transformers 4.57.6 + PEFT 0.18.0; independently verify full/linear branches under cross-audit O, distributed fresh-original cycle and merge/direct route'}
                entry['optional_conditional_scopes'] = [{'name': 'routed/shared expert Linear LoRA', 'status': 'SOURCE-CREDIBLE / NOT_RUN',
                    'required_for_minimum': False, 'note': 'Router/shared gate excluded; large all-expert adapter/activation residency, explicit targets and separate serving verification.'},
                    {'name': 'derived quantized route', 'status': 'NOT SELECTED', 'required_for_minimum': False}]
                resources = {'original_declared_bytes': 159358031480, 'BF16_tensor_payload_bytes': 159348782592,
                    'inference_planning_aggregate_GiB': [170, 210], 'starting_topology': '4 x 80 GB or separately verified 2 x 141 GB; no purchase/fit guarantee',
                    'host_RAM_start_GiB': [192, 256], 'free_disk_start_GB': [350, 500]}
                test_model = 'Qwen3-Coder-Next'
            tests = [dict(r) for r in cross_tests if r['model'] == test_model]
            entry['infrastructure_matrix_source'] = 'cross_model_audit/infrastructure_test_matrix.csv'
            deferred = []
            entry['scope_gate_note'] = 'Historical A–S gates retained; expert/quantized breadth is outside these 19 conservative checks. O includes both full and linear branches for Next.'
        else:
            targets = load(directory, 'adaptation_targets.json')
            entry['proposed_runtime'] = load(directory, 'runtime_profile.json')
            serialization = load(directory, 'serialization.json')
            entry['selected_native_profile'] = {'name': serialization.get('selected_profile', 'NATIVE_TEKKEN_TEXT_ONLY_SYSTEM_USER_FULL_RAW_SUFFIX'),
                'input': serialization['canonical_render'], 'generation_prefix': serialization['generation_prefix'],
                'output': 'Entire raw emitted suffix, all generated reasoning/markers retained; no output parser/projection',
                'source': directory + '/serialization.json'}
            if directory == 'devstral_small2_2512':
                entry['conservative_adaptation'] = targets['scopes']['attention_only']
                entry['optional_conditional_scopes'] = [{'name': 'dense attention+MLP', 'scope': targets['scopes']['attention_plus_mlp'],
                    'required_for_minimum': False, 'required_for_claim': 'Direct dense MLP adaptation coverage requires P and its dependent lifecycle gates, not attention-only O'}]
                entry['original_conversion'] = load(directory, 'reconstruction_analysis.json')
                deferred = ['P']
            elif directory == 'glm47_flash':
                entry['conservative_adaptation'] = targets['scopes']['MLA_attention_only']
                entry['optional_conditional_scopes'] = [{'name': 'MLA+routed expert parameters', 'scope': targets['scopes']['MLA_plus_routed_expert_parameters'],
                    'required_for_minimum': False, 'restrictions': targets['expert_scope_requirements'],
                    'required_for_claim': 'Q and scope-specific dependent reload/export/lifecycle/resource gates before routed-expert adaptation claims'}]
                deferred = ['Q']
            else:
                entry['conservative_adaptation'] = targets['scopes']['conservative_attention']
                entry['optional_conditional_scopes'] = [{'name': 'attention+Mamba in_proj', 'scope': targets['scopes']['hybrid_attention_mamba_in'],
                    'required_for_minimum': False, 'required_for_claim': 'R plus reference dispatch and dependent lifecycle/parity/reset/resource gates before Mamba projection adaptation claims'},
                    {'name': 'hybrid+routed expert parameters', 'scope': targets['scopes']['expert_hybrid_plus_routed'],
                    'required_for_minimum': False, 'restrictions': targets['parameter_wrapper_restrictions'],
                    'required_for_claim': 'S plus expert gradients/wrapper restoration/memory and scope-specific reload/export gates'}]
                entry['unresolved_excluded_targets'] = targets['excluded']
                deferred = ['R', 'S']
            resources = load(directory, 'resource_estimates.json')
            entry['original_base_lifecycle_source'] = directory + '/original_base_lifecycle.json'
            tests = csv_rows(BASE / directory / 'infrastructure_test_matrix.csv')
            entry['infrastructure_matrix_source'] = directory + '/infrastructure_test_matrix.csv'
            entry['scope_gate_note'] = 'Every historical row remains NOT_RUN. Deferred broader-scope rows are not deleted, passed or treated as prerequisites to the conservative baseline; coverage claims require them.'
        entry['resource_regime'] = resources
        entry['resources_are_descriptive_not_measured_or_hardware_ceiling'] = True
        assert all(t['status'] == 'NOT_RUN' for t in tests)
        entry['NOT_RUN_infrastructure_checks'] = tests
        entry['NOT_RUN_infrastructure_count'] = len(tests)
        entry['deferred_extended_scope_test_ids'] = deferred
        entry['conservative_verification_gate_ids'] = [t['id'] for t in tests if t['id'] not in deferred]
        admitted[directory] = entry
    write_csv('model_status_matrix.csv', list(statuses[0]), statuses)

    coverage = [
        ('ordinary_dense_attention_MLP', 'devstral_small2_2512', 'Native same-original FP8 reconstruction plus ordinary attention; dense MLP scope separately source-supported', 'Dense attention O plus lifecycle; MLP P if claiming MLP adaptation'),
        ('ordinary_attention_routed_MoE', 'qwen3_coder_30b_a3b', 'Original BF16 plus ordinary attention/individual expert Linear topology', 'A–S conservative attention lifecycle; separate expert scope if claiming expert adaptation'),
        ('hybrid_recurrent_DeltaNet', 'qwen3_coder_next', 'Original BF16 plus ordinary full/DeltaNet attention projection LoRA and fresh recurrent state', 'A–S, especially full/linear O and independent sharded/reset lifecycle'),
        ('MLA', 'glm47_flash', 'Native default-thinking full suffix; MLA projection LoRA with same-original expert packing', 'Conservative P and lifecycle; Q only for expert claim'),
        ('Mamba2_state_space', 'nemotron35_lightning_bf16', 'Native default-thinking full suffix; conservative attention plus credible separate Mamba in_proj path', 'Conservative Q plus SSM/reset/parity; R for Mamba projection adaptation, S for expert claim')]
    coverage_rows = []
    for regime, directory, path, later in coverage:
        e = admitted[directory]
        coverage_rows.append({'required_mechanism': regime, 'model': e['model'], 'repository': e['repository'], 'revision': e['revision'],
            'static_path_or_precise_failure': 'STATICALLY ADMISSIBLE FRESH-ORIGINAL PATH', 'path_evidence': path,
            'native_serialization': e['frozen_lineage_evidence']['serialization'], 'later_claim_gate': later,
            'static_gap_resolved': 'YES', 'infrastructure_verified': 'NO', 'source': e['verdict_source']})
    write_csv('mechanism_coverage_matrix.csv', list(coverage_rows[0]), coverage_rows)
    fallback_rows = []
    for primary, repo, reason in [
        ('devstral_small2_2512', 'mistralai/Devstral-Small-2507', 'Own FP8 original has a credible official BF16 reconstruction and fresh-original path; native FP8 backward being unsupported does not trigger replacement.'),
        ('glm47_flash', 'deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct', 'Native default-thinking full-stream profile and credible MLA fresh-original path exist; optional expert/direct-serving uncertainty does not trigger replacement.')]:
        l = landscape[repo]
        assert load(primary, 'original_base_lifecycle.json')['fallback_triggered'] is False
        fallback_rows.append({'primary_configuration_id': primary, 'fallback_repository': repo, 'fallback_revision': l['revision'],
            'status': 'NOT TRIGGERED', 'trigger_condition': 'Only the specific failed-primary static path specified in landscape section 15',
            'reason': reason, 'fallback_work_executed_in_closure': False, 'admitted_to_infrastructure_roster': False})
    dump('fallback_resolution.json', {'triggered': [], 'predeclared_fallbacks': fallback_rows,
        'nemotron_fallback': None, 'nemotron_policy': 'No automatic fallback; record an exact source-based block rather than adding releases/sizes.',
        'future_failure_policy': 'No automatic switch. A later factual blocker can justify documented bounded re-review of its named trigger and distinct original; never use coding outcomes or optional-scope difficulty.'})

    pair_reasons = [
        {'before': ORDER[0], 'after': ORDER[1], 'coverage': 'At the initial baseline every owner adds a core primitive and native wrapper; no performance score or survivor count distinguishes them.',
         'adaptation_testability': 'Native BF16 ordinary attention on Qwen30 avoids Devstral original-FP8 reconstruction/scale/alias and multimodal-key validation at the first baseline.',
         'verification_burden': 'Use established single-sequence full-attention baseline before adding a conversion and different serializer; Qwen30 runtime source lock is an explicit pre-execution gate.',
         'resource_burden': 'Devstral BF16 is smaller, but resources are a later tiebreak and do not override the earlier conversion/testability distinction.'},
        {'before': ORDER[1], 'after': ORDER[2], 'coverage': 'Both add an unrepresented mechanism and serialization after Qwen; dense and MLA are both retained.',
         'adaptation_testability': 'Ordinary dense q/k/v/o and MLP module forwards precede compressed/low-rank attention and expert tensor packing.',
         'verification_burden': 'Resolve Devstral own-original reconstruction explicitly, then add MLA kernel/cache/export validation; no source-supported path is discarded.',
         'resource_burden': 'Devstral reconstructed base ~44.725 GiB versus GLM main ~55.774 GiB supports this engineering sequence; neither estimate is a fit guarantee.'},
        {'before': ORDER[2], 'after': ORDER[3], 'coverage': 'MLA and Mamba each add a new core mechanism and native default-thinking wrapper; both retained.',
         'adaptation_testability': 'Ordinary MLA projection adapter flow precedes reference Mamba scan/dispatch and wrapper-bypass restrictions.',
         'verification_burden': 'Mamba needs SSM/conv/KV reset plus known dt-clamp parity and kernel warmup/reset verification in addition to full suffix checks.',
         'resource_burden': 'Comparable base residency; recurrent backward/workspace uncertainty, rather than active parameter count, is recorded.'},
        {'before': ORDER[3], 'after': ORDER[4], 'coverage': 'Mamba and DeltaNet are independent; Nemotron additionally introduces a serializer not yet checked, while Next shares the already checked Qwen family.',
         'adaptation_testability': 'Next requires separately verified full/linear projection branches and distributed same-original adaptation; no Next pass is inherited.',
         'verification_burden': 'Defer Next sharded load/reset/adapter/export until smaller configurations establish baseline governance/transport; preserve Qwen30 before Next.',
         'resource_burden': 'Next ~148.405 GiB BF16 tensor payload and multi-GPU planning exceeds Nemotron ~58.819 GiB main payload. No hardware ceiling or quality exclusion.'}]
    failure_policy = {'A': {'class': 'PROTOCOL/MODEL INCOMPATIBILITY', 'action': 'STOP that configuration/model track'},
        'B': {'class': 'INFRASTRUCTURE/CONFIGURATION DEFECT', 'action': 'QUARANTINE → bounded repair → rerun affected/dependent gates'},
        'C': {'class': 'MEASUREMENT/VERIFICATION INCOMPLETE', 'action': 'PENDING; never convert to PASS'},
        'repair_invariants': ['same immutable original checkpoint', 'P/K/H and lane budgets', '32768 context', '2048 output reserve',
                              'entire completion semantics', 'task population', 'frozen generation controls', 'normative protocol behavior'],
        'execution_status': 'HANDOFF ONLY; 1G2A NOT STARTED',
        'bounded_repair_note': 'Declare repair scope/attempt bound and dependency graph in later 1G2A before measurements; this audit invents no repair budget.'}
    dump('verification_order.json', {'status': 'FROZEN STATIC ENGINEERING RECOMMENDATION; NOT EXECUTED',
        'priority_rule': ['coverage gain', 'fresh-original adaptation testability', 'verification burden', 'resource burden', 'retain both if still tied'],
        'coverage_subdimensions_from_landscape_14': ['architecture/adaptation', 'serialization', 'adaptation resource', 'inference resource'],
        'coverage_assessment': 'Assess incremental intended core mechanisms and native families; overlapping full-attention blocks do not double-count Next as an independent ordinary-MoE substitute. No invented weighted score.',
        'sequence': ORDER, 'sequence_models': [admitted[k]['model'] for k in ORDER], 'ordering_decisions': pair_reasons,
        'Qwen30_before_Next_preserved': True, 'previous_absolute_adjacency_not_required': 'Earlier order compared only the two Qwens; completed independent gap representatives now occur between them.',
        'tie_policy': 'No candidate removed to impose a model count. Retain both on a genuine tie; sequence is a methodological staging recommendation, not a proof of a unique optimal order.',
        'minimum_first_configuration': ORDER[0],
        'minimum_required_path': {'configurations': [ORDER[0]], 'source_gate_ids': list('ABCDEFGHIJKLMNOPQRS'),
            'scope': 'Native original BF16, conservative attention LoRA, entire raw suffix, full context/control/terminal/isolation/repeat/resource gates, save/reload/serve-or-merge and second fresh ORIGINAL cycle',
            'source_lock_before_any_execution': 'Resolve vLLM 0.11.2 immutable source/build against archived hashes; no silent replacement with 0.16.0/0.30.0',
            'no_pass_transfer': True, 'failure_does_not_automatically_drop_others': True},
        'extended_mechanism_coverage_path': {'configurations': ORDER[1:],
            'scope': 'Independent conservative lifecycle per non-redundant configuration, plus only those hybrid/MLP/expert gates required for the particular intended claim',
            'conditional_scope_claims': {'dense_MLP': 'Devstral P', 'Mamba_input_projection': 'Nemotron R', 'DeltaNet_projection': 'Next O full/linear branches',
                'stacked_expert': 'GLM Q or Nemotron S plus their scope-dependent lifecycle/export/resource checks',
                'ordinary_expert': 'Separately declared Qwen expert scope-specific checks; not automatically included in historical A–S'},
            'all_survivors_all_expensive_scopes_required': False}, 'failure_policy_handoff': failure_policy,
        'spending_or_infrastructure_execution_authorized': False})
    roster = {'status': 'STATIC INFRASTRUCTURE-VERIFICATION ROSTER FROZEN', 'freeze_scope': 'Five exact eligible tracks, native-profile intent, conservative-versus-extended boundaries and recommended order; executable locks/profiles remain unverified',
        'candidate_count': 5, 'NOT_RUN_total_source_matrix_rows': sum(e['NOT_RUN_infrastructure_count'] for e in admitted.values()),
        'candidates': [admitted[k] for k in ORDER],
        'excluded_configuration': {'configuration_id': 'gpt_oss_20b', 'repository': QUEUE[2][2], 'revision': QUEUE[2][3], 'verdict': DROP,
            'reason': blockers['gpt_oss_20b'], 'source': 'cross_model_audit/REPORT.md sections 1–7'},
        'final_experimental_model_roster_frozen': False, 'complete_executable_profiles_frozen': False,
        'final_current_repo_v1_protocol_externally_frozen': False, 'Study1_ready': False,
        'failure_policy_handoff': failure_policy, 'execution_authorized': False}
    dump('infrastructure_roster.json', roster)
    decision = {'decision': 'STOP MODEL SHOPPING: YES', 'static_landscape_closed': True,
        'frozen_rule_source': 'landscape_closure/REPORT.md sections 15 and 22–23',
        'bounded_queue_complete': True, 'queue': [r['model'] for r in statuses], 'required_core_gaps_resolved': [r['required_mechanism'] for r in coverage_rows],
        'named_fallbacks_resolved': True, 'fallbacks_triggered': [], 'optional_regimes_made_mandatory': False,
        'optional_or_reference_regimes_outside_core_claim': ['Gemma native channels', 'Granite modest dense resources', 'dense DeltaNet interaction',
            'conditional-memory lookup', 'latent expert heads', 'CSA/QSA', 'cluster-scale variants'],
        'optional_gap_rule_application': 'No completed bounded preflight establishes an additional feasible conditional-memory/latent/native-channel regime required by the stated five-core-mechanism claim. Existing optional/reference interactions remain outside it, not declared redundant or impossible.',
        'claims_limited_to_retained_and_later_verified_mechanisms': True,
        'reopen_discovery_only_for': ['Concrete factual blocker in an intended admission, documented pre-outcome and tied to a named gap/trigger',
            'Actually material new release/regime under an explicit stated cutoff revision',
            'If conditional license/specialized training evidence establishes an independently feasible known regime required for an explicitly expanded breadth claim, resolve that named scope gap before claiming comprehensive closure'],
        'not_reopen_for': ['benchmark magnitude', 'expected coding quality', 'anticipated adaptation gain', 'desire for an impressive/larger roster', 'optional sensitivity alone'],
        'static_infrastructure_roster_frozen': True, 'final_experimental_roster_frozen': False,
        'final_protocol_external_freeze': False, 'infrastructure_success_claimed': False, 'Study1_readiness_claimed': False,
        'protocol_modified': False, 'new_model_search': False, 'new_checkpoint_introduced': False,
        'weight_bodies_acquired': False, 'model_instantiated': False, 'adapter_executed': False, 'inference_occurred': False,
        'GPU_execution': False, 'protected_candidates_accessed': False, 'benchmark_outcomes_used': False, 'commit_made': False,
        '1G2A_started': False, 'next_boundary': 'STOP after closure; any later infrastructure execution is a separate authorized step'}
    dump('closure_decision.json', decision)
    build_report(statuses, coverage_rows, roster, pair_reasons)
    print(json.dumps({'decision': decision['decision'], 'candidates': 5, 'source_matrix_NOT_RUN': roster['NOT_RUN_total_source_matrix_rows'],
                      'order': ORDER, 'source_inputs': len(paths)}, indent=2))


def build_report(statuses, coverage, roster, ordering):
    lines = ['# STEP 8K-B.1G1E-CLOSE — Static landscape / infrastructure-roster closure', '',
        'Closure review: **2026-10-04, Asia/Calcutta**. The landscape cutoff remains **2026-10-03**; no releases or sources were refreshed.', '',
        '## 1. Verdict', '', '**STOP MODEL SHOPPING: YES**', '',
        '**Static landscape closed: YES**, for the five core mechanism regimes stated in the frozen 1G1E rule. The bounded Devstral/GLM/Nemotron queue has resolved every required gap with a statically admissible fresh-original path. Neither named fallback was triggered.', '',
        'Freeze the **static infrastructure-verification roster of five exact configurations** and its engineering sequence. This freezes who and what is eligible to be verified; all executable runtime locks, infrastructure results, final experimental model selection, external protocol freeze and Study1 readiness remain unestablished.', '',
        '[Closure decision](closure_decision.json), [infrastructure roster](infrastructure_roster.json), [verification order](verification_order.json).', '',
        '## 2. Scope/prohibitions', '',
        'This is a local decision audit of already completed immutable/static evidence. Inputs are restricted to the eight named static artifact groups and the existing Draft2/Draft3 specification/policy artifacts. Exact byte lengths and SHA-256 values are recorded in [source_manifest.json](source_manifest.json). No network request, discovery, model release refresh, new checkpoint, weight body/header acquisition, model/adapter instantiation, recipe, inference, GPU execution or spending occurred.', '',
        'No protected candidate inventory/task, outcome, private scorer, A/B/M/C/BC experiment or Study1/2/3 was accessed or run. No benchmark magnitude, coding-quality prediction or adaptation-gain expectation affected any decision. Draft2/Draft3, P/K/H, BC ownership, 32768 deployed context, 2048 total generated-token reserve, complete replacement and entire-stream semantics remain unchanged. No protocol accommodation, retry, clipping, shifting, suppression or final-only extraction is introduced. No commit.', '',
        '## 3. Completed bounded queue', '',
        'All six requested tracks have completed static dispositions. The two Qwen proceed decisions and the proposed gpt-oss final-only DROP are retained from the [cross-model audit](../cross_model_audit/REPORT.md). The three new mechanism-gap paths retain their own completed preflight verdicts: [Devstral D1](../devstral_small2_2512/REPORT.md), [GLM G1](../glm47_flash/REPORT.md), [Nemotron N1](../nemotron35_lightning_bf16/REPORT.md).', '',
        'The older gpt-oss preflight reported an unresolved Harmony completion boundary. The later cross-model normative audit explicitly resolved it to DROP for the proposed final-only projection. This documented supersession is not an unresolved artifact contradiction; no Harmony question is reopened. No direct contradiction requiring new model-specific investigation was found among the final controlling artifacts.', '',
        'Historical landscape I/A uncertainty for the three work items is resolved by their later preflights. Eligibility/product relevance gates are retained from the frozen landscape, without substituting quality claims or rerunning the census. No historical CSV/report is edited.', '',
        '## 4. Model status matrix', '', '| Model | Exact repository / SHA | Static disposition | Infrastructure eligible |', '|---|---|---|---|']
    for r in statuses:
        lines += [f"| {r['model']} | `{r['repository']}` / `{r['revision']}` | {r['static_verdict']} | {r['eligible_for_infrastructure_verification']} |"]
    lines += ['', '[model_status_matrix.csv](model_status_matrix.csv) records full-stream status, same-original adaptation, regime, remaining blockers, fallback status and verdict authority for every row.', '',
        'Each admitted path captures the entire raw emitted textual suffix, including any generated reasoning/markers. Only already authorized verified final native terminal removal and CRLF/CR normalization may occur; every generated ID still counts toward 2048. A default-thinking profile can produce invalid replacement content or multi-file format failure. Compatibility does not promise useful or code-only output.', '',
        'The excluded gpt-oss projection cannot be repaired through infrastructure because deleting substantive analysis requires a protocol amendment. Its source-credible BF16 adaptation route does not rescue that output path; the DROP remains path-specific rather than an impossibility claim about all gpt-oss outputs.', '',
        '## 5. Frozen mechanism-coverage test', '',
        'Apply [1G1E sections 12–15 and 22–23](../landscape_closure/REPORT.md): the dense, MLA and Mamba gaps must each have a statically admissible fresh-base path or precise source-based failure, with named fallbacks considered where their triggers apply. Together with the historical Qwen paths, all five required core regimes now have positive static paths.', '',
        '| Required regime | Exact static representative | Later claim boundary |', '|---|---|---|']
    for r in coverage:
        lines += [f"| {r['required_mechanism']} | {r['model']} | {r['later_claim_gate']} |"]
    lines += ['', '[mechanism_coverage_matrix.csv](mechanism_coverage_matrix.csv) records immutable identities and source authority. All rows say infrastructure verified **NO**. Static representation does not establish completed experiments or model-wide adaptation coverage.', '',
        'Serialization diversity is already present as Qwen ChatML/non-thinking, Tekken/Mistral instructions, GLM native roles/default thinking and Nemotron ChatML/default thinking with different vocabulary/control/state behavior. Common markers do not establish equivalent lineage or output transport. Harmony is an explicit source-based failed proposed boundary, not a retained positive transport.', '',
        'Optional Gemma channels, modest dense Granite resources, dense DeltaNet interactions, latent experts, conditional-memory lookup, CSA/QSA and cluster-scale variants remain visible outside the core claim. The completed queue does not establish a new independently feasible instance of those regimes that is required by the stated core scope. None is made mandatory merely because it appears in the 36-model census, and none is declared redundant or impossible. No claim to every architecture, frontier release or mechanism×serialization×resource interaction is made.', '',
        '## 6. STOP-MODEL-SHOPPING decision', '', '**STOP MODEL SHOPPING: YES**', '',
        'Every section-15 work item names its immutable original, eligible/source-credible inference/adaptation/product path, exact full-stream native profile, target scopes, same-original lifecycle, descriptive resources and empirical matrix. Both fallback conditions are resolved without activation. The section-22 conditional stop is therefore satisfied for the frozen core scope.', '',
        'Legitimate reopening requires a concrete factual blocker in an intended admission, or an actually material new release/regime under a stated cutoff revision. If resolved licensing/specialized-training evidence establishes an independently feasible known extra regime that an explicitly expanded breadth claim requires, resolve that named scope gap before asserting comprehensive closure. Document the reason and scope pre-outcome. Do not reopen for benchmark magnitude, expected adaptation quality, a more impressive roster or optional sensitivity alone. No new cutoff or expanded claim is adopted now.', '',
        '## 7. Fallback resolution', '',
        '- **Devstral Small 2 → Devstral-Small-2507: NOT TRIGGERED.** D1 establishes reconstruction from its own immutable FP8 original to BF16 and a credible fresh-original LoRA/save/reload/export cycle. Unsupported direct native-FP8 training alone is not the stipulated failure.',
        '- **GLM-4.7-Flash → DeepSeek-Coder-V2-Lite-Instruct: NOT TRIGGERED.** G1 establishes default-thinking full-suffix compatibility and MLA adaptation. Optional expert/direct-serving uncertainty does not negate that conservative path.',
        '- **Nemotron: no automatic fallback exists.** Do not invent one or move up a size ladder.', '',
        'Exact already-censused fallback SHAs and conditions are in [fallback_resolution.json](fallback_resolution.json). Neither fallback was preflighted anew, admitted, downloaded or executed here. A later empirical failure does not automatically switch originals; its class and factual implication must be documented under the bounded policy.', '',
        '## 8. Redundancy analysis', '',
        'Apply only the frozen four dimensions: architecture/base lineage, documented checkpoint/training lineage, tokenizer/serialization family, and runtime/adaptation characteristics. Checkpoint identity alone is not a novelty argument; shared vendor or tokenizer alone is not a redundancy argument. All five survive as **NON-REDUNDANT** for the stated core scope.', '']
    for e in roster['candidates']:
        lines += [f"- **{e['model']}: NON-REDUNDANT.** {e['non_redundancy_reason']}"]
    lines += ['', 'Frozen landscape lineage groups and documentary reasons are retained in each roster entry. Material architecture/state/conversion differences suffice here; undocumented training ancestry is not invented to create independence. These choices do not identify causal performance effects, infer model quality or force a survivor count. No redundant-for-core candidate was found among the five admitted paths.', '',
        '## 9. Infrastructure-verification roster', '',
        'The bounded roster contains exactly the following verification tracks. Each has static protocol compatibility, a credible same-original adapter path, a non-redundant core contribution and no unresolved static blocker eliminating its conservative path. Empirical blockers remain explicit.', '',
        '| Track | Selected native profile | Conservative scope | Proposed serving runtime | Existing NOT_RUN matrix |', '|---|---|---|---|---|',
        '| Qwen30 | Historical exact system/user ChatML + full raw suffix | 192 q/k/v/o Linear targets; original BF16 | vLLM 0.11.2 V1 | Cross-audit A–S: 19 |',
        '| Devstral Small 2 | Tekken text-only SYSTEM_PROMPT/INST, ends [/INST], full suffix | 160 q/k/v/o targets on own-original BF16 reconstruction | vLLM 0.30.0 pinned commit | D1 A–X: 24 |',
        '| GLM-4.7-Flash | Native default thinking + full raw suffix | 235 MLA q_a/q_b/kv_a/kv_b/o targets | vLLM 0.30.0 pinned commit | G1 A–X: 24 |',
        '| Nemotron BF16 | Native default thinking + full raw suffix | 24 attention q/k/v/o targets | vLLM 0.30.0 pinned commit | N1 A–X: 24 |',
        '| Qwen Next | Historical exact system/user Qwen template + full raw suffix | Full attention + DeltaNet projection Linears, historical all-attention scope | vLLM 0.16.0 pinned commit | Cross-audit A–S: 19 |', '',
        'The roster JSON preserves exact source profiles/arguments, target scopes, matrix row **names and procedures**, resources and provenance links. Total source matrix rows: **110, all NOT_RUN**. Counts are evidence inventories, not a requirement to run every conditional broader-scope row on every model.', '',
        'No runtime version is refreshed or unified. Qwen30 0.11.2 still needs an immutable source/build lock against its archived hashes before execution. Next retains 0.16.0 at `89a77b10846fd96273cce78d86d2556ea582d26e`. D1/G1/N1 retain 0.30.0 at `ced6857afa0ea7b2e3f0846a62e1394e90f15607`, Transformers `02d8fb9784e8f14a1251e4c992cd82a5762417c6` and PEFT `532a05dd505c28993119b7715ee286f4234bf51b`. Full binary/container/CUDA/kernel/transitive locks are unverified. Source support is not a runnable environment.', '',
        'Optional scopes remain separate: Devstral attention+MLP, GLM stacked routed parameters, Nemotron Mamba in_proj and hybrid+expert parameters, and the Qwens’ wider expert/derived quantized paths. Frozen routers/norms/state vectors/modality exclusions and Mamba fused out_proj exclusion remain intact. Direct broad adapter serving is not inferred from training injection. A verified separate merge/export derivative may serve where source-credible, but can never parent adaptation.', '',
        'Resource descriptions retain full residency. Qwen30 original is 61,066,575,656 bytes, approximately 56.87 GiB BF16 base, with 65–75 GiB serving planning. Devstral original is 25,793,059,408 bytes; its full BF16 reconstruction is 48,022,722,560 bytes, about 44.725 GiB, with roughly 51.725–57.725 GiB base/KV/workspace subtotal. GLM main payload is 59,886,793,728 bytes, about 55.774 GiB. Nemotron main payload is 63,155,886,464 bytes, about 58.819 GiB, plus SSM/conv/KV/workspace. Next tensor payload is 159,348,782,592 bytes, about 148.405 GiB, with roughly 170–210 GiB aggregate inference planning and distributed loading/export. Original MTP bodies remain retained where present.', '',
        'These are inherited arithmetic/planning ranges, not measurements, a hardware ceiling, a purchase authorization or throughput ranking. Original authentication, reconstruction/repacking, fresh optimizer/RNG and repeated full-original reload/reset/export burden must all be measured. No active-parameter residency shortcut is used.', '',
        '## 10. Verification order', '',
        '**Qwen3-Coder-30B-A3B-Instruct → Devstral-Small-2-24B-Instruct-2512 → GLM-4.7-Flash → NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 → Qwen3-Coder-Next.**', '',
        'Use coverage gain, fresh-original adaptation testability, verification burden, resource burden, then retain both if still tied. Within coverage preserve the landscape dimensions: architecture/adaptation, serialization, adaptation-resource and inference-resource coverage. These are qualitative source-grounded comparisons; no weighted or benchmark score is invented. All independent core owners remain in the roster.', '']
    for n, pair in enumerate(ordering, 1):
        lines += [f"{n}. **{pair['before']} before {pair['after']}.** {pair['coverage']} {pair['adaptation_testability']} {pair['verification_burden']} {pair['resource_burden']}"]
    lines += ['', 'Qwen30 before Next remains preserved. Earlier two-Qwen ordering did not require adjacency once three independent mechanism-gap representatives completed. Next is deferred, not discarded. The sequence is an explicit engineering recommendation rather than a theorem of unique optimality. No concrete project resource cap was supplied, so no resource tiebreak eliminates a survivor. Identical resource estimates or tied evidence would retain both.', '',
        '## 11. Minimum required path', '',
        '**Minimum first configuration: Qwen3-Coder-30B-A3B-Instruct**, exact BF16 original and historical native input/full-suffix profile, conservative attention LoRA. Preserve the cross-audit A–S matrix: exact bodies, immutable source/build/parser lock, real 32768 capacity, prompt/control/native-terminal/cap/raw-byte certificates, same/fresh-process repeats, no-read/no-tools isolation, measured peaks/timing, backward, save/reload, a verified serve-or-merge route, second ORIGINAL rebuild and contamination audit.', '',
        'Later execution should resolve nonhardware lock/profile/fixture/isolation gates first; then shortest load/prompt/terminal checks before near-capacity/cap/repeat tests; then conservative adapter lifecycle. Include measurements while the authorized checks run rather than provisioning a separate timing-only deployment. Freeze fixtures/repeats/tolerances/acceptance before measurement. None of this work begins here.', '',
        'This minimum establishes a testable infrastructure/protocol baseline before spending on additional mechanisms. It does not establish dense/MLA/Mamba/DeltaNet adaptation breadth or a final product choice. Qwen30 failure does not automatically reject another architecture: shared contract/isolation defects must be resolved; architecture-specific failures follow their own stopped/quarantined/pending track. No quality outcome changes the order.', '',
        '## 12. Extended mechanism-coverage path', '',
        'Then independently verify Devstral, GLM, Nemotron and Next in the stated order, retaining each exact native profile and original. Definitions and gate procedures may be reused; model/token/control/state/gradient/lifecycle passes cannot be inherited.', '',
        '- Devstral conservative attention O can precede attention+MLP P. A dense MLP adaptation claim requires P and its scope-dependent save/reload/export/reset/resource gates; the full D1 matrix remains NOT_RUN.',
        '- GLM conservative MLA P precedes optional routed-parameter Q. An MLA mechanism claim does not require all expert parameters to adapt; expert claims do require Q and the corresponding lifecycle/export/memory evidence.',
        '- Nemotron conservative attention Q plus ordinary model/state/SSM reset gates establishes only the narrow path. Mamba input-projection adaptation claims require R with the pinned reference dispatch and relevant lifecycle/parity/reset gates. Expert scope S is independently conditional. Fused out_proj stays excluded.',
        '- Next’s historical conservative all-attention scope already includes full and DeltaNet Linear projections. Cross-audit O must independently verify both branches plus fresh hybrid state; routed/shared experts are separate, expensive scope choices.', '',
        'No automatic requirement exists to execute every expensive expert or quantized scope on every survivor. Historical matrix rows are retained with their original NOT_RUN statuses, while the closure adds conservative-versus-extended staging annotations. Unexecuted branches cannot become PASS or support their associated claims. Final architecture-breadth claims must name the configurations and scopes that actually pass.', '',
        '## 13. Failure-policy handoff', '',
        'Restate the planned 1G2A classes from the [closure instruction](request_source.txt), without executing 1G2A:', '',
        '| Class | Required action |', '|---|---|',
        '| A. PROTOCOL/MODEL INCOMPATIBILITY | STOP that configuration/model track |',
        '| B. INFRASTRUCTURE/CONFIGURATION DEFECT | QUARANTINE → bounded repair → rerun affected/dependent gates |',
        '| C. MEASUREMENT/VERIFICATION INCOMPLETE | PENDING; never convert to PASS |', '',
        'No repair may change P/K/H or other budgets, 32768 context, 2048 reserve, completion semantics, task population, generation controls or normative protocol behavior merely to obtain PASS. Preserve immutable original identity and provenance. A runtime configuration alias, packing/export fix or dependency repair is permissible only as a documented engineering correction within those invariants; it requires affected/dependent recertification and cannot silently change the selected original/profile.', '',
        'Specify the repair bound, affected/dependent gate graph, repeat roster and tolerance policy in the later authorized 1G2A plan. This audit introduces no numeric retry/repair budget and no generation retry. A changed checkpoint or genuinely incompatible output contract is not an infrastructure repair.', '',
        '## 14. Freeze boundaries', '',
        '| Boundary | State after closure | Meaning |', '|---|---|---|',
        '| STATIC LANDSCAPE CLOSED | YES, frozen core scope and existing cutoff | Bounded static queue complete; broad shopping stops |',
        '| INFRASTRUCTURE ROSTER FROZEN | YES, static five-track roster/order/scope boundaries | Exact configurations eligible for later verification; no infrastructure success |',
        '| Complete executable runtime/profile locks | NO | Later source/build/container/hardware/effective-control certification required |',
        '| FINAL EXPERIMENTAL MODEL ROSTER | NO | Depends on later candidate-blind infrastructure evidence and reviewed scope decision |',
        '| FINAL current-repo-v1 PROTOCOL FREEZE | NO | Existing drafts unchanged; external governance/conformance/admission prerequisites remain |',
        '| Study1 readiness | NO | No execution/admission/population/external certification established |', '',
        'Static roster freezing is newly authorized by this closure step; earlier preflights correctly withheld it. It does not retrospectively alter them. Eligibility/profile intent is frozen, while runtime proposals still contain explicitly unresolved locks. Repairs or a documented factual incompatibility require transparent bounded disposition updates, not open-ended model shopping or outcome-driven selection.', '',
        '## 15. Remaining blockers', '',
        'Every model has unresolved empirical body/build/capacity/output/control/terminal/isolation/repeat/resource/adapter/lifecycle gates. Specific source-identified concerns remain: Qwen30 immutable 0.11.2 lock; Next distributed recurrent-state and notice packaging; Devstral original-FP8 reconstruction/key/scaling/alias/export behavior; GLM body/index discrepancy and MLA/expert packing/cache/kernel parity; Nemotron body/index discrepancy, reference Mamba backward and training/serving dt-clamp/state/kernel parity. These do not become static failures merely because execution has not occurred.', '',
        'The cross-model audit’s remaining final-protocol prerequisites are retained: independent normative/configuration review, exact implementation/build identities, product/deny/acquisition authentication and external verifier/signer roles, later authorized public-task certification, chronology/curated-evidence governance, independent literal conformance expectations and CPython 3.11.9/Unicode 14.0 certification, verified runtime/no-read profiles, later common pre-outcome admission/intersection and information-matching claim limits. Their protected artifacts were neither inspected nor certified here. This closure supplies only the static roster prerequisite.', '',
        '## 16. Files created/modified', '',
        'All new writes are under `experiments/model_preflight/roster_closure/`: REPORT.md, both required CSV matrices, infrastructure_roster.json, verification_order.json, fallback_resolution.json, closure_decision.json, source_manifest.json, artifact_manifest.json, validation.json, baseline_integrity.json, request_source.txt and deterministic standard-library build/validation scripts.', '',
        'Historical reports/manifests/fixtures, Draft2/Draft3/policy and product tracked files remain unchanged. Preservation uses the existing permitted allowlist extended through completed N1: **1217 prior files**, without protected directory enumeration. The artifact manifest records sizes/SHA-256 for every new file except itself to avoid circular hashing. [Validation](validation.json).', '',
        'HEAD remains `7fcdecbe26f4fd01138edf8f58c02ce4b947db0b`; final status remains `?? experiments/model_preflight/`, already present at entry. Tracked/staged diffs are empty; no commit.', '',
        '## 17. Claim limitations', '',
        'This step establishes static closure and bounded verification eligibility/order only. It establishes no runnable installation, infrastructure pass, final model selection, model quality, adaptation improvement, throughput/fit guarantee, final protocol external verification or Study1 readiness. A source-supported path is not a measured successful lifecycle. A synthetically fitting prompt is not loaded-model capacity. Greedy/seed does not certify determinism; independently retained reasoning may make replacement output invalid.', '',
        'No claim spans every model in the 36-entry census or every optional interaction. A distinct model architecture does not establish performance diversity, causal attribution or adaptation gain. Scope/process attestations and preservation hashes are not OS-level no-read/isolation trace certificates. Old preflight hardware measurements remain historical and were not refreshed or used as a project hardware ceiling.', '',
        '## 18. Final recommendation', '',
        '**STOP MODEL SHOPPING: YES. Static landscape closed: YES.** Freeze the five exact static infrastructure-verification tracks and engineering sequence recorded above. Minimum first configuration: **Qwen3-Coder-30B-A3B-Instruct**. Fallbacks triggered: **NONE**. Final experimental model roster and final external protocol freeze remain open.', '',
        '**Protocol changed: NO. Inference occurred: NO. Protected candidates accessed: NO. Commit made: NO.**', '',
        '**STOP.** Do not begin 1G2A, download weights, instantiate models/adapters, rent/use GPUs or start infrastructure verification in this step.', '']
    (ROOT / 'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
