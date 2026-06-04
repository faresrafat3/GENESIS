# 🔧 البنية متعددة النماذج — Multi-Model Infrastructure

**التاريخ:** 2026-06-04
**الإصدار:** 1.0
**الغرض:** تشغيل GENESIS وtests مستقلة على عدة نماذج بالتوازي مع تدوير ذكي لـ 11 مفتاح OpenRouter free.

---

## 🧩 المكونات الثلاثة

### 1. `tools/api_key_pool.py` — Smart Key Rotator

كلاس Python بيدير مجموعة مفاتيح:
- **يدور تلقائياً** بين المفاتيح (round-robin)
- **يكتشف rate-limit / 429 / quota errors** وينقل للمفتاح التالي
- **يعزل المفاتيح الميتة** (401/403) ولا يحاول معاها تاني
- **يحفظ إحصائيات استخدام** لكل مفتاح في `logs/api_key_pool_stats.json`
- **Persistent stats** — تكمل من حيث وقفت بين الـ runs

**الأمان:**
- لا يوجد مفتاح واحد مكتوب في الكود
- يقرأ من 3 مصادر بالترتيب:
  1. Environment variables (`OPENROUTER_API_KEY_<NAME>`)
  2. ملف `.env` المحلي (في `.gitignore`)
  3. ملف `.keys.json` أو أي ملف تختاره (لو موجود)

### 2. `tools/model_registry.py` — Curated Catalog

سجل لكل النماذج الـ 13 المتاحة على OpenRouter:
- **shortcut**: اسم قصير للاستخدام في الـ CLI
- **openrouter_id**: الـ ID الكامل
- **benchmarks**: أرقام رسمية من vendor cards (مرجعية)
- **sources**: روابط للمراجع الرسمية

النماذج الـ 13:

| Shortcut | Family | Context | Best Bench (Official) |
|---|---|---|---|
| `gemma-4-31b-free` | Google Gemma 4 31B | 262K | **GPQA 84.3% 🥇** |
| `gemma-4-26b-free` | Google Gemma 4 MoE | 262K | GPQA 82.3% |
| `gpt-oss-120b-free` | OpenAI gpt-oss | 131K | GPQA 80.1% |
| `nemotron-3-super-free` | NVIDIA Nemotron 3 Super | 1M | GPQA 79.2% |
| `nemotron-3-ultra-free` | NVIDIA Nemotron 3 Ultra | 1M | **PinchBench 91% 🥇** |
| `nemotron-3-nano-free` | NVIDIA Nemotron 3 Nano | 1M | RULER 87.5% @64K |
| `nemotron-3-nano-omni-free` | Nemotron Nano Omni (multimodal) | 256K | — |
| `nemotron-nano-9b-v2-free` | Nemotron Nano 9B v2 | 128K | — |
| `laguna-m1-free` | Poolside Laguna M.1 | 131K | **SWE 72.5% 🥇** |
| `laguna-xs2-free` | Poolside Laguna XS.2 | 131K | SWE 68.2% |
| `qwen3-coder-free` | Qwen3 Coder | 1M | SWE ~73% |
| `glm-4.5-air-free` | Z.AI GLM-4.5-Air | 131K | **Tool Selection 94% 🥇** |
| `lfm-2.5-thinking-free` | Liquid LFM 2.5 (1.2B) | 32K | GPQA 37.9% (لكن سريع جداً) |

### 3. `tools/run_multi_model_benchmark.py` — Multi-Model Runner

يشغل أي عدد من النماذج على نفس الـ task (حالياً GPQA) ويعمل comparison:
- **يستخدم الـ pool** تلقائياً مع key rotation
- **يحفظ نتائج كل نموذج** في ملف منفصل
- **يولّد summary.md** فيه ranking مقارن بـ official benchmarks
- **يكتشف الـ gap** بين أداءنا والأرقام الرسمية → مؤشر مباشر على bugs في scaffolding

---

## 🚀 الاستخدام السريع

### Setup أول مرة (مرة واحدة)

```bash
cd ~/GENESIS

# 1) انسخ القالب
cp .env.example .env

# 2) عدّل .env وضع المفاتيح الحقيقية (نفس الـ format)
nano .env
# سطر لكل مفتاح:
#   OPENROUTER_API_KEY_AHMED=sk-or-v1-...
#   OPENROUTER_API_KEY_FARESRAFAT433=sk-or-v1-...
#   إلخ.

# 3) قيد الصلاحيات على .env
chmod 600 .env

# 4) تحقق إن .env مش بيتراك من git
git check-ignore -v .env
# المفروض يطلع: .gitignore:6:.env    .env
```

### تأكيد إن المفاتيح شغالة

```bash
# يقرأ كل المفاتيح ويعمل call صغير لاختبار واحد
python tools/api_key_pool.py --test_call
```

**ناتج متوقع:**
```
✓ APIKeyPool ready with 11 keys: ['ahmed', 'faresrafatfares', ...]
=== APIKeyPool Summary ===
Total: 11 | Available: 11 | Dead: 0
  [✓] ahmed              req=0    ok=0    fail=0   rate=  0.0%
  ...
Testing first key with a tiny call...
  attempt 1 key=ahmed status=trying
  attempt 1 key=ahmed status=success
  ✓ Response: 'OK'
```

### استكشاف الـ Registry

```bash
# قائمة كل النماذج
python tools/model_registry.py --list

# أحسن نماذج لكل task
python tools/model_registry.py --for_task gpqa
python tools/model_registry.py --for_task coding
python tools/model_registry.py --for_task agent

# ترتيب بـ benchmark معين
python tools/model_registry.py --bench gpqa_diamond
```

### تشغيل المقارنة (الاستخدام الأساسي!)

```bash
# 🧪 Smoke test سريع: 3 نماذج × 20 سؤال (~5-10 دقايق)
python tools/run_multi_model_benchmark.py \
    --task gpqa \
    --models smoke \
    --limit 20 \
    --output_dir results/smoke_test

# 🎯 الأهم: أحسن 5 نماذج لـ GPQA على 20 سؤال
python tools/run_multi_model_benchmark.py \
    --task gpqa \
    --models top_for_gpqa \
    --limit 20 \
    --output_dir results/gpqa_top5_smoke

# 💯 كل النماذج × كل الـ 198 سؤال (هياخد ساعات بس هيدينا picture كاملة)
python tools/run_multi_model_benchmark.py \
    --task gpqa \
    --models all \
    --limit 0 \
    --output_dir results/full_comparison

# 🔬 نموذج محدد، تحكم كامل
python tools/run_multi_model_benchmark.py \
    --task gpqa \
    --models nemotron-3-ultra-free,gemma-4-31b-free,gpt-oss-120b-free \
    --limit 50 \
    --reasoning high \
    --max_tokens 8192 \
    --output_dir results/top3_50q
```

### قراءة النتائج

```bash
# Markdown summary بالتفاصيل
cat results/<output_dir>/summary.md

# JSON ratio detailed
cat results/<output_dir>/summary.json | python3 -m json.tool

# Pool stats — استخدام كل مفتاح
cat results/<output_dir>/pool_stats.json | python3 -m json.tool
```

---

## 🧠 الذكاء في الـ Pool

### Rate Limit Handling
لما مفتاح يرجع `429` أو `quota exceeded`:
1. يُعزل لمدة `rate_limit_cooldown` (default 60 ثانية)
2. الـ pool ينقل **فوراً** للمفتاح التالي بدون فقدان السؤال
3. بعد الـ cooldown، المفتاح يرجع للـ rotation

### Permanent Failure Handling
لما مفتاح يرجع `401` / `403` / `invalid_api_key`:
1. يتعزل **نهائياً** للـ session كله
2. الـ pool يكمل بالباقي
3. بيتطبع warning واضح: `❌ Key X marked DEAD`

### Round-Robin مع Fairness
الـ pool بيستخدم الـ cursor بشكل دوار، يعني لو عندك 11 مفتاح وعملت 100 طلب:
- كل مفتاح بياخد ~9 طلب تقريباً
- لو واحد فيهم بطيء أو في cooldown، الباقي بياخد عبئه

### Smart Waiting
لو **كل** المفاتيح في cooldown، الـ pool بيختار الأقدم منهم (الأقرب لانتهاء cooldown) وينتظر الفرق فقط، مش 60 ثانية كاملة.

---

## 🔒 الأمان (مراجعة قبل أي push)

قبل أي `git push`، اعمل الفحص ده:

```bash
# 1) تأكد إن .env مش staged
git status .env

# 2) فحص الـ commits المحلية ما فيهاش keys
git diff main..HEAD | grep -E "sk-or-v1-|sk-proj-" && echo "⛔ KEYS FOUND!" || echo "✓ Clean"

# 3) فحص كل التغييرات قبل الـ push
git diff --staged | grep -E "sk-or-v1-|sk-proj-" && echo "⛔ STAGED KEYS!" || echo "✓ Safe to push"
```

لو طلع أي شيء من النقطتين 2 أو 3، **أوقف الـ push فوراً** واعمل:
```bash
git reset --soft HEAD~1   # أو عدد الـ commits المحدد
# امسح المفاتيح من الملفات
# commit نظيف
```

ولو فعلاً push كده بالغلط:
```bash
# 1) ادخل https://openrouter.ai/settings/keys واعمل revoke لكل مفتاح طلع
# 2) جدد المفاتيح
# 3) عدّل .env المحلي
```

---

## 📊 إيه الفايدة دلوقتي؟

### قبل الـ infrastructure دي
- مفتاح واحد بس
- Free tier rate limits توقفك بعد دقايق
- بتقدر تختبر نموذج واحد فقط في كل run
- مفيش طريقة لمقارنة النماذج

### بعدها
- **11 مفتاح بالتوازي** = ~11x rate limit headroom
- **13 نموذج جاهز للاختبار** بـ shortcut واحد
- **comparison table تلقائي** بـ official vs measured benchmarks
- **detect bugs in scaffolding** — لو الـ gap كبير بين أداءنا والأرقام الرسمية، نعرف فيه مشكلة (زي bug run_53)

---

## 🎯 الاستخدام في الخطة الجاية للمشروع

### الخطوة 1: Pure Baseline Comparison (الـ benchmark الحقيقي بدون GENESIS)
```bash
python tools/run_multi_model_benchmark.py \
    --task gpqa \
    --models top_for_gpqa \
    --limit 50 \
    --output_dir results/baseline_top5_50q
```
ده هيدينا **السقف الحقيقي** لكل نموذج لوحده.

### الخطوة 2: GENESIS Comparison (نفس النماذج مع GENESIS)
```bash
# لكل نموذج
for model in nemotron-3-ultra-free gpt-oss-120b-free gemma-4-31b-free; do
    python run_openrouter_benchmark.py \
        --task gpqa \
        --max_gen 2 \
        --run_id $((100 + RANDOM % 1000)) \
        --use_evolutionary_discovery \
        --meta_model $model \
        --task_model $model
done
```

### الخطوة 3: تحليل
- لو **GENESIS > pure baseline** → دليل على القيمة المضافة للبنية
- لو **GENESIS < pure baseline** → فيه bugs في scaffolding (زي اللي شفناه run_53)
- لو **GENESIS ≈ baseline** → البنية ما بتأثرش، نشتغل على الـ pipeline integration

---

## ✅ ما تم في commit ده

| الملف | الغرض | حساس؟ |
|---|---|---|
| `tools/api_key_pool.py` | Key rotation engine | لا |
| `tools/model_registry.py` | Model catalog (13 models) | لا |
| `tools/run_multi_model_benchmark.py` | Multi-model runner | لا |
| `.env.example` | قالب فاضي للمفاتيح | لا |
| `scripts/setup_keys_local.sh.example` | قالب لإعداد محلي سريع | لا |
| `.gitignore` (تحديث) | حماية `.env` + `scripts/setup_keys_local.sh` | — |
| `GENESIS_Multi_Model_Infrastructure_AR.md` | التوثيق الكامل (هذا الملف) | لا |

**لا يوجد أي مفتاح حقيقي في أي ملف.** المفاتيح كلها يجب أن تكون فقط في `.env` المحلي.
