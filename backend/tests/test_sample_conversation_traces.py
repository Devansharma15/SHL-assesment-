"""Regression tests based on the provided sample conversation traces."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.orchestrator import AgentOrchestrator


CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "shl_product_catalog.json"


class FakeRetriever:
    def search(self, query: str):
        return []


class FakeReranker:
    def rerank(self, query: str, candidates: list[dict]):
        return candidates


@pytest.fixture(scope="module")
def catalog():
    with open(CATALOG_PATH, encoding="utf-8") as file:
        return json.load(file)


async def _ask(messages: list[dict], catalog: list[dict]) -> dict:
    orchestrator = AgentOrchestrator()
    return await orchestrator.process(
        messages=messages,
        retriever=FakeRetriever(),
        reranker=FakeReranker(),
        catalog=catalog,
    )


def _names(response: dict) -> list[str]:
    return [rec["name"] for rec in response["recommendations"]]


def _append(messages: list[dict], response: dict) -> list[dict]:
    return [*messages, {"role": "assistant", "content": response["reply"]}]


@pytest.mark.asyncio
async def test_c1_senior_leadership_clarifies_then_recommends(catalog):
    messages = [{"role": "user", "content": "We need a solution for senior leadership."}]
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []
    assert response["end_of_conversation"] is False

    messages = _append(messages, response)
    messages.append(
        {
            "role": "user",
            "content": "The pool consists of CXOs, director-level positions; people with more than 15 years of experience.",
        }
    )
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []

    messages = _append(messages, response)
    messages.append(
        {"role": "user", "content": "Selection - comparing candidates against a leadership benchmark."}
    )
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "Occupational Personality Questionnaire OPQ32r",
        "OPQ Universal Competency Report 2.0",
        "OPQ Leadership Report",
    ]


@pytest.mark.asyncio
async def test_c2_rust_missing_specific_test_then_builds_shortlist(catalog):
    messages = [
        {
            "role": "user",
            "content": "I'm hiring a senior Rust engineer for high-performance networking infrastructure. What assessments should I use?",
        }
    ]
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []
    assert "Rust-specific" in response["reply"]

    messages = _append(messages, response)
    messages.append({"role": "user", "content": "Yes, go ahead. Should I also add a cognitive test for this level?"})
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "Smart Interview Live Coding",
        "Linux Programming (General)",
        "Networking and Implementation (New)",
        "SHL Verify Interactive G+",
        "Occupational Personality Questionnaire OPQ32r",
    ]


@pytest.mark.asyncio
async def test_c3_contact_center_language_and_accent_gating(catalog):
    messages = [
        {
            "role": "user",
            "content": "We're screening 500 entry-level contact centre agents. Inbound calls, customer service focus. What should we use?",
        }
    ]
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []
    assert "language" in response["reply"].lower()

    messages = _append(messages, response)
    messages.append({"role": "user", "content": "English."})
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []
    assert "accent" in response["reply"].lower()

    messages = _append(messages, response)
    messages.append({"role": "user", "content": "US."})
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "SVAR - Spoken English (US) (New)",
        "Contact Center Call Simulation (New)",
        "Entry Level Customer Serv-Retail & Contact Center",
        "Customer Service Phone Simulation",
    ]


@pytest.mark.asyncio
async def test_c4_graduate_financial_analyst_refines_with_sjt(catalog):
    messages = [
        {
            "role": "user",
            "content": (
                "Hiring graduate financial analysts - final-year students, no work experience. "
                "We need numerical reasoning and a finance knowledge test."
            ),
        }
    ]
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "SHL Verify Interactive – Numerical Reasoning",
        "Financial Accounting (New)",
        "Basic Statistics (New)",
        "Occupational Personality Questionnaire OPQ32r",
    ]

    messages = _append(messages, response)
    messages.append(
        {
            "role": "user",
            "content": "Can you also add a situational judgement element for work-context decision making?",
        }
    )
    response = await _ask(messages, catalog)
    assert "Graduate Scenarios" in _names(response)


@pytest.mark.asyncio
async def test_c5_sales_audit_and_opq_sales_comparison(catalog):
    messages = [
        {
            "role": "user",
            "content": "As part of annual talent audit, we need to re-skill our Sales organization.",
        }
    ]
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "Global Skills Assessment",
        "Global Skills Development Report",
        "Occupational Personality Questionnaire OPQ32r",
        "OPQ MQ Sales Report",
        "Sales Transformation 2.0 - Individual Contributor",
    ]

    messages = _append(messages, response)
    messages.append({"role": "user", "content": "What's the difference between OPQ and OPQ MQ Sales Report?"})
    response = await _ask(messages, catalog)
    assert response["end_of_conversation"] is False
    assert response["reply"]


@pytest.mark.asyncio
async def test_c6_safety_critical_industrial_refinement(catalog):
    messages = [
        {
            "role": "user",
            "content": (
                "We're hiring plant operators for a chemical facility. Safety is top priority - "
                "reliability and procedure compliance."
            ),
        }
    ]
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "Dependability and Safety Instrument (DSI)",
        "Manufac. & Indust. - Safety & Dependability 8.0",
        "Workplace Health and Safety (New)",
    ]

    messages = _append(messages, response)
    messages.append({"role": "user", "content": "We're industrial. The 8.0 bundle is the right fit. Confirmed."})
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "Manufac. & Indust. - Safety & Dependability 8.0",
        "Workplace Health and Safety (New)",
    ]
    assert response["end_of_conversation"] is True


@pytest.mark.asyncio
async def test_c7_legal_question_refuses_without_losing_shortlist(catalog):
    messages = [
        {
            "role": "user",
            "content": "They're functionally bilingual - English fluent for written work. Go with the hybrid for healthcare admin staff handling HIPAA patient records.",
        }
    ]
    response = await _ask(messages, catalog)
    assert "HIPAA (Security)" in _names(response)

    messages = _append(messages, response)
    messages.append(
        {
            "role": "user",
            "content": "Are we legally required under HIPAA to test all staff who touch patient records?",
        }
    )
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []
    assert "legal" in response["reply"].lower() or "compliance" in response["reply"].lower()

    messages = _append(messages, response)
    messages.append({"role": "user", "content": "Understood. Keep the shortlist as-is."})
    response = await _ask(messages, catalog)
    assert "HIPAA (Security)" in _names(response)
    assert response["end_of_conversation"] is True


@pytest.mark.asyncio
async def test_c8_admin_assistant_excel_word_simulation_refinement(catalog):
    messages = [
        {
            "role": "user",
            "content": "I need to quickly screen admin assistants for Excel and Word daily.",
        }
    ]
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "MS Excel (New)",
        "MS Word (New)",
        "Occupational Personality Questionnaire OPQ32r",
    ]

    messages = _append(messages, response)
    messages.append(
        {
            "role": "user",
            "content": "In that case, I am OK with adding a simulation - we want to capture the capabilities.",
        }
    )
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "Microsoft Excel 365 (New)",
        "Microsoft Word 365 (New)",
        "MS Excel (New)",
        "MS Word (New)",
        "Occupational Personality Questionnaire OPQ32r",
    ]


@pytest.mark.asyncio
async def test_c9_full_stack_jd_clarifies_and_refines(catalog):
    messages = [
        {
            "role": "user",
            "content": (
                'Here is the JD: "Senior Full-Stack Engineer - Core Java, Spring, REST API design, '
                'Angular, SQL, AWS, Docker, microservice delivery." Can you recommend a battery?'
            ),
        }
    ]
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []
    assert "backend" in response["reply"].lower()

    messages = _append(messages, response)
    messages.append(
        {
            "role": "user",
            "content": "Backend-leaning. Day-one priorities are Core Java and Spring; SQL is constant.",
        }
    )
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []
    assert "senior" in response["reply"].lower()

    messages = _append(messages, response)
    messages.append(
        {
            "role": "user",
            "content": "Senior IC. They lead design on their own services but don't manage other engineers directly.",
        }
    )
    response = await _ask(messages, catalog)
    assert _names(response)[:4] == [
        "Core Java (Advanced Level) (New)",
        "Spring (New)",
        "RESTful Web Services (New)",
        "SQL (New)",
    ]

    messages = _append(messages, response)
    messages.append(
        {
            "role": "user",
            "content": "Add AWS and Docker. Drop REST - the API design signal will already come through in Spring.",
        }
    )
    response = await _ask(messages, catalog)
    names = _names(response)
    assert "RESTful Web Services (New)" not in names
    assert "Amazon Web Services (AWS) Development (New)" in names
    assert "Docker (New)" in names


@pytest.mark.asyncio
async def test_c10_can_drop_opq_after_no_shorter_replacement(catalog):
    messages = [
        {
            "role": "user",
            "content": "We run a graduate management trainee scheme. Need cognitive, personality, and situational judgement.",
        }
    ]
    response = await _ask(messages, catalog)
    assert _names(response) == [
        "SHL Verify Interactive G+",
        "Occupational Personality Questionnaire OPQ32r",
        "Graduate Scenarios",
    ]

    messages = _append(messages, response)
    messages.append(
        {
            "role": "user",
            "content": "Can you remove the OPQ32r and replace it with something shorter?",
        }
    )
    response = await _ask(messages, catalog)
    assert response["recommendations"] == []
    assert "shorter" in response["reply"].lower()

    messages = _append(messages, response)
    messages.append({"role": "user", "content": "Drop the OPQ. Final list: Verify G+ and Graduate Scenarios."})
    response = await _ask(messages, catalog)
    assert _names(response) == ["SHL Verify Interactive G+", "Graduate Scenarios"]
    assert response["end_of_conversation"] is True
