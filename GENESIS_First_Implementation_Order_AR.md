# Virtual-GENESIS First Implementation Order (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة هي **آخر خارطة قصيرة جدًا قبل الكود**.

هي لا تعيد النظرية ولا الـ specs، بل تجيب ببساطة عن:

> إذا بدأنا الآن، ما أول ملف؟ ثم ما الذي بعده؟
> ما الترتيب العملي الأقل خطورة والأعلى فائدة؟

الهدف:
- منع البدء من نقطة خاطئة
- تقليل hidden dependencies
- الوصول سريعًا إلى أول slice runnable

---

# 1) المبدأ التنفيذي
ابدأ من:
1. **البيانات الأساسية**
2. ثم **state substrate**
3. ثم **persistent memory**
4. ثم **runtime reasoning**
5. ثم **verification**
6. ثم **concept logic**
7. ثم **economy control**
8. ثم **evaluation**

### السبب
هذا الترتيب يجعل كل طبقة تبنى فوق طبقة مستقرة قبلها.

---

# 2) الترتيب الأولي file-by-file / module-by-module

## Step 1 — Base shared schemas
### ابدأ بملفات مثل:
- `core/objects/base.py`
- `core/objects/provenance.py`
- `core/objects/scope.py`
- `core/objects/cost.py`
- `core/ontology/enums.py`

### الهدف
وجود اللبنات الأساسية التي سترث منها بقية الـ objects.

### Done when
- كل واحدة لها schema واضحة
- serialization works

---

## Step 2 — Core object models
### بعدها مباشرة:
- `core/objects/task.py`
- `core/objects/blackboard.py`
- `core/objects/memory.py`
- `core/objects/concept.py`
- `core/objects/decision.py`
- `core/objects/ledger.py`
- `core/objects/eval.py`

### الهدف
امتلاك object layer كاملة للـ prototype slice.

### Done when
- يمكن إنشاء instances valid
- references واضحة
- IDs mandatory

---

## Step 3 — Blackboard core runtime
### ثم:
- `runtime/blackboard_core/service.py`
- `runtime/blackboard_core/snapshots.py`

### الوظائف الأولى
- create_blackboard
- update_blackboard
- get_blackboard
- snapshot_blackboard
- close_blackboard

### الهدف
وجود state substrate runnable قبل أي logic ثقيل.

---

## Step 4 — Task ingress
### ثم:
- `runtime/task_ingress/service.py`

### الوظائف الأولى
- ingest_task
- normalize_task
- estimate_task_properties

### الهدف
من user input → TaskObject → Blackboard seed

---

## Step 5 — Memory OS minimal
### ثم:
- `runtime/memory_os/store.py`
- `runtime/memory_os/retriever.py`
- `runtime/memory_os/forgetting.py`
- `runtime/memory_os/reports.py`

### الوظائف الأولى
- store_memory
- retrieve_memory
- archive_memory
- deprecate_memory

### الهدف
Baseline retrieval-only path يصبح ممكنًا.

---

## Step 6 — Reasoning runtime minimal
### ثم:
- `runtime/reasoning_runtime/service.py`

### الوظائف الأولى
- run_reasoning
- generate_candidate_claims
- attach_reasoning_to_blackboard

### الهدف
تشغيل المسار المباشر للإجابة، ولو بشكل بسيط.

---

## Step 7 — Verification runtime minimal
### ثم:
- `runtime/verification_runtime/service.py`

### الوظائف الأولى
- verify_output
- record_verification
- is_good_enough

### الهدف
عدم الاكتفاء بإخراج answer بلا check.

---

## Step 8 — End-to-end baseline slice
### هنا لا تضف modules جديدة
بل كوّن runner بسيط يربط:
- task_ingress
- blackboard
- memory retrieval
- reasoning
- verification
- episode storage

### ملف مقترح
- `runtime/pipeline/minimal_run.py`

### الهدف
الحصول على أول run كاملة قابلة للتكرار.

---

## Step 9 — Concept engine minimal
### ثم:
- `runtime/concept_engine/selector.py`
- `runtime/concept_engine/proposer.py`
- `runtime/concept_engine/scope.py`
- `runtime/concept_engine/registry.py`

### الوظائف الأولى
- propose_concepts
- contrastive_concept_search
- draft_scope
- promote_concept

### الهدف
إدخال أول mechanism تختبر Thesis 1.

---

## Step 10 — Economy control minimal
### ثم:
- `runtime/economy_control/router.py`
- `runtime/economy_control/escalation.py`
- `runtime/economy_control/ledger.py`
- `runtime/economy_control/reports.py`

### الوظائف الأولى
- choose_tier
- should_escalate
- record_cognitive_spend

### الهدف
إدخال أول mechanism تختبر Thesis 2.

---

## Step 11 — Evaluation harness minimal
### ثم:
- `eval/conditions/`
- `eval/runners/run_condition.py`
- `eval/runners/compare_conditions.py`
- `eval/reports/summary.py`

### الهدف
تشغيل baselines والـ conditions وإنتاج evidence أولية.

---

# 3) ما أول شيء runnable يجب أن نراه؟

## First runnable target
Task واحدة تدخل → Blackboard تُنشأ → Memory retrieval → Reasoning → Verification → Final result + Episode stored

### قبل أي Concept أو Economy logic
يعني أول نجاح عملي يجب أن يكون:
# **Minimal baseline path works end-to-end**

---

# 4) ما أول شيء يجب ألا نفعله؟
- لا تبدأ بـ concept engine قبل blackboard وmemory
- لا تبدأ بـ tier router قبل وجود reasoning path وverification
- لا تبدأ بـ evaluation harness قبل وجود runnable baselines
- لا تبدأ بـ reports كثيرة قبل وجود data حقيقية
- لا تبدأ بـ theory builder أو anomaly manager الآن

---

# 5) أول deliverable واقعي
نقترح أن يكون أول deliverable بعد بدء الكود هو:

## Deliverable 1
**Minimal Baseline Run Demo**

ويجب أن يثبت:
- TaskObject created
- BlackboardObject created
- Memory pack injected
- Reasoning output produced
- Verification output produced
- Episode summary stored

إذا تحقق هذا، ننتقل بعدها إلى:
- concept formation
- economy routing

---

# 6) الترتيب الأقصر جدًا
إذا أردت الترتيب في صورة bullets سريعة:

1. base schemas
2. object models
3. blackboard core
4. task ingress
5. memory OS minimal
6. reasoning runtime minimal
7. verification runtime minimal
8. minimal end-to-end pipeline
9. concept engine minimal
10. economy control minimal
11. evaluation harness minimal

---

# 7) القرار النهائي
لا يوجد بعد هذه الوثيقة سبب منطقي قوي لمزيد من التوثيق العام.

الخطوة التالية الطبيعية الآن هي:

# **Start implementation from Step 1**

وإذا احتجنا لاحقًا وثيقة داعمة، تكون فقط وثائق موضعية أثناء البناء، لا موجات تنظير جديدة.
