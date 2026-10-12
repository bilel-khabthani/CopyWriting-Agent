"""Phase 1 + 3: the two-agent pipeline (now format-aware).

Chains Agent 1 (Strategist, JSON) and Agent 2 (Writer, markdown), validates the
strategy, retries weak output, and automatically falls back to a secondary model
when the primary one fails.

The pipeline is UI-agnostic: it reports progress through an optional callback so
the Telegram bot can show status messages.

Backward compatibility
----------------------
``run_pipeline(brief)`` still runs the original video-ad flow. The generic
entry point is ``run_for_format(format_key, brief)``; every supported format is
listed in :mod:`formats`.
"""

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import config
from formats import FORMAT_VIDEO_AD, get_format
from ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaError,
)
from prompts import normalize_brief, validate_strategy
from prompts_formats import (
    build_strategist_messages,
    build_writer_messages,
)

ProgressFn = Optional[Callable[[str], None]]


class PipelineError(Exception):
    """Raised when the pipeline cannot produce a deliverable."""


@dataclass
class Result:
    brief: dict
    strategy: dict
    script: str
    strategist_model: str
    scriptwriter_model: str
    strategy_attempts: int
    used_fallback: bool
    seconds: float
    notes: List[str] = field(default_factory=list)
    format: str = FORMAT_VIDEO_AD


def _model_chain() -> List[str]:
    """Primary model first, then the fallback, without duplicates."""
    ordered = [config.MODEL, config.FALLBACK_MODEL]
    seen = []
    for model in ordered:
        if model and model not in seen:
            seen.append(model)
    return seen


def _emit(on_progress: ProgressFn, message: str) -> None:
    if on_progress:
        try:
            on_progress(message)
        except Exception:
            pass


def _generate_strategy(
    client: OllamaClient, brief: dict, format_key: str, on_progress: ProgressFn
):
    """Run Agent 1 with retries and model fallback. Returns (strategy, model, attempts)."""
    chain = _model_chain()
    attempts = 0
    last_error = None

    for model in chain:
        for _ in range(2):
            attempts += 1
            try:
                strategy = client.chat_json(
                    build_strategist_messages(brief, format_key),
                    temperature=config.STRATEGIST_TEMPERATURE,
                    model=model,
                )
            except OllamaConnectionError:
                raise
            except OllamaError as exc:
                last_error = exc
                continue

            problems = validate_strategy(strategy)
            if not problems:
                return strategy, model, attempts
            last_error = OllamaError(
                "Invalid strategy from {0}: {1}".format(model, "; ".join(problems))
            )

    raise PipelineError(
        "Could not build a valid strategy. Last error: {0}".format(last_error)
    )


def _generate_script(
    client: OllamaClient,
    brief: dict,
    strategy: dict,
    format_key: str,
    on_progress: ProgressFn,
):
    """Run Agent 2 with model fallback. Returns (script, model)."""
    chain = _model_chain()
    last_error = None

    for model in chain:
        try:
            script = client.chat(
                build_writer_messages(brief, strategy, format_key),
                temperature=config.WRITER_TEMPERATURE,
                num_predict=1400,
                model=model,
            )
            return script, model
        except OllamaConnectionError:
            raise
        except OllamaError as exc:
            last_error = exc
            continue

    raise PipelineError(
        "Could not write the deliverable. Last error: {0}".format(last_error)
    )


def run_for_format(
    format_key: str, brief: dict, on_progress: ProgressFn = None
) -> Result:
    """Run the full two-agent pipeline for a given format and return a Result."""
    meta = get_format(format_key)
    if meta is None:
        raise ValueError("Unknown format: {0}".format(format_key))
    format_key = meta["key"]

    started = time.perf_counter()
    clean_brief = normalize_brief(brief)
    notes: List[str] = []

    client = OllamaClient()
    try:
        _emit(on_progress, "Agent 1/2 - Analyzing audience and psychology...")
        strategy, strat_model, attempts = _generate_strategy(
            client, clean_brief, format_key, on_progress
        )
        if attempts > 1:
            notes.append("Strategy needed {0} attempts.".format(attempts))

        _emit(
            on_progress,
            "Agent 2/2 - Writing the {0}...".format(meta["name"]),
        )
        script, writer_model = _generate_script(
            client, clean_brief, strategy, format_key, on_progress
        )
    finally:
        client.close()

    used_fallback = (
        strat_model != config.MODEL or writer_model != config.MODEL
    )
    if used_fallback:
        notes.append(
            "Used fallback model for: {0}".format(
                ", ".join(
                    m
                    for m, name in (
                        (strat_model, "strategist"),
                        (writer_model, "scriptwriter"),
                    )
                    if m != config.MODEL
                )
            )
        )

    return Result(
        brief=clean_brief,
        strategy=strategy,
        script=script,
        strategist_model=strat_model,
        scriptwriter_model=writer_model,
        strategy_attempts=attempts,
        used_fallback=used_fallback,
        seconds=round(time.perf_counter() - started, 2),
        notes=notes,
        format=format_key,
    )


def run_pipeline(brief: dict, on_progress: ProgressFn = None) -> Result:
    """Backward-compatible entry point: the original video-ad flow."""
    return run_for_format(FORMAT_VIDEO_AD, brief, on_progress=on_progress)


if __name__ == "__main__":
    import json

    sample = {
        "brand": "SleepGuard Pro",
        "product": "A smartwatch that tracks sleep and warns you before you get sick.",
        "audience": "health-conscious adults aged 25-40",
        "goal": "sell the product",
        "platform": "YouTube Shorts",
        "product_type": "physical product",
        "tone": "scientific but friendly",
    }

    format_key = FORMAT_VIDEO_AD

    print("Running pipeline ({0})...\n".format(format_key))
    result = run_for_format(
        format_key, sample, on_progress=lambda msg: print("[progress]", msg)
    )
    print("\n=== STRATEGY ===")
    print(json.dumps(result.strategy, indent=2, ensure_ascii=False))
    print("\n=== DELIVERABLE ===")
    print(result.script)
    print("\n--- meta ---")
    print("format            :", result.format)
    print("strategist model  :", result.strategist_model)
    print("scriptwriter model:", result.scriptwriter_model)
    print("strategy attempts :", result.strategy_attempts)
    print("used fallback     :", result.used_fallback)
    print("seconds           :", result.seconds)
    print("notes             :", result.notes)
