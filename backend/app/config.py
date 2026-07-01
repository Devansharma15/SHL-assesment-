"""Application configuration via environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- LLM Provider ---
    llm_provider: str = "gemini"
    llm_model: str = "gemini-1.5-pro"
    gemini_api_key: str = ""

    # --- LLM Generation ---
    llm_temperature: float = 0.1
    llm_max_output_tokens: int = 4096
    llm_retry_attempts: int = 3
    llm_retry_base_delay: float = 1.0

    # --- Embedding & Reranking ---
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # --- Application ---
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    log_level: str = "INFO"
    max_turns: int = 8
    response_timeout_seconds: int = 30
    max_message_length: int = 5000

    # --- Retrieval ---
    semantic_top_k: int = 20
    keyword_top_k: int = 20
    reranker_top_k: int = 10
    rrf_k: int = 60

    # --- Agent Tuning ---
    clarification_readiness_threshold: float = 0.4
    min_retrieval_confidence: float = 0.1
    max_clarification_turns: int = 3

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# Singleton instance
settings = Settings()
