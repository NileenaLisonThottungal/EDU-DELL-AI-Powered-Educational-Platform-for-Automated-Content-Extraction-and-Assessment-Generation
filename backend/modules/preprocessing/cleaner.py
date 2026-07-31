"""Symbol/noise removal and normalization (Section 3.2.2)."""
import re

_BULLET_CHARS = "•●▪◦‣·"
_NOISE_PATTERN = re.compile(
    r"[" + re.escape(_BULLET_CHARS) + r"]|_{2,}|-{3,}|={3,}|\t"
)
_MULTI_SPACE = re.compile(r"[  ]{2,}")
_MULTI_NEWLINE = re.compile(r"\n{3,}")
# Keep numbering/lettered-list markers like "1.", "i)", "ii)" — only strip when
# they're not followed by content (i.e. stray leftover markers).
_STRAY_MARKER = re.compile(r"^\s*(?:\d+\.|[ivxlcdm]+\))\s*$", re.IGNORECASE)


def clean_text(raw_text: str) -> str:
    text = _NOISE_PATTERN.sub(" ", raw_text)
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_NEWLINE.sub("\n\n", text)

    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and not _STRAY_MARKER.match(stripped):
            lines.append(stripped)

    return "\n".join(lines)
