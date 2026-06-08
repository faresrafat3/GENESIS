"""
Tests for genesis/skill_engine/
Component: SKILL_ENGINE
Source: MUSE-Autoskill + EvoSkill + SkillOps + SoK

Tests cover:
  - SkillContract: creation, precondition checking, validation gap
  - Skill: creation, catalog entry, memory, serialization
  - SkillFolder: create, from_path, validate_structure
  - SkillLibrary: CRUD, frontier, maintenance, catalog
  - SkillEvaluator: test running, contract validation
  - SkillRetriever: BM25+semantic hybrid retrieval
  - SkillExtractor: heuristic extraction from agent code
  - FailureCollector: failure collection from gen artifacts
  - EvoSkillLoop: proposal + building + frontier management
  - Public API: register, retrieve, get_catalog, run_evo
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from genesis.skill_engine.skill import Skill, SkillContract, SkillFolder
from genesis.skill_engine.library import SkillLibrary, HealthReport
from genesis.skill_engine.evaluator import SkillEvaluator, TestResult
from genesis.skill_engine.retriever import SkillRetriever
from genesis.skill_engine.extractor import SkillExtractor, FailureCollector, FailureCase
from genesis.skill_engine.evolver import (
    SkillProposal, ProposerAgent, SkillBuilderAgent, EvoSkillLoop
)


# ─── SkillContract Tests ──────────────────────────────────────────────────────

class TestSkillContract(unittest.TestCase):
    def test_basic_creation(self):
        c = SkillContract(
            preconditions=["SERPER_API_KEY available"],
            operation="search web",
            artifact_type="json",
            validator="check json exists",
            failure_modes=["rate limit"],
        )
        self.assertFalse(c.has_validation_gap)
        self.assertEqual(c.artifact_type, "json")

    def test_validation_gap(self):
        c = SkillContract()  # empty validator
        self.assertTrue(c.has_validation_gap)

    def test_validation_gap_whitespace(self):
        c = SkillContract(validator="   ")
        self.assertTrue(c.has_validation_gap)

    def test_precondition_check_no_env(self):
        c = SkillContract(preconditions=["NONEXISTENT_XYZ_API_KEY available"])
        old = os.environ.pop("NONEXISTENT_XYZ_API_KEY", None)
        try:
            met, unmet = c.check_preconditions({})
            self.assertFalse(met)
            self.assertGreater(len(unmet), 0)
        finally:
            if old:
                os.environ["NONEXISTENT_XYZ_API_KEY"] = old

    def test_precondition_check_with_env(self):
        os.environ["MYTEST_API_KEY"] = "testkey123"
        c = SkillContract(preconditions=["MYTEST_API_KEY available"])
        try:
            met, unmet = c.check_preconditions({})
            self.assertTrue(met)
            self.assertEqual(len(unmet), 0)
        finally:
            del os.environ["MYTEST_API_KEY"]

    def test_to_dict(self):
        c = SkillContract(preconditions=["P"], operation="O", artifact_type="A")
        d = c.to_dict()
        self.assertIn("preconditions", d)
        self.assertIn("operation", d)
        self.assertIn("artifact_type", d)

    def test_from_dict_roundtrip(self):
        c = SkillContract(
            preconditions=["p1", "p2"],
            operation="do something",
            artifact_type="json",
            validator="check it",
            failure_modes=["f1"],
        )
        d = c.to_dict()
        c2 = SkillContract.from_dict(d)
        self.assertEqual(c2.operation, "do something")
        self.assertEqual(c2.preconditions, ["p1", "p2"])
        self.assertFalse(c2.has_validation_gap)


# ─── Skill Tests ──────────────────────────────────────────────────────────────

class TestSkill(unittest.TestCase):
    def _make(self, **kwargs) -> Skill:
        defaults = dict(
            name="test_skill",
            description="A test skill",
            domain="research",
        )
        defaults.update(kwargs)
        return Skill(**defaults)

    def test_basic_creation(self):
        s = self._make()
        self.assertEqual(s.name, "test_skill")
        self.assertEqual(s.domain, "research")
        self.assertEqual(s.usage_count, 0)
        self.assertEqual(s.performance_score, 0.0)

    def test_catalog_entry_basic(self):
        s = self._make(description="Does amazing things")
        entry = s.get_catalog_entry()
        self.assertIn("test_skill", entry)
        self.assertIn("Does amazing things", entry)

    def test_catalog_entry_with_score(self):
        s = self._make(performance_score=85.5)
        entry = s.get_catalog_entry()
        self.assertIn("score:", entry)  # format: [score:86]

    def test_catalog_entry_with_usage(self):
        s = self._make(usage_count=10)
        entry = s.get_catalog_entry()
        self.assertIn("10x", entry)

    def test_success_rate_empty(self):
        s = self._make()
        self.assertEqual(s.success_rate, 0.0)

    def test_success_rate_computed(self):
        s = self._make(success_count=7, failure_count=3)
        self.assertAlmostEqual(s.success_rate, 0.7, places=5)

    def test_record_use_success(self):
        s = self._make()
        s.record_use(success=True)
        self.assertEqual(s.usage_count, 1)
        self.assertEqual(s.success_count, 1)
        self.assertEqual(s.failure_count, 0)

    def test_record_use_failure(self):
        s = self._make()
        s.record_use(success=False)
        self.assertEqual(s.usage_count, 1)
        self.assertEqual(s.failure_count, 1)

    def test_body_hash_consistent(self):
        s = self._make(instructions="print('hello')")
        h1 = s.body_hash
        h2 = s.body_hash
        self.assertEqual(h1, h2)

    def test_to_dict_has_schema_version(self):
        s = self._make()
        d = s.to_dict()
        self.assertEqual(d["schema_version"], "1.0")
        self.assertEqual(d["component"], "SKILL_ENGINE")

    def test_to_dict_serializable(self):
        s = self._make(task_types=["research", "analysis"])
        d = s.to_dict()
        json_str = json.dumps(d)
        self.assertIsInstance(json_str, str)

    def test_from_dict_roundtrip(self):
        s = self._make(
            description="Test skill", performance_score=75.0,
            task_types=["coding"], generation=2, parent_skill="parent"
        )
        d = s.to_dict()
        s2 = Skill.from_dict(d)
        self.assertEqual(s2.name, s.name)
        self.assertAlmostEqual(s2.performance_score, 75.0)
        self.assertEqual(s2.task_types, ["coding"])
        self.assertEqual(s2.generation, 2)

    def test_lineage_fields(self):
        s = self._make(generation=3, parent_skill="parent_v2", frontier_rank=1)
        self.assertEqual(s.generation, 3)
        self.assertEqual(s.parent_skill, "parent_v2")
        self.assertEqual(s.frontier_rank, 1)

    def test_memory_operations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            s = self._make()
            s.skill_dir = Path(tmpdir)
            # Empty memory
            self.assertEqual(s.read_memory(), "")
            # Append
            s.append_memory("Test note", "micro_task")
            content = s.read_memory()
            self.assertIn("Test note", content)
            self.assertIn("micro_task", content)

    def test_build_skill_md(self):
        s = self._make(
            when_to_use=["Use for X", "Use for Y"],
            core_principles=["Principle 1"],
            workflow="Step 1\nStep 2",
        )
        md = s._build_skill_md()
        self.assertIn("test_skill", md)
        self.assertIn("Use for X", md)
        self.assertIn("Step 1", md)


# ─── SkillFolder Tests ───────────────────────────────────────────────────────

class TestSkillFolder(unittest.TestCase):
    def _make_skill(self, name="test_folder_skill") -> Skill:
        return Skill(
            name=name,
            description="Test folder skill",
            domain="research",
            when_to_use=["When testing"],
            workflow="Step 1: test\nStep 2: verify",
        )

    def test_create_basic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            s = self._make_skill()
            path = SkillFolder.create(Path(tmpdir), s)
            self.assertTrue(path.exists())
            self.assertTrue((path / "SKILL.md").exists())

    def test_create_with_scripts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            s = self._make_skill()
            path = SkillFolder.create(
                Path(tmpdir), s,
                scripts={"main.py": "print('hello')"}
            )
            self.assertTrue((path / "scripts" / "main.py").exists())

    def test_create_with_tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            s = self._make_skill()
            path = SkillFolder.create(
                Path(tmpdir), s,
                tests={"test_skill.py": "def test_x():\n    assert True"}
            )
            self.assertTrue((path / "tests" / "test_skill.py").exists())

    def test_from_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            s = self._make_skill()
            path = SkillFolder.create(Path(tmpdir), s)
            loaded = SkillFolder.from_path(path)
            self.assertEqual(loaded.name, "test_folder_skill")
            self.assertEqual(loaded.domain, "research")

    def test_from_path_not_found(self):
        with self.assertRaises(FileNotFoundError):
            SkillFolder.from_path(Path("/nonexistent/path"))

    def test_validate_structure_good(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            s = self._make_skill()
            path = SkillFolder.create(
                Path(tmpdir), s,
                tests={"test_s.py": "def test_x(): assert True"}
            )
            issues = SkillFolder.validate_structure(path)
            self.assertEqual(issues, [])

    def test_validate_structure_no_tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            s = self._make_skill()
            path = SkillFolder.create(Path(tmpdir), s)
            issues = SkillFolder.validate_structure(path)
            self.assertGreater(len(issues), 0)
            self.assertTrue(any("tests" in i.lower() for i in issues))

    def test_validate_structure_missing_dir(self):
        issues = SkillFolder.validate_structure(Path("/does/not/exist"))
        self.assertTrue(any("exist" in i.lower() for i in issues))


# ─── SkillLibrary Tests ───────────────────────────────────────────────────────

class TestSkillLibrary(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.lib = SkillLibrary(
            skills_dir=Path(self.tmpdir) / "skills",
            db_path=Path(self.tmpdir) / "test.db",
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_skill(self, name="lib_test", score=60.0) -> Skill:
        return Skill(
            name=name, description=f"Test skill {name}",
            domain="research", performance_score=score,
            when_to_use=[f"Use {name}"], workflow="Do stuff",
        )

    def test_register_and_get(self):
        s = self._make_skill()
        ok = self.lib.register(s)
        self.assertTrue(ok)
        got = self.lib.get("lib_test")
        self.assertIsNotNone(got)
        self.assertEqual(got.name, "lib_test")

    def test_register_duplicate_fails(self):
        s = self._make_skill()
        self.lib.register(s)
        ok2 = self.lib.register(s)  # same name
        self.assertFalse(ok2)

    def test_register_overwrite(self):
        s = self._make_skill(score=60.0)
        self.lib.register(s)
        s2 = self._make_skill(score=80.0)
        s2.description = "Updated description"
        self.lib.register(s2, overwrite=True)
        got = self.lib.get("lib_test")
        self.assertEqual(got.description, "Updated description")

    def test_get_unknown_returns_none(self):
        result = self.lib.get("nonexistent_xyz")
        self.assertIsNone(result)

    def test_retire(self):
        s = self._make_skill()
        self.lib.register(s)
        ok = self.lib.retire("lib_test")
        self.assertTrue(ok)
        self.assertIsNone(self.lib.get("lib_test"))

    def test_retire_unknown(self):
        ok = self.lib.retire("nonexistent")
        self.assertFalse(ok)

    def test_list_all_empty(self):
        skills = self.lib.list_all()
        self.assertEqual(skills, [])

    def test_list_all_ordered(self):
        self.lib.register(self._make_skill("a_skill", score=30.0))
        self.lib.register(self._make_skill("b_skill", score=80.0))
        self.lib.register(self._make_skill("c_skill", score=60.0))
        skills = self.lib.list_all()
        scores = [s.performance_score for s in skills]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_count(self):
        self.assertEqual(self.lib.count(), 0)
        self.lib.register(self._make_skill("s1"))
        self.assertEqual(self.lib.count(), 1)
        self.lib.register(self._make_skill("s2"))
        self.assertEqual(self.lib.count(), 2)

    def test_frontier_management(self):
        s1 = self._make_skill("f1", score=90.0)
        s2 = self._make_skill("f2", score=70.0)
        s3 = self._make_skill("f3", score=50.0)
        self.lib.register(s1)
        self.lib.register(s2)
        self.lib.register(s3)

        added1 = self.lib.add_to_frontier(s1)
        added2 = self.lib.add_to_frontier(s2)
        self.assertTrue(added1)
        self.assertTrue(added2)

        frontier = self.lib.get_frontier()
        names = [s.name for s in frontier]
        self.assertIn("f1", names)

    def test_frontier_eviction(self):
        # With k=3 frontier, 4th skill evicts weakest
        lib = SkillLibrary(
            skills_dir=Path(self.tmpdir) / "skills2",
            db_path=Path(self.tmpdir) / "test2.db",
            frontier_k=2,
        )
        s1 = self._make_skill("e1", score=90.0)
        s2 = self._make_skill("e2", score=70.0)
        s3 = self._make_skill("e3", score=80.0)
        lib.register(s1); lib.add_to_frontier(s1)
        lib.register(s2); lib.add_to_frontier(s2)
        lib.register(s3); added = lib.add_to_frontier(s3)
        # s3 (80) should evict s2 (70)
        self.assertTrue(added)
        frontier = lib.get_frontier()
        names = [s.name for s in frontier]
        self.assertIn("e1", names)
        self.assertNotIn("e2", names)

    def test_health_check_validation_gap(self):
        s = self._make_skill()
        s.contract = SkillContract()  # no validator = gap
        self.lib.register(s)
        report = self.lib.health_check()
        self.assertIn("lib_test", report.validation_gaps)

    def test_health_check_redundancy(self):
        """Test that two skills with same body_hash are detected as redundant."""
        from genesis.skill_engine.skill import Skill
        # Create skills with exact same instructions → same hash
        s1 = Skill(name="redundant_a", description="Skill A", instructions="same code")
        s2 = Skill(name="redundant_b", description="Skill B", instructions="same code")
        # Verify hashes match
        self.assertEqual(s1.body_hash, s2.body_hash)
        self.lib.register(s1)
        self.lib.register(s2)
        report = self.lib.health_check()
        self.assertGreater(len(report.redundant_pairs), 0)

    def test_catalog_yaml_contains_skill(self):
        s = self._make_skill("catalog_test", score=75.0)
        self.lib.register(s)
        cat = self.lib.get_catalog_yaml()
        self.assertIn("catalog_test", cat)

    def test_catalog_prompt_contains_skill(self):
        s = self._make_skill("prompt_test")
        self.lib.register(s)
        prompt = self.lib.get_catalog_prompt()
        self.assertIn("prompt_test", prompt)

    def test_merge(self):
        s1 = self._make_skill("merge_a", score=80.0)
        s2 = self._make_skill("merge_b", score=60.0)
        s1.instructions = "unique content a"
        s2.instructions = "unique content b"
        self.lib.register(s1)
        self.lib.register(s2)
        merged = self.lib.merge(s1, s2)
        self.assertEqual(merged.name, "merge_a")  # winner
        self.assertIsNone(self.lib.get("merge_b"))  # loser retired

    def test_update(self):
        s = self._make_skill()
        self.lib.register(s)
        s.performance_score = 95.0
        self.lib.update(s)
        got = self.lib.get("lib_test")
        self.assertAlmostEqual(got.performance_score, 95.0)


# ─── SkillEvaluator Tests ────────────────────────────────────────────────────

class TestSkillEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = SkillEvaluator(timeout_sec=15)
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_skill_with_tests(self, test_code: str, should_pass: bool = True) -> Skill:
        s = Skill(
            name=f"eval_test_{'pass' if should_pass else 'fail'}",
            description="Evaluation test skill",
        )
        SkillFolder.create(
            Path(self.tmpdir), s,
            tests={"test_skill.py": test_code}
        )
        return s

    def test_no_tests_passes_with_warning(self):
        s = Skill(name="no_tests_skill", description="No tests")
        s.skill_dir = Path(self.tmpdir) / "no_tests_skill"
        s.skill_dir.mkdir()
        (s.skill_dir / "SKILL.md").write_text("---\nname: no_tests_skill\n---\n")
        result = self.evaluator.run_tests(s)
        # No tests = allowed through (with warning about validation gap)
        self.assertTrue(result.passed)
        self.assertIn("validation gap", result.error_trace.lower())

    def test_passing_tests(self):
        s = self._make_skill_with_tests("def test_ok():\n    assert True\n")
        result = self.evaluator.run_tests(s)
        self.assertTrue(result.passed)
        self.assertEqual(result.tests_passed, 1)

    def test_failing_tests(self):
        s = self._make_skill_with_tests("def test_fail():\n    assert False\n", False)
        result = self.evaluator.run_tests(s)
        self.assertFalse(result.passed)
        self.assertGreater(result.tests_failed, 0)

    def test_result_has_timing(self):
        s = self._make_skill_with_tests("def test_t():\n    assert True\n")
        result = self.evaluator.run_tests(s)
        self.assertGreater(result.execution_time_ms, 0)

    def test_validate_contract_no_env(self):
        s = Skill(name="x", description="x")
        s.contract = SkillContract(preconditions=["MISSING_KEY_12345 available"])
        old = os.environ.pop("MISSING_KEY_12345", None)
        try:
            ok, issues = self.evaluator.validate_contract(s, {})
            self.assertFalse(ok)
        finally:
            if old:
                os.environ["MISSING_KEY_12345"] = old

    def test_validate_artifact_file_exists(self):
        s = Skill(name="x", description="x")
        s.contract = SkillContract(artifact_type="text", validator="file exists")
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"content")
            path = f.name
        try:
            ok, msg = self.evaluator.validate_artifact(s, path)
            self.assertTrue(ok)
        finally:
            os.unlink(path)

    def test_validate_artifact_missing_file(self):
        s = Skill(name="x", description="x")
        s.contract = SkillContract(artifact_type="json", validator="json valid")
        ok, msg = self.evaluator.validate_artifact(s, "/nonexistent/path.json")
        self.assertFalse(ok)

    def test_validate_artifact_valid_json(self):
        s = Skill(name="x", description="x")
        s.contract = SkillContract(artifact_type="json", validator="valid json")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump({"test": 1}, f)
            path = f.name
        try:
            ok, msg = self.evaluator.validate_artifact(s, path)
            self.assertTrue(ok)
        finally:
            os.unlink(path)

    def test_validate_artifact_invalid_json(self):
        s = Skill(name="x", description="x")
        s.contract = SkillContract(artifact_type="json", validator="valid json")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("not json {{{")
            path = f.name
        try:
            ok, msg = self.evaluator.validate_artifact(s, path)
            self.assertFalse(ok)
        finally:
            os.unlink(path)

    def test_validation_gap(self):
        s = Skill(name="x", description="x")
        s.contract = SkillContract()  # no validator
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            ok, msg = self.evaluator.validate_artifact(s, path)
            self.assertTrue(ok)
            self.assertIn("gap", msg.lower())
        finally:
            os.unlink(path)


# ─── SkillRetriever Tests ────────────────────────────────────────────────────

class TestSkillRetriever(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.lib = SkillLibrary(
            skills_dir=Path(self.tmpdir) / "skills",
            db_path=Path(self.tmpdir) / "ret.db",
        )
        self.retriever = SkillRetriever()

        # Register some skills
        skills = [
            Skill(name="web_search_skill", description="Search web for information",
                  domain="research", task_types=["research"],
                  when_to_use=["web search needed", "real-time info"], performance_score=80.0),
            Skill(name="coding_skill", description="Write and execute Python code",
                  domain="coding", task_types=["coding"],
                  when_to_use=["code execution needed"], performance_score=70.0),
            Skill(name="analysis_skill", description="Analyze data and generate reports",
                  domain="analysis", task_types=["analysis"],
                  when_to_use=["data analysis required"], performance_score=60.0),
        ]
        for s in skills:
            self.lib.register(s, overwrite=False)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_retrieve_returns_list(self):
        results = self.retriever.retrieve("search web", self.lib, top_k=3)
        self.assertIsInstance(results, list)

    def test_retrieve_top_k_respected(self):
        results = self.retriever.retrieve("skill", self.lib, top_k=2)
        self.assertLessEqual(len(results), 2)

    def test_retrieve_relevant_skill_first(self):
        results = self.retriever.retrieve("web search information", self.lib, top_k=3)
        if results:
            self.assertEqual(results[0].name, "web_search_skill")

    def test_retrieve_domain_filter(self):
        results = self.retriever.retrieve("skill", self.lib, top_k=5, domain_filter="coding")
        for s in results:
            self.assertEqual(s.domain, "coding")

    def test_retrieve_empty_library(self):
        import shutil
        tmpdir2 = tempfile.mkdtemp()
        try:
            lib2 = SkillLibrary(
                skills_dir=Path(tmpdir2) / "skills",
                db_path=Path(tmpdir2) / "empty.db"
            )
            results = self.retriever.retrieve("anything", lib2, top_k=3)
            self.assertEqual(results, [])
        finally:
            shutil.rmtree(tmpdir2, ignore_errors=True)

    def test_tokenize(self):
        tokens = self.retriever._tokenize("Find web search platforms for Egypt")
        self.assertNotIn("for", tokens)
        self.assertIn("web", tokens)
        self.assertIn("search", tokens)

    def test_bm25_score_relevant(self):
        query_tokens = ["web", "search"]
        doc_tokens = ["web", "search", "platform", "information"]
        corpus = [doc_tokens, ["coding", "python", "execute"]]
        score = self.retriever._bm25_score(query_tokens, doc_tokens, corpus)
        self.assertGreater(score, 0)

    def test_bm25_score_irrelevant(self):
        query_tokens = ["web", "search"]
        doc_tokens = ["python", "code", "execute"]
        corpus = [["web", "search", "info"], doc_tokens]
        score = self.retriever._bm25_score(query_tokens, doc_tokens, corpus)
        self.assertGreaterEqual(score, 0)

    def test_semantic_score_overlap(self):
        q = ["web", "search", "platform"]
        d = ["web", "search", "data"]
        score = self.retriever._semantic_score(q, d)
        self.assertGreater(score, 0)

    def test_semantic_score_no_overlap(self):
        q = ["web", "search"]
        d = ["coding", "python"]
        score = self.retriever._semantic_score(q, d)
        self.assertEqual(score, 0.0)


# ─── SkillExtractor Tests ────────────────────────────────────────────────────

class TestSkillExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = SkillExtractor(llm_client=None)

    def test_below_threshold_returns_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("print('hello')")
            path = f.name
        try:
            skills = self.extractor.extract_from_agent(path, score=50.0)
            self.assertEqual(skills, [])
        finally:
            os.unlink(path)

    def test_extract_web_search_pattern(self):
        code = """
from genesis.tools.web_search import web_search, EvidenceLog, extract_keywords
evidence_log = EvidenceLog()
results = web_search("micro task platforms", mode="quick")
# self-critique pass
# critique the output
for r in results:
    evidence_log.add_claim(r.title)
evidence_log.save("evidence_log.json")
"""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            path = f.name
        try:
            skills = self.extractor.extract_from_agent(path, score=80.0)
            self.assertIsInstance(skills, list)
            if skills:
                self.assertIsInstance(skills[0], Skill)
        finally:
            os.unlink(path)

    def test_extract_missing_file(self):
        skills = self.extractor.extract_from_agent("/nonexistent.py", score=90.0)
        self.assertEqual(skills, [])

    def test_extracted_skill_has_source_info(self):
        code = "from genesis.tools.web_search import web_search, EvidenceLog\nEvidenceLog()"
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            path = f.name
        try:
            skills = self.extractor.extract_from_agent(path, score=85.0, run_id="run_99", gen_id=3)
            for s in skills:
                self.assertEqual(s.source_run, "run_99")
                self.assertEqual(s.source_gen, 3)
                self.assertAlmostEqual(s.performance_score, 85.0)
        finally:
            os.unlink(path)


class TestFailureCollector(unittest.TestCase):
    def setUp(self):
        self.collector = FailureCollector()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_gens_returns_empty(self):
        failures = self.collector.collect(self.tmpdir, current_gen=5, threshold=0.6)
        self.assertEqual(failures, [])

    def test_collects_low_score_failure(self):
        gen_dir = Path(self.tmpdir) / "gen_1"
        gen_dir.mkdir()
        eval_data = {
            "overall_score": 40.0,  # < 60 → failure
            "hallucination_rate": 0.7,
            "task_name": "micro_task",
            "error": "",
            "checklist": [{"criterion": "accuracy", "met": False}],
        }
        with open(gen_dir / "open_task_eval.json", "w") as f:
            json.dump(eval_data, f)

        failures = self.collector.collect(self.tmpdir, current_gen=1, threshold=0.6)
        self.assertEqual(len(failures), 1)
        self.assertAlmostEqual(failures[0].score, 0.4)
        self.assertAlmostEqual(failures[0].hallucination_rate, 0.7)

    def test_ignores_high_score(self):
        gen_dir = Path(self.tmpdir) / "gen_1"
        gen_dir.mkdir()
        eval_data = {"overall_score": 80.0, "hallucination_rate": 0.1}
        with open(gen_dir / "open_task_eval.json", "w") as f:
            json.dump(eval_data, f)

        failures = self.collector.collect(self.tmpdir, current_gen=1, threshold=0.6)
        self.assertEqual(failures, [])

    def test_failure_case_fields(self):
        self.assertIsInstance(FailureCase(
            gen=1, task_description="test", agent_output_excerpt="output",
            score=0.4, hallucination_rate=0.6, error_trace="error"
        ), FailureCase)


# ─── Evolver Tests ────────────────────────────────────────────────────────────

class TestSkillProposal(unittest.TestCase):
    def test_creation(self):
        p = SkillProposal(
            action="create",
            target_skill=None,
            description="Search web",
            rationale="Missing capability",
            capability_gap="No web search",
            proposed_name="web_search_v2",
        )
        self.assertEqual(p.action, "create")
        self.assertEqual(p.proposed_name, "web_search_v2")


class TestProposerAgent(unittest.TestCase):
    def test_heuristic_high_hallucination(self):
        proposer = ProposerAgent(llm_client=None)
        failures = [
            FailureCase(gen=1, task_description="t", agent_output_excerpt="o",
                        score=0.5, hallucination_rate=0.7, error_trace="")
        ]
        proposal = proposer.propose(failures, [])
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.action, "create")
        self.assertIn("evidence", proposal.proposed_name.lower())

    def test_heuristic_no_failures(self):
        proposer = ProposerAgent()
        proposal = proposer.propose([], [])
        self.assertIsNone(proposal)

    def test_record_outcome(self):
        proposer = ProposerAgent()
        p = SkillProposal(
            action="create", target_skill=None,
            description="test", rationale="r", capability_gap="g"
        )
        proposer.record_outcome(p, score_delta=0.15)
        self.assertEqual(len(proposer.feedback_history), 1)
        self.assertAlmostEqual(proposer.feedback_history[0]["score_delta"], 0.15)


class TestSkillBuilderAgent(unittest.TestCase):
    def test_heuristic_materialize(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = SkillBuilderAgent(llm_client=None, skills_base_dir=tmpdir)
            proposal = SkillProposal(
                action="create", target_skill=None,
                proposed_name="test_heuristic_skill",
                description="Test skill from heuristic",
                rationale="Testing",
                capability_gap="Missing test capability",
            )
            skill = builder.materialize(proposal)
            self.assertIsNotNone(skill)
            self.assertIsNotNone(skill.skill_dir)
            self.assertTrue(skill.skill_dir.exists())

    def test_materialize_creates_tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = SkillBuilderAgent(llm_client=None, skills_base_dir=tmpdir)
            proposal = SkillProposal(
                action="create", target_skill=None,
                proposed_name="test_with_tests_skill",
                description="Skill with tests",
                rationale="Testing", capability_gap="gap",
            )
            skill = builder.materialize(proposal)
            self.assertIsNotNone(skill)
            if skill.skill_dir:
                self.assertTrue((skill.skill_dir / "tests").exists())


# ─── Public API Tests ─────────────────────────────────────────────────────────

class TestSkillEnginePublicAPI(unittest.TestCase):
    """Tests for genesis/skill_engine/__init__.py public API."""

    def test_get_catalog_returns_string(self):
        from genesis.skill_engine import get_catalog
        cat = get_catalog()
        self.assertIsInstance(cat, str)

    def test_get_stats_returns_dict(self):
        from genesis.skill_engine import get_stats
        stats = get_stats()
        self.assertIn("total_skills", stats)
        self.assertIn("frontier_size", stats)

    def test_get_skill_none_for_missing(self):
        from genesis.skill_engine import get_skill
        result = get_skill("absolutely_nonexistent_skill_xyz")
        self.assertIsNone(result)

    def test_get_frontier_returns_list(self):
        from genesis.skill_engine import get_frontier
        frontier = get_frontier()
        self.assertIsInstance(frontier, list)

    def test_retrieve_returns_list(self):
        from genesis.skill_engine import retrieve
        results = retrieve("web search Arabic platforms")
        self.assertIsInstance(results, list)

    def test_health_check_returns_report(self):
        from genesis.skill_engine import health_check
        report = health_check()
        self.assertIsInstance(report, HealthReport)
        self.assertIsInstance(report.total_skills, int)

    def test_run_maintenance_returns_int(self):
        from genesis.skill_engine import run_maintenance
        n = run_maintenance()
        self.assertIsInstance(n, int)
        self.assertGreaterEqual(n, 0)


# ─── Integration: Web Search Arabic Skill ────────────────────────────────────

class TestWebSearchArabicSkill(unittest.TestCase):
    """Test the actual web_search_arabic skill in genesis/skill_engine/skills/."""

    def test_skill_folder_exists(self):
        skill_dir = Path(__file__).parent.parent / "genesis/skill_engine/skills/web_search_arabic"
        self.assertTrue(skill_dir.exists(), f"Skill dir not found: {skill_dir}")

    def test_skill_md_exists(self):
        skill_dir = Path(__file__).parent.parent / "genesis/skill_engine/skills/web_search_arabic"
        self.assertTrue((skill_dir / "SKILL.md").exists())

    def test_skill_md_valid(self):
        skill_dir = Path(__file__).parent.parent / "genesis/skill_engine/skills/web_search_arabic"
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("web_search_arabic", content)
        self.assertIn("When to use", content)
        self.assertIn("Workflow", content)

    def test_skill_scripts_exist(self):
        skill_dir = Path(__file__).parent.parent / "genesis/skill_engine/skills/web_search_arabic"
        scripts_dir = skill_dir / "scripts"
        self.assertTrue(scripts_dir.exists())
        self.assertTrue((scripts_dir / "search.py").exists())

    def test_skill_tests_exist(self):
        skill_dir = Path(__file__).parent.parent / "genesis/skill_engine/skills/web_search_arabic"
        tests_dir = skill_dir / "tests"
        self.assertTrue(tests_dir.exists())

    def test_memory_file_exists(self):
        skill_dir = Path(__file__).parent.parent / "genesis/skill_engine/skills/web_search_arabic"
        self.assertTrue((skill_dir / ".memory.md").exists())

    def test_skill_loadable_from_path(self):
        skill_dir = Path(__file__).parent.parent / "genesis/skill_engine/skills/web_search_arabic"
        skill = SkillFolder.from_path(skill_dir)
        self.assertEqual(skill.name, "web_search_arabic")
        self.assertEqual(skill.domain, "research")

    def test_validate_structure(self):
        skill_dir = Path(__file__).parent.parent / "genesis/skill_engine/skills/web_search_arabic"
        issues = SkillFolder.validate_structure(skill_dir)
        self.assertEqual(issues, [], f"Validation issues: {issues}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
