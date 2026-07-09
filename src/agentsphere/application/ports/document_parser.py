from typing import Protocol


class DocumentParserProtocol(Protocol):
    async def parse(self, filename: str, content_bytes: bytes, mime_type: str | None = None) -> str:
        """Parses text content from raw bytes depending on document extension format."""
        ...

    async def fetch_url(self, url: str) -> str:
        """Asynchronously fetches page body content from web URL targets and strips HTML layout structures."""
        ...
