# Matsui Securities NISA Ranking - Research

## Summary

Matsui Securities (松井証券) publishes weekly NISA rankings across three asset classes: Japanese stocks, US stocks, and investment trusts.
The ranking pages are publicly viewable (no login required) at `www.matsui.co.jp/nisa/ranking/`.
**No JSON API was found.** The ranking tables in the HTML are **empty** -- data is loaded entirely via client-side JavaScript after page load. The JS bundle that populates the tables could not be identified through static analysis (only analytics scripts are visible in the HTML source). This means scraping requires a **headless browser** (Selenium/Playwright) to execute JavaScript and render the tables.

## Public URLs

### NISA Ranking Pages (No Login Required)

**Japanese Stocks (日本株):**
```
https://www.matsui.co.jp/nisa/ranking/
```

**Investment Trusts (投資信託):**
```
https://www.matsui.co.jp/nisa/ranking/fund.html
```

**US Stocks (米国株):**
```
https://www.matsui.co.jp/nisa/ranking/us-stock.html
```

### Related Domains

| Domain | Purpose | Auth Required |
|--------|---------|---------------|
| `www.matsui.co.jp` | Main site, NISA ranking pages | No |
| `finance.matsui.co.jp` | Market data, general stock rankings | 403 (likely referrer/session gated) |
| `fund.matsui.co.jp` | Investment trust info | Redirects to maintenance page |
| `deal.matsui.co.jp` | Trading interface | Yes (login required) |

### General Stock Rankings (Non-NISA, for reference)
```
https://www.matsui.co.jp/stock/ranking/
```
This page has **some data server-side rendered** (weekly trading volume ranking is embedded in HTML) while other sections (day trading popularity) load dynamically. Links to individual stocks go to `finance.matsui.co.jp/stock/{code}/index`.

## Ranking Categories

### Japanese Stocks (日本株) - 3 rankings
| Category | Japanese | Content |
|----------|----------|---------|
| Weekly Purchase Amount | 週間買付金額ランキング(成長投資枠) | Top stocks by NISA purchase amount |
| Weekly Trading Volume | 週間出来高ランキング(成長投資枠) | Top stocks by NISA trading volume |
| Weekly Balance | 週間残高ランキング(成長投資枠) | Top stocks by NISA holdings balance |

### Investment Trusts (投資信託) - 4 rankings
| Category | Japanese | Content |
|----------|----------|---------|
| Weekly Purchase Amount | 週間買付金額ランキング(成長投資枠+つみたて投資枠) | Top funds by purchase amount |
| Weekly Purchase Count | 週間買付件数ランキング | Top funds by number of purchases |
| Weekly Auto-Investment Count | 週間積立設定件数ランキング | Top funds by new auto-invest setups |
| Weekly Auto-Investment Amount | 週間積立設定金額ランキング | Top funds by auto-invest amount |

### US Stocks (米国株) - 2 rankings
| Category | Japanese | Content |
|----------|----------|---------|
| Stock Weekly Purchase Amount | 【株】週間買付金額ランキング(成長投資枠) | Top US stocks by purchase amount |
| ETF Weekly Purchase Amount | 【ETF】週間買付金額ランキング(成長投資枠) | Top US ETFs by purchase amount |

## Data Fields

### Japanese Stock Rankings
| Field | Japanese | Description | Example |
|-------|----------|-------------|---------|
| Rank | 順位 | Position in ranking | 1 |
| Week-over-week change | 前週比 | Movement vs previous week | ↑, ↓, → |
| Stock code | コード | 4-digit ticker code | 7203 |
| Stock name | 銘柄名 | Japanese company name | トヨタ自動車 |
| Current price | 現在値 | Latest stock price | 2,500 |
| Minimum investment | 最低投資金額 | Min buy amount in yen | 250,000 |

### Investment Trust Rankings
| Field | Japanese | Description | Example |
|-------|----------|-------------|---------|
| Rank | 順位 | Position in ranking | 1 |
| Week-over-week change | 前週比 | Movement vs previous week | ↑, ↓, → |
| Fund name | ファンド名 | Full fund name | eMAXIS Slim 全世界株式 |
| NAV | 基準価額 | Net asset value | 25,000 |
| Growth frame | 成長投資枠 | Eligible for growth frame | ○/× |
| Accumulation frame | つみたて投資枠 | Eligible for accumulation frame | ○/× |

### US Stock Rankings
| Field | Japanese | Description | Example |
|-------|----------|-------------|---------|
| Rank | 順位 | Position in ranking | 1 |
| Week-over-week change | 前週比 | Movement vs previous week | ↑, ↓, → |
| Stock code | コード | US ticker symbol | AAPL |
| Stock name | 銘柄名 | Company/ETF name | Apple |
| Industry | 業種 | Sector (stocks only) | Technology |
| Minimum investment (JPY) | 最低投資金額 | Min buy in yen (last business day rate * price) | 35,000 |

## Technical Architecture

### Page Rendering
- **CMS/Framework**: Not identified (no webpack/vite/next.js artifacts visible)
- **Rendering**: Client-side JavaScript populates empty HTML table templates
- **Analytics scripts only visible**: Google Tag Manager (GTM-TL6ZFV), Rtoaster, eBis
- **No visible JS bundle**: The JavaScript file(s) that load ranking data are not identifiable from the HTML source alone. They may be injected via Google Tag Manager or loaded dynamically.

### Why Tables Appear Empty
The raw HTML contains table headers but **zero data rows** in `<tbody>`. When fetched without JavaScript execution (curl, requests, WebFetch), the tables are empty. The data is populated by JavaScript after page load, likely by:
1. A JS bundle injected via Google Tag Manager (GTM-TL6ZFV), or
2. A deferred/async script not visible in the initial HTML, or
3. An inline script that runs after DOM ready (stripped by the fetch tool)

### Hidden API (Not Confirmed)
Despite extensive probing, no JSON API endpoint was discovered:
- `https://www.matsui.co.jp/api/nisa/ranking` → 404
- `https://www.matsui.co.jp/nisa/ranking/ranking.json` → 404
- `https://www.matsui.co.jp/nisa/ranking/data/` → 404
- `https://www.matsui.co.jp/nisa/ranking/api/ranking` → 404
- `https://finance.matsui.co.jp/nisa/ranking` → 403

The `finance.matsui.co.jp` domain returns 403 for direct access, suggesting it requires specific referrer headers or session tokens. Known working paths on this domain (from sitemap):
- `finance.matsui.co.jp/ranking-rise/index` (stock price rise ranking)
- `finance.matsui.co.jp/ranking-fall/index` (stock price fall ranking)
- `finance.matsui.co.jp/ranking-volume/index` (trading volume ranking)
- `finance.matsui.co.jp/ranking-trading-top/index` (trading value ranking)

None of these are NISA-specific.

### Authentication
- NISA ranking pages on `www.matsui.co.jp`: **No login required** (public)
- `finance.matsui.co.jp`: Returns 403 (referrer/session gated, not standard login)
- `deal.matsui.co.jp`: **Login required** (trading interface)

## Data Extraction Approach

### Recommended: Headless Browser (Playwright/Selenium)

Since the data is loaded via client-side JavaScript with no discoverable JSON API:

1. **Launch headless browser** (Playwright recommended over Selenium for performance)
2. **Navigate** to the ranking URL
3. **Wait for table data** to populate (wait for `<tbody>` to contain `<tr>` elements)
4. **Parse** the rendered HTML table rows
5. **Extract** rank, code, name, price, and other fields from `<td>` elements

### Alternative: Intercept XHR (Needs Browser DevTools Investigation)

A real browser's Network tab (DevTools) should reveal the XHR/fetch requests made when the page loads. This would expose the actual API endpoint and allow direct JSON access without rendering. **This investigation requires manual browser inspection** -- the endpoint could not be determined through static analysis alone.

### Challenges
- Requires JavaScript execution (no simple HTTP GET scraping)
- JS loading mechanism is opaque (possibly GTM-injected)
- No pagination info available (unknown if top 10, 20, or 50)
- Updated weekly (specific day not confirmed)
- HTML table structure may change without notice
- `finance.matsui.co.jp` API access pattern is unclear

## Comparison with Other Brokerages

| Feature | Matsui Securities | SBI Securities | Rakuten Securities |
|---------|------------------|---------------|-------------------|
| Public Access | Yes | Yes (IRIS pages) | Yes |
| JSON API | Not found | No | No (form-based) |
| Data Format | Client-side JS rendered | Server-rendered HTML | Server-rendered HTML |
| Scraping Method | Headless browser required | HTTP GET + HTML parse | HTTP GET + HTML parse |
| Asset Classes | JP stocks, US stocks, funds | JP stocks, funds | JP stocks, funds |
| Ranking Types | 9 total (3+4+2) | 4 total | Multiple |
| Extra Fields | Price, min investment, industry | Rank + name only | More extensive |
| Update Frequency | Weekly | Weekly | Weekly |
| Authentication | Not required | Not required for IRIS | Not required |

## Next Steps

1. **Manual browser inspection**: Open `https://www.matsui.co.jp/nisa/ranking/` in Chrome, open DevTools Network tab, filter XHR/Fetch, reload page. This will reveal the actual API endpoint(s) used to load ranking data.
2. **Playwright prototype**: Write a quick script to render the page and extract table data.
3. **GTM container analysis**: Inspect the GTM container (GTM-TL6ZFV) to find injected scripts that may load the ranking data.
