from pypdf import PdfReader

from vectorstore.chroma_store import (
    collection,
    embedding_model
)

def ingest_pdf(file_path):

    reader = PdfReader(file_path)

    full_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            full_text += text + "\n"

    # CHUNKING
    chunks = []

    chunk_size = 500

    for i in range(0, len(full_text), chunk_size):

        chunk = full_text[i:i + chunk_size]

        chunks.append(chunk)

    # STORE IN CHROMA
    for index, chunk in enumerate(chunks):

        embedding = embedding_model.encode(
            chunk
        ).tolist()

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"pdf_chunk_{index}"]
        )

    return {
        "message": "PDF ingested successfully",
        "chunks_added": len(chunks)
    }