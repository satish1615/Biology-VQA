"""CLI: python -m biovqa.cli [validate|summary]."""
import argparse
import json
from pathlib import Path
from .core import load_tasks, validate_dataset, dataset_summary


def main():
    parser = argparse.ArgumentParser(description="Validate or summarize Biology VQA tasks")
    parser.add_argument("action", choices=["validate", "summary"])
    parser.add_argument("--dataset", type=Path, default=Path("data/tasks.json"))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    tasks = load_tasks(args.dataset)
    if args.action == "summary":
        print(json.dumps(dataset_summary(tasks), indent=2))
        return
    errors = validate_dataset(tasks, args.root)
    if errors:
        print(json.dumps(errors, indent=2))
        raise SystemExit(1)
    print(f"PASS: {len(tasks)} tasks valid; images found; unique IDs")


if __name__ == "__main__":
    main()
