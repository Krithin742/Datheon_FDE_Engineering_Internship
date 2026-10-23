
import json
import unittest
from pathlib import Path

from src.ingestion.pipeline import split_into_chunks, process_documents, OUTPUT_FILE


class TestIngestionPipeline(unittest.TestCase):

    def test_chunks_are_created(self):
        text = "one two three four five six"
        chunks = split_into_chunks(text, chunk_size=4, overlap=1)

        self.assertEqual(len(chunks), 2)

    def test_chunks_overlap(self):
        text = "one two three four five six"
        chunks = split_into_chunks(text, chunk_size=4, overlap=1)

        self.assertEqual(chunks[0].split()[-1], chunks[1].split()[0])

    def test_whitespace_is_normalized(self):
        text = "hello   world\nagain"
        chunks = split_into_chunks(text, chunk_size=10, overlap=0)

        self.assertEqual(chunks[0], "hello world again")

    def test_invalid_chunk_size(self):
        with self.assertRaises(ValueError):
            split_into_chunks("hello world", chunk_size=0, overlap=0)

    def test_invalid_overlap(self):
        with self.assertRaises(ValueError):
            split_into_chunks("hello world", chunk_size=4, overlap=4)


if __name__ == "__main__":
    unittest.main()
