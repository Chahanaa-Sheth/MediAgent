from Bio import Entrez

# REQUIRED EMAIL
Entrez.email = "shethchahanaa@gmail.com"


def search_pubmed(query):

    # SEARCH PUBMED
    search_handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=3
    )

    search_results = Entrez.read(search_handle)

    ids = search_results["IdList"]

    papers = []

    # FETCH PAPER DETAILS
    for paper_id in ids:

        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=paper_id,
            rettype="abstract",
            retmode="text"
        )

        paper_data = fetch_handle.read()

        papers.append(paper_data)

    return papers