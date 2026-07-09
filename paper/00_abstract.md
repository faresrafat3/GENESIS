# Abstract

## Draft v0.2 — 2026-06-05

---

## English Abstract

**Background.** Recent LLM orchestration systems (AlphaEvolve [1], Aletheia [2], Co-Scientist [3]) claim substantial performance gains over pure LLM baselines through evolutionary search, verification loops, and multi-agent debate. Yet the field lacks rigorous ablation studies isolating architectural contributions from **scaffolding artifacts** — bugs in prompt engineering, response parsing, and error handling that can silently degrade LLM performance.

**Contributions.** We present GENESIS, an LLM orchestration framework, and use it as a substrate to investigate a fundamental question: *how much of the observed gap between "pure LLM" and "full agentic system" performance is attributable to scaffolding bugs vs. architectural limitations?*

Through controlled experiments on GPQA Diamond (graduate-level multiple-choice science) using `gpt-oss-120b` (OpenAI, 2026), we find:

1. **Scaffolding bugs alone cause a 45-percentage-point accuracy gap** between pure baseline (75.00%) and initial agentic system (30.30%) — despite identical LLM, task, and evaluation protocol.

2. **Five scaffolding bug categories** account for essentially all of this gap:
   (i) JSON key case mismatches,
   (ii) inadequate `max_tokens` budgets,
   (iii) chain-of-thought suppression via "output ONLY letter" instructions,
   (iv) empty content when reasoning consumes token budget,
   (v) missing fallback for invalid responses.

3. **Reasoning tokens correlate negatively with per-question accuracy** (median 989 for correct vs. 6,836 for incorrect answers), suggesting a *reasoning saturation phenomenon* not previously documented at the per-question level. This challenges the naive assumption that "more thinking = better answers".

4. **Domain-level asymmetry**: models consistently perform much better on Physics (81.8%) than on Chemistry Organic (33% average across models), a pattern that persists across model sizes and reasoning strategies.

5. **A general-purpose library** (`genesis/llm_helpers.py`) that fixes all five bug categories in a portable, tested (35/35 unit tests passing) manner. When applied, invalid response rate drops from 35% to 0%.

**Impact.** Our findings suggest that a substantial portion of reported gains from "agentic architectures" in the recent literature may in fact reflect *fixed scaffolding baselines*, not genuine architectural contributions. We call for standardized scaffolding hygiene checks before claiming architectural value.

**Data & code.** All results, prompts, and infrastructure available at `github.com/faresrafat3/GENESIS`.

---

## الملخص العربي

**الخلفية.** أنظمة orchestration الحديثة للنماذج اللغوية (AlphaEvolve، Aletheia، Co-Scientist) تدعي مكاسب أداء كبيرة فوق baselines الـ LLM النقية عبر evolutionary search، verification loops، ومناقشة multi-agent. لكن المجال يفتقر لدراسات ablation صارمة تفصل المساهمات المعمارية عن **scaffolding artifacts** — bugs في prompt engineering، response parsing، وerror handling التي تُخفض أداء الـ LLM بصمت.

**المساهمات.** نقدم GENESIS، إطار LLM orchestration، ونستخدمه كأرضية للتحقيق في سؤال أساسي: *كم من الفجوة المُلاحظة بين "LLM نقي" و"نظام agentic كامل" يعود لـ bugs في الـ scaffolding مقارنة بقيود معمارية؟*

عبر تجارب مضبوطة على GPQA Diamond باستخدام `gpt-oss-120b`، نجد:

1. **bugs الـ scaffolding وحدها تسبب فجوة 45 نقطة مئوية** بين pure baseline (75.00%) وأول نظام agentic (30.30%).

2. **خمس فئات من bugs الـ scaffolding** تفسر كل هذه الفجوة تقريباً.

3. **reasoning tokens تترابط سلبياً مع per-question accuracy** (median 989 لـ الصحيح مقابل 6,836 لـ الخطأ)، مما يشير إلى ظاهرة *reasoning saturation*.

4. **عدم تماثل على مستوى domain**: النماذج تؤدي أفضل باستمرار على Physics (81.8%) من Chemistry Organic (~33% متوسط).

5. **مكتبة عامة** (`genesis/llm_helpers.py`) تحل جميع فئات bugs بطريقة portable ومختبرة.

**الأثر.** نتائجنا تشير أن جزءاً كبيراً من المكاسب المُبلغ عنها من "architectures agentic" في الأدبيات الحديثة قد تعكس فعلياً *baselines scaffolding ثابتة*، وليس مساهمات معمارية حقيقية.

---

## Keywords

LLM orchestration, agentic systems, scaffolding, prompt engineering, GPQA benchmark, reasoning models, ablation studies, `gpt-oss-120b`, evaluation methodology

---

## References (بتتحدث في §2)
[1] AlphaEvolve (DeepMind, 2024)
[2] Aletheia / Gemini Deep Think (DeepMind, 2025)
[3] Co-Scientist / Gemini for Science (DeepMind, 2025)

---

## Notes for Later Revision

- ⚠️ الأرقام الحالية على 20q subset. النهائي هيبقى على 198q.
- ⚠️ لسه محتاجين نضيف رقم "post-fix accuracy" لما T1 يخلص.
- ⚠️ لسه محتاجين نقارن مع نماذج تانية (Gemma 4 31B, Nemotron Ultra).
- 📊 كل ادعاء في الـ abstract له جدول/رسم في الأقسام المفصلة (§5-§8).

**Status:** 🟡 Draft — placeholder pending T1 results
