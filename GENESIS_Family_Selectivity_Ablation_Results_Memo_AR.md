# Virtual-GENESIS Family Selectivity Ablation Results Memo (Updated)

## الغرض
توثيق نتائج أول ablations family-specific selectivity على `prototype_v3b_curriculum` بعد تثبيت defaults الحالية واختبار ما إذا كانت بعض العائلات تحتاج concepts أكثر أو أقل.

## الإعدادات المختبرة
1. `current_default`
   - comparison: top1 / score7
   - synthesis: top1 / score7
   - procedure: top0
2. `synthesis_top2`
   - synthesis top2 / score7
3. `procedure_top1`
   - procedure top1 / score7
4. `synthesis_top2_procedure_top1`
   - synthesis top2 / score7
   - procedure top1 / score7

---

## النتيجة الأساسية
### أهم ملاحظة
- تغيير `synthesis` من top1 إلى top2 **لم يغير النتائج** في هذه الشريحة.
- فتح `procedure` من top0 إلى top1 **رفع concept activation** لكنه **لم يرفع success**، بل زاد cost قليلًا.

### بالأرقام المختصرة
#### current_default
- concept_success = **0.875**
- concept_activation_rate = **0.6528**
- combined_avg_cost ≈ **0.00168**

#### synthesis_top2
- نفس النتائج تقريبًا كما هي

#### procedure_top1
- concept_activation_rate ارتفعت إلى **0.7083**
- success بقيت **0.875**
- cost زادت قليلًا

#### synthesis_top2_procedure_top1
- same pattern as procedure_top1

---

## القراءة
### 1. synthesis لا تحتاج second concept في الشريحة الحالية
هذا أهم استنتاج مباشر.

إذن:
- top2 for synthesis غير مبررة حاليًا
- الأقل كلفة والأكثر أناقة يبقى top1

### 2. procedure لا تستفيد حاليًا من concepts بالقدر الذي يبرر تفعيلها
عندما سمحنا بمفهوم واحد في procedure:
- activation ارتفعت
- performance لم تتحسن
- cost زادت قليلًا

إذن:
- procedure top0 default يبدو ما زال الأفضل حاليًا

### 3. current_default ما زالت أفضل policy إجمالية مؤقتًا
لأن:
- selectivity أدنى من permissive settings
- performance نفسها
- cost أقل أو مساوية

---

## الحكم الحالي
### Family-specific selectivity conclusion
أفضل default حالية تبقى:
- comparison: top1 / score7
- synthesis: top1 / score7
- procedure: top0

أي أن hypothesis القائلة إن synthesis قد تحتاج second concept **لم تتأكد** في الشريحة الحالية.
كما أن procedure concept activation تبدو حتى الآن **غير مبررة اقتصاديًا**.

---

## ماذا يعني هذا استراتيجيًا؟
1. current default ليست arbitrary anymore؛ أصبحت مدعومة بmicro-evidence
2. لا داعي الآن لتوسيع Concept policy family-wise أكثر قبل ظهور slices أو curricula أصعب
3. bottleneck التالية لم تعد selectivity by family، بل يمكن أن تنتقل إلى:
   - richer perturbations
   - stronger concept semantics
   - أو eventual contradiction/anomaly integration

---

## القرار النهائي
### ما نعتمده مؤقتًا
- comparison: top1 / score7
- synthesis: top1 / score7
- procedure: top0

### ما نوقفه الآن
- لا نفعّل top2 synthesis افتراضيًا
- لا نفعّل concepts في procedure افتراضيًا

### ما الخطوة التالية
بما أن family-specific tuning لم تكشف gains إضافية واضحة، فيمكن الآن:
- تثبيت هذه defaults
- والعودة للتركيز على perturbation difficulty أو future governance layers

وهذا يرفع نضج Thesis 1 من:
- concept usefulness
إلى:
- **concept policy with empirically defended defaults**
