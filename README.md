# pynisa

[![PyPI version](https://badge.fury.io/py/pynisa.svg)](https://badge.fury.io/py/pynisa)
[![Python versions](https://img.shields.io/pypi/pyversions/pynisa.svg)](https://pypi.org/project/pynisa/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://obichan117.github.io/pynisa/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/obichan117/pynisa/blob/main/examples/quickstart.ipynb)

Fetch NISA account trading rankings from major Japanese securities brokerages.

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
```

### CLI

```bash
# JP stock rankings from all brokerages (side by side)
nisa

# US stock rankings from all brokerages
nisa us

# Single brokerage
nisa rakuten
nisa us sbi -n 5

# Output as CSV or JSON
nisa rakuten -f csv
nisa us rakuten -f json
```

## Supported Brokerages

| Brokerage | Asset Types | Update Frequency |
|-----------|------------|-----------------|
| Rakuten Securities | JP/US/CN/ASEAN stocks, JP/Foreign ETFs | Monthly |
| SBI Securities | JP/US/CN stocks, US/CN ETFs, Funds | Weekly |

## License

MIT
