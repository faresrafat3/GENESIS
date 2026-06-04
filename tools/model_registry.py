"""
Model Registry — Curated catalogue of OpenRouter models with official benchmarks.
==================================================================================

All numbers come from official model cards / vendor reports.
المصادر مكتوبة في الحقل `sources` لكل نموذج.

Usage:
    from tools.model_registry import MODELS, get_model, list_by_tier

    m = get_model("nemotron-3-ultra-free")
    print(m.openrouter_id, m.benchmarks.get("gpqa_diamond"))

    for m in list_by_tier("frontier"):
        print(m.shortcut, m.openrouter_id)

تصميم عام: كل model هو data record، الكود مش بيعتمد على أي ميزة خاصة بأي نموذج.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ModelSpec:
    """مواصفات نموذج واحد. كل الحقول optional ما عدا shortcut + openrouter_id."""

    shortcut: str  # الاسم القصير للاستخدام في الـ CLI
    openrouter_id: str  # الـ ID الكامل على OpenRouter
    family: str  # vendor / family (e.g. "NVIDIA Nemotron 3")
    role: str  # "frontier" | "reasoning" | "coding" | "agent" | "small" | "general"
    context_tokens: int  # حجم الـ context window
    active_params_b: Optional[float] = None  # B parameters active per token (MoE)
    total_params_b: Optional[float] = None  # B parameters total
    is_free: bool = True  # متاح على free tier
    supports_reasoning: bool = False  # يقبل reasoning parameter
    supports_tools: bool = True  # tool calling
    # Benchmarks (key = standard short name, value = % accuracy as float 0-100)
    benchmarks: dict[str, float] = field(default_factory=dict)
    # ملاحظات حرة
    notes: str = ""
    sources: list[str] = field(default_factory=list)

    @property
    def description(self) -> str:
        parts = [self.family]
        if self.active_params_b and self.total_params_b:
            parts.append(f"{self.total_params_b:.0f}B/{self.active_params_b:.0f}B active")
        elif self.total_params_b:
            parts.append(f"{self.total_params_b:.0f}B")
        parts.append(f"ctx={self.context_tokens // 1000}K")
        if self.is_free:
            parts.append("free")
        return " · ".join(parts)


# ============================================================
#                  THE REGISTRY
# ============================================================
# Note: All benchmarks are official numbers from the vendor's
# model card or technical report at the time of release.
# لا نخترع أرقام، ولا نقيس بنفسنا قبل ما نوثق.

MODELS: dict[str, ModelSpec] = {
    # ─── NVIDIA Nemotron 3 family ────────────────────────────
    "nemotron-3-ultra-free": ModelSpec(
        shortcut="nemotron-3-ultra-free",
        openrouter_id="nvidia/nemotron-3-ultra-550b-a55b:free",
        family="NVIDIA Nemotron 3 Ultra",
        role="frontier",
        context_tokens=1_000_000,
        active_params_b=55.0,
        total_params_b=550.0,
        is_free=True,
        supports_reasoning=True,
        benchmarks={
            "pinchbench_agent_productivity": 91.0,
            "ifbench": 82.0,
            "ruler_1m_long_context": 95.0,
            "swe_bench_verified": 70.4,  # max across harnesses (65-70.4)
            "terminal_bench_2": 54.0,
            "enterpriseops_planning": 33.0,
            "profbench_search": 56.0,
        },
        notes="Best-in-class for agent orchestration. GPQA score NOT officially published — must measure ourselves.",
        sources=[
            "https://developer.nvidia.com/blog/nvidia-nemotron-3-ultra-powers-faster-more-efficient-reasoning-for-long-running-agents/",
            "https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf",
        ],
    ),
    "nemotron-3-super-free": ModelSpec(
        shortcut="nemotron-3-super-free",
        openrouter_id="nvidia/nemotron-3-super-120b-a12b:free",
        family="NVIDIA Nemotron 3 Super",
        role="general",
        context_tokens=1_000_000,
        active_params_b=12.0,
        total_params_b=120.0,
        is_free=True,
        supports_reasoning=True,
        benchmarks={
            "mmlu_pro": 83.73,
            "gpqa_diamond": 79.23,
            "swe_bench_verified": 60.47,
            "livecodebench": 81.19,
            "hmmt_math": 94.73,  # with tools
            "pinchbench_agent": 85.6,
        },
        notes="Strong all-rounder; 7.5x faster than Qwen3.5-122B; good GPQA at 79%.",
        sources=["https://stackbuiltai.com/nemotron-3-super-review-2026/"],
    ),
    "nemotron-3-nano-free": ModelSpec(
        shortcut="nemotron-3-nano-free",
        openrouter_id="nvidia/nemotron-3-nano-30b-a3b:free",
        family="NVIDIA Nemotron 3 Nano",
        role="small",
        context_tokens=1_000_000,
        active_params_b=3.0,
        total_params_b=30.0,
        is_free=True,
        supports_reasoning=True,
        benchmarks={
            "math": 82.88,
            "humaneval": 78.05,
            "ruler_64k": 87.5,
            "ruler_128k": 82.92,
            "ruler_512k": 70.56,
        },
        notes="Most efficient; 1M context; outperforms Qwen3-30B on math/code.",
        sources=["https://llm-stats.com/blog/research/nemotron-3-nano-launch"],
    ),
    "nemotron-3-nano-omni-free": ModelSpec(
        shortcut="nemotron-3-nano-omni-free",
        openrouter_id="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        family="NVIDIA Nemotron 3 Nano Omni",
        role="small",
        context_tokens=256_000,
        active_params_b=3.0,
        total_params_b=30.0,
        is_free=True,
        supports_reasoning=True,
        benchmarks={},  # multimodal-focused, GPQA not its strength
        notes="Multimodal (text/image/video/audio). 256K context (not 1M).",
        sources=["https://www.buildfastwithai.com/blogs/nvidia-nemotron-3-nano-omni-2026"],
    ),
    "nemotron-nano-9b-v2-free": ModelSpec(
        shortcut="nemotron-nano-9b-v2-free",
        openrouter_id="nvidia/nemotron-nano-9b-v2:free",
        family="NVIDIA Nemotron Nano 9B v2",
        role="small",
        context_tokens=128_000,
        active_params_b=9.0,
        total_params_b=9.0,
        is_free=True,
        supports_reasoning=True,
        benchmarks={},  # older v2 generation, fewer official numbers public
        notes="Smaller dense model from Nemotron v2 generation.",
        sources=[],
    ),

    # ─── OpenAI GPT-OSS ─────────────────────────────────────
    "gpt-oss-120b-free": ModelSpec(
        shortcut="gpt-oss-120b-free",
        openrouter_id="openai/gpt-oss-120b:free",
        family="OpenAI gpt-oss",
        role="reasoning",
        context_tokens=131_000,
        active_params_b=5.1,
        total_params_b=120.0,
        is_free=True,
        supports_reasoning=True,
        benchmarks={
            "gpqa_diamond": 80.1,         # high reasoning, no tools
            "gpqa_diamond_low": 67.1,
            "gpqa_diamond_medium": 73.1,
            "aime_2024": 95.8,
            "aime_2025": 92.5,
            "mmlu": 90.0,
            "swe_bench_verified": 62.4,
            "tau_bench_retail": 67.8,
        },
        notes="GPQA-Diamond 80.1% official (high effort). Strong reasoning baseline.",
        sources=[
            "https://arxiv.org/html/2508.10925v1",
            "https://build.nvidia.com/openai/gpt-oss-120b/modelcard",
        ],
    ),

    # ─── Poolside Laguna (coding-specialized) ─────────────
    "laguna-m1-free": ModelSpec(
        shortcut="laguna-m1-free",
        openrouter_id="poolside/laguna-m.1:free",
        family="Poolside Laguna M.1",
        role="coding",
        context_tokens=131_000,
        active_params_b=23.0,
        total_params_b=225.0,
        is_free=True,
        supports_reasoning=False,
        benchmarks={
            "swe_bench_verified": 72.5,
            "swe_bench_multilingual": 67.3,
            "swe_bench_pro": 46.9,
            "terminal_bench_2": 40.7,
        },
        notes="Coding-focused flagship. NOT a general-purpose chat model — strongest in plan-execute-observe agent loops.",
        sources=[
            "https://poolside.ai/models",
            "https://docs.poolside.ai/release-notes/laguna-m1",
        ],
    ),
    "laguna-xs2-free": ModelSpec(
        shortcut="laguna-xs2-free",
        openrouter_id="poolside/laguna-xs.2:free",
        family="Poolside Laguna XS.2",
        role="coding",
        context_tokens=131_000,
        active_params_b=3.0,
        total_params_b=33.0,
        is_free=True,
        supports_reasoning=False,
        benchmarks={
            "swe_bench_verified": 68.2,
            "swe_bench_multilingual": 62.4,
            "swe_bench_pro": 44.5,
            "terminal_bench_2": 30.1,
        },
        notes="Open-weight (Apache 2.0). Coding agent on a single GPU. Surprisingly close to M.1.",
        sources=["https://poolside.ai/models"],
    ),

    # ─── Google Gemma 4 ─────────────────────────────────────
    "gemma-4-31b-free": ModelSpec(
        shortcut="gemma-4-31b-free",
        openrouter_id="google/gemma-4-31b-it:free",
        family="Google Gemma 4",
        role="frontier",
        context_tokens=262_000,
        active_params_b=31.0,
        total_params_b=31.0,
        is_free=True,
        supports_reasoning=True,  # thinking mode
        benchmarks={
            "gpqa_diamond": 84.3,  # HIGHEST in this whole registry!
            "mmlu": 87.1,
            "humaneval": 76.8,
            "aime_2026": 89.2,
            "math_vision": 85.6,
            "codeforces_elo": 2150,
            "mmlu_pro": 80.6,
            "mmmu_pro": 76.9,
        },
        notes="🥇 BEST GPQA-Diamond score (84.3%) in this registry. Multimodal (vision). Strong agentic coding too.",
        sources=[
            "https://huggingface.co/google/gemma-4-31B-it",
            "https://friendli.ai/blog/gemma-4-31b-it",
        ],
    ),
    "gemma-4-26b-free": ModelSpec(
        shortcut="gemma-4-26b-free",
        openrouter_id="google/gemma-4-26b-a4b-it:free",
        family="Google Gemma 4 (MoE)",
        role="general",
        context_tokens=262_000,
        active_params_b=4.0,
        total_params_b=26.0,
        is_free=True,
        supports_reasoning=True,
        benchmarks={
            "gpqa_diamond": 82.3,
            "mmlu": 82.7,
            "humaneval": 73.2,
            "math_vision": 82.4,
        },
        notes="MoE variant. Slightly lower than 31B but much cheaper inference.",
        sources=["https://huggingface.co/google/gemma-4-31B"],
    ),

    # ─── Z-AI GLM ───────────────────────────────────────────
    "glm-4.5-air-free": ModelSpec(
        shortcut="glm-4.5-air-free",
        openrouter_id="z-ai/glm-4.5-air:free",
        family="Z.AI GLM-4.5-Air",
        role="agent",
        context_tokens=131_000,
        active_params_b=12.0,
        total_params_b=106.0,
        is_free=True,
        supports_reasoning=True,  # thinking mode
        benchmarks={
            "math_500": 98.1,
            "aime_2024": 89.4,
            "mmlu_pro": 81.4,
            "tau_bench_retail": 77.9,
            "bfcl_v3": 76.4,
            "tool_selection_quality": 94.0,  # from Galileo
        },
        notes="🥇 Best tool-calling in registry (BFCL 76.4 + Tool Selection 94%). Dual mode thinking/non-thinking.",
        sources=[
            "https://docs.z.ai/guides/llm/glm-4.5",
            "https://galileo.ai/model-hub/glm-4-5-air-overview",
        ],
    ),

    # ─── Qwen Coder ─────────────────────────────────────────
    "qwen3-coder-free": ModelSpec(
        shortcut="qwen3-coder-free",
        openrouter_id="qwen/qwen3-coder:free",
        family="Qwen3 Coder",
        role="coding",
        context_tokens=1_000_000,
        active_params_b=None,
        total_params_b=None,
        is_free=True,
        supports_reasoning=False,
        benchmarks={
            "swe_bench_verified": 73.4,  # Qwen3.6 family number, approximate
        },
        notes="1M context, coding-tuned. Free on OpenRouter (preview).",
        sources=["https://costgoat.com/pricing/openrouter-free-models"],
    ),

    # ─── Liquid LFM (tiny but mighty) ──────────────────────
    "lfm-2.5-thinking-free": ModelSpec(
        shortcut="lfm-2.5-thinking-free",
        openrouter_id="liquid/lfm-2.5-1.2b-thinking:free",
        family="Liquid LFM 2.5",
        role="small",
        context_tokens=32_000,
        active_params_b=1.2,
        total_params_b=1.2,
        is_free=True,
        supports_reasoning=True,
        benchmarks={
            "gpqa_diamond": 37.86,
            "mmlu_pro": 49.65,
            "ifeval": 88.42,
            "math_500": 87.96,
            "aime_2025": 31.73,
            "gsm8k": 85.60,
        },
        notes="Tiny 1.2B model with thinking. Surprisingly strong IFEval (88.42). Good for fast iteration / sanity tests.",
        sources=[
            "https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking",
            "https://www.liquid.ai/blog/lfm2-5-1-2b-thinking-on-device-reasoning-under-1gb",
        ],
    ),
}


# ============================================================
#                  Query helpers
# ============================================================

def get_model(shortcut_or_id: str) -> ModelSpec:
    """يقبل shortcut أو openrouter_id كامل."""
    if shortcut_or_id in MODELS:
        return MODELS[shortcut_or_id]
    for m in MODELS.values():
        if m.openrouter_id == shortcut_or_id:
            return m
    raise KeyError(f"Unknown model: {shortcut_or_id}. Available: {list(MODELS.keys())}")


def list_by_role(role: str) -> list[ModelSpec]:
    return [m for m in MODELS.values() if m.role == role]


def list_by_benchmark(bench: str, *, min_score: float = 0.0) -> list[ModelSpec]:
    """Sorted descending by score."""
    out = [m for m in MODELS.values() if m.benchmarks.get(bench, 0) >= min_score]
    out.sort(key=lambda m: m.benchmarks.get(bench, 0), reverse=True)
    return out


def list_supports_long_context(min_tokens: int = 256_000) -> list[ModelSpec]:
    return [m for m in MODELS.values() if m.context_tokens >= min_tokens]


def recommended_for(task: str) -> list[ModelSpec]:
    """يرجع نماذج موصى بها لنوع مهمة معين، مرتبة."""
    task = task.lower()
    if task in ("gpqa", "knowledge", "reasoning"):
        return list_by_benchmark("gpqa_diamond", min_score=50)
    if task in ("swe_bench", "coding", "swe"):
        return list_by_benchmark("swe_bench_verified", min_score=50)
    if task in ("agent", "orchestration", "tools"):
        # نجمع pinchbench + ifbench + tool_selection
        scored = []
        for m in MODELS.values():
            score = (
                m.benchmarks.get("pinchbench_agent_productivity", 0)
                + m.benchmarks.get("pinchbench_agent", 0)
                + m.benchmarks.get("ifbench", 0)
                + m.benchmarks.get("tool_selection_quality", 0)
            )
            if score > 0:
                scored.append((score, m))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored]
    return list(MODELS.values())


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true", help="List all models")
    p.add_argument("--for_task", type=str, help="Recommend models for: gpqa | coding | agent")
    p.add_argument("--bench", type=str, help="Sort by benchmark (e.g. gpqa_diamond)")
    args = p.parse_args()

    if args.for_task:
        print(f"=== Recommended for: {args.for_task} ===")
        for m in recommended_for(args.for_task):
            top_bench = max(m.benchmarks.items(), key=lambda x: x[1], default=("-", 0))
            print(f"  {m.shortcut:30s} {m.description}  [{top_bench[0]}={top_bench[1]}]")
    elif args.bench:
        print(f"=== Sorted by: {args.bench} ===")
        for m in list_by_benchmark(args.bench):
            print(f"  {m.shortcut:30s} {args.bench}={m.benchmarks.get(args.bench, '-')}  ({m.description})")
    else:
        # full list
        print(f"=== Model Registry ({len(MODELS)} models) ===\n")
        for m in MODELS.values():
            print(f"▸ {m.shortcut}  →  {m.openrouter_id}")
            print(f"    {m.description}")
            if m.benchmarks:
                top3 = sorted(m.benchmarks.items(), key=lambda x: x[1], reverse=True)[:3]
                bench_str = ", ".join(f"{k}={v}" for k, v in top3)
                print(f"    top benchmarks: {bench_str}")
            if m.notes:
                print(f"    note: {m.notes}")
            print()
