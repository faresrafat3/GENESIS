# 📚 Stolen Papers — Cross-Reference for Our Paper

هذا المجلد يوثق كل الأوراق اللي بنشير إليها/نسرق منها، ولكل واحدة:
- **Curves/Tables** نحاول نقلد فورمتها
- **Research Questions** طرحوها ونجاوبها في مشروعنا
- **Findings** تدعم أو تعارض اكتشافاتنا
- **Where in our paper** بنشير إليها

---

## 📊 Master Cross-Reference Table

| Paper | Their Contribution | Our Response / Answer | Section in Our Paper |
|---|---|---|---|
| **AlphaEvolve** | Evolutionary discovery over LLM outputs | We implement AlphaEvolve-style loop (partial: skeleton in orchestrator) | §3.4, §8 |
| **FunSearch** | Program search + database | We adopt sampling temp + population + best-so-far | §3.4 |
| **Aletheia** | Generate-Verify-Revise loops | We port verify-revise into feedback_agent | §3.5 |
| **Co-Scientist** | Multi-agent research | We use single meta+target+feedback (deferred multi) | §3.6, §11 |
| **GPQA** | Graduate MCQ benchmark | We use it as primary eval | §4.2 |
| **gpt-oss model card** | Reasoning-effort scaling | We test on `high` effort + observe saturation | §5, §9 |

---

## 📄 Individual Paper Notes

Each paper has a detailed notes file:
- `alphaevolve.md` — Google DeepMind AlphaEvolve
- `funsearch.md` — DeepMind FunSearch (Nature 2024)
- `aletheia.md` — DeepMind Aletheia (Gemini Deep Think)
- `coscientist.md` — DeepMind Co-Scientist
- `gpqa_benchmark.md` — GPQA (Rein et al. 2023)
- `gpt_oss_card.md` — OpenAI gpt-oss model card (arXiv:2508.10925)

---

## 🎯 Research Questions Adopted from Others

### From AlphaEvolve:
- **RQ (AE1):** Does evolutionary search over LLM outputs beat single-shot LLM?
- **Our Answer:** ⏳ TBD (T3 ablation without evo)

### From FunSearch:
- **RQ (FS1):** Does maintaining a population diverse improve discovery?
- **Our Answer:** ⏳ TBD (population + diversity implemented in skeleton)

### From Aletheia:
- **RQ (AL1):** Does generate-verify-revise loop improve correctness over single generation?
- **Our Answer:** ⏳ Feedback agent is our verify-revise (T3 will ablate)

### From Co-Scientist:
- **RQ (CS1):** Does multi-agent debate beat single agent?
- **Our Answer:** ⏳ Deferred (we use meta+target+feedback = 3 agents in pipeline, but not debate)

### From GPQA:
- **RQ (GP1):** How well do LLMs perform across Physics/Chemistry/Biology?
- **Our Answer:** ✅ Physics 81.8% >> Chemistry 66.7% ≈ Biology 66.7% (gpt-oss pure baseline)

### From gpt-oss card:
- **RQ (GO1):** Does higher reasoning effort improve accuracy monotonically?
- **Our Answer:** ⚠️ **Counter-finding**: reasoning_tokens correlate NEGATIVELY with per-question accuracy in our data

---

## 📈 Curves We Intend to Reproduce/Adapt

| Original Figure | Their Format | Our Adaptation | Data Source |
|---|---|---|---|
| AlphaEvolve Fig 3 | score vs generation | Same, but per T1/T3 runs | Ablation results |
| FunSearch Table 1 | baseline vs discovered | Same, our baseline vs post-fix | §5, §7 |
| Aletheia Fig 2 | iteration count vs correctness | Feedback rounds vs accuracy | §8 |
| Co-Scientist Table 2 | multi vs single agent | 1/2/3 agents comparison | §8 |
| GPQA per-domain | Bar chart | Same, all our models | §5 |
| gpt-oss card scaling | line: effort vs acc | Adapted: our per-token curve | §9 |

---

## 🔥 New Findings We'll Contribute Back

هذه الاكتشافات جديدة (لسه ما شفناها في الأدبيات) وستمثل contributions قوية:

1. **Scaffolding-vs-Architecture attribution**: 45 من 50-point gap يرجع لـ 5 bugs محددة
2. **Reasoning saturation**: correlation سلبية بين reasoning_tokens وaccuracy على GPQA
3. **Domain asymmetry**: Chemistry Organic هو الـ hardest domain عبر كل النماذج المُختبرة
4. **Empty content phenomenon**: 35% من requests بـ content="" لما max_tokens يستهلك في reasoning
5. **Recovery via reasoning extraction**: 6/7 empty responses تُنقذ من reasoning_details

كل واحدة من دي = potentially standalone paper 🔥

---

**آخر تحديث:** 2026-06-05
