from rag.rag_system import search_knowledge
from tools.pubmed_tool import search_pubmed

def research_agent(query):

    # LOCAL + PINECONE RAG
    rag_context = search_knowledge(query)

    # PUBMED PAPERS
    papers = search_pubmed(query)

    pubmed_context = "\n\n".join(papers[:3])

    return f"""
RESEARCH FINDINGS

━━━━━━━━━━━━━━━━━━━

LOCAL MEDICAL KNOWLEDGE:
{rag_context}

━━━━━━━━━━━━━━━━━━━

PUBMED RESEARCH PAPERS:
{pubmed_context}
"""