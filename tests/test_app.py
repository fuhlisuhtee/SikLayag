import json
import os
import unittest
from unittest.mock import patch

import app


class SikLayagApiTests(unittest.TestCase):
    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def test_home_serves_the_design(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SIK", response.data)
        self.assertIn(b"static/app.js", response.data)
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

    @patch("app._cached_search", return_value={"total": 0, "results": []})
    def test_search_passes_year_filters(self, cached_search):
        response = self.client.get(
            "/api/search?q=  social+media  &start_year=2020&end_year=2024"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["query"], "social media")
        cached_search.assert_called_once_with("social media", 2020, 2024)

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
                        "paperId": "paper/id",
                        "authors": [{"name": "Author"}],
                        "year": 2024,
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
            set(result["results"][0]), {"title", "authors", "year", "url"}
        )
        self.assertTrue(result["results"][0]["url"].startswith("https://"))

    @patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": ""})
    @patch("app.urlopen")
    def test_provider_requests_five_results_for_selected_year_range(self, urlopen):
        response = unittest.mock.MagicMock()
        response.read.return_value = json.dumps(
            {
                "total": 6,
                "data": [
                    {
                        "paperId": f"paper-{index}",
                        "title": f"Paper {index}",
                        "authors": [],
                        "year": 2024,
                        "url": f"https://www.semanticscholar.org/paper/{index}",
                    }
                    for index in range(6)
                ],
            }
        ).encode()
        urlopen.return_value.__enter__.return_value = response

        result = app.search_papers("research topic", 2020, 2024)

        request = urlopen.call_args.args[0]
        self.assertIn("limit=5", request.full_url)
        self.assertIn("year=2020-2024", request.full_url)
        self.assertIn("fields=paperId", request.full_url)
        self.assertNotIn("x-api-key", request.headers)
        self.assertEqual(len(result["results"]), 5)

    @patch("app.search_papers", return_value={"total": 5, "results": []})
    def test_identical_searches_use_the_short_cache(self, search_papers):
        app._search_cache.clear()
        try:
            first = self.client.get("/api/search?q=classroom+research")
            second = self.client.get("/api/search?q=Classroom+Research")
        finally:
            app._search_cache.clear()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        search_papers.assert_called_once_with("classroom research", None, None)


if __name__ == "__main__":
    unittest.main()
