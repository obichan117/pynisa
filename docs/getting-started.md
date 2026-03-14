# Getting Started

## Installation

```bash
pip install pynisa
```

Or with uv:

```bash
uv add pynisa
```

## Python API

### Fetch Rankings

```python
import pynisa

# Get default ranking (JP stocks, purchase amount)
result = pynisa.ranking("rakuten")
result.data    # pandas DataFrame
result.period  # "2026年2月1日～2026年2月28日"
result.updated # "2026年3月2日更新"

# US stocks from SBI
result = pynisa.ranking("sbi", "us_stock_buy", count=5)

# Specific category
result = pynisa.ranking("sbi", "fund_buy")
```

### List Sources and Categories

```python
pynisa.sources()
# ['rakuten', 'sbi']

pynisa.categories("rakuten")
# ['jp_stock_buy', 'jp_stock_balance', 'jp_etf_buy', ...]

pynisa.categories("sbi")
# ['stock_buy', 'stock_count', ..., 'us_stock_buy', 'cn_stock_buy', ...]
```

### RankingResult

`pynisa.ranking()` returns a `RankingResult` with:

- `data` — pandas DataFrame with columns: `rank`, `change`, `ticker`, `name`, `source`, `category`
- `period` — ranking period (e.g. `"2026年2月1日～2026年2月28日"`)
- `updated` — last update date (if available)

Some categories include extra columns (`sector` for US stocks, `market` for foreign ETFs).

## CLI

### Asset Type Commands

```bash
# JP stock rankings from all brokerages (side by side)
nisa

# US stock rankings from all brokerages
nisa us

# Chinese/HK stocks
nisa cn

# Investment trusts
nisa fund

# Filter to a specific brokerage
nisa us rakuten
nisa us sbi -n 5
```

### Per-Brokerage Commands

```bash
nisa rakuten                  # Default (JP stocks)
nisa sbi -c fund_buy -n 5    # Specific category
nisa rakuten -f csv           # Output as CSV
nisa sbi -f json              # Output as JSON
```

### Utility Commands

```bash
nisa sources              # List brokerages
nisa categories rakuten   # List categories for a brokerage
```
