# Virtual-GENESIS - السرقات الشرعية: الدورة الثالثة
# Legitimate Thefts - Cycle 3 (Theory Leverage - Option B)

> Document Type: Legitimate Theft Registry
> Status: Current
> Date: 2026-06-01
> Scope: Covers new thefts 5.33-5.38 for Cycle 3 development (Local Theory Leverage - Option B)

---

## مقدمة

هذه الوثيقة توثق "السرقات الشرعية" الجديدة التي تم استخدامها في الدورة الثالثة من تطوير Virtual-GENESIS.
هذه الدورة تركز على مسار واحد:
1. **Local Theory Leverage (Option B)** - تفعيل النظريات المحلية كمحرك استباقي للتنبؤ والتحقق والتوجيه

كل سرقة تتبع المنهجية المعتمدة: ناخذ مجهود الغير من ابحاث ومشاريع وافكار، نستخلص الجوهر القابل للتشغيل، ونحوله الى مكون عملي في نظامنا مع توثيق كامل لما اخذناه وما تركناه وما اصبح عندنا.

---

# السرقات الجديدة من الابحاث

---

## 5.33 من Popper - Falsifiability (The Logic of Scientific Discovery, 1934)
### ما الذي أخذناه؟
- مبدا القابلية للتكذيب: النظرية العلمية الحقيقية يجب ان تولد تنبؤات محددة قابلة للاختبار والتكذيب
- فكرة ان جودة النظرية تقاس بقدرتها على التنبؤ الناجح (predictive power)
- ان التنبؤ الفاشل هو معلومة قيمة عن حدود النظرية [Popper, 1934/1959](https://doi.org/10.4324/9780203994627)

### ما الذي لم نأخذه الآن؟
- مفهوم الاستبعاد النهائي للنظرية عند التكذيب المتكرر (refutation)
- الاختبارات المنهجية المتعددة لتكذيب النظرية بشكل كامل
- التفريق بين التكذيب الحاسم والتكذيب القابل للتاويل
- مفهوم degree of corroboration الكامل

### ماذا أصبح عندنا؟
- **دالة get_theory_prediction_for_task()**: كل نظرية محلية تولد تنبؤا محددا لكل مهمة
  - predicts_failure: هل تتنبا النظرية بفشل المهمة؟
  - predicts_difficulty: هل تتنبا بصعوبة؟
  - confidence: مبنية على predictive_value الفعلية للنظرية
- **مقياس predictive_value**: يقيس جودة النظرية بناء على نسبة تنبؤاتها الصحيحة
- التنبؤ قابل للتحقق بعد تنفيذ المهمة: اذا تنبات بالفشل ونجحت = دليل ضد النظرية

---

## 5.34 من Bayesian Epistemology - Howson & Urbach (Scientific Reasoning: The Bayesian Approach, 1989)
### ما الذي أخذناه؟
- التحديث البايزي للمعتقدات: بعد كل ملاحظة جديدة، يتم تحديث درجة الثقة في الفرضية
- نظرية Bayes: P(H|E) = P(E|H) * P(H) / P(E) -- المعتقد المسبق (prior) يتحدث مع الدليل الجديد لانتاج معتقد محدث (posterior)
- Laplace smoothing: تقنية لتجنب القيم المتطرفة (0 او 1) عندما تكون الملاحظات قليلة -- تبدا من 0.5 وتتحرك تدريجيا [Howson & Urbach, 1989](https://doi.org/10.1017/CBO9780511570643)

### ما الذي لم نأخذه الآن؟
- التحديث البايزي الكامل مع prior distributions واحتمالات شرطية (full posterior computation)
- الشبكات البايزية (Bayesian Networks) لنمذجة العلاقات بين النظريات
- التفريق بين انواع مختلفة من التنبؤات واوزانها
- التوازن الدقيق بين التكلفة والعائد المتوقع (decision-theoretic Bayesianism)

### ماذا أصبح عندنا؟
- **دالة update_theory_predictive_value()**: تحديث بسيط بعد كل مهمة
  - الصيغة: `predictive_value = (correct_predictions + 1) / (prediction_count + 2)`
  - تبدا من 0.5 (Laplace prior) وتتحرك حسب الاداء الفعلي
  - لا تصل ابدا الى 0.0 او 1.0 تماما (تجنب اليقين المطلق)
- **choose_tier_theory_guided()**: القرار المسبق (prior) من النظرية يؤثر على اختيار الطبقة
  - تنبؤ بالصعوبة مع ثقة >= 0.5: يمنع tier_0
  - تنبؤ بالفشل مع ثقة >= 0.6: يفرض tier_2
- **النمط البايزي**: المعتقد المسبق (predictive_value) يوجه القرار، ثم يتحدث بنتيجة المهمة

---

## 5.35 من Theory-Theory of Concepts - Gopnik & Wellman (1994, 2012)
### ما الذي أخذناه؟
- المفاهيم ليست مجرد تصنيفات معزولة بل هي جزء من نظريات ضمنية (implicit theories)
- النظرية توجه اختيار المفاهيم ذات الصلة: المفاهيم المرتبطة بالنظرية تحصل على تفعيل اقوى لانها جزء من اطار تفسيري متماسك
- الاطفال يبنون نظريات ضمنية تحدد اي المفاهيم "تنتمي معا" [Gopnik & Wellman, 2012](https://doi.org/10.1093/acprof:oso/9780195367638.003.0012) [Gopnik & Wellman, 1994](https://doi.org/10.1111/j.1468-0017.1994.tb00156.x)

### ما الذي لم نأخذه الآن؟
- البنية الكاملة للنظريات الضمنية عند الاطفال والبالغين
- التحولات المفاهيمية الكاملة (conceptual change) عبر التطور
- الانتقال بين اطر نظرية مختلفة (framework theory transitions)
- دور التجربة المباشرة في تشكيل النظريات الضمنية

### ماذا أصبح عندنا؟
- **select_applicable_concepts_theory_guided()**: المفاهيم المذكورة في concept_refs للنظرية تحصل على دفعة +3 في درجة التفعيل (theory_boost)
- **نمط الانتماء النظري**: المفاهيم "تنتمي معا" لانها جزء من نفس النظرية المحلية
- النظرية تعمل كعامل ترجيح: ليس كل المفاهيم متساوية، بل المرتبطة بالاطار التفسيري تُفضل

---

## 5.36 من Explanation-Based Learning - DeJong & Mooney (1986)
### ما الذي أخذناه؟
- التعلم المبني على التفسير: النظرية تسمح بالتعميم من مثال واحد اذا كان التفسير متماسكا
- المفاهيم القريبة من عتبة القبول يمكن ان تدخل اذا كانت النظرية توفر تفسيرا لملاءمتها (theory-driven admission)
- الفرق بين التعلم من الامثلة فقط (similarity-based) والتعلم المبني على التفسير (explanation-based): الاخير اكثر كفاءة لانه لا يحتاج امثلة كثيرة [DeJong & Mooney, 1986](https://doi.org/10.1007/BF00114116)

### ما الذي لم نأخذه الآن؟
- التعميم الكامل من مثال واحد مع التفسير السببي الكامل (full causal explanation)
- بناء domain theory كاملة وتطبيقها على امثلة جديدة
- الجمع بين EBL و similarity-based learning في نظام واحد
- تعلم الـ preconditions من الشرح

### ماذا أصبح عندنا؟
- **Theory-Guided Admission**: المفاهيم غير المختارة التي درجتها قريبة من الحد الادنى (ضمن 2 نقطة من fam_min_score) تدخل اذا كانت في concept_refs للنظرية
- الدخول مشروط بان النظرية "تفسر" ملاءمة المفهوم
- العلامة [theory_admission] توثق ان الدخول تم بسبب النظرية وليس بسبب الدرجة وحدها
- **النمط**: النظرية تخفض عتبة الدخول للمفاهيم التي تنتمي لاطارها التفسيري

---

## 5.37 من Scientific Realism - Boyd (1983) / Putnam (1975)
### ما الذي أخذناه؟
- حجة النجاح التنبؤي (no-miracles argument): اذا نجحت النظرية في التنبؤ بظواهر جديدة (novel predictions)، فهذا دليل قوي على ان بنيتها تعكس واقعا حقيقيا
- النظريات الناجحة تنبؤيا تستحق ثقة اكبر ليس فقط اداتيا بل بنيويا (structural realism)
- التنبؤ الناجح ليس صدفة: هو اشارة الى ان النظرية "تمسك بشيء حقيقي" [Boyd, 1983](https://doi.org/10.1017/CBO9781139171519.033) [Putnam, 1975](https://doi.org/10.1017/CBO9780511625268)

### ما الذي لم نأخذه الآن؟
- الجدل الفلسفي الكامل حول الواقعية مقابل الاداتية (realism vs instrumentalism)
- Pessimistic Meta-Induction: حجة ان نظريات ناجحة سابقة ثبت خطاها
- التفريق بين الواقعية البنيوية والواقعية الكيانية (structural vs entity realism)
- مفهوم approximate truth الكامل

### ماذا أصبح عندنا؟
- **predictive_value كمقياس جودة**: كلما نجحت النظرية في التنبؤ، زاد predictive_value
- القيمة التنبؤية العالية تعني: "هذه النظرية تمسك بشيء حقيقي في بنية المهام"
- **confidence في التنبؤ مبنية على predictive_value**: النظرية ذات السجل التنبؤي الجيد تنتج تنبؤات اكثر ثقة
- القيمة التنبؤية تؤثر على قرارات النظام: theory with high predictive_value -> stronger routing/verification signals

---

## 5.38 من DevOps Runbook Automation - SRE Practices (Google, 2016)
### ما الذي أخذناه؟
- في هندسة موثوقية المواقع (SRE)، الـ runbooks هي وثائق تحدد مسبقا كيفية التعامل مع كل نوع من المشاكل
- التنبؤ بالمشكلة يستدعي تصعيدا استباقيا (proactive escalation): لا تنتظر الفشل الفعلي
- الانذار المبكر (early warning) يفعل مسار استجابة محدد مسبقا بدلا من الاستجابة التفاعلية
- اتمتة القرار: "اذا الانذار X، نفذ الاجراء Y" -- لا تفكير بشري مطلوب [Beyer et al., 2016 - Site Reliability Engineering, Google](https://sre.google/sre-book/table-of-contents/)

### ما الذي لم نأخذه الآن؟
- Runbooks كاملة مع خطوات متعددة وشروط فرعية
- التصعيد الهرمي متعدد المستويات (multi-level escalation chains)
- On-call rotations والتناوب بين الفرق
- التكامل مع انظمة التنبيه الخارجية (Prometheus, Grafana, etc.)

### ماذا أصبح عندنا؟
- **choose_tier_theory_guided()**: النظرية تعمل كـ runbook استباقي لتوجيه المهام
  - "اذا النظرية تتنبا بالفشل بثقة >= 0.6 -> tier_2 فورا" (runbook rule 1)
  - "اذا النظرية تتنبا بالصعوبة بثقة >= 0.5 -> لا tier_0" (runbook rule 2)
- **النمط**: theory-as-runbook -- النظرية المحلية تحدد مسبقا كيفية التعامل مع كل نوع مهام بدلا من الانتظار للفشل
- القاعدتان بسيطتان وقابلتان للتطبيق الآلي بدون تدخل بشري

---

# تشغيل اضافي لسرقات كلاسيكية قائمة

---

## ملاحظة حول 6.2 من Lakatos - تشغيل اضافي (Methodology of Scientific Research Programmes, 1978)
### ما الذي كان عندنا سابقاً؟
- مفهوم البرنامج البحثي بنواته الصلبة وحزامه الواقي
- التفريق بين التحولات التقدمية والتراجعية
- anomaly detection as signal for potential paradigm shift

### ما الذي أضفناه الآن؟
- **check_theory_explains_contradiction()**: النظرية القوية تستطيع استيعاب التناقضات وتفسيرها
- اذا تداخلت رموز ادعاءات النظرية التنبؤية (predictive_claims) مع محتوى التناقض بعتبة 2+ رموز:
  - النظرية "تفسر" التناقض ضمن اطارها
  - تزداد explanatory_power بمقدار 0.1 (حد اقصى 1.0)
- **التحول: من كشف التناقض الى تفسيره نظريا**
- النظرية التي تفسر تناقضات اكثر هي نظرية اقوى (progressive research programme)
- الذي لا يفسر: نظرية ضعيفة (degenerating programme) -- لكن لم نطبق الاستبعاد بعد

---

## ملاحظة حول 6.3 من Kuhn - تشغيل اضافي (Structure of Scientific Revolutions, 1962)
### ما الذي كان عندنا سابقاً؟
- anomaly detector مع crisis report
- anomaly accumulation -> behavioral change (من الدورة الثانية)
- matches_known_anomaly_pattern() لاكتشاف انماط Kuhnian

### ما الذي أضفناه الآن؟
- **ثقة النظرية من سجل التنبؤات**: تماما كما يبنى paradigm confidence من النجاح المتراكم
- predictive_value يرتفع مع كل تنبؤ ناجح ويهبط مع كل فشل
- النظرية ذات predictive_value عالي = paradigm مستقر وموثوق
- النظرية ذات predictive_value منخفض = paradigm يتراجع (قد يحتاج revolution)
- **confidence في get_theory_prediction_for_task** مبنية مباشرة على predictive_value:
  - نظرية جديدة: confidence = 0.5 (neutral)
  - نظرية ناجحة: confidence يرتفع تدريجيا
  - نظرية فاشلة: confidence ينخفض تدريجيا
- **التحول: من كشف الازمة الى قياس صحة النظرية كميا**

---

## ملاحظة حول 6.8 من Predictive Processing / Active Inference - تشغيل اضافي (Friston, 2010)
### ما الذي كان عندنا سابقاً؟
- hypothesis-first answering
- anomaly_severity = prediction error signal (من الدورة الثانية)
- verify_output_anomaly_aware: تشديد عند ارتفاع prediction error

### ما الذي أضفناه الآن؟
- **verify_output_theory_guided()**: التنبؤ النظري يوجه دقة التحقق استباقيا
- عندما تتنبا النظرية بالفشل (predicts_failure):
  - النظام يشدد معايير القبول قبل ان يحدث الفشل فعلا
  - يتطلب ضرب علامتين اوليتين (primary markers) بدلا من واحدة
  - يتطلب نجاح كل الخصائص المطلوبة (ALL properties)
- عندما تتنبا بالصعوبة فقط (predicts_difficulty):
  - يتطلب ضرب علامة ثانوية (secondary marker) اضافية
- **الفرق عن anomaly-aware verification**:
  - Anomaly-aware: يشدد بعد اكتشاف الشذوذ (reactive)
  - Theory-guided: يشدد بناء على تنبؤ مسبق (proactive/predictive)
- **التكامل**: عند تفعيل كلا المسارين، theory-guided يطبق اولا، ثم anomaly-aware يطبق فوقه (يؤخذ الاشد)

---

# ملخص التغطية

| # | المصدر | المكون الناتج | النوع |
|---|--------|--------------|-------|
| 5.33 | Popper (Falsifiability) | get_theory_prediction_for_task + predictive_value metric | سرقة جديدة |
| 5.34 | Bayesian Epistemology (Howson & Urbach) | update_theory_predictive_value + choose_tier_theory_guided | سرقة جديدة |
| 5.35 | Theory-Theory of Concepts (Gopnik & Wellman) | theory-guided concept boost (+3) | سرقة جديدة |
| 5.36 | Explanation-Based Learning (DeJong & Mooney) | theory-guided concept admission | سرقة جديدة |
| 5.37 | Scientific Realism (Boyd/Putnam) | predictive_value as quality signal | سرقة جديدة |
| 5.38 | DevOps Runbook Automation (Google SRE) | theory-as-runbook routing rules | سرقة جديدة |
| 6.2+ | Lakatos | check_theory_explains_contradiction | تشغيل اضافي |
| 6.3+ | Kuhn | theory confidence from prediction track record | تشغيل اضافي |
| 6.8+ | Predictive Processing | verify_output_theory_guided (proactive strictness) | تشغيل اضافي |

---

*نهاية وثيقة السرقات الشرعية - الدورة الثالثة*
