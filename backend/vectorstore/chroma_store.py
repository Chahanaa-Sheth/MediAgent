import chromadb

from sentence_transformers import SentenceTransformer

# Better embedding model
embedding_model = SentenceTransformer(
    "pritamdeka/S-PubMedBert-MS-MARCO"
)

# CHROMA CLIENT

client = chromadb.PersistentClient(
    path="./chroma_db"
)

# COLLECTION
collection = client.get_or_create_collection(
    name="medical_knowledge"
)

def add_documents():

    if collection.count() > 0:
        return

    docs = [

        {
            "text": "Migraine causes severe headaches, nausea, and sensitivity to light.",
            "source": "seed"
        },

        {
            "text": "Fever may occur due to viral or bacterial infections.",
            "source": "seed"
        },

        {
            "text": "Chest pain may indicate cardiac issues and requires medical evaluation.",
            "source": "seed"
        },

        {
            "text": "Stomach pain can be caused by gastritis or food poisoning.",
            "source": "seed"
        },

        {
            "text": "Shortness of breath may indicate respiratory problems.",
            "source": "seed"
        }

    ]

    for index, doc in enumerate(docs):

        embedding = embedding_model.encode(
            doc["text"],
            normalize_embeddings=True
        ).tolist()

        collection.add(
            ids=[str(index)],
            documents=[doc["text"]],
            embeddings=[embedding],
            metadatas=[{
                "source": doc["source"]
            }]
        )

def search_documents(
    query: str,
    top_k: int = 5
):

    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    output = []

    for doc, distance, metadata in zip(
        documents,
        distances,
        metadatas
    ):

        score = max(0,round(1 - distance, 4))

        output.append({

            "content": doc,

            "score": round(score, 4),

            "source": metadata.get(
                "source",
                "unknown"
            )
        })

    return output