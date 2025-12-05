"""
Token management utilities for LLM prompt handling.
Uses a simple heuristic: 1 token ≈ 4 characters.
For production use, consider using tiktoken or openai.util.get_encoding.
"""

import logging

logger = logging.getLogger(__name__)

# Conservative estimate: 1 token ≈ 4 characters
# For more accurate counting, use: `pip install tiktoken`
CHARS_PER_TOKEN = 4

# Token limits for different models
TOKEN_LIMITS = {
    "gpt-4o-mini": 128000,
    "gpt-4o": 128000,
    "gpt-4-turbo": 128000,
    "gpt-3.5-turbo": 4096,
}

# Reserve tokens for system message + answer generation
RESERVED_TOKENS = 500


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text using simple heuristic.
    
    Args:
        text: The text to estimate tokens for.
    
    Returns:
        Estimated token count.
    """
    # Simple heuristic: count words and characters
    # More accurate would be to use tiktoken
    word_count = len(text.split())
    char_count = len(text)
    
    # Use average of word-based and character-based estimates
    # Word-based: ~1.3 tokens per word
    # Char-based: ~1 token per 4 characters
    token_estimate_word = int(word_count * 1.3)
    token_estimate_char = int(char_count / CHARS_PER_TOKEN)
    
    # Use the higher estimate to be conservative
    return max(token_estimate_word, token_estimate_char)


def get_token_limit(model: str) -> int:
    """
    Get the maximum token limit for a model.
    
    Args:
        model: Model name (e.g., "gpt-4o-mini").
    
    Returns:
        Maximum token count for the model.
    """
    return TOKEN_LIMITS.get(model, 4096)


def truncate_chunks_by_tokens(
    chunks: list,
    max_tokens: int,
    preserve_order: bool = True
) -> list:
    """
    Truncate a list of text chunks to fit within a token limit.
    
    Keeps adding chunks until reaching the limit, then stops.
    This preserves the most relevant (earliest) chunks while removing later ones.
    
    Args:
        chunks: List of text chunks to truncate.
        max_tokens: Maximum number of tokens allowed.
        preserve_order: If True, keep chunks in original order.
    
    Returns:
        Truncated list of chunks that fit within the token limit.
    """
    if not chunks:
        return []
    
    selected_chunks = []
    total_tokens = 0
    
    for i, chunk in enumerate(chunks):
        chunk_tokens = estimate_tokens(chunk)
        
        if total_tokens + chunk_tokens <= max_tokens:
            selected_chunks.append(chunk)
            total_tokens += chunk_tokens
        else:
            logger.debug(
                f"Reached token limit after {i} chunks. "
                f"Total tokens: {total_tokens}/{max_tokens}"
            )
            break
    
    return selected_chunks


def is_prompt_safe(prompt: str, model: str) -> tuple[bool, dict]:
    """
    Check if a prompt is safe to send to an LLM API.
    
    Args:
        prompt: The full prompt text.
        model: Model name (e.g., "gpt-4o-mini").
    
    Returns:
        Tuple of (is_safe: bool, info: dict with token count and limit).
    """
    token_limit = get_token_limit(model)
    estimated_tokens = estimate_tokens(prompt)
    
    # Reserve tokens for response generation
    available_tokens = token_limit - RESERVED_TOKENS
    is_safe = estimated_tokens <= available_tokens
    
    info = {
        "estimated_tokens": estimated_tokens,
        "token_limit": token_limit,
        "reserved_tokens": RESERVED_TOKENS,
        "available_tokens": available_tokens,
        "is_safe": is_safe,
    }
    
    if not is_safe:
        logger.warning(
            f"Prompt may exceed token limit for {model}: "
            f"{estimated_tokens} tokens > {available_tokens} available tokens"
        )
    
    return is_safe, info
