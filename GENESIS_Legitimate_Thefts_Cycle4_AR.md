# Virtual-GENESIS - السرقات الشرعية: الدورة الرابعة
# Legitimate Thefts - Cycle 4 (Broader Domain - Option D)

> Document Type: Legitimate Theft Registry
> Status: Current
> Date: 2026-06-01
> Scope: Covers new thefts 5.39-5.44 for Cycle 4 development (Broader Domain - Option D)

---

## مقدمة

هذه الوثيقة توثق "السرقات الشرعية" الجديدة التي تم استخدامها في الدورة الرابعة من تطوير Virtual-GENESIS.
هذه الدورة تركز على اختبار ما اذا كان النظام ينتقل ويعمل خارج الشريحة التحليلية الاصلية (comparison, synthesis, procedure) نحو مجالات مهام جديدة نوعيا.
الهدف: قياس قابلية النقل (portability) للآليات المعرفية التي بنيناها -- هل تكوين المفاهيم والاقتصاد المعرفي والنظريات المحلية تنفع في عائلات مهام لم تصمم من اجلها؟

كل سرقة تتبع المنهجية المعتمدة: ناخذ مجهود الغير من ابحاث ومشاريع وافكار، نستخلص الجوهر القابل للتشغيل، ونحوله الى مكون عملي في نظامنا مع توثيق كامل لما اخذناه وما تركناه وما اصبح عندنا.

---

# السرقات الجديدة من الابحاث

---

## 5.39 من Bloom's Taxonomy (Bloom et al., 1956; Anderson & Krathwohl, 2001)
### ما الذي أخذناه؟
- التحليل كعملية معرفية عليا متمايزة عن الفهم والتطبيق: التصنيف يفرق بين "تحلل" (تكسير المادة الى اجزاء، ايجاد العلاقات، تحديد الدوافع) وبين العمليات الادنى
- التحليل يتطلب تحديد السلاسل السببية (causal chain identification) والعلاقات بين الاجزاء
- العمليات المعرفية العليا لها متطلبات تشغيلية مختلفة عن العمليات الدنيا
- [Bloom et al., 1956](https://doi.org/10.1002/9780470479216.corpsy0128) [Anderson & Krathwohl, 2001](https://doi.org/10.1007/978-94-007-0753-5_154)

### ما الذي لم نأخذه الآن؟
- التصنيف الكامل من 6 مستويات (remember, understand, apply, analyze, evaluate, create)
- لم ننفذ evaluate او create كعائلات منفصلة
- البعد الثاني للتصنيف المحدث (Knowledge Dimension: factual, conceptual, procedural, metacognitive)
- الترتيب الهرمي الصارم بين المستويات (ان كل مستوى يتطلب اتقان ما قبله)
- ادوات التقييم التعليمية المبنية على التصنيف

### ماذا أصبح عندنا؟
- **عائلة المهام `analysis`** بكلمات مفتاحية للتصنيف: root cause, causal, diagnose, analyze, why did, system failure, breakdown, factor, impact analysis
- **خصائص مطلوبة (required_properties)** تتطلب التفكير السببي: causal reasoning, root identification, factor analysis
- **تهيئة محرك المفاهيم**: استراتيجية semantic_balanced مع min_score 6 (اقل من المجالات الاصلية لان المجال جديد)
- **6 حالات مهام تحليلية** في prototype_v7_broader_domain.py: تستهدف تحليل الاسباب الجذرية، الاستنتاج السببي، تشخيص الانظمة

---

## 5.40 من Information Extraction / Sarawagi (2008, "Information Extraction")
### ما الذي أخذناه؟
- التعريف الجوهري لمهمة استخراج المعلومات (IE): تحويل نص غير منظم او شبه منظم الى سجلات منظمة بحقول محددة النوع
- مفهوم ملء الخانات (slot filling): تحديد واستخراج قطع معلومات محددة ووضعها في خانات معرفة مسبقا
- التمييز بين المعلومات المطلوبة والضوضاء المحيطة بها في النص الخام
- [Sarawagi, 2008](https://doi.org/10.1561/1500000003)

### ما الذي لم نأخذه الآن؟
- نماذج التعرف على الكيانات المسماة (NER models)
- تسلسل CRF (Conditional Random Fields) للوسم
- خطوط انابيب استخراج العلاقات (relation extraction pipelines)
- حل الاشارات المرجعية (coreference resolution)
- المكدس الكامل لاستخراج المعلومات الذي يتطلب نماذج تعلم آلي
- Open Information Extraction والاستخراج بدون مخطط مسبق

### ماذا أصبح عندنا؟
- **عائلة المهام `extraction`** بكلمات مفتاحية: extract, identify all, list every, find each, pull out, slot, field, structured, parse, entities
- **خصائص مطلوبة** تتطلب استخراج كامل الحقول ومخرجات منظمة: complete field extraction, structured output, no hallucinated fields
- **تهيئة محرك المفاهيم**: استراتيجية contract_heavy مع min_score 7 (دقة عالية لان الاستخراج يتطلب صرامة)
- **6 حالات مهام استخراجية** تتطلب سحب بيانات منظمة من نصوص مشوشة

---

## 5.41 من Classical AI Planning / STRIPS (Fikes & Nilsson, 1971) / PDDL (McDermott et al., 1998)
### ما الذي أخذناه؟
- فكرة ان التخطيط عملية معرفية متمايزة: توليد تسلسل اجراءات لتحقيق اهداف مع احترام الشروط المسبقة والقيود
- مفهوم ترتيب التبعيات (dependency ordering): الاجراء B يتطلب اكتمال الاجراء A اولا
- القيود كجزء جوهري من التخطيط: ليس اي ترتيب يصلح، بل يجب احترام المتطلبات المسبقة
- [Fikes & Nilsson, 1971](https://doi.org/10.1016/0004-3702(71)90010-5) [McDermott et al., 1998](https://homepages.inf.ed.ac.uk/mfourman/tools/propplan/pddl.pdf)

### ما الذي لم نأخذه الآن؟
- شكلانية STRIPS (المشغلات، الشروط المسبقة، قوائم الاضافة والحذف)
- تعريفات PDDL للمجال والمشكلة (domain/problem definitions)
- خوارزميات البحث عن الخطط (forward chaining, backward chaining, partial-order planning, GraphPlan)
- التخطيط تحت عدم اليقين (probabilistic planning)
- الجدولة الزمنية (temporal planning / scheduling)
- التخطيط متعدد الوكلاء (multi-agent planning)

### ماذا أصبح عندنا؟
- **عائلة المهام `planning`** بكلمات مفتاحية: plan, schedule, sequence, steps to, organize, prioritize, arrange, workflow, dependencies, before/after
- **خصائص مطلوبة** تتطلب خطوات متسلسلة وارضاء القيود وترتيب التبعيات: sequenced steps, constraint satisfaction, dependency ordering
- **تهيئة محرك المفاهيم**: استراتيجية semantic_balanced مع min_score 6
- **6 حالات مهام تخطيطية** بسيناريوهات متعددة الخطوات وثقيلة القيود

---

## 5.42 من Transfer Learning / Domain Adaptation (Pan & Yang, 2010, "A Survey on Transfer Learning")
### ما الذي أخذناه؟
- السؤال المركزي للتعلم بالنقل: هل المعرفة المكتسبة في مجال واحد تساعد في مجال آخر؟
- مفهوم قياس النقل: النقل الايجابي (يساعد)، النقل السلبي (يضر)، ومعامل النقل كنسبة الاداء مع/بدون المعرفة المنقولة
- التفريق بين المجال المصدر (source domain) والمجال الهدف (target domain) والعلاقة بينهما
- [Pan & Yang, 2010](https://doi.org/10.1109/TKDE.2009.191)

### ما الذي لم نأخذه الآن؟
- طرق النقل المبنية على الخصائص (feature-based transfer)
- النقل المبني على الامثلة (instance-based transfer)
- مشاركة المعلمات (parameter sharing) بين النماذج
- محاذاة التوزيعات (distribution matching) باستخدام MMD او CORAL
- شبكات النقل العميق (deep transfer networks)
- التكيف متعدد المصادر (multi-source domain adaptation)

### ماذا أصبح عندنا؟
- **دالة `generate_domain_transfer_report()`** التي تقيس:
  - `concept_activation_rate_per_family`: نسبة تفعيل المفاهيم في كل عائلة (اصلية وجديدة)
  - `transfer_coefficients` لكل مفهوم: هل المفهوم ينتقل من العائلات الاصلية للعائلات الجديدة؟
  - `family_pair_transfer_matrix`: مصفوفة توضح اي ازواج عائلات تنتقل المفاهيم بينها بشكل افضل
  - `overall_transfer_rate`: النسبة الاجمالية للنقل المفاهيمي عبر المجالات

---

## 5.43 من Curriculum Learning (Bengio et al., 2009, "Curriculum Learning")
### ما الذي أخذناه؟
- فكرة التقييم التدريجي بالصعوبة: اختبار النظام على متغيرات متزايدة الصعوبة من المهام
- تطبيق منهج الصعوبة التدريجية على مهام المجالات الجديدة باستخدام البنية التحتية للاضطراب (perturbation infrastructure) من الدورة الثانية
- المنهج كاداة تشخيص: اين ينكسر النظام عندما تزداد الصعوبة في مجالات لم يصمم لها؟
- [Bengio et al., 2009](https://doi.org/10.1145/1553374.1553380)

### ما الذي لم نأخذه الآن؟
- التصميم التلقائي للمنهج (automatic curriculum design)
- التعلم الذاتي الخطى (self-paced learning)
- بروتوكولات المنهج بين المعلم والطالب (teacher-student curriculum)
- ترجيح العينات بناء على الخسارة (loss-based sample weighting)
- المناهج التكيفية التي تتغير اثناء التدريب

### ماذا أصبح عندنا؟
- **دالة `build_v7_broader_domain_curriculum()`** التي تطبق منهج الاضطراب من 6 مستويات على جميع مهام التوسع المجالي الـ 18
- **108 حالة مهمة** في المنهج الكامل (18 مهمة اساسية x 6 مستويات)
- اختبار ما اذا كان النظام يحافظ على الاداء تحت ضغط متزايد في المجالات الجديدة
- استخدام نفس مشغلات الاضطراب من الدورة الثانية (support_removal, evidence_reordering, contrast_weakening, structure_weakening, stronger_shortcut_lures) مما يتيح مقارنة مباشرة بين المجالات القديمة والجديدة

---

## 5.44 من Cross-Domain Generalization / Meta-Learning (Thrun, 1998, "Learning to Learn")
### ما الذي أخذناه؟
- سؤال التعلم الفوقي: هل التعلم-كيف-تتعلم على بعض المهام ينتقل الى انواع مهام جديدة تماما؟
- مفهوم "حكم القابلية للنقل" (portability verdict): قياس ما اذا كانت الآليات المعرفية (المفاهيم، النظريات، توجيه الاقتصاد) المبنية على مجموعة مهام تعمل على مهام مختلفة نوعيا
- التفريق بين التعميم داخل المجال (in-domain generalization) والتعميم عبر المجالات (cross-domain generalization)
- [Thrun, 1998](https://doi.org/10.1007/978-1-4615-5529-2_1)

### ما الذي لم نأخذه الآن؟
- خوارزمية MAML (Model-Agnostic Meta-Learning)
- بروتوكولات التعلم من امثلة قليلة (few-shot meta-learning)
- اخذ عينات من توزيعات المهام (task distribution sampling)
- التحسين الفوقي المبني على التدرج (gradient-based meta-optimization)
- بنية الشبكات العصبية للتعلم الفوقي

### ماذا أصبح عندنا؟
- **محرك تقييم التوسع المجالي (run_broader_domain_eval.py)** الذي يشغل جميع الشروط الستة ضد عائلات مهام جديدة نوعيا ويقيس:
  - هل تكوين المفاهيم يساعد في العائلات الجديدة؟ (concept formation portability)
  - هل توجيه الاقتصاد يعمم؟ (economy routing generalization)
  - هل رافعة النظريات تنتقل؟ (theory leverage transfer)
- **حكم القابلية للنقل (portability_verdict)** كمخرج منظم يلخص هذه الاجابات
- اذا كانت الآليات تعمل على العائلات الجديدة = **نقل ايجابي** = الآليات تمسك ببنية حقيقية وليست مجرد ملائمة للبيانات الاصلية

---

# ملخص التغطية

| # | المصدر | المكون الناتج | النوع |
|---|--------|--------------|-------|
| 5.39 | Bloom's Taxonomy (Bloom et al., 1956; Anderson & Krathwohl, 2001) | عائلة المهام analysis + تهيئة المحرك + 6 حالات مهام | سرقة جديدة |
| 5.40 | Information Extraction (Sarawagi, 2008) | عائلة المهام extraction + تهيئة المحرك + 6 حالات مهام | سرقة جديدة |
| 5.41 | Classical AI Planning / STRIPS / PDDL (Fikes & Nilsson 1971; McDermott et al 1998) | عائلة المهام planning + تهيئة المحرك + 6 حالات مهام | سرقة جديدة |
| 5.42 | Transfer Learning (Pan & Yang, 2010) | generate_domain_transfer_report + transfer_coefficients + family_pair_matrix | سرقة جديدة |
| 5.43 | Curriculum Learning (Bengio et al., 2009) | build_v7_broader_domain_curriculum (18 x 6 = 108 حالة) | سرقة جديدة |
| 5.44 | Cross-Domain Generalization / Meta-Learning (Thrun, 1998) | run_broader_domain_eval + portability_verdict | سرقة جديدة |

---

*نهاية وثيقة السرقات الشرعية - الدورة الرابعة*
