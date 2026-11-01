import json
import os
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from unittest.mock import patch

import app


class SikLayagApiTests(unittest.TestCase):
    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()
        with app._provider_request_lock:
            app._next_provider_request_at = 0
        with app._search_cache_lock:
            app._search_cache.clear()

    def test_home_serves_the_design(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SIK", response.data)
        self.assertIn(b"static/app.js", response.data)
        self.assertIn(b'id="load-more-results"', response.data)
        self.assertIn(b"10 resulta bawat pahina", response.data)
        self.assertNotIn(b'id="faq"', response.data)
        self.assertNotIn(b'href="#faq"', response.data)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_seeky_endpoint_returns_prepared_bilingual_answer(self):
        english = self.client.post("/api/seeky", json={"question": "what is rrl"})
        filipino = self.client.post(
            "/api/seeky", json={"question": "ano ang ibig sabihin ng rrl"}
        )

        self.assertEqual(english.status_code, 200)
        self.assertEqual(english.get_json()["language"], "en")
        self.assertEqual(filipino.status_code, 200)
        self.assertEqual(filipino.get_json()["language"], "fil")
        self.assertEqual(filipino.get_json()["match_type"], "keyword")

    def test_seeky_endpoint_validates_question(self):
        self.assertEqual(self.client.post("/api/seeky", json={}).status_code, 400)
        self.assertEqual(
            self.client.post("/api/seeky", json={"question": " "}).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(
                "/api/seeky", json={"question": "a" * 301}
            ).status_code,
            400,
        )

    def test_search_rejects_empty_and_overlong_queries(self):
        self.assertEqual(self.client.get("/api/search").status_code, 400)
        self.assertEqual(
            self.client.get(f"/api/search?q={'a' * 301}").status_code, 400
        )

    def test_search_rejects_invalid_year_filters(self):
        self.assertEqual(
            self.client.get("/api/search?q=research&start_year=not-a-year").status_code,
            400,
        )
        self.assertEqual(
            self.client.get("/api/search?q=research&start_year=2025&end_year=2020").status_code,
            400,
        )

    @patch("app.urlopen", side_effect=URLError("provider unavailable"))
    def test_search_returns_a_safe_error_when_provider_is_unreachable(self, _urlopen):
        response = self.client.get("/api/search?q=research")

        self.assertEqual(response.status_code, 502)
        self.assertIn("error", response.get_json())

    @patch("app.urlopen", side_effect=TimeoutError("provider timed out"))
    def test_search_returns_gateway_timeout_when_provider_times_out(self, _urlopen):
        response = self.client.get("/api/search?q=research")

        self.assertEqual(response.status_code, 504)
        self.assertEqual(
            response.get_json()["error"],
            "Search is temporarily unavailable. Please try again later.",
        )

    @patch(
        "app.urlopen",
        side_effect=HTTPError(
            "https://api.semanticscholar.org", 429, "Rate limited", {}, None
        ),
    )
    def test_search_returns_busy_message_when_provider_rate_limits(self, _urlopen):
        response = self.client.get("/api/search?q=research")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json()["error"],
            "Search service is busy; try again shortly.",
        )

    @patch(
        "app._cached_search",
        return_value={
            "total": 0,
            "offset": 0,
            "limit": 10,
            "has_more": False,
            "results": [],
        },
    )
    def test_search_passes_year_filters(self, cached_search):
        response = self.client.get(
            "/api/search?q=  social+media  &start_year=2020&end_year=2024"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["query"], "social media")
        cached_search.assert_called_once_with("social media", 2020, 2024, 0)

    @patch(
        "app._cached_search",
        return_value={
            "total": 25,
            "offset": 10,
            "limit": 10,
            "has_more": True,
            "results": [],
        },
    )
    def test_search_accepts_a_pagination_offset(self, cached_search):
        response = self.client.get("/api/search?q=research&offset=10")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["offset"], 10)
        self.assertTrue(response.get_json()["has_more"])
        cached_search.assert_called_once_with("research", None, None, 10)

    def test_search_rejects_invalid_pagination_offsets(self):
        for offset in ("-10", "1", "1010", "not-a-number"):
            with self.subTest(offset=offset):
                response = self.client.get(f"/api/search?q=research&offset={offset}")
                self.assertEqual(response.status_code, 400)

    @patch(
        "app.urlopen",
    )
    def test_provider_maps_papers_and_rejects_non_http_links(self, urlopen):
        response = unittest.mock.MagicMock()
        response.read.return_value = json.dumps(
            {
                "total": 1,
                "data": [
                    {
                        "title": "Research paper",
                        "abstract": "A study of this research topic.",
                        "paperId": "paper/id",
                        "authors": [{"name": "Author"}],
                        "year": 2024,
                        "venue": "Research Journal",
                        "citationCount": 12,
                        "url": "https://www.semanticscholar.org/paper/id",
                    }
                ],
            }
        ).encode()
        urlopen.return_value.__enter__.return_value = response

        result = app.search_papers("research topic")

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["results"][0]["authors"], ["Author"])
        self.assertEqual(
            set(result["results"][0]),
            {
                "title",
                "abstract",
                "authors",
                "year",
                "venue",
                "citation_count",
                "url",
            },
        )
        self.assertEqual(result["results"][0]["abstract"], "A study of this research topic.")
        self.assertTrue(result["results"][0]["url"].startswith("https://"))

    @patch("app.urlopen")
    def test_provider_normalizes_missing_paper_metadata(self, urlopen):
        response = unittest.mock.MagicMock()
        response.read.return_value = b'{"total": 1, "data": [{"authors": null, "url": "javascript:alert(1)"}]}'
        urlopen.return_value.__enter__.return_value = response

        result = app.search_papers("research topic")
        paper = result["results"][0]

        self.assertEqual(paper["title"], "Title unavailable")
        self.assertIsNone(paper["abstract"])
        self.assertEqual(paper["authors"], [])
        self.assertIsNone(paper["year"])
        self.assertIsNone(paper["venue"])
        self.assertIsNone(paper["citation_count"])
        self.assertIsNone(paper["url"])

    @patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": ""})
    @patch("app.urlopen")
    def test_provider_requests_ten_results_for_selected_year_range(self, urlopen):
        response = unittest.mock.MagicMock()
        response.read.return_value = json.dumps(
            {
                "total": 12,
                "data": [
                    {
                        "paperId": f"paper-{index}",
                        "title": f"Paper {index}",
                        "abstract": None,
                        "authors": [],
                        "year": 2024,
                        "url": f"https://www.semanticscholar.org/paper/{index}",
                    }
                    for index in range(12)
                ],
            }
        ).encode()
        urlopen.return_value.__enter__.return_value = response

        result = app.search_papers("research topic", 2020, 2024)

        request = urlopen.call_args.args[0]
        self.assertIn("limit=10", request.full_url)
        self.assertIn("offset=0", request.full_url)
        self.assertIn("year=2020-2024", request.full_url)
        self.assertIn("abstract", request.full_url)
        self.assertNotIn("x-api-key", request.headers)
        self.assertEqual(len(result["results"]), 10)
        self.assertTrue(result["has_more"])

    @patch("app.urlopen")
    def test_provider_requests_the_requested_page(self, urlopen):
        response = unittest.mock.MagicMock()
        response.read.return_value = b'{"total": 15, "data": [{"paperId": "paper-10"}]}'
        urlopen.return_value.__enter__.return_value = response

        result = app.search_papers("research topic", offset=10)

        self.assertIn("offset=10", urlopen.call_args.args[0].full_url)
        self.assertEqual(result["offset"], 10)
        self.assertTrue(result["has_more"])

    @patch("app.urlopen")
    def test_provider_keeps_pagination_available_when_total_is_missing(self, urlopen):
        response = unittest.mock.MagicMock()
        response.read.return_value = json.dumps(
            {
                "data": [
                    {"paperId": f"paper-{index}", "title": f"Paper {index}"}
                    for index in range(10)
                ]
            }
        ).encode()
        urlopen.return_value.__enter__.return_value = response

        result = app.search_papers("research topic")

        self.assertEqual(result["total"], 10)
        self.assertTrue(result["has_more"])

    @patch("app.search_papers", return_value={"total": 5, "results": []})
    def test_identical_searches_use_the_short_cache(self, search_papers):
        app._search_cache.clear()
        first = self.client.get("/api/search?q=classroom+research")
        second = self.client.get("/api/search?q=Classroom+Research")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        search_papers.assert_called_once_with("classroom research", None, None, 0)

    def test_concurrent_identical_cache_misses_make_one_provider_call(self):
        def delayed_search(*args):
            time.sleep(0.02)
            return {"total": 1, "results": []}

        with patch("app.search_papers", side_effect=delayed_search) as search_papers:
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(
                    executor.map(
                        lambda _: app._cached_search("same query", None, None),
                        range(4),
                    )
                )

        self.assertEqual(len(results), 4)
        search_papers.assert_called_once_with("same query", None, None, 0)

    def test_provider_requests_are_spaced_for_concurrent_users(self):
        starts = []
        active_requests = 0
        maximum_active_requests = 0
        state_lock = threading.Lock()
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"total": 0, "data": []}'

        def fake_urlopen(*args, **kwargs):
            nonlocal active_requests, maximum_active_requests
            with state_lock:
                active_requests += 1
                maximum_active_requests = max(
                    maximum_active_requests, active_requests
                )
                starts.append(time.monotonic())
            time.sleep(0.01)
            with state_lock:
                active_requests -= 1
            return response

        with patch("app.PROVIDER_MIN_REQUEST_INTERVAL_SECONDS", 0.05):
            with patch("app.urlopen", side_effect=fake_urlopen):
                with ThreadPoolExecutor(max_workers=2) as executor:
                    list(executor.map(app.search_papers, ["first", "second"]))

        self.assertEqual(maximum_active_requests, 1)
        self.assertGreaterEqual(starts[1] - starts[0], 0.045)


if __name__ == "__main__":
    unittest.main()
