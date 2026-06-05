# ⚡ دليل التشغيل السريع — GPQA 20 سؤال

ده المسار العملي السريع بدل تشغيل 198 سؤال على free tier.

## لماذا؟

- الـ 198 سؤال بتاخد وقت طويل جداً على النماذج المجانية
- إحنا أصلاً بنقارن مع **pure baseline = 75% على نفس 20 سؤال**
- فالأصح علمياً في مرحلة الـ debugging والتأكد من الـ scaffolding:
  - **GENESIS على نفس subset**
  - وبعدها فقط نطلع للـ 198

## الـ task السريع

تم إنشاء task خارجي هنا:

```bash
tasks/gpqa_subset_20
```

ويحتوي على:

- `data/public/diamond_questions.json` — أول 20 سؤال
- `data/private/diamond_questions.json` — نفس الـ 20 للتقييم
- `data/public/evaluate.py`
- `data/public/task.md`
- `reference/` files

## تشغيل سريع

### 1) baseline / GENESIS comparison

```bash
cd ~/GENESIS
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
export OPENAI_API_KEY="<your_openrouter_key>"

# مهم: شغّل من داخل .venv لو موجود
# source .venv/bin/activate

python run_openrouter_benchmark.py \
  --task_dir tasks/gpqa_subset_20 \
  --max_gen 2 \
  --run_id 56 \
  --use_evolutionary_discovery \
  --meta_model openai/gpt-oss-120b:free \
  --task_model openai/gpt-oss-120b:free
```

> ملاحظة: `run_openrouter_benchmark.py` دلوقتي **يفضّل تلقائياً** `./.venv/bin/python` لو موجود، عشان يتفادى مشكلة `ModuleNotFoundError: openai` في بعض البيئات.

## ماذا نقيس؟

نفس السؤال المركزي:

- **pure baseline على نفس subset = 75.00%**
- لو GENESIS بعد الإصلاحات يطلع:
  - `> 75%` → architecture adds value
  - `≈ 75%` → neutral
  - `< 75%` → لسه فيه bugs أو overhead ضار

## لماذا `--task_dir` مهم؟

لأن `genesis.orchestrator` يدعم external task directories، وده بيخلينا:

- نعمل subsets
- نعمل quick experiments
- نتحكم في حجم benchmark بدون ما نكسر الـ bundled task

## ملاحظات

- ده **للـ fast iteration فقط**
- أي claim قوي لازم يرجع يتأكد على full 198 questions بعدين
- لكن دلوقتي ده هو المسار الصح عشان ما نضيعش وقت ولا quota
