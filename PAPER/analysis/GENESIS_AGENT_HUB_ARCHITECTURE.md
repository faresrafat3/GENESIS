# GENESIS Agent Hub — البنية الأولية الكاملة
# تاريخ: 2026-06-08
# بحث عميق في: BDI، SOUL.md، MCP، MAGMA، MemGPT، OpenClaw
# هذا الملف = المرجع الرئيسي لكل تطوير الـ Agent Hub

---

## لماذا نبدأ بالـ Agent Hub وليس Skills أو Meta؟

لأن الـ Agent Hub = **الهيكل الذي تجلس عليه كل شيء آخر:**

```
Skills       → تُحفظ في agent.skills[]
Memory       → تُدار بواسطة agent.memory
Soul         → يُحكم agent.soul كل قرار
Tools        → تُستدعى من agent.tool_hub
Meta Engine  → يُحلّل agent.trajectory
```

بدون Agent Hub = Skills وMemory وMeta كلها تطير في الفراغ.

---

## المصادر الرئيسية والاكتشافات

### 1. SOUL.md (OpenClaw — 2026 Industry Standard)
```
soul.md   = Constitution (Non-Negotiable Rules) — لا يتغير مع كل task
           = Trust boundaries + tool permissions + cost guardrails + memory rules
           ≠ personality fluff — ده control plane حقيقي

user.md   = Human Profile + Working Contract
agents.md = Task instructions + operational rules
tools.md  = Available tools guide
memory.md = Curated durable facts (صغيرة ومنظمة)
identity.md = Name + role + routing metadata

المبدأ الذهبي: "إذا تغيّر soul.md كثيراً — الـ system لا يملك stable identity"
```

### 2. BDI Model (Classical AI → LLM Integration)
```
B = Beliefs  → ما يعرفه الـ agent (Memory: episodic + semantic)
D = Desires  → ما يريده (Goal Contract من INTENT ENGINE)
I = Intentions → ما التزم بفعله (current plan + action sequence)

BDI في GENESIS:
  B (Beliefs)    → research_memory + context.md + evidence_log
  D (Desires)    → goal_spec.json (من INTENT ENGINE)
  I (Intentions) → target_agent.py (الـ code هو الـ intention!)
```

### 3. Memory Architecture (MAGMA + MemGPT + MemoryOS)
```
أفضل بنية 2026 = 4 أنواع منفصلة:

Working Memory    → Context window (current task)
Episodic Memory   → Past experiences (timestamped)
Semantic Memory   → Extracted facts (atemporal)
Procedural Memory → How-to knowledge (= Skills!)

MAGMA (أعلى أداء 0.70 على LoCoMo):
  4 graphs: semantic + temporal + causal + entity
  intent-guided subgraph traversal
  multi-hop temporal reasoning

MemGPT/Letta:
  LLM = OS
  Working Memory = RAM (context window)
  External Storage = Disk (SQLite/vector DB)
  Function calls لإدارة الانتقال بين الطبقات
```

### 4. Tool Hub (MCP — Model Context Protocol)
```
MCP = "USB-C for AI tools" — المعيار الصناعي 2026
  - Dynamic tool discovery (لا static hardcoding)
  - JSON-RPC 2.0 protocol
  - Server Cards (.well-known URL)
  - OAuth 2.1 authentication
  - 97M+ monthly downloads، 200+ servers

الفرق المهم:
  Tools = execute + return results
  Skills = prepare agent + inject procedural knowledge

Tool Hub في GENESIS:
  - web_search (Serper + Jina) ← موجود
  - code_executor (sandbox) ← موجود (venv)
  - file_system (read/write) ← موجود
  - llm_call (OpenRouter pool) ← موجود (api_key_pool)
  - skill_retrieve ← جديد (Skill Engine)
  - memory_read/write ← جديد (Memory Engine)
```

---

## الـ Agent Hub Architecture — البنية الكاملة

### الفلسفة الأساسية

```
Agent = Soul + Memory + Tools + Skills
      (ما هو) + (ما يعرف) + (ما يفعل) + (كيف يفعل)

الفصل المقدس:
  Soul  ← لا يتغير إلا عمداً
  Memory ← تتطور مع كل تجربة
  Tools  ← تُستدعى من Hub (لا مدمجة في الـ agent)
  Skills ← تُستخرج من successes وتُعاد استخدامها
```

### بنية الملفات

```
genesis/agent_hub/
├── __init__.py
├── agent.py              ← AgentSpec (الكيان الكامل)
├── soul.py               ← AgentSoul (identity + values + constitution)
├── memory/
│   ├── __init__.py
│   ├── manager.py        ← AgentMemoryManager (orchestrates all types)
│   ├── working.py        ← WorkingMemory (context window management)
│   ├── episodic.py       ← EpisodicMemory (timestamped experiences)
│   ├── semantic.py       ← SemanticMemory (extracted facts)
│   └── procedural.py     ← ProceduralMemory (← Skill Library bridge)
├── tool_hub/
│   ├── __init__.py
│   ├── registry.py       ← ToolRegistry (dynamic discovery)
│   ├── tool.py           ← ToolSpec (contract per tool)
│   └── tools/
│       ├── web_search.py  ← wraps genesis/tools/web_search.py
│       ├── code_exec.py   ← sandbox execution
│       ├── file_system.py ← read/write
│       ├── llm_call.py    ← OpenRouter pool wrapper
│       └── skill_use.py   ← Skill Library interface
└── registry.py           ← AgentRegistry (CRUD + discovery)
```

---

## Section 1: SOUL — الهوية والقيم

### ما نسرقه بالكامل

```
من OpenClaw SOUL.md معيار:
  soul.md   = Constitution (non-negotiable)
  identity.md = External presentation

من BDI Architecture (arXiv:2512.09458):
  BDI → Beliefs + Desires + Intentions
  commitment strategies (لا تُعيد التخطيط مع كل خطوة)
  intention revision (فقط عند تغيّر الظروف)

من arXiv:2604.23280 (Agent Identity):
  confidence score (ليس binary credential)
  behavioral consistency tracking
  provenance + justification chains
```

### AgentSoul — التصميم

```python
# genesis/agent_hub/soul.py

@dataclass
class AgentSoul:
    """
    مسروق من: OpenClaw SOUL.md معيار + BDI Architecture
    
    Soul = Constitution (Non-Negotiable)
    لا تتغير إلا بقرار واعٍ من المطور
    """
    
    # IDENTITY (من identity.md)
    name: str                    # "GENESIS-Research-Agent"
    role: str                    # "Strategic Research Analyst"
    version: str                 # "1.0.0"
    
    # VALUES (من soul.md — core)
    core_values: list[str] = field(default_factory=lambda: [
        "accuracy_over_speed",
        "cite_sources_always",
        "admit_uncertainty_explicitly",
        "global_before_local",  # هام لـ micro_task bias
    ])
    
    # CONSTITUTION (trust boundaries)
    trust_boundaries: list[str] = field(default_factory=lambda: [
        "never_fabricate_links",
        "never_auto_write_soul",  # OpenClaw security principle
        "always_sandbox_code",
        "require_approval_for_external_writes",
    ])
    
    # COST GUARDRAILS (من soul.md)
    max_llm_calls_per_task: int = 20
    max_web_searches_per_task: int = 15
    max_cost_usd_per_task: float = 1.0
    
    # MEMORY RULES (من soul.md)
    memory_rules: list[str] = field(default_factory=lambda: [
        "expire_episodic_after_30_days",
        "validate_facts_before_storing",
        "never_store_secrets_in_memory",
    ])
    
    # BEHAVIORAL CONSISTENCY (BDI: commitment strategies)
    commitment_strategy: str = "stable"  # stable | adaptive | aggressive
    replanning_trigger: str = "regime_change"  # when to replan
    
    # SOUL FILE (Anthropic format)
    soul_md: str = ""  # the full SOUL.md content
    
    def to_soul_md(self) -> str:
        """Generate SOUL.md format for injection into agent prompt"""
        
    def validate_action(self, action: str) -> tuple[bool, str]:
        """BDI: adoption filter — is this action within constitution?"""
        
    def check_trust(self, source: str) -> float:
        """confidence score (0-1) for a data source"""
        
    @classmethod
    def load(cls, soul_md_path: str) -> "AgentSoul":
        """Load from SOUL.md file"""
        
    def save(self, path: str) -> None:
        """Save as SOUL.md"""

# الـ Soul Files في genesis/agent_hub/souls/
# SOUL.md format:
"""
---
name: GENESIS-Research-Agent
role: Strategic Research Analyst
version: 1.0.0
---

## Identity
You are GENESIS, a precise research agent that finds actionable information.

## Core Values
- Accuracy over speed: verify before stating
- Always cite sources: every claim needs a URL or "UNVERIFIED"
- Admit uncertainty: say "unknown" not "probably"
- Global before local: search globally, then filter by region

## Constitution (Non-Negotiable)
- Never fabricate URLs or links
- Never auto-modify soul.md
- Always run code in sandbox
- Require approval for writes to external systems

## Cost Guardrails
- Max 20 LLM calls per task
- Max 15 web searches per task
- Max $1.00 per task

## Memory Rules
- Expire episodic memories after 30 days
- Validate facts before storing in semantic memory
- Never store API keys or secrets
"""
```

### Artifact: soul.md per agent

```
genesis/agent_hub/souls/
├── research_agent.soul.md      ← الـ agent الحالي
├── coding_agent.soul.md        ← لو بنيناه
└── analysis_agent.soul.md      ← لو بنيناه
```

---

## Section 2: MEMORY — الذاكرة الكاملة

### ما نسرقه بالكامل

```
من MAGMA (arXiv:2601.03236 — أفضل أداء 2026):
  4 subgraphs: semantic + temporal + causal + entity
  intent-guided subgraph traversal
  cross-graph traversal للـ multi-hop questions

من MemGPT/Letta (arXiv:2310.08560):
  LLM = OS metaphor
  Working Memory = RAM (context window)
  External = Disk (SQLite)
  Function calls: memory_read(), memory_write(), memory_search()

من MemoryOS (arXiv:2506.06326):
  STM → MTM → LPM hierarchy
  heat-based eviction (يطرد الأقل استخداماً)
  persona module (behavioral consistency)

من BDI Architecture:
  Beliefs = episodic + semantic
  provenance tracking per belief
  conflict resolution
```

### AgentMemory — التصميم

```python
# genesis/agent_hub/memory/manager.py

class AgentMemoryManager:
    """
    مسروق من: MAGMA (graph structure) + MemGPT (OS metaphor) + MemoryOS (hierarchy)
    
    4 Memory Types — مفصولة تماماً:
    """
    
    working: WorkingMemory      # RAM — context window manager
    episodic: EpisodicMemory    # Disk — past experiences (timestamped)
    semantic: SemanticMemory    # Disk — extracted facts (atemporal)
    procedural: ProceduralMemory # Disk — how-to (= Skill Library bridge)
    
    def read(self, query: str, memory_type: str = "all") -> MemoryResult
    def write(self, content: str, memory_type: str, metadata: dict) -> None
    def search(self, query: str, intent: str) -> list[MemoryItem]
    def consolidate(self) -> None  # episodic → semantic (nightly)
    def evict(self) -> None        # heat-based eviction (MemoryOS)


# genesis/agent_hub/memory/working.py
class WorkingMemory:
    """
    Context window manager
    مسروق من: MemGPT paging system
    """
    max_tokens: int = 8000
    current_items: list[MemoryItem]
    
    def add(self, item: MemoryItem) -> None
    def evict_oldest(self) -> None      # FIFO + heat score
    def get_context(self) -> str        # للـ LLM prompt
    def page_out(self, item) -> None    # → episodic


# genesis/agent_hub/memory/episodic.py
class EpisodicMemory:
    """
    Past experiences — timestamped
    مسروق من: MAGMA temporal subgraph + Generative Agents
    """
    db: SQLite                          # timestamped events
    
    def store(self, event: str, context: dict, timestamp: datetime) -> None
    def retrieve(self, query: str, time_range: tuple = None) -> list[Episode]
    def consolidate_to_semantic(self) -> None  # periodic
    def expire(self, max_age_days: int = 30) -> None  # memory rule


# genesis/agent_hub/memory/semantic.py
class SemanticMemory:
    """
    Extracted facts — atemporal
    مسروق من: MAGMA semantic subgraph + A-MEM (Zettelkasten)
    """
    db: SQLite + vector_index           # facts + embeddings
    
    def store(self, fact: str, source: str, confidence: float) -> None
    def search(self, query: str) -> list[Fact]
    def update(self, fact_id: str, new_value: str) -> None
    def delete(self, fact_id: str) -> None
    def resolve_conflict(self, fact_a: Fact, fact_b: Fact) -> Fact


# genesis/agent_hub/memory/procedural.py
class ProceduralMemory:
    """
    How-to knowledge = Skill Library bridge
    مسروق من: Voyager + MUSE-Autoskill
    """
    skill_library: SkillLibrary        # reference to PILLAR 1
    
    def retrieve_skill(self, task_type: str) -> list[Skill]
    def store_skill(self, skill: Skill) -> None
    def execute_skill(self, skill_name: str, context: dict) -> Any
```

### Artifact: memory files per agent

```
genesis/agent_hub/memories/
└── research_agent/
    ├── episodic.db        ← SQLite (timestamped events)
    ├── semantic.db        ← SQLite + vector index
    └── working_state.json ← current context window state
```

---

## Section 3: TOOL HUB — الأدوات المنفصلة

### الفلسفة الأساسية

```
Tools ≠ مدمجة في الـ agent code
Tools = كيانات مستقلة في Hub → الـ agent يستدعيها

المصدر:
  MCP (Model Context Protocol) — معيار 2026
  "USB-C for AI tools"
  Dynamic discovery — لا static hardcoding
  Tool = contract: input schema + output schema + execution
```

### ToolSpec — التصميم

```python
# genesis/agent_hub/tool_hub/tool.py

@dataclass
class ToolSpec:
    """
    مسروق من: MCP Tool specification + SkillOps contract (P,O,A,V,F)
    """
    # Identity
    name: str               # "web_search"
    description: str        # للـ agent (progressive disclosure)
    version: str            # "1.0.0"
    
    # Contract (SkillOps inspired)
    input_schema: dict      # JSON Schema
    output_schema: dict     # JSON Schema
    preconditions: list[str]
    postconditions: list[str]
    failure_modes: list[str]
    
    # Execution
    executor: callable      # الـ function الفعلية
    requires_sandbox: bool = False
    requires_approval: bool = False
    
    # Cost
    cost_per_call_usd: float = 0.0
    rate_limit_per_min: int = 60
    
    # MCP-style metadata
    server_url: str = ""    # لو external MCP server
    auth_required: bool = False


# genesis/agent_hub/tool_hub/registry.py
class ToolRegistry:
    """
    مسروق من: MCP Server dynamic discovery
    """
    tools: dict[str, ToolSpec]
    
    def register(self, tool: ToolSpec) -> None
    def discover(self) -> list[ToolSpec]    # MCP: query at runtime
    def get(self, name: str) -> ToolSpec
    def get_catalog(self) -> str            # للـ agent system prompt
    def invoke(self, name: str, args: dict) -> ToolResult
    def get_by_capability(self, capability: str) -> list[ToolSpec]
```

### الأدوات الموجودة → تُنقل للـ Hub

```python
# genesis/agent_hub/tool_hub/tools/web_search.py
# يُغلّف genesis/tools/web_search.py
WEB_SEARCH_TOOL = ToolSpec(
    name="web_search",
    description="Search web for real-time information. Use for: facts, platform availability, payment proofs",
    input_schema={"query": "str", "mode": "quick|deep|read"},
    output_schema={"results": "list[SearchResult]", "evidence_log": "EvidenceLog"},
    preconditions=["SERPER_API_KEY available"],
    failure_modes=["rate_limit → retry", "no_results → broaden_query"],
    executor=web_search,
    cost_per_call_usd=0.001,
    rate_limit_per_min=30,
)

# genesis/agent_hub/tool_hub/tools/llm_call.py
# يُغلّف genesis/util.py + tools/api_key_pool.py
LLM_CALL_TOOL = ToolSpec(
    name="llm_call",
    description="Call LLM with automatic key rotation",
    input_schema={"messages": "list", "model": "str", "max_tokens": "int"},
    output_schema={"content": "str", "usage": "dict"},
    executor=make_openai_client,
    cost_per_call_usd=0.0,  # free tier
)

# genesis/agent_hub/tool_hub/tools/skill_use.py  [NEW]
# يُغلّف Skill Library
SKILL_USE_TOOL = ToolSpec(
    name="skill_use",
    description="Retrieve and execute a proven skill from the skill library",
    input_schema={"skill_name": "str", "context": "dict"},
    output_schema={"result": "any", "skill_used": "str"},
    executor=skill_library.execute_skill,
)
```

### Tool Catalog في Agent Prompt

```yaml
# Progressive Disclosure (MCP style):
# Level 1: catalog (minimal tokens) → inject at startup
# Level 2: full spec → inject on demand

AVAILABLE TOOLS:
  web_search: Search web for real-time information [cost: ~$0.001/call]
  code_exec: Run Python code in sandbox [requires_sandbox: true]
  skill_use: Use proven skill from library [free]
  memory_read: Read from agent memory [free]
  llm_call: Call secondary LLM [free tier]
```

---

## Section 4: AGENT SPECIFICATION — الكيان الكامل

### AgentSpec — التصميم الكامل

```python
# genesis/agent_hub/agent.py

@dataclass
class AgentSpec:
    """
    الكيان الكامل = Soul + Memory + Tools + Skills + BDI state
    JSON-serializable لـ:
      - REST API (AgentRegistry)
      - Vibe Web interface (المستقبل)
      - Multi-agent coordination (A2A protocol)
    """
    
    # IDENTITY
    id: str                          # UUID
    name: str
    version: str
    created_at: datetime
    
    # SOUL (Section 1)
    soul: AgentSoul
    soul_md_path: str               # path to SOUL.md file
    
    # MEMORY (Section 2)  
    memory_config: MemoryConfig     # what types, what limits
    memory_dir: str                 # where to store memory files
    
    # TOOLS (Section 3)
    tool_names: list[str]           # tools from ToolRegistry
    tool_permissions: dict[str, list[str]]  # which tools can do what
    
    # SKILLS (from Skill Engine)
    skill_names: list[str]          # skills from SkillLibrary
    
    # BDI STATE (runtime, not persisted)
    beliefs: dict = field(default_factory=dict)     # current facts
    desires: list[str] = field(default_factory=list) # current goals
    intentions: list[str] = field(default_factory=list) # current plan
    
    # COGNITIVE PIPELINE (Virtual GENESIS)
    pipeline_config: dict = field(default_factory=lambda: {
        "use_semantic_verification": True,
        "use_value_computation": True,
        "use_ladder_tracking": True,
        "use_theory_testing": True,
    })
    
    # TRAJECTORY (Meta Engine)
    run_history: list[str] = field(default_factory=list)  # run IDs
    
    def to_system_prompt(self) -> str:
        """Build complete system prompt from soul + tools + skills catalog"""
        
    def to_dict(self) -> dict:
        """JSON-serializable (for REST + vibe web)"""
        
    def validate(self) -> list[str]:
        """Validate agent spec — returns list of issues"""
        
    @classmethod
    def load(cls, path: str) -> "AgentSpec"
    
    def save(self, path: str) -> None


# genesis/agent_hub/registry.py
class AgentRegistry:
    """
    CRUD للـ agents
    Foundation للـ vibe web drag-and-drop (المستقبل)
    مسروق من: MCP Server Cards (.well-known)
    """
    
    db: SQLite
    agents_dir: Path               # filesystem storage
    
    def create(self, spec: AgentSpec) -> str           # → agent ID
    def read(self, agent_id: str) -> AgentSpec
    def update(self, agent_id: str, spec: AgentSpec) -> None
    def delete(self, agent_id: str) -> None
    def list(self, filter: dict = None) -> list[AgentSpec]
    def discover(self) -> dict                          # MCP Agent Card format
    def get_catalog(self) -> list[dict]                 # minimal metadata
```

---

## Section 5: Artifact Architecture — كل الـ Files وشكلها

### مبدأ التصميم

```
كل artifact عنده:
  schema_version  → backward compatibility
  created_by      → أي section أنتجه
  consumed_by     → من يقرأه
  lifecycle       → per_agent | per_run | per_gen | persistent
  format          → JSON | YAML | MD | DB | SQLite
```

### الـ Artifacts الكاملة للـ Agent Hub

```
genesis/agent_hub/
├── souls/
│   └── research_agent.soul.md       [lifecycle: persistent, consumed_by: all]
├── memories/
│   └── {agent_id}/
│       ├── episodic.db              [lifecycle: persistent, grows with use]
│       ├── semantic.db              [lifecycle: persistent]
│       └── working_state.json       [lifecycle: per_session]
├── tool_hub/
│   └── tool_registry.json           [lifecycle: persistent, auto-generated]
├── skills/                          [← Skill Engine artifacts]
│   ├── skill_catalog.yaml           [consumed_by: META_AGENT_PROMPT]
│   └── {skill_name}/
│       ├── SKILL.md
│       ├── scripts/
│       ├── tests/
│       └── .memory.md
└── registry.db                      [lifecycle: persistent, AgentRegistry]

# SOUL.md Schema (Agent Identity File)
---
schema_version: "1.0"
created_by: developer (or meta_optimizer in future)
consumed_by: [META_AGENT, FEEDBACK_AGENT, TARGET_AGENT]
lifecycle: persistent
format: Markdown + YAML frontmatter
---

# AgentSpec Schema (JSON)
{
  "schema_version": "1.0",
  "created_by": "AgentRegistry",
  "consumed_by": ["orchestrator", "meta_optimizer", "vibe_web"],
  "lifecycle": "persistent",
  "format": "JSON"
}

# ToolRegistry Schema (JSON)
{
  "schema_version": "1.0",
  "created_by": "ToolRegistry (auto-discovered)",
  "consumed_by": ["TARGET_AGENT", "META_AGENT"],
  "lifecycle": "persistent",
  "format": "JSON"
}
```

---

## Integration مع الـ Main Loop

### أين يدخل Agent Hub في orchestrator.py

```python
# Section 0 (قبل Goal Spec):
from genesis.agent_hub import AgentRegistry, ToolRegistry
from genesis.agent_hub.soul import AgentSoul

# Load or create agent spec for this run
agent_registry = AgentRegistry()
if agent_id:
    agent_spec = agent_registry.read(agent_id)
else:
    agent_spec = AgentSpec.from_task(task_name, soul_path="souls/research_agent.soul.md")

# Load soul → inject in META_AGENT_PROMPT
soul_section = agent_spec.soul.to_soul_md()

# Load tool catalog → inject in META_AGENT_PROMPT  
tool_catalog = ToolRegistry().get_catalog()

# Section 3 (Prompts):
META_AGENT_PROMPT = soul_section + "\n" + tool_catalog + "\n" + META_AGENT_PROMPT

# Section 5b (Feedback):
# Update agent beliefs based on gen results (BDI update)
agent_spec.beliefs["last_gen_score"] = overall_score
agent_spec.beliefs["hallucination_rate"] = hallucination_rate
agent_registry.update(agent_id, agent_spec)
```

---

## فحص المصداقية — هل نسرق صح؟

### ما نأخذه حرفياً (وده ميزة):

| من المشروع | ما نأخذه حرفياً | ملف في GENESIS |
|-----------|----------------|----------------|
| OpenClaw SOUL.md format | الـ file structure + 5 sections | `souls/*.soul.md` |
| Anthropic SKILL.md format | الـ directory structure بالكامل | `skills/*/SKILL.md` |
| MCP Tool Spec | input/output schema + discovery | `tool_hub/registry.py` |
| MemGPT paging | working_memory → episodic paging | `memory/working.py` |
| MAGMA 4-graph | semantic+temporal+causal+entity | `memory/semantic.py` |
| BDI commitment | stable intentions, revision only on trigger | `agent.py` |

### ما يختلف في GENESIS:

```
1. SOUL.md في GENESIS محتواه مختلف:
   - يُحدَّد تلقائياً من task_type
   - يُضمّن Goal Contract (من INTENT ENGINE)
   - constitution يشمل: "global_before_local" (bias fix)

2. Memory في GENESIS:
   - Procedural Memory = Skill Library (مش Voyager JavaScript skills)
   - Episodic = Gen history (مش conversation history)
   - Working = Context Window per generation (مش per conversation)

3. Tool Hub في GENESIS:
   - Tools تُستدعى بـ Python function (مش JSON-RPC)
   - MCP protocol = inspiration للـ design (مش implementation)
   - Tool cost tracking يذهب لـ Safety Monitor

4. AgentSpec في GENESIS:
   - يُولَّد تلقائياً من task.md + soul.md
   - BDI beliefs = evaluation results (مش world state)
   - BDI intentions = target_agent.py (الـ code هو الـ intention)
```

---

## خطة التنفيذ — بالترتيب

### Week 1: Soul Layer
```
genesis/agent_hub/soul.py        ← AgentSoul dataclass
genesis/agent_hub/souls/          ← soul.md files
tests/test_agent_soul.py         ← 30+ tests
Integration: soul_section → META_AGENT_PROMPT
```

### Week 2: Tool Hub
```
genesis/agent_hub/tool_hub/tool.py     ← ToolSpec
genesis/agent_hub/tool_hub/registry.py ← ToolRegistry
genesis/agent_hub/tool_hub/tools/      ← wrap existing tools
tests/test_tool_hub.py                ← 30+ tests
Integration: tool_catalog → META_AGENT_PROMPT
```

### Week 3: Memory Layer (Working + Episodic)
```
genesis/agent_hub/memory/working.py    ← WorkingMemory
genesis/agent_hub/memory/episodic.py   ← EpisodicMemory
genesis/agent_hub/memory/manager.py    ← AgentMemoryManager
tests/test_agent_memory.py            ← 40+ tests
```

### Week 4: Memory Layer (Semantic + Procedural)
```
genesis/agent_hub/memory/semantic.py   ← SemanticMemory
genesis/agent_hub/memory/procedural.py ← ProceduralMemory (Skill bridge)
Integration: memory_read/write في TARGET_AGENT template
```

### Week 5: AgentSpec + Registry
```
genesis/agent_hub/agent.py            ← AgentSpec
genesis/agent_hub/registry.py         ← AgentRegistry
tests/test_agent_hub.py               ← 40+ tests
Integration: orchestrator Section 0
```

### Week 6: Integration + Tests
```
Full integration في orchestrator
Artifact schemas (schema_version في كل JSON)
End-to-end test: micro_task run مع Agent Hub
```

---

## الـ Vibe Web Foundation (المستقبل)

```
كل ما نبنيه الآن = يدعم vibe web drag-and-drop:

AgentSpec → JSON-serializable → REST API endpoint
AgentRegistry → قائمة agents → يُعرض في UI كـ cards
ToolRegistry → قائمة tools → drag-and-drop للـ agent
SkillLibrary → قائمة skills → assign للـ agent
SoulMd → editable في UI
MemoryManager → visualizable في UI

Backend APIs المطلوبة (في المستقبل):
  GET  /agents                     ← list all agents
  POST /agents                     ← create agent
  GET  /agents/{id}               ← get agent
  PUT  /agents/{id}               ← update agent
  GET  /agents/{id}/soul          ← get soul.md
  GET  /agents/{id}/memory        ← memory stats
  GET  /tools                     ← tool catalog
  GET  /skills                    ← skill catalog
  POST /runs                      ← start run with agent_id
```
