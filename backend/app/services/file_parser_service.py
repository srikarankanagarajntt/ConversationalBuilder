"""File parser service — extracts raw text from PDF, DOCX, and PPTX files."""
from __future__ import annotations

import io

from app.core.exceptions import UnsupportedFileTypeError


class FileParserService:
    async def extract_text(self, raw_bytes: bytes, content_type: str) -> str:
        """
        Dispatch to the appropriate parser based on MIME type.
        Returns the full extracted plain text.
        """
        if "pdf" in content_type:
            return self._parse_pdf(raw_bytes)
        elif "wordprocessingml" in content_type or "msword" in content_type:
            return self._parse_docx(raw_bytes)
        elif "presentationml" in content_type:
            return self._parse_pptx(raw_bytes)
        else:
            raise UnsupportedFileTypeError(content_type)

    def _parse_pdf(self, data: bytes) -> str:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    def _parse_docx(self, data: bytes) -> str:
        from docx import Document

        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def _parse_pptx(self, data: bytes) -> str:
        from pptx import Presentation

        prs = Presentation(io.BytesIO(data))
        texts = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    texts.append(shape.text)
        return "\n".join(texts)
