# Shortcut API Client

This Python library implements:

- A `ShortcutClient` class that supports methods for making GET, DELETE, PUT, and POST calls to Shortcut's v3 REST API
- `ShortcutClient.upload_files` for uploading files (linking them to Shortcut Stories is separate)
- Rate limiting that honors Shortcut's 200 requests/min limit

## Getting Started

1. [Create a Shortcut API token](https://app.shortcut.com/settings/account/api-tokens) and set it as `SHORTCUT_API_TOKEN` in your environment.
1. Clone this repository: `git clone https://github.com/semperos/scapi.git`
1. Install Python package and project manager [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. Run `uv run --with jupyter jupyter lab` to start a Jupyter server
1. Open the [GettingStarted.ipynb](GettingStarted.ipynb) Jupyter notebook and explore the examples

## Analysis

You can install `scapi[analysis]` to include optional dependencies for data analysis.

See the [Analysis.ipynb](Analysis.ipynb) Jupyter notebook for examples of data analysis and reporting using Shortcut data.

## Ideas

- Option to save responses as CSV, TSV, or Parquet files

## License

Copyright 2024 Daniel Gregoire

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
