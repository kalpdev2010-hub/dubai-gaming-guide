import re
from typing import Optional, List

def extract_price_from_text(text: str) -> Optional[float]:
    """
    Extracts the first monetary value from text in a robust way.
    Handles various currency formats like $1,299.99, $500, €100, £75.50, etc.
    Returns the first found price (most prominent in text) as a float.
    """
    # Comprehensive regex to match prices with optional currency symbols
    # Matches: $1,234.56, $123, €99.99, £1,200.00, 1000 USD, etc.
    price_pattern = re.compile(
        r"""
        (?<!\d)                                  # Negative lookbehind for digit
        (?:                                       
            [$€£¥₹]                               # Currency symbols at start
            |                                    # or
            (?=\d)                               # Lookahead for digit (for symbol after)
        )
        \s*                                      # Optional whitespace
        (\d{1,3}(?:,\d{3})*(?:\.\d{2})?          # Group with commas (e.g. 1,000,000.00)
        |\d+(?:\.\d{2})?)                        # or simple number with optional decimal
        (?:\s*(?:USD|CAD|EUR|GBP|JPY|CNY))?      # Optional currency code
        |                                        # OR
        (\d+(?:\.\d{2,})?)                       # Number with optional decimal (no commas)
        \s*(?:[$€£¥₹]                             # Currency symbol after
        |(?:USD|CAD|EUR|GBP|JPY|CNY))
        """,
        re.VERBOSE
    )
    
    matches = price_pattern.findall(text)
    
    # Flatten the tuple matches from two groups into single list of found prices
    valid_prices = []
    for match in matches:
        # Each match is a tuple of (group1, group2) — take the non-empty one
        price_str = next(filter(bool, match), "")
        if price_str:
            # Remove commas and extract number
            cleaned = re.sub(r'[^\d.]', '', price_str)
            try:
                price = float(cleaned)
                # Only consider reasonable price range for a monitor
                if 10 <= price <= 10000:
                    valid_prices.append(price)
            except ValueError:
                continue
    
    # Return the first valid price found (most prominent in text)
    # Avoids picking a lower accessory price over the main product
    return valid_prices[0] if valid_prices else None


def extract_price_from_html(html_content: str) -> Optional[float]:
    """
    Extract price from raw HTML content by stripping tags and processing text.
    """
    # Simple HTML tag removal
    text_content = re.sub(r'<[^>]+>', ' ', html_content)
    # Collapse whitespace
    text_content = re.sub(r'\s+', ' ', text_content)
    return extract_price_from_text(text_content)