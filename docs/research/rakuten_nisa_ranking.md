# Rakuten Securities NISA Ranking - Research

Last updated: 2026-03-14

## Summary

Rakuten Securities provides public NISA buy/balance rankings across multiple asset classes.
The **stock/ETF rankings use publicly accessible CSV files** (no authentication required).
The **investment trust (fund) rankings are server-rendered HTML** with no hidden API.

---

## 1. Public URLs

### Stock & ETF Rankings (CSV-backed, public, no auth)

| Page | URL |
|------|-----|
| Domestic stocks & ETF/ETN | `https://www.rakuten-sec.co.jp/web/market/ranking/nisa/` |
| Foreign stocks & ETF | `https://www.rakuten-sec.co.jp/web/market/ranking/nisa/foreign.html` |
| Investment trusts (funds) | `https://www.rakuten-sec.co.jp/web/market/ranking/nisa/fund.html` |

### Fund Rankings (HTML, server-rendered)

| Page | URL |
|------|-----|
| NISA purchase amount | `https://www.rakuten-sec.co.jp/web/fund/rakuten-bank/ranking_detail.html?type=500027` |
| NISA purchase count | `https://www.rakuten-sec.co.jp/web/fund/rakuten-bank/ranking_detail.html?type=500028` |
| NISA accumulation amount | `https://www.rakuten-sec.co.jp/web/fund/rakuten-bank/ranking_detail.html?type=500029` |
| NISA accumulation count | `https://www.rakuten-sec.co.jp/web/fund/rakuten-bank/ranking_detail.html?type=500030` |
| NISA balance | `https://www.rakuten-sec.co.jp/web/fund/rakuten-bank/ranking_detail.html?type=500031` |
| All funds purchase amount | `https://www.rakuten-sec.co.jp/web/fund/find/ranking/ranking.html` |

---

## 2. CSV Endpoints (Hidden API - Best Data Source)

Data is loaded via jQuery `$.get()` on the stock/ETF ranking pages.
These CSV files are **publicly accessible, no authentication required**.

### Base URL

```
https://www.rakuten-sec.co.jp/web/market/ranking/nisa/
```

### Domestic (Japan)

| File | Description |
|------|-------------|
| `JP_STK_TRD_VAL.csv` | Domestic stocks - purchase amount ranking |
| `JP_STK_BALANCE.csv` | Domestic stocks - holdings balance ranking |
| `JP_ETF_TRD_VAL.csv` | Domestic ETF/ETN - purchase amount ranking |
| `JP_ETF_BALANCE.csv` | Domestic ETF/ETN - holdings balance ranking |

### Foreign

| File | Description |
|------|-------------|
| `US_STK_TRD_VAL.csv` | US stocks - purchase amount ranking |
| `US_STK_BALANCE.csv` | US stocks - holdings balance ranking |
| `CH_STK_TRD_VAL.csv` | Chinese stocks - purchase amount ranking |
| `CH_STK_BALANCE.csv` | Chinese stocks - holdings balance ranking |
| `ASN_STK_TRD_VAL.csv` | ASEAN stocks - purchase amount ranking |
| `ASN_STK_BALANCE.csv` | ASEAN stocks - holdings balance ranking |
| `F_ETF_TRD_VAL.csv` | Foreign ETFs - purchase amount ranking |
| `F_ETF_BALANCE.csv` | Foreign ETFs - holdings balance ranking |

**Total: 12 CSV files**

---

## 3. CSV Data Format

### Domestic Stocks (4 columns)

```
rank,direction,ticker_code,name
1,↑,7974,任　天　堂
2,↑,9432,ＮＴＴ
...
2026年2月1日～2026年2月28日,,,
2026年3月2日更新,,,
```

Fields:
- `rank`: Integer 1-10
- `direction`: `↑` (up), `↓` (down), `→` (unchanged), `NEW`
- `ticker_code`: 4-digit Japan stock code (e.g., `7974`)
- `name`: Company name in full-width Japanese

### Foreign Stocks (5 columns)

```
rank,direction,ticker,name,sector
1,↑,MSFT,マイクロソフト,ソフトウェア・サービス
```

Fields:
- `rank`: Integer 1-10
- `direction`: Arrow indicator
- `ticker`: US/foreign ticker symbol (e.g., `MSFT`)
- `name`: Company name in Japanese
- `sector`: Industry classification in Japanese

### Foreign ETFs (6 columns)

```
rank,direction,ticker,name,market,detail_url
1,↑,GLDM,SPDR ゴールド・ミニシェアーズ・トラスト,米国,https://...quote.html?ric=GLDM.N
```

Fields:
- `rank`: Integer 1-10
- `direction`: Arrow indicator
- `ticker`: ETF ticker symbol
- `name`: ETF name in Japanese
- `market`: Market country (米国 etc.)
- `detail_url`: Full URL to quote detail page

### Metadata (last 2 rows)

- Period: `2026年2月1日～2026年2月28日` (monthly aggregation)
- Update date: `2026年3月2日更新`

---

## 4. Fund Ranking (HTML - No API)

The investment trust ranking pages at `/web/fund/rakuten-bank/ranking_detail.html` are **server-rendered HTML**.

### Data Fields Available

| Field | Japanese | Notes |
|-------|----------|-------|
| Rank | 順位 | 01-10 |
| Fund name | ファンド名 | With link to detail |
| Management company | 委託会社 | |
| NAV (base price) | 基準価額 | With daily change |
| Net assets | 純資産 | In 億円 (hundred millions) |
| Fund score (3yr) | ファンドスコア | |
| Category | 分類 | Asset type |
| Sales fee | 販売手数料 | |
| Management fee | 信託報酬 | |
| Return (6mo/1yr/3yr) | リターン | |
| Sharpe ratio | シャープレシオ | |
| Accumulation flag | 積立 | Boolean |
| ¥100 flag | 100円投資 | Boolean |

### Filter Parameters

- `type`: Ranking category (500027=NISA buy amount, 500028=buy count, etc.)
- `freqid`: Period (1=daily, 2=weekly, 3=monthly)
- `tget`: Gender (1=all, 2=male, 3=female)
- `group`: Age (20代, 30代, 40代, 50代, 60代以上)

### Note on Authentication

The fund ranking pages show a login form but the ranking data itself is visible without login.
Some interactive features (favorites, comparison) require authentication.

---

## 5. Authentication Summary

| Resource | Auth Required? |
|----------|---------------|
| CSV files (stock/ETF rankings) | No - fully public |
| Market ranking HTML pages | No - publicly viewable |
| Fund ranking HTML pages | No - data visible without login |
| Fund detail API (`/api/ss/detail/`) | No - returns chart data |
| Favorites/comparison features | Yes - requires login |

---

## 6. Recommended Approach

**Primary: CSV endpoints** for stock/ETF NISA rankings.
- 12 CSV files, publicly accessible, no auth
- Clean structured data, easy to parse
- Updated monthly, data refreshed ~2nd of each month
- Top 10 rankings only

**Secondary: HTML scraping** for fund (investment trust) rankings.
- Server-rendered HTML at `/web/fund/rakuten-bank/ranking_detail.html`
- Richer data (NAV, fees, returns, Sharpe ratio)
- Top 10 rankings, filterable by gender/age/period
- More fragile (HTML structure may change)

---

## 7. Related API Endpoints

| Endpoint | Returns | Notes |
|----------|---------|-------|
| `/api/ss/detail/?ID={ISIN}` | HTML with embedded Highcharts JSON | Fund NAV chart data |
| Security detail link pattern | `https://www.trkd-asia.com/rakutensec/resultcnt_ja.jsp?all=on&sector=na&code={TICKER}` | External (Thomson Reuters) |
| US quote pattern | `/web/market/search/us_search/quote.html?ric={TICKER}.{EXCHANGE}` | Quote page |
| JP quote pattern | `/web/market/search/quote.html?ric={CODE}.T` | Quote page |
