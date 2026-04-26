import pytest
from scraper.price_extractor import extract_price_from_text, extract_price_from_html

def test_extract_price_from_text():
    # Test various formats
    assert extract_price_from_text("Only $1,299.99 today!") == 1299.99
    assert extract_price_from_text("Was $500, now $300!") == 500.0
    assert extract_price_from_text("€99.99 for limited time") == 99.99
    assert extract_price_from_text("Just £75!") == 75.0
    assert extract_price_from_text("Save $200 on $500 monitor") == 200.0
    assert extract_price_from_text("Starting at $100.50") == 100.5
    assert extract_price_from_text("Buy now for 1500 USD") == 1500.0
    assert extract_price_from_text("¥1,200 special offer") == 1200.0
    assert extract_price_from_text("No price here") is None
    assert extract_price_from_text("Free!") is None
    assert extract_price_from_text("$5, $10, $1000") == 5.0  # First, not minimum

def test_extract_price_from_html():
    html = """
    <div class="product">
        <h1>LG 34-inch Curved Monitor</h1>
        <p>Now <span class="price">$499.99</span> was $699.99</p>
        <p>Save $200 instantly!</p>
    </div>
    """
    assert extract_price_from_html(html) == 499.99

    html_no_match = "<p>No prices listed</p>"
    assert extract_price_from_html(html_no_match) is None

def test_edge_cases():
    # Malformed but plausible
    assert extract_price_from_text("$1,000,000.00 prize") == 1000000.0
    assert extract_price_from_text("Price: .99 cents") is None  # Not valid
    assert extract_price_from_text("10,000€ available") == 10000.0
    assert extract_price_from_text("Only $5 99") is None  # Invalid format
    assert extract_price_from_text("$123") == 123.0