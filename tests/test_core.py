from pathlib import Path
from copy import deepcopy
import pytest
from biovqa.core import load_tasks, validate_dataset, validate_task, dataset_summary, evaluate_response

ROOT = Path(__file__).resolve().parents[1]
TASKS = load_tasks(ROOT / 'data/tasks.json')

def test_all_curated_tasks_valid():
    assert validate_dataset(TASKS, ROOT) == {}

def test_answers_and_distractors_unique():
    for task in TASKS:
        assert len(set(task['choices'].values())) == 4
        assert task['answer'] in task['choices']

def test_grading():
    task = TASKS[0]
    assert evaluate_response(task, task['answer'])['correct'] is True
    assert evaluate_response(task, next(k for k in 'ABCD' if k != task['answer']))['correct'] is False
    with pytest.raises(ValueError):
        evaluate_response(task, 'E')

def test_duplicate_ids_rejected():
    assert 'Duplicate task id' in validate_dataset([TASKS[0], TASKS[0]], ROOT)[TASKS[0]['id']]

def test_image_path_traversal_rejected():
    bad = deepcopy(TASKS[0]); bad['image'] = '../../etc/passwd'
    assert any('within' in e for e in validate_task(bad, ROOT))

def test_bad_choices_rejected():
    bad = deepcopy(TASKS[0]); bad['choices']['B'] = bad['choices']['A']
    assert any('distinct' in e for e in validate_task(bad, ROOT))

def test_summary():
    summary = dataset_summary(TASKS)
    assert summary['tasks'] == 6
    assert summary['domains']['Biochemistry'] == 2
