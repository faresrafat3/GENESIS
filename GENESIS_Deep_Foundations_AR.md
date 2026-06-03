# Virtual-GENESIS Deep Foundations (Arabic)

## لماذا هذه النسخة الجديدة من التخطيط؟
هذه الوثيقة تجمع بين:
- أبحاث agent self-improvement الحديثة
- أبحاث memory/harness/search الحديثة
- مبادئ معرفية وفلسفية أقدم يمكن تحويلها إلى architecture
- قيود التشغيل العملية: OpenRouter :free في البداية

## قيد التشغيل الأساسي
### OpenRouter Free-first
- استخدام suffix `:free` للوصول للنماذج المجانية.
- النماذج المجانية ذات rate limits منخفضة.
- وفق docs الرسمية: حتى 20 request/min على نماذج `:free`، و50 request/day إذا لم تُشترَ credits بقيمة 10$ على الأقل، و1000/day بعد شراء 10$ credits.
- هذا يجعل cost-awareness و caching و replay و memory compression جزءًا من **جوهر النظام** وليس تحسينًا ثانويًا.

## النتيجة المعمارية الأساسية
في free-first setup لا يمكننا الاعتماد على:
- many-candidate brute force
- long reflection chains on every task
- judge committees دائمًا
- heavyweight online exploration

بل يجب بناء:
1. **سلم تكلفة**: default cheap path ثم escalation مشروط.
2. **استرجاع ذكي بدل إعادة التفكير من الصفر**.
3. **تحسين offline/on-replay بدل live-only**.
4. **patches صغيرة قابلة للعزو** بدل تغييرات ضخمة.
5. **مهارات قابلة لإعادة الاستخدام** بدل استدعاءات كثيرة مكررة.

## المبادئ الحديثة التي سنبني فوقها
### 1) Harness as first-class object
- SIA / Meta-Harness / AHE / AutoHarness / Code as Agent Harness
- الدرس: ما يحيط بالنموذج ليس مجرد wrapper بل مصدر أساسي للذكاء.

### 2) Traces as learning substrate
- Meta-Harness: full traces > compressed summaries
- AHE: component / experience / decision observability
- الدرس: أي تحسين محترم يحتاج trace-rich substrate.

### 3) Memory as operating system
- Mem0: extraction / update / delete / noop memory operations
- MemOS: memory as system resource with lifecycle and scheduling
- SimpleMem: structured compression + recursive consolidation + adaptive retrieval
- الدرس: الذاكرة ليست مجرد vector DB؛ هي lifecycle كامل.

### 4) Skill accumulation
- Voyager: skill library + curriculum
- SkillClaw: collective skill evolution
- الدرس: الذكاء التراكمي يحتاج unit اسمها skill، لا مجرد history.

### 5) Language-based self-improvement
- Reflexion / Self-Refine / GEPA
- الدرس: اللغة feedback mechanism وليست فقط output format.

### 6) Archive-based search
- DGM / HyperAgents / FunSearch / AlphaEvolve / CodeEvolve
- الدرس: حفظ التنوع والـ stepping stones ضروري.

### 7) Controller discovery
- AutoTTS
- الدرس: اكتشاف سياسة توزيع compute/search أهم من كتابة heuristics يدويًا.

### 8) Experiment governance
- AI Scientist / AI Scientist-v2
- الدرس: أي منظومة تحسين تحتاج experiment manager + reviewer + archive.

## المبادئ الكلاسيكية/الفلسفية التي نستلهمها
### A) Polya — How to Solve It
أربع خطوات:
1. فهم المشكلة
2. وضع خطة
3. تنفيذ الخطة
4. النظر للخلف

**الترجمة المعمارية:**
- Task Understanding Module
- Plan Synthesizer
- Execution Engine
- Reflection / After-Action Review

### B) Lakatos — Proofs and Refutations
المعرفة تتقدم عبر:
- conjectures
- attempted proofs
- counterexamples
- concept revision

**الترجمة المعمارية:**
- answer as conjecture
- verifier as counterexample generator
- failure cases cause not just retry, but **schema/prompt/skill revision**

### C) Kuhn — Paradigm / Anomaly / Crisis / Shift
العلم لا يتقدم فقط بتجميع حلول؛ بل عبر:
- normal puzzle solving
- anomaly accumulation
- crisis
- paradigm shift

**الترجمة المعمارية:**
- normal mode
- anomaly detector
- failure clustering
- controller/skill family fork when anomalies exceed threshold

### D) Herbert Simon — Bounded Rationality / Satisficing
القرار الواقعي ليس optimal دومًا بل “good enough under constraints”.

**الترجمة المعمارية:**
- Budget-aware stopping
- aspiration thresholds
- first-satisfactory answer under controlled verification
- no endless search on free tier

### E) OODA Loop — Observe / Orient / Decide / Act
في البيئات الديناميكية، سرعة الدورة نفسها ميزة.

**الترجمة المعمارية:**
- Observe = retrieve context + logs + tool state
- Orient = build situational model
- Decide = choose policy / route / skill
- Act = execute
- ثم loop جديدة

### F) Blackboard Architecture
حل المشكلات المعقدة يمكن أن يبنى من عدة specialist modules تشارك على مساحة عمل مشتركة.

**الترجمة المعمارية:**
- Shared Task Blackboard
- planner يكتب decomposition
- retriever يضيف evidence
- critic يضيف objections
- verifier يضيف pass/fail artifacts
- answer composer يستهلك كل ذلك

### G) Society of Mind (Minsky)
الذكاء ليس مبدأ واحدًا بل مجتمعًا من agents/skills البسيطة المتفاعلة.

**الترجمة المعمارية:**
- no monolithic agent
- multiple micro-policies
- skills + critics + routers + memory workers
- diversity by design

### H) Predictive Processing / Active Inference
العقل لا ينتظر البيانات فقط؛ بل يتنبأ ويقارن ويقلل الخطأ.

**الترجمة المعمارية:**
- hypothesis-first answering
- prediction error = verifier disagreement / evidence mismatch / execution failure
- active information gathering when uncertainty high

### I) Antifragility
بعض الأنظمة لا تصمد فقط أمام الفشل، بل تتحسن بسببه.

**الترجمة المعمارية:**
- every failure should create asset:
  - lesson
  - patch
  - anti-pattern
  - benchmark case
  - skill improvement candidate

## النظرية التي ستجمع كل هذا
### النظرية المقترحة للمشروع
**Externalized Recursive Intelligence**

تعريفها:
نظام ذكاء لا يعتمد أساسًا على تعديل weights، بل على تنظيم:
- الملاحظة
- الاسترجاع
- التنبؤ
- البحث
- التحقق
- الأرشفة
- ترقية السياسات والمهارات

بحيث يصبح قادرًا على التحسن التراكمي، مع بقاء الموديلات نفسها ثابتة نسبيًا.

## البنية النظرية النهائية
### 1) The Loop of Intelligence
#### Level 1: Single-task cognition
- perception / retrieval
- planning
- generation
- verification
- selection

#### Level 2: Cross-task learning
- memory updates
- lesson extraction
- skill evolution
- prompt policy evolution

#### Level 3: Meta-cognitive redesign
- which policy families are working?
- where are anomalies accumulating?
- which controller should govern future tasks?

## مكونات النظام بعد تعميق النظرية
### 1. Task Blackboard
مساحة حالة مشتركة تحتوي:
- normalized task statement
- task family tags
- uncertainty estimate
- retrieved facts/docs
- candidate plans
- candidate answers
- verifier outputs
- confidence traces

### 2. OODA Controller
- Observe: gather context + model/provider state + memory hits
- Orient: build task state and threat/opportunity map
- Decide: pick policy/skill/model path
- Act: execute next step

### 3. Bounded-Rationality Governor
- aspiration level per task family
- stop if answer exceeds threshold and additional search not worth budget
- escalate only when expected gain > expected cost

### 4. Predictive Answering Layer
- build hypothesis before full answer
- ask: what evidence would confirm/disconfirm this?
- gather missing evidence actively if needed

### 5. Proofs-and-Refutations Engine
- answer treated as conjecture
- verifier generates local/global counterexamples
- counterexample type determines repair path:
  - formatting patch
  - evidence patch
  - strategy patch
  - skill patch
  - routing patch

### 6. Skill Genome + Skill Capsules
كل skill لها:
- triggers
- cost profile
- model compatibility
- evidence needs
- known failure modes
- parent skills / descendants
- benchmark history

### 7. Memory OS
#### memory classes
- working memory
- episodic memory
- semantic memory
- strategic memory
- anomaly memory
- benchmark memory

#### lifecycle actions
- add
- merge
- update
- deprecate
- fork
- expire

### 8. Replay Research Lab
يعمل على traces محفوظة لاكتشاف:
- better routing
- cheaper verification order
- candidate counts المناسبة
- lesson utility
- prompt patches
- skill branch superiority

### 9. Anomaly & Paradigm Manager
- tracks repeated unexplained failures
- clusters them
- if cluster persistent:
  - create crisis report
  - propose paradigm fork
  - run shadow evaluation

### 10. Antifragility Engine
كل فشل يمر عبر pipeline:
- classify failure
- ask “what asset can we extract?”
- save to archive
- maybe create new benchmark case
- maybe create new skill branch
- maybe create routing blacklist rule

## ما الذي يضاف للمشروع مقارنة بالنسخة السابقة؟
### إضافات جديدة
1. **Task Blackboard** بدل shared logs فقط.
2. **OODA Controller** كمنطق control موحد.
3. **Bounded-Rationality Governor** مناسب لـ free-tier.
4. **Predictive Answering** بدل generation-first فقط.
5. **Proofs-and-Refutations Engine** لتنظيم النقد والإصلاح.
6. **Anomaly/Paradigm Manager** لمعالجة الفشل البنيوي لا الفردي فقط.
7. **Antifragility Engine** لتحويل الفشل إلى أصل معرفي.

## لماذا هذا أقوى للنماذج المجانية؟
لأن النماذج المجانية تفرض:
- throughput محدود
- calls قليلة
- تفاوت في الجودة

إذًا يجب أن نعوض ذلك بـ:
- better orchestration
- higher memory reuse
- stronger verification
- strict budget gating
- offline improvement
- fewer but smarter calls

## قواعد تصميم خاصة بـ free-first
1. اجعل default path قصيرًا.
2. اجعل deep path مشروطًا وقابلًا للتبرير.
3. لا تستخدم committee دائمًا.
4. استعمل rerank/verify فقط عند الحاجة.
5. ابنِ bank أمثلة verified لتقليل الاستدعاءات مستقبلًا.
6. حوّل المخرجات الجيدة إلى skills أو lessons بسرعة.
7. فضّل التحسينات التي تقلل calls مستقبلًا.

## خارطة القدرات المستقبلية
### Capability Class A — Practical Assistant
- سؤال/جواب
- تلخيص
- استخراج
- بحث
- coding help

### Capability Class B — Agentic Work
- planning
- multi-step execution
- file/tool workflows
- structured analysis

### Capability Class C — Scientific / Conceptual Work
- compare theories
- build argument trees
- literature synthesis
- idea generation
- experiment planning

### Capability Class D — Meta-Intelligence
- policy improvement
- skill evolution
- benchmark generation
- anomaly detection
- architecture critique

## بنشماركات/مجالات تقييم نقترحها
- GAIA للأسئلة العامة التي تتطلب reasoning + multimodality + tool use
- OSWorld للمهام الحاسوبية المفتوحة (لاحقًا)
- memory benchmarks مثل LoCoMo / AMA-style tasks
- benchmark داخلي صغير من real user tasks

## المعادلة الذهبية للمشروع
**ذكاء = (فهم + استرجاع + تخطيط + تحقق + تعلّم + ضبط تكلفة)**

وليس:
**ذكاء = موديل أقوى فقط**

## القرار النهائي
النسخة القادمة من Virtual-GENESIS يجب أن تقوم على خمس ركائز:
1. **Harness-first**
2. **Trace-rich**
3. **Memory-OS**
4. **Proofs-and-Refutations**
5. **Antifragile improvement**

## ما الذي نفعله لاحقًا؟
قبل التنفيذ الكامل، نكتب Specs تفصيلية جديدة لـ:
1. Task Blackboard Schema
2. Memory OS Schema
3. OODA Controller Policy
4. Bounded-Rationality & Budget Policy
5. Proofs-and-Refutations Verifier Interface
6. Anomaly / Crisis / Paradigm Rules
7. Skill Genome / Capsule Spec
8. Replay Research Lab Spec
