# upper_circuit_finder

![CI](https://github.com/pkalyankumar1010/upper_circuit_finder/actions/workflows/upper_circuit_finder.yml/badge.svg)

Short, fast NSE-optimized scanner that finds stocks hitting the upper circuit on the NSE and creates a GitHub issue with the results.

Features
- Uses NSE's price band hitter API to only check stocks that hit circuit (very fast)
- Filters out stocks that hit upper/lower circuit in the last 14 days
- Creates a GitHub issue with results (optional; controlled by `GITHUB_TOKEN`)

Quickstart
1. Create a Python virtual environment and install dependencies:

```bash
# upper_circuit_finder

![CI](https://github.com/pkalyankumar1010/upper_circuit_finder/actions/workflows/upper_circuit_finder.yml/badge.svg)

A fast, NSE-optimized scanner that finds Indian stocks hitting the upper circuit using NSE's "price band hitter" API. The script filters out stocks that hit an upper or lower circuit in the last 14 days, saves results to a CSV, and can optionally create a GitHub issue with the findings.

**Highlights**
- Uses NSE's price band hitter API to check only stocks that actually hit circuit (very fast)
- Filters out stocks that hit circuits in the last 14 days to surface fresh momentum
- Saves results to `csv/upper_circuit_stocks_<YYYYMMDD>.csv`
- Optional GitHub issue creation when `GITHUB_TOKEN` is provided

## Prerequisites
- Python 3.10+ recommended
- `requirements.txt` includes all Python dependencies (e.g., `yfinance`, `pandas`, `PyGithub`).

## Installation
1. Create and activate a virtual environment:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd)
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration (environment variables)
Create an `.env` file in the repo root or set environment variables directly. Supported variables:

- `GITHUB_TOKEN` — (optional) Personal access token or Actions token to allow automatic issue creation
- `GITHUB_USERNAME` — (optional) GitHub user/organization for the repo (default: `pkalyankumar1010`)
- `GITHUB_REPO` — (optional) Repository name (default: `upper_circuit_finder`)

If you plan to let the script commit CSVs locally, ensure `git` is available and configured. In CI (GitHub Actions), commits are handled by the workflow instead of the script.

## Usage
Run the NSE-optimized scanner:

```bash
python upper_circuit_finder_nse.py
```

What the script does:
- Visits NSE to obtain the list of price-band hitters (upper circuit candidates)
- Filters to stocks within 1% of their circuit limit
- Checks the last 14 trading days via Yahoo Finance to exclude symbols that already hit a circuit
- Saves qualifying results to `csv/upper_circuit_stocks_<YYYYMMDD>.csv`
- Optionally creates a GitHub issue summarizing the results when `GITHUB_TOKEN` is set

## Output
- CSV files are saved under the `csv/` directory with the date in filename.
- The script prints a table to the console and logs status messages during the run.

## GitHub Actions
This repository includes a workflow that runs the scanner on a schedule (see `.github/workflows/upper_circuit_finder.yml`). To enable automatic issue creation from Actions, add a repository secret named `GITHUB_TOKEN` (or a personal access token with `repo` scope).

## Troubleshooting & Notes
- NSE may block automated requests (403/429). Options if you encounter blocking:
	- Use a proxy or VPN
	- Run from a different IP (avoid some cloud CI providers)
	- Use `curl_cffi` (optional dependency) for better browser impersonation — the script falls back to `requests` if `curl_cffi` isn't available
- If you see compressed or non-JSON responses, the script attempts decompression (brotli/gzip) and will print helpful debug information.
- On Windows, the script configures stdout encoding for proper Unicode output.

## Contributing
- Read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

Enjoy! 🚀
