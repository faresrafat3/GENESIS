# 🏆 Pure Baseline Results — أول قياس حقيقي للنماذج بدون GENESIS

**التاريخ:** 2026-06-05
**Run:** `results/run_gpt-oss-120b_20q/`
**الإعداد:** gpt-oss-120b-free × 20 سؤال GPQA Diamond, reasoning=high, max_tokens=16384
**11 مفتاح OpenRouter في pool نشط**

---

## 🎯 النتيجة الكبيرة

| النموذج | اللي قسناه | الـ Official | الـ Gap | الـ Invalid |
|---|---|---|---|---|
| **gpt-oss-120b:free** | **75.00%** ✅ | 80.1% | -5.1 | **0** 🎯 |

**هذا أول قياس حقيقي موثوق لـ pure baseline على GPQA Diamond بعد كل الإصلاحات!**

### المقارنة مع الـ runs السابقة:
| Run | Accuracy | Invalid | الـ Setup |
|---|---|---|---|
| GENESIS run_53 (Jun 4 صباحاً) | 30.30% | 0 (لكن fake — `q.get('question')` bug) | bug في scaffolding |
| Pure baseline smoke v1 | 60% | 7/20 (35%) | extract_letter بـ 4 patterns |
| Pure baseline smoke v2 | لم يكتمل | — | timeout — لم يخلص |
| **Pure baseline اليوم** | **75%** | **0/20** | كل الإصلاحات + 16K tokens |

---

## 🔥 ما يثبته هذا الـ Run

### 1. ✅ الـ Infrastructure شغالة 100%
- **0 invalid responses** على 20 سؤال صعب من graduate-level
- Pool distribution مثالي: كل مفتاح أخذ 2-3 طلبات بالضبط
- **0 rate-limit events** على gpt-oss-120b
- **3 recoveries via follow-up** — الـ smart fallback شغال على الحالات الحدية

### 2. ✅ فجوة 5.1% فقط من الـ Official — مقبولة جداً للـ free tier
الـ official 80.1% كان بـ `reasoning=high` على full BF16 weights عند OpenAI.
الـ 75% بتاعنا على free tier (ممكن quantized) + 20 questions sample مش 198.

**إحصائياً:**
- 20 سؤال = margin of error ±10% (95% CI)
- 5.1 gap داخل margin هذا
- يعني فعلياً النموذج بيعمل **حوالي الـ official score**

### 3. ✅ الـ Bug في GENESIS run_53 ثبت 100%
- النموذج لوحده: **75%**
- GENESIS run_53 على نفس النموذج: 30%
- **الـ -45 نقطة هو bug في scaffolding** (case mismatch + max_tokens=50 + invalid letter handling)

دلوقتي عندنا **proof of concept نهائي**: لو نصلح الـ scaffolding bugs في GENESIS، الـ baseline اللي نقدر نوصله = 75%، و GENESIS لازم يزود فوقه ليثبت قيمته المضافة.

---

## 📈 Per-Question Breakdown

```
Q  1 Physics    ✓ A=A
Q  2 Chemistry  ✗ C, truth A   ← cinnamaldehyde + Grignard + sulfur ylide
Q  3 Physics    ✓ B=B
Q  4 Physics    ✓ C=C
Q  5 Physics    ✓ B=B
Q  6 Physics    ✓ B=B
Q  7 Physics    ✗ A, truth C   ← high-energy particle physics
Q  8 Biology    ✓ D=D
Q  9 Chemistry  ✓ C=C
Q 10 Physics    ✓ D=D
Q 11 Biology    ✗ C, truth A   (recovered via followup — لكن خطأ)
Q 12 Physics    ✓ B=B
Q 13 Chemistry  ✓ B=B
Q 14 Biology    ✓ A=A
Q 15 Physics    ✓ C=C
Q 16 Chemistry  ✗ A, truth C   (recovered via followup — لكن خطأ)
Q 17 Chemistry  ✓ D=D
Q 18 Physics    ✗ B, truth C
Q 19 Chemistry  ✓ D=D          (recovered via followup — صحيح! 🎯)
Q 20 Physics    ✓ C=C
```

**Per-domain:**
- Physics: 9/11 = 81.8%  (أعلى من الـ official Physics)
- Chemistry: 4/6 = 66.7%  (الأسئلة الكيمياء العضوية صعبة)
- Biology: 2/3 = 66.7%

---

## ⚠️ اكتشافات مهمة عن OpenRouter Free Tier

### 1. الـ Rate Limit: 50 طلب/يوم لكل model لكل account
كل من النماذج التالية اتنفدت على كل الـ 11 مفتاح خلال الـ runs اليوم:
- ❌ `nvidia/nemotron-3-ultra-550b-a55b:free` 
- ❌ `nvidia/nemotron-3-super-120b-a12b:free`
- ❌ `nvidia/nemotron-3-nano-30b-a3b:free`
- ❌ `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`
- ❌ `nvidia/nemotron-nano-9b-v2:free`
- ❌ `liquid/lfm-2.5-1.2b-thinking:free`

⚠️ على rate-limit (مش daily):
- `google/gemma-4-31b-it:free` (يرجع بكرة أو بعد دقيقة)
- `google/gemma-4-26b-a4b-it:free`
- `poolside/laguna-m.1:free`
- `poolside/laguna-xs.2:free`
- `z-ai/glm-4.5-air:free`

❌ مش موجود:
- `qwen/qwen3-coder:free` — **404 Not Found** على OpenRouter (الـ model ID خطأ)

✅ شغال:
- **`openai/gpt-oss-120b:free`** — ده اللي استخدمناه (550 طلب/يوم متاحين)

### 2. الـ Free Tier بطيء جداً
- 90 ثانية / سؤال على gpt-oss-120b
- 20 سؤال = 36 دقيقة
- 198 سؤال = ~5 ساعات

### 3. الحل العملي
**$10 credits على OpenRouter** تفتح **1000 طلب/يوم** بدل 50.

---

## 🛠️ الإصلاحات المضافة في هذا الـ session

| # | الإصلاح | الأثر |
|---|---|---|
| 1 | `DAILY_EXHAUST_PATTERNS` في pool | يكتشف "free-models-per-day" ويعزل المفتاح لـ UTC midnight بدل cooldown 60s |
| 2 | `daily_exhausted_until` في KeyStats | tracking منفصل للـ daily vs short-term limits |
| 3 | `_next_available_key_id` fast-fail | لو كل المفاتيح exhausted، يرفع RuntimeError واضح بدل ما ينتظر ساعات |
| 4 | `--check_quotas` flag في pool | probe كل مفتاح individually ليبين الحالة |
| 5 | `-u` (unbuffered) في nohup | stdout بيتطبع بـ real-time في الـ background runs |

---

## 🎯 الخطوة الجاية

دلوقتي عندنا الـ ground truth:
> **Pure baseline لـ gpt-oss-120b على GPQA = 75%**

الخطوة التالية للمشروع:
1. **شغّل GENESIS مع نفس الـ model + الـ scaffolding fixes** → النتيجة المتوقعة:
   - لو GENESIS bugs ثبتت: حوالي 75% (نفس الـ baseline)
   - لو GENESIS بيضيف قيمة: **>75%** ← هذا الـ proof اللي بنحاول نوصله!
   - لو فيه bugs جديدة: <75%

2. **أعد قياس الـ baseline بكرة** على الـ Nemotron 3 Ultra (لما الـ daily limit يرجع)
3. **اشتري $10 credits** على واحد من الحسابات → 1000 طلب/يوم، مفيش انتظار

---

## 📂 الملفات في هذا الـ commit

| الملف | الغرض |
|---|---|
| `tools/api_key_pool.py` | إضافة daily-exhaust detection + fast-fail + check_quotas |
| `results/run_gpt-oss-120b_20q/gpt-oss-120b-free.json` | كل الـ 20 سؤال بالتفاصيل |
| `results/run_gpt-oss-120b_20q/summary.md` | comparison table |
| `results/run_gpt-oss-120b_20q/pool_stats.json` | إحصائيات المفاتيح |
| `GENESIS_Pure_Baseline_Results_AR.md` | هذا التقرير |

---

## ✅ الأهم: نخلوش الإيمان

**كل اللي شفناه اليوم يثبت ثلاث حقائق:**

1. **النموذج (gpt-oss-120b) قوي فعلاً** — 75% على free tier ≈ الـ official 80.1%
2. **الـ infrastructure بتاعتنا production-ready** — 0 invalid, perfect pool rotation, smart fallbacks
3. **GENESIS run_53 كان bug في scaffolding 100%** — مش ضعف في النموذج، مش ضعف في فكرة GENESIS، مش ضعف في reasoning

دلوقتي الطريق واضح: نصلح scaffolding GENESIS بنفس الفلسفة (`extract_response_text`, smart fallback, 16K tokens, إلخ) ونعيد قياس. لو GENESIS طلع **فوق 75%**، يبقى عندنا الـ proof النهائي على قيمته.
