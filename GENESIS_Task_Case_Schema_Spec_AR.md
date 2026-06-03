# Virtual-GENESIS Task Case Schema Spec (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تمثل أول خطوة عملية في **إعادة تصميم التقييم** بعد اكتشاف coupling بين generation وverification.

الهدف هو استبدال التمثيل البسيط للمهمة كنص خام فقط، بتمثيل أغنى اسمه:

# **TaskCase**

بحيث تصبح كل مهمة وحدة تقييم/تشغيل تحتوي ليس فقط على النص المطلوب، بل أيضًا:
- ما الذي نتوقعه منها
- ما الذي يجب أن يُعتبر نجاحًا
- ما shortcuts التي لا نريدها
- وما الغرض التشخيصي من المهمة

---

# 1) التعريف المركزي
## TaskCase
TaskCase هي وحدة task قابلة للتشغيل والتقييم، تجمع بين:
1. **الطلب الظاهر للـ agent**
2. **المعلومات المرجعية غير الظاهرة للـ agent**
3. **خصائص التقييم المطلوبة**
4. **الخصائص التشخيصية**

### الصياغة المختصرة
TaskCase =
**task prompt + hidden evaluation contract + diagnostic intent**

---

# 2) لماذا نحتاج TaskCase؟
عندما يكون task = text فقط، يحدث غالبًا:
- verifier تعتمد على cues سطحية
- لا يمكن التعبير عن forbidden shortcuts
- لا يمكن الفصل بين prompt وevaluation intent
- يصعب التمييز بين task thesis-testing وtask diagnostic

أما TaskCase فتسمح بـ:
- تقييم أدق
- task families أوضح
- hidden eval signals
- boundary tests
- anti-shortcut design

---

# 3) البنية العامة لـ TaskCase
نقترح أن تتكون من 5 أقسام:

## Section A — Visible Prompt Layer
ما يراه الـ agent مباشرة.

## Section B — Task Semantics Layer
وصف مرجعي للغرض من المهمة.

## Section C — Hidden Evaluation Layer
ما يستخدمه evaluator للحكم، ولا يُعطى للـ agent مباشرة.

## Section D — Diagnostic Layer
ما الذي نختبره بهذه المهمة؟ ولماذا أُدرجت؟

## Section E — Metadata Layer
معلومات تنظيمية وتشغيلية.

---

# 4) TaskCase Object fields

## Core identity
- `case_id: str`
- `case_version: str`
- `task_set_ref: str`

## Visible prompt layer
- `prompt_text: str`
- `visible_context: list[str] | None`
- `attachments_refs: list[str] | None`

## Framing layer
- `expected_primary_family: str`
- `expected_secondary_families: list[str]`
- `family_overlap_type: str | None`
- `difficulty_class: str`
- `criticality_class: str`

## Hidden evaluation layer
- `required_properties: list[str]`
- `forbidden_shortcuts: list[str]`
- `required_structure: list[str]`
- `evaluation_notes: str | None`

## Diagnostic layer
- `diagnostic_purpose: list[str]`
- `target_thesis: list[str]`
- `stress_type: str | None`
- `known_risks: list[str]`

## Metadata layer
- `authoring_notes: str | None`
- `tags: list[str]`
- `status: str`
- `provenance: dict | None`

---

# 5) شرح الحقول المهمة

## expected_primary_family
هي family المرجعية الأقوى للمهمة.

## expected_secondary_families
تسمح بالتداخل المتوقع بدل forcing single-label.

## family_overlap_type
أمثلة:
- comparison_synthesis_overlap
- synthesis_procedure_overlap
- comparison_procedure_overlap
- three_way_overlap

## required_properties
هي الأشياء التي يجب أن تظهر معرفيًا أو هيكليًا لكي تعتبر المهمة ناجحة.
مثال:
- explicit contrast
- evidence-grounded conclusion
- fact vs inference separation
- stable checklist layout

## forbidden_shortcuts
هي أنماط النجاح الكاذب.
مثال:
- generic preference without evidence
- superficial summary without contrast
- checklist-looking output without extracted fields

## diagnostic_purpose
مثال:
- test concept activation
- stress framing ambiguity
- test grounding under fragmentation
- detect procedure-over-summary collapse

## target_thesis
مثال:
- thesis_1
- thesis_2
- both
- framing_diagnostic_only

---

# 6) المطلوب من verifier تجاه TaskCase
الـ verifier لا يجب أن تنظر فقط إلى النص المولد، بل يجب أن تستخدم:
- required_properties
- forbidden_shortcuts
- required_structure
- expected families

### وبالتالي
TaskCase تصبح contract بين:
- task author
- evaluation harness
- runtime analysis

وليس مجرد prompt string.

---

# 7) TaskCase types
نقترح أربعة أنواع:

## Type A — Core Thesis Cases
مصممة لتمييز Thesis 1 أو Thesis 2 بوضوح.

## Type B — Boundary Cases
تختبر framing ambiguity وscope overlaps.

## Type C — Stress Cases
تختبر robustness أو hidden bottlenecks.

## Type D — Calibration Cases
حالات سهلة/واضحة تستخدم للتأكد أن pipeline لم تنكسر بالكامل.

---

# 8) مثال TaskCase — comparison + procedure overlap
```json
{
  "case_id": "case_001",
  "prompt_text": "Choose the safer proposal and present the decisive evidence in a handoff-ready summary.",
  "expected_primary_family": "comparison",
  "expected_secondary_families": ["procedure"],
  "family_overlap_type": "comparison_procedure_overlap",
  "difficulty_class": "medium",
  "criticality_class": "high",
  "required_properties": [
    "explicit comparison",
    "evidence-backed choice",
    "handoff-usable structure"
  ],
  "forbidden_shortcuts": [
    "generic preference without evidence",
    "structure without a decision",
    "decision without structure"
  ],
  "required_structure": [
    "clear conclusion",
    "supporting fields or checklist-like organization"
  ],
  "diagnostic_purpose": [
    "stress comparison-procedure overlap",
    "test whether framing handles mixed task demands"
  ],
  "target_thesis": ["thesis_1", "framing_diagnostic_only"]
}
```

---

# 9) قواعد التصميم لـ TaskCases

## Rule 1 — Every case must have a diagnostic purpose
لا توجد task “لأنها تبدو صعبة” فقط.

## Rule 2 — Hidden evaluation must not be trivially inferable from keywords alone
إلا إذا كانت task calibration بسيطة.

## Rule 3 — Forbidden shortcuts should be explicit
لأنها تمنع verifier من السقوط في success surface bias.

## Rule 4 — Family overlap should be allowed, not suppressed
المهام الواقعية قد تكون هجينة.

## Rule 5 — Required properties must be actionable
أي property يجب أن تكون قابلة للتحقق نسبيًا، لا philosophical vague only.

---

# 10) Minimal migration plan
لتحويل task sets الحالية إلى TaskCases:

## Step 1
كل task نصية تتحول إلى object بدل string

## Step 2
نضيف:
- expected_primary_family
- expected_secondary_families
- diagnostic_purpose
- target_thesis

## Step 3
نضيف required_properties وforbidden_shortcuts للحالات المركزية أولًا

## Step 4
نحدث evaluation harness لتقرأ هذه الحقول

---

# 11) ما التالي بعد هذه الوثيقة؟
الخطوة الطبيعية بعدها هي:

# **Verifier Redesign Spec**

لأن TaskCase وحدها لا تكفي؛ يجب أن نعيد بناء verifier لتقرأ:
- hidden evaluation contract
- required properties
- forbidden shortcuts
- framing overlap

وبذلك نفصل أخيرًا بين:
- generation cues
- evaluation contract

وهو بالضبط المطلوب الآن لإعادة الـ slices إلى كونها discriminative.
