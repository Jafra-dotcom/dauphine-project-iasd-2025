"""Main module for the TelecomPlus multi-agent support system."""


from tools.pdf_retriever import PDFRetriever

if __name__ == "__main__":
    retriever = PDFRetriever()
    results = retriever.search("Quels modes de paiement acceptez-vous ?")

    for r in results:
        print(r.page_content[:300])
        print("-" * 50)

