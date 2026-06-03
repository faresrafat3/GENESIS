# Virtual-GENESIS Productive Forgetting Implementation Memo
# مذكرة تنفيذ النسيان المنتج

> Document Type: Implementation Memo
> Status: Implemented
> Date: 2026-06-01
> Hypothesis: H3 - Productive Forgetting (Tier S)

---

## 1. الغرض

هذه المذكرة توثق ما تم بناؤه لتنفيذ فرضية Productive Forgetting (H3) من البرنامج البحثي.

الهدف: اعطاء نظام الذاكرة ادارة دورة حياة كاملة تمنع تلوث الذاكرة وتحافظ على جودة الاسترجاع عبر النسيان المنتج.

المرجع النظري: `Virtual_SIA_Productive_Forgetting_Theory_AR.md` (الاقسام 1-15)

---

## 2. المكونات المنفذة

### 2.1 Memory Decay (اضمحلال الذاكرة)
**المكان**: `virtual_genesis/runtime/memory_os/store.py` - دالة `apply_decay(decay_rate)`

تخفض decay_score لكل ذاكرة نشطة بناء على مقدار التقادم (staleness). الذكريات التي لم تُستخدم منذ وقت طويل تفقد من قوتها تدريجيا.

### 2.2 عمليات دورة الحياة (Lifecycle Operations)
**المكان**: `virtual_genesis/runtime/memory_os/store.py`

- `archive_memory(id)`: تنقل الذاكرة الى حالة archived (محفوظة لكن غير نشطة)
- `deprecate_memory(id)`: تنقل الذاكرة الى حالة deprecated (قيد الازالة)
- `delete_memory(id)`: تنقل الذاكرة الى حالة deleted (مزالة)
- `get_active_memories()`: ترجع فقط الذكريات في حالة active
- `record_access(id, tick)`: تسجل عملية وصول (تحديث last_accessed و access_count)

### 2.3 Memory Utility Scoring (تقييم فائدة الذاكرة)
**المسار**: `virtual_genesis/runtime/memory_os/utility.py`

يحسب درجة فائدة لكل ذاكرة بناء على 4 عوامل مرجحة:
- retrieval_frequency (0.25): كم مرة استُرجعت
- recency (0.30): متى آخر مرة استُرجعت
- decay_score (0.25): حالة الاضمحلال الحالية
- outcome_quality (0.20): هل ساهمت في نتيجة جيدة

### 2.4 Forgetting Policy (سياسة النسيان)
**المسار**: `virtual_genesis/runtime/memory_os/forgetting_policy.py`

تطبق سياسة نسيان منتج:
1. تحسب utility لكل الذكريات النشطة
2. تؤرشف الذكريات تحت utility_threshold (مع احترام max_archive_ratio)
3. تُهمل الذكريات تحت utility_threshold * 0.5 (اسوأ الحالات)
4. ترجع تقرير بالقرارات المتخذة

### 2.5 Pipeline Integration (تكامل مع المسار)
**المكان**: `virtual_genesis/runtime/pipeline/minimal_run.py`

عند تفعيل `use_productive_forgetting=True`:
- قبل الاسترجاع: `store.apply_decay(0.05)`
- بعد تخزين episode_memory: تطبيق forgetting_policy اذا عدد الذكريات النشطة > 10
- الـ retriever يستخدم `get_active_memories()` بدلا من `all()`

---

## 3. قرارات التصميم

### 3.1 Linear Decay بدلا من Exponential
اخترنا linear decay (staleness * rate) بدلا من exponential decay (Ebbinghaus الاصلي) لان:
- ابسط في الفهم والتنبؤ
- لا يحتاج لمعايرة دقيقة
- كافي كبداية لاختبار الفرضية
- يمكن استبداله لاحقا اذا ثبتت الحاجة

### 3.2 صيغة Utility
```python
utility = 0.25 * retrieval_frequency + 0.30 * recency + 0.25 * decay + 0.20 * outcome_quality
```
الاوزان مستوحاة من الابحاث:
- **recency (0.30)**: الاعلى لان Ebbinghaus يؤكد ان الحداثة اقوى مؤشر
- **retrieval_frequency (0.25)**: RIF يقول ان الاسترجاع المتكرر يقوي الذاكرة
- **decay (0.25)**: يعكس الحالة التراكمية للذاكرة
- **outcome_quality (0.20)**: الاقل لان ليست كل ذاكرة لها outcome واضح

### 3.3 max_archive_ratio Safety
- القيمة الافتراضية: 0.3 (لا تؤرشف اكثر من 30% في دورة واحدة)
- يمنع over-forgetting (الازالة الجماعية التي قد تفقد معلومات مهمة)
- desirable difficulty: صعوبة مناسبة = لا تزيل كل شيء دفعة واحدة

### 3.4 عتبة > 10 ذكريات
- الـ forgetting policy لا تعمل اذا عدد الذكريات النشطة <= 10
- منطقي: لا معنى للنسيان في ذاكرة صغيرة جدا
- يمنع التدمير المبكر للذكريات في بداية التشغيل

---

## 4. العلاقة بالنظرية

| قسم نظري | ما نفذناه |
|-----------|-----------|
| القسم 5: الابعاد الخمسة للنسيان | decay (temporal), access frequency (usage), utility (relevance), archiving (preservation), deletion (permanent removal) |
| القسم 11: Memory Lifecycle Engine | store operations: active -> archived -> deprecated -> deleted |
| القسم 12: قوانين النسيان المنتج | القانون 1 (الزمن يضعف) = apply_decay, القانون 2 (الاسترجاع يقوي) = record_access, القانون 3 (الفائدة تحدد البقاء) = utility scoring |

---

## 5. كيفية الاستخدام

### تشغيل في الـ pipeline:
```python
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline
from virtual_genesis.core.objects.task_case import TaskCase

task = TaskCase.create(
    prompt_text="Compare X with Y",
    expected_primary_family="comparison"
)

result = run_minimal_pipeline(
    task,
    use_productive_forgetting=True,  # تفعيل النسيان المنتج
)
```

### استخدام مباشر لمكونات النسيان:
```python
from virtual_genesis.runtime.memory_os.store import InMemoryMemoryStore
from virtual_genesis.runtime.memory_os.utility import compute_memory_utility
from virtual_genesis.runtime.memory_os.forgetting_policy import apply_forgetting_policy

store = InMemoryMemoryStore()
# ... تخزين ذكريات ...

# تطبيق الاضمحلال
store.apply_decay(decay_rate=0.05)

# تطبيق سياسة النسيان
report = apply_forgetting_policy(
    store,
    utility_threshold=0.3,
    max_archive_ratio=0.3,
)
print(f"Archived: {report['archived_count']}")
print(f"Deprecated: {report['deprecated_count']}")
print(f"Still active: {report['total_active']}")
```

---

## 6. الحالة الحالية

- الميزة مبوبة خلف `use_productive_forgetting: bool = False` في minimal_run.py
- **ليست** ضمن الـ frozen defaults حاليا
- backward compatible: كل الـ defaults تحافظ على السلوك القديم
- 32 اختبار يغطون جميع المكونات
- MemoryUnit اضيف لها 4 حقول جديدة (decay_score, last_accessed, access_count, memory_status) كلها بقيم افتراضية

---

## 7. الخطوات التالية

1. **Abstraction-Assisted Forgetting**: بدلا من حذف كل ذاكرة منخفضة الفائدة، يمكن دمج عدة ذكريات متشابهة في ذاكرة واحدة مجردة (abstract summary)
2. **Negative Retention**: تتبع الذكريات التي كان من الافضل نسيانها (ذكريات ادت لقرارات خاطئة) لتسريع نسيانها في المستقبل
3. **Retrieval-Induced Suppression (Active Mode)**: بدلا من الاعتماد فقط على decay الطبيعي لاضعاف غير المسترجع، يمكن اضافة آلية تثبيط صريحة تضعف الذكريات المنافسة عند الاسترجاع
4. **تجارب مقارنة**: تشغيل retention vs forgetting على مسار تحسن طويل الامد لقياس هل النسيان المنتج يحسن الاداء الكلي
5. **ربط بالـ anomaly system**: الذكريات المرتبطة بـ anomalies مؤكدة يمكن ان تحصل على حماية من النسيان

---

*نهاية مذكرة تنفيذ النسيان المنتج*
