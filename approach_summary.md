# SHL Assessment Recommender: Approach Summary

## 1. Design Choices
Our core philosophy was to build a system that is robust, stateless, and efficient. We opted for a **Stateless API** combined with a determinisic **Agent Orchestrator**. Rather than relying entirely on the LLM to govern conversation flow (which is slow and prone to hallucination), we implemented a state machine that handles input routing:
*   **Intent Detection & Guardrails**: We used deterministic pattern matching to instantly identify prompt injections, off-topic requests, and gibberish, blocking them before they incur LLM latency.
*   **Fallback Mechanisms**: If the LLM goes offline or fails to generate a response, the orchestrator defaults to a catalog-grounded fallback, ensuring the user always receives a response based on the top retrieved assessments.

## 2. Retrieval Setup
To guarantee that the recommender accurately matches specific SHL tests (like the OPQ32r) to general job requirements, we implemented a sophisticated **Hybrid Search Architecture**:
*   **Semantic Search**: A FAISS Index (IndexFlatIP) embedded with `BAAI/bge-small-en-v1.5` processes broad contextual queries like "I need a test for a senior software engineer."
*   **Keyword Search**: A BM25 index handles exact keyword and acronym matches, ensuring tests with specific names aren't lost in dense vector space.
*   **Reciprocal Rank Fusion (RRF)**: We combined the scores from FAISS and BM25 to balance contextual meaning with exact terminology.
*   **Cross-Encoder Reranking**: The top results from the RRF step are fed into `cross-encoder/ms-marco-MiniLM-L-6-v2`, which highly accurately reranks the results against the original user query to maximize relevance.

## 3. Prompt Design
We engineered our prompts to tightly constrain the LLM, ensuring predictable output formatting and behavior:
*   **Structured Outputs**: The LLM is forced to output a strict JSON array, separating the conversational `reply` from the structured `recommendations` payload.
*   **Clarification Gating**: We designed the system prompt to explicitly refuse providing recommendations until exactly five key hiring criteria are explicitly gathered from the user.
*   **Zero-Hallucination Guidelines**: The LLM is instructed strictly to rely *only* on the provided `catalog_context`.

## 4. Evaluation Method
We established an automated testing pipeline using `pytest` to simulate a variety of complex user interactions. We utilized **12 advanced conversational traces** that tested:
*   **Recall & Precision**: Does the system recommend the expected assessments for complex queries (e.g., matching a Rust developer role with the correct technical tests)?
*   **Refusal & Guardrails**: Does the system successfully block legal compliance questions, competitor references, and gibberish?
*   **Refinement**: Can the system adapt when a user alters their requirements mid-conversation?

## 5. What Did Not Work
*   **Pure LLM Clarification Gating**: Initially, we relied entirely on the LLM to decide when to ask clarification questions and when to recommend. However, the LLM often became "impatient" with gibberish or non-compliant users and hallucinated recommendations early. We solved this by enforcing a hard 8-turn limit and explicit gibberish guardrails.
*   **Pure Semantic Search**: Using dense vectors alone struggled with short acronyms and highly specific technical skills (e.g., "SQL" or "OPQ"). This failure directly led to our adoption of the BM25 keyword index and RRF.
*   **LLM Link Formatting**: Asking the LLM to format assessment URLs into Markdown links inside the conversational text frequently resulted in broken links. We resolved this by extracting URLs into a separate, structured `recommendations` array for the frontend to render safely.

## 6. How We Measured Improvement
Improvement was continuously tracked across three main axes:
1.  **Test Pass Rate**: The primary metric was the success rate of our 12 evaluation traces. Hardcoding turn limits and adding the BM25 index measurably improved our trace pass rate from ~60% to 100%.
2.  **Completeness Score**: We tracked the agent's ability to extract the 5 required criteria across multi-turn conversations, ensuring that the final recommendation recall improved alongside the completeness score.
3.  **Latency**: By moving guardrails and intent detection out of the LLM and into fast regex/heuristic checks, we reduced the average response latency by nearly a full second.
