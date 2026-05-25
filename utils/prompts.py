from typing import Dict

SUMMARY_STYLE_OPTIONS = {
    "1": "Short Summary",
    "2": "Detailed Summary",
    "3": "Bullet Point Summary",
    "4": "Key Insights",
    "5": "Beginner Friendly Explanation",
}

DOCUMENT_STYLE_OPTIONS = {
    "1": "Technical Document",
    "2": "Academic Article",
    "3": "Business Report",
    "4": "General Content",
    "5": "Beginner Explanation",
}

SUMMARY_INSTRUCTIONS: Dict[str, str] = {
    "Short Summary": (
        "Create a concise summary that captures the main idea clearly and efficiently. "
        "Avoid unnecessary details and keep the summary easy to scan."
    ),
    "Detailed Summary": (
        "Create a full summary that preserves the main ideas, supporting points, and structure. "
        "Include enough context to understand the topic without being repetitive."
    ),
    "Bullet Point Summary": (
        "Create a set of clear bullet points highlighting the most important facts, conclusions, and actions. "
        "Each point should be brief and readable."
    ),
    "Key Insights": (
        "Extract the most meaningful insights, findings, and takeaways from the content. "
        "Focus on what a reader should remember."
    ),
    "Beginner Friendly Explanation": (
        "Explain the material in simple, everyday language that a beginner can understand. "
        "Use examples, analogies, and plain terms where possible."
    ),
}

DOCUMENT_CONTEXT: Dict[str, str] = {
    "Technical Document": (
        "This is a technical document. Use precise terminology, explain dependencies, and preserve the engineering context. "
        "The reader may have a technical background and expects accurate, practical insights."
    ),
    "Academic Article": (
        "This is an academic article. Respect the structure of research, include the key arguments, and keep the summary objective. "
        "Emphasize methodology, results, and conclusions."
    ),
    "Business Report": (
        "This is a business report. Highlight strategy, outcomes, and recommendations. "
        "Focus on what business leaders need to know."
    ),
    "General Content": (
        "This is general content. Keep it accessible, contextual, and easy for a broad audience to read. "
        "Emphasize clarity and readability."
    ),
    "Beginner Explanation": (
        "This content should be explained for beginners. Use everyday language and avoid jargon unless it is defined clearly. "
        "Focus on teaching the underlying ideas."
    ),
}


def build_summary_prompt(
    content: str,
    summary_style: str,
    document_style: str,
    title: str = "",
    is_final: bool = False,
) -> str:
    summary_instruction = SUMMARY_INSTRUCTIONS.get(
        summary_style,
        "Summarize the content accurately and clearly.",
    )
    document_instruction = DOCUMENT_CONTEXT.get(
        document_style,
        "Summarize the content accurately and clearly.",
    )
    title_section = f"Title: {title}\n" if title else ""
    combine_instruction = (
        "If this content is already a partial summary, combine it into a single coherent summary "
        "that preserves the original meaning and style."
        if is_final
        else ""
    )

    prompt = (
        f"You are an expert content summarizer. {document_instruction}\n"
        f"Use a non-repetitive, context-aware, and human-readable voice. {summary_instruction}\n"
        f"{combine_instruction}\n"
        f"{title_section}"
        "Content:\n"
        f"{content.strip()}"
    )
    return prompt
