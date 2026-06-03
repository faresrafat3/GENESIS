# Virtual-GENESIS Current Regime Memo (Arabic)

## الغرض
هذه الوثيقة تثبّت **الوضع التشغيلي الحالي الأفضل** للمشروع بعد سلسلة طويلة من:
- التنظير
- الـ formal specs
- prototype slices
- evaluation redesign
- taskcase migration
- perturbation curriculum
- concept selectivity tuning

الهدف منها أن نعرف بوضوح:
1. ما الذي نعتبره الآن regime التشغيلية الأفضل مؤقتًا؟
2. ما الذي نثق فيه؟
3. ما الذي ما زال غير مستقر؟
4. ما أفضل slices للتقييم؟
5. ما defaults الحالية المهمة؟
6. ما الأولويات التالية؟

---

# 1) الحكم التنفيذي الحالي
المشروع لم يعد:
- فكرة فقط
- أو specs فقط
- أو prototype toy فقط

بل أصبح:
# **small but principled experimental system**

مع:
- Task ingestion
- Blackboard runtime
- Memory OS minimal
- Concept formation minimal
- Economy-aware tier routing
- TaskCase-based evaluation
- Curriculum-based evaluation regime

---

# 2) ما الذي نعتبره الآن “Core Runtime Regime”؟

## Runtime stack الحالية
1. Task ingress مع family scores + ranked frames + ambiguity signal
2. Blackboard task-local state
3. Memory retrieval typed
4. Concept-aware retrieval
5. Reasoning runtime family-sensitive
6. Verification runtime contract-aware
7. Economy-aware tier routing
8. Ledger logging
9. Episode persistence
10. Periodic concept cycle

### حكم
هذه هي الآن النواة التشغيلية الأساسية التي نتحرك فوقها.

---

# 3) ما هي السياسات الافتراضية الحالية؟

## 3.1 Concept Selectivity default
### الحالية
- `max_active_concepts = 1`
- `min_activation_score = 7`

### سبب اعتمادها
- خفض over-activation مقارنة بالوضع الأرخى
- حفظ gains الأساسية داخل `prototype_v3b_curriculum`
- لم يظهر أن second concept تضيف عائدًا واضحًا في الشريحة الحالية

### مستوى الثقة
**متوسط**
ليست نهائية، لكنها أفضل default مؤقتة حاليًا.

---

## 3.2 Tier routing regime
### الحالية
- cheap / tier_1 هو default balanced worker
- premium / tier_2 only when needed
- concept support can suppress unnecessary escalation
- ambiguity can block cheap collapse and keep balanced tier

### مستوى الثقة
**مرتفع نسبيًا**
هذه من أكثر أجزاء النظام استقرارًا حتى الآن.

---

## 3.3 Verification regime
### الحالية
- TaskCase-aware
- required_properties + forbidden_shortcuts
- framing-aware but no longer broadly permissive

### مستوى الثقة
**متوسط**
أكثر نضجًا من البداية، لكنه ما يزال قابلًا للتحسن في الحالات الأصعب.

---

# 4) ما هي أفضل evaluation slices حاليًا؟

## 4.1 Calibration slices
### `prototype_v2`
- clean
- مفيدة كمرجع بسيط
- لكنها saturating الآن

### `prototype_v3` / old forms
- useful historical references
- لكنها ليست primary evidence now

### الحكم
تُستخدم كـ calibration / sanity only.

---

## 4.2 Primary thesis slice
### `prototype_v3b_curriculum`
هذه هي **أفضل thesis-testing regime حاليًا**.

### لماذا؟
- أقل تشبعًا من v2/v5
- أقل فوضى من v4
- TaskCase-based
- curriculum generated programmatically
- تظهر thesis-level differences بوضوح معقول

### الحكم
تُستخدم الآن كـ **Primary Thesis Evaluation Regime**.

---

## 4.3 Diagnostic slice
### `prototype_v4_cases`
- boundary-heavy
- framing ambiguity مرتفعة
- ممتازة لاكتشاف bottlenecks upstream/downstream
- غير مناسبة وحدها كحكم نهائي على theses

### الحكم
تبقى **Diagnostic Slice** رسمية.

---

# 5) ما الذي نثق فيه الآن؟

## Strong confidence
### A. Thesis 2 strong signal
الـ economy-aware path consistently تقدم cost frontier ممتازة.

### B. Need for TaskCase-based evaluation
التجارب أثبتت أن prompt-only tasks لم تعد كافية.

### C. Need for curriculum/perturbation layer
hand-authored static slices وحدها غير كافية بعد الآن.

## Medium confidence
### D. Thesis 1 has meaningful support
concept-aware path يمكنها أن تتفوق، لكن gainsها أكثر حساسية لتصميم الشريحة والـ contract والـ selectivity.

### E. Task framing is a real upstream variable
ليست مجرد خطوة إدارية بسيطة.

## Low-to-medium confidence
### F. current concept policy is globally optimal
ما زلنا لا نعرف إن كان top-1/score7 مناسبًا لكل families أو regimes.

---

# 6) ما الذي ما زال غير مستقر؟

## 6.1 Concept leverage under harder hidden contracts
بعض الشرائح أظهرت أن المفاهيم useful، لكن ما زال مطلوبًا ضبط أثرها بدقة تحت ضغط أعلى.

## 6.2 Family-specific selectivity
ما زلنا لا نعرف إن كانت synthesis تحتاج سياسة مفاهيم مختلفة عن comparison أو procedure.

## 6.3 premium ROI under richer regimes
حتى الآن ممتازة، لكن نحتاج شرائح أغنى قليلاً لاحقًا.

## 6.4 Evaluation ceiling problem
كلما تحسن النظام، بعض الشرائح القديمة تتشبع. هذا يعني أن evaluation نفسها ستظل moving target.

---

# 7) الحالة الحالية للـ theses

## Thesis 1
**Concept Formation beats retrieval-only adaptation**

### Current status
- **Supported, but conditionally**
- strongest support on `prototype_v3b_curriculum`
- depends on:
  - concept quality
  - concept selectivity
  - taskcase contract quality
  - non-saturated evaluation regime

### concise judgment
ليست محسومة نهائيًا، لكنها الآن **أقوى من مرحلة hypothesis فقط**.

---

## Thesis 2
**Cognitive Economy beats stronger-model-only scaling**

### Current status
- **Strongly supported in current prototype regime**
- repeated evidence that economy-aware path gives large cost savings with limited or no performance loss in suitable slices

### concise judgment
هذه هي الأطروحة الأكثر نضجًا واستقرارًا حتى الآن.

---

## Combined regime
### Current status
- currently the strongest operational path
- often near-premium success with low cost and light concept use

### concise judgment
**best current operating regime** لكن ما زال تحت experimental qualification لا production claim.

---

# 8) ما الذي نعتبره “Current Best Operating Regime”؟
نقترح أن الـ current best regime مؤقتًا هي:

## Core regime
- TaskCase-based evaluation where available
- Ranked framing with ambiguity signals
- Memory OS active
- Concept-aware retrieval active
- Concept selectivity: top-1 / score7
- Economy-aware routing active
- Premium escalation only when justified
- Curriculum-based thesis testing via `prototype_v3b_curriculum`
- Boundary diagnostics via `prototype_v4_cases`

هذه هي الصيغة الحالية التي نعتمدها كمرجع تشغيل مؤقت.

---

# 9) ما الذي نوقفه الآن؟

## We pause for now:
- adding new major theory layers
- adding contradiction/anomaly runtime full
- adding sparse committee system
- expanding to multimodal/OS/web heavy runtime
- writing more general docs unless directly tied to next step

### rationale
لأن النظام الحالي ما زال يعطي عائدًا عاليًا من:
- tuning the current regime
- improving concept usage
- improving evaluation pressure

---

# 10) ما الذي نفعله بعد ذلك؟
نقترح أولويتين فقط، بترتيب واضح:

## Priority 1 — Family-specific concept selectivity
نسأل:
- comparison: هل top-1 تكفي؟
- synthesis: هل تحتاج top-2 أو threshold مختلفة؟
- procedure: هل تحتاج top-0 أحيانًا؟

هذا هو الامتداد الطبيعي المباشر لـ Thesis 1 الآن.

## Priority 2 — Better curriculum pressure
تطوير operators أقوى تدريجيًا، لكن دون العودة إلى فوضى v4.

---

# 11) ماذا نعتبر إنذارًا؟
إذا حدث واحد أو أكثر من التالي، يجب أن نعيد تقييم regime:
1. concept activation تعود إلى 1.0 بلا gain واضح
2. premium invocations ترتفع sharply without payoff
3. slices الجديدة تتشبع بسرعة مرة أخرى
4. framing ambiguity leaks into thesis slices بشكل كبير
5. family-specific performance diverges بقوة دون explanation

---

# 12) الحكم النهائي
## Current best understanding
المشروع الآن يملك:
- نواة تشغيلية واضحة
- regime تقييم ناضجة نسبيًا
- evidence أولية قوية لـ Thesis 2
- evidence واعدة ومعتبرة لـ Thesis 1
- وأفضل حالة تشغيلية مبدئية حتى الآن هي:

# **Concept-aware + Economy-aware path under TaskCase-based curriculum evaluation**

### لكن
يجب أن نظل نتعامل معه كـ:
- **experimental operating regime**
وليس final architecture claim.

وهذا بالضبط الوضع الصحيح لنظام بحثي وتنفيذي ناضج في هذه المرحلة.
