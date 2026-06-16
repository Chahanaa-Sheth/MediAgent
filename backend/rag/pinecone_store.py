from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

# EMBEDDING MODEL
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# PINECONE
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pc.Index(
    os.getenv("PINECONE_INDEX")
)

# STORE CHUNKS
def store_chunks(chunks):

    vectors = []

    for i, chunk in enumerate(chunks):

        embedding = model.encode(chunk).tolist()

        vectors.append(
            (
                str(i),
                embedding,
                {
                    "text": chunk
                }
            )
        )

    index.upsert(vectors)

# SEARCH
def search_chunks(query):

    query_embedding = model.encode(query).tolist()

    results = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True
    )

    matches = results["matches"]

    texts = []

    for match in matches:

        texts.append(
            match["metadata"]["text"]
        )

    return "\n".join(texts)