from typing import Dict, List, Any
import asyncio
from vectorstore.chroma_store import search_documents
from rag.rag_system import search_knowledge
from tools.pubmed_tool import search_pubmed
from utils.exceptions import Logger, RAGError


class RAGService:
    """Service for RAG operations"""

    def __init__(self):
        self.logger = Logger("RAGService")

    async def search_all_sources(self, query: str) -> Dict[str, Any]:
        """Search across all knowledge sources"""
        try:
            results = {
                "local_documents": await self._search_local(query),
                "pubmed_papers": await self._search_pubmed(query),
                "pinecone_results": await self._search_pinecone(query)
            }
            self.logger.info("RAG search completed", query_length=len(query))
            return results
        except Exception as e:
            self.logger.error("RAG search failed", error=str(e))
            raise RAGError(f"RAG search failed: {str(e)}")

    async def _search_local(self, query: str) -> List[Dict[str, Any]]:
        """Search local Chroma vector database"""
        try:
            results = await asyncio.to_thread(search_documents, query)
            return [results] if results else []
        except Exception as e:
            self.logger.error("Local search failed", error=str(e))
            return []

    async def _search_pubmed(self, query: str) -> List[Dict[str, Any]]:
        """Search PubMed"""
        try:
            results = await asyncio.to_thread(search_pubmed, query)
            return results if results else []
        except Exception as e:
            self.logger.error("PubMed search failed", error=str(e))
            return []

    async def _search_pinecone(self, query: str) -> List[Dict[str, Any]]:
        """Search Pinecone vector database"""
        try:
            results = await asyncio.to_thread(search_knowledge, query)
            return [results] if results else []
        except Exception as e:
            self.logger.error("Pinecone search failed", error=str(e))
            return []

    async def ingest_pdf(self, pdf_text: str, filename: str) -> Dict[str, Any]:
        """Ingest PDF text into Chroma"""
        try:
            result = await asyncio.to_thread(self._ingest_pdf_sync, pdf_text, filename)
            self.logger.info("PDF ingested", filename=filename, chunks=result.get("chunks_added", 0))
            return result
        except Exception as e:
            self.logger.error("PDF ingestion failed", error=str(e), filename=filename)
            raise RAGError(f"PDF ingestion failed: {str(e)}")

    def _ingest_pdf_sync(self, pdf_text: str, filename: str) -> Dict[str, Any]:
        """Synchronous PDF ingestion (run in thread)"""
        from vectorstore.chroma_store import collection, embedding_model

        # Chunking
        chunks = []
        chunk_size = 500

        for i in range(0, len(pdf_text), chunk_size):
            chunk = pdf_text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)

        # Store in Chroma
        for index, chunk in enumerate(chunks):
            embedding = embedding_model.encode(chunk).tolist()

            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"pdf_{filename}_{index}"]
            )

        return {
            "message": "PDF ingested successfully",
            "chunks_added": len(chunks),
            "filename": filename
        }

    async def get_best_sources(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the best sources across all knowledge bases"""
        all_results = await self.search_all_sources(query)

        # Combine and rank results
        combined = []
        for source_type, results in all_results.items():
            for result in results:
                if isinstance(result, dict):
                    combined.append({
                        **result,
                        "source": source_type
                    })
                else:
                    combined.append({
                        "content": str(result),
                        "source": source_type
                    })

        # Sort by relevance (assuming each result has a score)
        combined.sort(key=lambda x: x.get("score", 0), reverse=True)

        return combined[:limit]
