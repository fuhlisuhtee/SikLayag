import unittest

from seeky import (
    DISCLAIMER,
    FAQ_ENTRIES,
    FALLBACK_ANSWER,
    match_question,
    preprocess_question,
)


class SeekyMatchingTests(unittest.TestCase):
    def test_exact_english_question(self):
        result = match_question("what is rrl")
        self.assertEqual(result["match_type"], "exact")
        self.assertEqual(result["language"], "en")
        self.assertTrue(result["answer"].startswith("RRL stands for"))
        self.assertNotIn(DISCLAIMER["en"], result["answer"])

    def test_exact_filipino_question_returns_filipino_answer(self):
        result = match_question("ANO ANG RRL?")
        self.assertEqual(result["match_type"], "exact")
        self.assertEqual(result["language"], "fil")
        self.assertTrue(result["answer"].startswith("Ang RRL o Review"))
        self.assertNotIn(DISCLAIMER["fil"], result["answer"])

    def test_keyword_matching_handles_greeting_before_a_topic(self):
        result = match_question("hello! what is research?")

        self.assertEqual(result["match_type"], "keyword")
        self.assertEqual(result["matched_question"], "What is research?")
        self.assertTrue(result["answer"].startswith("Research is a systematic process"))

    def test_topic_matching_ignores_unrelated_words_around_a_question(self):
        result = match_question(
            "hello! this random thing, can you tell me what research is?"
        )

        self.assertEqual(result["match_type"], "keyword")
        self.assertEqual(result["matched_question"], "What is research?")

    def test_keyword_matching_handles_rephrased_definition_request(self):
        result = match_question("can you define research")

        self.assertEqual(result["match_type"], "keyword")
        self.assertEqual(result["matched_question"], "What is research?")
        self.assertTrue(result["answer"].startswith("Research is a systematic process"))

    def test_keyword_phrase_matches_filipino_question(self):
        result = match_question("ano ang ibig sabihin ng rrl")
        self.assertEqual(result["match_type"], "keyword")
        self.assertEqual(result["language"], "fil")
        self.assertTrue(result["answer"].startswith("Ang RRL o Review"))

    def test_weighted_keyword_matches_feature_question(self):
        result = match_question("research editor")
        self.assertEqual(result["match_type"], "keyword")
        self.assertEqual(result["language"], "en")
        self.assertTrue(result["answer"].startswith("The Interactive Research Editor"))

    def test_preprocessing_removes_noise_and_preserves_known_phrases(self):
        result = preprocess_question(
            "Hey! Can you tell me what quantitative research is in simple terms?"
        )

        self.assertEqual(result["keywords"], ["quantitative", "research"])
        self.assertIn("quantitative research", result["phrases"])

    def test_preprocessing_extracts_only_meaningful_example_keyword(self):
        result = preprocess_question(
            "hey! can you tell me what research is in simple terms?"
        )

        self.assertEqual(result["keywords"], ["research"])

    def test_taglish_question_selects_filipino_answer(self):
        result = match_question("ano yung quantitative research")

        self.assertEqual(result["language"], "fil")
        self.assertTrue(result["answer"].startswith("Ang quantitative research"))

    def test_fuzzy_match_handles_a_typo(self):
        result = match_question("what is quantitive research?")
        self.assertEqual(result["match_type"], "fuzzy")
        self.assertTrue(result["answer"].startswith("Quantitative research focuses"))

    def test_fuzzy_matching_does_not_guess_between_similar_topics(self):
        result = match_question("What is qualitative versus quantitative research?")

        self.assertEqual(result["match_type"], "fallback")
        self.assertEqual(result["answer"], FALLBACK_ANSWER)

    def test_fuzzy_match_handles_varying_spelling(self):
        result = match_question("what is quantative resarch?")
        self.assertEqual(result["match_type"], "fuzzy")
        self.assertTrue(result["answer"].startswith("Quantitative research focuses"))

    def test_related_questions_are_suggested_in_the_answer_language(self):
        english = match_question("what is qualitative research")
        filipino = match_question("ano ang kwalitatibong pananaliksik")

        self.assertIn(
            "What are the characteristics of qualitative research?",
            english["suggested_questions"],
        )
        self.assertIn(
            "Ano ang mga katangian ng kwalitatibong pananaliksik?",
            filipino["suggested_questions"],
        )

    def test_suggested_questions_stay_in_the_matched_faq_category(self):
        result = match_question("what is qualitative research")
        matched_faq = next(
            faq for faq in FAQ_ENTRIES
            if faq["questions"][result["language"]] == result["matched_question"]
        )
        suggested_faqs = [
            next(
                faq for faq in FAQ_ENTRIES
                if faq["questions"][result["language"]] == question
            )
            for question in result["suggested_questions"]
        ]

        self.assertLessEqual(len(suggested_faqs), 3)
        self.assertTrue(
            all(faq["category"] == matched_faq["category"] for faq in suggested_faqs)
        )

    def test_greeting_and_farewell_prompts_get_personable_replies(self):
        greeting = match_question("helloo!")
        farewell = match_question("byee")

        self.assertEqual(greeting["match_type"], "greeting")
        self.assertIn("I'm Seeky", greeting["answer"])
        self.assertEqual(farewell["match_type"], "farewell")
        self.assertIn("Good luck with your research", farewell["answer"])

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
