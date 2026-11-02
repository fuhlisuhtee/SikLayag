from rapidfuzz.fuzz import ratio

from .preprocessing import is_filipino, meaningful_phrase, normalize


KEYWORD_THRESHOLD = 3
KEYWORD_MATCH_MARGIN = 2
FUZZY_THRESHOLD = 82
FUZZY_MATCH_MARGIN = 2


def exact_match(normalized_question, faq_entries):
    for faq in faq_entries:
        for language in ("en", "fil"):
            candidates = (
                faq["questions"][language],
                *faq["phrases"][language],
            )
            if any(normalize(candidate) == normalized_question for candidate in candidates):
                return faq, language
    return None


def topic_match(preprocessed, faq_entries):
    keywords = set(preprocessed["keywords"])
    question_words = set(preprocessed["tokens"])
    has_question_intent = bool(
        question_words
        & {"can", "define", "explain", "meaning", "what", "who", "why", "ano", "paano"}
    )
    if not has_question_intent or not keywords:
        return None

    candidates = []
    for faq in faq_entries:
        for language in ("en", "fil"):
            faq_candidates = (
                faq["questions"][language],
                *faq["phrases"][language],
            )
            for candidate in faq_candidates:
                terms = set(meaningful_phrase(candidate).split())
                if terms and terms.issubset(keywords):
                    candidates.append((len(terms), faq))

    if not candidates:
        return None
    best_specificity = max(specificity for specificity, _ in candidates)
    best_faqs = {
        id(faq): faq for specificity, faq in candidates
        if specificity == best_specificity
    }
    if len(best_faqs) != 1:
        return None

    faq = next(iter(best_faqs.values()))
    answer_language = "fil" if is_filipino(preprocessed["normalized"]) else "en"
    return faq, answer_language


def keyword_match(preprocessed, faq_entries):
    keywords = set(preprocessed["keywords"])
    phrases = set(preprocessed["phrases"])
    ranked = []
    for faq in faq_entries:
        score = max(
            sum(
                weight
                for phrase, weight in faq["keywords"][language]
                if (
                    meaningful_phrase(phrase) in phrases
                    if len(meaningful_phrase(phrase).split()) > 1
                    else meaningful_phrase(phrase) in keywords
                )
            )
            for language in ("en", "fil")
        )
        if score >= KEYWORD_THRESHOLD:
            ranked.append((score, faq))

    ranked.sort(key=lambda result: result[0], reverse=True)
    if not ranked:
        return None
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < KEYWORD_MATCH_MARGIN:
        return None

    answer_language = "fil" if is_filipino(preprocessed["normalized"]) else "en"
    return ranked[0][1], answer_language


def fuzzy_match(preprocessed, faq_entries):
    keywords = preprocessed["keywords"]
    fuzzy_question = " ".join(preprocessed["phrases"] or keywords)
    if len(keywords) < 2:
        return None

    ranked = []
    for faq in faq_entries:
        for language in ("en", "fil"):
            candidates = (
                faq["questions"][language],
                *faq["phrases"][language],
            )
            score = max(
                ratio(fuzzy_question, meaningful_phrase(candidate))
                for candidate in candidates
            )
            ranked.append((score, faq, language))

    ranked.sort(key=lambda result: result[0], reverse=True)
    if not ranked or ranked[0][0] < FUZZY_THRESHOLD:
        return None
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < FUZZY_MATCH_MARGIN:
        if ranked[0][1] is ranked[1][1]:
            answer_language = "fil" if is_filipino(preprocessed["normalized"]) else "en"
            return ranked[0][1], answer_language
        return None
    return ranked[0][1], ranked[0][2]
