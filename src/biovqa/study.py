"""Deterministic, source-grounded flashcards for pasted biology notes.

No notes are sent to external services. This does not claim to be a generative model.
"""
from __future__ import annotations

import re

BIOLOGY_TERMS = (
    "mitochondria", "ribosome", "transcription", "translation", "replication",
    "chromosome", "chromatid", "cytokinesis", "mitosis", "meiosis",
    "mutation", "allele", "enzyme", "substrate", "immunity", "antibody",
    "neuron", "synapse", "homeostasis", "diffusion", "osmosis",
    "nucleus", "photosynthesis", "glycolysis", "membrane", "ATP",
)


def create_flashcards(notes: str, *, limit: int = 30) -> list[dict[str, str]]:
    """Create cloze cards only when an exact biology term occurs in a source sentence."""
    if not isinstance(notes, str) or limit < 1:
        return []
    sentences = re.split(r"(?<=[.!?])\s+|\n+", notes.strip())
    cards = []
    seen = set()
    for raw in sentences:
        sentence = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", raw).strip()
        if len(sentence) < 32 or sentence.casefold() in seen:
            continue
        for term in BIOLOGY_TERMS:
            match = re.search(rf"\b{re.escape(term)}\b", sentence, flags=re.IGNORECASE)
            if match:
                answer = match.group(0)
                cloze = sentence[:match.start()] + "_____" + sentence[match.end():]
                if cloze == sentence:
                    continue
                cards.append({"prompt": cloze, "answer": answer, "source_sentence": sentence})
                seen.add(sentence.casefold())
                break
        if len(cards) >= limit:
            break
    return cards
