# Python API Reference

## Functions

### `pynisa.ranking(source, category=None, *, count=10)`

Fetch NISA ranking from a brokerage.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | `str` | required | Brokerage name (`"rakuten"`, `"sbi"`) |
| `category` | `str \| None` | `None` | Ranking category. If None, uses default. |
| `count` | `int` | `10` | Maximum number of results |

**Returns:** `RankingResult`

### `pynisa.categories(source)`

List available ranking categories for a source.

**Returns:** `list[str]`

### `pynisa.sources()`

List available brokerage source names.

**Returns:** `list[str]`

## RankingResult

Returned by `pynisa.ranking()`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `data` | `pd.DataFrame` | Ranking data |
| `period` | `str` | Ranking period (e.g. `"2026年2月1日～2026年2月28日"`) |
| `updated` | `str` | Last update date (e.g. `"2026年3月2日更新"`) |

### DataFrame Columns

| Column | Type | Description |
|--------|------|-------------|
| `rank` | `Int64` | Ranking position (1-10) |
| `change` | `str` | Rank change from previous period (`↑` up, `↓` down, `→` same, `NEW`) |
| `ticker` | `str` | Stock/ETF ticker code |
| `name` | `str` | Stock/fund name (Japanese) |
| `source` | `str` | Brokerage name |
| `category` | `str` | Category used |

Extra columns by category:

- `sector` — US, Chinese, ASEAN stocks
- `market` — Foreign ETFs (Rakuten)

## Categories Reference

### Rakuten Securities

| Category | Description |
|----------|-------------|
| `jp_stock_buy` | Domestic stocks - purchase amount (default) |
| `jp_stock_balance` | Domestic stocks - balance |
| `jp_etf_buy` | Domestic ETF/ETN - purchase amount |
| `jp_etf_balance` | Domestic ETF/ETN - balance |
| `us_stock_buy` | US stocks - purchase amount |
| `us_stock_balance` | US stocks - balance |
| `cn_stock_buy` | Chinese stocks - purchase amount |
| `cn_stock_balance` | Chinese stocks - balance |
| `asean_stock_buy` | ASEAN stocks - purchase amount |
| `asean_stock_balance` | ASEAN stocks - balance |
| `foreign_etf_buy` | Foreign ETFs - purchase amount |
| `foreign_etf_balance` | Foreign ETFs - balance |

### SBI Securities

| Category | Description |
|----------|-------------|
| `stock_buy` | Domestic stocks - purchase amount (default) |
| `stock_count` | Domestic stocks - purchase count |
| `stock_balance` | Domestic stocks - balance |
| `fund_buy` | Investment trusts - purchase amount |
| `fund_count` | Investment trusts - purchase count |
| `fund_buy_count` | Investment trusts - buy count |
| `fund_balance` | Investment trusts - balance |
| `us_stock_buy` | US stocks - purchase amount |
| `us_etf_buy` | US ETFs - purchase amount |
| `cn_stock_buy` | Chinese/HK stocks - purchase amount |
| `cn_etf_buy` | Chinese/HK ETFs - purchase amount |
