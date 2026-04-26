const axios = require('axios');
const cheerio = require('cheerio');

async function extractArticleInfo(url) {
  try {
    const response = await axios.get(url);
    const $ = cheerio.load(response.data);

    // Extract title: remove site name suffix after dash or pipe
    let title = $('meta[property="og:title"]').attr('content');
    if (!title) {
      title = $('title').text().trim();
    }
    // Remove common site name suffixes (e.g., " - Yahoo News Singapore")
    const cleanedTitle = title.replace(/\s*[-|]\s*Yahoo\s+News.*/i, '').trim();

    // Extract publication date and normalize to ISO string
    let date = $('meta[property="article:published_time"]').attr('content');
    if (!date) {
      const dateTimeAttr = $('time[datetime]').attr('datetime');
      const timeText = $('time[datetime]').text().trim();
      date = dateTimeAttr || timeText;
    }
    const parsedDate = date ? new Date(date).toISOString() : null;

    // Extract price: find first monetary value in USD that is related to product cost
    const textContent = $('p, h1, h2, h3, span').text();
    // Match USD amounts (e.g., $5000, $5,000, $5,000.99)
    const priceMatch = textContent.match(/\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?/);
    const price = priceMatch ? priceMatch[0] : null;

    return {
      title: cleanedTitle,
      date: parsedDate,
      price: price,
      url: url
    };
  } catch (error) {
    throw new Error(`Failed to extract article info: ${error.message}`);
  }
}

module.exports = extractArticleInfo;