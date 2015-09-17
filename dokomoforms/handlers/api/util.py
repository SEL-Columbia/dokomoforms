"""Utility functions for API handlers."""
import re
from unicodedata import normalize


def filename_safe(filename: str) -> str:
    """Make a string safe to use as a file name.

    Based on Django's slugify function, this converts spaces to hyphens,
    removes characters that aren't alphanumerics, underscores, or hyphens,
    and strips leading and trailing whitespace.
    """
    filename = normalize('NFKC', filename)
    filename = re.sub('[^\w\s-]', '', filename, flags=re.U).strip()
    return re.sub('[-\s]+', '-', filename, flags=re.U)
