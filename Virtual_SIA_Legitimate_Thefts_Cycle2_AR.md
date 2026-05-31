# Virtual-SIA - السرقات الشرعية: الدورة الثانية
# Legitimate Thefts - Cycle 2 (Evaluation Pressure + Anomaly Leverage)

> Document Type: Legitimate Theft Registry
> Status: Current
> Date: 2026-06-01
> Scope: Covers new thefts 5.24-5.32 for Cycle 2 development (Evaluation Pressure + Minimal Anomaly Leverage)

---

## مقدمة

هذه الوثيقة توثق "السرقات الشرعية" الجديدة التي تم استخدامها في الدورة الثانية من تطوير Virtual-SIA.
الدورة تشمل مسارين:
1. **Evaluation Pressure (Option C)** - توسيع عوامل الاضطراب وضغط التقييم
2. **Minimal Anomaly Leverage (Option A)** - تفعيل الشذوذ كمحرك سلوكي

كل سرقة تتبع المنهجية المعتمدة: نأخذ مجهود الغير من أبحاث ومشاريع وأفكار، نستخلص الجوهر القابل للتشغيل، ونحوله إلى مكون عملي في نظامنا مع توثيق كامل لما أخذناه وما تركناه وما أصبح عندنا.

---

# السرقات الجديدة من الأبحاث

---

## 5.24 من Zeiler & Fergus (Visualizing and Understanding Convolutional Networks)
### ما الذي أخذناه؟
- منهجية الـ ablation study: إزالة مكونات واحدة تلو الأخرى لفهم مساهمة كل جزء في الأداء الكلي
- فكرة أن إزالة feature واحدة تكشف مدى اعتماد النظام عليها [Zeiler & Fergus, 2014](https://arxiv.org/abs/1311.1901)

### ما الذي لم نأخذه الآن؟
- الـ visualization techniques الخاصة بالـ CNN layers
- الـ deconvolution approach لإعادة بناء الـ activations
- الـ occlusion sensitivity maps

### ماذا أصبح عندنا؟
- **عامل support_removal**: يزيل العبارات الداعمة من نص المهمة واحدة تلو الأخرى
- يكشف مدى اعتماد النظام على أدلة محددة vs فهم عام
- جزء أساسي من المستوى 4 في المنهج الدراسي الموسع

---

## 5.25 من Hogarth & Einhorn (Order Effects in Belief Updating)
### ما الذي أخذناه؟
- أن ترتيب تقديم الأدلة يؤثر بشكل كبير على الاستنتاج النهائي
- ظاهرة primacy/recency effects في تحديث المعتقدات
- أن النظام الصلب يجب أن يكون مستقلاً عن ترتيب المعلومات [Hogarth & Einhorn, 1992](https://doi.org/10.1016/0010-0285(92)90012-Q)

### ما الذي لم نأخذه الآن؟
- النموذج الرياضي الكامل لتحديث المعتقدات (anchoring and adjustment model)
- التمييز بين step-by-step vs end-of-sequence evaluation
- الـ serial position curve التفصيلية

### ماذا أصبح عندنا؟
- **عامل evidence_reordering**: يعيد ترتيب الجمل في نص المهمة لاختبار ثبات الإجابة
- يكشف ما إذا كان النظام يعتمد على ترتيب محدد بدلاً من فهم المحتوى
- جزء من المستوى 5 في المنهج الدراسي

---

## 5.26 من Nie et al. / Gardner et al. (Adversarial NLI / Contrast Sets)
### ما الذي أخذناه؟
- فكرة Contrast Sets: تغييرات بسيطة على المدخلات يجب أن تغير الإجابة الصحيحة
- أن النماذج غالباً تعتمد على إشارات سطحية بدلاً من الفهم الحقيقي
- Adversarial NLI: أمثلة مصممة خصيصاً لكسر اعتماد النموذج على shortcuts [Gardner et al., 2020](https://arxiv.org/abs/2004.02709) [Nie et al., 2020](https://arxiv.org/abs/1910.14599)

### ما الذي لم نأخذه الآن؟
- الـ human-in-the-loop adversarial data collection
- الـ model-in-the-loop annotation process
- بناء datasets ضخمة من الأمثلة العدائية

### ماذا أصبح عندنا؟
- **عامل contrast_weakening**: يستبدل كلمات التباين القوية بأخرى أضعف
- يختبر ما إذا كان النظام يفهم الفرق الجوهري أم يعتمد على إشارات لفظية واضحة
- جزء أساسي من المستوى 4 في المنهج الدراسي

---

## 5.27 من Mann & Thompson (Rhetorical Structure Theory)
### ما الذي أخذناه؟
- أن النصوص لها بنية خطابية تربط الأجزاء ببعضها (علاقات السبب والنتيجة، التفصيل، التباين)
- أن إضعاف هذه البنية يكشف مدى اعتماد النظام على الترابط الشكلي
- أن الـ nuclei vs satellites distinction يحدد ما هو أساسي وما هو مساعد [Mann & Thompson, 1988](https://doi.org/10.1515/text.1.1988.8.3.243)

### ما الذي لم نأخذه الآن؟
- التحليل الكامل لـ RST trees
- الـ annotation schemes المعقدة
- العلاقات الخطابية التفصيلية (30+ نوع)

### ماذا أصبح عندنا؟
- **عامل structure_weakening**: يزيل الإشارات البنيوية (الترقيم، القوائم، الروابط المنطقية)
- يختبر ما إذا كان النظام يفهم المحتوى مستقلاً عن تنسيقه
- جزء من المستوى 5 في المنهج الدراسي

---

## 5.28 من Goodfellow et al. / Geirhos et al. (Adversarial Examples / Shortcut Learning)
### ما الذي أخذناه؟
- أن النماذج تعتمد على shortcuts بدلاً من الميزات الحقيقية
- أن إضافة perturbations صغيرة يمكنها خداع النظام بالكامل
- أن texture bias vs shape bias يكشف نوع التعلم الحقيقي [Goodfellow et al., 2015](https://arxiv.org/abs/1412.6572) [Geirhos et al., 2020](https://arxiv.org/abs/2004.07780)

### ما الذي لم نأخذه الآن؟
- الـ gradient-based adversarial attack methods
- الـ adversarial training كأسلوب دفاعي
- الـ certified robustness approaches

### ماذا أصبح عندنا؟
- **عامل stronger_shortcut_lures**: يضيف عدة shortcuts مضللة تجعل المسار الممنوع أكثر إغراءً
- **anti-shortcut benchmark**: مجموعة مهام مصممة خصيصاً بحيث لا يمكن النجاح إلا بتجنب الـ shortcuts فعلاً
- المستوى 5 في المنهج الدراسي يختبر مقاومة النظام لهذه الإغراءات

---

## 5.29 من Bengio et al. (Curriculum Learning)
### ما الذي أخذناه؟
- أن التدرج في الصعوبة يحسن التعلم
- أن ترتيب العينات من السهل إلى الصعب يعطي نتائج أفضل من الترتيب العشوائي
- أن تحديد "السهولة" يمكن أن يكون based on loss أو based on complexity [Bengio et al., 2009](https://dl.acm.org/doi/10.1145/1553374.1553380)

### ما الذي لم نأخذه الآن؟
- الـ self-paced learning extensions
- الـ automatic curriculum generation via RL
- الـ competence-based curriculum progression

### ماذا أصبح عندنا؟
- **منهج دراسي من 6 مستويات** (توسيع من 4 إلى 6):
  - المستوى 0: المهمة الأصلية (بدون اضطراب)
  - المستوى 1: اضطراب خفيف (keyword noise)
  - المستوى 2: اضطراب متوسط (sentence injection)
  - المستوى 3: اضطراب قوي (full reformulation)
  - المستوى 4: اضطراب مركب (support_removal + contrast_weakening)
  - المستوى 5: اضطراب أقصى (evidence_reordering + stronger_shortcut_lures + structure_weakening)
- التدرج يكشف "نقطة الانكسار" حيث يبدأ النظام في الفشل

---

## 5.30 من Ribeiro et al. (CheckList: Beyond Accuracy)
### ما الذي أخذناه؟
- منهجية الاختبار السلوكي المنظم: لا تكتفي بالدقة العامة، بل اختبر قدرات محددة
- الـ behavioral testing taxonomy: Minimum Functionality Tests, Invariance Tests, Directional Tests
- فكرة أن كل capability يجب أن تُختبر بمجموعة cases مستقلة [Ribeiro et al., 2020](https://arxiv.org/abs/2005.04118)

### ما الذي لم نأخذه الآن؟
- الـ templating system الكامل لتوليد الأمثلة
- الـ user-facing GUI للاختبار التفاعلي
- الـ NLP-specific test types (NER, sentiment, QA)

### ماذا أصبح عندنا؟
- **تقرير مقاومة الاضطراب (perturbation_resistance report)**: يحلل الأداء حسب نوع الاضطراب ومستوى الصعوبة
- يحسب success_rate لكل perturbation_type على حدة
- يحدد "نقطة الانكسار" (أول مستوى ينخفض فيه النجاح عن 80%)
- يحسب مقاومة كل عائلة (family) بشكل مستقل

---

## 5.31 من Chandola et al. (Anomaly Detection: A Survey)
### ما الذي أخذناه؟
- تصنيف أنواع الشذوذ: point anomalies, contextual anomalies, collective anomalies
- أن شدة الشذوذ (severity) يمكن قياسها كدالة في عدة عوامل مركبة
- أن التنوع في مصادر الشذوذ يزيد من خطورته [Chandola et al., 2009](https://doi.org/10.1145/1541880.1541882)

### ما الذي لم نأخذه الآن؟
- خوارزميات الكشف الإحصائية المعقدة (Gaussian Mixture, Isolation Forest, etc.)
- الـ unsupervised anomaly detection approaches
- الـ time-series specific anomaly detection

### ماذا أصبح عندنا؟
- **دالة compute_anomaly_severity_score()**: تحسب شدة مركبة (0.0-1.0) بناءً على:
  - عدد المرشحين للشذوذ (count factor)
  - أقصى شدة بين المرشحين (max severity)
  - تنوع المصادر (source_type diversity)
- **دالة matches_known_anomaly_pattern()**: تكشف الأنماط المتكررة:
  - تزامن property_gap + shortcut_pattern
  - فشل متكرر في عائلة واحدة
  - تجمع التناقضات

---

## 5.32 من PagerDuty/Datadog (DevOps Incident Management Patterns)
### ما الذي أخذناه؟
- أن الحوادث تُدار بمستويات تصعيد تلقائية بناءً على شدة الإشارة
- أن threshold-based escalation يمنع التصعيد المفرط
- أن الحذر الإضافي عند وجود إشارات anomaly يقلل الأخطاء المكلفة
- نمط "عند الشك، صعّد" [PagerDuty Incident Management](https://www.pagerduty.com/resources/learn/what-is-incident-management/) [Datadog Alerting](https://docs.datadoghq.com/monitors/)

### ما الذي لم نأخذه الآن؟
- الـ on-call rotation والجدولة
- الـ runbooks الآلية
- الـ multi-team coordination protocols
- الـ SLA/SLO monitoring

### ماذا أصبح عندنا؟
- **should_escalate_anomaly_aware()**: تصعيد تلقائي عند anomaly_severity > 0.5
- **choose_tier_anomaly_aware()**: عند severity > 0.4 لا يختار tier_0 أبداً، عند > 0.7 يفرض tier_2
- نمط "الحذر المدروس" تحت إشارات الشذوذ: لا panic، بل escalation محسوبة

---

# تشغيل إضافي لسرقات كلاسيكية قائمة

---

## ملاحظة حول 6.3 من Kuhn - تشغيل إضافي
### ما الذي كان عندنا سابقاً؟
- anomaly detector
- crisis report
- paradigm fork protocol

### ما الذي أضفناه الآن؟
- **الشذوذ أصبح يُحدث تغييراً سلوكياً فعلياً** وليس مجرد تقرير
- matches_known_anomaly_pattern() تكشف أنماط Kuhnian:
  - تراكم الشذوذ في عائلة واحدة = بداية أزمة
  - تزامن property_gap + shortcut_pattern = إشارة لتحول paradigmatic
- عند تراكم الإشارات: النظام يغير سلوكه (تصعيد، تحقق أشد، حذر أكبر)
- **الانتقال من مراقبة الشذوذ إلى الاستجابة له**

---

## ملاحظة حول 6.8 من Predictive Processing / Active Inference - تشغيل إضافي
### ما الذي كان عندنا سابقاً؟
- hypothesis-first answering
- uncertainty-driven evidence acquisition

### ما الذي أضفناه الآن؟
- **anomaly_severity = prediction error signal تم تشغيله فعلياً**
- compute_anomaly_severity_score() هي الترجمة العملية لـ "prediction error magnitude"
- كلما زاد التباين بين المتوقع والفعلي (أي الشذوذ)، زادت الشدة
- الشدة العالية تعني: "النموذج التنبؤي الحالي لا يعمل جيداً هنا" -> استجابة أقوى مطلوبة
- **التحول: من مبدأ نظري إلى دالة حسابية تؤثر في سلوك النظام**

---

## ملاحظة حول 6.12 من Ashby (Requisite Variety) - تشغيل إضافي
### ما الذي كان عندنا سابقاً؟
- Policy Portfolio
- Requisite Variety Monitor

### ما الذي أضفناه الآن؟
- **ضغط الشذوذ يتطلب تنوعاً مكافئاً في الاستجابة**
- choose_tier_anomaly_aware() تطبيق مباشر: anomaly pressure -> higher tier (more variety)
- عند severity > 0.4: لا يكفي tier_0 (الأقل تنوعاً) -> يجب tier_1 على الأقل
- عند severity > 0.7: يجب tier_2 (أقصى تنوع متاح)
- **المبدأ مُفعّل**: only variety can absorb variety -> only premium tier can handle high anomaly

---

# ملخص التغطية

| # | المصدر | المكون الناتج | النوع |
|---|--------|--------------|-------|
| 5.24 | Zeiler & Fergus | support_removal operator | سرقة جديدة |
| 5.25 | Hogarth & Einhorn | evidence_reordering operator | سرقة جديدة |
| 5.26 | Nie et al. / Gardner et al. | contrast_weakening operator | سرقة جديدة |
| 5.27 | Mann & Thompson | structure_weakening operator | سرقة جديدة |
| 5.28 | Goodfellow et al. / Geirhos et al. | stronger_shortcut_lures + anti-shortcut benchmark | سرقة جديدة |
| 5.29 | Bengio et al. | 6-level curriculum | سرقة جديدة |
| 5.30 | Ribeiro et al. | perturbation_resistance report | سرقة جديدة |
| 5.31 | Chandola et al. | anomaly severity scoring | سرقة جديدة |
| 5.32 | PagerDuty/Datadog | escalation caution | سرقة جديدة |
| 6.3+ | Kuhn | anomaly -> behavioral change | تشغيل إضافي |
| 6.8+ | Predictive Processing | severity = prediction error | تشغيل إضافي |
| 6.12+ | Ashby | anomaly pressure -> higher tier | تشغيل إضافي |

---

*نهاية وثيقة السرقات الشرعية - الدورة الثانية*
