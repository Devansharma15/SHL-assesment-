import asyncio
import json
import logging
from agent.orchestrator import AgentOrchestrator
from retrievers.hybrid_retriever import HybridRetriever
from retrievers.reranker import CrossEncoderReranker

# configure logging so we can see output
logging.basicConfig(level=logging.DEBUG)

async def main():
    catalog = json.load(open('data/shl_product_catalog.json', encoding='utf-8'))
    orchestrator = AgentOrchestrator()
    messages = [{'role': 'user', 'content': 'i want to hire .net developer'}]
    from vectorstore.bm25_store import BM25Store
    from vectorstore.faiss_store import FAISSStore
    
    faiss_store = FAISSStore()
    faiss_store.initialize()
    
    bm25_store = BM25Store()
    bm25_store.initialize()

    res = await orchestrator.process(
        messages,
        HybridRetriever(faiss_store, bm25_store),
        CrossEncoderReranker(),
        catalog
    )
    print("FINAL RESPONSE:", json.dumps(res, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
