# OpenCrimeData (Flask)

Open-source Flask web app for searching crime-related records by:
- Full name, middle name, last name
- DOB
- Address
- Country, city, place
- Other keyword notes

Includes:
- Local demo records search
- Open source/live connectors (UK Police + Interpol summary)
- Web search links for Interpol, FBI, UK police data, India open datasets, and DuckDuckGo
- Cyberpunk neon UI styling

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## API

- `GET /api/search` with query params:
  - `full_name`, `middle_name`, `last_name`, `dob`, `address`, `country`, `city`, `place`, `notes`
- `GET /api/sources` for current source health snapshots.

## Notes

- Some external provider APIs can throttle or change without notice; app degrades gracefully to `unavailable`.
- FBI public search is linked as web search (no API key required for this app baseline).
