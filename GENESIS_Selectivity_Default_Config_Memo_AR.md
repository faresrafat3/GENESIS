# Virtual-GENESIS Selectivity Default Config Memo (Arabic)

## الغرض
تثبيت نتيجة عملية من جولة الـ selectivity ablations داخل الكود نفسه بدل تركها implicit أو مرتبطة بتجربة واحدة.

## ما الذي تقرر حتى الآن؟
بناءً على الـ micro-ablations السابقة، أفضل وضع افتراضي تجريبي حاليًا هو:
- `max_active_concepts = 1`
- `min_activation_score = 7`

### لماذا؟
لأن هذا الإعداد:
1. خفّض concept activation مقارنة بالوضع الأرخى
2. حافظ على gains الأساسية داخل `prototype_v3b_curriculum`
3. لم يُظهر أن second concept تضيف عائدًا واضحًا في الشريحة الحالية

## ما الذي تغير في التنفيذ؟
- أُضيف ملف config صريح داخل:
  - `virtual_genesis/runtime/concept_engine/config.py`
- Concept Engine الآن تقرأ قيمها الافتراضية من config بدل الاعتماد على defaults صامتة أو monkeypatching مباشر

## الفائدة
1. selectivity policy أصبحت object/configuration-level concern
2. أسهل في التتبع والتعديل لاحقًا
3. فصل بين:
   - current default operating regime
   - وبين ablation overrides التجريبية

## التنبيه المهم
هذا ليس “قرارًا نهائيًا” للمشروع كله.
بل:
- **أفضل default مؤقتة**
- حتى تظهر evidence جديدة على slices أو curricula أصعب

## القرار التالي
لا نغيّر هذه default الآن إلا إذا:
- ظهرت slice جديدة أكثر تمييزًا
- أو أثبتت ablations family-specific أن comparison/synthesis/procedure تحتاج policies مختلفة

وهذا يرفع نضج Thesis 1 من مجرد observations إلى stateful, configurable mechanism.
