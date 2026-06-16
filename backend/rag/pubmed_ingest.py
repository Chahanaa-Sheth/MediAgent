from pymed import PubMed

from vectorstore.chroma_store import (
    collection,
    embedding_model
)

pubmed = PubMed(
    tool="MediAgent",
    email="shethchahanaa@gmail.com"
)

def ingest_pubmed(query):

    articles = pubmed.query(
        query,
        max_results=5
    )

    for index, article in enumerate(articles):

        title = article.title

        abstract = article.abstract

        if not abstract:
            continue

        document = f"""
        TITLE:
        {title}

        ABSTRACT:
        {abstract}
        """

        embedding = embedding_model.encode(
            document
        ).tolist()

        collection.add(
            documents=[document],
            embeddings=[embedding],
            ids=[f"{query}_{index}"]
        )

        print(f"Added: {title}")