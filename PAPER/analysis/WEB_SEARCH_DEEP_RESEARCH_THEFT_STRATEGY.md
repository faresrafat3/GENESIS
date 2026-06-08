# استراتيجية السرقة الشرعية العميقة — Web Search + Deep Research في GENESIS
# تاريخ: 2026-06-08
# المصدر: تحليل 15+ ورقة بحثية من 2025-2026

---

## الصورة الكاملة للمجال — ليس سطحياً

### التطور التاريخي في 4 مراحل (من arXiv:2506.18959)

```
المرحلة 1 (قبل 2023): Static RAG
  Query → Retrieve → Generate
  المشكلة: ثابت، لا يتكيف، يعتمد على corpus محدود

المرحلة 2 (2023-2024): Iterative RAG
  Query → Retrieve → Reason → Re-Query → ...
  FLARE, Self-RAG, IRCoT
  المشكلة: لا يتعلم من البيئة، يبحث في corpora ثابتة

المرحلة 3 (2024-2025): Agentic RAG
  ReAct: Thought → Action (Search) → Observation → Thought...
  Search-o1, WebThinker, SimpleDeepSearcher
  المشكلة: prompting فقط، لا يحسّن استراتيجية البحث

المرحلة 4 (2025-2026): RL-Trained Deep Research
  DeepResearcher, Search-R1, R1-Searcher, WebThinker (NeurIPS)
  Agent يتدرب في بيئة ويب حقيقية بـ RL
  يتعلم: متى يبحث؟ كيف يُعيد الصياغة؟ كيف يتراجع؟
```

**GENESIS حالياً = المرحلة 0** (بدون أي بحث)
**الهدف المباشر = المرحلة 3** (Agentic RAG بدون RL training)
**الهدف البعيد = المرحلة 4** (لو أضفنا RL على الـ orchestrator)

---

## الأوراق المحددة والعناصر المسروقة

---

### 🥇 THEFT #1 — DeepResearcher (arXiv:2504.03160)
**الورقة:** "DeepResearcher: Scaling Deep Research via Reinforcement Learning in Real-world Environments"
**المختبر:** Qwen Team — أبريل 2025

**ما نسرقه:**

#### 1. بنية الـ Tool Call
```python
# DeepResearcher يستخدم JSON-structured tool calls:
{
  "tool": "web_search",
  "queries": ["query1", "query2"]  # يبحث بأكثر من query في نفس الوقت
}
# النتيجة: {title, url, snippet} لكل نتيجة

# للـ web browsing:
{
  "tool": "web_browse", 
  "url": "https://..."
}
# النتيجة: محتوى الصفحة مضغوط في short-term memory
```

#### 2. Short-Term Memory for Evidence
```python
# DeepResearcher يحتفظ بـ memory repository لكل query
# عند browse: يقرر (1) هل يكمل القراءة؟ (2) ما الذي يضيفه للـ memory؟
# يُجمّع الـ evidence قبل الـ synthesis
```

#### 3. Reasoning-before-Action Pattern
```
<think>
  [الـ agent يفكر: هل المعلومة كافية؟ هل المصدر موثوق؟]
</think>
[action: web_search/web_browse/synthesize]
```

**نسرق:** البنية الكاملة — tool call format + short-term memory + reasoning wrapper
**نُطبّق في:** `META_AGENT_PROMPT` snippet في orchestrator + reference_target_agent

---

### 🥇 THEFT #2 — Search-R1 (COLM 2025, arXiv:2503.00223)
**الورقة:** "Search-R1: Training LLMs to Reason and Leverage Search Engines with RL"
**المختبر:** Jin et al. — مارس 2025

**ما نسرقه:**

#### 1. الـ Reward Structure (للمستقبل — عند إضافة RL للـ orchestrator)
```python
# Search-R1 يحسب reward على:
# (1) Final answer correctness (EM score)
# (2) Search token efficiency (لا يعاقب على البحث المفيد)
# (3) يُهمل tokens الـ search results في حساب الـ KL divergence

# نسرق هذا المبدأ:
# الـ Regime Detector يُكافئ search diversity
# لا يُعاقب على كثرة البحث إذا أدى لـ accuracy أعلى
```

#### 2. Search Token Masking في الـ Feedback
```
# Search-R1: tokens الـ search results لا تدخل في loss
# نسرق: الـ feedback agent لا يُحاسب الـ agent على "كم بحث"
# بل يُحاسبه على "كيف استخدم نتائج البحث"
```

**نُطبّق في:** Regime Detector (signal جديد: search_effectiveness)

---

### 🥇 THEFT #3 — WebThinker (NeurIPS 2025)
**الورقة:** "WebThinker: Empowering Large Reasoning Models with Deep Research Capability"
**المختبر:** Li et al. — أبريل 2025

**ما نسرقه — الأهم:**

#### "Think-Search-Draft" Loop
```
الفرق الجوهري عن DeepResearcher:
WebThinker لا ينتظر حتى ينتهي من كل البحث ثم يكتب
بل يتناوب: Think → Search → Draft → Search → Revise

ده يعني:
- الـ agent يبدأ يكتب التقرير وهو لسه بيبحث
- كل search يُحسّن draft موجود — مش بيبدأ من صفر
- النتيجة: تقارير أكثر تماسكاً وأقل hallucination
```

#### Online DPO للـ Iterative Refinement
```python
# WebThinker يستخدم DPO لتفضيل trajectories الأفضل
# نسرق المبدأ: الـ Feedback Agent يُقارن Gen N مع Gen N-1
# ويُرجّح الـ trajectory الأفضل بحثاً وليس فقط accuracy
```

**نُطبّق في:**
- `META_AGENT_PROMPT`: "ابدأ تكتب draft أثناء البحث — لا تنتظر"
- Feedback Agent: يُقارن search trajectory quality

---

### 🥇 THEFT #4 — A-RAG (arXiv:2602.03442)
**الورقة:** "A-RAG: Scaling Agentic RAG"
**المختبر:** فبراير 2026

**ما نسرقه — الأذكى:**

#### 3 مستويات من الـ Search Tools
```python
# A-RAG يُعطي الـ agent 3 tools بدل 1:
tools = {
    "keyword_search": "ابحث بكلمات مفتاحية — سريع وواسع",
    "semantic_search": "ابحث بالمعنى — أبطأ لكن أدق",
    "chunk_read": "اقرأ جزء محدد من مصدر — للتعمق"
}
# الـ agent يختار التول المناسب لكل مرحلة

# نسرق:
# بدل web_search واحد نُعطي الـ agent:
# - quick_search: snippet فقط (سريع، رخيص)
# - deep_search: snippet + page content (أبطأ، أغلى)
# - read_source: اقرأ URL محدد كامل
```

**نُطبّق في:** Web Search Tool Layer — 3 functions بدل 1

---

### 🥇 THEFT #5 — Rulers (arXiv:2601.08654)
**الورقة:** "Rulers: Locked Rubrics and Evidence-Anchored Scoring"
**المختبر:** يناير 2026

**ما نسرقه — للـ LLM-as-Judge:**

#### Schema-Constrained Evaluation
```python
# Rulers لا يسأل الـ judge "هل الإجابة صح؟"
# بل يُجبره على إنتاج structured object:
judge_output = {
    "checklist": [True, False, True, ...],  # decision vector
    "evidence_quotes": [
        {"unit": "paragraph_3", "quote": "النص المقتبس"},
        ...
    ],
    "boundary_justifications": "لماذا هذا الحد؟",
    "final_score": 7.2
}
# النتيجة: لا يستطيع الـ judge يخترع — كل ادعاء مرتبط بـ quote

# نسرق هذا تماماً للـ Open Task Evaluator في GENESIS:
# الـ judge لا يُعطي score فقط — يُعطي evidence_quotes
# كل claim مرتبط بنص فعلي من الـ output
# Hallucinated claims = لا يوجد quote → يُحسب كـ hallucination
```

**نُطبّق في:** LLM-as-Judge في Section 5a.1

---

### 🥇 THEFT #6 — MA-RAG (arXiv:2505.20096)
**الورقة:** "MA-RAG: Multi-Agent Retrieval-Augmented Generation"
**المختبر:** مايو 2025

**ما نسرقه:**

#### Planner → Step Definer → Retriever Architecture
```
MA-RAG يفصل:
  1. Planner: يقرأ الـ query ويُجزّئه لـ sub-questions
  2. Step Definer: لكل sub-question يولّد subquery تفصيلي للبحث
  3. Retriever: ينفذ البحث ويُعيد evidence
  4. Generator: يُجمّع كل الـ evidence ويُنتج الإجابة

الفرق عن single-agent: الـ Planner يرى الصورة الكاملة
الـ Step Definer يتخصص في توليد queries فعّالة

نسرق هذا الفصل للـ Goal Specification Layer في GENESIS:
  Section 0a (Planner): يجزّئ الـ task لـ sub-goals
  Section 0b (Step Definer): لكل sub-goal يولّد search queries
  Section 5a (Retriever + Generator): الـ target agent ينفذ
```

**نُطبّق في:** Goal Specification Layer

---

### 🥇 THEFT #7 — InfoDeepSeek Benchmark (arXiv:2505.15872)
**الورقة:** "InfoDeepSeek: Benchmarking Agentic Information Seeking"
**المختبر:** مايو 2025

**ما نسرقه:**

#### IA@5 Metric — Information Accuracy at 5 iterations
```
InfoDeepSeek يقيس:
  - ACC: هل الإجابة النهائية صح؟
  - IA@5: هل المعلومات المجمّعة في 5 خطوات دقيقة؟

الفكرة المهمة: قياس جودة البحث مستقلاً عن جودة الإجابة
يمكن الـ agent يجمع معلومات صح لكن يُجيب غلط (reasoning error)
أو يُجيب صح رغم معلومات ناقصة (lucky guess)

نسرق هذا المبدأ:
Evidence Audit Score (مستقل عن Final Output Score)
- Output Score: هل التقرير النهائي جيد؟
- Evidence Score: هل المعلومات المجمّعة موثّقة وصحيحة؟
الاثنان يدخلان الـ Regime Detector كـ signals منفصلة
```

**نُطبّق في:** Evidence Audit في Section 5a.1

---

### 🥇 THEFT #8 — SAGE Benchmark (arXiv:2602.05975)
**الورقة:** "SAGE: Benchmarking and Improving Retrieval for Deep Research Agents"
**المختبر:** فبراير 2026

**ما نسرقه — اكتشاف مهم جداً:**

#### BM25 يتفوق على LLM Retrievers بـ 30%!
```
SAGE اكتشف:
  BM25 (keyword matching قديم) > LLM-based retrievers في corpus بحثي
  السبب: الـ LLM agents يولّدون sub-queries طويلة وكثيرة الكلمات
  بينما BM25 يحتاج keywords موجزة ودقيقة

الدرس:
  لا تجعل الـ agent يبحث بجمل طويلة
  جبره يولّد keywords مضغوطة أولاً
  ثم يبحث بالـ keywords
  
نسرق: في Step Definer، نُجبر توليد keywords قبل الـ query الكاملة:
{
  "keywords": ["micro-task", "Egypt", "payment proof", "2026"],
  "full_query": "micro-task platforms available in Egypt with payment proof 2026"
}
ونبحث بالاثنين: keyword_search + semantic_search
```

**نُطبّق في:** Search Planning (Section 0b) + Web Search Tool

---

## الاستراتيجية الكاملة للتطبيق في GENESIS

### 4 طبقات — بالترتيب من الأسهل للأصعب

---

#### الطبقة 1 — Tool Layer (أسبوع واحد)
**ما نبنيه:** `genesis/tools/web_search.py`

```python
import httpx
import os

def web_search(query: str, mode: str = "quick") -> list[dict]:
    """
    Stolen from: DeepResearcher (tool format) + A-RAG (3 modes) + SAGE (keyword extraction)
    
    modes:
      "quick"  → snippet only (Serper API, 10 results) — رخيص وسريع
      "deep"   → snippet + first paragraph (Serper + Jina reader)
      "read"   → full page content (Jina reader URL)
    
    Returns: [{title, url, snippet, date, credibility_hint}]
    """
    api_key = os.getenv("SERPER_API_KEY") or os.getenv("WEB_SEARCH_API_KEY")
    
    if mode == "quick":
        # Serper API — JSON search
        response = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": 10},
            timeout=30
        )
        results = response.json().get("organic", [])
        return [{"title": r.get("title"), "url": r.get("link"), 
                 "snippet": r.get("snippet"), "date": r.get("date", "unknown"),
                 "credibility_hint": "search_result"} for r in results]
    
    elif mode == "read":
        # Jina Reader — full page
        response = httpx.get(f"https://r.jina.ai/{query}", timeout=60)
        return [{"title": "Full page", "url": query, 
                 "content": response.text[:5000],  # أول 5000 حرف
                 "date": "now", "credibility_hint": "full_page"}]

def extract_keywords(query: str, llm_client) -> list[str]:
    """
    Stolen from: SAGE finding (BM25 > LLM retrievers when queries are precise)
    Forces keyword extraction before search
    """
    response = llm_client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=[{
            "role": "user",
            "content": f"Extract 3-5 precise search keywords from: '{query}'\nReturn JSON: {{\"keywords\": [\"kw1\", \"kw2\"]}}"
        }],
        max_tokens=100
    )
    # parse and return keywords
```

---

#### الطبقة 2 — Agent Template Layer (3 أيام)
**ما نبنيه:** إضافة snippet في `META_AGENT_PROMPT` في `orchestrator.py`

```python
# Stolen from: DeepResearcher (reasoning-before-action) + WebThinker (think-search-draft)
WEB_SEARCH_SNIPPET = """
AVAILABLE TOOLS (use when task requires real-world information):

```python
# Tool 1: Quick web search (use for: facts, platforms, prices, availability)
from genesis.tools.web_search import web_search
results = web_search("your query here", mode="quick")
# Returns: [{title, url, snippet, date, credibility_hint}]

# Tool 2: Deep search with page content
results = web_search("your query here", mode="deep") 

# Tool 3: Read a specific URL fully
page = web_search("https://specific-url.com", mode="read")
```

SEARCH STRATEGY (stolen from WebThinker):
1. Think first: what do I need to know? What am I uncertain about?
2. Extract keywords before searching (stolen from SAGE finding)
3. Search with multiple queries for same sub-goal (stolen from DeepResearcher)
4. Start drafting while searching — don't wait for all info
5. For each claim: cite the source URL and date
6. If source not found: write "UNVERIFIED — needs manual check"

EVIDENCE TRACKING (stolen from Rulers):
For each important claim in your output, track:
{
  "claim": "Appen is available in Egypt",
  "source_url": "https://reddit.com/...",
  "source_date": "2026-03-15",
  "confidence": "HIGH/MEDIUM/LOW/UNVERIFIED"
}
Save this as evidence_log.json in WORKING_DIR
"""
```

---

#### الطبقة 3 — Evaluation Layer (أسبوع)
**ما نبنيه:** `genesis/open_task_evaluator.py`

```python
# Stolen from: Rulers (schema-constrained) + InfoDeepSeek (IA@5 metric) + LLM-as-Judge best practices

class OpenTaskEvaluator:
    """
    Runs when no evaluate.py exists.
    Produces unified score for Regime Detector.
    """
    
    def evaluate(self, output_path: str, task_md: str, evidence_log: dict) -> dict:
        """
        Returns:
        {
          "output_score": 0-100,    # جودة الـ output النهائي
          "evidence_score": 0-100,  # جودة الـ evidence المجمّعة (IA@5 مُلهم)
          "hallucination_rate": 0-1, # نسبة الادعاءات غير الموثّقة
          "checklist": [{
              "criterion": "نص المعيار",
              "met": True/False,
              "evidence_quote": "النص الفعلي من الـ output",
              "source_url": "رابط المصدر أو null"
          }],
          "overall_score": 0-100    # weighted average → يدخل Regime Detector
        }
        """
        # يُجبر الـ judge على إنتاج structured object (Rulers)
        # يقيس evidence_score مستقلاً (InfoDeepSeek IA@5)
        # يُحسب hallucination_rate = claims بدون source / total claims
```

---

#### الطبقة 4 — Goal Specification Layer (أسبوعين)
**ما نبنيه:** `genesis/goal_specification.py` + Section 0 في orchestrator

```python
# Stolen from: MA-RAG (Planner/Step Definer) + Enterprise Deep Research (task annotation)
# + HTN planning (hierarchical decomposition)

class GoalSpecification:
    """
    Section 0: قبل Meta-Agent
    Decomposes task into hierarchical goal structure
    """
    
    def decompose(self, task_md: str) -> dict:
        """
        Returns goal_spec.json:
        {
          "primary_goal": "...",
          "success_criteria": ["معيار 1", "معيار 2"],
          "priority_order": ["الأهم أولاً", "ثم..."],
          "scope": "global",  # أو "local: Egypt"
          "sub_goals": [
            {
              "id": "sg1",
              "description": "...",
              "priority": 1,  # 1=أعلى
              "search_queries": ["query1", "query2"],  # Step Definer
              "keywords": ["kw1", "kw2"],  # SAGE improvement
              "success_criteria": "...",
              "domain": "web/academic/forum/social"
            }
          ]
        }
        """
        # MA-RAG Planner pattern
        # HTN decomposition principle
```

---

## جدول السرقات الكاملة

| # | الورقة | arXiv | العنصر المسروق | يُطبَّق في | الأثر المتوقع |
|---|--------|-------|----------------|------------|---------------|
| 1 | DeepResearcher | 2504.03160 | Tool call format + short-term memory + reasoning-before-action | Web Search Tool + Agent Template | ✅ بحث حقيقي في الـ agent |
| 2 | Search-R1 | COLM 2025 | Search token masking + reward structure | Regime Detector signal | ✅ لا يُعاقب على البحث المفيد |
| 3 | WebThinker | NeurIPS 2025 | Think-Search-Draft loop | META_AGENT_PROMPT | ✅ تقارير أكثر تماسكاً |
| 4 | A-RAG | 2602.03442 | 3-level search tools | Web Search Tool | ✅ balance بين سرعة وعمق |
| 5 | Rulers | 2601.08654 | Schema-constrained judge + evidence quotes | LLM-as-Judge | ✅ لا hallucination في التقييم |
| 6 | MA-RAG | 2505.20096 | Planner/Step Definer architecture | Goal Spec Layer | ✅ sub-goals محددة بدقة |
| 7 | InfoDeepSeek | 2505.15872 | IA@5 metric (evidence independent of output) | Evidence Audit | ✅ يقيس جودة البحث مستقلاً |
| 8 | SAGE | 2602.05975 | BM25 > LLM retrievers + keyword extraction | Search Planning | ✅ +30% retrieval accuracy |

---

## ما لا نسرقه (ولماذا)

| العنصر | السبب |
|--------|-------|
| RL Training (Search-R1, DeepResearcher) | يحتاج GPU + training data + أسابيع — خارج نطاقنا |
| Browser automation (Manus, Grok) | latency عالي + تعقيد — مش مناسب للـ free tier |
| Full HyperGraph Memory (HGMem) | overkill — short-term memory كافي لحالتنا |
| Multimodal search (WebWatcher) | GENESIS مش multimodal بعد |

---

## ترتيب التنفيذ الفعلي

```
Week 1:
  Day 1-2: genesis/tools/web_search.py (Serper API + Jina)
  Day 3-4: إضافة WEB_SEARCH_SNIPPET للـ META_AGENT_PROMPT
  Day 5-7: تشغيل micro_task مرة تانية — قارن مع Gen 1

Week 2:
  Day 1-4: genesis/open_task_evaluator.py (Rulers + InfoDeepSeek)
  Day 5-7: ربط الـ evaluator بـ Section 5a.1 + Regime Detector

Week 3-4:
  genesis/goal_specification.py (MA-RAG + HTN)
  Section 0 في orchestrator
  ربط goal_spec.json بكل section

Week 5:
  Enhanced Pipeline توصيل (LadderAscent → feedback)
  Evidence Coverage Report
  Push + tests
```
