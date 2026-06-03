# Virtual-GENESIS Concept Selectivity Spec (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تأتي بعد أن أصبحت Thesis 1 تمتلك evidence قوية داخل `prototype_v3b_curriculum`،
لكن هذه القوة كشفت bottleneck جديدة:

- `concept_activation_rate = 1.0`
- `concept_count = 11`

أي أن المفاهيم أصبحت مفيدة، لكن هناك خطر أن تكون:
- over-activated
- أو proliferating أكثر من اللازم
- أو مرتبطة بالـ curriculum الحالية أكثر من ارتباطها بجوهر المهمة

إذًا الهدف الآن هو:

# **تحويل استخدام المفاهيم من وجود useful concepts إلى استخدام انتقائي ومنضبط لها**

---

# 1) التعريف المركزي
## Concept Selectivity
هي السياسة والآليات التي تحدد:
- متى ينبغي تفعيل concept؟
- كم concept نفعّل للمهمة الواحدة؟
- أي concepts نرجّح؟
- ومتى يجب **عدم** تفعيل أي concept؟

### الصياغة المختصرة
Concept Selectivity =
**controlled activation of abstractions under relevance, budget, and anti-sprawl constraints**

---

# 2) لماذا selectivity مهمة؟
إذا كانت المفاهيم لا تُفعل أبدًا:
- تصبح artifacts جميلة بلا أثر

إذا كانت المفاهيم تُفعل دائمًا:
- تتحول إلى noise
- تضعف falsifiability
- وقد تخلق apparent gains مبنية على over-conditioning

إذًا الهدف ليس:
- zero concepts
ولا:
- all concepts all the time

بل:
# **right concepts, at the right time, in the right quantity**

---

# 3) الفرضيات الأساسية
### Hypothesis 1
وجود concepts مفيد، لكن **الانتقائية** في استخدامها لا تقل أهمية عن تكوينها.

### Hypothesis 2
Top-k الثابتة قد تكون أسهل في البداية لكنها ستقود إلى concept overuse أو concept sprawl لاحقًا.

### Hypothesis 3
الـ selectivity الجيدة يجب أن تراعي:
- semantic fit
- contract fit
- family fit
- cost/complexity
- anti-redundancy

### Hypothesis 4
بعض المهام يجب أن تتلقى **zero concepts** if concept value is low.

---

# 4) ما الذي يحدد صلاحية concept للمهمة؟
نقترح أن صلاحية concept candidate for activation تُحسب من خمسة مكونات:

## A) Task-family fit
هل concept تنتمي إلى family المناسبة؟

## B) Contract fit
هل concept مرتبطة بـ required properties أو forbidden shortcuts للمهمة؟

## C) Lexical/semantic fit
هل هناك overlap أو semantic closeness بين task/case والـ concept؟

## D) Redundancy penalty
هل concept تضيف جديدًا أم تكرر concept أخرى مفعلة؟

## E) Risk/complexity penalty
هل عدد المفاهيم المفعلة أو nature of task يجعل إضافة concept أخرى عبئًا أكثر من فائدة؟

---

# 5) Selectivity policy modes

## Mode 1 — Null concept mode
لا تُفعل أي concepts.

## Mode 2 — Top-1 concept mode
تُفعل concept واحدة فقط، strongest candidate.

## Mode 3 — Top-k bounded mode
عدد صغير محدود (مثل 2 أو 3) مع thresholds واضحة.

## Mode 4 — Dynamic mode
عدد المفاهيم يتحدد حسب:
- ambiguity
- contract complexity
- benefit estimate

### recommendation الحالية
للـ prototype الحالية:
# **Top-1 or Top-2 bounded mode**
أفضل من activation المفتوحة.

---

# 6) Concept Activation Object
نقترح object صريحة:

## ConceptActivationDecision
- `task_ref`
- `concept_ref`
- `activation_score`
- `activation_reasons`
- `redundancy_penalty`
- `selected: bool`
- `rank`
- `notes`

هذه object مهمة جدًا لكي لا يصبح التفعيل implicit وغير قابل للتفسير.

---

# 7) Activation scoring (تصور أولي)
نقترح score مبدئية على شكل:

**ActivationScore = FamilyFit + ContractFit + SemanticFit - RedundancyPenalty - ComplexityPenalty**

### note
ليس مهمًا الآن أن تكون رقمية دقيقة جدًا، لكن المهم أن تصبح explicit ومحكومة.

---

# 8) متى لا نستخدم أي concept؟
هذه نقطة محورية.

## Zero-concept conditions
1. task low complexity and low ambiguity
2. no relevant concept clears threshold
3. concepts المتاحة generic جدًا
4. procedural skill alone sufficient
5. concept activation expected to add noise more than value

### why important
لأن success الحقيقية لـ Concept Engine ليست في تفعيلها دائمًا، بل في معرفتها متى **تسكت**.

---

# 9) العلاقة مع Cognitive Economy
Concept Selectivity ليست مشكلة محلية فقط، بل اقتصادية أيضًا.

كل concept مفعلة تستهلك:
- context space
- attention budget
- interpretation bandwidth
- verifier coupling

إذًا concept selection جزء من:
# **cognitive allocation**

---

# 10) العلاقة مع Task Framing
framing تساعد في الانتقاء:
- primary frame تعطي family prior
- secondary frames قد ترفع concept أخرى
- لكن ambiguity العالية لا تعني تفعيل كل concepts الممكنة

إذًا:
- framing guides
- selectivity filters

---

# 11) العلاقة مع TaskCase contracts
TaskCase hidden contract الآن يجب أن تكون مصدرًا قويًا للـ selectivity.

## important signals
- `required_properties`
- `forbidden_shortcuts`
- `diagnostic_purpose`

### implication
concepts التي ترتبط بهذه signals يجب أن تُعطى وزنًا أعلى من concepts family-generic فقط.

---

# 12) العلاقة مع reasoning runtime
هناك ثلاث درجات من تأثير concept:

## Level A — Hint-only
مذكورة كhint عامة

## Level B — Directive
تغير قالب reasoning أو تمنع shortcut محددة

## Level C — Control influence
تؤثر على retrieval / verification / tier routing

### recommendation
المفاهيم القوية يجب أن تتحرك من Hint-only إلى Directive/Control influence.

---

# 13) Failure modes في selectivity
### Failure Mode 1 — Over-activation
مفاهيم كثيرة في كل task.

### Failure Mode 2 — Under-activation
وجود concepts نافعة لكن لا تُستخدم.

### Failure Mode 3 — Redundant activation
عدة concepts متشابهة تتكرر بلا فائدة إضافية.

### Failure Mode 4 — Family lock-in
تفعيل concept لمجرد family match حتى لو contract mismatch.

### Failure Mode 5 — Contract myopia
تفعيل concepts مرتبطة بـ contract فقط وتجاهل family/semantic fit.

---

# 14) Minimal implementation path
الخطوة الحالية المقترحة:

## Step 1
إرجاع `select_applicable_concepts` من top-k broad إلى:
- scored candidates
- explicit ActivationDecision objects

## Step 2
فرض حد أقصى صغير:
- top-1 أو top-2

## Step 3
إضافة threshold صريح
أي concept تحت score معين لا تُفعل

## Step 4
إضافة redundancy penalty
إذا كانت concept الثانية لا تضيف جديدًا، تُسقط

## Step 5
إضافة report جديد:
- concept selectivity report

---

# 15) Metrics جديدة نحتاجها
## Selectivity metrics
1. concept_activation_rate
2. avg concepts per task
3. zero-concept task rate
4. concept utility when activated
5. redundant concept activation rate
6. activation precision (كم مرة كانت concept المفعلة helpful فعلاً)

---

# 16) ما هو النجاح هنا؟
### Success criteria
- activation rate تنخفض من overuse إلى selective use
- performance لا تنهار
- أو تتحسن under stricter regimes
- concept utility per activation ترتفع
- concept_count قد تبقى نفسها، لكن **activation discipline** تتحسن

---

# 17) القرار التالي بعد هذه الوثيقة
الخطوة التالية يجب أن تكون تنفيذية مباشرة:
1. تعديل concept selection لتنتج activation scores
2. تقييد max active concepts
3. بناء selectivity report
4. إعادة تشغيل `prototype_v3b_curriculum`
5. مقارنة:
   - performance
   - cost
   - concept_activation_rate
   - concept utility

وهذا سيكون الاختبار الحقيقي التالي لنضج Thesis 1.
