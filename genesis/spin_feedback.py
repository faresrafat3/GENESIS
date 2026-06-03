#!/usr/bin/env python3
"""
GENESIS SPIN Semantic Gap Feedback — Phase 3: Self-Play Iterative Refinement
Inspired by DeepSeek AI's "SPIN-OFF" (June 2026)

Uses semantic distance between strong (best-of-N) and weak (single sample) 
LLM outputs as a self-training signal — no external reward model needed.

Core insight (from the paper): The model generates TWO versions of each answer:
  1. STRONG: best-of-N sampling (multiple attempts, pick best)
  2. WEAK: single greedy sample
  
The semantic cosine distance between these two is the learning signal.
Larger gap → more room for improvement → higher priority for retraining.
"""

from __future__ import annotations

import json
import os
import sys
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import numpy as np


# ── Semantic Distance Calculator ───────────────────────────────────────────

@dataclass
class GapReport:
    """Report on semantic gap between strong and weak outputs."""
    task_text: str
    strong_output: str
    weak_output: str
    cosine_distance: float
    improvement_priority: float  # 0.0-1.0, higher = needs more work
    gap_category: str  # "small" (<0.2), "medium" (0.2-0.5), "large" (>0.5)
    details: str = ""


def simple_text_vectorize(text: str, dim: int = 256) -> np.ndarray:
    """
    Simple bag-of-trigrams vectorization for semantic distance.
    
    For production, replace with sentence-transformers or API embeddings.
    This is a lightweight heuristic that works without GPU.
    """
    if not text:
        return np.zeros(dim)
    
    # Extract trigrams
    text_lower = text.lower()
    trigrams = {}
    for i in range(len(text_lower) - 2):
        tri = text_lower[i:i+3]
        trigrams[tri] = trigrams.get(tri, 0) + 1
    
    # Hash to fixed dimension
    vec = np.zeros(dim)
    for tri, count in trigrams.items():
        idx = hash(tri) % dim
        vec[idx] += count
    
    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    
    return vec


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine distance between two vectors (0=identical, 1=orthogonal)."""
    if a.shape != b.shape:
        # Pad/truncate to match
        max_dim = max(len(a), len(b))
        a_pad = np.zeros(max_dim)
        b_pad = np.zeros(max_dim)
        a_pad[:len(a)] = a
        b_pad[:len(b)] = b
        a, b = a_pad, b_pad
    
    similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)
    return 1.0 - max(-1.0, min(1.0, similarity))


def compute_semantic_gap(
    task_text: str,
    strong_output: str,
    weak_output: str,
) -> GapReport:
    """
    Compute the semantic gap between strong and weak outputs.
    
    Args:
        task_text: The original task/prompt
        strong_output: Best-of-N output (higher quality)
        weak_output: Single-sample output (lower quality)
    
    Returns:
        GapReport with distance and improvement priority
    """
    # Vectorize all texts
    task_vec = simple_text_vectorize(task_text)
    strong_vec = simple_text_vectorize(strong_output)
    weak_vec = simple_text_vectorize(weak_output)
    
    # Distance between strong and weak
    gap = cosine_distance(strong_vec, weak_vec)
    
    # Distance from task to strong (how well the best answer aligns with task)
    task_alignment = cosine_distance(task_vec, strong_vec)
    
    # Improvement priority = gap weighted by task misalignment
    # High priority when: (1) large gap AND (2) even the strong answer is far from ideal
    improvement_priority = min(1.0, (gap * 0.7 + task_alignment * 0.3))
    
    # Categorize
    if gap < 0.2:
        category = "small"
    elif gap < 0.5:
        category = "medium"
    else:
        category = "large"
    
    details = (
        f"Gap: {gap:.3f} ({category}) | "
        f"Task alignment: {task_alignment:.3f} | "
        f"Priority: {improvement_priority:.2f}"
    )
    
    return GapReport(
        task_text=task_text,
        strong_output=strong_output,
        weak_output=weak_output,
        cosine_distance=gap,
        improvement_priority=improvement_priority,
        gap_category=category,
        details=details,
    )


# ── SPIN Feedback Generator ────────────────────────────────────────────────

def generate_spin_feedback(
    current_agent_code: str,
    execution_results: Dict[str, Any],
    previous_gaps: List[GapReport] | None = None,
) -> str:
    """
    Generate SPIN-style feedback for the next generation.
    
    Identifies which parts of the agent code have the largest semantic gaps
    and produces targeted improvement suggestions.
    
    Args:
        current_agent_code: Current target_agent.py content
        execution_results: Results from agent execution
        previous_gaps: Gap reports from previous generations
    
    Returns:
        Feedback text for the feedback agent
    """
    feedback_parts = ["# SPIN Semantic Gap Analysis\n"]
    
    # Section 1: Current execution summary
    feedback_parts.append("## Execution Summary")
    if "error" in execution_results:
        feedback_parts.append(f"❌ Execution failed: {execution_results['error']}")
        feedback_parts.append("Focus on fixing the error first before optimizing.")
    else:
        feedback_parts.append(f"✅ Execution succeeded")
        if "family" in execution_results:
            feedback_parts.append(f"- Task family: {execution_results['family']}")
        if "tier_used" in execution_results:
            feedback_parts.append(f"- Reasoning tier: {execution_results['tier_used']}")
    
    # Section 2: Semantic gap analysis
    feedback_parts.append("\n## Semantic Gap Analysis")
    
    if previous_gaps:
        feedback_parts.append("| Task | Gap | Category | Priority |")
        feedback_parts.append("|------|-----|----------|----------|")
        for i, gap in enumerate(previous_gaps):
            emoji = {"small": "🟢", "medium": "🟡", "large": "🔴"}.get(gap.gap_category, "⚪")
            feedback_parts.append(
                f"| Task {i+1} | {gap.cosine_distance:.3f} | {emoji} {gap.gap_category} | {gap.improvement_priority:.2f} |"
            )
        
        # Find highest priority tasks
        high_priority = [g for g in previous_gaps if g.improvement_priority > 0.5]
        if high_priority:
            feedback_parts.append(f"\n⚠️ {len(high_priority)} tasks have HIGH improvement priority:")
            for g in high_priority[:3]:
                feedback_parts.append(f"  - Priority {g.improvement_priority:.2f}: {g.gap_category} gap")
        
        # Trend analysis
        if len(previous_gaps) >= 2:
            trend = previous_gaps[-1].cosine_distance - previous_gaps[-2].cosine_distance
            if trend < -0.05:
                feedback_parts.append(f"\n📈 Positive trend: gap decreased by {abs(trend):.3f}")
            elif trend > 0.05:
                feedback_parts.append(f"\n📉 Negative trend: gap increased by {trend:.3f} — needs attention")
            else:
                feedback_parts.append(f"\n➡️ Stable trend: gap change of {trend:.3f}")
    else:
        feedback_parts.append("No semantic gap data from previous generations.")
        feedback_parts.append("Next generation should collect gap data by comparing strong/weak outputs.")
    
    # Section 3: Code-level improvement suggestions
    feedback_parts.append("\n## Suggested Improvements")
    
    # Check for common issues
    suggestions = []
    
    if "TODO" in current_agent_code or "FIXME" in current_agent_code:
        suggestions.append("🔧 Fix all TODO/FIXME placeholders — they indicate incomplete reasoning")
    
    if "except Exception" in current_agent_code and "traceback" not in current_agent_code.lower():
        suggestions.append("🔧 Add better error tracing — bare 'except Exception' hides failures")
    
    if "pass" in current_agent_code and "# placeholder" in current_agent_code:
        suggestions.append("🔧 Fill all placeholder implementations")
    
    if "sleep(" in current_agent_code or "time.sleep" in current_agent_code:
        suggestions.append("⚡ Remove unnecessary sleep() calls — they waste tokens and time")
    
    if not suggestions:
        suggestions.append("✅ No obvious code issues found — focus on semantic gap reduction")
    
    for s in suggestions:
        feedback_parts.append(f"- {s}")
    
    # Section 4: SPIN training guidance
    feedback_parts.append("\n## SPIN Training Guidance")
    feedback_parts.append(
        "For each task where the semantic gap is large:\n"
        "1. Generate a STRONG answer (best-of-3 sampling with temperature=0.7)\n"
        "2. Generate a WEAK answer (single sample with temperature=0)\n"
        "3. Compute the cosine distance between their vector representations\n"
        "4. If distance > 0.3: flag for retraining — the model hasn't learned this pattern yet\n"
        "5. If distance < 0.1: the model has converged — move to harder tasks\n"
        "\n"
        "Target: reduce average semantic gap below 0.15 across all tasks."
    )
    
    return "\n".join(feedback_parts)


# ── SPIN Loop Runner ───────────────────────────────────────────────────────

async def run_spin_loop(
    task_texts: List[str],
    agent_fn,
    num_iterations: int = 3,
    gap_threshold: float = 0.15,
) -> Dict[str, Any]:
    """
    Run the SPIN self-play loop across multiple iterations.
    
    Args:
        task_texts: List of task texts to process
        agent_fn: Async function that takes (task_text, temperature) -> output
        num_iterations: Number of SPIN iterations
        gap_threshold: Stop early if average gap falls below this
    
    Returns:
        Results dict with gaps, improvements, and convergence info
    """
    all_gaps: List[GapReport] = []
    avg_gaps: List[float] = []
    
    iteration = 0
    for iteration in range(num_iterations):
        iteration_gaps: List[GapReport] = []
        
        for task_text in task_texts:
            # Generate strong answer (best-of-3 with variety)
            candidates = []
            for _ in range(3):
                try:
                    output = await agent_fn(task_text, temperature=0.7)
                    candidates.append(output)
                except Exception:
                    pass
            
            strong_output = max(candidates, key=len) if candidates else ""
            
            # Generate weak answer (single greedy sample)
            try:
                weak_output = await agent_fn(task_text, temperature=0.0)
            except Exception:
                weak_output = ""
            
            # Compute gap
            if strong_output and weak_output:
                gap = compute_semantic_gap(task_text, strong_output, weak_output)
                iteration_gaps.append(gap)
                all_gaps.append(gap)
        
        if iteration_gaps:
            avg_gap = sum(g.cosine_distance for g in iteration_gaps) / len(iteration_gaps)
            avg_gaps.append(avg_gap)
            
            # Check convergence
            if avg_gap < gap_threshold:
                break
    
    # Compile results
    return {
        "total_iterations": iteration + 1,
        "total_gaps_computed": len(all_gaps),
        "final_avg_gap": avg_gaps[-1] if avg_gaps else None,
        "converged": avg_gaps[-1] < gap_threshold if avg_gaps else False,
        "gap_trend": avg_gaps,
        "high_priority_count": sum(1 for g in all_gaps if g.improvement_priority > 0.5),
        "gap_reports": [{
            "task": g.task_text[:200],
            "distance": g.cosine_distance,
            "category": g.gap_category,
            "priority": g.improvement_priority,
        } for g in all_gaps],
    }


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick demo
    strong = "The Virtual GENESIS cognitive pipeline successfully classified the task as a synthesis problem and applied tier-2 reasoning with concept activation from memory."
    weak = "Task classified. Used tier-2. Response generated."
    task = "Bridge the gap between cognitive pipeline and LLM reasoning"
    
    report = compute_semantic_gap(task, strong, weak)
    print(json.dumps({
        "distance": report.cosine_distance,
        "category": report.gap_category,
        "priority": report.improvement_priority,
        "details": report.details,
    }, indent=2))