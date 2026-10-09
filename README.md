# BioVQA AI

An **interactive Biology visual question answering (VQA) workbench** designed to practice building precise, image-grounded scientific assessments. It includes six authored schematic figures spanning cell biology, gene regulation, biochemistry, genetics and neurobiology. Each question has four distinct choices, a verified gold option, scientific reasoning, at least two image observations and a source statement.

## What works

- **Practice:** study the image, answer an image-dependent question, then review evidence and mechanistic reasoning.
- **Task Explorer:** browse six curated sample records; export the dataset as JSON.
- **Author & Validate:** compose a new VQA record and check answer format, textual completeness and local image path; export validated tasks.
- **Dataset Audit:** examine topical coverage, correct-answer distribution, duplicate IDs, images and schema validity.
- **Automated tests:** exercise validation, path safety, scoring and dataset summaries.

## Launch

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
streamlit run app.py
```

Open the local URL shown by Streamlit, usually `http://localhost:8501`.

```bash
python -m biovqa.cli validate
python -m biovqa.cli summary
pytest -q
```

## Repository layout

```text
BioVQA-AI/
  app.py                  # interactive interface
  assets/                 # six original SVG educational diagrams
  data/tasks.json         # six original reviewed-by-code example records
  src/biovqa/core.py      # validation, scoring, dataset summaries
  src/biovqa/cli.py       # quality-check CLI
  tests/test_core.py      # regression tests
```

## Image and scientific integrity

The diagrams in `assets/` are **original schematic illustrations** created for this demonstration. They are **not genuine microscopy, protein-assay results or patient records**. Scientific explanations are educational, not peer-reviewed or medically validated. A schema check cannot establish biology correctness, true image dependence, distractor quality or research applicability. Real VQA dataset work requires domain review, clear permissions or licenses for source images, and reproducible provenance.

For histopathology, cytology and fluorescence microscopy, use a real, appropriately licensed image dataset and the companion **LifeSci Vision Evaluator** project; do not label generated illustrations as laboratory specimens.

## Application to biology-evaluation work

Concepts demonstrated: **biology VQA, scientific image description, multiple-choice distractor design, visual evidence, structured annotation, evaluation schemas, answer-key verification, Python testing**.

## Development roadmap

- Add domain-expert review states, multi-reviewer agreement and disagreement tracking.
- Support image-region annotations with coordinates and evidence references.
- Add independent expert-written question sets and blinded model evaluation runs.
- Import ethically sourced licensed microscopy and molecular biology figures.

## License
MIT. Example assets and sample dataset are included as original materials under this repository license.
