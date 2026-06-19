from Bio import Entrez

# REQUIRED EMAIL
Entrez.email = "shethchahanaa@gmail.com"


def search_pubmed(query):

    # SEARCH PUBMED
    search_handle = Entrez.esearch(
        db="pubmed",
        term=f"({query}) AND english[Language]",
        retmax=3
    )

    search_results = Entrez.read(search_handle)

    ids = search_results["IdList"]

    papers = []

    # FETCH PAPER DETAILS
    fetch_handle = Entrez.efetch(
    db="pubmed",
    id=",".join(ids),
    rettype="abstract",
    retmode="text"
)

    paper_data = fetch_handle.read()

    return [paper_data]