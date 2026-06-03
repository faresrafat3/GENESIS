# Virtual-GENESIS Research Blueprint (Arabic)

## الفرضية الأساسية
بما أن التنفيذ سيتم عبر OpenRouter API، فالمشروع يجب أن يركز على **الذكاء الخارجي حول النموذج** بدل الاعتماد المبكر على تحديث الأوزان. الهدف هو بناء طبقة تشغيل ذكية تجعل مجموعة من النماذج الثابتة تتصرف كمنظومة تتعلم، تتحقق، وتتحسن تراكميًا.

## النتيجة البحثية التي نريدها
ليس مجرد Agent ينفذ، بل:
1. **ذكاء أثناء المهمة**: search / critique / verify / rerank.
2. **ذكاء بين المهام**: memory / lessons / skill accumulation.
3. **ذكاء في التصميم نفسه**: prompt-policy evolution / harness evolution / routing evolution.
4. **ذكاء اقتصادي**: تحسن accuracy/cost/latency معًا.

## الأعمال القريبة وما الذي نأخذه منها
### 1) SIA
- دمج harness updates و weight updates.
- الدرس: فصل واضح بين تحسين “كيف يعمل النظام” وتحسين “ما يعرفه النموذج”.
- قرارنا: نبدأ بالشق الأول بقوة، ونصمم الشق الثاني كمسار مستقبلي فقط.

### 2) Meta-Harness
- search over harness code باستخدام source + scores + execution traces.
- الدرس: **التجارب الكاملة والتراسات الخام أقوى من الملخصات**.
- تطبيق عندنا: لا نخزن فقط score نهائي؛ نخزن traces منظمة وقابلة للتحليل.

### 3) Agentic Harness Engineering (AHE)
- observability ثلاثية: component / experience / decision observability.
- الدرس: كل تعديل لازم يكون قابلًا للعزو والرجوع والتحقق.
- تطبيق عندنا: manifest لكل تعديل prompt/policy/skill مع توقعات واختبار رجعي.

### 4) Darwin Gödel Machine (DGM)
- archive مفتوح لتنوع الحلول + self-modification empirically validated.
- الدرس: لا تحتفظ فقط بالأفضل الحالي؛ احتفظ أيضًا بـ stepping stones.
- تطبيق عندنا: archive للسياسات والمهارات والبرومبتات وليس winner واحد.

### 5) HyperAgents
- meta-mechanism نفسه editable + persistent memory + performance tracking.
- الدرس: ليس فقط task policy بل improvement policy نفسها يجب أن تتطور.
- تطبيق عندنا: لاحقًا نطوّر controller يقرر كيف نحسن، لا فقط ماذا نحسن.

### 6) AlphaEvolve / FunSearch / CodeEvolve
- evolutionary search + evaluator + diversity/islands + program database.
- الدرس: ال verifier القوي مع archive متنوع يفتح مجال اكتشافات حقيقية.
- تطبيق عندنا: prompt/policy/skill evolution مع diversity pools و evaluator ثابت.

### 7) TTT-Discover
- test-time learning لتحقيق state-of-the-art في بعض مسائل الاكتشاف.
- الدرس: أحيانًا المشكلة تحتاج internalization حقيقي.
- قرارنا: نؤجل هذا لمسار لاحق بسبب القيود، لكن نصمم النظام بحيث يقبل هذه الطبقة مستقبلًا.

### 8) AutoTTS
- لا تصمم heuristic يدويًا؛ صمم environment يجعل heuristic نفسها تُكتشف cheaply.
- الدرس: **اكتشاف سياسة توزيع الميزانية** أرخص من trial-and-error المباشر.
- تطبيق عندنا: offline replay environment لتجريب routing/retry/deepen policies فوق traces محفوظة.

### 9) Reflexion / Self-Refine
- feedback اللفظي والانعكاس الذاتي يحسن الأداء دون weight updates.
- الدرس: linguistic feedback مصدر تعلم قوي وقليل التكلفة.
- تطبيق عندنا: lesson compiler + critique memory + self-revision loop.

### 10) STaR
- self-generated rationales + filtering + iterative improvement.
- الدرس: أمثلة النجاح التي تم التحقق منها تتحول إلى مادة تعليمية.
- تطبيق عندنا: verified few-shot bank مبني من النجاحات.

### 11) Voyager
- automatic curriculum + ever-growing skill library + iterative prompting.
- الدرس: مكتبة مهارات قابلة للاسترجاع أهم من محاولة “تذكر كل شيء” في prompt واحد.
- تطبيق عندنا: Skill Capsules + capability unlock graph.

### 12) SkillClaw
- collective skill evolution across users / sessions.
- الدرس: الخبرة المتفرقة يجب أن تتجمع في shared skill repository.
- تطبيق عندنا: مهارات قابلة للترقية مع validation قبل النشر.

### 13) GEPA / MIPRO / ADAS
- prompt optimization و agent design search من خلال language feedback والأرشيف.
- الدرس: اللغة نفسها medium تعلم غني جدًا، وغالبًا أكثر كفاءة من RL في low-data regimes.
- تطبيق عندنا: prompt/policy evolution في المرحلة المتوسطة قبل أي fine-tuning.

### 14) AI Scientist / AI Scientist-v2
- archive + reviewer + experiment manager + tree search.
- الدرس: systems research القوية تحتاج evaluator متعدد الطبقات، وليس مجرد score وحيد.
- تطبيق عندنا: benchmark harness + shadow evaluation + reviewer ensemble.

## ما لا ننسخه حرفيًا
1. لا full self-modifying codebase من اليوم الأول.
2. لا RL/update loops ثقيلة مع API-only setup.
3. لا benchmark hacking على verifier واحد.
4. لا giant-agent واحد بكل الأدوار.
5. لا اعتماد على prompt engineering فقط.

## الرؤية المعمارية النهائية
### ثلاث حلقات مترابطة
#### A) Online Intelligence Loop
يعمل داخل كل مهمة:
- classify
- retrieve
- plan
- generate
- critique
- verify
- rerank
- answer

#### B) Mid-Term Improvement Loop
يعمل بين المهام:
- collect traces
- cluster failures
- extract lessons
- patch prompts/policies/skills
- regression test
- publish or rollback

#### C) Offline Discovery Loop
يعمل دوريًا:
- replay historical traces
- simulate alternative controllers/prompts/routers
- discover lower-cost or higher-accuracy policies
- promote best policies after shadow eval

## المعمارية المفصلة
### 1) Task Intake & Taxonomy
- نوع المهمة
- درجة صعوبتها
- حساسية الدقة
- budget class
- preferred verification path

### 2) Budget & Difficulty Governor
- يحدد max calls
- max tokens
- max candidate count
- escalation rules
- متى نستخدم model أقوى أو rerank أو judge إضافي

### 3) Model Router
#### أدوار النماذج
- Planner
- Worker
- Critic
- Judge
- Optional Compressor/Summarizer

#### سياسات الاختيار
- by task type
- by cost ceiling
- by latency ceiling
- by confidence
- by historical win-rate per task family

### 4) Prompt Compiler
يبني prompt من:
- task profile
- domain pack
- relevant lessons
- retrieved examples
- output schema
- tool availability
- verifier expectations

### 5) Memory OS
#### أنواع الذاكرة
- Episodic
- Failure
- Success
- Strategy
- Example / few-shot
- Skill metadata
- Cost-performance stats

#### قواعد الاسترجاع
- lexical + semantic
- task-family aware
- recency + reliability weighting
- conflict resolution between old/new lessons

### 6) Candidate Search Engine
#### modes
- single-pass
- best-of-N
- critique-and-revise
- debate-lite
- branch-and-prune
- disagreement-triggered deepening

### 7) Verifier Ensemble
#### طبقات التحقق
1. Schema
2. Deterministic rules
3. Evidence check
4. Execution / tests
5. Consistency check
6. Judge model
7. Regression gate

### 8) Reranking Layer
- semantic rerank
- verifier-aware rerank
- cost-aware rerank
- diversity-aware rerank

### 9) Skill Capsule System
كل skill capsule تحتوي:
- trigger conditions
- instructions template
- required tools
- validation recipe
- examples
- known failure modes
- version history

### 10) Lesson Compiler
من traces إلى:
- lesson text
- patch candidate
- anti-pattern
- routing rule
- skill update proposal
- confidence score

### 11) Improvement Manager
- يقبل proposals
- يختبرها shadow
- يقارن baseline vs candidate
- ينشر أو يرجع rollback

### 12) Observability Layer
نسجل:
- model used
- provider used
- session_id
- tokens / cost / latency
- retrieved memories
- verifier outputs
- failure taxonomy
- chosen policy path

## الأفكار الجديدة الخاصة بنا
### 1) Policy Replay Lab
أهم فكرة في المشروع.
بدل ما كل policy جديدة نختبرها live فقط، نبني replay lab على traces سابقة:
- نجرب routing alternatives
- نجرب candidate counts مختلفة
- نجرب judge order مختلف
- نجرب prompt patches
- نقيّم معظمها offline أو شبه-offline

### 2) Improvement Contracts
كل patch لازم يصرح:
- ما المشكلة التي يحلها
- أين قد يسبب regression
- كيف سنختبره
- ما metric النجاح
ثم نتحول من “تعديل عشوائي” إلى “فرضية قابلة للدحض”.

### 3) Skill Genome
كل skill لها genes/attributes:
- task families
- required evidence type
- cost class
- typical failure modes
- dependencies
- compatible models
هذا يسهل inheritance/merging/branching.

### 4) Disagreement-Triggered Deepening
الـ deep mode لا يُفعّل لمجرد الصعوبة الظاهرة فقط، بل أيضًا عند:
- planner/worker disagreement
- high verifier uncertainty
- answer unsupported by evidence
- judge split

### 5) Evidence Locking
في المهام الحساسة، لا يخرج النظام جوابًا نهائيًا إلا إذا حقق حدًا أدنى من evidence integrity.

### 6) Multi-Objective Reward بدون RL
نستخدم scoring function خارجية تجمع:
- correctness
- robustness
- evidence grounding
- latency
- cost
- consistency
بدل optimization على متريك واحدة.

## كيف نستفيد من OpenRouter عمليًا
### ما سنستعمله من المنصة
- `/models` و `/models/user` لاكتشاف النماذج وقدراتها.
- provider routing preferences.
- `session_id` للـ sticky routing و prompt caching.
- structured outputs / json schema.
- tool calling.
- rerank endpoint.
- observability/log metadata.
- private models لاحقًا إذا احتجنا.

### قواعد تشغيل على OpenRouter
1. كل workflow له `session_id` ثابت.
2. نقرأ models metadata دوريًا ونبني catalog محلي.
3. نستخدم structured outputs افتراضيًا للخطوات الداخلية.
4. نخصص model roles بدل model واحد.
5. نضيف provider constraints حسب الحساسية.
6. نستخدم rerank رسمي للوثائق/المرشحين عند الحاجة.

## خطة البحث الهندسي
### المرحلة A — Foundation Spec
- تعريف أول 2-3 task families
- تعريف metrics
- تعريف cost budget bands
- تعريف failure taxonomy
- تعريف trace schema

### المرحلة B — Minimal Intelligence Core
- Orchestrator
- Router
- Prompt compiler
- JSON schemas
- basic verifier
- logs

### المرحلة C — Learning Without Training
- memory store
- lesson compiler
- prompt patch engine
- few-shot bank
- candidate compare/select

### المرحلة D — Self-Improvement Engine
- proposal generation
- shadow evaluation
- rollout archive
- policy replay lab
- publish/rollback

### المرحلة E — Skill Ecosystem
- skill capsules
- skill registry
- cross-task transfer
- collective update rules

### المرحلة F — Advanced Search
- branch-and-prune
- disagreement deepening
- adaptive budget controller
- controller discovery over replay traces

## الفرضيات البحثية التي سنختبرها
1. detailed traces > scalar metrics فقط.
2. verifier ensembles > single judge.
3. skill capsules + memory > plain chat history.
4. policy replay discovery > manual heuristic tuning.
5. reflective prompt evolution > brute-force best-of-N under same budget.
6. cost-aware routing > strongest-model-always.
7. improvement contracts + rollback > naive prompt iteration.

## ablations المقترحة
- بدون memory
- بدون verifier ensemble
- بدون candidate search
- بدون lesson compiler
- بدون skill capsules
- بدون replay lab
- موديل واحد vs multi-model routing
- static prompts vs prompt compiler

## مقاييس النجاح
### primary
- task success rate
- verifier pass rate
- groundedness / evidence score
- avg cost per successful task
- latency per solved task

### secondary
- retry count
- regression rate
- transfer across task families
- human intervention rate
- skill reuse rate

## أنواع المخاطر
1. Prompt overfitting
2. Judge bias
3. Memory pollution
4. cost explosion
5. policy complexity explosion
6. stale skill accumulation
7. silent regressions

## آليات التخفيف
- golden benchmark
- shadow mode
- rollback on regression
- TTL لبعض الدروس
- confidence thresholds
- deterministic validators أولًا
- hard cost caps
- archive branching بدل overwrite

## لماذا هذا المشروع يمكن أن يكون قويًا؟
لأنه لا يحاول منافسة الأوراق على ملعب واحد فقط. بل يدمج:
- Harness evolution
- Reflection
- Skill accumulation
- Archive search
- Observability
- Cost-aware routing
- Replay-based controller discovery
في منظومة واحدة مناسبة لـ API-only reality.

## القرار الاستراتيجي النهائي
النسخة الأولى من النظام يجب أن تكون:
**frozen-model, adaptive-system, trace-rich, verifier-heavy, memory-growing**

وليس:
**training-heavy, benchmark-specific, single-model, prompt-only**

## مخرجات ما قبل التنفيذ
قبل كتابة الكود الكامل، نحتاج مستندات فرعية:
1. product spec
2. trace schema
3. skill capsule schema
4. lesson schema
5. verifier interface spec
6. routing policy spec
7. benchmark plan
8. rollout log spec
9. regression protocol
10. release phases
