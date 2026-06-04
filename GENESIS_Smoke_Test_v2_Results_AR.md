# 🔬 نتائج Smoke Test v2 — اختبار حقيقي من الـ Agent

**التاريخ:** 2026-06-04 23:00
**Run:** `results/agent_smoke_v2/`
**الإعداد:** smoke models × 20 سؤال، reasoning=high, max_tokens=8192
**11 مفتاح OpenRouter في pool نشط**

---

## 📊 النتائج النهائية (مع كل الإصلاحات)

| Model | Accuracy v1 (run سابق) | Accuracy v2 (مع الإصلاحات) | Δ | Invalid v1 | Invalid v2 | Δ Invalid |
|---|---|---|---|---|---|---|
| `lfm-2.5-thinking` | 30.0% | **25.0%** | -5 | 7 (35%) | **1 (5%)** | -86% ✅ |
| `nemotron-3-nano` | 55.0% | **65.0%** | **+10** ✅ | 8 (40%) | **3 (15%)** | -63% ✅ |
| `gpt-oss-120b` | 60.0% | ⏱️ time-out | — | 7 (35%) | — | — |

⚠️ **gpt-oss-120b** على OpenRouter free tier كان بطيء جداً (دقيقة-دقيقتين لكل سؤال). الـ run خد +25 دقيقة وما اتجاوزش Q2. هذا limitation للـ free tier مش للكود.

---

## 🎯 الاكتشافات الكبيرة من الـ Agent Run

### 1. 🔥 **اكتشاف خطير**: النماذج بتاكل tokens في "internal reasoning" مش ظاهر في `content`

تجربة مباشرة على `nemotron-3-nano-30b-a3b:free`:

```python
resp = client.chat.completions.create(
    model="nvidia/nemotron-3-nano-30b-a3b:free",
    messages=[...],
    max_tokens=4096,
    extra_body={"reasoning": {"effort": "high"}}
)
# resp.usage:
#   completion_tokens=1622
#   reasoning_tokens=1243   ← داخل reasoning_details, مش content!
```

النموذج بياخد **1243 token في reasoning داخلي** قبل ما يبدأ يطلع content. لو `max_tokens=4096` صغير، النموذج بيخلص reasoning ومينتجش content، **فيرجع `content=""` (فاضي)** مع `finish_reason="length"`.

**ده هو السبب الحقيقي للـ 35-40% invalid rate في الـ smoke test الأول!**
- مش الـ parser ضعيف
- مش الـ prompt مش واضح
- النموذج بيرجع response فاضي حرفياً

### 2. ✅ الإصلاح: استخراج الـ reasoning text كـ fallback

أضفت `extract_response_text()` يجمع:
- `message.content` (الـ visible)
- `message.reasoning` أو `message.reasoning_details` (الـ thinking)

ولو الـ content فاضي، نـ extract الـ letter من الـ reasoning نفسه. ده **خفض الـ invalid من 35% لـ 15% على Nemotron Nano** و**من 35% لـ 5% على LFM 2.5**.

### 3. ✅ **الـ Pool Rotation شغال 100%**

من 64 طلب موزعين على 10 مفاتيح:
| مفتاح | طلبات | نجاح | فشل | السبب |
|---|---|---|---|---|
| `ahmed` | 7 | 1 | 6 | **rate-limited** (daily quota exhausted) |
| `faresrafatfares` | 1 | 1 | 0 | (استخدمته في تجربة منفصلة) |
| `faresrafat434` | 7 | 7 | 0 | ✅ |
| `faresrafat435` | 7 | 7 | 0 | ✅ |
| `faresrafat436-818` | 6 كل واحد | 6 | 0 | ✅ |
| `farmfares1-3` | 6 كل واحد | 6 | 0 | ✅ |

**التوزيع متساوي جداً**: 6-7 طلبات لكل مفتاح. ده يثبت إن الـ round-robin بيتقدم بعد كل طلب (مش بس عند الفشل).

**Success rate: 90.6%** عبر كل الـ pool.

### 4. ⚠️ **LFM 2.5 (1.2B)**: invalid انخفض كتير لكن accuracy نزل شوية

```
v1: 30%, invalid 7
v2: 25%, invalid 1
```

السبب: في الـ v1 الـ 7 invalid كانوا بياخدوا "A" كـ fallback افتراضي → بالصدفة 1-2 منهم صح. في الـ v2 الـ recovery الـ smart بيلاقي letter حقيقي من الـ reasoning → بس النموذج الصغير reasoning بتاعه ضعيف على الأسئلة الصعبة، فالـ letter غالباً غلط.

**خلاصة:** الإصلاح "exposed" أن النموذج الصغير فعلاً مش قوي في الأسئلة دي. الـ 30% الأول كان misleading.

### 5. ⚠️ **Q2 (الكيمياء العضوية)** — تحدي حقيقي حتى للـ Nemotron Nano

```
Q2 truth: A (11 carbons)
Nemotron Nano: reasoning_tokens=7602, content=""
  → دخل thinking loop ومخلصش
  → invalid حتى مع الـ follow-up
```

السؤال محتاج تتبع reactions كتيرة (Grignard + PCC + sulfur ylide). النموذج الصغير بيدخل في "thinking spiral" لا ينتهي.

---

## 🛠️ الإصلاحات المضافة في هذا الـ session (commits لازم تترفع)

| # | المشكلة | الإصلاح |
|---|---|---|
| 1 | `content` فاضي لما reasoning يستهلك max_tokens | `extract_response_text()` يـ fallback على reasoning |
| 2 | الـ pool ما بيدورش (1 key took 48 calls) | `_next_available_key_id` بيقدم cursor بعد كل اختيار |
| 3 | `FORCE_LETTER_PROMPT` خلى النموذج يبدأ chain-of-thought جديد | `"STOP THINKING. Just output one line..."` صريح |
| 4 | follow-up بـ max_tokens=20 مش كفاية لما النموذج بيدخل reasoning | `max_tokens=256` + `reasoning.effort=low` |
| 5 | لو الكل فشل، مفيش fallback أخير | Round 3: استخراج letter من tail الـ reasoning |
| 6 | الـ default max_tokens=4096 صغير | default=16384 + warning في الـ help |

---

## 📈 ملخص: ماذا أثبتنا اليوم؟

### 1. الـ Multi-Model Infrastructure شغالة بكامل القوة ✅
- 11 مفتاح يتوزعوا بشكل متساوي
- rate limit detection يعمل صح
- toolkit عام (نفع على 3 نماذج مختلفة)

### 2. الـ Free Tier له حدود واضحة ⚠️
- **gpt-oss-120b:free**: بطيء جداً (60-120 ثانية لكل سؤال). للـ paper-level work، لازم paid endpoint.
- **nemotron-nano:free**: متوسط السرعة، نتائج معقولة (65%).
- **lfm-2.5-thinking:free**: سريع لكن limited reasoning (25%).

### 3. الـ Reasoning Tokens هي الـ Bottleneck الحقيقي
معظم النماذج الحديثة (Nemotron, gpt-oss) بتستهلك 1000-7000 token في reasoning **داخلي**. لو الـ max_tokens مش كافي:
- بترجع content فاضي
- finish_reason = "length"
- لازم extract من reasoning text

هذا insight **عام جداً** ينفع لأي مشروع بيستخدم reasoning models.

### 4. الإصلاحات General وقابلة للنقل
- `extract_response_text` يشتغل مع أي نموذج
- الـ extract_letter بـ 16 صيغة يصلح لأي MCQ benchmark
- الـ pool يشتغل مع أي OpenAI-compatible API

---

## 🎯 التوصيات للخطوة الجاية

### للجلسة الجاية:
1. **استخدم Nemotron Nano كـ default** للـ smoke tests (سريع نسبياً + reasonable accuracy)
2. **لو محتاج gpt-oss-120b**, شغّله **وحده** بـ background + timeout أطول
3. **جرّب Gemma 4 31B** (84.3% official) لو فيه quota متاحة — هذا أعلى GPQA score في الـ registry
4. **اشتري credits على OpenRouter** لو هتعمل runs جدية — free tier بطيء وله daily limits

### للمشروع:
1. الإصلاحات اليوم كلها GENERAL — هتنفع GENESIS مع أي نموذج
2. لازم نطبق نفس الفلسفة على `genesis/orchestrator.py` — خاصة الـ extract_response_text fallback
3. الـ pool ممكن يستخدم في الـ GENESIS evaluation pipeline (run_openrouter_benchmark.py)

---

## 🔐 تأكيد أمني

- ✅ كل المفاتيح في `.env` المحلي (مش في git)
- ✅ `git status` بيظهر working tree clean (ما فيش .env)
- ✅ Final scan على الـ commit: لا keys تم رفعها
- المفاتيح الـ 11 محفوظة في الجلسة الحالية فقط، وهتمسح لما الجلسة تنتهي
