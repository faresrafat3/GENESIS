"""
Multi-Provider Registry — Inference providers beyond OpenRouter.
=================================================================

Catalog of free-tier LLM providers with their OpenAI-compatible endpoints,
auth methods, and known rate limits.

The MultiProviderPool will use this to route requests intelligently:
- Pick a provider that supports the requested model
- Rotate across providers if one is exhausted
- Respect per-provider rate limits

تصميم عام: كل مزود هو ProviderSpec، لا hardcoding لأي مزود في الـ logic.

SECURITY: لا يوجد مفتاح مخزن هنا. كل المفاتيح من env vars.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ProviderSpec:
    """مواصفات مزود واحد.

    Args:
        name: short id (e.g., "google_gemini", "groq")
        base_url: OpenAI-compatible endpoint URL
        env_var_pattern: env var name pattern for API key
                         (e.g., "GEMINI_API_KEY" or "OPENROUTER_API_KEY_*")
        models: list of model IDs available on this provider
        free_rpd: dict {model_id: requests_per_day} for free tier (None = no daily cap)
        free_rpm: requests per minute (overall provider cap)
        free_tpd: tokens per day (overall provider cap)
        supports_reasoning: does this provider expose reasoning effort?
        supports_tools: does it support tool calling?
        notes: human-readable notes for setup / quirks
        setup_url: URL to get API key
    """
    name: str
    base_url: str
    env_var_pattern: str
    models: list[str]
    free_rpd: dict[str, int] = field(default_factory=dict)
    free_rpm: Optional[int] = None
    free_tpd: Optional[int] = None
    supports_reasoning: bool = False
    supports_tools: bool = True
    notes: str = ""
    setup_url: str = ""
    requires_credit_card: bool = False
    requires_phone_verify: bool = False

    @property
    def is_multi_key(self) -> bool:
        """هل يقبل مفاتيح متعددة (بـ wildcard pattern)؟"""
        return "_*" in self.env_var_pattern or self.env_var_pattern.endswith("_")


# ============================================================
#                  THE REGISTRY
# ============================================================
# كل أرقام الـ rate limits من vendor docs (موثقة في sources/notes).
# Updated: 2026-06-05

PROVIDERS: dict[str, ProviderSpec] = {
    # ──── Google AI Studio (الأكثر سخاء) ────
    "google_gemini": ProviderSpec(
        name="google_gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        env_var_pattern="GEMINI_API_KEY",
        models=[
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemma-3-27b-it",
        ],
        free_rpd={
            "gemini-2.5-flash": 1500,
            "gemini-2.5-flash-lite": 1500,
            "gemini-2.5-pro": 50,
            "gemini-2.0-flash": 1500,
            "gemma-3-27b-it": 1500,
        },
        free_rpm=15,  # default; Pro is 5, Flash is 15-30
        supports_reasoning=True,  # Gemini supports thinking mode
        supports_tools=True,
        notes=(
            "Most generous free tier. 1M context window. "
            "WARNING: free-tier inputs may be used by Google for training. "
            "For sensitive data use Vertex AI (paid)."
        ),
        setup_url="https://aistudio.google.com/app/apikey",
    ),

    # ──── Groq (الأسرع) ────
    "groq": ProviderSpec(
        name="groq",
        base_url="https://api.groq.com/openai/v1",
        env_var_pattern="GROQ_API_KEY",
        models=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
            "deepseek-r1-distill-llama-70b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
        ],
        free_rpd={"_default": 1000},  # 1000 per model
        free_rpm=30,
        supports_reasoning=True,  # Some models support reasoning
        supports_tools=True,
        notes=(
            "Ultra-fast LPU inference (~315 tok/s on Llama 70B). "
            "1000 req/day per model. Best for speed-critical agentic loops. "
            "Does NOT train on user data."
        ),
        setup_url="https://console.groq.com/keys",
    ),

    # ──── Cerebras (أعلى daily tokens) ────
    "cerebras": ProviderSpec(
        name="cerebras",
        base_url="https://api.cerebras.ai/v1",
        env_var_pattern="CEREBRAS_API_KEY",
        models=[
            "llama-3.1-70b",
            "llama-3.1-8b",
            "llama-3.3-70b",
            "qwen-3-32b",
            "gpt-oss-120b",
        ],
        free_rpm=30,
        free_tpd=1_000_000,  # 1M tokens/day total
        supports_tools=True,
        notes=(
            "1M tokens/day total (across all models). "
            "Token budget binds before request count. "
            "For long-context tasks (>5K tokens/req), this limits to ~100-200 calls/day."
        ),
        setup_url="https://cloud.cerebras.ai",
    ),

    # ──── NVIDIA NIM (Nemotron direct) ────
    "nvidia_nim": ProviderSpec(
        name="nvidia_nim",
        base_url="https://integrate.api.nvidia.com/v1",
        env_var_pattern="NVIDIA_API_KEY",
        models=[
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/nemotron-3-super-120b-a12b",
            "nvidia/nemotron-3-nano-30b-a3b",
            "deepseek-ai/deepseek-r1",
            "deepseek-ai/deepseek-v3",
            "meta/llama-3.3-70b-instruct",
        ],
        supports_reasoning=True,
        supports_tools=True,
        notes=(
            "Direct access to Nemotron family + DeepSeek R1/V3. "
            "Phone verification required for some models. "
            "Free prototyping tier; per-account limits not publicly documented."
        ),
        setup_url="https://build.nvidia.com",
        requires_phone_verify=True,
    ),

    # ──── GitHub Models (الـ secret weapon - GPT-5 و Claude!) ────
    "github_models": ProviderSpec(
        name="github_models",
        base_url="https://models.github.ai/inference",
        env_var_pattern="GITHUB_TOKEN",
        models=[
            "openai/gpt-5",
            "openai/gpt-4.1",
            "openai/gpt-4o",
            "openai/o4-mini",
            "anthropic/claude-sonnet-4",
            "anthropic/claude-haiku-3.5",
            "xai/grok-3",
            "xai/grok-3-mini",
            "meta/llama-3.3-70b-instruct",
            "deepseek/deepseek-r1",
        ],
        supports_reasoning=True,
        supports_tools=True,
        notes=(
            "🔥 ONLY free source for GPT-5, GPT-4.1, Claude Sonnet 4! "
            "Rate limits tied to Copilot tier (Free GitHub = limited, Pro = more). "
            "Public preview — limits may change without notice. "
            "Use 'models:read' scope on GitHub PAT."
        ),
        setup_url="https://github.com/settings/tokens (create PAT with models:read scope)",
    ),

    # ──── OpenRouter (الحالي) ────
    "openrouter": ProviderSpec(
        name="openrouter",
        base_url="https://openrouter.ai/api/v1",
        env_var_pattern="OPENROUTER_API_KEY_*",  # multi-key
        models=[
            "openai/gpt-oss-120b:free",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "nvidia/nemotron-3-nano-30b-a3b:free",
            "google/gemma-4-31b-it:free",
            "z-ai/glm-4.5-air:free",
            "poolside/laguna-m.1:free",
            "poolside/laguna-xs.2:free",
            "liquid/lfm-2.5-1.2b-thinking:free",
        ],
        free_rpd={"_default": 50},  # 50/day/model under $10 credits
        free_rpm=20,
        supports_reasoning=True,
        supports_tools=True,
        notes=(
            "Aggregator for many models. 50 req/day/model on free tier. "
            "$10 credits → 1000 req/day. Multi-key via OPENROUTER_API_KEY_<NAME>."
        ),
        setup_url="https://openrouter.ai/settings/keys",
    ),

    # ──── Cloudflare Workers AI (edge) ────
    "cloudflare_workers": ProviderSpec(
        name="cloudflare_workers",
        base_url="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
        env_var_pattern="CLOUDFLARE_API_TOKEN",
        models=[
            "@cf/meta/llama-3.1-70b-instruct",
            "@cf/openai/gpt-oss-120b",
            "@cf/qwen/qwen-2.5-coder-32b-instruct",
        ],
        notes=(
            "10,000 neurons/day. Best for edge inference. "
            "base_url requires account_id substitution."
        ),
        setup_url="https://dash.cloudflare.com/profile/api-tokens",
    ),

    # ──── Mistral (EU) ────
    "mistral": ProviderSpec(
        name="mistral",
        base_url="https://api.mistral.ai/v1",
        env_var_pattern="MISTRAL_API_KEY",
        models=[
            "mistral-small-latest",
            "codestral-latest",
            "open-mistral-nemo",
        ],
        supports_tools=True,
        notes="Free 'experiment' tier. EU data residency. Limited rate.",
        setup_url="https://console.mistral.ai/api-keys",
    ),

    # ──── DeepSeek (الأرخص للـ reasoning) ────
    "deepseek": ProviderSpec(
        name="deepseek",
        base_url="https://api.deepseek.com/v1",
        env_var_pattern="DEEPSEEK_API_KEY",
        models=[
            "deepseek-chat",  # V3
            "deepseek-reasoner",  # R1
        ],
        supports_reasoning=True,
        supports_tools=True,
        notes="Generous free tier (granted balance). Cheap reasoning.",
        setup_url="https://platform.deepseek.com/api_keys",
    ),
}


# ============================================================
#                  Query helpers
# ============================================================

def find_provider_for_model(model_id: str) -> list[ProviderSpec]:
    """يرجع كل المزودين اللي يدعموا model معين."""
    matches = []
    for p in PROVIDERS.values():
        # exact match
        if model_id in p.models:
            matches.append(p)
            continue
        # partial match (e.g., "llama-3.3-70b" matches "llama-3.3-70b-versatile")
        for m in p.models:
            if model_id in m or m in model_id:
                matches.append(p)
                break
    return matches


def list_providers_with_card(require_card: bool = False) -> list[ProviderSpec]:
    return [p for p in PROVIDERS.values() if p.requires_credit_card == require_card]


def get_setup_instructions() -> str:
    """يرجع تعليمات setup كاملة لكل المزودين."""
    lines = ["# Free LLM Provider Setup Guide", ""]
    for name, p in PROVIDERS.items():
        lines.append(f"## {name}")
        lines.append(f"  Setup URL: {p.setup_url}")
        lines.append(f"  Env var:   {p.env_var_pattern}")
        if p.free_rpd:
            for m, lim in p.free_rpd.items():
                lines.append(f"  Free RPD:  {m}: {lim}")
        if p.free_rpm:
            lines.append(f"  Free RPM:  {p.free_rpm}")
        if p.free_tpd:
            lines.append(f"  Free TPD:  {p.free_tpd:,}")
        if p.notes:
            lines.append(f"  Notes:     {p.notes}")
        if p.requires_credit_card:
            lines.append(f"  ⚠️  Credit card required")
        if p.requires_phone_verify:
            lines.append(f"  ⚠️  Phone verification may be required")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true", help="List all providers")
    p.add_argument("--find_model", type=str, help="Find providers for a model")
    p.add_argument("--setup", action="store_true", help="Print full setup guide")
    args = p.parse_args()

    if args.list:
        print(f"=== {len(PROVIDERS)} providers in registry ===\n")
        for name, spec in PROVIDERS.items():
            print(f"▸ {name}")
            print(f"    {len(spec.models)} models, base_url={spec.base_url}")
            print(f"    env={spec.env_var_pattern}")
            print(f"    rpd={spec.free_rpd or 'N/A'}, rpm={spec.free_rpm}, tpd={spec.free_tpd}")
            if spec.notes:
                print(f"    note: {spec.notes[:100]}")
            print()
    elif args.find_model:
        matches = find_provider_for_model(args.find_model)
        if not matches:
            print(f"No providers found for: {args.find_model}")
        else:
            print(f"=== Providers supporting {args.find_model} ===\n")
            for p in matches:
                print(f"▸ {p.name}: {p.base_url}")
                print(f"    Notes: {p.notes[:100]}")
                print()
    elif args.setup:
        print(get_setup_instructions())
    else:
        print(__doc__)
        print(f"\nUse --list, --find_model, or --setup. {len(PROVIDERS)} providers registered.")
