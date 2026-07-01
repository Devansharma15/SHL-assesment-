"""Requirement Extractor — Module 4.

Extracts structured hiring requirements from natural language messages.
Uses keyword dictionaries and pattern matching for entity extraction.

Purpose:
    Convert unstructured user messages into a structured HiringRequirements
    object that downstream modules (clarification, retrieval, recommendation)
    can consume.

Inputs:
    - messages: Full conversation history.

Outputs:
    - HiringRequirements dataclass with all extracted entities.

Dependencies:
    None (pure Python, no LLM).

Failure Cases:
    - Ambiguous role names → stored as raw text, LLM disambiguates later.
    - Multiple conflicting values → last mention wins (most recent context).

Engineering Trade-offs:
    - Keyword-based extraction over NER: simpler, faster, sufficient for
      the bounded domain of HR/assessment hiring vocabulary.
    - Incremental merging across turns preserves conversational continuity.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class HiringRequirements:
    """Structured representation of extracted hiring requirements."""

    role: str | None = None
    industry: str | None = None
    experience: str | None = None
    seniority: str | None = None
    technical_skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    leadership_required: bool = False
    personality_required: bool = False
    languages: list[str] = field(default_factory=list)
    remote_preference: bool | None = None
    adaptive_preference: bool | None = None
    volume_hiring: bool = False
    purpose: str | None = None  # screening, development, succession
    assessment_types: list[str] = field(default_factory=list)
    duration_constraint: str | None = None
    candidate_count: str | None = None
    raw_context: str = ""

    @property
    def completeness_score(self) -> float:
        """Score from 0.0–1.0 indicating how complete the requirements are.

        Weighted by information value:
        - Role: 0.35 (most important)
        - Seniority: 0.15
        - Skills (any): 0.20
        - Assessment type preference: 0.15
        - Purpose/industry/other: 0.15
        """
        score = 0.0

        if self.role:
            score += 0.35
        if self.seniority:
            score += 0.15
        if self.technical_skills or self.soft_skills:
            score += 0.20
        if self.assessment_types:
            score += 0.15
        if self.purpose or self.industry or self.volume_hiring or self.leadership_required:
            score += 0.15

        return min(score, 1.0)

    @property
    def missing_fields(self) -> list[str]:
        """Return list of high-value fields that are still missing."""
        missing = []
        if not self.role:
            missing.append("role")
        if not self.seniority:
            missing.append("seniority")
        if not self.technical_skills and not self.soft_skills:
            missing.append("skills")
        if not self.assessment_types:
            missing.append("assessment_types")
        if not self.purpose:
            missing.append("purpose")
        return missing


class RequirementExtractor:
    """Extracts structured hiring requirements from conversation messages.

    Uses layered keyword matching and pattern recognition to parse
    natural language into the HiringRequirements structure.
    Merges incrementally across conversation turns.
    """

    # --- Seniority keyword mapping ---
    SENIORITY_MAP: dict[str, str] = {
        "entry": "Entry-Level",
        "entry-level": "Entry-Level",
        "entry level": "Entry-Level",
        "junior": "Entry-Level",
        "graduate": "Graduate",
        "grad": "Graduate",
        "intern": "Entry-Level",
        "mid": "Mid-Professional",
        "mid-level": "Mid-Professional",
        "mid level": "Mid-Professional",
        "intermediate": "Mid-Professional",
        "senior": "Professional Individual Contributor",
        "lead": "Professional Individual Contributor",
        "principal": "Professional Individual Contributor",
        "staff": "Professional Individual Contributor",
        "manager": "Manager",
        "management": "Manager",
        "supervisor": "Supervisor",
        "director": "Director",
        "executive": "Executive",
        "c-suite": "Executive",
        "c suite": "Executive",
        "vp": "Executive",
        "vice president": "Executive",
        "front line": "Front Line Manager",
        "frontline": "Front Line Manager",
    }

    # --- Technical skills ---
    TECHNICAL_SKILLS: set[str] = {
        "java", "python", "javascript", "typescript", "c#", "c++", "go", "golang",
        "ruby", "rust", "swift", "kotlin", "scala", "php", "r", "sql", "nosql",
        "html", "css", "react", "angular", "vue", "node", "nodejs", "django",
        "flask", "spring", ".net", "dotnet", "aws", "azure", "gcp", "docker",
        "kubernetes", "devops", "ci/cd", "git", "linux", "networking",
        "machine learning", "ml", "ai", "data science", "data analysis",
        "data engineering", "cloud", "cybersecurity", "security", "blockchain",
        "mobile", "ios", "android", "api", "rest", "graphql", "microservices",
        "agile", "scrum", "project management", "salesforce", "sap", "erp",
        "excel", "power bi", "tableau", "analytics", "statistics",
        "coding", "programming", "software", "web development",
    }

    # --- Soft skills ---
    SOFT_SKILLS: set[str] = {
        "communication", "teamwork", "collaboration", "leadership",
        "problem solving", "problem-solving", "critical thinking",
        "analytical", "analytical thinking", "creativity", "innovation",
        "time management", "adaptability", "flexibility", "work ethic",
        "interpersonal", "negotiation", "presentation", "public speaking",
        "emotional intelligence", "decision making", "decision-making",
        "conflict resolution", "customer service", "empathy", "attention to detail",
        "strategic thinking", "mentoring", "coaching",
    }

    # --- Industry keywords ---
    INDUSTRY_MAP: dict[str, str] = {
        "bank": "Banking & Finance",
        "banking": "Banking & Finance",
        "finance": "Banking & Finance",
        "financial": "Banking & Finance",
        "insurance": "Insurance",
        "healthcare": "Healthcare",
        "health": "Healthcare",
        "medical": "Healthcare",
        "pharma": "Pharmaceutical",
        "pharmaceutical": "Pharmaceutical",
        "tech": "Technology",
        "technology": "Technology",
        "software": "Technology",
        "it": "Technology",
        "retail": "Retail",
        "ecommerce": "Retail",
        "e-commerce": "Retail",
        "manufacturing": "Manufacturing",
        "automotive": "Automotive",
        "telecom": "Telecommunications",
        "telecommunications": "Telecommunications",
        "consulting": "Consulting",
        "government": "Government",
        "public sector": "Government",
        "education": "Education",
        "energy": "Energy",
        "oil": "Energy",
        "gas": "Energy",
        "logistics": "Logistics",
        "supply chain": "Logistics",
        "media": "Media & Entertainment",
        "hospitality": "Hospitality",
        "real estate": "Real Estate",
        "construction": "Construction",
        "legal": "Legal",
        "nonprofit": "Nonprofit",
        "fmcg": "FMCG",
        "consumer goods": "FMCG",
        "call center": "Contact Center",
        "call centre": "Contact Center",
        "contact center": "Contact Center",
        "contact centre": "Contact Center",
        "bpo": "Contact Center",
    }

    # --- Assessment type keywords ---
    ASSESSMENT_TYPE_MAP: dict[str, str] = {
        "cognitive": "Ability & Aptitude",
        "aptitude": "Ability & Aptitude",
        "numerical": "Ability & Aptitude",
        "verbal": "Ability & Aptitude",
        "reasoning": "Ability & Aptitude",
        "logical": "Ability & Aptitude",
        "personality": "Personality & Behavior",
        "behavioral": "Personality & Behavior",
        "behaviour": "Personality & Behavior",
        "opq": "Personality & Behavior",
        "situational": "Biodata & Situational Judgment",
        "sjt": "Biodata & Situational Judgment",
        "judgement": "Biodata & Situational Judgment",
        "judgment": "Biodata & Situational Judgment",
        "coding": "Knowledge & Skills",
        "programming": "Knowledge & Skills",
        "technical test": "Knowledge & Skills",
        "knowledge test": "Knowledge & Skills",
        "simulation": "Simulations",
        "interview": "Interview",
        "360": "Development & 360",
        "development": "Development & 360",
    }

    # --- Purpose patterns ---
    PURPOSE_PATTERNS: list[tuple[re.Pattern, str]] = [
        (re.compile(r"\b(screen|screening|filter|shortlist)\b", re.I), "screening"),
        (re.compile(r"\b(develop|development|growth|coaching|training)\b", re.I), "development"),
        (re.compile(r"\b(succession|promotion|internal mobility)\b", re.I), "succession"),
        (re.compile(r"\b(hiring|recruit|recruitment|talent acquisition)\b", re.I), "hiring"),
        (re.compile(r"\b(volume|bulk|mass|high.volume|large.scale)\b", re.I), "volume_hiring"),
    ]

    @classmethod
    def extract(cls, messages: list[dict]) -> HiringRequirements:
        """Extract hiring requirements from all user messages.

        Processes messages chronologically so that later messages
        can refine or override earlier extractions.

        Args:
            messages: Full conversation history.

        Returns:
            Populated HiringRequirements.
        """
        reqs = HiringRequirements()
        all_user_text_parts: list[str] = []

        for msg in messages:
            if msg.get("role") != "user":
                continue

            content = msg["content"]
            all_user_text_parts.append(content)
            content_lower = content.lower()

            # Extract seniority
            cls._extract_seniority(content_lower, reqs)

            # Extract industry
            cls._extract_industry(content_lower, reqs)

            # Extract technical skills
            cls._extract_technical_skills(content_lower, reqs)

            # Extract soft skills
            cls._extract_soft_skills(content_lower, reqs)

            # Extract assessment type preferences
            cls._extract_assessment_types(content_lower, reqs)

            # Extract purpose
            cls._extract_purpose(content_lower, reqs)

            # Extract role (heuristic: noun phrases after "hire/hiring/need/looking for")
            cls._extract_role(content, reqs)

            # Extract boolean flags
            cls._extract_flags(content_lower, reqs)

            # Extract candidate count
            cls._extract_candidate_count(content, reqs)

        reqs.raw_context = " | ".join(all_user_text_parts)

        logger.debug(
            "Extracted requirements: role=%s, seniority=%s, skills=%d tech + %d soft, "
            "score=%.2f, missing=%s",
            reqs.role,
            reqs.seniority,
            len(reqs.technical_skills),
            len(reqs.soft_skills),
            reqs.completeness_score,
            reqs.missing_fields,
        )

        return reqs

    @classmethod
    def _extract_seniority(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract seniority level from text."""
        for keyword, level in cls.SENIORITY_MAP.items():
            if keyword in text:
                reqs.seniority = level
                return  # First match wins (ordered by specificity in dict)

    @classmethod
    def _extract_industry(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract industry from text."""
        for keyword, industry in cls.INDUSTRY_MAP.items():
            if keyword in text:
                reqs.industry = industry
                return

    @classmethod
    def _extract_technical_skills(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract technical skills mentioned in text."""
        for skill in cls.TECHNICAL_SKILLS:
            # Use word boundary check for short skills to avoid false positives
            if len(skill) <= 3:
                if re.search(rf"\b{re.escape(skill)}\b", text, re.I):
                    if skill not in reqs.technical_skills:
                        reqs.technical_skills.append(skill)
            else:
                if skill in text and skill not in reqs.technical_skills:
                    reqs.technical_skills.append(skill)

    @classmethod
    def _extract_soft_skills(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract soft skills mentioned in text."""
        for skill in cls.SOFT_SKILLS:
            if skill in text and skill not in reqs.soft_skills:
                reqs.soft_skills.append(skill)

    @classmethod
    def _extract_assessment_types(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract assessment type preferences from text."""
        for keyword, atype in cls.ASSESSMENT_TYPE_MAP.items():
            if keyword in text and atype not in reqs.assessment_types:
                reqs.assessment_types.append(atype)

    @classmethod
    def _extract_purpose(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract hiring purpose from text."""
        for pattern, purpose in cls.PURPOSE_PATTERNS:
            if pattern.search(text):
                if purpose == "volume_hiring":
                    reqs.volume_hiring = True
                else:
                    reqs.purpose = purpose

    @classmethod
    def _extract_role(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract job role using heuristic patterns."""
        # Clean up common misleading phrases
        clean_text = re.sub(r"\b(i need a test for|looking for a test for)\b", "hiring", text, flags=re.I)
        clean_text = re.sub(r"\b(need to hire)\b", "hiring", clean_text, flags=re.I)

        role_patterns = [
            re.compile(
                r"(?:hir(?:e|ing)|looking\s+for|assess(?:ing)?|recruit(?:ing)?)"
                r"\s+(?:a\s+|an\s+|the\s+)?(.+?)(?:\s+(?:position|role|candidate|for|who|with|at|in)\b|[.,;!?]|$)",
                re.I,
            ),
            re.compile(
                r"\b(?:for\s+(?:a\s+|an\s+|the\s+)?)(.+?)\s+(?:position|role|job)\b",
                re.I,
            ),
            re.compile(
                r"\b([\w\s\-]+?\s+(?:developer|engineer|analyst|manager|specialist|consultant|designer|architect|scientist|administrator))\b",
                re.I,
            ),
        ]

        for pattern in role_patterns:
            match = pattern.search(clean_text)
            if match:
                role_candidate = match.group(1).strip().rstrip(".,;!?")
                
                # Filter out generic bad matches
                bad_words = {"test", "assessment", "tool", "platform", "solution"}
                if role_candidate.lower() in bad_words:
                    continue
                    
                if role_candidate and len(role_candidate) > 2:
                    reqs.role = role_candidate
                    return

    @classmethod
    def _extract_flags(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract boolean flags from text."""
        if re.search(r"\b(remote|work\s+from\s+home|wfh|virtual|distributed)\b", text, re.I):
            reqs.remote_preference = True
        if re.search(r"\b(on.?site|in.?office|office.?based)\b", text, re.I):
            reqs.remote_preference = False
        if re.search(r"\b(adaptive|computer.?adaptive|cat)\b", text, re.I):
            reqs.adaptive_preference = True
        if re.search(r"\b(leader|leadership|managerial|manage\s+team)\b", text, re.I):
            reqs.leadership_required = True
        if re.search(r"\b(personality|behavioral|behaviour|character|trait)\b", text, re.I):
            reqs.personality_required = True

    @classmethod
    def _extract_candidate_count(cls, text: str, reqs: HiringRequirements) -> None:
        """Extract candidate volume information."""
        count_match = re.search(r"(\d+)\s*(?:candidates?|people|hires?|positions?)", text, re.I)
        if count_match:
            count = int(count_match.group(1))
            reqs.candidate_count = str(count)
            if count >= 50:
                reqs.volume_hiring = True
