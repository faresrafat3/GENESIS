# 🎯 GENESIS Agent Charter — READ THIS FIRST

**آخر تحديث:** 2026-06-05
**الحالة:** نشط — يتم تطبيقه في كل session

> **هذا الملف يجب أن يُقرأ في بداية كل session جديدة بواسطة أي agent يشتغل على المشروع.**
> فارس (owner المشروع) طلب أن يُحفظ هذا الملف كـ persistent memory.

---

## 🔴 القواعد الحاكمة (Non-negotiable)

### 1. الورقة البحثية هي المحور
- **كل شغل نعمله يجب أن يغذي الورقة `paper/`**
- مش code لوحده، مش analysis لوحده — كل حاجة تدخل في المنتج النهائي
- الهدف: **أقوى ورقة في المجال** (paper-quality، مبالغة في التفاصيل مطلوبة)

### 2. مبالغة التفاصيل مطلوبة
- كل ادعاء ← جدول أو رسم أو شاهد رقمي
- كل experiment ← multiple sub-analyses (per-domain, per-difficulty, per-model, per-token-usage)
- كل hypothesis ← test explicitly designed لها
- **مفيش "high level summary"** — كله يتفصّل

### 3. Cross-reference من الأوراق المسروقة
- عندنا **100+ سرقة موثقة** في `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md`
- الأوراق الأساسية: AlphaEvolve/FunSearch, Aletheia, Co-Scientist (DeepMind)
- **كل شغل جديد**: نراجع الأوراق ونشوف:
  - هل عندهم منحنى/جدول يستحق أن نقلده؟
  - هل عندهم سؤال بحثي نجاوبه من زاوية GENESIS؟
  - هل نتائجهم تعارض أو تدعم اكتشافاتنا؟

### 4. Research posture, not product posture
- **نقيس أولاً، نبني ثانياً** (measure first, build second)
- **باينات strong قبل أي إضافة complexity**
- الـ router للـ instant/thinking = **مؤجل حتى baseline يستقر**
- Multi-provider pool = **مؤجل** (deferred)
- إصلاح scaffolding + قياس impact = **الأولوية القصوى**

### 5. Security discipline (persistent)
- **أبداً** لا تضع API keys في أي committed file
- قبل `git commit`: scan لكل key patterns (sk-*, gsk_, csk-, github_pat_, ghp_, nvapi-, AIzaSy)
- `.env` محلي فقط، مش في git
- التحقق موجود في scripts الـ commit

---

## 📊 الحالة الحالية للمشروع (Snapshot)

**التاريخ:** 2026-06-05

### Facts Established (باينات مثبتة):
- **gpt-oss-120b official GPQA Diamond:** 80.1% (from NVIDIA/OpenAI card)
- **gpt-oss-120b pure baseline (free tier, our measurement):** **75.00%** (20q subset, 0 invalid)
- **GENESIS pre-fix (run_53) على same model:** **30.30%** (198q)
- **Gap of -45 points = scaffolding bugs 100%** (proven by X² test + diagnosis)

### Infrastructure المبنية (باتوسع مستمر):
1. `tools/api_key_pool.py` — 11-key OpenRouter pool مع rotation
2. `tools/model_registry.py` — 13 models with official benchmarks
3. `tools/providers.py` — 9 free providers documented
4. `tools/run_multi_model_benchmark.py` — direct benchmark runner
5. `genesis/llm_helpers.py` — battle-tested LLM utilities (35 tests passing)
6. `genesis/orchestrator.py` — scaffolding fixes applied

### Tests: 463/463 passing ✓

### Critical Unknown (الأولوية):
**Does GENESIS post-fix > 75%?**
- If yes → **proof of architecture value** ✨
- If no → need ablation study

### Deferred (مش دلوقتي):
- ⏳ Instant vs Thinking architecture study (بعد baseline يستقر)
- ⏳ Multi-provider pool implementation
- ⏳ SWE-bench integration
- ⏳ Paper writing "strategy" (نحن بنعمل الورقة نفسها الآن)

---

## 📚 هيكل الورقة (Paper Skeleton)

```
paper/
├── README.md                 ← فهرس + workflow
├── PAPER_MAIN.md             ← ملف مجمّع (يُبنى من الأقسام)
├── 00_abstract.md            ← ملخص
├── 01_introduction.md        ← مقدمة + motivation + contributions
├── 02_related_work.md        ← الأوراق المسروقة + literature
├── 03_methodology.md         ← GENESIS architecture + benchmarks
├── 04_experimental_setup.md  ← infrastructure + models + evaluation
├── 05_baseline_results.md    ← pure baseline measurements
├── 06_scaffolding_analysis.md ← الـ 5 bugs + diagnosis
├── 07_genesis_results.md     ← GENESIS post-fix results (بينبني)
├── 08_ablation_studies.md    ← أي component يضيف قيمة (بينبني)
├── 09_discussion.md          ← التفسيرات + المفاجآت
├── 10_limitations.md         ← ما لم نغطه
├── 11_future_work.md         ← instant vs thinking + غيرها
├── 12_appendices.md          ← جداول تفصيلية + prompts + code
├── figures/                  ← رسوم بيانية (SVG/PNG generated)
├── data/                     ← raw data للجداول
└── sources/                  ← notes على الأوراق المسروقة
```

---

## 🔁 Workflow في كل session جديدة

### 1. عند البدء:
```bash
# اقرأ الـ charter ده (الملف اللي بتقرأه دلوقتي)
cat AGENT_CHARTER.md

# اقرأ آخر تقرير حالة
cat GENESIS_RESEARCH_REPORT_Current_State_*.md | tail -100

# اقرأ فهرس الورقة
cat paper/README.md

# شوف آخر commits
git log --oneline -10
```

### 2. عند العمل على تجربة جديدة:
1. **Design** — كتب Method قبل الـ code
2. **Register** — أضفها في paper/07_genesis_results.md كـ "Planned"
3. **Run** — نفذ التجربة
4. **Document** — اكتب في نفس الملف: Data + Analysis + Interpretation
5. **Update tables/figures** — أضف row جديد في الجداول المقارنة
6. **Cross-reference** — لو التجربة تجاوب على سؤال من الأوراق المسروقة، اذكر ذلك

### 3. عند إضافة feature في الكود:
1. **Justify** — ليه؟ (يجب أن يخدم سؤال بحثي)
2. **Document** — كل change في paper/06_scaffolding_analysis.md أو المناسب
3. **Test** — كل feature له test (existing pattern: `tests/`)
4. **Measure** — before/after comparison لو ممكن

### 4. عند الـ commit:
- **security scan إلزامي**
- **الرسالة**: تشرح تأثير التغيير على الورقة، مش بس على الكود
- **مثال جيد**: "feat: run T3 ablation without evolutionary discovery → adds Table 5 to paper/08_ablation.md"

---

## 🎨 معايير التفاصيل (Level of Detail)

### للجداول:
- **مش سطر واحد** — كل جدول له:
  - Header واضح
  - Caption يشرح ماذا يقيس
  - Notes تحته للتفسير
  - Reference للـ raw data file في `paper/data/`

### للرسوم البيانية:
- **مش placeholder** — كل رسم:
  - SVG أو PNG في `paper/figures/`
  - Caption تفصيلي
  - Legend واضح
  - يشير للـ hypothesis اللي يختبرها

### للحجج (arguments):
- **claim + evidence + reference**
- **لا "may" أو "could" بدون test**
- كل mention لعدد ← ملف raw data يحتويه

---

## 🎯 الأولويات (بترتيب صارم)

### حالياً (Session-active):
1. **بناء هيكل الورقة كامل** (skeleton كل الملفات)
2. **ملء 5 أقسام أولى بمحتوى قوي**: Abstract, Intro, Related Work, Methods, Baseline Results
3. **استخراج القوالب** من AlphaEvolve/FunSearch/Aletheia/Co-Scientist papers
4. **جداول ورسوم** لكل التجارب الـ 6 اللي عملناها

### قادم قريباً:
5. تشغيل T1: GENESIS post-fix على 20q → قسم 07
6. لو T1 يعطي > 75% → توسيع لـ 198q (T2) → قسم 07
7. Ablation studies (T3) → قسم 08

### مؤجل (لا تلمسه إلا لو فارس طلب):
- Instant vs Thinking architecture study
- Multi-provider pool implementation
- SWE-bench integration
- Router logic (engineering)

---

## 📖 الأوراق الأساسية للتأثر بها (Sources to Steal From)

### DeepMind (المصدر الأساسي):
1. **AlphaEvolve** — evolutionary discovery, LLM-driven mutation, evaluator gating
   - `GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md`
2. **FunSearch** — program search, sampling temperature, database of programs
   - نفس الملف
3. **Aletheia** — proof-driven generate-verify-revise, verification loops
   - `GENESIS_DeepMind_Aletheia_Theft_AR.md`
4. **Co-Scientist** — multi-agent scientific research
   - `GENESIS_DeepMind_CoScientist_Theft_AR.md`

### أنواع المنحنيات/الجداول اللي نقلدها:
- **AlphaEvolve Figure 3**: score vs generation (evolutionary progress curves)
- **FunSearch Table 1**: baseline vs discovered algorithms comparison
- **Aletheia Figure 2**: iteration count vs correctness
- **Co-Scientist Table 2**: multi-agent vs single-agent performance
- **GPQA paper**: per-domain accuracy breakdowns
- **gpt-oss model card**: reasoning-effort scaling curves

### أسئلة نجاوبها في ورقتنا (من الأوراق دي):
- ⭐ هل الـ evolutionary search بيضيف قيمة فوق pure LLM؟ (AlphaEvolve H)
- ⭐ هل الـ verifier بتحسن الـ generator؟ (Aletheia H)
- ⭐ هل multi-agent بيتفوق على single-agent؟ (Co-Scientist H)
- ⭐ هل reasoning tokens ت correlate مع accuracy؟ (gpt-oss discovery — عندنا counter-evidence!)

---

## 🚨 Common Mistakes to Avoid

Based on فارس's explicit feedback:
1. ❌ **لا تقترح router أو engineering قبل ما البحث يخلص**
2. ❌ **لا تحط API keys في أي ملف** حتى لو "temporary"
3. ❌ **لا تعمل over-specialization لـ task واحد** (زي spaceship-titanic "Mars" bug)
4. ❌ **لا تعتمد على fake results** (default to "A" فى invalid = fake الـ 30%)
5. ❌ **لا تجعل التقرير سطحي** — فارس عايز مبالغة تفاصيل
6. ❌ **لا تنسى cross-reference الأوراق المسروقة**

---

## ✅ Definition of Done للأي شغل

قبل ما تعتبر شغل "تم":
- [ ] هل ضاف row/section في الورقة؟
- [ ] هل عنده جدول أو رسم؟
- [ ] هل تم cross-reference مع الأوراق المسروقة؟
- [ ] هل الـ code له test؟
- [ ] هل الـ security scan نجح؟
- [ ] هل commit message يوضح تأثيره على الورقة؟
- [ ] هل تم تحديث `paper/README.md` بالتقدم؟

---

## 🔗 المراجع الرئيسية للـ Agent الجديد

عند بدء أي session جديدة، اقرأ بالترتيب:
1. `AGENT_CHARTER.md` (هذا الملف)
2. `GENESIS_RESEARCH_REPORT_Current_State_2026-06-05_AR.md`
3. `paper/README.md`
4. `paper/PAPER_MAIN.md` (اللي بيتوسع)
5. `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md` (100+ سرقة)
6. آخر 10 commits: `git log --oneline -10`

**عند أي شك: اسأل فارس. لا تفترض.**

---

## 📝 التوقيع

هذا الـ Charter مبني على طلب فارس الصريح في session 2026-06-05:

> "عايز نعمل ونتابع ونكمل شغل علي الورقه طول الوقت علاقات وجداول ورسوم بيانيه كثيره بالتفصيل لاسئله معينه و كده وهكذا كاننا بنعمل اقوي ورقه في المجال عايزك تبالغ عادي في التفاصيل والحاجات الياما اللي هتعملها في الورقه ده مهم ليا جدا جدا وخد من الاوراق اللي سرقنا منها المنحيات او المواضيع او غيرها عادي و تابعها وجاوبها في مشروعنا وهكذا فاهمني وسجل واحفظ ده ليك عشان لما تكمل شغل معايا في سيشن جديد ولا حاجه في المشروع تمام"

**الترجمة الالتزامية:** الورقة = المحور. تفاصيل مبالغ فيها. اسرق منحنيات من الأوراق المسروقة. اسجل هذا للـ session القادمة.

---

**نهاية الـ Charter. الشغل الفعلي يبدأ من `paper/`.**
