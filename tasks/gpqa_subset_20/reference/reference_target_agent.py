#!/usr/bin/env python3
"""
OpenAI-compatible Agent on diamond_questions.json → generates submission JSON with model answers.
Uses OpenAI compatible gateway (like openGateway).
"""

import argparse
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

import httpx
import openai
from tqdm.asyncio import tqdm as async_tqdm


# -----------------------------------------------------------------------------
# Configuration — model, labels, concurrency
# -----------------------------------------------------------------------------
MODEL_NAME = os.getenv("TASK_MODEL") or "mimo-v2.5-pro"
DATASET_LABEL = "diamond_qna"
CONCURRENCY = 2


# -----------------------------------------------------------------------------
# Cost & API client
# -----------------------------------------------------------------------------
def setup_openai() -> openai.OpenAI:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY or LLM_API_KEY.")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE") or "https://opengateway.gitlawb.com/v1"
    http_client = httpx.Client(headers={"Accept-Encoding": "identity"}, timeout=120.0)
    return openai.OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)


# -----------------------------------------------------------------------------
# Prompt building & model response parsing
# -----------------------------------------------------------------------------
def format_question(example: dict) -> str:
    """
    Format a question with answer options.
    """
    question_text = example["Question"]
    options = example["options"]

    prompt = (
        f"Answer this multiple choice question.\n\n{question_text}\n\n"
        f"A) {options['A']}\nB) {options['B']}\nC) {options['C']}\nD) {options['D']}\n\n"
        f'Respond with JSON only: {{"answer": "A"}} (value is A, B, C, or D).'
    )

    return prompt


# -----------------------------------------------------------------------------
# Inference — one question (OpenAI call) and full run with concurrency
# -----------------------------------------------------------------------------
async def get_answer_async(
    index: int,
    example: dict,
    client: openai.OpenAI,
    semaphore: asyncio.Semaphore,
) -> dict:
    """
    Get model answer for a single question.
    """
    question_id = example.get("id", index)
    async with semaphore:
        try:
            prompt = format_question(example)
            response, model_answer_raw, model_answer = None, "", ""
            for attempt in range(3):
                try:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        lambda: client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.0,
                            response_format={"type": "json_object"}
                        ),
                    )
                    model_answer_raw = (response.choices[0].message.content or "").strip()
                    if not model_answer_raw:
                        raise ValueError("empty model response")
                    
                    try:
                        ans_dict = json.loads(model_answer_raw)
                        model_answer = str(ans_dict.get("answer", "")).strip().upper()
                    except json.JSONDecodeError:
                        model_answer = ""

                    if model_answer not in "ABCD":
                        # Fallback parsing
                        model_answer = next((letter for letter in "ABCD" if letter in model_answer_raw.upper()), "")

                    if model_answer not in "ABCD":
                        raise ValueError(f"answer must be A–D, got: {model_answer_raw[:120]!r}")
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2**attempt)
            
            usage = response.usage
            input_tokens = getattr(usage, "prompt_tokens", None) or 0
            output_tokens = getattr(usage, "completion_tokens", None) or 0
            return {
                "success": True,
                "question_id": question_id,
                "model_answer": model_answer,
                "model_answer_raw": model_answer_raw,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "reasoning_tokens": 0,
                "cost_usd": 0.0,
            }
        except Exception as exc:
            return {"success": False, "question_id": question_id, "error": str(exc)}


async def get_all_answers_async(
    questions: list, client: openai.OpenAI, concurrency: int
) -> list:
    """Run inference on all questions concurrently."""
    semaphore = asyncio.Semaphore(max(1, concurrency))
    tasks = [
        get_answer_async(index, example, client, semaphore)
        for index, example in enumerate(questions)
    ]
    return await async_tqdm.gather(*tasks, desc="Getting answers")


# -----------------------------------------------------------------------------
# Results — merge per-question rows into summary dict + write JSON
# -----------------------------------------------------------------------------
def build_results(questions: list, question_results: list) -> dict:
    results = {
        "model": MODEL_NAME,
        "dataset_config": DATASET_LABEL,
        "total_questions": len(questions),
        "errors": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_reasoning_tokens": 0,
        "total_cost_usd": 0.0,
        "details": [],
        "timestamp": datetime.now().isoformat(),
    }

    detail_keys = (
        "question_id",
        "model_answer",
        "model_answer_raw",
        "input_tokens",
        "output_tokens",
        "reasoning_tokens",
        "cost_usd",
    )

    for question_result in question_results:
        if question_result.get("success"):
            results["total_input_tokens"] += question_result["input_tokens"]
            results["total_output_tokens"] += question_result["output_tokens"]
            results["total_reasoning_tokens"] += question_result["reasoning_tokens"]
            results["total_cost_usd"] += question_result["cost_usd"]
            results["details"].append({key: question_result[key] for key in detail_keys})
        else:
            results["errors"] += 1
            results["details"].append(
                {"question_id": question_result["question_id"], "error": question_result["error"]}
            )
            print(f"Error on question {question_result['question_id']}: {question_result['error']}")

    return results


# -----------------------------------------------------------------------------
# Entry — load data, get answers, persist, print summary
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="GPQA OpenAI Agent - Generate model predictions")
    parser.add_argument(
        "--dataset_dir",
        type=Path,
        required=True,
        help="Path to dataset directory containing diamond_questions.json"
    )
    parser.add_argument(
        "--working_dir",
        type=Path,
        required=True,
        help="Working directory where results/ will be created"
    )
    args = parser.parse_args()

    data_file = args.dataset_dir / "diamond_questions.json"
    output_dir = args.working_dir / "results"

    if not data_file.is_file():
        raise SystemExit(f"Missing data file: {data_file}")

    questions = json.loads(data_file.read_text(encoding="utf-8"))

    client = setup_openai()
    question_results = asyncio.run(get_all_answers_async(questions, client, CONCURRENCY))
    results = build_results(questions, question_results)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{MODEL_NAME.replace('/', '_')}_{DATASET_LABEL}_{timestamp}.json"
    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    total_tokens = (
        results["total_input_tokens"] + results["total_output_tokens"] + results["total_reasoning_tokens"]
    )
    answered = results["total_questions"] - results["errors"]
    print(
        f"{answered}/{len(questions)} answered | "
        f"cost ${results['total_cost_usd']:.4f} | tokens {total_tokens} | saved {output_file}"
    )


if __name__ == "__main__":
    main()
