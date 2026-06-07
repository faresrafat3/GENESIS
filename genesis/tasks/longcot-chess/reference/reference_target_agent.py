#!/usr/bin/env python3
"""
Reference target agent to run OpenAI-compatible inference on chess hard questions.
Uses OpenAI compatible gateway (like openGateway).
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List
import openai


def setup_openai_client(api_key: str, base_url: str):
    """Initialize OpenAI client."""
    return openai.OpenAI(api_key=api_key, base_url=base_url)


def load_chess_hard_questions(dataset_dir: Path) -> List[Dict[str, Any]]:
    """Load chess hard questions from chess_hard.json."""
    chess_hard_path = dataset_dir / "chess_hard.json"

    if not chess_hard_path.exists():
        raise FileNotFoundError(f"Chess hard questions not found at {chess_hard_path}")

    with open(chess_hard_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    if not questions:
        raise ValueError("No questions found in chess_hard.json")

    print(f"Loaded {len(questions)} questions from chess_hard.json")
    return questions


def extract_solution(response: str):
    """Extract solution from model response.

    Handles formats like:
    - solution = ["c4", "bxc4", "bxc4"]
    - solution = 218
    """
    if not response:
        return None

    import re

    # Look for solution = [...] or solution = <number>
    pattern = r'solution\s*=\s*(.+?)(?:\n|$)'
    match = re.search(pattern, response, re.IGNORECASE)

    if not match:
        return None

    solution_str = match.group(1).strip()

    # Try to parse as list
    if solution_str.startswith('['):
        try:
            solution_str = solution_str.replace("'", '"')
            parsed = json.loads(solution_str)
            return [str(x).strip() for x in parsed]
        except:
            items = re.findall(r'[\"\']?([^,\[\]\"\'\s]+)[\"\']?', solution_str)
            return [item.strip() for item in items if item.strip()]

    solution_str = solution_str.strip('"\'')
    try:
        return int(solution_str)
    except ValueError:
        return solution_str


def call_openai(client, model: str, prompt: str) -> Dict[str, Any]:
    """Call OpenAI API and return response with metadata."""
    try:
        start_time = time.time()

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )

        elapsed = time.time() - start_time
        content = response.choices[0].message.content or ""

        # Extract usage metadata
        usage = {}
        if response.usage:
            m = response.usage
            usage = {
                "prompt_tokens": getattr(m, "prompt_tokens", 0) or 0,
                "completion_tokens": getattr(m, "completion_tokens", 0) or 0,
                "total_tokens": getattr(m, "total_tokens", 0) or 0,
            }

        return {
            "success": True,
            "content": content,
            "usage": usage,
            "elapsed_seconds": elapsed,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "content": None,
            "usage": {},
            "elapsed_seconds": time.time() - start_time,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }


def run_inference(
    client,
    model: str,
    questions: List[Dict[str, Any]],
    working_dir: Path
):
    """Run inference on all questions and save results."""
    working_dir.mkdir(parents=True, exist_ok=True)
    results = []

    print(f"\nRunning inference on {len(questions)} questions...")
    print(f"Model: {model}")
    print(f"Output directory: {working_dir}\n")

    for idx, question in enumerate(questions, 1):
        question_id = question.get("question_id", f"unknown_{idx}")
        prompt = question.get("prompt", "")

        print(f"[{idx}/{len(questions)}] Processing {question_id}...", end=" ", flush=True)

        response = call_openai(client, model, prompt)

        solution = None
        if response["success"] and response["content"]:
            solution = extract_solution(response["content"])

        result = {
            "question_id": question_id,
            "prompt": prompt,
            "solution": solution,
            "model_response": response["content"],
            "success": response["success"],
            "usage": response["usage"],
            "elapsed_seconds": response["elapsed_seconds"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if response["error"]:
            result["error"] = response["error"]

        results.append(result)

        status = "✓" if response["success"] else "✗"
        print(f"{status} ({response['elapsed_seconds']:.1f}s)")

        time.sleep(0.5)

    responses_file = working_dir / "responses.json"
    with open(responses_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    summary_file = working_dir / "summary.json"
    summary = {
        "total_questions": len(questions),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "total_prompt_tokens": sum(r["usage"].get("prompt_tokens", 0) for r in results),
        "total_completion_tokens": sum(r["usage"].get("completion_tokens", 0) for r in results),
        "total_elapsed_seconds": sum(r["elapsed_seconds"] for r in results),
        "model": model,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total questions: {summary['total_questions']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Total tokens: {summary['total_prompt_tokens'] + summary['total_completion_tokens']}")
    print(f"  Total time: {summary['total_elapsed_seconds']:.1f}s")
    print(f"\nResults saved to: {working_dir}")
    print(f"  All responses: {responses_file}")
    print(f"  Summary: {summary_file}")
    print(f"{'='*60}")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Run OpenAI-compatible inference on chess hard questions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dataset_dir",
        type=Path,
        required=True,
        help="Directory containing chess_hard.json"
    )

    parser.add_argument(
        "--working_dir",
        type=Path,
        required=True,
        help="Directory to save results"
    )

    args = parser.parse_args()

    model = os.environ.get("TASK_MODEL") or "mimo-v2.5-pro"
    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE") or "https://opengateway.gitlawb.com/v1"

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY or LLM_API_KEY environment variable not set")
        return 1

    if not args.dataset_dir.exists():
        print(f"Error: Dataset directory does not exist: {args.dataset_dir}")
        return 1

    args.working_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f"Reference Target Agent - OpenAI Inference")
    print(f"{'='*60}")
    print(f"Dataset directory: {args.dataset_dir}")
    print(f"Working directory: {args.working_dir}")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"{'='*60}\n")

    client = setup_openai_client(api_key, base_url)
    questions = load_chess_hard_questions(args.dataset_dir)

    summary = run_inference(
        client,
        model,
        questions,
        args.working_dir
    )

    return 0


if __name__ == "__main__":
    exit(main())
