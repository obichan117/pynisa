# CLI Reference

## Asset Type Commands

### `nisa`

Show JP stock rankings from all brokerages side by side.

```bash
nisa
```

### `nisa us`

Show US stock rankings from all brokerages.

```bash
nisa us [SOURCE] [OPTIONS]
```

| Argument | Description |
|----------|-------------|
| `SOURCE` | Optional. Brokerage name to show only that source. |

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--count` | `-n` | `10` | Number of results |
| `--format` | `-f` | `table` | Output format: `table`, `csv`, `json` |

```bash
nisa us                    # All brokerages side by side
nisa us rakuten            # Rakuten only
nisa us sbi -n 5           # SBI top 5
nisa us rakuten -f json    # JSON output
```

### `nisa cn`

Chinese/HK stock rankings. Same options as `nisa us`.

### `nisa asean`

ASEAN stock rankings (Rakuten only). Same options as `nisa us`.

### `nisa fund`

Investment trust rankings. Same options as `nisa us`.

### `nisa jp_etf`

JP ETF/ETN rankings (Rakuten only). Same options as `nisa us`.

### `nisa foreign_etf`

Foreign ETF rankings (Rakuten only). Same options as `nisa us`.

## Per-Brokerage Commands

### `nisa rakuten`

Fetch ranking from Rakuten Securities.

```bash
nisa rakuten [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--category` | `-c` | `jp_stock_buy` | Ranking category |
| `--count` | `-n` | `10` | Number of results |
| `--format` | `-f` | `table` | Output format: `table`, `csv`, `json` |

### `nisa sbi`

Fetch ranking from SBI Securities. Same options as `nisa rakuten` (default category: `stock_buy`).

## Utility Commands

### `nisa sources`

List available brokerage sources.

### `nisa categories SOURCE`

List available ranking categories for a brokerage.

```bash
nisa categories rakuten
nisa categories sbi
```
