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
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

2. Create an `.env` file (or set environment variables) with the following values:

- `GITHUB_TOKEN` (optional — required to create issues)
- `GITHUB_USERNAME` (optional — default: pkalyankumar1010)
- `GITHUB_REPO` (optional — default: upper_circuit_finder)

You can copy `.env.example` to start.

Running locally

```bash
python upper_circuit_finder_nse.py
```

GitHub Actions

This repo already includes a workflow at `.github/workflows/upper_circuit_finder.yml` that runs at 20:00 IST on weekdays and invokes `upper_circuit_finder_nse.py`.

If you want issues to be created, add a `GITHUB_TOKEN` (or personal access token) to the repository secrets.

Contributing
- Please read `CONTRIBUTING.md` for guidance on opening issues and pull requests.

License

This project is available under the MIT license — see `LICENSE`.

Contact

Open an issue or PR on this repository to report bugs or request features.

Enjoy! 🚀
