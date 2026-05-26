"""
Base CSV parser. All source-specific parsers inherit from this.
Handles encoding detection, delimiter sniffing, and column mapping.
"""
import io
import csv
import logging
import chardet
from abc import ABC, abstractmethod
from typing import Iterator

logger = logging.getLogger(__name__)


class ParseError(Exception):
    pass


class BaseCSVParser(ABC):
    """
    Reusable CSV parser base.
    Subclasses define COLUMN_MAP to translate source column names
    to internal canonical names.
    """
    # Map: source column name (lowercase, stripped) → internal field name
    COLUMN_MAP: dict[str, str] = {}
    REQUIRED_FIELDS: list[str] = []
    SOURCE_TYPE: str = ""

    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.errors: list[str] = []

    def detect_encoding(self, raw_bytes: bytes) -> str:
        result = chardet.detect(raw_bytes[:50_000])
        return result.get("encoding") or "utf-8"

    def read_file(self) -> str:
        raw = self.file_obj.read()
        encoding = self.detect_encoding(raw)
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            return raw.decode("utf-8", errors="replace")

    def sniff_delimiter(self, sample: str) -> str:
        try:
            dialect = csv.Sniffer().sniff(sample[:4096], delimiters=",;\t|")
            return dialect.delimiter
        except csv.Error:
            return ","

    def normalize_header(self, header: str) -> str:
        """Lowercase, strip whitespace, replace spaces/hyphens with underscores."""
        return header.strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_")

    def map_columns(self, raw_headers: list[str]) -> dict[str, str]:
        """Returns mapping: raw_header → internal_name for matched columns."""
        mapping = {}
        for h in raw_headers:
            normalized = self.normalize_header(h)
            if normalized in self.COLUMN_MAP:
                mapping[h] = self.COLUMN_MAP[normalized]
        return mapping

    def parse(self) -> Iterator[dict]:
        """
        Yields one dict per row with internal field names.
        Rows that cannot be mapped are yielded with _parse_error key.
        """
        content = self.read_file()
        delimiter = self.sniff_delimiter(content)
        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

        if not reader.fieldnames:
            raise ParseError("File appears to be empty or has no headers.")

        col_map = self.map_columns(list(reader.fieldnames))
        missing = [f for f in self.REQUIRED_FIELDS if f not in col_map.values()]
        if missing:
            raise ParseError(f"Missing required columns: {missing}. Found: {list(reader.fieldnames)}")

        for row_num, row in enumerate(reader, start=2):
            mapped = {"_row_number": row_num, "_raw": dict(row)}
            for raw_col, internal_name in col_map.items():
                mapped[internal_name] = (row.get(raw_col) or "").strip()
            yield mapped

    @abstractmethod
    def validate_row(self, row: dict) -> list[str]:
        """Return list of validation error strings for a single row."""
        ...
