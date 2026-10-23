
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
    """Split text into word-based chunks with overlapping words."""

    # Normalize whitespace before splitting.
    text = " ".join(text.split())
    words = text.split()

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and less than chunk_size")

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        # Join the words in the current chunk.
        chunk_text = " ".join(words[start:end])
        chunks.append(chunk_text)

        if end == len(words):
            break

        # Move forward while keeping the requested overlap.
        start = end - overlap

    return chunks


def process_documents():
    """Load Markdown documents, create chunks, and preserve metadata."""

    documents = sorted(DATA_FOLDER.glob("*.md"))

    if not documents:
        print(f"No Markdown documents found in: {DATA_FOLDER}")
        return

    records = []

    for file_path in documents:
        text = load_markdown(file_path)

        if not text.strip():
            print(f"Skipping empty document: {file_path.name}")
            continue

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

    # Create the output directory if it doesn't exist.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save one JSON record per line.
    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("Ingestion completed successfully!")
    print(f"Documents found: {len(documents)}")
    print(f"Chunks created: {len(records)}")
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_documents()
