from biovqa.study import create_flashcards


def test_cards_trace_to_exact_source_sentences():
    notes = "Mitochondria make much of the ATP in many eukaryotic cells. Transcription copies DNA information into an RNA molecule."
    cards = create_flashcards(notes)
    assert len(cards) == 2
    for card in cards:
        assert card["source_sentence"] in notes
        assert "_____" in card["prompt"]
        assert card["answer"].casefold() in card["source_sentence"].casefold()


def test_nonbiology_and_duplicate_sentences_are_ignored():
    notes = "This sentence contains enough words but not one of the target terms.\n" + "Ribosome molecules participate in the process of building protein chains.\n" * 2
    cards = create_flashcards(notes)
    assert len(cards) == 1
    assert cards[0]["answer"].casefold() == "ribosome"


def test_limits_and_invalid_inputs():
    notes = "Meiosis reduces ploidy through successive nuclear divisions.\n" * 5
    assert len(create_flashcards(notes, limit=1)) == 1
    assert create_flashcards(None) == []
    assert create_flashcards(notes, limit=0) == []
