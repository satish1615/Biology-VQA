"""Framework-agnostic scientific VQA dataset validation."""
from collections import Counter
from pathlib import Path
import json

DOMAINS = {
    "Cell Biology", "Molecular Cell Biology", "Genetics",
    "Biochemistry", "Neurobiology", "Immunology",
}
LETTERS = ("A", "B", "C", "D")
REQUIRED_FIELDS = (
    "id", "subdomain", "image", "question", "choices", "answer",
    "explanation", "image_description", "visual_evidence", "image_provenance",
)


def load_tasks(path: str | Path) -> list[dict]:
    """Read JSON tasks. Caller is responsible for validating content."""
    with Path(path).open(encoding="utf-8") as handle:
        result = json.load(handle)
    if not isinstance(result, list):
        raise ValueError("Expected a JSON list of task records")
    return result


def validate_task(task: dict, asset_root: Path | None = None) -> list[str]:
    """Return actionable errors; no model is required for validation."""
    if not isinstance(task, dict):
        return ["Task must be a JSON object"]
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in task:
            errors.append(f"Missing field: {field}")
    if errors:
        return errors
    if not isinstance(task["id"], str) or not task["id"].strip():
        errors.append("id must be a non-empty string")
    if task["subdomain"] not in DOMAINS:
        errors.append(f"subdomain must be one of: {', '.join(sorted(DOMAINS))}")
    choices = task["choices"]
    if not isinstance(choices, dict) or set(choices) != set(LETTERS):
        errors.append("choices must contain exactly A, B, C, D")
    elif any(not isinstance(v, str) or not v.strip() for v in choices.values()):
        errors.append("All choices must be non-empty strings")
    elif len({v.strip().casefold() for v in choices.values()}) != 4:
        errors.append("All distractors and the correct choice must be distinct")
    if task["answer"] not in LETTERS:
        errors.append("answer must be A, B, C, or D")
    for field, minimum in (("question", 40), ("explanation", 100), ("image_description", 140), ("image_provenance", 15)):
        if not isinstance(task[field], str) or len(task[field].strip()) < minimum:
            errors.append(f"{field} must have at least {minimum} characters")
    evidence = task["visual_evidence"]
    if not isinstance(evidence, list) or len(evidence) < 2 or any(not isinstance(x, str) or len(x.strip()) < 18 for x in evidence):
        errors.append("visual_evidence needs at least two specific observations (18+ characters each)")
    image = task["image"]
    if not isinstance(image, str) or not image.strip():
        errors.append("image must be a path string")
    elif asset_root is not None:
        root = Path(asset_root).resolve()
        candidate = (root / image).resolve()
        if not candidate.is_relative_to(root):
            errors.append("image path must stay within the project root")
        elif not candidate.is_file():
            errors.append(f"image missing: {image}")
    return errors


def validate_dataset(tasks: list[dict], asset_root: Path | None = None) -> dict[str, list[str]]:
    errors = {str(t.get("id", f"item-{i}")) if isinstance(t, dict) else f"item-{i}": validate_task(t, asset_root) for i, t in enumerate(tasks)}
    counts = Counter(t.get("id") for t in tasks if isinstance(t, dict))
    for i, task in enumerate(tasks):
        if isinstance(task, dict) and counts[task.get("id")] > 1:
            errors[str(task.get("id", f"item-{i}"))].append("Duplicate task id")
    return {key: messages for key, messages in errors.items() if messages}


def evaluate_response(task: dict, selected: str) -> dict:
    """Grade one response against an explicitly authored gold answer."""
    if selected not in LETTERS:
        raise ValueError("selected must be A, B, C, or D")
    return {
        "correct": selected == task["answer"],
        "gold_answer": task["answer"],
        "explanation": task["explanation"],
        "visual_evidence": task["visual_evidence"],
    }


def dataset_summary(tasks: list[dict]) -> dict:
    return {"tasks": len(tasks), "domains": dict(sorted(Counter(t["subdomain"] for t in tasks).items())),
            "answer_distribution": dict(sorted(Counter(t["answer"] for t in tasks).items()))}
