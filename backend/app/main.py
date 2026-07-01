"""FastAPI application factory and lifecycle management."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware import RequestLoggingMiddleware, TimeoutMiddleware
from api.routes import router
from app.config import settings
from agent.orchestrator import AgentOrchestrator
from retrievers.hybrid_retriever import HybridRetriever
from retrievers.reranker import CrossEncoderReranker
from services.chat_service import ChatService
from vectorstore.bm25_store import BM25Store
from vectorstore.faiss_store import FAISSStore

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Global service instances (initialized on startup)
_chat_service: ChatService | None = None


def get_chat_service() -> ChatService:
    """Get the global ChatService instance."""
    if _chat_service is None:
        raise RuntimeError(
            "ChatService not initialized. Application may not have started properly."
        )
    return _chat_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler: initializes services on startup, cleans up on shutdown."""
    global _chat_service

    logger.info("=" * 60)
    logger.info("SHL Assessment Recommender — Starting up...")
    logger.info("=" * 60)

    # Initialize vector stores
    logger.info("Initializing FAISS vector store...")
    faiss_store = FAISSStore()
    faiss_store.initialize()
    logger.info("Pre-loading embedding model...")
    _ = faiss_store.embedding_service.model

    logger.info("Initializing BM25 keyword store...")
    bm25_store = BM25Store()
    bm25_store.initialize()

    # Initialize hybrid retriever
    logger.info("Initializing hybrid retriever...")
    retriever = HybridRetriever(
        faiss_store=faiss_store,
        bm25_store=bm25_store,
        semantic_top_k=settings.semantic_top_k,
        keyword_top_k=settings.keyword_top_k,
        rrf_k=settings.rrf_k,
    )

    # Initialize reranker
    logger.info("Initializing cross-encoder reranker...")
    reranker = CrossEncoderReranker(model_name=settings.reranker_model)
    logger.info("Pre-loading cross-encoder model...")
    _ = reranker.model

    # Initialize Agent Orchestrator
    logger.info("Initializing AI Agent Orchestrator...")
    orchestrator = AgentOrchestrator()

    # Build chat service
    _chat_service = ChatService(
        retriever=retriever,
        reranker=reranker,
        catalog=faiss_store.catalog,
        orchestrator=orchestrator,
    )

    logger.info("All services initialized successfully.")
    logger.info("=" * 60)

    yield  # Application is running

    # Cleanup
    logger.info("Shutting down SHL Assessment Recommender...")
    _chat_service = None


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="SHL Assessment Recommender API",
        description=(
            "Conversational AI assistant that helps HR professionals find "
            "the right SHL assessments for their talent evaluation needs."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TimeoutMiddleware)

    # Register routes
    app.include_router(router)

    return app


# Create the application instance
app = create_app()
