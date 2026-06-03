# Virtual-GENESIS - السرقات الشرعية: الموجة الثالثة
# Legitimate Thefts - Wave 3 (Self-Benchmarking + Productive Forgetting)

> Document Type: Legitimate Theft Registry
> Status: Current
> Date: 2026-06-01
> Scope: Covers new thefts 5.45-5.54 for Wave 3 development (Self-Benchmarking H8 + Productive Forgetting H3)

---

## مقدمة

هذه الوثيقة توثق "السرقات الشرعية" الجديدة التي تم استخدامها في الموجة الثالثة من تطوير Virtual-GENESIS.
هذه الموجة تركز على ميزتين اساسيتين من Tier S في البرنامج البحثي:
1. Self-Benchmarking (H8): بناء نظام تقييم ذاتي النمو يحول اشارات الفشل الى ضغط تقييمي جديد
2. Productive Forgetting (H3): بناء سياسة نسيان منتج تمنع تلوث الذاكرة وتحافظ على جودة الاسترجاع

كل سرقة تتبع المنهجية المعتمدة: ناخذ مجهود الغير من ابحاث ومشاريع وافكار، نستخلص الجوهر القابل للتشغيل، ونحوله الى مكون عملي في نظامنا مع توثيق كامل لما اخذناه وما تركناه وما اصبح عندنا.

---

# السرقات الجديدة من الابحاث

---

## 5.45 من FunSearch (DeepMind 2023, Romera-Paredes et al.)
### ما الذي أخذناه؟
- فكرة ان النظام يمكن ان يبحث في فضاء artefacts (في حالتنا: اختبارات) تحت اشراف evaluator
- FunSearch يبحث عن functions تحقق هدف رياضي; نحن نبحث عن TaskCases تكشف نقاط ضعف
- المبدأ العام: search guided by evaluation over generated artefacts
- [Romera-Paredes et al., 2023](https://www.nature.com/articles/s41586-023-06924-6)

### ما الذي لم نأخذه الآن؟
- LLM-based program search (البحث عبر توليد برامج بواسطة LLM)
- evolutionary mutation of code (طفرات تطورية على الكود)
- scoring via mathematical optimality (التقييم عبر المثالية الرياضية)
- multi-island population architecture
- الـ prompt evolution الخاص بـ FunSearch

### ماذا أصبح عندنا؟
- **`benchmark_generator.py`** يولد TaskCase objects من anomaly candidates تحت اشراف verifier regime
- كل anomaly candidate (property_gap, shortcut_pattern, contradiction_pattern) يتحول الى TaskCase تشخيصية
- التوليد يتم عبر source_type mapping الى prompt templates تستهدف اعادة انتاج الخلل
- diagnostic_purpose=["anomaly_derived", "self_benchmark"] توسم كل حالة مولدة

---

## 5.46 من AutoTTS / Auto Test-Time Strategies (extension of 5.13)
### ما الذي أخذناه؟
- فكرة ان البيئة تكتشف heuristics الاختبار الخاصة بها
- AutoTTS تولد وتقيم test-time strategies; نحن نولد ونقيم اختبارات تشخيصية
- المبدأ: self-discovered testing heuristics بدلا من heuristics مصممة يدويا
- الدورة: generate -> evaluate -> retain what works -> generate again

### ما الذي لم نأخذه الآن؟
- LLM generation of strategies (توليد استراتيجيات عبر LLM)
- prompt-based search (بحث مبني على prompts)
- online adaptation during inference (تكيف اثناء الاستدلال)
- الـ meta-prompting الخاص بـ AutoTTS
- strategy composition operators

### ماذا أصبح عندنا؟
- **`run_self_benchmark_cycle`** يكتشف blind spots ويولد اختبارات جديدة كـ self-discovered testing heuristics
- الدورة الكاملة: تقييم اولي -> تحليل anomalies -> توليد TaskCases جديدة -> تقييم ثان -> قياس diagnostic value
- النظام يبني curriculum اختبار خاص به من اشارات الفشل

---

## 5.47 من Novelty Search (Lehman & Stanley, 2011)
### ما الذي أخذناه؟
- مبدأ diversity-driven search بدلا من objective-only search
- ليس المهم ان الاختبار "اصعب" بل ان يكون "مختلف" عن الموجود
- التغطية (coverage) كهدف بحث: البحث عن المناطق غير المكتشفة بدلا من تحسين هدف واحد
- [Lehman & Stanley, 2011](https://doi.org/10.1162/EVCO_a_00025)

### ما الذي لم نأخذه الآن؟
- genetic algorithm operators (مشغلات الخوارزمية الجينية)
- behavioral characterization spaces (فضاءات توصيف السلوك)
- novelty archive (ارشيف الجدة)
- المقاييس المتجهية للمسافة السلوكية
- speciation mechanisms

### ماذا أصبح عندنا؟
- **`blind_spot_discovery.py`** يبحث عن تغطية التنوع (coverage matrix) ويكتشف المناطق غير المختبرة
- يبني coverage_matrix عبر (family, perturbation_type, difficulty_class) combinations
- يكتشف untested_combinations: مناطق لم يصلها اي اختبار
- يكتشف suspiciously_easy_regions: مناطق بنسبة نجاح 100% (مشتبه بها)
- coverage_ratio يقيس نسبة التغطية الفعلية من التغطية الممكنة

---

## 5.48 من Metamorphic Testing (Chen et al., 2018)
### ما الذي أخذناه؟
- فكرة ان العلاقات بين مدخلات الاختبار (metamorphic relations) تولد اختبارات جديدة بدون oracle
- اذا عرفنا ان perturbation X يجب الا يغير النتيجة، فاي تغير يكشف خلل
- المبدأ: التفاوت في النتائج عبر conditions يكشف خصائص تشخيصية
- [Chen et al., 2018](https://doi.org/10.1145/3143561)

### ما الذي لم نأخذه الآن؟
- formal metamorphic relation specification (التعريف الرسمي للعلاقات التحويلية)
- automated oracle derivation (اشتقاق تلقائي للـ oracle)
- full MR catalog (كتالوج كامل للعلاقات التحويلية)
- source-input to follow-up-input transformations
- MR-based test case prioritization

### ماذا أصبح عندنا؟
- **`diagnostic_value.py`** يقيس كيف تتفاوت النتائج عبر conditions
- الصيغة: `4 * p * (1 - p)` حيث p = نسبة النجاح عبر الـ conditions
- القيمة = 0.0 عندما كل الـ conditions تعطي نفس النتيجة (غير مميز)
- القيمة = 1.0 عندما الانقسام 50/50 (اقصى تمييز بين الـ conditions)
- التفاوت العالي يكشف ان الاختبار يميز بين حالات مختلفة (discriminative)

---

## 5.49 من Curriculum Self-Play (AlphaZero concept, Silver et al.)
### ما الذي أخذناه؟
- فكرة ان النظام يولد تحدياته الخاصة (self-play)
- بدلا من benchmark خارجي ثابت، النظام يبني curriculum من anomalies و blind spots
- الدورة المغلقة: evaluate -> discover weakness -> generate challenge -> re-evaluate
- [Silver et al., 2017](https://doi.org/10.1038/nature24270)

### ما الذي لم نأخذه الآن؟
- game-theoretic formulation (الصياغة في اطار نظرية الالعاب)
- MCTS (Monte Carlo Tree Search)
- neural value/policy networks (شبكات القيمة والسياسة)
- symmetric self-play (اللعب الذاتي المتماثل)
- Elo rating systems
- continuous self-play loops

### ماذا أصبح عندنا؟
- **`run_self_benchmark_cycle`** دورة كاملة تبدا بالتقييم، تكتشف الفجوات، تولد اختبارات، تعيد التقييم
- 7 خطوات متكاملة: compare_conditions -> anomaly_candidates -> blind_spots -> generate_cases -> re-evaluate -> diagnostic_value -> combined_report
- النتيجة: النظام يولد ضغط تقييمي جديد من داخله بدلا من الاعتماد على مصمم خارجي

---

## 5.50 من Ebbinghaus Forgetting Curve (1885)
### ما الذي أخذناه؟
- مبدأ ان الذكريات تضعف مع الزمن بدون reinforcement
- معدل الضعف يعتمد على الزمن منذ آخر استخدام
- Staleness = (current_tick - last_accessed) كمقياس اساسي للتقادم
- [Ebbinghaus, 1885](https://doi.org/10.1037/10011-000)

### ما الذي لم نأخذه الآن؟
- exponential decay formula الدقيقة (استخدمنا linear decay ابسط)
- spacing effect optimization (تحسين تاثير التباعد)
- مفهوم overlearning (التعلم الزائد)
- savings method للقياس
- multi-trial retention curves

### ماذا أصبح عندنا؟
- **`store.apply_decay(decay_rate)`** يخفض decay_score بناء على `(current_tick - last_accessed) * rate`
- كل ذاكرة active تفقد من decay_score بما يتناسب مع عمرها منذ آخر استخدام
- decay_score مقيد بين 0.0 و 1.0
- الذكريات المستخدمة حديثا (last_accessed قريب من current_tick) تتأثر اقل
- decay_rate = 0.05 كقيمة افتراضية في الـ pipeline

---

## 5.51 من Retrieval-Induced Forgetting (Anderson et al., 1994)
### ما الذي أخذناه؟
- مبدأ ان استرجاع بعض الذكريات يضعف الذكريات المنافسة
- الاسترجاع ليس محايدا بل يعيد تشكيل landscape الذاكرة
- كل عملية access تقوي المسترجع وتضعف الباقي نسبيا (عبر الـ decay الطبيعي)
- [Anderson, Bjork & Bjork, 1994](https://doi.org/10.1037/0278-7393.20.5.1063)

### ما الذي لم نأخذه الآن؟
- inhibitory control mechanism (آلية التحكم المثبط)
- part-set cuing effects (تاثيرات التلميح الجزئي)
- category-exemplar paradigm (نموذج الفئة-المثال)
- retrieval practice paradigm الكامل
- strength-dependent competition models

### ماذا أصبح عندنا؟
- **`record_access(memory_id, tick)`** يعزز الذاكرة المسترجعة: `access_count += 1` و `last_accessed = tick`
- **`apply_decay`** يضعف غير المسترجعة تلقائيا (كلما زاد الفرق بين tick الحالي و last_accessed)
- الاثر الصافي: الذكريات المسترجعة تصبح اقوى، والذكريات غير المسترجعة تضعف تدريجيا
- هذا يخلق competitive dynamics بين الذكريات بدون inhibition صريح

---

## 5.52 من Memory Reconsolidation (Nader et al., 2000)
### ما الذي أخذناه؟
- مبدأ ان الذكريات المعاد تنشيطها تصبح قابلة للتحديث (labile state)
- اعادة التنشيط فرصة للتعديل لا مجرد الاسترجاع
- عملية الاسترجاع ذاتها تغير حالة الذاكرة (decay_score, utility, last_accessed)
- [Nader, Schafe & LeDoux, 2000](https://doi.org/10.1038/35021052)

### ما الذي لم نأخذه الآن؟
- protein synthesis inhibition paradigm (نموذج تثبيط تخليق البروتين)
- reconsolidation window timing (توقيت نافذة اعادة التوحيد)
- boundary conditions (شروط الحدود)
- destabilization-reconsolidation sequence الكاملة
- pharmacological intervention studies

### ماذا أصبح عندنا؟
- الذاكرة المسترجعة (via `record_access`) يمكن ان يتغير `utility_score` و `decay_score` بناء على النتيجة الجديدة
- `compute_memory_utility` يعيد حساب الفائدة عند كل تقييم (الذاكرة ليست ثابتة)
- outcome_quality يتغير اذا meta['good_enough'] تغير بعد الاسترجاع
- كل عملية وصول هي فرصة لتحديث حالة الذاكرة بالكامل

---

## 5.53 من Desirable Difficulties (Bjork, 1994)
### ما الذي أخذناه؟
- مبدأ ان الصعوبة المناسبة تحسن الاحتفاظ طويل الامد
- ليس كل سهولة استرجاع مفيدة; الانتقائية تقوي ما يبقى
- ازالة الذكريات منخفضة الفائدة تحسن signal-to-noise ratio للذكريات المتبقية
- [Bjork, 1994](https://doi.org/10.1016/S0079-7421(08)60016-2)

### ما الذي لم نأخذه الآن؟
- interleaving effects (تاثيرات التداخل)
- generation effect (تاثير التوليد)
- variability of practice (تنوع الممارسة)
- full desirable difficulty taxonomy (التصنيف الكامل للصعوبات المرغوبة)
- spacing schedules optimization

### ماذا أصبح عندنا؟
- **`forgetting_policy`** لا تحتفظ بكل شيء; بازالة الضوضاء تقوي ما يبقى
- `get_active_memories()` يرجع فقط الذكريات النشطة (بعد ازالة المؤرشفة والمهملة)
- utility_threshold يحدد حد الفائدة الادنى للبقاء نشطا
- max_archive_ratio يمنع الازالة الجماعية (حماية من over-forgetting)
- النتيجة: retrieval quality تتحسن لان المنافسين الضعفاء ازيلوا

---

## 5.54 من MemOS (extension of 5.15, MemoryOS lifecycle management)
### ما الذي أخذناه؟
- مفهوم lifecycle management للذاكرة مع عمليات صريحة: active -> archived -> deprecated -> deleted
- الذاكرة لها حالات ومسارات انتقال واضحة
- كل حالة لها معنى تشغيلي: active تشارك في retrieval, archived محفوظة لكن غير نشطة, deprecated قيد الازالة, deleted مزالة
- [MemOS/MemoryOS Framework](https://arxiv.org/abs/2506.06326)

### ما الذي لم نأخذه الآن؟
- MemOS full API (sharding, distributed memory, tiered storage backends)
- profile-based personalization (التخصيص المبني على الملفات الشخصية)
- multi-user memory isolation
- external storage connectors
- memory indexing with vector databases

### ماذا أصبح عندنا؟
- **`memory_status`** field مع 4 حالات: active, archived, deprecated, deleted
- **`archive_memory(id)`**: تنقل الذاكرة من active الى archived
- **`deprecate_memory(id)`**: تنقل الذاكرة من active الى deprecated
- **`delete_memory(id)`**: تنقل الذاكرة من active الى deleted
- **`get_active_memories()`**: تفلتر وترجع فقط الذكريات النشطة
- العمليات صريحة وقابلة للتتبع (explicit lifecycle transitions)

---

# ملخص التغطية

| # | المصدر | المكون الناتج | النوع |
|---|--------|--------------|-------|
| 5.45 | FunSearch (Romera-Paredes et al., 2023) | benchmark_generator.py: توليد TaskCase من anomalies | سرقة جديدة |
| 5.46 | AutoTTS / Auto Test-Time Strategies | run_self_benchmark_cycle: دورة اكتشاف ذاتي للاختبارات | سرقة جديدة (extension of 5.13) |
| 5.47 | Novelty Search (Lehman & Stanley, 2011) | blind_spot_discovery.py: تغطية التنوع واكتشاف المناطق العمياء | سرقة جديدة |
| 5.48 | Metamorphic Testing (Chen et al., 2018) | diagnostic_value.py: قياس التفاوت التشخيصي عبر conditions | سرقة جديدة |
| 5.49 | Curriculum Self-Play (Silver et al., AlphaZero concept) | run_self_benchmark_cycle: دورة تقييم ذاتي كاملة | سرقة جديدة |
| 5.50 | Ebbinghaus Forgetting Curve (1885) | store.apply_decay: اضمحلال الذاكرة بمرور الزمن | سرقة جديدة |
| 5.51 | Retrieval-Induced Forgetting (Anderson et al., 1994) | record_access + apply_decay: تعزيز المسترجع واضعاف الباقي | سرقة جديدة |
| 5.52 | Memory Reconsolidation (Nader et al., 2000) | record_access: الاسترجاع يحدث الذاكرة | سرقة جديدة |
| 5.53 | Desirable Difficulties (Bjork, 1994) | forgetting_policy: الانتقائية تقوي ما يبقى | سرقة جديدة |
| 5.54 | MemOS (lifecycle management) | memory_status + archive/deprecate/delete + get_active_memories | سرقة جديدة (extension of 5.15) |

---

*نهاية وثيقة السرقات الشرعية - الموجة الثالثة*
