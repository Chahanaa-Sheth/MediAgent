from rag.rag_system import search_knowledge

query = "Why does period pain happen?"

results = search_knowledge(query)

for result in results:
    print(result.page_content)