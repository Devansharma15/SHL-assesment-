"""Enumerations for assessment types and agent intents."""

from enum import StrEnum


class TestType(StrEnum):
    """SHL assessment test types."""

    COGNITIVE_ABILITY = "Cognitive Ability"
    PERSONALITY = "Personality Assessment"
    BEHAVIORAL = "Behavioral Assessment"
    SKILLS_SIMULATION = "Skills Simulation"
    KNOWLEDGE_TEST = "Knowledge Test"
    SKILLS_TEST = "Skills Test"
    LANGUAGE = "Language Assessment"
    INTERVIEW = "Interview"
    MULTI_MEASURE = "Multi-Measure"


class AssessmentCategory(StrEnum):
    """Assessment category groupings."""

    ABILITY_APTITUDE = "Ability & Aptitude"
    PERSONALITY_BEHAVIOR = "Personality & Behavior"
    SITUATIONAL_JUDGEMENT = "Situational Judgement"
    TECHNICAL_SKILLS = "Technical Skills"
    JOB_SIMULATION = "Job Simulation"
    INTERVIEW_SOLUTIONS = "Interview Solutions"
    BASIC_SKILLS = "Basic Skills"
    LANGUAGE_SKILLS = "Language Skills"
    ROLE_SPECIFIC = "Role-Specific"
    COMPREHENSIVE = "Comprehensive"
    SAFETY_COMPLIANCE = "Safety & Compliance"
    LEADERSHIP = "Leadership"


class AgentIntent(StrEnum):
    """Detected user intent for agent routing."""

    RECOMMENDATION = "recommendation"
    CLARIFICATION = "clarification"
    REFINEMENT = "refinement"
    COMPARISON = "comparison"
    GREETING = "greeting"
    OFF_TOPIC = "off_topic"
    PROMPT_INJECTION = "prompt_injection"
    UNKNOWN = "unknown"


class ConversationStage(StrEnum):
    """Current stage of the conversation flow."""

    GREETING = "greeting"
    GATHERING = "gathering"
    RECOMMENDING = "recommending"
    REFINING = "refining"
    COMPARING = "comparing"
    COMPLETE = "complete"


class ConfidenceLevel(StrEnum):
    """Confidence level for recommendations."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
