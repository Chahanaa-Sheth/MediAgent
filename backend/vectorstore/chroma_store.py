import chromadb

from sentence_transformers import SentenceTransformer

# EMBEDDING MODEL
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# CHROMA CLIENT
client = chromadb.Client()

# COLLECTION
collection = client.get_or_create_collection(
    name="medical_knowledge"
)

def add_documents():

    docs = [

        "Migraine causes severe headaches, nausea, and sensitivity to light.",

        "Fever may occur due to viral or bacterial infections.",

        "Chest pain may indicate cardiac issues and requires medical evaluation.",

        "Stomach pain can be caused by gastritis or food poisoning.",

        "Shortness of breath may indicate respiratory problems."

    ]

    for index, doc in enumerate(docs):

        embedding = embedding_model.encode(doc).tolist()

        collection.add(
            documents=[doc],
            embeddings=[embedding],
            ids=[str(index)]
        )

def search_documents(query):

    query_embedding = embedding_model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documents = results["documents"][0]

    return "\n\n".join(documents)