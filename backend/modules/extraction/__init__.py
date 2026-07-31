"""Input Layer dispatcher: routes a file/URL/raw text to the right extractor."""
from .docx_extractor import extract_docx_text
from .pdf_extractor import extract_pdf_text
from .pptx_extractor import extract_pptx_text
from .txt_extractor import extract_txt_text
from .url_extractor import UnsafeURLError, extract_url_text

_EXTRACTORS_BY_EXTENSION = {
    "pdf": extract_pdf_text,
    "docx": extract_docx_text,
    "pptx": extract_pptx_text,
    "txt": extract_txt_text,
}

SUPPORTED_EXTENSIONS = tuple(_EXTRACTORS_BY_EXTENSION.keys())


class UnsupportedFileTypeError(ValueError):
    pass


def extract_from_file(filename: str, file_bytes: bytes) -> str:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    extractor = _EXTRACTORS_BY_EXTENSION.get(extension)
    if extractor is None:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '.{extension}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    return extractor(file_bytes)


def extract_from_url(url: str) -> str:
    return extract_url_text(url)


def extract_from_raw_text(text: str) -> str:
    return text


__all__ = [
    "extract_from_file",
    "extract_from_url",
    "extract_from_raw_text",
    "UnsupportedFileTypeError",
    "UnsafeURLError",
    "SUPPORTED_EXTENSIONS",
]
