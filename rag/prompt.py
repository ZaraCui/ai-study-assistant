def build_prompt(question, context):
    joined = "\n\n---\n\n".join(context)
    return f"""
You are a helpful study assistant.

Use ONLY the following notes to answer the question.
If the answer is not found, say: "The notes do not contain this information."

Notes:
{joined}

Question: {question}

Answer:
"""
