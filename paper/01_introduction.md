# §1 Introduction

## 1.1 The Rise of Agentic LLM Systems

خلال العامين الأخيرين، شهد المجال انفجاراً في **agentic systems** المبنية على LLMs. من AlphaEvolve [1] و FunSearch [2] لـ evolutionary discovery، إلى Aletheia [3] لـ proof-driven verification، إلى Co-Scientist [4] لـ multi-agent research — كل هذه الأنظمة تدعي مكاسب أداء كبيرة فوق pure LLM baselines.

مثال: على GPQA Diamond (benchmark reasoning صعب [5])، الادعاءات تراوحت من +5 نقاط (baseline shifts) إلى +20 نقطة (full pipelines). لكن **معظم هذه الادعاءات لا تفصل بين مساهمتين قابلتين للخلط:**

1. **Architectural contribution:** التأثير الحقيقي للـ evolutionary search / verification / multi-agent debate
2. **Scaffolding artifacts:** الفروق في كيفية بناء الـ prompts، parsing الـ responses، handling errors

## 1.2 A Motivating Case Study

في مشروع GENESIS، بنينا LLM orchestration framework مشابه (meta-agent + target agent + feedback agent + evolutionary discovery + cognitive pipeline). أول قياس على GPQA Diamond مع `gpt-oss-120b` أعطى:

- **GENESIS accuracy: 30.30%** (198 questions)
- **Pure `gpt-oss-120b` baseline (same tier, same task, same evaluator): 75.00%** (20q subset)
- **Official gpt-oss-120b: 80.1%** (198q, high reasoning effort)

**Gap: -45 points** بين GENESIS وpure baseline لنفس النموذج.

كان السؤال الطبيعي: "هل معمارية GENESIS بها قيود جوهرية؟" لكن التحقيق التفصيلي كشف عن **5 فئات من bugs في scaffolding** تفسر الفجوة بالكامل. بعد إصلاحها في مكتبة portable (`genesis/llm_helpers.py`)، الأداء بدأ يتحسن بشكل كبير (سنقيسه في §7).

هذا الاكتشاف أثار سؤال أوسع:

> **كم من الفجوات المُبلغ عنها في الأدبيات الحديثة بين "pure LLM" و "agentic architecture" ترجع لـ scaffolding bugs بدلاً من مساهمات معمارية حقيقية؟**

## 1.3 Contributions

هذه الورقة تقدم:

### C1: Rigorous Baseline Methodology
نقدم بروتوكول قياس صارم لـ pure LLM baseline على GPQA Diamond يعالج:
- Response parsing (16 patterns للـ letter extraction)
- Empty content recovery (extraction من `reasoning_details`)
- Invalid response retry (force-letter follow-up)
- Multi-key rate limit handling (11-key rotation pool)

### C2: Taxonomy of Scaffolding Bugs
نحدد **5 فئات** من bugs يشيعوا في LLM orchestration systems (§6):
- **B1:** JSON key case mismatch (impact: -30 pts)
- **B2:** Inadequate max_tokens budget (-15 pts)
- **B3:** "ONLY letter" instruction suppresses CoT (-10 pts)
- **B4:** Empty content dropped without reasoning fallback (-20 pts via recovery)
- **B5:** Invalid response without smart retry (-3 pts)

لكل bug: symptom, root cause, diagnostic test, fix, cross-reference to existing frameworks.

### C3: Portable Library
`genesis/llm_helpers.py` — مكتبة عامة تحل الـ 5 bugs:
- 220 lines, 35 unit tests passing
- No GENESIS-specific dependencies (portable to LangChain/DSPy/CrewAI/AutoGen)
- Includes: `extract_response_text`, `extract_letter`, `ask_for_letter_followup`, `safe_get_question_field`, `build_mcq_prompt`, `SCIENTIFIC_MCQ_SYSTEM_PROMPT`

### C4: Novel Empirical Findings
- **C4a:** Reasoning tokens correlate **negatively** with per-question accuracy (median 989 for correct vs 6,836 for incorrect on gpt-oss-120b/GPQA). We call this "reasoning saturation" (§5.5, §9.2).
- **C4b:** Domain asymmetry: models systematically fail Chemistry Organic (83% "Hard" questions) more than Physics (9% "Hard") (§5.4).
- **C4c:** "Empty content phenomenon" — 35% of GPQA questions produce empty `content` from reasoning models but rich `reasoning_details` (§5.6).

### C5: Diagnostic Toolkit
`tools/diagnose_run_53.py` — سكريبت آلي يفحص أي LLM orchestration output لـ 5 bugs categories ويعطي report كامل بالأدلة الرقمية.

## 1.4 Roadmap

- **§2 Related Work:** الأوراق الأساسية (AlphaEvolve, Aletheia, Co-Scientist, GPQA)
- **§3 GENESIS Architecture:** معمارية النظام (meta/target/feedback/evolutionary/pipeline)
- **§4 Experimental Setup:** infrastructure, models, evaluation
- **§5 Baseline Results:** pure baseline measurements + cross-model comparison
- **§6 Scaffolding Analysis:** 5 bugs taxonomy مع أدلة
- **§7 GENESIS Post-Fix Results:** أداء بعد إصلاح scaffolding (⏳ pending T1)
- **§8 Ablation Studies:** أي component يضيف قيمة (⏳ pending T3)
- **§9 Discussion:** تفسيرات + reasoning saturation hypothesis
- **§10 Limitations:** ما لم نغطه
- **§11 Future Work:** instant vs thinking، multi-provider، multi-agent debate
- **§12 Appendices:** جداول تفصيلية، prompts، code snippets

## 1.5 A Note on Research Posture

هذه ورقة **بحث تجريبي متواضع** — لا تدعي أن معمارية GENESIS تتفوق على state-of-the-art. بدلاً من ذلك، تدعي أن:

> **يجب على المجتمع البحثي أن يعتمد "scaffolding hygiene checks" قبل الادعاء بمكاسب معمارية.**

النتائج الحالية تشير أن معظم الفجوات المُبلغ عنها **قد تكون scaffolding**، لكن تحديد النسبة الدقيقة يتطلب replicate هذه الدراسة على أنظمة أخرى (LangChain, DSPy, CrewAI, AutoGen).

---

## References (inline placeholders)

[1] AlphaEvolve — Google DeepMind (see §2.1)
[2] FunSearch — Nature 2024 (see §2.1)
[3] Aletheia / Gemini Deep Think — DeepMind (see §2.2)
[4] Co-Scientist — Gemini for Science (see §2.3)
[5] GPQA — Rein et al. 2023, arXiv:2311.12022 (see §2.5)
[6] gpt-oss model card — arXiv:2508.10925 (see §2.6)

**Section status:** 🟡 Solid draft. May need updating after T1 results.
