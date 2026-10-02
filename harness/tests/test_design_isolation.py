"""Researcher artifacts stay Git-visible but never experimental model inputs."""

import json
from pathlib import Path
import subprocess
from unittest.mock import Mock

import pytest

from harness.adaptation import apply_structured_adaptation, validate_adaptation_config
from harness.context import build_context, collect_context_files
from harness.isolation import require_model_path
from harness import run_experiment as runner
from harness.workspace import create_workspace
from harness.tests.test_evaluation import experiment


@pytest.fixture
def repository(tmp_path):
    (tmp_path / 'benchmark_design' / 'nested').mkdir(parents=True)
    (tmp_path / 'benchmark_design' / 'nested' / 'audit.json').write_text(
        '{"secret": "researcher sentinel"}', encoding='utf-8')
    (tmp_path / 'app.py').write_text('VALUE = 1', encoding='utf-8')
    return tmp_path


def test_tracked_tree_collection_without_gitignore(repository):
    subprocess.run(['git', 'init', str(repository)], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(repository), 'add', '.'], check=True)
    tracked = subprocess.check_output(
        ['git', '-C', str(repository), 'ls-files'], text=True)
    assert 'benchmark_design/nested/audit.json' in tracked
    assert not (repository / '.gitignore').exists()
    files = collect_context_files(repository)
    assert 'app.py' in files
    assert not any('benchmark_design' in name for name in files)
    assert not any(name.startswith('.git/') for name in files)
    assert 'VALUE = 1' in build_context(repository, ['app.py'])
    assert 'researcher sentinel' not in build_context(repository, ['app.py'])


@pytest.mark.parametrize('name', [
    'benchmark_design/nested/audit.json',
    'benchmark_design\\nested\\audit.json',
    'safe/../benchmark_design/nested/audit.json',
    '../benchmark_design/nested/audit.json',
    'BENCHMARK_DESIGN/nested/audit.json',
    'benchmark_design/../app.py',
])
def test_explicit_context_paths_rejected(repository, name):
    with pytest.raises(ValueError, match='Researcher-only'):
        build_context(repository, [name])


def test_absolute_path_and_sensitive_root_rejected(repository):
    with pytest.raises(ValueError):
        build_context(repository, [str(repository / 'benchmark_design/nested/audit.json')])
    with pytest.raises(ValueError):
        collect_context_files(repository / 'benchmark_design')
    with pytest.raises(ValueError):
        create_workspace(repository / 'benchmark_design')


@pytest.mark.parametrize('field', ['memory_file', 'rule_file'])
@pytest.mark.parametrize('variant', ['relative', 'absolute', 'backslashes', 'parent'])
def test_adaptation_rejects_file_sources_before_read(repository, field, variant):
    name = 'benchmark_design/nested/audit.json'
    name = {'relative': name, 'absolute': str(repository / name),
            'backslashes': name.replace('/', '\\'),
            'parent': 'memory/../' + name}[variant]
    with pytest.raises(ValueError):
        validate_adaptation_config({'condition': 'B', field: name})
    with pytest.raises(ValueError):
        runner.load_json_file(name)


def test_root_workspace_copy_excludes_nested_tree(repository, monkeypatch):
    (repository / '.git').mkdir()
    (repository / '.git' / 'sensitive-object').write_text('researcher sentinel')
    monkeypatch.chdir(repository)
    workspace = create_workspace(repository)
    assert (workspace / 'app.py').read_text() == 'VALUE = 1'
    assert not (workspace / 'benchmark_design').exists()
    assert not (workspace / '.git').exists()


def test_git_metadata_cannot_reintroduce_tracked_design(repository):
    with pytest.raises(ValueError, match='Git metadata'):
        build_context(repository, ['.git/objects/design'])


@pytest.mark.parametrize('origin', [
    'benchmark_design/nested/audit.json',
    'C:\\repo\\benchmark_design\\nested\\audit.json',
    'safe/../benchmark_design/discovery/example.md',
])
def test_preflight_aborts_before_model_invocation(monkeypatch, origin):
    generate = Mock(side_effect=AssertionError('Model must not run'))
    monkeypatch.setattr(runner, 'generate', generate)
    sources = [('repository context', 'innocuous body')]
    messages = [{'role': 'user', 'content': 'Implement.'}]
    with pytest.raises(ValueError, match='Researcher-only'):
        runner.generate_with_preflight(messages, sources, {}, source_paths=(Path(origin),))
    generate.assert_not_called()


@pytest.mark.parametrize('body', [
    'note = "benchmark_design"',
    '# Documentation mentions benchmark_design/discovery/example.md',
])
def test_allowed_source_mentions_pass_context_and_preflight(repository, monkeypatch, body):
    (repository / 'app.py').write_text(body, encoding='utf-8')
    context = build_context(repository, ['app.py'])
    generate = Mock(return_value='mock response')
    monkeypatch.setattr(runner, 'generate', generate)
    messages = [{'role': 'user', 'content': context}]
    assert runner.generate_with_preflight(
        messages, [('repository context', context)], {},
        source_paths=(repository / 'app.py',),
    ) == 'mock response'
    generate.assert_called_once_with(messages, {})


@pytest.mark.parametrize('text', [
    'Discuss why benchmark_design is researcher-only.',
    'The directory name benchmark_design is reserved.',
])
def test_task_mentions_pass_preflight(monkeypatch, text):
    generate = Mock(return_value='mock response')
    monkeypatch.setattr(runner, 'generate', generate)
    messages = [{'role': 'user', 'content': text}]
    runner.generate_with_preflight(messages, [('task prompt', text)], {})
    generate.assert_called_once_with(messages, {})


@pytest.mark.parametrize('label', [
    'Discussion of benchmark_design',
    'benchmark_design/discovery/example.md',
])
def test_free_text_labels_do_not_claim_origin(monkeypatch, label):
    generate = Mock(return_value='mock response')
    monkeypatch.setattr(runner, 'generate', generate)
    messages = [{'role': 'user', 'content': 'Implement.'}]
    runner.generate_with_preflight(messages, [(label, 'Implement.')], {})
    generate.assert_called_once()


@pytest.mark.parametrize('condition,component', [('B', 'memory'), ('C', 'rule'), ('M', 'evidence')])
def test_inline_adaptation_mentions_pass_validation_and_preflight(monkeypatch, condition, component):
    state = validate_adaptation_config({
        'condition': condition, 'adaptation_schema': '1',
        'adaptation': {component: 'Earlier documentation mentioned benchmark_design.'},
    })
    prompt, sources = apply_structured_adaptation('Implement.', state)
    messages = [{'role': 'user', 'content': prompt}]
    generate = Mock(return_value='mock response')
    monkeypatch.setattr(runner, 'generate', generate)
    runner.generate_with_preflight(messages, sources, {})
    generate.assert_called_once_with(messages, {})


@pytest.mark.parametrize('field', ['memory_file', 'rule_file'])
def test_adaptation_resolved_alias_rejected_before_read_and_inference(experiment, monkeypatch, field):
    path, config, base, _ = experiment
    alias = 'adaptation-alias.json'
    original = Path.resolve
    def resolve(candidate, *args, **kwargs):
        if candidate.name == alias:
            return base.parent / 'benchmark_design/discovery/example.json'
        return original(candidate, *args, **kwargs)
    monkeypatch.setattr(Path, 'resolve', resolve)
    reader = Mock(side_effect=AssertionError('Protected artifact must not be read'))
    with monkeypatch.context() as reads:
        reads.setattr(Path, 'read_text', reader)
        with pytest.raises(ValueError, match='Researcher-only'):
            validate_adaptation_config({'condition': 'B', field: alias})
        with pytest.raises(ValueError, match='Researcher-only'):
            runner.load_json_file(alias)
        reader.assert_not_called()
    config[field] = alias
    path.write_text(json.dumps(config), encoding='utf-8')
    result = runner.run_experiment(path)
    assert result['run_status'] == 'invalid_infrastructure'
    assert 'Researcher-only' in str(result['errors'])
    runner.generate.assert_not_called()


def test_historical_adaptation_and_context_paths_validate():
    root = Path(__file__).resolve().parents[2]
    configs = list((root / 'experiments').glob('*.json'))
    assert configs
    for path in configs:
        config = json.loads(path.read_text(encoding='utf-8'))
        validate_adaptation_config(config)
        for name in config['context_files']:
            require_model_path(root / 'taskflow_base' / name)


@pytest.mark.parametrize('origin', ['benchmark_design/nested/audit.json', '.git/objects/design'])
def test_resolved_aliases_are_rejected(repository, monkeypatch, origin):
    # Deterministically exercise resolved-origin checking without OS symlink privileges.
    (repository / 'alias.json').write_text('researcher sentinel')
    original = Path.resolve
    def resolve(path, *args, **kwargs):
        if path.name == 'alias.json':
            return repository / origin
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'resolve', resolve)
    with pytest.raises(ValueError):
        build_context(repository, ['alias.json'])
    assert 'alias.json' not in collect_context_files(repository)
    monkeypatch.chdir(repository)
    assert not (create_workspace(repository) / 'alias.json').exists()


@pytest.mark.parametrize('field', ['context_files', 'memory_file', 'rule_file'])
def test_official_execution_invalid_before_inference(experiment, field):
    path, config, base, _ = experiment
    sensitive = 'benchmark_design/nested/audit.json'
    if field == 'context_files':
        config[field] = [sensitive]
    else:
        config[field] = sensitive
    path.write_text(json.dumps(config), encoding='utf-8')
    result = runner.run_experiment(path)
    assert result['run_status'] == 'invalid_infrastructure'
    assert 'Researcher-only' in str(result['errors'])
    runner.generate.assert_not_called()
