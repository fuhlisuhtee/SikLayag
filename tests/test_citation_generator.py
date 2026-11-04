import unittest

from citation_generator import generate_apa7_citations


class Apa7CitationTests(unittest.TestCase):
    def test_journal_article_generates_three_apa_citation_forms(self):
        citations = generate_apa7_citations(
            {
                "authors": ["Jane Doe", "John Smith"],
                "year": 2024,
                "title": "Researching student experiences",
                "venue": "Journal of Research",
                "volume": "12",
                "issue": "3",
                "pages": "34-45",
                "doi": "https://doi.org/10.1234/example",
            }
        )

        self.assertEqual(citations["narrative"], "Doe and Smith (2024)")
        self.assertEqual(citations["parenthetical"], "(Doe & Smith, 2024)")
        self.assertEqual(
            citations["reference"],
            "Doe, J., & Smith, J. (2024). Researching student experiences. "
            "Journal of Research, 12(3), 34-45. https://doi.org/10.1234/example",
        )
        self.assertIn(
            "<em>Journal of Research, 12</em>(3), 34-45.",
            citations["reference_html"],
        )

    def test_reference_html_escapes_metadata(self):
        citations = generate_apa7_citations(
            {
                "authors": ["Jane Doe"],
                "year": 2024,
                "title": "<script>alert(1)</script>",
                "venue": "Research & Review",
            }
        )

        self.assertNotIn("<script>", citations["reference_html"])
        self.assertIn("&lt;script&gt;", citations["reference_html"])
        self.assertIn("<em>Research &amp; Review</em>", citations["reference_html"])

    def test_three_or_more_authors_use_et_al_in_text(self):
        citations = generate_apa7_citations(
            {
                "authors": ["Jane Doe", "John Smith", "Alex Lee"],
                "year": 2022,
                "title": "A study",
            }
        )

        self.assertEqual(citations["narrative"], "Doe et al. (2022)")
        self.assertEqual(citations["parenthetical"], "(Doe et al., 2022)")

    def test_missing_authors_doi_and_publication_details_are_supported(self):
        citations = generate_apa7_citations(
            {
                "authors": [],
                "year": None,
                "title": "An untimed study about citation quality",
                "url": "https://www.semanticscholar.org/paper/123",
            }
        )

        self.assertEqual(
            citations["narrative"], '"An untimed study about citation..." (n.d.)'
        )
        self.assertEqual(
            citations["parenthetical"],
            '("An untimed study about citation...", n.d.)',
        )
        self.assertEqual(
            citations["reference"],
            "An untimed study about citation quality (n.d.).",
        )

    def test_unavailable_title_and_year_use_safe_fallbacks(self):
        citations = generate_apa7_citations(
            {"authors": ["Author"], "title": "Title unavailable", "year": None}
        )

        self.assertEqual(citations["narrative"], "Author (n.d.)")
        self.assertEqual(
            citations["reference"],
            "Author (n.d.). [Title unavailable].",
        )

    def test_article_without_doi_omits_semantic_scholar_record_link(self):
        citations = generate_apa7_citations(
            {
                "authors": ["Jane Doe"],
                "year": 2024,
                "title": "Research article",
                "url": "https://www.semanticscholar.org/paper/123",
            }
        )

        self.assertEqual(
            citations["reference"], "Doe, J. (2024). Research article."
        )


if __name__ == "__main__":
    unittest.main()
