# Virtual-GENESIS Evaluation Redesign Memo (Arabic)

## الغرض
هذه المذكرة تسجل اكتشافًا مهمًا في مسار التنفيذ:

> بعد تقوية reasoning runtime ودمج task framing signals داخل verification، لم تعد بعض الشرائح خاصة `prototype_v4` مناسبة لتمييز الفروق بين conditions، لأن generation والـ verification أصبحا متوافقين أكثر من اللازم.

بالتالي نحتاج الآن إلى:
# **إعادة تصميم وحدة التقييم نفسها**

وليس فقط تعديل thresholds أو markers.

---

## المشكلة المكتشفة
### ما الذي حدث؟
- reasoning runtime أصبحت family-aware أكثر
- outputs أصبحت تحمل إشارات لفظية/هيكلية ترضي verification بسهولة
- حتى بعد تشديد verification، ظلت conditions المختلفة تحقق سقفًا قريبًا من 1.0 في v4

### النتيجة
prototype_v4 لم تعد discriminative enough لاختبار Thesis 1 و2.

### السبب الأعمق
ليس فقط permissive verifier، بل:

> **coupling بنيوي بين generation وevaluation**

أي أن النظام “تعلم” شكل النجاح لأنه النجاح مقاس بإشارات قريبة جدًا من surface form للجواب.

---

## التمييز الذي يجب أن نثبته الآن
من هذه اللحظة يجب أن نميّز بين نوعين من الشرائح:

### Type A — Thesis-discriminative slice
تُستخدم لقياس الفرضيات المركزية ويجب أن تبقى discriminative.

### Type B — Stress/diagnostic slice
تُستخدم لاكتشاف bottlenecks مثل framing ambiguity أو classification instability.

### الترتيب الحالي
- `prototype_v2` = أقرب إلى Type A
- `prototype_v4` = أقرب إلى Type B

هذا مهم جدًا حتى لا نقرأ كل slice بنفس المعنى.

---

## المطلوب تغييره
### 1) تمثيل task case
بدل task كنص فقط، نحتاج case object يحتوي على:
- prompt_text
- expected_family / framing hints
- hidden evaluation targets
- required properties
- forbidden shortcuts
- diagnostic purpose

### 2) verification redesign
بدل lexical markers فقط، نحتاج verifier تقيس:
- presence of required properties
- structural adequacy
- anti-shortcut signals
- mismatch between required family behavior and generated behavior

### 3) separation of generation cues and evaluation cues
لا يجب أن تكون cues التي تساعد generation هي نفسها cues التي تجعل التقييم يمر.

---

## القرار العملي
الخطوة التالية المنطقية ليست layer جديدة، بل:
1. تعريف **TaskCase Schema**
2. تحديث task sets لتصبح case-based
3. تحديث verifier لتقرأ required_properties/forbidden_shortcuts
4. إعادة تشغيل slices مع هذا الفصل

---

## الحكم
هذا ليس تراجعًا، بل علامة نضج:
- النظام لم يعد فقط ينتج أرقامًا
- بل بدأ يكشف متى تكون الأرقام ذاتها مضللة

وهذا من أهم نقاط القوة في أي برنامج بحثي وتنفيذي منضبط.
