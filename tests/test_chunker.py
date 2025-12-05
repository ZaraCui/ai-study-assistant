from rag.chunker import chunk_text


def test_chunker_overlap_and_sizes():
    # create a text with 1100 words (words are 'w')
    words = ["w"] * 1100
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=500, overlap=50)
    # Expect at least 3 chunks: 500, then overlap shifts
    assert len(chunks) >= 3

    # Check that overlap exists between consecutive chunks
    first = chunks[0].split()
    second = chunks[1].split()
    # The last 50 words of first should equal the first 50 of second
    assert first[-50:] == second[:50]
