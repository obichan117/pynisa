# Monex Securities (マネックス証券) NISA Ranking Research

## Summary

Monex does NOT have a single dedicated, regularly-updated public ranking page for individual stock NISA purchases (unlike Rakuten/SBI). Instead, NISA ranking data is scattered across:

1. **Investment trust (fund) rankings** on `fund.monex.co.jp` (dedicated ranking system)
2. **Age-group fund rankings** on `info.monex.co.jp` (server-rendered HTML)
3. **One-off news articles** on `info.monex.co.jp/news/` (editorial content, not machine-readable)

There is **no publicly accessible JSON API** for NISA rankings discovered.

---

## 1. Investment Trust (Fund) Rankings — `fund.monex.co.jp`

### URLs

| Ranking Type | URL |
|---|---|
| All rankings overview | `https://fund.monex.co.jp/rankinglist` |
| NISA monthly sales (売れ筋) | `https://fund.monex.co.jp/rankinglist?type=NisaMonthlySales` |
| NISA monthly reserve contracts (積立契約件数) | `https://fund.monex.co.jp/rankinglist?type=NisaMonthlyReserve` |
| Tsumitate NISA monthly reserve | `https://fund.monex.co.jp/rankinglist?type=RsrvNisaMonthRsrv` |
| SP/mobile view | `https://fund.monex.co.jp/rankinglist?spview=on` |

### Data Fields (expected)

- Rank position
- Fund name
- Fund code (dscrCd)
- Trust fee rate (信託報酬率)
- Fund type/category

### Technical Notes

- The `fund.monex.co.jp` domain consistently **times out** when fetched programmatically (60s timeout exceeded). This suggests heavy JavaScript rendering, bot protection, or WAF.
- No JSON API endpoint found. Tried `/api/v1/rankinglist` and `?format=json` — both failed.
- Fund detail pages use pattern: `?page=detail-by-code&dscrCd=XXXX`
- The pages appear to be **JavaScript-rendered** (likely React/Vue SPA), which explains why simple HTTP fetches time out or return empty content.
- **Authentication**: The ranking list pages themselves are public, but links to fund details redirect through `mst.monex.co.jp` SSO for account-specific features.

### API Discovery Status

**Not found.** The `fund.monex.co.jp` site likely uses internal APIs to render rankings client-side, but:
- The domain blocks or rate-limits non-browser requests
- No publicly documented API exists
- Browser DevTools inspection would be needed to discover XHR endpoints

---

## 2. Age-Group Fund Rankings — `info.monex.co.jp`

### URL

`https://info.monex.co.jp/nisa/ranking/age-group.html`

### Data Fields

- Age group categories: 20s-30s, 40s-50s, 60+
- Two NISA frameworks: Growth Investment (成長投資枠) and Accumulation (つみたて投資枠)
- Top 10 funds per category
- Fund names
- Operating companies
- Ranked by investment amount (積立金額)

### Technical Notes

- **Server-side rendered HTML** — data is embedded directly in the page
- Data period example: 2026-02-02 to 2026-02-27 (約定日ベース)
- Updated monthly
- **No API endpoints** visible; static HTML
- **Public access**: Yes, no authentication required to view rankings
- GTM tracking implemented

---

## 3. Individual Stock Rankings — News Articles (Editorial)

Monex publishes individual stock NISA rankings as **one-off news articles**, not as a regularly updated data page.

### Known Articles

| Title | URL | Period |
|---|---|---|
| 2025年の米国株NISAで人気の個別銘柄 | `https://info.monex.co.jp/news/2025/20251204_03.html` | Jan 1 - Nov 18, 2025 |
| 米国株をNISA口座で投資する人気銘柄 | `https://info.monex.co.jp/news/2026/20260115_01.html` | As of Dec 24, 2025 |
| 新NISA 日本株・米国株の人気ランキングTOP20 | `https://media.monex.co.jp/articles/-/23731` | January 2024 |

### Data Fields (from articles)

**US Individual Stocks:**
- Rank position
- Ticker symbol (e.g., NVDA, TSLA)
- Company name (Japanese + English)
- Stock price in USD
- Stock price in JPY (converted)
- Business description
- Ranked by: 買付口座数 (purchase account count)

**US ETFs (from 2026/01 article):**
- Rank position
- Ticker symbol
- ETF name
- Benchmark index
- Minimum purchase amount (JPY)
- Distribution yield (%)
- Annual per-share distributions (USD)
- Ranked by: 保有口座数 (holding account count)

**Japanese Stocks (from media.monex.co.jp article):**
- Rank position
- Ticker code (e.g., 9432, 8306, 2914)
- Company name
- Industry classification
- Ranked by: 買付約定ユーザー数 (purchase transaction user count)

### Sample Data — US Stocks (2025 article)

| Rank | Ticker | Company |
|------|--------|---------|
| 1 | NVDA | NVIDIA |
| 2 | PLTR | Palantir Technologies |
| 3 | TSLA | Tesla |
| 4 | PFE | Pfizer |
| 5 | AAPL | Apple |
| 6 | VZ | Verizon Communications |
| 7 | KO | Coca-Cola |
| 8 | MSFT | Microsoft |
| 9 | SOFI | SoFi |
| 10 | MO | Altria Group |

### Sample Data — Japanese Stocks (Jan 2024, media.monex.co.jp)

| Rank | Code | Company |
|------|------|---------|
| 1 | 9432 | NTT |
| 2 | 8306 | 三菱UFJフィナンシャル |
| 3 | 2914 | 日本たばこ産業 |
| 7 | 7203 | トヨタ自動車 |

### Technical Notes

- These are **static HTML editorial articles** — no API, no dynamic data loading
- Published irregularly (not monthly)
- Would need to **scrape HTML** to extract data
- URL pattern for news: `https://info.monex.co.jp/news/{year}/{date}_{seq}.html`
- URL pattern for media: `https://media.monex.co.jp/articles/-/{id}`

---

## 4. Old Tsumitate NISA Rankings

### URL

`https://info.monex.co.jp/nisa/tsumitate/product/ranking.html`

### Status

- Contains **outdated data** (Q1 2022)
- Static HTML
- Likely no longer maintained since new NISA system launched in 2024

---

## Authentication Summary

| Resource | Auth Required? |
|---|---|
| Fund rankings (`fund.monex.co.jp/rankinglist`) | No (public page, but hard to scrape) |
| Age-group rankings (`info.monex.co.jp/nisa/ranking/`) | No |
| News articles (`info.monex.co.jp/news/`) | No |
| Media articles (`media.monex.co.jp/articles/`) | No |
| Fund detail pages (buy/sell) | Yes (SSO via `mst.monex.co.jp`) |

---

## Comparison with Other Brokers

| Feature | Monex | Rakuten | SBI |
|---|---|---|---|
| Dedicated stock NISA ranking page | No (articles only) | ? | ? |
| Fund NISA ranking page | Yes (`fund.monex.co.jp`) | ? | ? |
| JSON API for rankings | Not found | ? | ? |
| Regular update cadence | Irregular (articles) / Monthly (funds) | ? | ? |
| Individual stock data | US stocks only (in articles) | ? | ? |

---

## Recommendations for pynisa

1. **Fund rankings**: The `fund.monex.co.jp` domain is heavily protected and times out on non-browser fetches. Would require **headless browser** (Playwright/Selenium) to access, or reverse-engineering the internal API via browser DevTools.

2. **Individual stock rankings**: Only available as editorial articles published irregularly. Not suitable for automated data collection unless you scrape specific known article URLs.

3. **Age-group fund rankings**: The `info.monex.co.jp/nisa/ranking/age-group.html` page is server-rendered HTML and accessible. Could be scraped with simple HTTP requests + BeautifulSoup.

4. **Priority recommendation**: Focus on `fund.monex.co.jp` fund rankings if fund data is needed. For individual stocks, Monex is not a good source compared to brokers that have dedicated ranking pages. The news articles are useful for one-time reference but not for automated tracking.

5. **Next step**: Use browser DevTools (Network tab) on `fund.monex.co.jp/rankinglist?type=NisaMonthlySales` to discover internal XHR/API endpoints. The site likely makes API calls that return JSON, but these are not publicly documented.
