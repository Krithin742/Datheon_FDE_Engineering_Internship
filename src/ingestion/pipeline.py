
import csv
import json
from pathlib import Path

from pypdf import PdfReader


# Find the main project folder.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Folder containing our sample documents.
DATA_FOLDER = PROJECT_ROOT / "data" / "sample_docs"

# File where the processed chunks will be saved.
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed_chunks.jsonl"

SUPPORTED_EXTENSIONS = {".md", ".csv", ".pdf"}


def load_markdown(file_path):
    """Read a Markdown document."""
    return file_path.read_text(encoding="utf-8")


def load_pdf(file_path):
    """Extract text from a text-based PDF."""
    reader = PdfReader(str(file_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages.append(f"Page {page_number}: {page_text.strip()}")

    return "\n\n".join(pages)


def split_into_chunks(text, chunk_size=45, overlap=8):
    """Split text into word-based chunks with overlap."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))

        if end == len(words):
            break

        # Move forward while keeping the requested overlap.
        start = end - overlap

    return chunks


def process_documents():
    """Ingest supported documents into JSONL records."""
    if not DATA_FOLDER.exists():
        print(f"Document folder not found: {DATA_FOLDER}")
        return

    documents = sorted(
        path for path in DATA_FOLDER.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    records = []

    for file_path in documents:
        file_type = file_path.suffix.lower()

        try:
            if file_type == ".csv":
                with file_path.open(
                    "r", encoding="utf-8-sig", newline=""
                ) as file:
                    reader = csv.DictReader(file)

                    for row_number, row in enumerate(reader, start=1):
                        department = (row.get("department") or "Unknown").strip()
                        text = " | ".join(
                            f"{key}: {value}"
                            for key, value in row.items()
                            if key and value is not None
                        ).strip()

                        if not text:
                            continue

                        records.append({
                            "chunk_id": f"{file_path.stem}_{row_number - 1}",
                            "text": text,
                            "metadata": {
                                "department": department,
                                "access_tier": "internal",
                                "source": file_path.name,
                                "file_type": file_type,
                                "chunk_index": row_number - 1
                            }
                        })

                print(
                    f"Processed {file_path.name}: "
                    f"{sum(r['metadata']['source'] == file_path.name for r in records)} records"
                )
                continue

            if file_type == ".md":
                text = load_markdown(file_path)
            else:
                text = load_pdf(file_path)

            if not text.strip():
                print(f"Skipping empty document: {file_path.name}")
                continue

            chunks = split_into_chunks(text)

            for index, chunk in enumerate(chunks):
                records.append({
                    "chunk_id": f"{file_path.stem}_{index}",
                    "text": chunk,
                    "metadata": {
                        "department": "IT",
                        "access_tier": "internal",
                        "source": file_path.name,
                        "file_type": file_type,
                        "chunk_index": index
                    }
                })

            print(f"Processed {file_path.name}: {len(chunks)} chunks")

        except Exception as error:
            print(f"Error processing {file_path.name}: {error}")

    # Create the output directory if it doesn't exist.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save one JSON record per line.
    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("\nIngestion completed!")
    print(f"Documents discovered: {len(documents)}")
    print(f"Total chunks/records created: {len(records)}")
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_documents()
