"""The shape of a finished record, and the normalization that gets raw strings there."""
import re

from pydantic import BaseModel, Field, ValidationError


class Book(BaseModel):
    title: str = Field(min_length=1)
    product_url: str = Field(pattern=r"^https://")  # canonical URL = identity
    price_text: str
    price_gbp: float = Field(ge=0)
    availability_text: str
    rating_text: str
    description: str | None = None
    source_page: str = Field(pattern=r"^https://")
    fetched_at: str


def parse_price(price_text: str | None) -> float | None:
    """'£51.77' -> 51.77 ; None if there is no number in the text."""
    m = re.search(r"\d+(?:\.\d+)?", (price_text or "").replace(",", ""))
    return float(m.group()) if m else None


def validate_record(raw: dict) -> Book:
    return Book(**raw, price_gbp=parse_price(raw.get("price_text")))


def reason(err: ValidationError) -> str:
    return "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in err.errors())
