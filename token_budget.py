"""
Token budgeting and priority-based context truncation.

Goal: every /chat and /chat/stream request stays under a configured token ceiling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration – tweak these numbers later if needed
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BudgetConfig:
    # Total input tokens we are willing to send to the model
    max_input_tokens: int = 12_000

    # How many tokens we reserve for the model's answer
    max_output_tokens: int = 2_048

    # Minimum tokens we always keep for the core system prompt
    min_system_tokens: int = 1_500


# Different budgets per intent (can be expanded later)
INTENT_BUDGETS: dict[str, BudgetConfig] = {
    "fiqh": BudgetConfig(max_input_tokens=11_000, max_output_tokens=2_048),
    "tafsir": BudgetConfig(max_input_tokens=13_000, max_output_tokens=2_500),
    "zakat": BudgetConfig(max_input_tokens=10_000, max_output_tokens=1_800),
    "general": BudgetConfig(max_input_tokens=12_000, max_output_tokens=2_048),
}


# ---------------------------------------------------------------------------
# Simple token estimator (replace with tiktoken / real counter later)
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Very rough estimate: \~4 characters per token."""
    if not text:
        return 0
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Priority-ordered truncation
# ---------------------------------------------------------------------------

def truncate_to_budget(
    *,
    system_core: str,
    tafsir_block: str = "",
    zakat_block: str = "",
    fiqh_block: str = "",
    purchase_block: str = "",
    memory_block: str = "",
    extra_context: str = "",
    user_question: str = "",
    intent: str = "general",
) -> tuple[str, int]:
    """
    Assemble the final system context while respecting the token budget.

    Returns:
        (final_system_context, max_output_tokens)
    """
    cfg = INTENT_BUDGETS.get(intent, INTENT_BUDGETS["general"])

    # Priority order (highest → lowest)
    # 1. Core system instructions (never drop)
    # 2. User question (never drop)
    # 3. Memory / user profile
    # 4. Fiqh / Madhhab
    # 5. Zakat
    # 6. Tafsir
    # 7. Purchase / other extra context

    pieces = [
        ("core", system_core),
        ("memory", memory_block),
        ("fiqh", fiqh_block),
        ("zakat", zakat_block),
        ("tafsir", tafsir_block),
        ("purchase", purchase_block),
        ("extra", extra_context),
    ]

    # Always keep the user question in the budget calculation
    question_tokens = estimate_tokens(user_question)
    remaining = cfg.max_input_tokens - question_tokens

    final_parts: list[str] = []

    for name, text in pieces:
        if not text:
            continue

        tokens = estimate_tokens(text)

        if tokens <= remaining:
            final_parts.append(text)
            remaining -= tokens
        else:
            # Truncate this piece to whatever is left
            if remaining > 200:  # only keep if we have a meaningful amount
                # Keep the beginning (usually the most important)
                char_limit = remaining * 4
                truncated = text[:char_limit].rsplit(" ", 1)[0] + "…"
                final_parts.append(truncated)
            # After truncation we stop adding lower-priority pieces
            break

    final_context = "\n\n".join(final_parts)
    return final_context, cfg.max_output_tokens


# ---------------------------------------------------------------------------
# Convenience helper used by main.py
# ---------------------------------------------------------------------------

def build_budgeted_prompt(
    *,
    islamic_context: str,
    hadith_adab: str,
    citation_block: str,
    fiqh_context: str = "",
    madhhab_instruction: str = "",
    tafsir_block: str = "",
    zakat_block: str = "",
    purchase_block: str = "",
    memory_block: str = "",
    extra_context: str = "",
    user_question: str = "",
    intent: str = "general",
) -> tuple[str, int]:
    """
    High-level helper that main.py will call.

    Returns:
        (full_prompt, max_output_tokens)
    """
    system_core = islamic_context + hadith_adab + citation_block

    if fiqh_context:
        system_core += fiqh_context
    if madhhab_instruction:
        system_core += madhhab_instruction

    budgeted_system, max_out = truncate_to_budget(
        system_core=system_core,
        tafsir_block=tafsir_block,
        zakat_block=zakat_block,
        purchase_block=purchase_block,
        memory_block=memory_block,
        extra_context=extra_context,
        user_question=user_question,
        intent=intent,
    )

    full_prompt = f"{budgeted_system}\n\nUser question: {user_question}"
    return full_prompt, max_out
