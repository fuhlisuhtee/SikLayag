import re
import unicodedata


STOP_WORDS = {
    "a", "about", "an", "and", "ang", "ano", "are", "as", "at", "ba", "be",
    "can", "could", "define", "did", "do", "does", "for", "from",
    "hello", "hey", "hi", "how", "i", "in", "is", "it", "me", "my", "ng", "of",
    "on", "or", "please", "simple", "tell", "terms", "that", "the",
    "their", "this", "to", "what", "when", "where", "which", "who",
    "why", "with", "would", "you", "your", "ako", "akin", "aking",
    "dahil", "dapat", "ito", "iyon", "kami",
    "kanila", "ko", "kung", "mga", "mo", "na", "ng", "nina", "nito",
    "niya", "nila", "namin", "para", "paano", "po", "sa", "saan",
    "si", "sila", "sino", "siya", "tayo", "tungkol", "yung",
}

FILIPINO_MARKERS = {
    "ako", "ang", "ano", "atin", "ba", "bakit", "ito", "ko", "mga",
    "ng", "para", "paano", "saan", "sino", "sa", "namin", "mo",
    "kailangan", "ibig", "kahulugan", "pananaliksik", "libre", "yung",
}


def normalize(text):
    decomposed = unicodedata.normalize("NFD", text.casefold())
    without_accents = "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", without_accents)).strip()


def meaningful_phrase(phrase):
    return " ".join(
        word for word in normalize(phrase).split()
        if word not in STOP_WORDS
    )


def contains_phrase(normalized_text, phrase):
    normalized_phrase = normalize(phrase)
    return bool(normalized_phrase) and f" {normalized_phrase} " in f" {normalized_text} "


def preprocess_question(question, faq_entries=None):
    if faq_entries is None:
        from .faqs import FAQ_ENTRIES

        faq_entries = FAQ_ENTRIES

    normalized_question = normalize(question)
    tokens = normalized_question.split()
    keywords = [word for word in tokens if word not in STOP_WORDS]
    normalized_keywords = " ".join(keywords)
    known_phrases = set()

    for faq in faq_entries:
        for language in ("en", "fil"):
            candidates = (
                faq["questions"][language],
                *faq["phrases"][language],
                *(phrase for phrase, _ in faq["keywords"][language]),
            )
            for candidate in candidates:
                phrase = meaningful_phrase(candidate)
                if len(phrase.split()) > 1:
                    known_phrases.add(phrase)

    phrases = [
        phrase for phrase in sorted(known_phrases, key=lambda value: (-len(value.split()), value))
        if contains_phrase(normalized_keywords, phrase)
    ]
    return {
        "normalized": normalized_question,
        "tokens": tokens,
        "keywords": keywords,
        "phrases": phrases,
    }


def is_filipino(normalized_question):
    return any(word in FILIPINO_MARKERS for word in normalized_question.split())
