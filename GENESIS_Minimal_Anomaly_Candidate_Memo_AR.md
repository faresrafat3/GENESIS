# Virtual-GENESIS Minimal Anomaly Candidate Memo (Arabic)

## الغرض
توثيق أول إدخال runtime/analytics لطبقة anomaly لكن بأخف صورة ممكنة:
- لا full anomaly manager
- لا crisis logic كاملة
- فقط **anomaly candidates extraction**

## ما الذي أُضيف؟
1. `AnomalyCandidate` object
2. `anomaly_runtime.service` لاستخراج candidates من:
   - property gaps
   - shortcut triggers
   - contradiction-derived patterns
3. `anomaly_candidates` تُكتب في output hooks
4. report جديدة: `anomaly_candidate_report`

## لماذا هذه الخطوة مهمة؟
لأننا انتقلنا من:
- contradictions measured
إلى:
- بعض patterns inside failure/verification/contradiction streams أصبحت تُرفع كمرشحات anomaly

أي أننا بدأنا أول bridge عملي من:
# Contradiction / failure signals → Anomaly candidates

## ما الذي لا تعنيه هذه الخطوة؟
- لا يوجد بعد anomaly lifecycle ناضجة
- لا يوجد anomaly prioritization policy معقدة
- لا يوجد crisis escalation engine

لكن هناك الآن:
- explicit candidate generation
- comparative reporting across conditions

## القيمة الحالية
هذه الخطوة صحيحة زمنيًا لأنها:
1. لا تضع burden كبيرًا على runtime
2. لا تشتت عن thesis core
3. تبني أرضية واضحة للـ Governance Spine دون قفز مبكر

## الحكم
Governance Spine الآن لم تعد نظرية فقط، ولا runtime كاملة، بل:
# **measurable emerging layer**

وهذا النوع من التقدم التدريجي هو الأنسب للحالة الحالية للمشروع.
