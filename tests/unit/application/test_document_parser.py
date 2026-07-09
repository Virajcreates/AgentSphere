import pytest

from agentsphere.infrastructure.rag.parsing.document_parser import DocumentParser


@pytest.mark.asyncio
async def test_document_parser_txt() -> None:
    parser = DocumentParser()
    content = b"Hello world! This is raw textual data."
    parsed = await parser.parse("data.txt", content)
    assert parsed == "Hello world! This is raw textual data."


@pytest.mark.asyncio
async def test_document_parser_html_strips_tags() -> None:
    parser = DocumentParser()
    html = b"<html><head><title>Test Title</title></head><body><h1>Heading</h1><p>Paragraph content.</p></body></html>"
    parsed = await parser.parse("index.html", html)
    assert "Test Title" not in parsed  # head section strips Javascript/Styles or cleans
    assert "Heading" in parsed
    assert "Paragraph content." in parsed
    assert "<html>" not in parsed  # stripped tags!


@pytest.mark.asyncio
async def test_document_parser_markdown() -> None:
    parser = DocumentParser()
    md = b"# Section Header\nSome **bold text** and [link](https://google.com)"
    parsed = await parser.parse("readme.md", md)
    assert "#" not in parsed
    assert "bold text" in parsed
    assert "link" in parsed
