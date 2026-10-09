"""BioVQA AI: working Streamlit question-authoring and practice app."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from biovqa.core import DOMAINS, LETTERS, dataset_summary, evaluate_response, load_tasks, validate_dataset, validate_task

ROOT = Path(__file__).parent
TASKS = load_tasks(ROOT / "data" / "tasks.json")

st.set_page_config(page_title="BioVQA AI", page_icon="🧬", layout="wide")
st.title("BioVQA AI")
st.caption("Image-grounded biology questions | scientific reasoning | auditable answers")
st.info("Educational prototype. Diagrams are original schematics, not microscopy or published experimental evidence. Human subject-matter review is required for research-grade tasks.")

tab1, tab2, tab3, tab4 = st.tabs(["Practice", "Task Explorer", "Author & Validate", "Dataset Audit"])
with tab1:
    st.subheader("Visual reasoning practice")
    domains = ["All"] + sorted({t["subdomain"] for t in TASKS})
    chosen = st.selectbox("Subdomain", domains)
    filtered = [t for t in TASKS if chosen == "All" or t["subdomain"] == chosen]
    selected_id = st.selectbox("Task", [t["id"] for t in filtered])
    task = next(t for t in filtered if t["id"] == selected_id)
    left, right = st.columns([1.15, 1])
    with left:
        st.image(str(ROOT / task["image"]), use_container_width=True)
        with st.expander("Structured image description"):
            st.write(task["image_description"])
    with right:
        st.caption(f'{task["subdomain"]}  |  {task["difficulty"]}  |  {task["id"]}')
        st.markdown(f'**{task["question"]}**')
        picked = st.radio("Choose one", LETTERS, format_func=lambda x: f'{x}. {task["choices"][x]}',
                          index=None, key=f'choice-{task["id"]}')
        if st.button("Check answer", disabled=picked is None):
            result = evaluate_response(task, picked)
            st.session_state[f'result-{task["id"]}'] = result
        result = st.session_state.get(f'result-{task["id"]}')
        if result:
            if result["correct"]:
                st.success("Correct")
            else:
                st.error(f'Incorrect. Correct answer: {result["gold_answer"]}')
            st.write(result["explanation"])
            st.markdown("**Visible evidence**")
            for observation in result["visual_evidence"]:
                st.write(f'• {observation}')
with tab2:
    st.subheader("Curated task records")
    items = pd.DataFrame([{ "ID": t["id"], "Subdomain": t["subdomain"], "Difficulty": t["difficulty"],
                             "Learning objective": t["learning_objective"] } for t in TASKS])
    st.dataframe(items, use_container_width=True, hide_index=True)
    selected_record = st.selectbox("View JSON", [t["id"] for t in TASKS], key="json_record")
    st.json(next(t for t in TASKS if t["id"] == selected_record))
    st.download_button("Download sample dataset", data=json.dumps(TASKS, indent=2, ensure_ascii=False),
                       file_name="biovqa_tasks.json", mime="application/json")
with tab3:
    st.subheader("Draft a new image-grounded VQA task")
    st.caption("Draft locally. Preview validation and download the record. Review scientific correctness and image licensing before publication.")
    with st.form("author_form"):
        task_id = st.text_input("Task ID", value="BIO-NEW-001")
        domain = st.selectbox("Biology subdomain", sorted(DOMAINS))
        image = st.text_input("Image path within repository", value="assets/metaphase.svg")
        question = st.text_area("Question", height=90)
        options = [st.text_input(f"Option {letter}") for letter in LETTERS]
        correct = st.selectbox("Verified correct option", LETTERS)
        explanation = st.text_area("Mechanistic reasoning and limitations", height=110)
        desc = st.text_area("Image description: modality, structures, layout, quality, possible artifacts", height=130)
        evid1 = st.text_input("Visual observation 1")
        evid2 = st.text_input("Visual observation 2")
        provenance = st.text_input("Image source, author, rights, date or identifier")
        submit = st.form_submit_button("Validate draft")
    if submit:
        draft = dict(id=task_id,subdomain=domain,image=image,question=question,choices=dict(zip(LETTERS, options)),
                     answer=correct,explanation=explanation,image_description=desc,visual_evidence=[evid1,evid2],
                     image_provenance=provenance,difficulty="Intermediate",learning_objective="Author review required")
        errors = validate_task(draft, ROOT)
        if errors:
            st.error("Draft needs changes:")
            for err in errors: st.write(f'• {err}')
        else:
            st.success("Schema and asset validation passed. Scientific validity still requires expert review.")
            st.download_button("Download task JSON", json.dumps(draft, indent=2, ensure_ascii=False),
                               file_name=f"{task_id}.json", mime="application/json")
with tab4:
    st.subheader("Quality control")
    summary = dataset_summary(TASKS)
    col1, col2 = st.columns(2)
    col1.metric("Curated examples", summary["tasks"])
    col2.metric("Covered subdomains", len(summary["domains"]))
    st.bar_chart(pd.Series(summary["domains"], name="Task count"))
    st.write("Correct-choice distribution", summary["answer_distribution"])
    errors = validate_dataset(TASKS, ROOT)
    if errors: st.error(errors)
    else: st.success("All sample tasks pass structural checks, ID checks, and image-path checks.")
    st.caption("This audit checks structure, not domain-expert correctness, experimental validity, or dataset independence.")
