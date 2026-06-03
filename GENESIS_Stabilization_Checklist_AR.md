# Virtual-GENESIS Stabilization Checklist (Arabic)

## 0) الغرض
هذه الوثيقة تنفذ توصية **Decision Memo**:

> **نثبت الآن، ثم نقفز لاحقًا**

الهدف هنا ليس إضافة قدرات جديدة، بل:
- تثبيت الـ current best regime
- تقليل churn
- توضيح ما هو المرجع الرسمي الحالي
- منع التعديلات المبعثرة التي تفسد attribution
- تجهيز قاعدة صلبة لأي دورة تطوير لاحقة

هذه الوثيقة يجب أن تُستخدم كقائمة عملية قبل أي توسع جديد.

---

# 1) ما الذي نعتبره “التثبيت”؟
التثبيت لا يعني تجميد المشروع تمامًا.

بل يعني:
1. تحديد ما هو **current default**
2. تحديد ما هو **current evidence package**
3. تحديد ما هو **غير محسوم**
4. منع التعديلات التي تمس المقارنات الأساسية بلا داعٍ
5. تنظيف النقاط السهلة التي تقلل الفوضى دون تغيير behavior الجوهري

---

# 2) Freeze List — ما الذي نجمّده الآن؟

## 2.1 Thesis status
- [ ] Thesis 2 تُعامل الآن كأقوى فرضية حالية
- [ ] Thesis 1 تُعامل كفرضية مدعومة لكن regime-sensitive

## 2.2 Evaluation regime roles
- [ ] `prototype_v3b_curriculum` = primary thesis regime
- [ ] `prototype_v4_cases` = diagnostic slice
- [ ] `v2 / old v3` = calibration references

## 2.3 Selectivity defaults
- [ ] comparison = top1 / score7
- [ ] synthesis = top1 / score7
- [ ] procedure = top0

## 2.4 Task representation
- [ ] TaskCase-based evaluation preferred where available
- [ ] raw string tasks not removed but treated as legacy path

## 2.5 Current best operating path
- [ ] concept-aware + economy-aware under TaskCase-based curriculum evaluation

---

# 3) What we do NOT change during stabilization

## No new major layers
- [ ] no full anomaly manager
- [ ] no full theory-guided routing
- [ ] no sparse committee system
- [ ] no multimodal/GUI/web runtime expansion

## No thesis-shifting changes
- [ ] no radical redefinition of Thesis 1 or 2
- [ ] no new core theory branches

## No evaluation role confusion
- [ ] do not reuse v4 as primary thesis slice
- [ ] do not interpret v2/v3 as strong evidence slices

## No config churn
- [ ] do not retune family-specific selectivity defaults unless a dedicated ablation justifies it

---

# 4) Cleanup List — ما الذي يمكن تنظيفه الآن بأمان؟

## 4.1 File / package hygiene
- [ ] التأكد أن كل `__init__.py` موجودة حيث ينبغي
- [ ] إزالة imports غير المستخدمة
- [ ] توحيد naming قدر الإمكان
- [ ] مراجعة المسارات النسبية imports لتكون مستقرة

## 4.2 Runtime hygiene
- [ ] مراجعة أي duplication obvious في runners أو reports
- [ ] التأكد أن كل object مهمة تتحول إلى dict/JSON cleanly
- [ ] التأكد أن provenance وIDs موجودة في المسارات الحرجة

## 4.3 Evaluation hygiene
- [ ] التأكد أن كل result file تكتب إلى مسار واضح ومستقر
- [ ] التأكد أن `summary`, `meta`, `aggregate_metrics` shapes مستقرة
- [ ] التأكد أن contrast بين conditions لا يعتمد على hidden side effects

## 4.4 Reporting hygiene
- [ ] current evidence memos محدثة مع آخر regime
- [ ] current best slices موثقة بوضوح
- [ ] contradiction/anomaly/theory reports قابلة للقراءة

---

# 5) Reference Package — ما المرجع الرسمي الحالي؟
هذا مهم جدًا حتى لا نضيع.

## 5.1 Current regime docs
- [ ] `Virtual_SIA_Current_Regime_Memo_AR.md`
- [ ] `Virtual_SIA_Current_Evidence_Package_AR.md`
- [ ] `Virtual_SIA_Decision_Memo_AR.md`

## 5.2 Core formal docs
- [ ] `Virtual_SIA_Core_Ontology_AR.md`
- [ ] `Virtual_SIA_Task_Blackboard_Spec_AR.md`
- [ ] `Virtual_SIA_Memory_OS_Spec_AR.md`
- [ ] `Virtual_SIA_Concept_Formation_Engine_Spec_AR.md`
- [ ] `Virtual_SIA_Cognitive_Economy_Ledger_And_Tier_Router_Spec_AR.md`

## 5.3 Key execution docs
- [ ] `Virtual_SIA_Minimal_Evaluation_Protocol_AR.md`
- [ ] `Virtual_SIA_Prototype_Slice_Plan_AR.md`
- [ ] `Virtual_SIA_Implementation_Preplan_AR.md`
- [ ] `Virtual_SIA_First_Implementation_Order_AR.md`

## 5.4 Current evidence memos
- [ ] `Virtual_SIA_Expanded_Evidence_Memo_AR.md`
- [ ] `Virtual_SIA_Prototype_V2_Evidence_Memo_AR.md`
- [ ] `Virtual_SIA_Prototype_V3_Evidence_Memo_AR.md`
- [ ] `Virtual_SIA_Prototype_V3B_Evidence_Memo_AR.md`
- [ ] `Virtual_SIA_Prototype_V3B_Curriculum_Evidence_Memo_AR.md`
- [ ] `Virtual_SIA_Prototype_V4_Boundary_Stress_Memo_AR.md`
- [ ] `Virtual_SIA_Prototype_V5_Evidence_Memo_AR.md`
- [ ] `Virtual_SIA_Concept_Selectivity_Update_Memo_AR.md`
- [ ] `Virtual_SIA_Contradiction_Analytics_Update_Memo_AR.md`
- [ ] `Virtual_SIA_Minimal_Anomaly_Candidate_Memo_AR.md`
- [ ] `Virtual_SIA_Minimal_Local_Theory_Builder_Memo_AR.md`
- [ ] `Virtual_SIA_Theory_Leverage_Update_Memo_AR.md`

---

# 6) Sanity Checks before any next cycle

## Check A — Defaults sanity
- [ ] selectivity config فعلاً مضبوطة على default الحالية
- [ ] evaluation slices تعمل كما هو موثق
- [ ] current best path لا تعتمد على hidden temporary overrides

## Check B — Reproducibility sanity
- [ ] تشغيل runners الأساسية يعطي outputs متسقة نوعيًا
- [ ] current evidence package قابلة لإعادة التوليد

## Check C — Interpretation sanity
- [ ] لا يوجد slice متشبعة تُقرأ كأنها primary thesis evidence
- [ ] لا يوجد diagnostic slice تُقرأ كأنها definitive verdict

## Check D — Governance sanity
- [ ] contradiction/anomaly/theory plumbing موجودة
- [ ] لكنها لا تُفرض كcontrol layers كبيرة قبل وقتها

---

# 7) What counts as stabilized enough?
نعتبر stabilization كافية إذا تحققت الشروط التالية:

1. **Current best defaults** واضحة ومثبتة
2. **Current evidence package** موحدة ومفهومة
3. **No obvious broken paths** في runtime الأساسية
4. **No urgent confounds** غير موثقة في evaluation regime
5. **No pending hidden overrides** تؤثر على النتائج بدون توثيق

إذا تحققت هذه الشروط، يمكننا الانتقال إلى الدورة التالية بأمان.

---

# 8) ما الدورة التالية المحتملة بعد stabilization؟
بعد التثبيت، نختار **واحدة فقط** من الدورات التالية:

## Cycle A — Stronger perturbation operators
إذا رأينا أن evaluation pressure ما زالت سهلة أو متحيزة

## Cycle B — Anomaly candidate leverage
إذا أردنا نقل Governance Spine من reporting إلى influence

## Cycle C — Local theory leverage
إذا أردنا اختبار هل النظريات المحلية يمكن أن تحسن السلوك فعلًا

## Cycle D — Broader task families / domains
إذا أردنا اختبار portability beyond current analytical slice

### recommendation الحالية
لا نختار الآن. نثبت أولًا، ثم نختار بناءً على الوضع بعد التثبيت.

---

# 9) ما الذي نعتبره Anti-pattern أثناء stabilization؟
- [ ] إضافة features كبيرة “لأنها تبدو جميلة”
- [ ] كسر defaults الحالية بدون evidence
- [ ] تعديل slices ثم مقارنة نتائجها كأنها نفس slice السابقة
- [ ] ضياع المذكرات المرجعية وسط التحديثات الصغيرة
- [ ] تفسير كل movement في الأرقام على أنها breakthrough أو collapse

---

# 10) القرار التنفيذي النهائي
## التوصية الآن:
# **نثبت الحالة الحالية وننظفها قبل أي قفزة جديدة.**

هذا لا يعني التوقف، بل يعني:
- حماية ما بنيناه
- منع الانحراف
- وزيادة قيمة أي دورة تطوير لاحقة

### الصياغة المختصرة
المرحلة الحالية هي:
# **Regime Consolidation before Next Expansion**
