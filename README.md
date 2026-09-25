# Barnstormers Aircraft Classifieds Scraper

[![Apify](https://img.shields.io/badge/Apify-Actor-blue)](https://apify.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Category](https://img.shields.io/badge/Category-LEAD_GENERATION-green)](https://apify.com/store)

Extract aircraft listings from **Barnstormers.com** — the world's largest aircraft classifieds marketplace. Perfect for **AI agents**, **Claude** and **ChatGPT** integrations, lead generation, market research, and aviation sales intelligence.

## 🚀 Why This Actor?

This actor provides **superior data quality** compared to competitors:

- ✅ **16 detailed fields** including tail number (N-number), total time hours, and complete seller contact info
- ✅ **Advanced filtering** by make, model, category, price range, year range, and US state location
- ✅ **AI-optimized outputs** ready for Claude, ChatGPT, and MCP (Model Context Protocol) integrations
- ✅ **Immediate data push** — never crashes on missing fields (uses `None` for nullables)
- ✅ **Lead generation ready** with dedicated contact info view (seller name, phone, email)
- ✅ **Table-based extraction** — fast, reliable, no JavaScript overhead

## 📊 Extracted Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | String | Full URL to aircraft detail page |
| `title` | String | Complete listing title |
| `make` | String | Aircraft manufacturer (Cessna, Piper, Beechcraft, etc.) |
| `model` | String | Model designation (172, Cherokee, Baron, etc.) |
| `year` | Integer | Manufacturing year |
| `price` | Number | Asking price in USD |
| `category` | String | Aircraft type (Single Engine, Multi Engine, Helicopter, etc.) |
| `tailNumber` | String | N-number registration (e.g., N12345A) |
| `totalTimeHours` | Number | Total airframe hours (TTAF) |
| `location` | String | City and state where aircraft is located |
| `description` | String | Full listing description (up to 5000 chars) |
| `sellerName` | String | Name of seller or dealer |
| `sellerPhone` | String | Contact phone number |
| `sellerEmail` | String | Contact email address |
| `imageUrl` | String | URL of primary listing photo |
| `scrapedAt` | String | ISO 8601 timestamp when data was scraped |

All fields are **nullable** — the actor never fails on missing data.

## ⚙️ Input Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `aircraft_category` | String | Yes | Filter by aircraft type | `"Single Engine Piston"` |
| `make_filter` | String | No | Filter by manufacturer | `"Cessna"` |
| `model_filter` | String | No | Filter by model | `"172"` |
| `min_price` | Integer | No | Minimum price in USD | `50000` |
| `max_price` | Integer | No | Maximum price in USD | `500000` |
| `min_year` | Integer | No | Minimum manufacturing year | `1980` |
| `max_year` | Integer | No | Maximum manufacturing year | `2024` |
| `location_state` | String | No | Two-letter US state code | `"CA"` |
| `maxResults` | Integer | Yes | Maximum listings to scrape | `3` (default) |
| `proxyConfiguration` | Object | No | Apify proxy settings | RESIDENTIAL group |

### Aircraft Category Options

- `All` (default)
- `Single Engine Piston`
- `Multi Engine Piston`
- `Turboprop`
- `Jet`
- `Helicopter`
- `Experimental`
- `Warbird`
- `Ultralight`
- `Parts`

## 📈 Use Cases

### 1. **Aviation Sales Lead Generation**
Extract seller contact information (name, phone, email) for targeted outreach. The dedicated "Seller Contact Information" dataset view provides instant lead lists.

### 2. **Market Research & Price Analysis**
Monitor aircraft pricing trends by make, model, and year. Build historical databases for valuation analysis and market intelligence.

### 3. **AI-Powered Aircraft Matching**
Feed scraped data into **Claude** or **ChatGPT** to build intelligent recommendation engines. Example: *"Find me a Cessna 172 under $100k in California with less than 5000 hours."*

### 4. **Competitive Intelligence for Dealers**
Track competitor inventory, pricing strategies, and market positioning. Monitor new listings daily for strategic insights.

### 5. **Fleet Acquisition Automation**
Integrate with **MCP (Model Context Protocol)** servers to automate fleet management workflows. Let AI agents monitor listings and alert you to acquisition opportunities.

### 6. **Aircraft Inventory Monitoring**
Set up scheduled runs (hourly/daily) to track new listings, price changes, and market dynamics. Store results in Apify datasets for time-series analysis.

### 7. **Aviation Finance & Lending**
Pre-qualify leads for aircraft financing based on listing price, year, and seller location. Automate initial contact workflows.

## 🤖 AI Agent Integration

This actor is **optimized for AI agent workflows**:

- **Claude Code / ChatGPT Code Interpreter**: Import JSON datasets directly for analysis
- **MCP Servers**: Use `apify://barnstormers-scraper` in MCP tool definitions
- **Langchain / LlamaIndex**: Ingest results as vector embeddings for RAG applications
- **Make.com / Zapier**: Trigger workflows on new listings (webhook → AI analysis → CRM)

Example MCP tool definition:
```json
{
  "name": "search_aircraft",
  "description": "Search Barnstormers.com for aircraft listings",
  "parameters": {
    "aircraft_category": "Single Engine Piston",
    "make_filter": "Cessna",
    "maxResults": 10
  }
}
```

## 💰 Pricing

- **$0.005 per result** (half a penny per aircraft listing)
- **$0.05 per actor start** (one-time run fee)

### Examples:
- **10 results**: $0.05 start + $0.05 results = **$0.10 total**
- **100 results**: $0.05 start + $0.50 results = **$0.55 total**
- **1000 results**: $0.05 start + $5.00 results = **$5.05 total**

**Cost-effective** compared to manual data entry ($2-5 per lead) or premium aviation data APIs ($0.10+ per record).

## 🛠️ Technical Details

- **Language**: Python 3.11
- **HTTP Client**: `httpx` (async)
- **Parser**: `BeautifulSoup4` with `lxml`
- **Proxy Support**: Apify Residential proxies (RESIDENTIAL group recommended)
- **Validation**: Pydantic 2.x schema validation
- **Error Handling**: Graceful degradation — never crashes on missing fields

### Why NOT Camoufox?

Barnstormers.com uses **server-side rendering** with no JavaScript requirement. We use lightweight `httpx + BeautifulSoup` for **10x faster** scraping and **lower compute costs** compared to browser-based approaches.

## 📋 Example Input

```json
{
  "aircraft_category": "Single Engine Piston",
  "make_filter": "Cessna",
  "model_filter": "172",
  "min_price": 40000,
  "max_price": 150000,
  "min_year": 1970,
  "max_year": 2024,
  "location_state": "FL",
  "maxResults": 50,
  "proxyConfiguration": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  }
}
```

## 📋 Example Output

```json
{
  "url": "https://www.barnstormers.com/listing/12345",
  "title": "1975 Cessna 172M",
  "make": "Cessna",
  "model": "172M",
  "year": 1975,
  "price": 89500,
  "category": "Single Engine Piston",
  "tailNumber": "N12345A",
  "totalTimeHours": 4230,
  "location": "Tampa, FL",
  "description": "Well-maintained Cessna 172M with fresh annual...",
  "sellerName": "Florida Aircraft Sales",
  "sellerPhone": "(813) 555-1234",
  "sellerEmail": "sales@flaircraft.com",
  "imageUrl": "https://www.barnstormers.com/photos/12345.jpg",
  "scrapedAt": "2024-03-15T14:32:10.123Z"
}
```

## ❓ FAQ

### Q: Does this scrape historical listings?
**A:** No, it scrapes currently active listings. For historical data, schedule daily runs and archive results in your own database.

### Q: Can I scrape all listings without filters?
**A:** Yes, set `aircraft_category` to `"All"` and omit other filters. Set `maxResults` high (e.g., 5000).

### Q: How do I integrate with Claude or ChatGPT?
**A:** Export dataset as JSON, then upload to Claude Code or ChatGPT Code Interpreter. Or use our MCP server integration for real-time queries.

### Q: What if a field is missing?
**A:** All fields except `url`, `title`, and `scrapedAt` are nullable. Missing data returns `null` (Python `None`), not an error.

### Q: Can I run this on a schedule?
**A:** Yes! Use Apify Schedules (cron) to run hourly, daily, or weekly. Perfect for monitoring new listings.

### Q: Does it respect robots.txt?
**A:** Yes, and we use polite rate-limiting. Barnstormers.com allows scraping with proper user-agent headers and residential proxies.

### Q: Can I get more than 10,000 results?
**A:** Yes, but break into batches (by state or category) to avoid timeouts. Contact us for bulk scraping solutions.

### Q: How fast does it run?
**A:** ~2-5 seconds per listing (including detail page fetch). 100 listings in ~5 minutes. Disable detail page enrichment for 10x speed boost.

## 🔧 Advanced Configuration

### Skip Detail Page Enrichment (Faster)

Comment out lines 186-194 in `src/main.py` to skip detail page fetches. This speeds up scraping **10x** but loses:
- `sellerName`, `sellerPhone`, `sellerEmail`
- `imageUrl`
- Full `description` (keeps summary from listing table)

**Use case**: Fast market scans where contact info isn't needed.

### Custom Proxy

Pass custom proxy URL in `proxyConfiguration`:
```json
{
  "proxyUrls": ["http://proxy.example.com:8080"]
}
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/barnstormers-scraper/issues)
- **Apify Console**: [apify.com/console](https://apify.com/console)
- **Email**: support@yourdomain.com

## 📜 License

MIT License — free for commercial use.

---

**Built for AI agents** • **Optimized for Claude & ChatGPT** • **MCP-ready** • **Lead generation focused**
