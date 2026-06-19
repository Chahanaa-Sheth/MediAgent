from typing import Dict, List, Any
import asyncio

from services.query_expansion import expand_medical_query

from vectorstore.chroma_store import (
    search_documents,
    collection,
    embedding_model
)

from rag.rag_system import search_knowledge
from tools.pubmed_tool import search_pubmed

from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.exceptions import Logger, RAGError


class RAGService:
    """Service for RAG operations"""

    def __init__(self):
        self.logger = Logger("RAGService")

    async def search_all_sources(
        self,
        query: str
    ) -> Dict[str, Any]:

        try:

            # ==========================================
            # QUERY EXPANSION
            # ==========================================

            expanded = await expand_medical_query(query)

            retrieval_terms = expanded.get(
                "keywords",
                [query]
            )

            expanded_query = " OR ".join(
                retrieval_terms[:15]
            )

            self.logger.info(
                "Expanded query",
                original=query,
                expanded=expanded_query
            )

            # ==========================================
            # PARALLEL RETRIEVAL
            # ==========================================

            local_task = self._search_local(
                expanded_query
            )

            pubmed_query = " ".join(retrieval_terms[:5])

            pubmed_task = self._search_pubmed(pubmed_query)

            pinecone_task = self._search_pinecone(
                expanded_query
            )

            local_docs, pubmed_docs, pinecone_docs = await asyncio.gather(
                local_task,
                pubmed_task,
                pinecone_task
            )

            print("\n" + "="*80)
            print("LOCAL DOCUMENTS RETRIEVED")
            print("="*80)

            for doc in local_docs:
                print(doc)

            print("="*80 + "\n")

            results = {
                "local_documents": local_docs,
                "pubmed_papers": pubmed_docs,
                "pinecone_results": pinecone_docs,
                "query_expansion": {
                    "primary_symptom": expanded.get(
                        "primary_symptom",
                        query
                    ),
                    "urgency_flag": expanded.get(
                        "urgency_flag",
                        "LOW"
                    ),
                    "retrieval_terms": retrieval_terms
                }
            }

            self.logger.info(
                "RAG search completed",
                query=query,
                expanded_terms=len(retrieval_terms),
                local_results=len(local_docs),
                pubmed_results=len(pubmed_docs),
                pinecone_results=len(pinecone_docs)
            )

            return results

        except Exception as e:

            self.logger.error(
                "RAG search failed",
                error=str(e)
            )

            raise RAGError(
                f"RAG search failed: {str(e)}"
            )

    async def _search_local(
        self,
        query: str
    ) -> List[Dict[str, Any]]:

        try:

            results = await asyncio.to_thread(
                search_documents,
                query,
                5
            )

            if not results:
                return []

            filtered_results = [
                result
                for result in results
                if result.get("score", 0) > 0.35
            ]

            return filtered_results

        except Exception as e:

            self.logger.error(
                "Local search failed",
                error=str(e)
            )

            return []

    async def _search_pubmed(
        self,
        query: str
    ) -> List[Dict[str, Any]]:

        try:

            results = await asyncio.to_thread(
                search_pubmed,
                query
            )

            return results[:3] if results else []

        except Exception as e:

            self.logger.error(
                "PubMed search failed",
                error=str(e)
            )

            return []

    async def _search_pinecone(
        self,
        query: str
    ) -> List[Dict[str, Any]]:

        try:

            results = await asyncio.to_thread(
                search_knowledge,
                query
            )

            return results if results else []

        except Exception as e:

            self.logger.error(
                "Pinecone search failed",
                error=str(e)
            )

            return []

    async def ingest_pdf(
        self,
        pdf_text: str,
        filename: str
    ) -> Dict[str, Any]:

        try:

            result = await asyncio.to_thread(
                self._ingest_pdf_sync,
                pdf_text,
                filename
            )

            self.logger.info(
                "PDF ingested",
                filename=filename,
                chunks=result["chunks_added"]
            )

            return result

        except Exception as e:

            self.logger.error(
                "PDF ingestion failed",
                filename=filename,
                error=str(e)
            )

            raise RAGError(
                f"PDF ingestion failed: {str(e)}"
            )

    def _ingest_pdf_sync(
        self,
        pdf_text: str,
        filename: str
    ) -> Dict[str, Any]:

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " "
            ]
        )

        chunks = splitter.split_text(pdf_text)

        added = 0

        for index, chunk in enumerate(chunks):

            if not chunk.strip():
                continue

            embedding = embedding_model.encode(
                chunk
            ).tolist()

            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"pdf_{filename}_{index}"],
                metadatas=[{
                    "source": filename,
                    "type": "pdf",
                    "chunk_number": index
                }]
            )

            added += 1

        return {
            "message": "PDF ingested successfully",
            "filename": filename,
            "chunks_added": added
        }

    async def get_best_sources(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:

        all_results = await self.search_all_sources(query)

        combined = []

        for source_type, results in all_results.items():

            if not isinstance(results, list):
                continue

            for result in results:

                if isinstance(result, dict):

                    combined.append({
                        **result,
                        "source": source_type
                    })

                else:

                    combined.append({
                        "content": str(result),
                        "source": source_type,
                        "score": 0
                    })

        combined.sort(
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        return combined[:limit]