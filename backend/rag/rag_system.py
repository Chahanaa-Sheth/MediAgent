from rag.pinecone_store import (
    store_chunks,
    search_chunks
)

def search_knowledge(query):

    results = search_chunks(query)

    return results