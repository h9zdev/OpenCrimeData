from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@dataclass
class CrimeRecord:
    full_name: str
    middle_name: str
    last_name: str
    dob: str
    address: str
    country: str
    city: str
    place: str
    notes: str


LOCAL_RECORDS = [
    CrimeRecord(
        full_name="Arjun",
        middle_name="K",
        last_name="Singh",
        dob="1991-04-12",
        address="MG Road 14",
        country="India",
        city="Bengaluru",
        place="Commercial Street",
        notes="Cyber fraud investigation, non-conviction record",
    ),
    CrimeRecord(
        full_name="Sarah",
        middle_name="L",
        last_name="Miller",
        dob="1988-11-23",
        address="221B Baker Street",
        country="UK",
        city="London",
        place="Marylebone",
        notes="Open theft case report",
    ),
]


def _contains(value: str, needle: str) -> bool:
    return needle.lower() in (value or "").lower()


def search_local_records(params: dict[str, str]) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for record in LOCAL_RECORDS:
        record_data = asdict(record)
        match = True
        for key, value in params.items():
            if value and key in record_data and not _contains(str(record_data[key]), value):
                match = False
                break
        if match:
            filtered.append(record_data)
    return filtered


def safe_get_json(url: str, timeout: int = 8) -> dict[str, Any] | list[Any] | None:
    try:
        response = requests.get(url, timeout=timeout)
        if response.ok:
            return response.json()
    except requests.RequestException:
        return None
    return None


def external_search_links(query: str) -> dict[str, str]:
    q = requests.utils.quote(query)
    return {
        "Interpol Notices": f"https://www.interpol.int/How-we-work/Notices/View-Red-Notices#{q}",
        "FBI Most Wanted": f"https://www.fbi.gov/wanted?search_api_fulltext={q}",
        "UK Police Data": f"https://data.police.uk/data/",
        "India OpenGov Crime": "https://www.data.gov.in/catalogs?title=crime",
        "General Web Search": f"https://duckduckgo.com/?q={q}+crime+record",
    }


def fetch_uk_police_summary() -> dict[str, Any]:
    # Public endpoint for available forces, helpful as live-source check.
    data = safe_get_json("https://data.police.uk/api/forces")
    if isinstance(data, list):
        return {
            "source": "UK Police",
            "status": "ok",
            "total_forces": len(data),
            "sample": data[:5],
        }
    return {"source": "UK Police", "status": "unavailable"}


def fetch_interpol_summary() -> dict[str, Any]:
    # Interpol API endpoints may change; using notices v1 endpoint with broad query.
    data = safe_get_json("https://ws-public.interpol.int/notices/v1/red?resultPerPage=5&page=1")
    if isinstance(data, dict):
        total = data.get("total")
        embedded = data.get("_embedded", {}).get("notices", [])
        return {
            "source": "Interpol",
            "status": "ok",
            "total": total,
            "sample": embedded[:5],
        }
    return {"source": "Interpol", "status": "unavailable"}


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/sources")
def source_health() -> Any:
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sources": [fetch_uk_police_summary(), fetch_interpol_summary()],
    }
    return jsonify(payload)


@app.get("/api/search")
def search() -> Any:
    params = {
        "full_name": request.args.get("full_name", "").strip(),
        "middle_name": request.args.get("middle_name", "").strip(),
        "last_name": request.args.get("last_name", "").strip(),
        "dob": request.args.get("dob", "").strip(),
        "address": request.args.get("address", "").strip(),
        "country": request.args.get("country", "").strip(),
        "city": request.args.get("city", "").strip(),
        "place": request.args.get("place", "").strip(),
        "notes": request.args.get("notes", "").strip(),
    }
    query_blob = " ".join(value for value in params.values() if value)
    local_results = search_local_records(params)

    return jsonify(
        {
            "query": params,
            "local_results": local_results,
            "source_snapshots": [fetch_uk_police_summary(), fetch_interpol_summary()],
            "web_links": external_search_links(query_blob or "crime record person search"),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
