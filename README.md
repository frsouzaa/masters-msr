# masters-msr

This repository contains the data-collection and analysis code for a master's
research project on repository lifecycle. For each GitHub repository, the
pipeline collects activity data and Google Trends interest, aggregates the
observations by month, calculates exponential moving averages and statistical
correlations, and writes CSV data and plots.

## Requirements

- Node.js 24.20 and npm
- Python 3.12.3
- A GitHub personal access token for the GitHub Rest and GraphQL API with public_repo permission

## Configure the local environment

Run these commands from the repository root:

```bash
# Create and activate the Python virtual environment.
python3 -m venv python/env
source python/env/bin/activate
python -m pip install --upgrade pip
python -m pip install -r python/requirements.txt

# Install the Node.js dependencies.
npm --prefix js ci
```

Create `js/.env` and add your GitHub token:

```dotenv
GH_TOKEN=your_github_token
```

`js/.env` is ignored by Git. Do not commit or share a real token. The Node
script loads this file when it starts.

## Run the project

Run from the repository root so that the scripts can find their relative input
and output paths.

### Analyze one repository

```bash
./run.sh https://github.com/owner/repository
```

For example:

```bash
./run.sh https://github.com/pytorch/pytorch
```

The script first runs the Node.js collector, then runs the Python analysis for
the same repository. It uses the virtual environment at `python/env`, so create
and install that environment before using this command.

### Analyze the configured repository list

Run without a URL:

```bash
./run.sh
```

This reads one GitHub repository URL per line from `repos.txt` and processes
each URL in sequence. Add or remove entries in that file to choose the batch.

`repos.txt` example:

```text
https://github.com/gin-gonic/gin
https://github.com/spring-projects/spring-boot
https://github.com/phpmailer/phpmailer
```

### Run either stage directly

With the Python virtual environment activated, the stages can also be run
separately:

```bash
npm --prefix js start https://github.com/owner/repository
python python/app.py https://github.com/owner/repository
```

The Python stage expects the Node collector's CSV files to exist in
`outputs/<repository-name>/`. Run the collector first when analyzing a
repository that does not already have collected data.

## Results

Each repository's files are written to `outputs/<repository-name>/`. The NPM
collector creates daily CSVs for stars, forks, issues, and pull requests. The
Python stage also collects commit history and Google Trends interest, then
creates monthly feature CSVs, EMA data, per-feature SVG plots, merged feature
data, statistical test and correlation CSVs, a correlation plot, and a summary
of feature trends.

The `outputs_correlations/` directory contains additional SVG correlation
plots. Generated output files are local data and are not tracked by Git.

To remove many derived CSV and plot files, run:

```bash
./clear.sh
```

This script removes matching correlation, EMA, final, merged, Anderson-Darling,
and plot files under `outputs/`. It does not remove the raw `per_day_*.csv`
collector data.

## Other scripts and data

- `python/msr27.py` performs a cross-repository summary using data already
  present under `outputs/`.
- `python/seart_analyzer.py` analyzes the root-level `results.json` file.

The two analysis scripts above are separate from the normal `run.sh` pipeline.
They require their input data files to be available in the expected locations.

## Troubleshooting

- **GitHub API authentication or rate-limit errors:** check that `js/.env`
  exists, that it contains `GH_TOKEN` with a valid token, and that the token
  can access the repository.
- **Python module import errors:** activate `python/env` and install
  `python/requirements.txt` in that environment.
- **Missing CSV or output errors:** run the collector before the Python stage,
  use a GitHub repository URL, and launch commands from the repository root.
- **Google Trends failures:** the interest data is fetched from Google Trends
  during Python processing and therefore requires internet access; retry later
  if the service is temporarily unavailable.
