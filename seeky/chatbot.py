from rapidfuzz.fuzz import ratio

from .faqs import FAQ_ENTRIES, suggested_questions
from .matcher import exact_match, fuzzy_match, keyword_match, topic_match
from .preprocessing import normalize, preprocess_question


FALLBACK_ANSWER = (
    "I don't have the answer for this one just yet! "
    "Try asking me something about research writing or the website."
)
DISCLAIMER = {
    "en": "Seeky can still make mistakes, so please double-check important information.",
    "fil": "Maaari pa ring magkamali si Seeky, kaya tiyaking suriin muli ang mahahalagang impormasyon.",
}
GREETING_ANSWERS = {
    "en": "Hey! I'm Seeky, your FAQ chatbot, here to help you!",
    "fil": "Kumusta! Ako si Seeky, ang iyong FAQ chatbot. Nandito ako para tumulong!",
}
FAREWELL_ANSWERS = {
    "en": (
        "Bye! See you again next time. Good luck with your research, "
        "and I hope your research is successfully defended!"
    ),
    "fil": (
        "Paalam! Sana ay magkita tayong muli. Good luck sa iyong pananaliksik, "
        "at sana ay maipagtanggol mo ito nang matagumpay!"
    ),
}
CONVERSATIONAL_PHRASES = {
    "greeting": {
        "en": ("hi", "hey", "hello", "heya", "hello there", "hey seeky", "hi seeky",
               "good morning", "good afternoon", "good evening"),
        "fil": ("kamusta", "kumusta", "mabuhay", "magandang umaga",
                "magandang hapon", "magandang gabi"),
    },
    "farewell": {
        "en": ("bye", "goodbye", "see you", "see you later", "farewell", "bye seeky"),
        "fil": ("paalam", "ingat", "hanggang sa muli", "hanggang sa susunod"),
    },
}


def _conversation_match(normalized_question):
    words = normalized_question.split()
    if not words or len(words) > 4 or len(normalized_question) > 32:
        return None

    ranked = []
    for intent, languages in CONVERSATIONAL_PHRASES.items():
        for language, phrases in languages.items():
            for phrase in phrases:
                ranked.append((ratio(normalized_question, normalize(phrase)), intent, language))

    score, intent, language = max(ranked)
    if score < 78:
        return None
    answer = GREETING_ANSWERS[language] if intent == "greeting" else FAREWELL_ANSWERS[language]
    return answer, language, intent


def _fallback_result():
    return {
        "answer": FALLBACK_ANSWER,
        "matched_question": None,
        "language": None,
        "match_type": "fallback",
        "suggested_questions": [],
    }


def match_question(question):
    preprocessed = preprocess_question(question, FAQ_ENTRIES)
    normalized_question = preprocessed["normalized"]
    if not normalized_question:
        return _fallback_result()

    conversation = _conversation_match(normalized_question)
    if conversation is not None:
        answer, language, intent = conversation
        return {
            "answer": answer,
            "matched_question": None,
            "language": language,
            "match_type": intent,
            "suggested_questions": [],
        }

    terms = set(preprocessed["keywords"])
    if {"qualitative", "quantitative"}.issubset(terms) or {
        "kwalitatibong", "kwantitatibong"
    }.issubset(terms):
        return _fallback_result()

    match = exact_match(normalized_question, FAQ_ENTRIES)
    match_type = "exact"
    if match is None:
        match = keyword_match(preprocessed, FAQ_ENTRIES)
        match_type = "keyword"
    if match is None:
        match = fuzzy_match(preprocessed, FAQ_ENTRIES)
        match_type = "fuzzy"
    if match is None:
        match = topic_match(preprocessed, FAQ_ENTRIES)
        match_type = "keyword"
    if match is None:
        return _fallback_result()

    faq, language = match
    return {
        "answer": faq["answers"][language],
        "matched_question": faq["questions"][language],
        "language": language,
        "match_type": match_type,
        "suggested_questions": suggested_questions(faq, language),
    }
