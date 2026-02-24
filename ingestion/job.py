import os
import sys
from extractors import extract_csv_data, extract_pdf_text, extract_ppt_text
from indexers import ingest_to_neo4j, ingest_to_chroma

# Define paths relative to the container's working directory
DATA_DIR = os.getenv("DATA_DIR", "./data")
CSV_PATH = os.path.join(DATA_DIR, "tax_data.csv")
PDF_PATHS = [os.path.join(DATA_DIR, "i1040gi.pdf"), os.path.join(DATA_DIR, "usc26@118-78.pdf")]
PPT_PATH = os.path.join(DATA_DIR, "MIC_3e_Ch11.pptx")

# INGEST_MODE: 'all' (default), 'chroma' (vector only), 'neo4j' (graph only)
INGEST_MODE = os.getenv("INGEST_MODE", "all").lower()

def run_ingestion():
    print(f"Starting ingestion pipeline (mode: {INGEST_MODE})...")

    # 1. Process Structured Data (CSV -> Neo4j)
    if INGEST_MODE in ("all", "neo4j"):
        if os.path.exists(CSV_PATH):
            print(f"Extracting structured data from {CSV_PATH}...")
            csv_records = extract_csv_data(CSV_PATH)
            print(f"Extracted {len(csv_records)} records. Ingesting to Neo4j...")
            ingest_to_neo4j(csv_records)
        else:
            print(f"Warning: CSV file not found at {CSV_PATH}", file=sys.stderr)
    else:
        print("Skipping Neo4j ingestion (mode: chroma-only)")

    # 2. Process Unstructured Data (PDFs & PPT -> ChromaDB)
    if INGEST_MODE in ("all", "chroma"):
        unstructured_chunks = []
        
        for pdf_path in PDF_PATHS:
            if os.path.exists(pdf_path):
                print(f"Extracting text from {pdf_path}...")
                unstructured_chunks.extend(extract_pdf_text(pdf_path))
            else:
                print(f"Warning: PDF file not found at {pdf_path}", file=sys.stderr)

        if os.path.exists(PPT_PATH):
            print(f"Extracting text from {PPT_PATH}...")
            unstructured_chunks.extend(extract_ppt_text(PPT_PATH))
        else:
            print(f"Warning: PPT file not found at {PPT_PATH}", file=sys.stderr)

        if unstructured_chunks:
            print(f"Extracted {len(unstructured_chunks)} total text chunks. Ingesting to ChromaDB...")
            ingest_to_chroma(unstructured_chunks)
        else:
            print("No unstructured chunks extracted.")
    else:
        print("Skipping ChromaDB ingestion (mode: neo4j-only)")

    print("Ingestion pipeline complete.")

if __name__ == "__main__":
    run_ingestion()