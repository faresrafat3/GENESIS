# API-SIA / Virtual-GENESIS

تصميم أولي لنظام تحسين ذكي عملي مبني فوق OpenRouter API بدون تحديث أوزان مباشرة للموديلات العامة.

## الفكرة
بدل تقليد SIA حرفيًا (Harness + Weight Updates)، نبني طبقة ذكاء خارجية فوق LLM API:
- Router للنماذج
- Memory طويلة وقصيرة المدى
- Prompt Compiler
- Verifier / Judge
- Candidate Search
- Skill Library
- Regression Harness
- Optional learned small modules later

## لماذا هذا مناسب؟
لأن القيود الحالية:
- LLM عبر OpenRouter API
- لا توجد بنية تدريب RL/LoRA كبيرة
- نريد تحسنًا تراكميًا عمليًا وقابلًا للإنتاج

## الاسم المقترح
**Virtual-GENESIS**
أو
**API-SIA**

## الهدف
تحقيق:
1. ذكاء أعلى على مستوى النظام
2. دقة أعلى عبر التحقق والمقارنة
3. تعلّم شبه تراكمي عبر الذاكرة والسياسات
4. تكلفة أقل من weight updates
5. سهولة نقل بين النماذج والمزودين

## المكونات
### 1) Orchestrator
- يدير الـ workflow
- يختار المسار المناسب
- يجمع traces وmetrics

### 2) Model Router
- planner model
- worker model
- critic/judge model
- fallback models

### 3) Prompt Compiler
- يولّد system/task prompts بحسب نوع المهمة
- يدمج memory وfew-shot وconstraints

### 4) Memory Layer
- episodic memory
- failure memory
- success memory
- strategy memory
- example bank

### 5) Candidate Search
- generate N candidates
- critique
- revise
- compare
- re-rank

### 6) Verifier Layer
- schema checks
- deterministic rules
- test execution
- consistency checks
- judge ensemble

### 7) Skill Library
- reusable prompts
- tool recipes
- domain heuristics
- debugging strategies

### 8) Regression Harness
- golden tasks
- benchmark suite
- cost/latency logs
- failure taxonomy

## الوضع التشغيلي
### Request lifecycle
1. تصنيف المهمة
2. اختيار profile
3. استدعاء planner
4. بناء prompt
5. توليد candidates
6. التحقق/التنفيذ
7. ranking
8. إخراج الإجابة
9. حفظ الدروس المستفادة

## مستويات الذكاء التي نحاكيها
- internalization جزئي عبر memory + retrieval
- policy improvement خارجي عبر dynamic routing
- self-improvement عبر prompt patching + lesson extraction

## لماذا أقوى من SIA عمليًا في هذا السياق؟
- لا يحتاج weight updates
- مناسب لـ OpenRouter API
- يمكنه الاستفادة من تعدد الموديلات
- أسهل في الصيانة والتوسع
- أقل مخاطرة في الانهيار بعد update

## مزايا OpenRouter المفيدة
- model fallbacks
- provider routing
- session_id sticky routing
- response caching
- structured outputs
- tool/function calling
- server tools
- workspaces / observability
- private models later

## المرحلة 1 (MVP)
- Python backend
- OpenRouter client
- 3 roles: planner / worker / judge
- JSON structured outputs
- memory بسيطة
- retry + compare
- logging
- benchmark صغير

## المرحلة 2
- vector memory
- prompt compiler متقدم
- self-critique loop
- disagreement judge
- domain skill packs

## المرحلة 3
- learned router/ranker محلي
- cost-aware planning
- regression gating
- shadow evaluations

## المرحلة 4
- bring your own tuned endpoint
- private model route عبر OpenRouter إذا توفر الوصول

## stack مقترح
- Python
- FastAPI
- SQLite/Postgres
- simple embedding store initially
- OpenRouter API
- pydantic for schemas
- pytest for regression suite

## مخرجات التنفيذ المطلوبة
1. core orchestrator
2. provider/model routing config
3. memory store
4. verifier pack
5. benchmark harness
6. evaluation reports

## المخاطر
- زيادة التعقيد orchestration-wise
- تكلفة الاستدعاءات إذا candidate count كبير
- judge bias
- retrieval pollution
- domain drift

## تخفيف المخاطر
- hard caps على retries
- deterministic validators أولًا
- small benchmark دائم
- per-task profile configs
- regression checks قبل أي تغيير افتراضي

## المقارنة العادلة مع SIA
نقارن على:
- accuracy
- robustness
- latency
- cost per solved task
- reproducibility
- human maintenance burden

## اسم تسويقي/بحثي بديل
- AIA-X
- Virtual-GENESIS
- API-SIA
- Scaffold-Only Plus
- Externalized Self-Improvement Agent
