# Virtual-GENESIS Tiered Intelligence Blueprint (Arabic)

## تحديث افتراضات المشروع
لم نعد في وضع free-only strictly. لدينا الآن افتراض جديد:
- يمكن استخدام OpenRouter مجانًا في البداية عبر `:free`.
- ويمكن إضافة طبقة paid قوية لاحقًا بسهولة، مثل DeepSeek V4 Pro.

## لماذا هذا التغيير مهم؟
لأن النظام لم يعد مضطرًا للاختيار بين:
- low-cost weak cognition
- أو expensive all-the-time cognition

بل يمكنه العمل بصيغة **Tiered Intelligence**:
1. cheap/default cognition
2. strong-on-demand cognition
3. collaborative/sparse multi-agent cognition فقط في الحالات الصعبة

## ما الذي نعرفه حاليًا عن DeepSeek على OpenRouter؟
- DeepSeek V4 Pro معروض على OpenRouter باعتباره MoE ضخمًا بعدد 1.6T total params و49B activated params، context window حوالي 1M tokens، وسعره $0.435/M input و$0.87/M output، وموجّه reasoning/coding/long-horizon workflows، مع دعم reasoning efforts `high` و`xhigh` [OR-model-page, OR-deepseek-page].
- DeepSeek V4 Flash معروض باعتباره efficiency-optimized MoE بعدد 284B total params و13B activated params، context حوالي 1M tokens، وسعره $0.0983/M input و$0.1966/M output، وموجّه للتكلفة/السرعة، وهناك free variant له أيضًا [OR-deepseek-page].
- OpenRouter أضاف دعم `thinking` لطرز DeepSeek V4 في changelog أبريل 2026 [OR-changelog-v4-thinking].

## الاستنتاج
نستطيع بناء بنية متعددة الطبقات:
### Tier 0 — Free / Ultra-cheap
- DeepSeek V4 Flash (free) أو ما شابهه
- مهام: triage, classification, retrieval prep, formatting, light critique

### Tier 1 — Cheap Paid
- DeepSeek V4 Flash paid
- مهام: standard planning, answer drafting, code edits الخفيفة

### Tier 2 — Premium Reasoner
- DeepSeek V4 Pro
- مهام: anomaly resolution, hard reasoning, synthesis, long-horizon plans, difficult coding/debugging

### Tier 3 — Sparse Committee
- MoA/SMoA-style collaborative reasoning only عند الأزمات أو high-value tasks

## المسار البحثي الجديد 1: Tiered Intelligence
### الفكرة
بدل نظام واحد، نبني عقلًا طبقيًا:
- cheap frontal cortex
- expensive deliberative cortex
- rare collective cognition

### سؤال البحث
كيف نقرر متى نصعّد من Tier إلى Tier أعلى؟

### الجواب المبدئي
بواسطة:
- uncertainty
- verifier disagreement
- anomaly score
- expected value of extra compute
- task criticality

## المسار البحثي الجديد 2: Sparse Mixture-of-Agents
### لماذا الآن؟
توفر موديل قوي نسبيًا مثل DeepSeek V4 Pro بسعر منخفض يفتح الباب لتجارب committee أبسط وأذكى.

### ما تقوله الأدبيات
- MoA تقترح layered collaboration بين عدة LLMs، وذكرت تفوقًا على GPT-4 Omni في بعض evaluations، مع ملاحظة أن LLMs تتحسن عندما تُعرض عليها إجابات نماذج أخرى حتى لو كانت هذه الإجابات أقل جودة منفردة [MoA-paper, MoA-html].
- SMoA تبيّن أن dense interaction بين agents مكلف، وتقترح sparsification عبر response selection وearly stopping، مع تكلفة أقل وأداء مقارب [SMoA].

### قرارنا
لا نستخدم committee دائمًا.
نستخدم **Sparse MoA** فقط عندما:
- verifier split
- task value high
- first-pass answer unstable
- multiple domain lenses needed

## المسار البحثي الجديد 3: Deliberate Search Structures
### ToT
- Tree of Thoughts تسمح بتعدد مسارات reasoning والنظر للأمام/backtracking، وذكرت قفزة في Game of 24 من 4% إلى 74% مقارنة بـ CoT [ToT].

### GoT
- Graph of Thoughts توسع ToT من شجرة إلى graph arbitrary، وذكرت تحسين جودة sorting بـ 62% فوق ToT مع خفض التكلفة >31% [GoT].

### قرارنا
في النظام:
- لا نولد answer linear فقط
- بل نمثل reasoning artifacts كبنية graph/tree على blackboard
- ونستخدم search structure حسب نوع المهمة:
  - Tree for planning
  - Graph for synthesis/argument/comparison

## المسار البحثي الجديد 4: Reasoning Transfer / Escrow
### من OpenRouter docs
- docs reasoning tokens تعرض نمطًا مهمًا: أخذ reasoning من نموذج قوي وإدخاله كنص مساعد إلى نموذج آخر لتحسين الإجابة [OR-reasoning-tokens].

### الفكرة الجديدة
نسميها:
**Reasoning Escrow**

- premium model يفكر أو يولد reasoning scaffold
- cheaper model يقوم بصياغة/تنفيذ/تفريع
- verifier يتحقق من الناتج

### لماذا مفيد؟
- يقلل عدد استدعاءات premium model
- يحافظ على جودة عالية في المهام الصعبة
- يناسب paid-but-still-cost-aware setups

## المسار البحثي الجديد 5: Self-Consolidation Without Full Fine-Tuning
### الأدبيات
- Self-Consolidation for Self-Evolving Agents تنتقد النجاح-only retrieval، وتؤكد قيمة contrastive reflection على الفشل، وتقترح distillation من textual experience إلى compact learnable parameters [EvoSC].

### قرارنا
في v1/v2 لا نعمل param updates فعلية.
لكن نستلهم الفكرة في شكل:
- distilled anti-pattern rules
- compact prompt patches
- skill upgrades
- policy embeddings/metadata

أي **self-consolidation into artifacts** بدل self-consolidation into weights.

## المسار البحثي الجديد 6: Procedural Memory Distillation
### الأدبيات
- ProcMEM يحول التجربة إلى skills ذات activation/execution/termination conditions [ProcMEM].
- MemSkill يدفع فكرة memory skills evolvable عبر controller-executor-designer [MemSkill].
- SkillRL يقترح hierarchical skill library وrecursive evolution [SkillRL].

### قرارنا
كل procedural learning ينتج:
- trigger
- steps
- verifier recipe
- stop condition
- failure signatures

## المسار البحثي الجديد 7: Decentralized Memory
### الأدبيات
- DecentMem يقترح ذاكرة لا مركزية لكل agent بدل repository مركزي واحد، مع dual pools للاستغلال والاستكشاف، وذكر improvements حتى 23.8% فوق أقوى centralized baseline وتقليل token usage حتى 49% [DecentMem].

### قرارنا
لو أصبح لدينا specialists متعددة بمرور الوقت:
- لكل specialist local memory
- مع shared distilled registry مركزي
- هذا يقلل contamination ويحافظ على diversity

## المسار البحثي الجديد 8: Compression as Evolving Asset
### الأدبيات
- TACO يطوّر structured compression rules لمشاهدات terminal agents بدل الاعتماد على truncation أو hand-crafted heuristics [TACO].

### قرارنا
الضغط ليس preprocess ثابت.
بل:
- document compression rules
- trace compression rules
- tool-output compression rules
- memory summarization rules
كلها قابلة للتطور والتقييم.

## ماذا يتغير في النظرية الأساسية؟
### قبل التحديث
Externalized Recursive Intelligence

### بعد التحديث
**Tiered Externalized Recursive Intelligence**

أي:
- المعرفة خارج الأوزان
- التحسن تراكمي
- لكن التفكير نفسه له طبقات تكلفة/قدرة

## المكونات الجديدة الناتجة
### 1) Tier Router
يختار بين:
- free/default
- paid flash
- pro reasoner
- sparse committee

### 2) Escalation Policy Engine
يعتمد على:
- uncertainty
- disagreement
- anomaly
- user value
- cost ceiling

### 3) Reasoning Escrow Store
يحفظ:
- reasoning scaffolds
- reusable deliberation traces
- compressed proof skeletons

### 4) Sparse Committee Manager
يدير:
- proposer agents
- aggregator agent
- early stopping
- diversity routing

### 5) Search Topology Manager
يحدد:
- linear
- tree
- graph
- debate-lite
بحسب نوع المهمة

## artefacts جديدة يجب إنتاجها
1. Tier catalog
2. Escalation policy tables
3. Reasoning escrow format
4. Committee protocol
5. Search topology schema
6. Compression rule registry
7. Premium-budget accounting spec
8. Task criticality rubric

## فرضيات بحثية جديدة
1. Tiered routing beats single-model routing in cost-quality terms.
2. Reasoning escrow recovers much of premium reasoning quality at lower cost.
3. Sparse committees dominate dense committees under API cost constraints.
4. Graph-structured reasoning artifacts outperform tree-only on synthesis/comparison tasks.
5. Distilled procedural memory artifacts outperform raw experience retrieval for repeated workflows.
6. Decentralized specialist memory preserves diversity better than one shared global store.

## المخاطر الجديدة
1. over-escalation إلى premium tier
2. committee overuse
3. reasoning leakage without utility
4. stale escrowed reasoning
5. complexity explosion in routing

## تخفيف المخاطر
- hard budget ceilings
- escalation audit logs
- utility threshold for escrow reuse
- periodic expiry for stale reasoning artifacts
- per-task-family defaults

## القرار البحثي المحدث
بوجود DeepSeek V4 Pro cheap-enough، لم يعد المسار الأمثل هو free-only optimization.
المسار الأمثل أصبح:
**cheap-first, premium-on-demand, sparse-collaboration-last**

وهذا أقوى بكثير من:
- always-cheap
- أو always-premium

## ما الذي نفعله بعد ذلك؟
نحتاج specs دقيقة لـ:
1. Tier Router & Escalation Policy
2. Reasoning Escrow Artifact
3. Search Topology Manager
4. Sparse Committee Protocol
5. Compression Rule Evolution

## مرجع الاختصارات الداخلية
- OR-model-page = OpenRouter DeepSeek V4 Pro model page
- OR-deepseek-page = OpenRouter DeepSeek models page
- OR-changelog-v4-thinking = OpenRouter changelog Apr 25 2026
- OR-reasoning-tokens = OpenRouter reasoning tokens docs
- MoA-paper = Mixture-of-Agents paper
- MoA-html = Mixture-of-Agents HTML/details
- SMoA = Sparse Mixture-of-Agents
- ToT = Tree of Thoughts
- GoT = Graph of Thoughts
- EvoSC = Self-Consolidation for Self-Evolving Agents
- ProcMEM = procedural memory paper
- MemSkill = evolving memory skills paper
- SkillRL = recursive skill-augmented RL paper
- DecentMem = decentralized memory paper
- TACO = self-evolving compression for terminal agents
