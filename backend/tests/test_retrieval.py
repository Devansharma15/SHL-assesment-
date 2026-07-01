"""Unit tests for the retrieval pipeline."""

from __future__ import annotations

from retrievers.hybrid_retriever import HybridRetriever
from retrievers.query_rewriter import QueryRewriter


class TestQueryRewriter:
    """Test query rewriting and context extraction."""

    def test_extracts_latest_user_message(self):
        messages = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "Answer"},
            {"role": "user", "content": "Follow-up question"},
        ]
        result = QueryRewriter.extract_latest_query(messages)
        assert result == "Follow-up question"

    def test_extracts_seniority_context(self):
        messages = [
            {"role": "user", "content": "I need a senior developer assessment"},
        ]
        context = QueryRewriter.extract_conversation_context(messages)
        assert context["seniority"] == "Senior"

    def test_extracts_entry_level(self):
        messages = [
            {"role": "user", "content": "Looking for graduate program assessments"},
        ]
        context = QueryRewriter.extract_conversation_context(messages)
        assert context["seniority"] == "Entry Level"

    def test_detects_comparison_request(self):
        assert QueryRewriter.is_comparison_request("Compare OPQ and Verify G+") is True
        assert QueryRewriter.is_comparison_request("What's the difference between these?") is True
        assert QueryRewriter.is_comparison_request("I need Java tests") is False

    def test_detects_refinement_request(self):
        assert QueryRewriter.is_refinement_request("Add personality tests") is True
        assert QueryRewriter.is_refinement_request("Also include coding tests") is True
        assert QueryRewriter.is_refinement_request("I need Java tests") is False

    def test_builds_enriched_query(self):
        messages = [
            {"role": "user", "content": "I'm hiring for a senior role"},
            {"role": "assistant", "content": "What kind of assessments?"},
            {"role": "user", "content": "I need coding tests for Java"},
        ]
        query = QueryRewriter.build_search_query(messages)
        assert "coding" in query.lower() or "java" in query.lower()
        assert "senior" in query.lower()


class TestReciprocalRankFusion:
    """Test the RRF algorithm."""

    def test_rrf_merges_results(self):
        list1 = [
            {"assessment": {"id": "a"}, "score": 0.9},
            {"assessment": {"id": "b"}, "score": 0.8},
            {"assessment": {"id": "c"}, "score": 0.7},
        ]
        list2 = [
            {"assessment": {"id": "b"}, "score": 5.0},
            {"assessment": {"id": "d"}, "score": 4.0},
            {"assessment": {"id": "a"}, "score": 3.0},
        ]

        fused = HybridRetriever.reciprocal_rank_fusion([list1, list2], k=60)

        # 'a' and 'b' appear in both lists, should have higher RRF scores
        ids = [r["assessment"]["id"] for r in fused]
        assert "a" in ids
        assert "b" in ids
        assert "c" in ids
        assert "d" in ids

        # 'b' appears at rank 1 in list1 and rank 0 in list2, should score highest
        assert fused[0]["assessment"]["id"] in ("a", "b")

    def test_rrf_handles_empty_lists(self):
        result = HybridRetriever.reciprocal_rank_fusion([[], []])
        assert result == []

    def test_rrf_handles_single_list(self):
        results = [{"assessment": {"id": "x"}, "score": 1.0}]
        fused = HybridRetriever.reciprocal_rank_fusion([results])
        assert len(fused) == 1
        assert fused[0]["assessment"]["id"] == "x"
