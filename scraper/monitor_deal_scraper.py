import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """Check if the given URL is valid and well-formed."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def fetch_page_content(url, timeout=10, retries=3):
    """
    Fetch the HTML content of a webpage with retry logic and error handling.
    
    Args:
        url (str): The URL to fetch.
        timeout (int): Request timeout in seconds.
        retries (int): Number of retry attempts on failure.
    
    Returns:
        str: HTML content if successful, None otherwise.
    """
    if not is_valid_url(url):
        logger.error(f"Invalid URL provided: {url}")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            # Ensure correct encoding
            response.encoding = response.apparent_encoding
            logger.info(f"Successfully fetched content from {url}")
            return response.text

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred while fetching {url}: {e}")
            if response.status_code == 404:
                break  # No point retrying if page not found
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error occurred while fetching {url}: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout occurred while fetching {url}: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while fetching {url}: {e}")

        if attempt < retries - 1:
            wait_time = (2 ** attempt) * 1.0  # Exponential backoff
            logger.info(f"Retrying in {wait_time} seconds... (Attempt {attempt + 2}/{retries})")
            time.sleep(wait_time)

    logger.error(f"Failed to retrieve page after {retries} attempts: {url}")
    return None

def extract_deal_title(soup, url):
    """
    Extract the deal title using multiple fallback strategies.
    
    Args:
        soup (BeautifulSoup): Parsed HTML document.
        url (str): Source URL for logging context.
    
    Returns:
        str: Extracted title or None if not found.
    """
    selectors = [
        'h1[data-analytics="headline"]',
        'h1',
        'header.article-header h1',
        'div.article-header h1',
        'title'
    ]

    for selector in selectors:
        try:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                title = element.get_text(strip=True)
                logger.info(f"Title extracted using selector '{selector}': {title}")
                return title
        except Exception as e:
            logger.debug(f"Selector '{selector}' failed: {e}")

    logger.warning(f"Could not extract title from {url}")
    return None

def extract_deal_price(soup, url):
    """
    Extract the deal price using semantic and pattern-based approaches.
    
    Args:
        soup (BeautifulSoup): Parsed HTML document.
        url (str): Source URL for logging context.
    
    Returns:
        str: Extracted price (e.g., "$400 off") or None.
    """
    # Common selectors for pricing info
    price_selectors = [
        'div.deal-price',
        'span.deal-price',
        'div.price-drop',
        'span.price-drop',
        'div.offer-price',
        'p strong',  # Often deals are written as "Get $400 off..."
        'p em',
        'p'
    ]

    # Price-related keywords to look for
    price_keywords = ['off', 'discount', 'save', 'only', 'was', 'now', '%']

    for selector in price_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(strip=True)
            if not text:
                continue

            # Look for price patterns or keywords
            if any(keyword in text.lower() for keyword in price_keywords) and ('$' in text or '%' in text):
                logger.info(f"Price-related text found via '{selector}': {text}")
                return text

    # Fallback: search all paragraphs for price-like content
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text(strip=True)
        if any(keyword in text.lower() for keyword in price_keywords) and ('$' in text or '%' in text):
            logger.info(f"Price-related text found in paragraph: {text}")
            return text

    logger.warning(f"No price information found in {url}")
    return None

def scrape_monitor_deal(url):
    """
    Main function to scrape the deal title and price from a Mashable article.
    
    Args:
        url (str): The URL of the Mashable deal article.
    
    Returns:
        dict: Dictionary containing 'title' and 'price' keys with scraped data.
              Returns None if scraping fails.
    """
    if not url:
        logger.error("No URL provided for scraping.")
        return None

    logger.info(f"Starting scrape for URL: {url}")

    html_content = fetch_page_content(url)
    if not html_content:
        logger.error(f"Cannot proceed without page content: {url}")
        return None

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        title = extract_deal_title(soup, url)
        price = extract_deal_price(soup, url)

        result = {
            "title": title,
            "price": price,
            "source_url": url
        }

        logger.info(f"Scraping completed. Result: {result}")
        return result

    except Exception as e:
        logger.error(f"Unexpected error during HTML parsing or scraping: {e}")
        return None