from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
from flask import Flask, jsonify, render_template, request
from duckduckgo_search import DDGS

app = Flask(__name__)

# Constants for APIs
FBI_API_URL = "https://api.fbi.gov/wanted/v1/list"
INTERPOL_API_URL = "https://ws-public.interpol.int/notices/v1/red"

def safe_get_json(url: str, params: dict[str, Any] | None = None, timeout: int = 10) -> dict[str, Any] | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def fetch_fbi_wanted(query: str) -> list[dict[str, Any]]:
    params = {"keyword": query}
    data = safe_get_json(FBI_API_URL, params=params)
    results = []
    if data and "items" in data:
        for item in data["items"]:
            results.append({
                "source": "FBI",
                "title": item.get("title"),
                "description": item.get("description"),
                "image": item.get("images", [{}])[0].get("large") if item.get("images") else None,
                "url": item.get("url"),
                "details": item.get("details"),
                "reward": item.get("reward_text")
            })
    return results

def fetch_interpol_notices(query: str) -> list[dict[str, Any]]:
    # Interpol search is usually by name/forename, so we try a simple search
    params = {"name": query, "resultPerPage": 5}
    data = safe_get_json(INTERPOL_API_URL, params=params)
    results = []
    if data and "_embedded" in data:
        notices = data["_embedded"].get("notices", [])
        for notice in notices:
            results.append({
                "source": "Interpol",
                "title": f"{notice.get('forename', '')} {notice.get('name', '')}".strip(),
                "description": f"Date of birth: {notice.get('date_of_birth', 'N/A')}",
                "image": notice.get("_links", {}).get("thumbnail", {}).get("href"),
                "url": f"https://www.interpol.int/en/How-we-work/Notices/View-Red-Notices#{notice.get('entity_id')}",
            })
    return results

def fetch_web_results(query: str) -> list[dict[str, Any]]:
    results = []
    try:
        with DDGS() as ddgs:
            # Search for crime records specifically
            search_query = f"{query} crime record"
            ddgs_results = ddgs.text(search_query, max_results=8)
            for r in ddgs_results:
                results.append({
                    "source": "Web Search",
                    "title": r.get("title"),
                    "description": r.get("body"),
                    "url": r.get("href"),
                    "image": None
                })
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": [], "message": "Please provide a search query."})

    fbi_results = fetch_fbi_wanted(query)
    web_results = fetch_web_results(query)
    # Interpol often returns 403 or empty if query is not specific enough, but we try.
    interpol_results = fetch_interpol_notices(query)

    combined_results = fbi_results + interpol_results + web_results

    return jsonify({
        "query": query,
        "results": combined_results,
        "count": len(combined_results)
    })

@app.route("/api/sources")
def sources():
    # Keep it simple, just return what's available
    return jsonify({
        "sources": [
            {"name": "FBI Wanted", "status": "active"},
            {"name": "Interpol Red Notices", "status": "active"},
            {"name": "DuckDuckGo Web Search", "status": "active"}
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
