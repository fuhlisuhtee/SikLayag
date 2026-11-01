import json
import os
import socket
import threading
import time
from collections import OrderedDict
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from seeky import match_question


load_dotenv()

app = Flask(__name__)

SEARCH_RESULT_LIMIT = 5
SEARCH_CACHE_TTL_SECONDS = 300
SEARCH_CACHE_MAX_ENTRIES = 256
_search_cache = OrderedDict()
_search_cache_lock = threading.Lock()


class SemanticScholarError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def search_papers(query, start_year=None, end_year=None):
    params = {
        "query": query,
        "limit": SEARCH_RESULT_LIMIT,
        "fields": "paperId,title,authors,year,url",
    }
    if start_year is not None or end_year is not None:
        first_year = start_year if start_year is not None else 1800
        last_year = end_year if end_year is not None else date.today().year
        params["year"] = f"{first_year}-{last_year}"
    encoded_params = urlencode(params)

    headers = {"User-Agent": "SikLayag/1.0"}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    req = Request(
        f"https://api.semanticscholar.org/graph/v1/paper/search?{encoded_params}",
        headers=headers,
    )

    try:
        with urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 429:
            raise SemanticScholarError(
                "Masyadong maraming paghahanap. Pakisubukan muli mamaya.", 503
            ) from error
        raise SemanticScholarError(
            "Hindi makuha ang mga resulta mula sa Semantic Scholar.", 502
        ) from error
    except (TimeoutError, socket.timeout) as error:
        raise SemanticScholarError(
            "Nag-time out ang Semantic Scholar. Pakisubukan muli.", 504
        ) from error
    except URLError as error:
        raise SemanticScholarError(
            "Hindi maabot ang Semantic Scholar. Pakisubukan muli mamaya.", 502
        ) from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SemanticScholarError(
            "Hindi mabasa ang tugon mula sa Semantic Scholar.", 502
        ) from error

    if not isinstance(payload, dict):
        raise SemanticScholarError(
            "Hindi inaasahan ang tugon mula sa Semantic Scholar.", 502
        )

    papers = payload.get("data")
    if not isinstance(papers, list):
        raise SemanticScholarError(
            "Hindi inaasahan ang tugon mula sa Semantic Scholar.", 502
        )

    results = []
    for paper in papers:
        if not isinstance(paper, dict):
            continue
        authors = paper.get("authors")
        paper_url = _http_url(paper.get("url"))
        paper_id = paper.get("paperId")
        if paper_url is None and isinstance(paper_id, str) and paper_id:
            paper_url = f"https://www.semanticscholar.org/paper/{quote(paper_id, safe='')}"
        results.append(
            {
                "title": paper.get("title") or "Walang pamagat",
                "authors": [
                    author["name"]
                    for author in authors or []
                    if isinstance(author, dict) and author.get("name")
                ],
                "year": paper.get("year"),
                "url": paper_url,
            }
        )
        if len(results) == SEARCH_RESULT_LIMIT:
            break

    return {"total": payload.get("total", len(results)), "results": results}


def _cached_search(query, start_year, end_year):
    key = (query.casefold(), start_year, end_year)
    now = time.monotonic()
    with _search_cache_lock:
        cached = _search_cache.get(key)
        if cached and now - cached[0] < SEARCH_CACHE_TTL_SECONDS:
            _search_cache.move_to_end(key)
            return cached[1]
        if cached:
            del _search_cache[key]

    result = search_papers(query, start_year, end_year)
    with _search_cache_lock:
        _search_cache[key] = (time.monotonic(), result)
        _search_cache.move_to_end(key)
        while len(_search_cache) > SEARCH_CACHE_MAX_ENTRIES:
            _search_cache.popitem(last=False)
    return result


def _parse_year(value, field_name):
    if value is None or value == "":
        return None
    try:
        year = int(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be a four-digit year.") from error
    if year < 1800 or year > date.today().year:
        raise ValueError(f"{field_name} must be between 1800 and {date.today().year}.")
    return year


def _http_url(value):
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return value


@app.get("/")
def home():
    return render_template("Siklayag.html", current_year=date.today().year)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Maglagay ng paksa o mga keyword."}), 400
    if len(query) > 300:
        return jsonify({"error": "Hanggang 300 character lamang ang paksa."}), 400

    try:
        start_year = _parse_year(request.args.get("start_year"), "Mula taon")
        end_year = _parse_year(request.args.get("end_year"), "Hanggang taon")
        if start_year is not None and end_year is not None and start_year > end_year:
            return jsonify({"error": "Hindi maaaring mas huli ang 'Mula taon'."}), 400
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    try:
        return jsonify(
            {
                "query": query,
                **_cached_search(query, start_year, end_year),
            }
        )
    except SemanticScholarError as error:
        app.logger.warning("Semantic Scholar search failed: %s", error)
        return jsonify({"error": str(error)}), error.status_code


@app.post("/api/seeky")
def api_seeky():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Ipadala ang tanong bilang JSON."}), 400

    question = payload.get("question")
    if not isinstance(question, str):
        return jsonify({"error": "Kailangang text ang tanong."}), 400
    if not question.strip():
        return jsonify({"error": "Maglagay ng tanong para kay Seek-y."}), 400
    if len(question) > 300:
        return jsonify({"error": "Hanggang 300 character lamang ang tanong."}), 400

    return jsonify(match_question(question))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
