"""
Base parser — handles both CSV and Excel (.xlsx/.xls) files.
All source-specific parsers inherit from this.

File type is detected from the filename extension, not MIME type,
because browsers send inconsistent MIME types for Excel files.
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
    Reusable file parser base.
    Supports CSV (any delimiter) and Excel (.xlsx / .xls).
    Subclasses define COLUMN_MAP to translate source column names
    to internal canonical names.
    """
    COLUMN_MAP: dict[str, str] = {}
    REQUIRED_FIELDS: list[str] = []
    SOURCE_TYPE: str = ""

    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.errors: list[str] = []

    # ── File type detection ───────────────────────────────────────────────────

    def _is_excel(self) -> bool:
        name = getattr(self.file_obj, "name", "") or ""
        return name.lower().endswith((".xlsx", ".xls"))

    # ── Encoding helpers ──────────────────────────────────────────────────────

    def detect_encoding(self, raw_bytes: bytes) -> str:
        result = chardet.detect(raw_bytes[:50_000])
        return result.get("encoding") or "utf-8"

    # ── Excel reader ──────────────────────────────────────────────────────────

    def _read_excel_rows(self) -> list[dict]:
        """Read an Excel file and return list of row dicts (same shape as csv.DictReader)."""
        try:
            import openpyxl
        except ImportError:
            raise ParseError("openpyxl is required to read Excel files. Install it with: pip install openpyxl")

        raw = self.file_obj.read()
        try:
            wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
        except Exception as e:
            raise ParseError(f"Cannot open Excel file: {e}. Make sure it is a valid .xlsx file.")

        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()

        if not rows:
            raise ParseError("Excel file is empty.")

        # First row = headers
        headers = [str(h).strip() if h is not None else "" for h in rows[0]]
        if not any(headers):
            raise ParseError("Excel file has no headers in the first row.")

        result = []
        for row_values in rows[1:]:
            # Skip completely empty rows
            if all(v is None or str(v).strip() == "" for v in row_values):
                continue
            row_dict = {}
            for i, h in enumerate(headers):
                val = row_values[i] if i < len(row_values) else None
                row_dict[h] = str(val).strip() if val is not None else ""
            result.append(row_dict)

        return result, headers

    # ── CSV reader ────────────────────────────────────────────────────────────

    def _read_csv_content(self) -> str:
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

    # ── Column mapping ────────────────────────────────────────────────────────

    def normalize_header(self, header: str) -> str:
        """
        Lowercase, strip, replace spaces/hyphens/dots with underscores.
        Also strips parenthetical suffixes like '(Menge)' or '(ME)'.
        e.g. 'Quantity (Menge)' → 'quantity'
             'Unit (ME)'        → 'unit'
             'Posting Date (Buchungsdatum)' → 'posting_date'
        """
        import re
        # Remove anything in parentheses and trim
        cleaned = re.sub(r'\s*\(.*?\)\s*', '', header).strip()
        return cleaned.lower().replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")

    def map_columns(self, raw_headers: list[str]) -> dict[str, str]:
        """Returns mapping: raw_header → internal_name for matched columns."""
        mapping = {}
        for h in raw_headers:
            normalized = self.normalize_header(h)
            if normalized in self.COLUMN_MAP:
                mapping[h] = self.COLUMN_MAP[normalized]
        return mapping

    # ── Main parse entry point ────────────────────────────────────────────────

    def parse(self) -> Iterator[dict]:
        """
        Yields one dict per data row with internal field names.
        Handles both CSV and Excel transparently.
        """
        if self._is_excel():
            yield from self._parse_excel()
        else:
            yield from self._parse_csv()

    def _parse_excel(self) -> Iterator[dict]:
        rows, raw_headers = self._read_excel_rows()

        col_map = self.map_columns(raw_headers)
        missing = [f for f in self.REQUIRED_FIELDS if f not in col_map.values()]
        if missing:
            raise ParseError(
                f"Missing required columns: {missing}. "
                f"Found columns: {raw_headers}. "
                f"Tip: Make sure you selected the correct Data Source type."
            )

        for row_num, row in enumerate(rows, start=2):
            mapped = {"_row_number": row_num, "_raw": dict(row)}
            for raw_col, internal_name in col_map.items():
                mapped[internal_name] = (row.get(raw_col) or "").strip()
            yield mapped

    def _parse_csv(self) -> Iterator[dict]:
        content = self._read_csv_content()
        delimiter = self.sniff_delimiter(content)

        try:
            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        except Exception as e:
            raise ParseError(f"Cannot read CSV file: {e}")

        if not reader.fieldnames:
            raise ParseError("CSV file appears to be empty or has no headers.")

        col_map = self.map_columns(list(reader.fieldnames))
        missing = [f for f in self.REQUIRED_FIELDS if f not in col_map.values()]
        if missing:
            raise ParseError(
                f"Missing required columns: {missing}. "
                f"Found columns: {list(reader.fieldnames)}. "
                f"Tip: Make sure you selected the correct Data Source type."
            )

        for row_num, row in enumerate(reader, start=2):
            mapped = {"_row_number": row_num, "_raw": dict(row)}
            for raw_col, internal_name in col_map.items():
                mapped[internal_name] = (row.get(raw_col) or "").strip()
            yield mapped

    @abstractmethod
    def validate_row(self, row: dict) -> list[str]:
        """Return list of validation error strings for a single row."""
        ...
