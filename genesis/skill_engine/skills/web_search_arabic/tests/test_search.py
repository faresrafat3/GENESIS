"""Tests for web_search_arabic skill."""
import sys
import os


def test_skill_md_exists():
    """SKILL.md must exist."""
    skill_dir = os.path.dirname(os.path.dirname(__file__))
    assert os.path.exists(os.path.join(skill_dir, "SKILL.md"))


def test_script_exists():
    """search.py must exist."""
    skill_dir = os.path.dirname(os.path.dirname(__file__))
    assert os.path.exists(os.path.join(skill_dir, "scripts", "search.py"))


def test_search_function_importable():
    """search_with_evidence must be importable."""
    skill_dir = os.path.dirname(os.path.dirname(__file__))
    scripts_dir = os.path.join(skill_dir, "scripts")
    sys.path.insert(0, scripts_dir)
    try:
        from search import search_with_evidence
        assert callable(search_with_evidence)
    finally:
        sys.path.pop(0)


def test_search_returns_dict():
    """search_with_evidence returns dict with expected keys."""
    skill_dir = os.path.dirname(os.path.dirname(__file__))
    scripts_dir = os.path.join(skill_dir, "scripts")
    sys.path.insert(0, scripts_dir)
    try:
        from search import search_with_evidence
        # Run without API key — should return gracefully
        result = search_with_evidence("test query")
        assert isinstance(result, dict)
        # Should have results key (even if empty due to no API key)
        assert "results" in result or "error" in result
    finally:
        sys.path.pop(0)
