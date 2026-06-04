# 🔴 تشخيص حاسم: لماذا حصلنا 30% على GPQA بدلاً من 67-80%؟

**التاريخ:** 2026-06-04
**Run:** `runs/run_53/gen_1` و `gen_2`
**النموذج:** `openai/gpt-oss-120b:free` عبر OpenRouter
**النتيجة الفعلية:** Gen1 = 30.30%, Gen2 = 32.32%
**النتيجة الرسمية للنموذج لوحده:** 67.1% (low) → 73.1% (medium) → **80.1% (high)**
**الفجوة:** ~37 إلى ~50 نقطة مئوية ⚠️

---

## 🎯 الخلاصة في سطر واحد

> **النموذج كان بيرد على أسئلة فاضية** بسبب **bug في حالة الحرف (case)** عند قراءة السؤال من JSON. النتيجة 30% = تخمين عشوائي تقريباً (السقف العشوائي = 25%).

---

## 🔬 الأدلة الرقمية (من `tools/diagnose_run_53.py`)

### 1. توزيع التنبؤات يكشف التخمين العشوائي

| الحرف | تنبؤات النموذج | الإجابات الصحيحة | إجاباته الصحيحة |
|---|---|---|---|
| A | 30 (15%) | 57 (29%) | 12/57 (21%) |
| B | 54 (27%) | 50 (25%) | 17/50 (34%) |
| C | 57 (29%) | 51 (26%) | 18/51 (35%) |
| D | 57 (29%) | 40 (20%) | 13/40 (33%) |

**χ² vs uniform = 10.36** → التوزيع شبه منتظم = **النموذج بيخمن**

لو النموذج كان فعلاً عارف، كان هينجح في معظم أسئلة الـ A (لأنها الأكثر شيوعاً = 57)، بس نسبة نجاحه فيها (21%) **أقل من** نسبة النجاح في B/C/D — ده دليل قاطع على عدم وجود إشارة حقيقية في التنبؤات.

---

## 🐛 الـ Bugs الموجودة (مرتبة بالخطورة)

### 🔴 [CRITICAL] Bug #1: `question_field_case_mismatch`

**الموقع:** `runs/run_53/gen_1/target_agent.py` السطر 159

```python
qtext = q.get('question') or q.get('text') or ''   # ❌ small 'q'
```

**المشكلة:** الـ JSON يحتوي على المفتاح `'Question'` بحرف **كبير**:
```json
{
  "id": 1,
  "Question": "Two quantum states with energies E1 and E2...",
  "options": {"A": "10^-4 eV", ...},
  "correct_answer_letter": "A"
}
```

نتيجة `q.get('question')` = **`None`** → ثم `or ''` = **`""`**

**الـ prompt الفعلي اللي وصل النموذج لكل سؤال:**
```
Question: 
Options:
A: 10^-4 eV
B: 10^-9 eV
C: 10^-11 eV
D: 10^-8 eV
Think step by step. Choose the best answer and output ONLY the letter A, B, C, or D.
```

**الأثر:** النموذج بيختار حرف بدون أي معلومة عن السؤال = **تخمين عشوائي**.

---

### 🟠 [HIGH] Bug #2: `no_chain_of_thought`

**الموقع:** نفس الملف، استدعاء `client.chat.completions.create`

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,
    max_tokens=50,   # ❌ صغير جداً
)
```

**المشكلة:**
1. `max_tokens=50` لا يكفي لأي reasoning جدي
2. `"output ONLY the letter A, B, C, or D"` يمنع النموذج من التفكير
3. **GPQA Diamond الرسمي يُقاس بـ reasoning effort = high** أي chain-of-thought طويل

حتى لو الـ bug الأول اتحل، النموذج بـ 50 token مش هيقدر يفكر في سؤال فيزياء كم، كيمياء عضوية، أو ميكانيكا نسبية.

**الأثر:** حتى لو وصلنا للنموذج السؤال صح، أداءه سيكون أقرب لـ 60% بدلاً من 80%.

---

### 🟡 [MEDIUM] Bug #3: `invalid_answer_defaults_to_A`

```python
if answer not in ["A","B","C","D"]:
    answer = answer[0] if answer and answer[0] in ["A","B","C","D"] else "A"
```

كل رد غير صالح بيتحول لـ `"A"`. ده يخفي مشاكل أعمق ويزيف الإحصائيات (خلانا نشوف 30% بدل ما نشوف "هذا fallback لمعظم الأسئلة").

---

### ✅ [OK] فحص: `pipeline_not_used_in_answer`

الـ pipeline (`run_minimal_pipeline`) **بيتنادى مرة واحدة في بداية الـ run** قبل حلقة الأسئلة. ناتجه (`tier_decision`, `theory_prediction`, `blackboard`) **بيتطبع في الـ stdout بس**، **مش بيتحقن في prompt كل سؤال**.

يعني فعلياً البنية GENESIS **مالهاش أي أثر على إجابات الأسئلة**. هي بتشتغل بشكل منعزل = overhead بدون فائدة.

**ده ليس bug في الـ pipeline نفسه** — ده فجوة في كيفية استخدامه داخل target_agent.

---

## 📊 ماذا يعني هذا للمشروع؟

### الخبر الجيد ✅
- **البنية GENESIS لم تتسبب في الـ 37-50 نقطة المفقودة.** الـ pipeline حتى لم يتم استخدامه فعلاً في الإجابة على الأسئلة.
- الـ "ablation summary" 98.6% baseline القديم على tasks الـ tabular لا يزال صالحاً.
- المشكلة كلها في الـ `target_agent.py` المُولّد من meta-agent، وهو **مولَّد جديد في كل run** فيمكن إصلاحه.

### الخبر المهم ⚠️
- **النتيجة 30%/32% الحالية ليست قياساً حقيقياً لـ GENESIS على GPQA.** هي قياس لـ "نموذج يخمن عشوائياً مع عدد قليل من tokens".
- **لا يصح المقارنة بـ baseline 98.6%** لأن:
  1. الـ baseline كان على tabular tasks مختلفة (spaceship-titanic)
  2. النتائج هنا 30% ≠ "أداء GENESIS على GPQA" بل "أداء meta-agent buggy"

### الـ "سرقة شرعية" المطلوبة الآن
هذا الـ bug **عام جداً** ويكشف نقطة ضعف هيكلية:
- الـ meta-agent prompt ليس فيه قواعد صارمة كافية لقراءة JSON بأي case-style
- الـ feedback agent لم يكتشف الـ bug في Gen2 (كرر نفس الـ pattern)
- لا يوجد **smoke-test تلقائي** يتأكد من أن `qtext != ""` قبل إرسال الـ prompt

---

## 🛠️ الإصلاح المقترح (مرتب بالأولوية)

### إصلاح فوري للأسئلة (تشخيصي، **ليس** تعديل GENESIS):
استخدم `tools/gpqa_pure_baseline.py` الذي كتبناه:
```bash
export OPENROUTER_API_KEY=sk-or-...
python tools/gpqa_pure_baseline.py \
    --model openai/gpt-oss-120b:free \
    --questions_path genesis/tasks/gpqa/data/private/diamond_questions.json \
    --output_path results/gpqa_pure_baseline_gpt-oss-120b-free.json \
    --reasoning high \
    --max_tokens 4096 \
    --limit 0
```

هذا يعطينا **السقف الحقيقي للنموذج** على GPQA (متوقع 60-80%).

### إصلاح هيكلي عام في META_AGENT_PROMPT:
1. **قاعدة "حاول كل case-variants عند قراءة JSON":**
   ```
   When reading dict keys, ALWAYS try multiple case variants:
   q.get('question') or q.get('Question') or q.get('QUESTION') or q.get('text')
   ```
2. **منع `max_tokens` صغير لمهام QA:**
   ```
   For QA tasks, ALWAYS use max_tokens >= 2048 to allow chain-of-thought.
   ```
3. **إزالة "output ONLY the letter":** استبدلها بـ:
   ```
   Reason step by step, then end with:
   ANSWER: <LETTER>
   ```
4. **smoke-test قبل الـ loop:**
   ```python
   sample = build_prompt(questions[0])
   assert "Question:\n" not in sample[:30], "Empty question detected — check JSON keys!"
   ```

### إصلاح هيكلي في FEEDBACK_AGENT_PROMPT:
1. مطالبته بفحص prediction distribution قبل اعتبار الـ Gen ناجحاً
2. لو التوزيع منتظم (شبه عشوائي)، اعتبره failure حتى لو accuracy > random

---

## 🎯 الخطوات التالية المقترحة (بتأكيدك)

| # | الخطوة | الوقت | الغرض |
|---|---|---|---|
| 1 | شغّل `tools/gpqa_pure_baseline.py` مع `--limit 20` أول | 5-10 دقائق | نتأكد الـ API شغال + نشوف السقف الحقيقي |
| 2 | شغّله كامل (--limit 0) لو نتائج 20 الأولى منطقية | 30-60 دقيقة | baseline حقيقي للمقارنة |
| 3 | عدّل META_AGENT_PROMPT بالقواعد العامة فوق | تعديل واحد | يمنع تكرار الـ bug في أي مهمة QA |
| 4 | شغّل run_54 وقارن: pure_baseline vs GENESIS + bug-fixed agent | 30 دقيقة | أول قياس حقيقي لأثر GENESIS على GPQA |

---

## 📂 المراجع والملفات ذات الصلة

- `tools/gpqa_pure_baseline.py` — قياس النموذج لوحده
- `tools/diagnose_run_53.py` — التشخيص الآلي لأي run
- `runs/run_53/gen_1/target_agent.py` — الكود الذي فيه الـ bug
- `runs/run_53/gen_1/evaluation_results.json` — النتائج الخام
- `runs/run_53/gen_1/diagnosis.json` — مخرجات `diagnose_run_53.py`
- المرجع الرسمي للنموذج: [OpenAI gpt-oss Model Card (arXiv:2508.10925)](https://arxiv.org/html/2508.10925v1)

---

## 🧠 درس عام للمشروع

**ما تعلمناه:** القياس بدون baseline نظيف = قياس بلا معنى. حتى لو الـ pipeline والـ evolution كلهم شغالين 100%, أي bug صغير في الـ scaffolding (زي case mismatch) يخفي كل التحسينات.

**القاعدة الجديدة المقترحة:** قبل أي ادعاء عن "تحسن من البنية"، يجب أن يكون عندنا:
1. **Pure baseline** للنموذج لوحده على نفس الـ task
2. **Sanity check** على prediction distribution (مش uniform)
3. **Smoke test** على أول 2-3 prompts للتأكد إنها مش فاضية

هذه القواعد تنتمي لـ **Task 9** (real benchmarks) وتقوي **Task 6** (AlphaEvolve — لأن fitness عشوائية لا تطور أي شيء).
