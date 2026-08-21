import pytest
from app.rag.chunking import chunk_text
from app.rag.retrieval import build_rag_context, RetrievedChunk


def test_chunk_small_text():
    chunks = chunk_text("Hello world", chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0] == "Hello world"


def test_chunk_large_text():
    text = " ".join(["word"] * 500)
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1


def test_chunk_empty_text():
    chunks = chunk_text("", chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 0


def test_chunk_whitespace_only():
    chunks = chunk_text("   ", chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 0


def test_build_context_no_chunks():
    context = build_rag_context([])
    assert "No relevant company knowledge" in context


def test_build_context_with_chunks():
    chunks = [
        RetrievedChunk(
            content="Refund policy states 30 days.",
            document_name="policy.md",
            similarity_score=0.95,
        ),
        RetrievedChunk(
            content="Gold members get 45 days.",
            document_name="tiers.md",
            similarity_score=0.80,
        ),
    ]
    context = build_rag_context(chunks)
    assert "policy.md" in context
    assert "tiers.md" in context
    assert "0.95" in context
    assert "0.80" in context
    assert "Refund policy" in context
