# SBI Securities NISA Ranking - Research

## Summary

SBI Securities publishes weekly NISA purchase rankings for domestic stocks and investment trusts.
The ranking data is publicly viewable (no login required) through the IRIS ranking system on their main website.
**No clean JSON API was found** -- the data is server-rendered HTML within the IRIS template system.

## Public URLs

### Weekly NISA Ranking Pages (No Login Required)

**Domestic Stocks (国内株式):**
```
https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETmgR001Control&_DataStoreID=DSWPLETmgR001Control&_PageID=WPLETmgR001Mdtl20&_ActionID=DefaultAID&getFlg=on&burl=iris_ranking&cat1=market&cat2=ranking&file=index.html&dir=tl1-rnk%7Ctl2-nisa%7Ctl3-stock&OutSide=on
```

**Investment Trusts (投資信託):**
```
https://www.sbisec.co.jp/ETGate/?OutSide=on&getFlg=on&_ControlID=WPLETmgR001Control&_PageID=WPLETmgR001Mdtl20&_ActionID=DefaultAID&_DataStoreID=DSWPLETmgR001Control&burl=iris_ranking&cat1=market&cat2=ranking&dir=tl1-rnk%7Ctl2-nisa%7Ctl3-fund&file=index.html
```

Alternative subdomains also work (same content):
- `site1.sbisec.co.jp`
- `site2.sbisec.co.jp`
- `site3.sbisec.co.jp`

### Annual Ranking Page (Static HTML, Public)
```
https://go.sbisec.co.jp/prd/common/newyear_forecast_2025_ranking2024.html
```

### Old marble URLs (NO LONGER WORK -- redirect to homepage)
```
https://site0.sbisec.co.jp/marble/domestic/ranking/nisa/
https://site0.sbisec.co.jp/marble/domestic/ranking/nisa/nisa.do
```

### Fund Ranking via marble (REQUIRES LOGIN -- redirects to login page)
```
https://site0.sbisec.co.jp/marble/fund/ranking/fundranking.do?Param6=salesprice
```

## Ranking Categories

4 ranking types are published weekly:

| Category | Japanese | Content |
|----------|----------|---------|
| Domestic Stock Purchase Amount | 国内株式 買付金額 | Top 10 stocks by NISA purchase amount |
| Domestic Stock Holdings Balance | 国内株式 保有残高 | Top 10 stocks by NISA holdings value |
| Investment Trust Purchase Amount | 投資信託 買付金額 | Top 10 funds by NISA purchase amount |
| Investment Trust Purchase Count | 投資信託 買付件数 | Top 10 funds by NISA purchase count |

## Data Fields

### Domestic Stock Rankings
| Field | Description | Example |
|-------|-------------|---------|
| Rank | Position 1-10 | 1 |
| Week-over-week change | Arrow indicator | ↑, ↓, →, New! |
| Company name | Japanese company name | 日本たばこ産業 |
| Ticker code | 4-digit stock code | 2914 |

### Investment Trust Rankings
| Field | Description | Example |
|-------|-------------|---------|
| Rank | Position 1-10 | 1 |
| Week-over-week change | Arrow indicator | ↑, ↓, →, New! |
| Fund name | Full fund name | eMAXIS Slim 全世界株式（オール・カントリー） |

Note: The ranking pages show **only rank, name/code, and week-over-week movement**.
No prices, volumes, or purchase amounts are disclosed.

## Technical Architecture

### Page Rendering System
- System: **ETGate** (SBI's proprietary portal framework)
- Template: **IRIS** ranking system (`burl=iris_ranking`)
- Rendering: Server-side HTML with client-side JavaScript for real-time price overlays
- The ranking table data is **embedded in the server-rendered HTML**, not loaded via a separate API call

### Real-Time Price Overlay (NOT the ranking data)
```
Base URL: https://vc.iris.sbisec.co.jp/vc/psdata/
Endpoint: ricDataList.do
Parameters: ricCodeList, hash, investor, callback
Example RICs: .N225, .DJI, JPY=X, EURJPY=X
Format: JSONP
```
This endpoint only provides real-time market index prices displayed in the header area.
It does NOT serve the ranking table data.

### Authentication
- The IRIS ranking pages (with `OutSide=on` or `getFlg=on`) are **publicly accessible without login**
- The marble/fund/ranking pages **require login** (redirect to login.sbisec.co.jp)
- The mobile site ranking pages **require login**

## Data Extraction Approach

Since no JSON API exists, data must be extracted via **HTML scraping**:

1. **HTTP GET** the IRIS ranking URL
2. **Parse HTML** to extract the ranking table (`<table class="md-table02">` or similar)
3. **Extract** rank, company name, ticker code, and week-over-week indicator from table rows
4. The page uses Shift-JIS or similar Japanese encoding (may need encoding handling)

### Challenges
- Content may be encoded in Shift_JIS (not UTF-8)
- Page uses ETGate framework with complex URL parameters
- No pagination (only top 10 shown)
- Updated weekly (specific day not confirmed, likely Monday)
- The HTML structure may change without notice

## Sample Data (2024 Annual)

### NISA Growth Investment - Domestic Stock (by Purchase Amount)
| Rank | Code | Company |
|------|------|---------|
| 1 | 9432 | NTT |
| 2 | 8306 | Mitsubishi UFJ Financial Group |
| 3 | 2914 | Japan Tobacco (JT) |
| 4 | 7203 | Toyota Motor |
| 5 | 8058 | Mitsubishi Corporation |
| 6 | 7011 | Mitsubishi Heavy Industries |
| 7 | 9433 | KDDI |
| 8 | 4661 | Oriental Land |
| 9 | 4503 | Astellas Pharma |
| 10 | 5401 | Nippon Steel |

## Third-Party Sources

Diamond ZAi Online publishes SBI's weekly NISA rankings with the same data:
- https://diamond.jp/zai/articles/-/1027895 (weekly articles, different URL per week)
- https://www.diamond.co.jp/zai/articles/-/305 (monthly fund rankings)

These may be easier to scrape than SBI's ETGate pages.

## Comparison with Rakuten

| Feature | SBI Securities | Rakuten Securities |
|---------|---------------|-------------------|
| Public Access | Yes (IRIS pages) | Yes |
| JSON API | No | No (form-based) |
| Data Format | Server-rendered HTML | Server-rendered HTML |
| Rankings | Top 10 only | More extensive |
| Update Frequency | Weekly | Weekly |
| Authentication | Not required for IRIS | Not required |
