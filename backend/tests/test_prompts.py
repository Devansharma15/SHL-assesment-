"""Tests for prompt templates."""

from agent.prompts import (
    BASE_SYSTEM_PROMPT,
    RECOMMENDATION_PROMPT,
    COMPARISON_PROMPT,
    REFINEMENT_PROMPT,
    build_recommendation_prompt,
    build_comparison_prompt,
    build_refinement_prompt,
    format_catalog_context
)
from agent.conversation_analyzer import ConversationAnalyzer


def test_format_catalog_context():
    """Test that catalog data is correctly formatted into a string."""
    catalog = [
        {
            "name": "Test A",
            "link": "http://a.com",
            "keys": ["Cognitive"],
            "duration": "10 mins",
            "job_levels": ["Entry", "Mid"],
            "description": "Desc A"
        }
    ]
    
    formatted = format_catalog_context(catalog)
    assert "NAME: Test A" in formatted
    assert "URL: http://a.com" in formatted
    assert "TYPE: Cognitive" in formatted
    assert "DURATION: 10 mins" in formatted
    assert "JOB LEVELS: Entry, Mid" in formatted


def test_build_recommendation_prompt():
    """Test recommendation prompt builder."""
    state = ConversationAnalyzer.analyze([
        {"role": "user", "content": "I need a java test for a senior dev."}
    ])
    
    prompt = build_recommendation_prompt(state, "CATALOG_DATA_HERE")
    
    # Should include base prompt
    assert "YOUR IDENTITY" in prompt
    assert "OUTPUT FORMAT" in prompt
    
    # Should include requirements
    assert "Seniority: Professional Individual Contributor" in prompt
    assert "Skills: java" in prompt
    
    # Should include catalog
    assert "CATALOG_DATA_HERE" in prompt


def test_build_comparison_prompt():
    """Test comparison prompt builder."""
    prompt = build_comparison_prompt("CATALOG_DATA_HERE")
    
    assert "YOUR IDENTITY" in prompt
    assert "PURPOSE: Compare two or more" in prompt
    assert "CATALOG_DATA_HERE" in prompt


def test_build_refinement_prompt():
    """Test refinement prompt builder."""
    state = ConversationAnalyzer.analyze([
        {"role": "user", "content": "I need a test."},
        {"role": "assistant", "content": "I recommend Test A."},
        {"role": "user", "content": "Also need java."}
    ])
    
    prompt = build_refinement_prompt(state, "CATALOG_DATA_HERE")
    
    assert "YOUR IDENTITY" in prompt
    assert "PURPOSE: Update previous recommendations" in prompt
    assert "java" in prompt
    assert "CATALOG_DATA_HERE" in prompt
