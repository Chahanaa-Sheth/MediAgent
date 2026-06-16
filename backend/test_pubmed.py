from tools.pubmed_tool import search_pubmed

results = search_pubmed("migraine causes")

for paper in results:
    print(paper)
    print("\n")