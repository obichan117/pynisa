# pynisa

Fetch NISA account trading rankings from major Japanese securities brokerages.

## Features

- **Python API** — Get ranking data as pandas DataFrames with period metadata
- **CLI** — View rankings in beautiful terminal tables, side by side across brokerages
- **Multiple Brokerages** — Rakuten Securities (12 categories), SBI Securities (11 categories)
- **Asset Type Commands** — `nisa`, `nisa us`, `nisa cn`, `nisa fund` for quick access
- **Multiple Output Formats** — Table, CSV, JSON

## Quick Start

```bash
pip install pynisa
```

=== "Python"

    ```python
    import pynisa

    result = pynisa.ranking("rakuten")
    result.data    # pandas DataFrame
    result.period  # "2026年2月1日～2026年2月28日"
    ```

=== "CLI"

    ```bash
    nisa            # JP stocks from all brokerages
    nisa us         # US stocks from all brokerages
    nisa rakuten    # Rakuten JP stocks
    nisa us sbi     # SBI US stocks
    ```

## Supported Brokerages

| Brokerage | Asset Types | Update Frequency |
|-----------|------------|-----------------|
| Rakuten Securities | JP/US/CN/ASEAN stocks, JP/Foreign ETFs | Monthly |
| SBI Securities | JP/US/CN stocks, US/CN ETFs, Funds | Weekly |
