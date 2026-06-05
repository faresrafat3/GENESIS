# 🌍 خريطة كاملة لمصادر LLM المجانية في 2026 — بدائل OpenRouter

**التاريخ:** 2026-06-05
**الهدف:** توسيع مصادر inference المجانية للمشروع عشان نتجاوز limits OpenRouter (50 req/day/model)

---

## 🏆 TL;DR — الـ Top 5 الموصى بها

| المزود | الأهم بيقدم | Rate Limit | Credit Card | Best For GENESIS |
|---|---|---|---|---|
| **🥇 Google AI Studio (Gemini)** | Gemini 2.5 Flash, 2.5 Pro, 3 Flash | **1,500 RPD** للـ Flash, 50 RPD لـ Pro | لا | **الأكثر سخاء + frontier quality** |
| **🥈 Groq** | Llama 3.3 70B, Mixtral | 30 RPM, 1000 RPD/model | لا | **أسرع inference (315 tok/s)** |
| **🥉 Cerebras** | Llama 3.1 70B/8B, gpt-oss-120b | 30 RPM, **1M tokens/day** | لا | **أعلى daily tokens** |
| **NVIDIA NIM** (build.nvidia.com) | Nemotron family, DeepSeek, Llama | per-account limits | لا | **NVIDIA models direct** |
| **GitHub Models** | **GPT-5, GPT-4.1, Claude, Grok 3** | يعتمد على Copilot tier | لا | **الوحيد بـ free GPT-5 و Claude!** |

---

## 📊 الجدول الكامل (13 مزود)

### الـ Tier 1: مجاني بدون credit card

| المزود | النماذج | الحد | إيش بيميزه |
|---|---|---|---|
| **Google AI Studio** | Gemini 2.5 Flash (1M ctx), 2.5 Pro (1M ctx), Gemma 3 | 1,500 req/day Flash, 50/day Pro | Multimodal + 1M context |
| **Groq** | Llama 3.3 70B, Llama 3.1 8B, Mixtral, Gemma 2 | 30 RPM, 1000/day per model | أسرع inference في العالم |
| **Cerebras** | Llama 3.1 70B/8B, gpt-oss-120b/20b | 30 RPM, **1M tokens/day** | أعلى throughput يومي |
| **NVIDIA NIM** | Nemotron family + DeepSeek R1/V3 + 100+ open | per-account (مش معلن بالظبط) | direct from NVIDIA |
| **GitHub Models** | **GPT-5, GPT-4.1, GPT-4o, Claude Sonnet/Haiku, Grok 3, o4-mini** | tied to Copilot tier (free GitHub = limited) | الوحيد بـ **GPT-5 مجاناً** |
| **OpenRouter** | 35+ free models | 50 req/day/model under $10 spent (بعدها 1000/day) | aggregator |
| **Cloudflare Workers AI** | Llama 3.1, Qwen, gpt-oss | 10,000 neurons/day | edge inference |
| **Mistral AI** | Mistral Small, Codestral | rate-limited free | EU data |
| **Cohere** | Command R/R+ | 1,000 calls/month trial | best embeddings |
| **DeepSeek** | DeepSeek V3/R1 | rate-limited | الأرخص للـ reasoning |
| **Hugging Face Inference** | open weights models | $0.10/month free credits | model variety |

### الـ Tier 2: trial credits ($5-$25)

| المزود | الكريدت | المدة |
|---|---|---|
| **OpenAI Direct** | $5 | 3 شهور (لو منخدمتش) |
| **Anthropic Claude** | $5 console + open-source program 6 شهور | varies |
| **xAI Grok** | $25 sign-up + $150/month data program | متجدد |
| **SambaNova** | $5 | 30 يوم |
| **Together AI** | لا (انتهى) | — |

### الـ Tier 3: research/academic grants

| البرنامج | المبلغ | المتطلبات |
|---|---|---|
| **Anthropic Research Credits** | $500 - $25,000+ | academic/AI safety/nonprofit |
| **OpenAI Researcher Access Program** | varies (2-8 أسابيع approval) | qualifying institution |
| **Google Cloud Research Credits** | $300 + extra | Google Cloud project |
| **AWS Activate** | up to $100K | startup |
| **Anthropic Claude for Open Source** | 6 months Claude Max 20x ($1,200 value) | open-source maintainer |

---

## 🎯 توصيتي للمشروع — Stack مجاني قوي

عشان نوفر **آلاف من requests يومياً** بدون credit card، نبني pool متعدد المزودين:

### الـ Daily Budget الناتج (إذا فعّلنا الكل):
```
Google Gemini Flash:         1,500 req/day
Google Gemini Pro:              50 req/day
Groq (3 models × 1000):       3,000 req/day
Cerebras:                     30 RPM × ~16h = ~28,800 req
NVIDIA NIM (Nemotron):        ~500 req/day
OpenRouter (11 keys × ~5 models): 2,750 req/day
GitHub Models (GPT-5/Claude!): copilot-tied
─────────────────────────────────────────────
TOTAL متاح:                  ~36,000+ req/day (تقريباً)
```

### مقابل اليوم (OpenRouter بس):
```
OpenRouter free tier:         50 req/day/model
× 11 keys × 5 models =       2,750 req/day
─────────────────────────────────────────────
TOTAL:                       2,750 req/day
```

**Δ = 13× زيادة في الـ daily capacity!** 🚀

---

## 🛠️ خطة التطبيق — توسعة الـ Infrastructure

### المرحلة 1: أوسّع الـ `api_key_pool.py` ليكون multi-provider

دلوقتي الـ pool بيدير مفاتيح OpenRouter بس. لازم نوسعه يدير:
- **Multiple providers** بنفس الفلسفة (rotation + cooldown)
- **Per-provider routing**: نختار المزود الأنسب لكل model
- **Cross-provider fallback**: لو Gemini exhausted، نروح لـ Cerebras

### المرحلة 2: Provider Registry

```python
PROVIDERS = {
    "google_gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "models": ["gemini-2.5-flash", "gemini-2.5-pro"],
        "auth": "GEMINI_API_KEY",
        "free_rpd": {"gemini-2.5-flash": 1500, "gemini-2.5-pro": 50},
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        "auth": "GROQ_API_KEY",
        "free_rpd": {"_default": 1000},
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "models": ["llama-3.1-70b", "llama-3.1-8b", "gpt-oss-120b"],
        "auth": "CEREBRAS_API_KEY",
        "free_rpm": 30,
        "free_tpd": 1_000_000,
    },
    "nvidia_nim": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "models": ["nvidia/nemotron-3-ultra", "deepseek/deepseek-r1"],
        "auth": "NVIDIA_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "models": ["openai/gpt-oss-120b:free", ...],
        "auth": "OPENROUTER_API_KEY_<NAME>",
        "free_rpd_per_model": 50,
    },
    "github_models": {
        "base_url": "https://models.github.ai/inference",
        "models": ["openai/gpt-5", "anthropic/claude-sonnet-4", "xai/grok-3"],
        "auth": "GITHUB_TOKEN",
        "notes": "Rate-limited by Copilot tier",
    },
}
```

### المرحلة 3: Smart Router

```python
def get_client_for_model(model_name: str, pool: MultiProviderPool):
    """يختار أفضل مزود متاح للنموذج المطلوب."""
    # 1) لو الـ model له primary provider، جربه أول
    # 2) لو exhausted، fallback لـ secondary providers
    # 3) لو الكل exhausted، fail fast
```

---

## 📋 خطوات عملية للـ setup (لما تكون عند فارس)

### 1. Google AI Studio (أهم خطوة!)
```bash
# 1. روح: https://aistudio.google.com/app/apikey
# 2. اعمل sign in بـ Google account
# 3. اعمل "Create API key" — هيدوني Gemini Flash + Pro
# 4. حط في .env:
echo "GEMINI_API_KEY=your_key_here" >> .env
```
**النتيجة:** 1,500 req/day على Gemini 2.5 Flash + 50/day على Pro (frontier quality)

### 2. Groq (لـ السرعة)
```bash
# 1. روح: https://console.groq.com
# 2. sign in (Google or GitHub)
# 3. Create API key
echo "GROQ_API_KEY=gsk_..." >> .env
```
**النتيجة:** Llama 3.3 70B بسرعة 315 tok/s، 1000 req/day

### 3. Cerebras (لـ daily volume)
```bash
# 1. روح: https://cloud.cerebras.ai
# 2. sign up (no card)
# 3. API keys section
echo "CEREBRAS_API_KEY=csk-..." >> .env
```
**النتيجة:** **1M tokens/day** على Llama 70B + **gpt-oss-120b أسرع من OpenRouter!**

### 4. NVIDIA NIM (لـ Nemotron مباشرة)
```bash
# 1. روح: https://build.nvidia.com
# 2. sign in
# 3. choose any Nemotron model → "Get API Key"
echo "NVIDIA_API_KEY=nvapi-..." >> .env
```
**النتيجة:** Nemotron 3 Ultra/Super/Nano direct, بدون OpenRouter middleman

### 5. GitHub Models (هذا الـ secret weapon! 🔥)
```bash
# 1. عندك GitHub account؟ تمام
# 2. روح: https://github.com/settings/tokens
# 3. Generate token (classic) — اختر "models:read" scope
echo "GITHUB_TOKEN=github_pat_..." >> .env
```
**النتيجة:** **GPT-5, GPT-4.1, Claude Sonnet/Haiku, Grok 3, o4-mini** كلهم مجاناً (rate-limited)

---

## ⚠️ تحذيرات مهمة لا تنساها

### 1. **Google Gemini Free Tier بيستخدم بيانتك للتدريب**
لو هتشتغل على بيانات حساسة، استخدم Vertex AI (paid) أو موزع تاني.
لكن لـ GPQA (public benchmark) ده مفيش مشكلة.

### 2. **GitHub Models Public Preview**
الـ rate limits مش معلنة بدقة وممكن تتغير. للـ production لا تعتمد عليه.

### 3. **Cerebras 1M token/day** = ~100 طلب بـ avg 10K input
لو الـ context كبير (زي حالتنا)، الحد ده ينخلص بسرعة.

### 4. **NVIDIA NIM phone verification** قد يكون مطلوب لـ DeepSeek

### 5. **متجمعش حسابات مختلفة على نفس IP**
معظم المزودين بيـ track الـ IP. لو شغلت 11 حساب على نفس IP زي OpenRouter، ممكن يلاحظوا.

---

## 🎯 الـ Recommendation Engine

### للـ GENESIS scaffolding (meta-agent + feedback-agent):
**استخدم GitHub Models → GPT-5** لو متاح، أو **Google Gemini 2.5 Pro** كـ fallback.
- ليه: high reasoning quality + tool calling
- الحدود: GitHub Models tied to Copilot, Gemini Pro = 50/day

### للـ target-agent على QA tasks (GPQA):
**استخدم Cerebras → gpt-oss-120b** أو **Groq → Llama 3.3 70B**
- ليه: سرعة عالية + reasonable accuracy
- الحدود: Cerebras 1M tokens/day, Groq 1000 RPD/model

### للـ evolutionary discovery population (many small calls):
**استخدم Groq → Llama 3.3 70B**
- ليه: أسرع نموذج، بيخلص الـ population في دقايق
- الحدود: 30 RPM (بس يكفي لـ 6-10 population)

### للـ tasks الـ thinking-heavy:
**استخدم NVIDIA NIM → DeepSeek R1** أو **Nemotron 3 Ultra مباشرة**
- ليه: أعلى reasoning depth
- الحدود: rate limits per-account

---

## 🚀 المخطط لو نفّذنا الكل

دلوقتي عندنا:
- ✅ 11 مفتاح OpenRouter (2,750 req/day متفرقة على free models)

لو نضيف الـ 5 مزودين الجدد:
- ✅ 1,550 req/day على Gemini (Flash + Pro)
- ✅ 3,000 req/day على Groq (3 models)
- ✅ 1M tokens/day على Cerebras (= حوالي 500-1000 req للأسئلة الطويلة)
- ✅ Nemotron مباشرة بدون daily limits قاسية
- ✅ GPT-5, Claude Sonnet مجاناً من GitHub Models

**التوتال متاح يومياً:** ~7,000+ req على frontier models + Cerebras tokens غير محدودة عملياً

**ده يكفي لـ:**
- **35 GENESIS runs كاملة** يومياً (مع 198 GPQA × 1 model)
- **70 evolutionary discoveries** يومياً
- **عدة paper-level experiments** بدون انتظار

---

## 📂 الملف المتبقي للجلسة الجاية

عشان نطبق ده فعلياً، محتاجين:

1. **توسعة `api_key_pool.py`** → `multi_provider_pool.py` يدير كل المزودين
2. **توسعة `model_registry.py`** ليشمل النماذج من كل مزود (مش بس OpenRouter)
3. **Smart routing logic** يختار أنسب مزود لكل model
4. **توثيق setup steps** لكل مزود في README

**أنا متحمس جداً ندخل في ده — هذا هيكسر barrier الـ rate limits بشكل أساسي ويفتح المشروع للـ benchmarks الحقيقية.**

---

## 🔗 المراجع

- [Free LLM APIs 2026 Comparison (TokenMix)](https://tokenmix.ai/blog/free-llm-apis-2026-every-provider-free-tier-tested)
- [Best Free LLM API 2026 (CostBench)](https://costbench.com/best/best-llm-api-with-free-tier/)
- [Free Model Directory](https://free-model.com/)
- [Google AI Studio](https://aistudio.google.com)
- [Groq Console](https://console.groq.com)
- [Cerebras Cloud](https://cloud.cerebras.ai)
- [NVIDIA Build](https://build.nvidia.com)
- [GitHub Models](https://github.com/marketplace/models)
- [Anthropic Research Credits](https://www.getaiperks.com/en/ai/anthropic-research-credit-program)
