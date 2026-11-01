import unittest

from seeky import FALLBACK_ANSWER, match_question


class SeekyMatchingTests(unittest.TestCase):
    def test_exact_english_question(self):
        result = match_question("what is rrl")
        self.assertEqual(result["match_type"], "exact")
        self.assertEqual(result["language"], "en")
        self.assertTrue(result["answer"].startswith("RRL stands for"))

    def test_exact_filipino_question_returns_filipino_answer(self):
        result = match_question("ANO ANG RRL?")
        self.assertEqual(result["match_type"], "exact")
        self.assertEqual(result["language"], "fil")
        self.assertTrue(result["answer"].startswith("Ang RRL o Review"))

    def test_keyword_phrase_matches_filipino_question(self):
        result = match_question("ano ang ibig sabihin ng rrl")
        self.assertEqual(result["match_type"], "keyword")
        self.assertEqual(result["language"], "fil")
        self.assertTrue(result["answer"].startswith("Ang RRL o Review"))

    def test_weighted_keyword_matches_feature_question(self):
        result = match_question("what does the research editor do")
        self.assertEqual(result["match_type"], "exact")
        self.assertTrue(result["answer"].startswith("The Interactive Research Editor"))

    def test_fuzzy_match_handles_a_typo(self):
        result = match_question("what is quantitive research?")
        self.assertEqual(result["match_type"], "fuzzy")
        self.assertTrue(result["answer"].startswith("Quantitative research focuses"))

    def test_out_of_scope_question_uses_fallback(self):
        result = match_question("How do I bake sourdough bread?")
        self.assertEqual(result["match_type"], "fallback")
        self.assertEqual(result["answer"], FALLBACK_ANSWER)

    def test_broad_ambiguous_keyword_uses_fallback(self):
        result = match_question("research")
        self.assertEqual(result["match_type"], "fallback")
        self.assertEqual(result["answer"], FALLBACK_ANSWER)

    def test_blank_question_uses_fallback(self):
        result = match_question("   ")
        self.assertEqual(result["match_type"], "fallback")


if __name__ == "__main__":
    unittest.main()
