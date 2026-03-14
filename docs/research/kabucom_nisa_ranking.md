# Mitsubishi UFJ eSmart Securities (kabu.com) NISA Ranking - Research

Last updated: 2026-03-14

## Summary

Mitsubishi UFJ eSmart Securities (formerly au Kabucom Securities / auカブコム証券) provides a **NISA purchase ranking page** at `kabu.com`.
However, unlike Rakuten/SBI, **there is no publicly accessible hidden API (CSV/JSON endpoint)**.
The ranking data appears to be **rendered via client-side JavaScript**, making it harder to extract programmatically.

The company was renamed from "auカブコム証券" to "三菱UFJ eスマート証券" but the website remains at `kabu.com`.

---

## 1. Public URLs

### NISA Ranking Pages

| Page | URL | Status |
|------|-----|--------|
| NISA Products (General NISA ranking) | `https://kabu.com/item/nisa/nisa/ranking.html` | Page exists but currently redirects to general NISA info page. Google index still describes ranking data. |
| Junior NISA Products (ranking) | `https://kabu.com/item/nisa/jnisa/ranking.html` | Same - redirects to NISA marketing page |
| Original Ranking (all products) | `https://kabu.com/investment/market/info/ranking.html` | **Requires authentication** (login required) |
| Market Ranking (general) | `https://kabu.com/investment/market/ranking.html` | General market info page |

### Fund Information Portal

| Page | URL | Status |
|------|-----|--------|
| Fund Search | `https://fundinfo.kabu.co.jp/fund-search` | Public, Next.js SSR app |
| Fund Snapshot | `https://fundinfo.kabu.co.jp/fund-details-snapshot?fundCode={CODE}` | Public, per-fund detail |

### NISA Product Lists (PDFs)

| Document | URL |
|----------|-----|
| Growth investment eligible funds (latest) | `https://kabu.com/item/nisa/nisa/img/NISA_growth_productslist_20260228.pdf` |
| Accumulation investment products | `https://kabu.com/item/nisa/tsumitate/item.html` |

---

## 2. Hidden API Investigation

### NISA Ranking Page (`ranking.html`)

- The URL `https://kabu.com/item/nisa/nisa/ranking.html` is indexed by Google with descriptions mentioning:
  - Three categories: **Stocks (株式)**, **Petit Stocks/プチ株 (fractional shares)**, **Investment Trusts (投資信託)**
  - TOP10 ranking per category
  - Data sorted by purchase amount (買付代金が多い順)
  - "Share" field = percentage of total purchase amount
- **Current state**: The page now serves the general NISA marketing page (same content as `/item/nisa/default.html`). The ranking data may have been removed or moved behind authentication.
- **No JavaScript API calls detected** in the served HTML. The page is static marketing content.

### Fund Search Portal (`fundinfo.kabu.co.jp`)

- Built with **Next.js** (server-side rendered)
- Build ID: `0XV6bmZVSdJqjMGuwQnFp` (changes on deployment)
- Has a sort option: `executionWeekRank` = "販売金額ランキング順位（週間）" (weekly sales ranking)
- URL pattern: `https://fundinfo.kabu.co.jp/fund-search?sortKey=executionWeekRank&sortOrder=asc&page=1`
- **No public API endpoint found**. Data is loaded via client-side JavaScript bundles; backend API URLs are not exposed in the HTML source.
- API endpoint guesses (`/api/funds`, `/api/fund-search`, `/bff/fund-search`, `/api/v1/funds`) all return 404.

### Original Ranking Page (authentication-gated)

- `https://kabu.com/investment/market/info/ranking.html` has extensive ranking data but **requires login**.
- Categories include: stocks (cash), margin trading, petit stocks, investment trusts (by sales amount, transaction count, accumulation settings, returns, distribution yields, net asset increases).
- Page states: "ログイン後ページよりご確認いただけます" (viewable after login).

### kabuStation API (Desktop Application API)

- **Not a public web API** - runs on `localhost:18080` within the kabuStation desktop application.
- Has a `/ranking` endpoint with 15 ranking types (price gain/loss, volume, margin, etc.).
- **Does NOT support NISA-specific rankings**.
- Requires kabuStation desktop app + account authentication.
- Documentation: `https://kabucom.github.io/kabusapi/reference/index.html`
- OpenAPI spec: `https://github.com/kabucom/kabusapi/blob/master/reference/kabu_STATION_API.yaml`

### MUFG Investment Trust Information API

- MUFG group offers a public API at `https://www.am.mufg.jp/tool/webapi/`
- Provides investment trust data from **Mitsubishi UFJ Asset Management** specifically.
- Requires agreement to terms of use. Specification document available (PDF).
- **Not specific to kabu.com's NISA rankings**, but may provide fund metadata.

---

## 3. Data Fields (from Google Index / Historical)

Based on Google's indexed descriptions of the ranking page, the historical data structure was:

### Stocks (株式) - TOP10

| Field | Japanese | Description |
|-------|----------|-------------|
| Rank | 順位 | 1-10 |
| Stock name | 銘柄名 | Company name |
| Share | シェア | % of total NISA purchase amount |

### Petit Stocks (プチ株) - TOP10

| Field | Japanese | Description |
|-------|----------|-------------|
| Rank | 順位 | 1-10 |
| Stock name | 銘柄名 | Company name |
| Share | シェア | % of total NISA purchase amount |

### Investment Trusts (投資信託) - TOP10

| Field | Japanese | Description |
|-------|----------|-------------|
| Rank | 順位 | 1-10 |
| Fund name | ファンド名 | Fund name |
| Share | シェア | % of total NISA purchase amount |

**Note**: Ticker codes (銘柄コード) were likely present but not confirmed from cached descriptions.

### Fund Search Portal Fields (fundinfo.kabu.co.jp)

| Field | Japanese | Description |
|-------|----------|-------------|
| Fund name | ファンド名/愛称 | Name and nickname |
| NAV | 基準価額 | Net asset value per unit |
| Net assets | 純資産 | Total net assets |
| Total return | トータルリターン | 1-year performance |
| Trust fee | 信託報酬 | Management fee |
| Distribution yield | 分配金利回り | |
| Standard deviation | 標準偏差 | Risk measure |
| Sharpe ratio | シャープレシオ | Risk-adjusted return |
| Weekly sales rank | 販売金額ランキング順位（週間） | Sortable |
| Fund classification | ファンド分類 | Category |
| Management company | 運用会社 | |

---

## 4. Authentication Requirements

| Resource | Auth Required? |
|----------|---------------|
| NISA ranking page (ranking.html) | No (public page) but ranking data no longer displayed |
| Original ranking page (info/ranking.html) | **Yes** - login required |
| Fund search portal (fundinfo.kabu.co.jp) | No - publicly accessible |
| Fund snapshot pages | No - publicly accessible |
| NISA product list PDFs | No - publicly accessible |
| kabuStation API | **Yes** - requires desktop app + account |
| s20.kabu.co.jp (trading platform) | **Yes** - redirects to login |
| MUFG AM Web API | Terms agreement required |

---

## 5. Recommended Approach

### Option A: Fund Search Portal (Best Available)

**URL**: `https://fundinfo.kabu.co.jp/fund-search?sortKey=executionWeekRank&sortOrder=asc`

- Publicly accessible, no authentication
- Has weekly sales amount ranking sort
- Rich data fields (NAV, fees, returns, Sharpe ratio)
- **Challenge**: Next.js client-side rendered. Requires browser automation (Playwright/Selenium) to extract data, as the backend API is not publicly exposed.

### Option B: HTML Scraping of NISA Page (If Data Returns)

**URL**: `https://kabu.com/item/nisa/nisa/ranking.html`

- Currently not showing ranking data (serves marketing page)
- Historical data had TOP10 for stocks, petit stocks, and investment trusts
- May need to be re-checked periodically as the site undergoes restructuring

### Option C: NISA Product List PDFs

**URL**: `https://kabu.com/item/nisa/nisa/img/NISA_growth_productslist_{YYYYMMDD}.pdf`

- Static list of all eligible funds (not a ranking)
- Fields: Fund code (投信協会ファンドコード), Fund name, Management company
- Updated periodically (found dates: 20250530, 20251031, 20260228)
- Good for building a universe of eligible funds, but no ranking/popularity data

### Verdict

**kabu.com has significantly less public ranking data than Rakuten or SBI.** The NISA ranking data appears to have been moved behind authentication or removed from the public site. The `fundinfo.kabu.co.jp` fund search portal is the best remaining public data source, but requires browser automation due to client-side rendering.

---

## 6. Key Subdomains

| Subdomain | Purpose |
|-----------|---------|
| `kabu.com` | Main website (public content) |
| `fundinfo.kabu.co.jp` | Fund information portal (Next.js, public) |
| `s10.kabu.co.jp` | Account application system |
| `s20.kabu.co.jp` | Trading platform (auth required) |
| `mauth-sso.kabu.co.jp` | SSO login system |
| `acs.kabu.co.jp` | Account opening system |
| `d10-spsite.kabu.co.jp` | Mobile login |
| `faq.kabu.com` | FAQ system (Salesforce-based) |
| `kabucom.github.io` | API documentation (kabuStation) |

---

## 7. Related APIs

| API | Type | NISA Rankings? | Auth? |
|-----|------|----------------|-------|
| kabuStation API (`localhost:18080/kabusapi/ranking`) | Desktop REST API | No NISA-specific rankings | Yes (account + desktop app) |
| MUFG AM Web API (`am.mufg.jp/tool/webapi/`) | Public Web API | No (fund metadata only) | Terms agreement |
| fundinfo.kabu.co.jp | Web portal | Weekly sales ranking (sort) | No (but needs browser automation) |
