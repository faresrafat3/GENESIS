# السرقات الشرعية - Real World Upgrades

## 5.65 من CheckList (Ribeiro et al. 2020, ACL Best Paper)
### ما الذي أخذناه؟
Minimum Functionality Tests + Invariance Tests: مفهوم اختبار ما اذا كان تغيير العقد يغير النتيجة
### ما الذي لم نأخذه الآن؟
Full behavioral testing suite generation
### ماذا أصبح عندنا؟
property_removal operator - اختبار ان ازالة خاصية مطلوبة تجعل التحقق ينجح

## 5.66 من Contrast Sets (Gardner et al. 2020, EMNLP)
### ما الذي أخذناه؟
Minimal edits to build closest failure point: تغيير خاصية واحدة في العقد يجب ان يغير نتيجة التحقق
### ما الذي لم نأخذه الآن؟
Crowdsourced contrast set generation
### ماذا أصبح عندنا؟
property_addition + shortcut_injection - اضافة قيد واحد يكسر النجاح

## 5.67 من Counterfactually-Augmented Data (Kaushik et al. 2020, ICLR)
### ما الذي أخذناه؟
Same text, reversed label: نفس المهمة لكن العقد مقلوب
### ما الذي لم نأخذه الآن؟
Human-in-the-loop counterfactual generation
### ماذا أصبح عندنا؟
contract_flip + counterfactual_contract - قلب معايير النجاح

## 5.68 من Dynabench (Kiela et al. 2021, NAACL)
### ما الذي أخذناه؟
Dynamic adversarial benchmark: النظام يولد مهام يفشل فيها
### ما الذي لم نأخذه الآن؟
Human adversary in the loop
### ماذا أصبح عندنا؟
contract_tightening_strict - تشديد ديناميكي يكشف نقاط الضعف

## 5.69 من Mem0 (2024) "Building Production-Ready AI Memory"
### ما الذي أخذناه؟
Memory CRUD lifecycle مع versioning: دورة حياة الذاكرة (اضافة/تحديث/بحث/حذف) مع metadata versioning
### ما الذي لم نأخذه الآن؟
Graph relations بين الذكريات والبحث الدلالي
### ماذا أصبح عندنا؟
SQLiteMemoryStore مع CRUD كامل وحالات (active/archived/deprecated/deleted)

## 5.70 من MemGPT / Letta (Packer et al. 2023)
### ما الذي أخذناه؟
Memory as OS with paging/hierarchy: تسلسل الذاكرة الساخنة/الدافئة/الباردة
### ما الذي لم نأخذه الآن؟
Context window management والـ paging الفعلي
### ماذا أصبح عندنا؟
decay_score + memory_status hierarchy يحاكي hot/warm/cold

## 5.71 من LangGraph Persistence (LangChain 2024)
### ما الذي أخذناه؟
State checkpointing for agent resumability: حفظ/استعادة حالة pipeline كاملة كـ atomic checkpoint
### ما الذي لم نأخذه الآن؟
Branching والـ time travel debugging
### ماذا أصبح عندنا؟
checkpoint.py مع save_checkpoint/load_checkpoint لاستمرارية الجلسات

## 5.72 من SQLite WAL mode + JSON1 extension
### ما الذي أخذناه؟
Zero-dependency, single-file, ACID-compliant storage مع JSON columns
### ما الذي لم نأخذه الآن؟
Full-text search عبر JSON fields
### ماذا أصبح عندنا؟
sqlite3 stdlib مع WAL mode وJSON columns لمرونة schema

## 5.73 من SWE-bench (Jimenez et al. 2024)
### ما الذي أخذناه؟
Real-task evaluation methodology: منهجية التقييم على مهام حقيقية مع مقارنة A/B على نفس المهام
### ما الذي لم نأخذه الآن؟
Full repository-level evaluation
### ماذا أصبح عندنا؟
run_real_llm_eval.py مع 3 conditions على نفس المهام (raw vs concept vs full)

## 5.74 من LATS - Language Agent Tree Search (Zhou et al. 2024)
### ما الذي أخذناه؟
Comparing reasoning strategies with real LLM: البروتوكول التجريبي لتشغيل نفس prompts عبر configurations مختلفة
### ما الذي لم نأخذه الآن؟
Tree search وMonte Carlo sampling
### ماذا أصبح عندنا؟
3 conditions (A/B/C) تقيس تاثير كل طبقة (concepts, theories) بشكل مستقل

## 5.75 من DSPy (Khattab et al. 2024)
### ما الذي أخذناه؟
Metric-driven prompt optimization: استخدام مقاييس التقييم لقياس هل concept hints تحسن جودة الـ LLM output
### ما الذي لم نأخذه الآن؟
Automatic prompt compilation والـ optimization loop
### ماذا أصبح عندنا؟
concept_lift و theory_lift metrics تقيس التحسن الفعلي من كل طبقة
