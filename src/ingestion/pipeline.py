
import json
from pathlib import Path


# Find the main project folder.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Folder containing our sample documents.
DATA_FOLDER = PROJECT_ROOT / "data" / "sample_docs"

# File where the processed chunks will be saved.
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed_chunks.jsonl"


def load_markdown(file_path):
    """Read a Markdown document and return its text."""
    return file_path.read_text(encoding="utf-8")


def split_into_chunks(text, chunk_size=45, overlap=8):
    """Split text into word-based chunks with a small overlap."""

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append(chunk_text)

        if end == len(words):
            break

        start = end - overlap

    return chunks


def process_documents():
    """Load documents, create chunks, and preserve metadata."""

    documents = list(DATA_FOLDER.glob("*.md"))

    if not documents:
        print("No Markdown documents found.")
        return

    records = []

    for file_path in documents:
        text = load_markdown(file_path)
        chunks = split_into_chunks(text)

        for index, chunk in enumerate(chunks):
            record = {
                "chunk_id": f"{file_path.stem}_{index}",
                "text": chunk,
                "metadata": {
                    "department": "IT",
                    "access_tier": "internal",
                    "source": file_path.name,
                    "chunk_index": index
                }
            }

            records.append(record)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("Ingestion completed successfully!")
    print(f"Documents processed: {len(documents)}")
    print(f"Chunks created: {len(records)}")
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_documents()
