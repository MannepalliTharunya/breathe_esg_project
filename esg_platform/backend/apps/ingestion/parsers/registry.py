"""Parser registry — maps source_type string to parser class."""
from .sap_parser import SAPParser
from .utility_parser import UtilityParser
from .travel_parser import TravelParser

PARSER_REGISTRY = {
    "sap": SAPParser,
    "utility": UtilityParser,
    "travel": TravelParser,
}


def get_parser(source_type: str, file_obj):
    cls = PARSER_REGISTRY.get(source_type)
    if not cls:
        raise ValueError(f"No parser registered for source type: {source_type!r}")
    return cls(file_obj)
