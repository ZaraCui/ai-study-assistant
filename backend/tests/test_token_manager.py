from rag.token_manager import estimate_tokens, truncate_chunks_by_tokens


def test_estimate_tokens_basic():
    s = "hello world"
    t = estimate_tokens(s)
    assert isinstance(t, int)
    assert t > 0


def test_truncate_chunks_by_tokens():
    # Create chunks with predictable sizes
    chunks = ["a" * 100, "b" * 200, "c" * 300]
    # Each chunk char-based tokens approx /4: so 25,50,75 tokens
    max_tokens = 60
    truncated = truncate_chunks_by_tokens(chunks, max_tokens)
    # Should include first (25) and second (50) would overflow, so only first
    assert len(truncated) >= 1
    assert truncated[0] == chunks[0]
