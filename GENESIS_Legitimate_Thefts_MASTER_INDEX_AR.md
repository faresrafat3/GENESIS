# Virtual-GENESIS — السجل الموحّد الشامل للسرقات الشرعية
# Legitimate Thefts — Master Index (Consolidated Registry)

> Document Type: Master Theft Registry (Single Source of Truth)
> Status: Authoritative / Living Document
> Date: 2026-06-04
> Scope: يجمع كل السرقات الشرعية (5.1–5.89 بحثية + 6.1–6.13 كلاسيكية) في مرجع واحد
> Total: 88 سرقة بحثية + 13 سرقة كلاسيكية = **101 سرقة موثقة**

---

## 0) لماذا هذه الوثيقة؟ (لأي مطوّر قادم)

هذه هي **نقطة المرجع الوحيدة** لمنهجية "السرقة الشرعية" في المشروع. السرقات كانت مبعثرة
عبر 7 وثائق منفصلة (Master Architecture + 6 سجلات دورات). هنا نجمعها في فهرس واحد قابل
للتتبّع، حتى يستطيع أي شخص يبني على المشروع أن:

1. يعرف **من أين أتت كل فكرة** (المصدر الأصلي + الرابط).
2. يعرف **ما أخذناه بالضبط** وما **تركناه عمدًا** (حتى لا نوهم أننا أخذنا أكثر مما أخذنا).
3. يعرف **ما الذي تحوّلت إليه الفكرة** عمليًا في الكود (المكوّن التشغيلي).
4. يعرف **حالة التنفيذ**: هل المكوّن مبني فعلًا في الكود؟ أم مسار مستقبلي؟ أم مبدأ معماري؟

### منهجية السرقة الشرعية (القالب الثابت)
لكل فكرة مأخوذة من بحث/مشروع/كتاب:
```
المصدر (+ رابط)  →  ما أخذناه  →  ما تركناه الآن  →  ما أصبح عندنا (المكوّن التشغيلي)
```
> الجوهر: لا نبني من الصفر. نأخذ مجهود الغير بوعي، نحدد بدقة ما نأخذ وما نترك، ونحوّل كل
> سرقة إلى **مكوّن قابل للقياس** — لا فكرة معلّقة.

### مفتاح حالة التنفيذ
- 🟢 **مُنفَّذ**: يوجد كود فعلي شغّال + اختبارات.
- 🟡 **مبدأ/جزئي**: مبدأ معماري موجّه أو plumbing بدون أثر سلوكي قوي مُثبَت.
- ⚪ **مسار مستقبلي**: مذكور كاتجاه، لم يُبنَ بعد.

---

## 1) الجدول الرئيسي — السرقات البحثية (5.1–5.89)

### الموجة التأسيسية (5.1–5.23) — من Master Architecture

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.1 | **SIA** ([arxiv](https://arxiv.org/html/2605.27276)) | فصل harness عن weights | مبدأ "harness intelligence first" | 🟢 |
| 5.2 | **Meta-Harness** ([arxiv](https://arxiv.org/abs/2603.28052)) | traces > feedback مضغوط | trace-rich substrate | 🟡 |
| 5.3 | **AHE** ([alphaxiv](https://www.alphaxiv.org/resources/2604.25850)) | ثلاثية observability | manifest+test plan+rollback | 🟡 |
| 5.4 | **AutoHarness** ([ads](https://ui.adsabs.harvard.edu/abs/2026arXiv260303329L/abstract)) | موديل أصغر + harness أحسن | مبدأ معماري أساسي | 🟢 |
| 5.5 | **Reflexion** ([arxiv](https://arxiv.org/html/2303.11366)) | verbal reinforcement + episodic memory | Lesson Compiler + Failure Memory | 🟡 |
| 5.6 | **Self-Refine** ([arxiv](https://arxiv.org/abs/2303.17651)) | generate→critique→refine | micro-reflection داخل المهمة | 🟡 |
| 5.7 | **STaR** ([arxiv](https://arxiv.org/abs/2203.14465)) | verified rationales فقط | Verified Example Bank | 🟡 |
| 5.8 | **Voyager** ([arxiv](https://arxiv.org/abs/2305.16291)) | skill library + curriculum | Skill Capsules + Library | 🟡 |
| 5.9 | **SkillClaw** ([alphaxiv](https://www.alphaxiv.org/abs/2604.08377)) | collective skill evolution | مسار تطور المهارات | ⚪ |
| 5.10 | **DGM** ([arxiv](https://arxiv.org/pdf/2505.22954)) | archive + stepping stones | archive of policies/skills/patches | 🟡 |
| 5.11 | **Hyperagents** ([arxiv](https://arxiv.org/abs/2603.19461)) | meta-improvement editable | improvement policy optimization | ⚪ |
| 5.12 | **FunSearch/AlphaEvolve** ([nature](https://www.nature.com/articles/s41586-023-06924-6)) | search over artefacts + diversity | evolution over prompts/skills/policies | 🟡 |
| 5.84 | **AlphaEvolve (DeepMind 2025-2026 focus)** | evolutionary search over cognitive artifacts (skills/concepts/theories/policies) with strict evaluator + population diversity + lineage tracking | `GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md` (detailed 2026 theft) → Evolutionary Discovery Engine in orchestrator + concept/theory layers (Task 6) | 🟡 (detailed theft + integration plan ready) |
| 5.85 | **Co-Scientist (Gemini for Science, DeepMind 2025-2026)** | multi-agent "idea tournament" + hypothesis generation/debate/verification with citations + computational discovery | `GENESIS_DeepMind_CoScientist_Theft_AR.md` (detailed 2026 theft) → Co-Scientist Scientific Discovery Layer in orchestrator + blackboard + theory/concept (Task 7) | 🟡 (detailed theft + integration plan ready) |
| 5.86 | **Aletheia (Gemini Deep Think, DeepMind 2026)** | tripartite Generator-Verifier-Reviser loop + iterative generate-verify-revise in natural language + tool-grounded literature + failure admission for research-level proofs/theories | `GENESIS_DeepMind_Aletheia_Theft_AR.md` (detailed 2026 theft) → Aletheia-style Proof-Driven Verification & Theory Engine in verification_runtime + theory_runtime + orchestrator (Task 8) | 🟡 (detailed theft + integration plan ready) |
| 5.87 | **Robust Target Agent Code Generation + Execution Logging (from AlphaEvolve evo runs with gpt-oss-120b:free, run_49)** | Robust import-at-top enforcement, GENERAL data loading template (full shapes, no column hardcodes), mandatory robust execution logging block with fallbacks to prevent scope errors ("json" local var), fake accuracy, and partial data bugs in LLM-generated target_agent.py during evolutionary discovery | Updated META_AGENT_PROMPT + FEEDBACK_AGENT_PROMPT in `genesis/orchestrator.py` (with explicit templates + CRITICAL instructions); tested in run_49 (Gen1 had json scope error + (870,2) shape, Gen2 fixed by feedback; evo + feedback stabilized) | 🟢 (prompts updated + run evidence; ties directly to 5.84 AlphaEvolve integration in orchestrator) |
| 5.88 | **GPQA-style QA/Reasoning Agent Generation (from run_50 on gpqa, AlphaEvolve evo)** | Explicit GENERAL template for loading JSON questions (diamond_questions.json etc.), per-question pipeline call + client step-by-step reasoning to choose A/B/C/D, robust per-question error handling, and output compatible with evaluate.py. Addresses "No recognizable data files" fallback that caused 0% in first hard benchmark run. | Added dedicated "DEDICATED GUIDANCE FOR Q&A..." section + strengthened FEEDBACK in `genesis/orchestrator.py`; run_50 on gpqa succeeded without crash (constitutional lifted to 5/10 on Gen2), evaluate.py ran and produced results (198 questions), but agent still defaulted to generic path (0% accuracy — expected at this stage). | 🟢 (prompt update pushed; evidence from first real GPQA run with evo) |
| 5.89 | **Robust Submission Format Discovery + Escaping + Real Eval Integration (from run_52/53 gpqa, AlphaEvolve evo)** | Fix KeyError '"question_id"' in META_PROMPT.format (unescaped JSON examples); improve evaluate.py find_submission_file (prefer answers.json/submission.json, skip execution logs, content-aware); support evaluation_results.json in run_evaluation + evo fitness; strengthen prompts for BOTH files + strict A/B/C/D only + client enforcement. GENERAL for any Q&A/benchmark. Ties real metrics to evo (accuracy_percent). | Updated `genesis/orchestrator.py` (prompts, run_evaluation, evo engine); `genesis/tasks/gpqa/data/public/evaluate.py` (finder); format test passed, ready for real accuracy >0 on gpqa/SWE; run_53+ will pick correct submission. | 🟢 (fixes applied in workspace; evidence from run_52 0% + crash + evaluate.py source analysis; GENERAL protected) |
| 5.13 | **AutoTTS** ([arxiv](https://arxiv.org/abs/2605.08083)) | ابنِ environment يكتشف heuristics | Replay Research Lab | 🟡 |
| 5.14 | **Mem0** ([arxiv](https://arxiv.org/pdf/2504.19413)) | memory ops: add/update/delete/noop | explicit memory operations | 🟢 |
| 5.15 | **MemOS** ([arxiv](https://arxiv.org/html/2505.22101v1)) | memory as managed resource + lifecycle | Memory OS core plane | 🟢 |
| 5.16 | **SimpleMem** ([arxiv](https://arxiv.org/html/2601.02553v1)) | structured compression + consolidation | compression as first-class | 🟡 |
| 5.17 | **ProcMEM/MemSkill/SkillRL** ([icml](https://icml.cc/virtual/2026/poster/65830)) | procedural memory + skills from experience | Procedural Memory + Skill Genome | 🟡 |
| 5.18 | **MoA/SMoA/Self-Consistency** ([arxiv](https://arxiv.org/abs/2411.03284)) | sparse committees > dense | Ensemble Policy Ladder | ⚪ |
| 5.19 | **ToT/GoT/Self-Discover** ([arxiv](https://arxiv.org/abs/2305.10601)) | reasoning topology as decision variable | Search Topology Manager | ⚪ |
| 5.20 | **ExpeL** ([semscholar](https://www.semanticscholar.org/paper/5e4597eb21a393b23e473cf66cb5ae8b27cab03e)) | relevance-aware lesson retrieval | Heuristic Retrieval Store | 🟡 |
| 5.21 | **Memento-Skills** ([arxiv](https://arxiv.org/abs/2603.18743)) | agent designs agents via skills | Sub-Agent Generation | ⚪ |
| 5.22 | **MemoryArena/LongMemEval** ([arxiv](https://arxiv.org/html/2410.10813v2)) | memory quality ≠ recall only | Memory Utility Scorecard | 🟢 |
| 5.23 | **Self-Consolidation/DecentMem/TACO** ([arxiv](https://arxiv.org/abs/2602.01966)) | failure = educational; rules evolve | Compression Rule Registry | 🟡 |

### الدورة 2 (5.24–5.32) — Evaluation Pressure + Anomaly Leverage

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.24 | **Zeiler & Fergus 2014** ([arxiv](https://arxiv.org/abs/1311.1901)) | منهجية الـ ablation | `support_removal` operator | 🟢 |
| 5.25 | **Hogarth & Einhorn 1992** ([doi](https://doi.org/10.1016/0010-0285(92)90012-Q)) | order effects في الحكم | `evidence_reordering` operator | 🟢 |
| 5.26 | **Gardner/Nie 2020** ([arxiv](https://arxiv.org/abs/2004.02709)) | Contrast Sets / Adversarial NLI | `contrast_weakening` operator | 🟢 |
| 5.27 | **Mann & Thompson 1988** ([doi](https://doi.org/10.1515/text.1.1988.8.3.243)) | Rhetorical Structure Theory | `structure_weakening` operator | 🟢 |
| 5.28 | **Goodfellow/Geirhos** ([arxiv](https://arxiv.org/abs/2004.07780)) | adversarial examples / shortcut learning | `stronger_shortcut_lures` + anti-shortcut bench | 🟢 |
| 5.29 | **Bengio et al. 2009** ([acm](https://dl.acm.org/doi/10.1145/1553374.1553380)) | curriculum learning | منهج 6 مستويات | 🟢 |
| 5.30 | **Ribeiro et al. 2020** ([arxiv](https://arxiv.org/abs/2005.04118)) | CheckList behavioral testing | `perturbation_resistance` report | 🟢 |
| 5.31 | **Chandola et al. 2009** ([doi](https://doi.org/10.1145/1541880.1541882)) | anomaly severity tax. | `compute_anomaly_severity_score()` | 🟢 |
| 5.32 | **PagerDuty/Datadog** ([link](https://www.pagerduty.com/resources/learn/what-is-incident-management/)) | threshold escalation | `should_escalate_anomaly_aware()` | 🟢 |

### الدورة 3 (5.33–5.38) — Theory Leverage

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.33 | **Popper 1934** ([doi](https://doi.org/10.4324/9780203994627)) | قابلية التكذيب | `get_theory_prediction_for_task()` + predictive_value | 🟢 |
| 5.34 | **Bayesian Epistemology (Howson & Urbach)** ([doi](https://doi.org/10.1017/CBO9780511570643)) | تحديث بايزي + Laplace | `update_theory_predictive_value()` | 🟢 |
| 5.35 | **Theory-Theory (Gopnik & Wellman)** ([doi](https://doi.org/10.1111/j.1468-0017.1994.tb00156.x)) | المفاهيم ضمن نظريات | theory-guided concept boost (+3) | 🟢 |
| 5.36 | **EBL (DeJong & Mooney 1986)** ([doi](https://doi.org/10.1007/BF00114116)) | التعلم بالتفسير | theory-guided admission | 🟢 |
| 5.37 | **Scientific Realism (Boyd/Putnam)** ([doi](https://doi.org/10.1017/CBO9780511625268)) | النجاح التنبؤي دليل بنيوي | predictive_value as quality | 🟢 |
| 5.38 | **DevOps Runbook / SRE (Google 2016)** ([sre.google](https://sre.google/sre-book/table-of-contents/)) | runbook استباقي | theory-as-runbook routing | 🟢 |

### الدورة 4 (5.39–5.44) — Broader Domain

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.39 | **Bloom's Taxonomy 1956/2001** ([doi](https://doi.org/10.1002/9780470479216.corpsy0128)) | التحليل كعملية عليا | عائلة `analysis` | 🟢 |
| 5.40 | **Information Extraction (Sarawagi 2008)** ([doi](https://doi.org/10.1561/1500000003)) | slot filling | عائلة `extraction` | 🟢 |
| 5.41 | **STRIPS/PDDL (Fikes & Nilsson 1971)** ([doi](https://doi.org/10.1016/0004-3702(71)90010-5)) | التخطيط + التبعيات | عائلة `planning` | 🟢 |
| 5.42 | **Transfer Learning (Pan & Yang 2010)** ([doi](https://doi.org/10.1109/TKDE.2009.191)) | قياس النقل عبر المجالات | `generate_domain_transfer_report()` | 🟢 |
| 5.43 | **Curriculum Learning (Bengio 2009)** ([acm](https://dl.acm.org/doi/10.1145/1553374.1553380)) | تدرّج صعوبة على مجالات جديدة | `build_v7_broader_domain_curriculum()` | 🟢 |
| 5.44 | **Meta-Learning (Thrun 1998)** ([doi](https://doi.org/10.1007/978-1-4615-5529-2_1)) | التعميم عبر أنواع مهام | portability verdict | 🟢 |

### الموجة 3 (5.45–5.54) — Self-Benchmarking + Productive Forgetting

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.45 | **FunSearch (Romera-Paredes 2023)** ([nature](https://www.nature.com/articles/s41586-023-06924-6)) | بحث في artefacts تحت evaluator | `benchmark_generator.py` | 🟢 |
| 5.46 | **AutoTTS** (امتداد 5.13) | بيئة تكتشف heuristics اختبار | `run_self_benchmark_cycle` | 🟢 |
| 5.47 | **Novelty Search (Lehman & Stanley 2011)** ([doi](https://doi.org/10.1162/EVCO_a_00025)) | بحث مدفوع بالتنوع | `blind_spot_discovery.py` | 🟢 |
| 5.48 | **Metamorphic Testing (Chen 2018)** ([doi](https://doi.org/10.1145/3143561)) | علاقات تحويلية بلا oracle | `diagnostic_value.py` | 🟢 |
| 5.49 | **Curriculum Self-Play (Silver 2017)** ([doi](https://doi.org/10.1038/nature24270)) | توليد التحديات ذاتيًا | self-benchmark loop (7 خطوات) | 🟢 |
| 5.50 | **Ebbinghaus 1885** ([doi](https://doi.org/10.1037/10011-000)) | منحنى النسيان | `store.apply_decay()` | 🟢 |
| 5.51 | **Retrieval-Induced Forgetting (Anderson 1994)** ([doi](https://doi.org/10.1037/0278-7393.20.5.1063)) | الاسترجاع يُضعف المنافس | `record_access()` + decay | 🟢 |
| 5.52 | **Reconsolidation (Nader 2000)** ([doi](https://doi.org/10.1038/35021052)) | الذاكرة المُنشّطة قابلة للتحديث | utility recompute on access | 🟢 |
| 5.53 | **Desirable Difficulties (Bjork 1994)** ([doi](https://doi.org/10.1016/S0079-7421(08)60016-2)) | الانتقائية تقوّي ما يبقى | `forgetting_policy` | 🟢 |
| 5.54 | **MemOS** (امتداد 5.15) ([arxiv](https://arxiv.org/abs/2506.06326)) | lifecycle management | archive/deprecate/delete + get_active | 🟢 |

### الموجة 3ب (5.55–5.62) — Identity Governance + Paradigm Fork

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.55 | **Personal Identity (Locke 1689, Parfit 1984)** ([doi](https://doi.org/10.1093/019824908X.001.0001)) | الهوية = استمرارية الالتزامات | `AgentIdentityObject` | 🟡 |
| 5.56 | **Organizational Governance (OECD/Cadbury 1992)** ([doi](https://doi.org/10.1787/9789264015999-en)) | سلاسل المساءلة | `accountability_log` + `CommitmentLedger` | 🟡 |
| 5.57 | **Git VCS (Torvalds 2005)** ([git-scm](https://git-scm.com/)) | تتبع السلالة | `lineage` tracking | 🟡 |
| 5.58 | **Constitutional AI (Bai 2022)** ([arxiv](https://arxiv.org/abs/2212.08073)) | المبادئ كدستور | commitments كدستور حاكم | 🟡 |
| 5.59 | **Kuhn 1962** (امتداد 6.3) ([doi](https://doi.org/10.7208/chicago/9780226458106.001.0001)) | تراكم الشذوذ → أزمة | `detect_crisis()` | 🟡 |
| 5.60 | **Lakatos 1978** (امتداد 6.2) ([doi](https://doi.org/10.1017/CBO9780511621123)) | انحطاط البرنامج البحثي | `theory_failures` metric | 🟡 |
| 5.61 | **Git Branching (Driessen 2010)** ([nvie](https://nvie.com/posts/a-successful-git-branching-model/)) | fork as branch مع حفظ الأصل | `propose_fork()` + `execute_fork()` | 🟡 |
| 5.62 | **Punctuated Equilibrium (Tushman & Romanelli 1985)** ([doi](https://doi.org/10.1016/0191-3085(85)90007-5)) | استقرار طويل + تغيير نادر | 3 مستويات أزمة + fork مضبوط | 🟡 |

### مرحلة الإنتاج (5.63–5.76) — API + Persistence + Real LLM

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.63 | **OpenRouter Multi-Model** ([docs](https://openrouter.ai/docs)) | tier→model mapping | `APIConfig.model_mapping` + `LLMAdapter` | 🟢 |
| 5.64 | **Session Architecture (Fielding REST, RFC 6265)** ([link](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)) | جلسات ذات حالة + دورة حياة | `Session` + `SessionManager` | 🟢 |
| 5.65 | **CheckList (Ribeiro 2020)** ([arxiv](https://arxiv.org/abs/2005.04118)) | MFT + invariance على العقد | `property_removal` operator | 🟢 |
| 5.66 | **Contrast Sets (Gardner 2020)** ([arxiv](https://arxiv.org/abs/2004.02709)) | أدنى تعديل يقلب الحكم | `property_addition` + `shortcut_injection` | 🟢 |
| 5.67 | **Counterfactual Data (Kaushik 2020)** ([arxiv](https://arxiv.org/abs/1909.12434)) | نفس النص، حكم معكوس | `contract_flip` + `counterfactual_contract` | 🟢 |
| 5.68 | **Dynabench (Kiela 2021)** ([arxiv](https://arxiv.org/abs/2104.14337)) | benchmark عدائي ديناميكي | `contract_tightening_strict` | 🟢 |
| 5.69 | **Mem0 (2024)** ([arxiv](https://arxiv.org/pdf/2504.19413)) | CRUD lifecycle + versioning | `SQLiteMemoryStore` | 🟢 |
| 5.70 | **MemGPT/Letta (Packer 2023)** ([arxiv](https://arxiv.org/abs/2310.08560)) | memory as OS + hierarchy | decay + status (hot/warm/cold) | 🟢 |
| 5.71 | **LangGraph Persistence (2024)** ([docs](https://langchain-ai.github.io/langgraph/)) | state checkpointing | `checkpoint.py` | 🟢 |
| 5.72 | **SQLite WAL + JSON1** ([sqlite](https://www.sqlite.org/wal.html)) | تخزين ACID بلا تبعيات | `sqlite3` persistence layer | 🟢 |
| 5.73 | **SWE-bench (Jimenez 2024)** ([arxiv](https://arxiv.org/abs/2310.06770)) | تقييم على مهام حقيقية | `run_real_llm_eval.py` | 🟢 |
| 5.74 | **LATS (Zhou 2024)** ([arxiv](https://arxiv.org/abs/2310.04406)) | مقارنة configs بنفس prompts | شروط A/B/C | 🟢 |
| 5.75 | **DSPy (Khattab 2024)** ([arxiv](https://arxiv.org/abs/2310.03714)) | تحسين مدفوع بالمقياس | `concept_lift`/`theory_lift` | 🟢 |
| 5.76 | **Ablation Evaluation Protocol (Melis 2018, Lipton & Steinhardt 2018)** ([arxiv](https://arxiv.org/abs/1707.05589)) | سلّم استئصال متدرج | A/B/C ablation ladder | 🟢 |

### مرحلة التحقق العدائي (5.77–5.80) — Adversarial Validation

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.77 | **Adversarial Filtering / HellaSwag (Zellers 2019)** ([arxiv](https://arxiv.org/abs/1905.07830)) | بناء عناصر تفشل فيها النماذج بالتصميم | `adversarial_hard_cases.py` | 🟢 |
| 5.78 | **Inverse Scaling Prize (McKenzie 2023)** ([arxiv](https://arxiv.org/abs/2306.09479)) | القدرة ≠ اتباع التعليمات | lure framing | 🟢 |
| 5.79 | **Sycophancy (Perez 2023, Anthropic)** ([arxiv](https://arxiv.org/abs/2212.09251)) | النماذج تأخذ اختصارات لإرضاء الصياغة | `strict_failure_markers` | 🟢 |
| 5.80 | **CheckList Failure-Rate (Ribeiro 2020)** ([arxiv](https://arxiv.org/abs/2005.04118)) | معدل الفشل هو الإشارة | strict scorer (shortcut/evidence rate) | 🟢 |

### مرحلة القفل الداخلي (5.81–5.83) — Internal Regime Lock (anti-sprawl)

| # | المصدر | ما أخذناه (مختصر) | ما أصبح عندنا | الحالة |
|---|--------|-------------------|----------------|:---:|
| 5.81 | **Model Cards (Mitchell et al. 2019, Google)** ([arxiv](https://arxiv.org/abs/1810.03993)) | بطاقة رسمية تحدد النطاق المعتمد + الاستخدام المقصود + الحدود كمرجع واحد | `Virtual_SIA_Internal_Regime_Lock_AR.md` كـ "بطاقة معمارية" (نواة/نطاق/حدود) | 🟢 |
| 5.82 | **Golden Configuration / Baselines (ITIL · NIST SP 800-128)** ([nist](https://csrc.nist.gov/pubs/sp/800/128/final)) | "تهيئة ذهبية" مجمّدة كخط أساس، وأي انحراف يُبرَّر | Canonical Configuration المجمّدة (§2.3) + قاعدة "كل flag حوكمة OFF افتراضيًا" | 🟢 |
| 5.83 | **SemVer + Trunk-Based Release Trains (Preston-Werner)** ([semver](https://semver.org/)) | فصل النواة المستقرة (trunk) عن التوسّعات قبل نضجها | تصنيف الطبقات A/B/C + قواعد منع التشعّب (anti-sprawl) | 🟢 |

---

## 2) الجدول الرئيسي — السرقات الكلاسيكية (6.1–6.13)

| # | المصدر | ما أخذناه | ما أصبح عندنا | الحالة |
|---|--------|-----------|----------------|:---:|
| 6.1 | **Polya** (How to Solve It) | فهم→خطة→تنفيذ→مراجعة | Understander/Planner/Executor/Reflector | 🟡 |
| 6.2 | **Lakatos** (Proofs & Refutations) | conjecture/proof/refutation/revision | answer=conjecture, verifier=counterexample | 🟢 |
| 6.3 | **Kuhn** (Scientific Revolutions) | anomaly/crisis/paradigm shift | anomaly detector + crisis + fork | 🟡 |
| 6.4 | **Simon** (Bounded Rationality) | satisficing + aspiration | Budget Governor + good-enough stopping | 🟢 |
| 6.5 | **OODA** (Boyd) | Observe/Orient/Decide/Act | OODA Controller (pipeline flow) | 🟢 |
| 6.6 | **Blackboard Architecture** | shared problem state | Task Blackboard | 🟢 |
| 6.7 | **Society of Mind** (Minsky) | الذكاء = مجتمع وكلاء | Society of Cognitive Services | 🟡 |
| 6.8 | **Predictive Processing** (Friston) | hypothesis + prediction error | hypothesis-first + anomaly severity | 🟢 |
| 6.9 | **Toulmin** (Argument Model) | claim/grounds/warrant/rebuttal | Argument Graph (contract verification) | 🟡 |
| 6.10 | **Schön** (Reflective Practitioner) | reflection in/on action | micro-reflection + postmortem | 🟡 |
| 6.11 | **Dreyfus** (Skill Acquisition) | novice→expert ladder | Skill Maturity Ladder | ⚪ |
| 6.12 | **Ashby** (Requisite Variety) | only variety absorbs variety | Policy Portfolio + tier escalation | 🟢 |
| 6.13 | **Case-Based Reasoning** (Aamodt & Plaza) | Retrieve/Reuse/Revise/Retain | Case-Based Adaptation (TaskCase) | 🟢 |

---

## 3) خريطة السرقات → ملفات الكود (للمطوّر)

| المكوّن في الكود | السرقات المسؤولة |
|------------------|-------------------|
| `runtime/concept_engine/` | 5.7, 5.20, 5.35, 5.36, 6.13 |
| `runtime/memory_os/` (+ decay/forgetting) | 5.14, 5.15, 5.16, 5.22, 5.50–5.54 |
| `runtime/theory_runtime/` | 5.33–5.38, 6.2 |
| `runtime/anomaly_runtime/` | 5.31, 5.32, 6.3, 6.8 |
| `runtime/economy_control/` | 5.4, 6.4, 6.12 |
| `runtime/verification_runtime/` | 6.2, 6.8, 6.9 |
| `runtime/identity_runtime/` | 5.55–5.62 |
| `eval/perturbations/` | 5.24–5.28, 5.65–5.68 |
| `eval/task_sets/` (+ adversarial) | 5.39–5.41, 5.77–5.80 |
| `eval/reports/` | 5.30, 5.42, 5.47, 5.48 |
| `eval/runners/` (+ real LLM) | 5.29, 5.43, 5.45, 5.46, 5.49, 5.73–5.76 |
| `persistence/` (SQLite) | 5.69–5.72 |
| `api/` | 5.63, 5.64 |
| `runtime/pipeline/minimal_run.py` | 6.1, 6.5, 6.6, 6.7 |
| `genesis/orchestrator.py` + `virtual_genesis/runtime/blackboard_core/` | 5.84 (Evolutionary Discovery), 5.85 (Co-Scientist tournament), 5.86 (Aletheia proof-driven loop), 5.87 (robust code gen/logging for evo), 6.6 (Blackboard) |
| `Virtual_SIA_Internal_Regime_Lock_AR.md` (منهجية القفل/anti-sprawl) | 5.81–5.83 |

---

## 4) إحصاء حالة التنفيذ (شفافية كاملة)

من الـ 98 سرقة:

| الحالة | العدد | النسبة | المعنى |
|--------|:---:|:---:|--------|
| 🟢 مُنفَّذ (كود + اختبارات) | ~61 | ~62% | فكرة تحوّلت لمكوّن شغّال مُختبَر |
| 🟡 مبدأ/جزئي | ~28 | ~29% | موجّه معماري أو plumbing بلا أثر سلوكي قوي مُثبَت |
| ⚪ مسار مستقبلي | ~9 | ~9% | اتجاه مذكور لم يُبنَ بعد |

> **ملاحظة صدق علمي:** "مُنفَّذ" تعني "موجود كود يعمل ومُختبَر" — **لا** تعني "مُثبَت تجريبيًا
> أنه يحسّن الأداء". الإثبات التجريبي منفصل وموثّق في `Virtual_SIA_Adversarial_Validation_Memo_AR.md`
> و`Virtual_SIA_Real_LLM_Broader_Results_AR.md`. ربط كل سرقة بمستوى إثباتها التجريبي هو عمل مستقبلي.

---

## 5) السرقات حسب الفئة المعرفية (للنظرية)

- **الذاكرة (Memory):** 5.14, 5.15, 5.16, 5.22, 5.50–5.54, 5.69–5.72
- **المفاهيم (Concepts):** 5.7, 5.20, 5.35, 5.36, 6.13
- **النظريات (Theories):** 5.33–5.38, 6.2
- **الحوكمة (Governance):** 5.31, 5.32, 5.55–5.62, 6.3
- **التقييم (Evaluation):** 5.24–5.30, 5.45–5.49, 5.65–5.68, 5.73–5.80
- **الاقتصاد المعرفي (Economy):** 5.1, 5.4, 6.4, 6.12
- **بنية التفكير (Reasoning):** 5.6, 5.18, 5.19, 6.1, 6.5, 6.6, 6.8, 6.9, 5.84, 5.85, 5.86, 5.87
- **التحسّن الذاتي (Self-Improvement):** 5.5, 5.10, 5.11, 5.12, 5.13, 5.21, 5.45, 5.46, 5.84, 5.85, 5.86, 5.87
- **البنية التحتية (Infrastructure):** 5.63, 5.64, 5.69–5.72
- **حماية الاتساع (Anti-Sprawl / Project Governance):** 5.81–5.83

---

## 6) المصادر المنفصلة (لمن يريد التوسّع)

هذا الفهرس يلخّص؛ التفاصيل الكاملة لكل سرقة (ما تركناه + التبريرات) في:
- `Virtual_SIA_Master_Architecture_AR.md` (5.1–5.23، 6.1–6.13)
- `Virtual_SIA_Legitimate_Thefts_Cycle2_AR.md` (5.24–5.32)
- `Virtual_SIA_Legitimate_Thefts_Cycle3_AR.md` (5.33–5.38)
- `Virtual_SIA_Legitimate_Thefts_Cycle4_AR.md` (5.39–5.44)
- `Virtual_SIA_Legitimate_Thefts_Wave3_AR.md` (5.45–5.54)
- `Virtual_SIA_Legitimate_Thefts_Wave3b_AR.md` (5.55–5.62)
- `Virtual_SIA_Legitimate_Thefts_Production_AR.md` (5.63–5.64)
- `Virtual_SIA_Legitimate_Thefts_RealWorld_AR.md` (5.65–5.75)
- `Virtual_SIA_Real_LLM_Broader_Results_AR.md` (5.76)
- `Virtual_SIA_Adversarial_Validation_Memo_AR.md` (5.77–5.80)
- `Virtual_SIA_Internal_Regime_Lock_AR.md` (5.81–5.83)
- `GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md` (5.84)
- `GENESIS_DeepMind_CoScientist_Theft_AR.md` (5.85)
- `GENESIS_DeepMind_Aletheia_Theft_AR.md` (5.86)

---

## 7) ملحق المصدر (Provenance) — السرقات 5.65–5.85

أُضيفت هذه السرقات بتاريخ **2026-05-31 / 2026-06-01** عبر آخر دفعة من العمل، ومصادرها داخل المشروع (بالإضافة للـ DeepMind 2026-06-04):

| المدى | الدفعة (commit theme) | الملفات الناتجة |
|-------|------------------------|------------------|
| 5.65–5.68 | **Contract Perturbation** | `eval/perturbations/contract_perturbations.py` |
| 5.69–5.72 | **SQLite Persistence** | `persistence/*.py` |
| 5.73–5.76 | **Real LLM Eval** | `api/llm_reasoning.py`, `eval/runners/run_real_llm_*` |
| 5.77–5.80 | **Adversarial Validation** | `eval/task_sets/adversarial_hard_cases.py`, `eval/runners/run_adversarial_llm_eval.py` |
| 5.81–5.83 | **Internal Regime Lock** | `Virtual_SIA_Internal_Regime_Lock_AR.md` |
| 5.84–5.89 | **DeepMind Science Thefts (AlphaEvolve + Co-Scientist + Aletheia) + Robust Evo Code Gen + Submission/Eval Integration** | `GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md` (5.84 + 5.87-5.89), `GENESIS_DeepMind_CoScientist_Theft_AR.md`, `GENESIS_DeepMind_Aletheia_Theft_AR.md` (Cycle 6 memos) + prompt robustness + evaluate integration in orchestrator (run_49/52/53 evidence) |

> كل هذه السرقات موثّقة بالتفصيل الكامل (ما أُخذ / ما تُرك / ما أصبح) في وثائقها الأصلية المذكورة
> في §6، ومُلخّصة في الجداول أعلاه (§1).

---

*نهاية السجل الموحّد الشامل — هذه الوثيقة هي المرجع الرسمي لمنهجية السرقة الشرعية في Virtual-GENESIS.*
