from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

    # Better chunking
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

    chunks = splitter.split_text(full_text)

    # Store in Chroma
    for index, chunk in enumerate(chunks):

        embedding = embedding_model.encode(
            chunk
        ).tolist()

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"pdf_chunk_{index}"],
            metadatas=[{
                "source": file_path,
                "type": "pdf",
                "chunk_number": index
            }]
        )

    return {
        "message": "PDF ingested successfully",
        "chunks_added": len(chunks)
    }