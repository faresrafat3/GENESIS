# Virtual-GENESIS Cognitive Economy Theory (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تحاول الإجابة عن سؤال جوهري:

> إذا كان agent يمتلك عدة طرق للتفكير، وعدة طبقات ذاكرة، وعدة درجات نماذج، وعدة أساليب تحقق،
> فكيف يوزع موارده الإدراكية بحيث يفكر “بقدر ما يستحق الأمر” وليس أكثر أو أقل؟

هذه هي الوثيقة الخامسة في البرنامج النظري بعد:
1. Concept Formation Theory
2. Productive Forgetting Theory
3. Anomaly, Crisis, and Paradigm Theory
4. Contradiction Theory

---

## 1) لماذا الاقتصاد الإدراكي مشكلة مركزية؟
الأنظمة القائمة على LLM APIs تواجه دائمًا سؤالًا ضمنيًا:
- هل أجيب الآن؟
- هل أبحث أكثر؟
- هل أسترجع ذاكرة إضافية؟
- هل أستخدم موديل أقوى؟
- هل أفتح committee؟
- هل أبني abstraction بدل أن أخرج answer سريع؟
- هل أستثمر في benchmark جديد أو skill جديدة بدل حل المسألة الحالية فقط؟

إذا لم يكن لدى النظام منطق واضح لتوزيع هذه الموارد، فسيقع في أحد ثلاثة أنماط:

### النمط 1 — Cognitive Overspending
تفكير زائد، استدعاءات كثيرة، escalation متكرر، كلفة مرتفعة دون عائد متناسب.

### النمط 2 — Cognitive Underspending
إجابات سريعة ورخيصة لكن هشة وغير مستقرة.

### النمط 3 — Misallocation
يصرف cognition على الجزء الخطأ:
- search بدل retrieval
- premium model بدل verifier
- committee بدل concept formation
- memory expansion بدل contradiction resolution

---

## 2) الملاحظة الأساسية
الذكاء ليس فقط جودة الاستدلال، بل **كيفية تخصيص الاستدلال**.

بالتالي:

> agent ذكي = agent يوزع موارده الإدراكية عقلانيًا تحت القيود.

هذا يربطنا بثلاثة خطوط فكرية مهمة:
- **bounded optimality**: الذكاء يجب أن يُفهم تحت القيود الواقعية للعمارة والبيئة [3](https://arxiv.org/abs/cs/9505103).
- **rational metareasoning**: التفكير في كيف نفكر، من خلال قيمة الحساب/الاستدلال نفسها [3](https://arxiv.org/html/2410.05563v1).
- **resource-rational analysis**: ما يبدو irrational قد يكون optimal under cognitive costs [1](https://www.sciencedirect.com/science/article/abs/pii/S2352154621000371) [2](https://cocosci.princeton.edu/papers/lieder_resource.pdf).

---

## 3) التعريف المركزي
### Cognitive Economy
نعرّف **الاقتصاد الإدراكي** بأنه:

> نظام المبادئ والآليات التي تنظم كيف يخصص agent موارده المحدودة من وقت، tokens، attention، memory bandwidth، verifier effort، model tier، وsearch depth، لتحقيق أعلى منفعة متوقعة عبر المهمة الحالية والمهمات المستقبلية.

لاحظ أن التعريف لا يتكلم فقط عن المهمة الحالية، بل أيضًا عن:
- reuse
- learning value
- future utility

---

## 4) ما هي “الموارد الإدراكية”؟
نقترح أن agent يمتلك على الأقل 8 أنواع من الموارد:

### 4.1 Time Budget
الزمن المتاح قبل أن تنخفض قيمة الإجابة أو تفشل المهمة.

### 4.2 Token Budget
حجم الإدخال/الإخراج/الـ reasoning الذي يمكن تحمله اقتصاديًا وتقنيًا.

### 4.3 Model-Tier Budget
كم مرة يجوز الصعود من cheap إلى premium.

### 4.4 Search Budget
عدد الفروع أو المسارات أو المرشحين المسموح بها.

### 4.5 Verification Budget
كم effort يمكن صرفه على checks/tests/judges.

### 4.6 Memory Bandwidth
كم من الذاكرة يمكن استرجاعه دون إدخال ضوضاء أو تضخم السياق.

### 4.7 Attention / Focus Budget
كم من جوانب المشكلة نحلل دفعة واحدة.

### 4.8 Improvement Budget
هل نستثمر compute في answer الآن، أم في lesson/skill/concept/benchmark للمستقبل؟

---

## 5) الفرضيات الأساسية للنظرية
### Hypothesis 1
الأنظمة الحالية تُهدر cognition أكثر مما تفتقدها.

### Hypothesis 2
جزء من “ذكاء” agent هو معرفة **متى لا تحتاج إلى مزيد من التفكير**.

### Hypothesis 3
أفضل قرار لحل مهمة حالية ليس دائمًا أفضل قرار لبناء ذكاء تراكمي طويل الأمد.

### Hypothesis 4
بعض الاستثمارات الإدراكية (مثل premium reasoning) تكون مجدية فقط إذا تحولت إلى artefacts قابلة لإعادة الاستخدام.

### Hypothesis 5
الـ cognitive allocation يجب أن يكون task-sensitive وuncertainty-sensitive وanomaly-sensitive.

---

## 6) من الاقتصاد الكلاسيكي إلى الاقتصاد الإدراكي
في الاقتصاد التقليدي نسأل:
- ما العائد؟
- ما التكلفة؟
- ما الخيار الأمثل؟

في الاقتصاد الإدراكي نسأل:
- ما العائد من المزيد من التفكير؟
- ما العائد من memory retrieval إضافي؟
- ما العائد من escalation إلى premium tier؟
- ما العائد من committee؟
- ما العائد من بناء concept أو skill جديدة؟

إذًا عندنا نسخة agentic من:
- Value of Computation
- Value of Information
- Value of Verification
- Value of Abstraction
- Value of Reuse

---

## 7) Rational Metareasoning كمصدر مباشر
الأعمال في rational metareasoning تصوغ المشكلة كالتالي:
- agent لديه belief state
- يمكنه القيام بحساب/استدلال إضافي
- هذا الحساب له **تكلفة** وله **قيمة متوقعة**
- والقيمة ترتبط بمدى تحسن القرار النهائي بسببه [3](https://arxiv.org/html/2410.05563v1) [2](https://openreview.net/pdf?id=ECXVwc1L4g)

### الترجمة عندنا
أي computation أو action معرفي داخل agent يجب أن يُنظر إليه بوصفه مرشحًا له:
1. Cost
2. Expected benefit
3. Timing value
4. Reusability value

---

## 8) Bound Optimality كمبدأ أعلى
Russell وSubramanian يقترحان أن perfect rationality ليست أساسًا مناسبًا، ويستبدلانها بفكرة **bounded optimality**، أي أن agent يجب أن يكون optimal بالنظر إلى architecture والقيود الفعلية [3](https://arxiv.org/abs/cs/9505103).

### الترجمة عندنا
المشروع لا يسعى إلى:
- perfect reasoning
بل إلى:
- **bounded-optimal cognition allocation**

وهذا ممتاز لأنه ينسجم مع واقع:
- API cost
- latency
- varying model tiers
- context limits

---

## 9) Resource-rationality كإطار موحد
resource-rational analysis تنظر إلى ما يبدو “bias” أو “shortcut” باعتباره قد يكون optimal under constraints [1](https://www.sciencedirect.com/science/article/abs/pii/S2352154621000371) [2](https://cocosci.princeton.edu/papers/lieder_resource.pdf).

### الترجمة عندنا
أحيانًا:
- retrieval shortcut
- heuristic stop
- عدم التصعيد
- أو حتى abstain

قد تكون قرارات ذكية، لا علامات ضعف.

إذًا يجب أن نسأل دائمًا:
- هل السلوك suboptimal حقًا؟
- أم optimal given limited resources and future opportunity cost؟

---

## 10) ما هي عناصر القرار الاقتصادي داخل agent؟
نقترح 7 أنواع قرارات اقتصادية معرفية:

### Decision Type A — Answer vs Think More
هل نُخرج answer الآن أم نزيد reasoning؟

### Decision Type B — Retrieve vs Reason Internally
هل نبحث في memory أو نولّد reasoning جديد؟

### Decision Type C — Cheap Model vs Premium Model
هل task تستحق التصعيد؟

### Decision Type D — Single Path vs Multi-Path Search
هل نكتفي linear أم نعمل self-consistency/tree/graph؟

### Decision Type E — Single Agent vs Sparse Committee
هل التنوع العقلي worth the cost؟

### Decision Type F — Solve Now vs Learn for Later
هل نوجّه جزءًا من compute لبناء lesson/concept/skill؟

### Decision Type G — Verify More vs Accept Risk
هل نزيد verification أم نقبل uncertainty؟

---

## 11) Value Functions المقترحة
### 11.1 Value of Computation (VoC)
ما فائدة تفكير إضافي مقارنة بتكلفته؟

### 11.2 Value of Information (VoI)
ما فائدة جمع evidence أو retrieval إضافي؟ [1](https://grokipedia.com/page/Value_of_information)

### 11.3 Value of Verification (VoV)
ما فائدة check إضافي أو judge إضافي؟

### 11.4 Value of Abstraction (VoA)
ما فائدة صرف compute على concept/skill/theory بدل الجواب الحالي فقط؟

### 11.5 Value of Reuse (VoR)
ما فائدة أن يكون الناتج reusable في المستقبل؟

### 11.6 Value of Escalation (VoE)
ما فائدة الانتقال من tier أقل إلى أعلى؟

### 11.7 Value of Collaboration (VoC*)
ما فائدة فتح sparse committee؟

---

## 12) المعادلة الكبرى المقترحة
بدل أن نقيم خطوة معرفية فقط بـ:
- immediate quality gain

نقترح أن تُقيَّم بـ:

**Expected Cognitive Return = Immediate Utility Gain + Future Reuse Gain + Learning Gain − Cost − Delay Penalty − Noise Risk**

هذه الصيغة ليست رياضية نهائية، لكنها principle مهم جدًا.

---

## 13) Anytime Cognition
أدبيات anytime algorithms تقول إن بعض الأنظمة يجب أن تكون قادرة على:
- إخراج حل صالح بسرعة
- ثم تحسينه إن توفر وقت إضافي [2](https://www.opentrain.ai/glossary/anytime-algorithm/) [4](https://arxiv.org/html/2601.11038)

### الترجمة عندنا
نحتاج agent يعمل بمنطق:
- first viable answer
- then optional improvement under budget

إذًا:

> intelligence should be interruptible yet improvable.

هذا مهم جدًا للبيئات الحية والـ APIs.

---

## 14) Cognitive Economy Ledger — artefact أساسي
نقترح artefact صريح يسجل:
- what cognition was spent on
- why
- expected benefit
- actual realized benefit

### حقول ledger
- **Task ID**
- **Cognitive action** (retrieve/search/escalate/verify/build concept/etc.)
- **Estimated Cost**
- **Estimated Value**
- **Actual Cost**
- **Actual Immediate Gain**
- **Actual Reuse Gain (later)**
- **Would repeat?**

هذا يسمح للنظام أن يتعلم ليس فقط من النتائج، بل من **اقتصاد قراراته**.

---

## 15) أين يحدث الهدر الإدراكي؟
### Waste Type 1 — Unnecessary Escalation
تصعيد إلى premium tier دون تحسن يبرر ذلك.

### Waste Type 2 — Verification Overkill
صرف checks كثيرة على task low-risk.

### Waste Type 3 — Redundant Retrieval
استرجاع معلومات كثيرة لا تؤثر على القرار.

### Waste Type 4 — Search Without Branch Value
فتح tree/graph دون داعٍ حقيقي.

### Waste Type 5 — Reflection Without Consolidation
reflection كثيرة لكن لا تتحول إلى artefacts نافعة.

### Waste Type 6 — Relearning Already Available Skills
حل المسألة من الصفر رغم وجود skill قابلة للاستدعاء.

---

## 16) أين يحدث التقشف الإدراكي الضار؟
### Underinvestment Type 1
عدم التصعيد رغم uncertainty عالية.

### Underinvestment Type 2
إخراج answer دون verifier عندما تكون المهمة حساسة.

### Underinvestment Type 3
عدم بناء lesson/skill بعد task باهظة أو غنية تعليميًا.

### Underinvestment Type 4
عدم تشغيل search topology مناسبة رغم وجود علامات topology mismatch.

---

## 17) الاقتصاد الإدراكي والمفهوم والذاكرة
### مع تكوين المفاهيم
قد يكون من الأجدى أحيانًا:
- صرف compute على concept formation
بدل:
- تحسين answer الحالية قليلًا

إذا كانت المهمة high-novelty وتولد reusable abstraction.

### مع Productive Forgetting
النسيان يقلل cost الإدراكي عبر:
- reducing clutter
- improving retrieval precision
- lowering contradiction noise

إذًا forgetting policy جزء من الاقتصاد الإدراكي.

### مع Contradiction Theory
إدارة التناقض نفسها لها cost.
أحيانًا الحسم الفوري غير اقتصادي، وأحيانًا الاحتفاظ بالتناقض أغلى من حله.

### مع Anomaly/Crisis Theory
الأزمات البنيوية قد تظهر أولًا على شكل:
- cost explosion
- premium dependency
- verifier overload
- patch inefficiency

---

## 18) الاقتصاد الإدراكي وexpected free energy
active inference يقدم فكرة أن agent لا يختار فقط ما يحقق utility، بل أيضًا ما يقلل uncertainty أو يحقق epistemic value [2](https://link.springer.com/article/10.1007/s00422-019-00805-w) [3](https://arxiv.org/abs/2504.14898).

### الترجمة عندنا
الagent الاقتصادي لا يسعى فقط إلى:
- correct answer

بل أيضًا إلى:
- uncertainty reduction when worth it
- epistemically valuable actions

لكن مع قيد جديد عندنا:
- cost-aware APIs
- bounded tiers

إذًا نحتاج نسخة agentic من:
- expected free energy
+ bounded economic governance

---

## 19) متى يجب أن نفكر أكثر؟
نقترح triggers أساسية:
1. high uncertainty
2. verifier disagreement
3. anomaly score high
4. high task value
5. high transfer opportunity
6. concept formation opportunity
7. contradiction not scope-resolved

إذا لم تتحقق هذه triggers، فزيادة التفكير قد تكون waste.

---

## 20) متى يجب أن نصعد؟
### قاعدة عامة
صعّد فقط إذا:
- expected utility gain + future reuse gain > escalation cost + delay penalty

### أمثلة
- task بسيطة formatting → no escalation
- hard synthesis with unstable evidence → maybe premium reasoning
- high-stakes answer with verifier split → likely escalation
- repeated family with reusable insight opportunity → escalation قد يكون worth it أكثر

---

## 21) متى يجب أن نفتح committee؟
الcommittee يجب أن تكون **آخر درجات التخصيص** لا الأولى.

### شروط committee
1. single strong model still unstable
2. multiple perspectives genuinely relevant
3. task value justifies latency/cost
4. disagreement cannot be resolved by extra verification alone

### وإلا:
- self-consistency أو model assist قد تكون أرخص وأنسب

---

## 22) Premium Compute Rule
### قانون أساسي
> Premium compute must buy reusable cognition.

أي premium reasoning يجب أن ينتج واحدًا أو أكثر من:
- reasoning scaffold
- argument graph
- lesson
- skill patch
- concept candidate
- anomaly evidence

وإلا صار استهلاكًا فاخرًا لا استثمارًا معرفيًا.

---

## 23) Cognitive Investment Portfolio
يمكن تصور استثمارات agent في أربع فئات:

### Portfolio A — Immediate Task Solving
answer / code / plan current task

### Portfolio B — Verification & Risk Reduction
tests / evidence / judges

### Portfolio C — Knowledge Capital Formation
lessons / concepts / skills / theories

### Portfolio D — System Restructuring
anomaly analysis / paradigm forks / new benchmarks

الـ agent الناضج لا يصرف كل ميزانيته على Portfolio A.

---

## 24) Failure modes في الاقتصاد الإدراكي
### Failure Mode 1 — Myopic Utility
يركز فقط على الجواب الحالي وينسى learning value.

### Failure Mode 2 — Prestige Bias
يصعد إلى premium لأن “الأقوى أفضل” دون مبرر.

### Failure Mode 3 — Cheapness Bias
يبخل في التصعيد لدرجة إنتاج answers هشة.

### Failure Mode 4 — Committee Fetish
يفتح collaboration بدون قيمة مضافة حقيقية.

### Failure Mode 5 — Reflection Vanity
يصرف cognition في reflections لا تتحول إلى assets.

### Failure Mode 6 — Verification Blindness
يوفر في التحقق حين يكون الخطأ مكلفًا.

---

## 25) كيف نختبر أن agent لديه اقتصاد إدراكي جيد؟
### Test A — Cost-Quality Frontier
هل يتحسن منحنى الجودة/الكلفة؟

### Test B — Escalation Calibration
هل يصعد عند الحاجة فقط؟

### Test C — Reuse Return Test
هل produce premium reasoning reusable artefacts؟

### Test D — Learning Allocation Test
هل يبني lessons/skills/concepts من المهام الغنية؟

### Test E — Waste Detection Test
هل يقلل redundant retrieval/search/verification overuse؟

---

## 26) البرنامج التجريبي المقترح
### تجربة 1 — Fixed policy vs Resource-rational policy
نقارن policy ثابتة مع policy تحسب العائد المتوقع من المزيد من التفكير.

### تجربة 2 — Premium always vs Premium on demand
هل التصعيد المشروط ينتج frontier أفضل؟

### تجربة 3 — Solve-only vs Solve+Learn allocation
هل تخصيص بعض compute لبناء lesson/skill/concept يعطي عائدًا أعلى عبر المهام؟

### تجربة 4 — Committee ladder
single path vs self-consistency vs model assist vs sparse committee

### تجربة 5 — Interruptible cognition
هل anytime-style stopping يحافظ على فاعلية جيدة تحت ضغوط الوقت/الكلفة؟

---

## 27) الفرضيات الجريئة
### Hypothesis A
العديد من إخفاقات agents ليست failures of reasoning بل failures of cognitive allocation.

### Hypothesis B
Resource-rational control سيعطي gains أكبر من مجرد switching to stronger models في كثير من الإعدادات العملية.

### Hypothesis C
الاستثمار في reusable cognition (skills/concepts/lessons) سيعطي long-run returns أعلى من استهلاك كل compute على immediate answers.

### Hypothesis D
يمكن استخدام مؤشرات الاقتصاد الإدراكي كإشارات مبكرة للأزمات البنيوية قبل تدهور benchmark score.

### Hypothesis E
أفضل agents لن تكون فقط those with better answers, بل those with better cognition portfolios.

---

## 28) النتيجة النظرية الحالية
إذا نجحت هذه النظرية، سننتقل من:
- “هل agent ذكي؟”
إلى:
- “كيف يخصص agent ذكاءه؟”

ومن:
- “quality of reasoning”
إلى:
- “governance of reasoning”

ومن:
- “model choice”
إلى:
- “cognitive portfolio management”

وهذا يجعل الاقتصاد الإدراكي ليس تفصيلًا هندسيًا، بل جزءًا من تعريف الذكاء نفسه في الأنظمة متعددة الطبقات فوق LLM APIs.
