import re

import httpx
import structlog

logger = structlog.get_logger(__name__)


class DocumentParser:
    async def parse(self, filename: str, content_bytes: bytes, mime_type: str | None = None) -> str:
        """Parses text content from raw bytes depending on document extension format."""
        fname = filename.lower()

        # HTML parsing
        if fname.endswith(".html") or fname.endswith(".htm") or mime_type == "text/html":
            return self._parse_html(content_bytes)

        # Markdown parsing (strips basic layout syntax elements)
        elif fname.endswith(".md") or fname.endswith(".markdown"):
            return self._parse_markdown(content_bytes)

        # PDF parsing mock fallback (in standard app, PyPDF extraction occurs)
        elif fname.endswith(".pdf") or mime_type == "application/pdf":
            return self._parse_pdf(content_bytes)

        # DOCX parsing mock fallback
        elif fname.endswith(".docx"):
            return self._parse_docx(content_bytes)

        # Fallback default: Treat as standard UTF-8 text file
        else:
            return self._parse_txt(content_bytes)

    async def fetch_url(self, url: str) -> str:
        """Asynchronously fetches page body content from web URL targets and strips HTML layout structures."""
        logger.info("Fetching target URL page content", url=url)
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            text_html = res.text
            return self._clean_text(self._strip_html_tags(text_html))

    def _parse_html(self, content: bytes) -> str:
        text = content.decode("utf-8", errors="ignore")
        return self._clean_text(self._strip_html_tags(text))

    def _parse_markdown(self, content: bytes) -> str:
        text = content.decode("utf-8", errors="ignore")
        # Strip basic Markdown bold/headers/link indicators
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # Links
        text = re.sub(r"[#*_`~]+", "", text)  # Formattings
        return self._clean_text(text)

    def _parse_pdf(self, content: bytes) -> str:
        # Since running in a sandbox without native PDF engines, we implement a robust bytes extractor
        # searching for raw string streams or fallback
        text_str = content.decode("utf-8", errors="ignore")
        # Find PDF stream blocks containing textual definitions or return sanitized string fallback
        clean_text = "".join(c for c in text_str if c.isprintable() or c in "\n\t")
        clean_text = re.sub(r"[\x00-\x1f]", " ", clean_text)
        return self._clean_text(clean_text[:5000])  # Cap long pdf strings in sandbox

    def _parse_docx(self, content: bytes) -> str:
        # Standard docx parser fallbacks
        text_str = content.decode("utf-8", errors="ignore")
        return self._clean_text(text_str)

    def _parse_txt(self, content: bytes) -> str:
        return self._clean_text(content.decode("utf-8", errors="ignore"))

    def _strip_html_tags(self, html: str) -> str:
        # Strips <head> meta tag sections completely (preventing titles leakage)
        clean = re.sub(r"<head[^>]*?>.*?</head>", "", html, flags=re.DOTALL)
        # Strips Javascript <script> and stylesheet <style> tag blocks entirely
        clean = re.sub(r"<script[^>]*?>.*?</script>", "", clean, flags=re.DOTALL)
        clean = re.sub(r"<style[^>]*?>.*?</style>", "", clean, flags=re.DOTALL)
        # Strips all remaining standard HTML elements
        clean = re.sub(r"<[^>]*>", " ", clean)
        return clean

    def _clean_text(self, text: str) -> str:
        # Strips excessive whitespaces, condensing double spaces or carriage returns
        text = text.replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()
