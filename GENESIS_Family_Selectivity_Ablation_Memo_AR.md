# Virtual-GENESIS Family Selectivity Ablation Memo (Arabic)

## الغرض
تلخيص أول ablation موجّهة لسؤال واحد:

> هل نحتاج سياسات انتقائية مختلفة للمفاهيم حسب family، خصوصًا synthesis وprocedure؟

## الإعدادات المقارنة
1. `current_default`
   - comparison: top1 / score7
   - synthesis: top1 / score7
   - procedure: top0
2. `synthesis_top2`
   - السماح بمفهومين في synthesis
3. `procedure_top1`
   - السماح بمفهوم واحد في procedure
4. `synthesis_top2_procedure_top1`
   - فتح policy أكثر permissive للعائلتين معًا

## القراءة المبدئية المتوقعة
هذه الـ ablation لا تهدف إلى إثبات thesis جديدة، بل إلى فحص:
- هل current default ربما متشددة على بعض العائلات؟
- أم أن التخفيف يزيد activation دون عائد؟

## ما الذي سنبحث عنه؟
1. هل يرتفع concept success أو combined success بشكل meaningful؟
2. هل يرتفع activation كثيرًا بلا كسب مناسب؟
3. هل procedure تستفيد أصلًا من concepts؟
4. هل synthesis تحتاج second concept فعلاً؟

## حكم النجاح المتوقع
- إذا تحسن synthesis materially عند top2 بدون cost/selectivity explosion → support family-specific policy
- إذا procedure top1 لا تضيف شيئًا أو ترفع activation فقط → نبقي top0

## ملاحظة
هذه المذكرة تُستكمل بالنتائج الفعلية من runner الجديدة، وهي تهدف الآن إلى تثبيت نية التجربة والمنطق التفسيري لها.
