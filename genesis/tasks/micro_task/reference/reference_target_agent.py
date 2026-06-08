#!/usr/bin/env python3
"""
Reference Target Agent for Micro-Task Economy Research Task.
Performs web research and produces a structured report on micro-task opportunities.
Uses OpenAI-compatible API (OpenRouter by default).
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx
import openai

# ─── Config ───────────────────────────────────────────────────────────────────
MODEL_NAME = os.getenv("TASK_MODEL") or "google/gemini-2.5-flash-preview-05-20:free"
RESULTS_DIR = Path("results")
REPORT_FILE = RESULTS_DIR / "micro_task_report.md"

# ─── OpenAI client ────────────────────────────────────────────────────────────
def setup_client() -> openai.OpenAI:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY or LLM_API_KEY.")
    base_url = (
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("OPENAI_API_BASE")
        or "https://openrouter.ai/api/v1"
    )
    http_client = httpx.Client(headers={"Accept-Encoding": "identity"}, timeout=300.0)
    return openai.OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)


# ─── The research prompt ──────────────────────────────────────────────────────
RESEARCH_PROMPT = """
أنت باحث ومحلل استراتيجي محترف في اقتصاد المهام الصغيرة (Micro-Task Economy). دورك ثلاثي: (1) صياد فرص حالية مؤكدة، (2) محلل مصداقية صارم، (3) متنبئ بفرص مستقبلية لم يدخلها الذكاء الاصطناعي بقوة. المجال: مهام تدفع 1-5 دولار، متاحة عالمياً بما في ذلك مصر، بدون خبرة عميقة، وبدون حيل IP أو VPN.

---

### الجزء الأول: صيد الفرص الحالية

**1. وصف الفرص المستهدفة:**

*   نظام المهمة: "أول من يقدم = يكسب" أو "مهام روتينية سريعة".

*   القيمة: 1-5 دولار للمهمة.

*   الطبيعة: اصطياد أخطاء ترجمة/إملائية، مسابقات أسماء، شعارات، تسجيلات صوتية، تقييم نتائج، تدريب AI، كتابة أسئلة وأجوبة.

*   الصنف: مهام "فورية" (تبدأ فوراً) أو "بعد قبول" (تحتاج اختبار بسيط).

*   **متاحة من مصر بدون VPN:** يجب التحقق من ذلك صراحة.

**2. استراتيجية البحث (X تويتر هو المصدر الرئيسي):**

*   **هاشتاجات وعبارات بحث على X:**

    `#MicroTasks`, `#BeerMoney`, `#MakeMoneyOnline`, `#SideHustle`, `#عمل_من_المنزل`, `#ربح_من_الإنترنت`, `#BugBounty`, `#NamingContest`, `مطلوب مهام`, `مطلوب مهام صوتية`, `مطلوب مترجمين`, `مطلوب مدققين`.

*   **حسابات معروفة للمتابعة والبحث في تغريداتها:** (اطلب مني البحث في تغريدات حسابات مثل: @microtaskers، @beermoneyforum، @RatRaceRebellion، وأي حسابات عربية ناشطة في المجال).

*   **ابحث أيضاً في:** Reddit (r/beermoney, r/WorkOnline, r/WorkFromHome)، منتديات عربية (مثل موقع "أعمال"، "محترفي الربح")، منصات: Freelancer.com، uTest، Appen، OneForma، Neevo، Clickworker.

*   **ابحث في LinkedIn:** منشورات حديثة بكلمات: "hiring micro taskers", "paid testing", "مطلوب مهام".

*   **ابحث في Product Hunt:** أدوات جديدة تم إطلاقها مؤخراً (آخر 30 يوم) وابحث عن إشارات لوجود برامج "Beta Testing" مدفوعة.

*   **ابحث في Discord:** سيرفرات عامة لشركات AI ناشئة (مثل Midjourney، OpenAI Community، إلخ) حيث يطلبون أحياناً مختبرين.

**3. التحقق من المصداقية (صارم جداً):**

*   ابحث عن دليل دفع واحد على الأقل: صورة إثبات دفع، تغريدة تأكيد، تعليق على Reddit، فيديو على YouTube. اذكر الرابط.

*   ابحث عن "اسم المنصة + scam" أو "اسم المنصة + review" أو "اسم المنصة + مصر".

   *قاعدة ذهبية لتجنب الاحتيال:* *أي منصة تطلب منك دفع رسوم تسجيل = احتيال.**

*   ضع علامة: (✅ مؤكدة) أو (⚠️ غير مؤكدة – تحتاج تحقق يدوي).

---

### الجزء الثاني: التنبؤ بالفرص المستقبلية (الطلب أعلى من العرض)

**1. تحليل نقاط ضعف الذكاء الاصطناعي الحالي (ثغرات لم يدخلها بقوة):**

*   اذكر 3 مجالات محددة لا يزال البشر يتفوقون فيها على AI في هذه اللحظة (مثال: فهم السخرية باللهجات العامية، اكتشاف "الكذبة البصرية" في فيديو غير مفبرك، تقييم كوميديا الموقف، كتابة زجل أو شعر بالعامية، تحليل نبرة الصوت العاطفية المعقدة).

**2. البحث عن "إشارات ضعيفة" (Weak Signals):**

*   في X: ابحث عن تغريدات من باحثين AI أو شركات ناشئة تقول: "We're struggling with...", "Looking for human evaluators for...", "Can't find enough dialect speakers...".

*   في Product Hunt: أدوات AI جديدة وتعلق بوجود أخطاء في فهم اللغة أو الثقافة.

*   كلمات مفتاحية: ("human evaluation" OR "native speakers needed" OR "dialect" OR "sarcasm detection" OR "voice cloning") (Arabic OR Egyptian OR "Middle East").

**3. صغ 3 توقعات استباقية (مفصلة وعملية):**

*   لكل توقع املأ الجدول التالي:

    | وصف المهمة المتوقعة (1-5$) | لماذا هي معقدة؟ | لماذا لم يدخلها الـ AI؟ | مستوى اختراق AI حالياً (من 1 لـ 10) | لماذا الطلب > العرض؟ | الإشارات الضعيفة (روابط) | خطوات استباقية (ماذا تفعل من الآن) |

---

### الجزء الثالث: نصائح أمان وتوصيات ذهبية

*   أضف قائمة بأشهر 5 علامات احتيال في هذا المجال ليحذر منها المستخدم.

*   أضف أفضل 3 منصات تدفع للمصريين حالياً بناءً على بحثك.

---

### صياغة النتيجة النهائية:

**تقرير 1: الفرص الحالية (منصات ومهام مفتوحة الآن)**

| المنصة/الفرصة | وصف المهمة | الصنف (فورية/بعد قبول) | الدفع ($) | متاحة في مصر؟ | رابط ودليل الدفع | تقييم المصداقية |

**تقرير 2: توقعات الفرص المستقبلية**

[الجدول المذكور أعلاه في التنبؤات]

**تقرير 3: نصائح وتحذيرات**

[القائمة]

---

ابدأ الآن. تذكر: 
- الدقة في التحقق من المصداقية أهم من الكثرة في عدد الفرص
- إذا لم تستطع التحقق من دليل الدفع، اكتب صراحة: "دليل الدفع: غير موجود — يحتاج تحقق يدوي"
- لا تخترع روابط أو أدلة غير موجودة
- لكل منصة، اذكر مصدر معلومتك وتاريخها إن أمكن

اكتب التقرير باللغة العربية بالكامل، مع الإبقاء على أسماء المنصات والروابط بالإنجليزية.
"""


# ─── Main research function ───────────────────────────────────────────────────
def run_research(client: openai.OpenAI) -> str:
    """Run the research task and return the report content."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting micro-task research...")
    print(f"Model: {MODEL_NAME}")
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional strategic researcher with access to your training knowledge "
                "about online platforms, micro-task economy, and AI capabilities as of early 2026. "
                "Be thorough, honest about what you can and cannot verify, and produce actionable insights. "
                "When you cannot verify something with real evidence, say so explicitly rather than fabricating. "
                "Write in Arabic as requested, keeping platform names and URLs in English."
            ),
        },
        {"role": "user", "content": RESEARCH_PROMPT},
    ]
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending research request to {MODEL_NAME}...")
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.3,
        max_tokens=8000,
    )
    
    report_content = response.choices[0].message.content or ""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Research complete. Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
    
    return report_content


# ─── Multi-turn refinement ────────────────────────────────────────────────────
def run_research_with_critique(client: openai.OpenAI) -> str:
    """Run research, then self-critique and refine."""
    
    # Turn 1: Initial research
    initial_report = run_research(client)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running self-critique pass...")
    
    # Turn 2: Self-critique
    critique_messages = [
        {
            "role": "system",
            "content": (
                "You are a strict fact-checker reviewing a micro-task economy research report. "
                "Your job is to identify: (1) any fabricated links or unverified claims stated as facts, "
                "(2) missing information about Egypt availability, (3) platforms that are known scams or defunct. "
                "Be ruthless in identifying hallucinations."
            ),
        },
        {
            "role": "user",
            "content": f"""راجع هذا التقرير البحثي بصرامة:

{initial_report}

حدد:
1. أي روابط أو أدلة قد تكون مخترعة (hallucinated)
2. ادعاءات غير مدعومة بمصادر
3. منصات قد تكون محتالة أو متوقفة
4. معلومات ناقصة عن التوفر في مصر

أجب بنقاط واضحة، ثم قل: هل التقرير موثوق بشكل عام؟""",
        },
    ]
    
    critique_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=critique_messages,
        temperature=0.1,
        max_tokens=2000,
    )
    critique = critique_response.choices[0].message.content or ""
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generating final refined report...")
    
    # Turn 3: Refined final report
    refine_messages = [
        {"role": "system", "content": "You are a professional researcher producing a final, accurate report."},
        {"role": "user", "content": RESEARCH_PROMPT},
        {"role": "assistant", "content": initial_report},
        {
            "role": "user",
            "content": f"""بناءً على هذا النقد:

{critique}

أعد كتابة التقرير النهائي مع:
1. تصحيح أي ادعاءات غير مؤكدة
2. وضع علامة ⚠️ بوضوح على كل ما لم تتحقق منه
3. حذف أي روابط قد تكون مخترعة
4. الحفاظ على نفس الهيكل والجداول

ابدأ التقرير بـ:
# تقرير بحثي: اقتصاد المهام الصغيرة للعمال المصريين
تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ملاحظة المنهجية: تم توليد هذا التقرير بواسطة نموذج ذكاء اصطناعي بدون وصول مباشر للإنترنت في وقت التشغيل. جميع المعلومات مبنية على بيانات التدريب حتى مطلع 2026. يُنصح بالتحقق اليدوي من جميع المنصات قبل التسجيل.
""",
        },
    ]
    
    final_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=refine_messages,
        temperature=0.2,
        max_tokens=8000,
    )
    final_report = final_response.choices[0].message.content or ""
    
    # Append critique as appendix
    full_output = final_report + f"\n\n---\n## ملحق: تقرير مراجعة الجودة الداخلية\n\n{critique}"
    
    return full_output


# ─── Entry point ──────────────────────────────────────────────────────────────
def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    client = setup_client()
    
    # Run 3-turn research: initial → critique → refined
    report = run_research_with_critique(client)
    
    # Save report
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ Report saved to: {REPORT_FILE}")
    print(f"Report length: {len(report)} characters")
    
    # Save metadata
    meta = {
        "task": "micro_task_economy_research",
        "model": MODEL_NAME,
        "timestamp": datetime.now().isoformat(),
        "report_file": str(REPORT_FILE),
        "report_length": len(report),
        "turns": 3,
    }
    meta_file = RESULTS_DIR / "meta.json"
    meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Metadata saved to: {meta_file}")


if __name__ == "__main__":
    main()
