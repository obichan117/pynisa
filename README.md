# pynisa

[![PyPI version](https://badge.fury.io/py/pynisa.svg)](https://badge.fury.io/py/pynisa)
[![Python versions](https://img.shields.io/pypi/pyversions/pynisa.svg)](https://pypi.org/project/pynisa/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://obichan117.github.io/pynisa/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/obichan117/pynisa/blob/main/examples/quickstart.ipynb)

Fetch NISA account trading rankings from major Japanese securities brokerages.

> **Note on ranking frequency:** Rakuten rankings are updated **monthly** (around the 2nd of each month), while SBI rankings are updated **weekly**. This means SBI data changes every week, but Rakuten data only changes once a month. Historical queries reflect these different update cycles.

## Installation

```bash
pip install pynisa
```

## Quick Start

### Python API

```python
import pynisa

# Fetch top 10 NISA stock ranking from Rakuten
result = pynisa.ranking("rakuten")
result.data    # pandas DataFrame
result.period  # "2026年2月1日～2026年2月28日"

# US stocks from SBI
result = pynisa.ranking("sbi", "us_stock_buy", count=5)

# Historical ranking (requires database)
result = pynisa.ranking("sbi", date="2026-03-07")

# Force live fetch (skip database)
result = pynisa.ranking("rakuten", live=True)

# Rank history for a ticker
result = pynisa.history("rakuten", "7974")

# List available dates
pynisa.dates("sbi")  # ["2026-03-14", "2026-03-07", ...]

# Sync database manually
pynisa.sync(force=True)
```

### CLI

```bash
# JP stock rankings from all brokerages (side by side)
nisa
```

> **楽天** (2026年2月1日～2026年2月28日)
>
> | rank | change | ticker | name |
> |-----:|--------|--------|------|
> | 1 | ↑ | 7974 | 任天堂 |
> | 2 | ↑ | 9432 | NTT |
> | 3 | ↓ | 8306 | 三菱UFJ |
> | 4 | ↑ | 7011 | 三菱重工業 |
> | 5 | ↑ | 5016 | JX金属 |
>
> **SBI** (2026/3/9 〜 2026/3/13)
>
> | rank | change | ticker | name |
> |-----:|--------|--------|------|
> | 1 | → | 8306 | 三菱UFJ |
> | 2 | → | 7267 | 本田技研工業 |
> | 3 | | 9984 | ソフトバンク |
> | 4 | ↑ | 5401 | 日本製鉄 |
> | 5 | ↑ | 7011 | 三菱重工業 |

```bash
# US stock rankings from all brokerages
nisa us
```

> **楽天** (2026年2月1日～2026年2月28日)
>
> | rank | change | ticker | name |
> |-----:|--------|--------|------|
> | 1 | ↑ | MSFT | マイクロソフト |
> | 2 | ↓ | NVDA | エヌビディア |
> | 3 | → | SOFI | ソーファイ |
> | 4 | ↑ | PLTR | パランティア |
> | 5 | ↓ | MU | マイクロン テクノロジー |
>
> **SBI** (2026/3/9 〜 2026/3/13)
>
> | rank | change | ticker | name |
> |-----:|--------|--------|------|
> | 1 | → | NVDA | エヌビディア |
> | 2 | ↑ | MSFT | マイクロソフト |
> | 3 | ↑ | TSLA | テスラ |
> | 4 | ↓ | PLTR | パランティア |
> | 5 | ↑ | IONQ | IonQ Inc |

```bash
# Single brokerage
nisa rakuten
nisa us sbi -n 5

# Output as CSV or JSON
nisa rakuten -f csv
nisa us rakuten -f json

# Historical rankings
nisa rakuten --date 2026-02-28       # specific date
nisa rakuten --last 4                # last 4 weeks, latest first
nisa us --last 4                     # works with asset commands
nisa --last 4                        # all sources, last 4 weeks

# Force live fetch (skip database)
nisa rakuten --live

# Rank history for a ticker
nisa history rakuten 7974
nisa history sbi 8306 -c stock_buy

# Database management
nisa sync                            # download/update database
nisa sync --force                    # force re-download
nisa dates rakuten                   # list available dates
nisa dates sbi -c stock_buy
```

## Supported Brokerages

| Brokerage | Asset Types | Update Frequency |
|-----------|------------|-----------------|
| Rakuten Securities (楽天) | JP/US/CN/ASEAN stocks, JP/Foreign ETFs | **Monthly** (~2nd of month) |
| SBI Securities | JP/US/CN stocks, US/CN ETFs, Funds | **Weekly** |

## Database

pynisa maintains a SQLite database of historical rankings, automatically downloaded from GitHub Releases on first use. The database is updated by GitHub Actions:

- **Every Monday** — captures SBI's weekly update
- **3rd of each month** — captures Rakuten's monthly update

The database is stored at `~/.cache/pynisa/nisa.db` and auto-synced when stale (> 1 day).

## License

MIT
