# cta-reporting

Small Python helper to pull CTA train positions and normalize them into a DataFrame.

## Setup
- Python 3.10+
- Create a virtualenv: `python -m venv .venv && source .venv/bin/activate`
- Install in editable mode: `pip install -e .`
- Add your CTA API key to `cta_api_key.txt` (file is gitignored).

## Usage
- Fetch default routes (Red/Blue/Brown/Green/Orange/Pink/Purple/Yellow):  
  `python -m cta_reporting`
- Override routes:  
  `python -m cta_reporting --routes red,blue`
- Use a different key file:  
  `python -m cta_reporting --key-file /path/to/key.txt`

The helper returns a pandas DataFrame; the CLI prints the first few rows. The same entry point is available via `python cta_testing.py` for convenience.
