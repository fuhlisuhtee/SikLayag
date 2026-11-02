def _faq(
    question_en,
    question_fil,
    answer_en,
    answer_fil,
    keywords_en,
    keywords_fil,
    phrases_en=(),
    phrases_fil=(),
    category="",
):
    return {
        "category": category,
        "questions": {"en": question_en, "fil": question_fil},
        "answers": {"en": answer_en, "fil": answer_fil},
        "phrases": {"en": phrases_en, "fil": phrases_fil},
        "keywords": {"en": keywords_en, "fil": keywords_fil},
    }


from .qualitative_research import FAQS as QUALITATIVE_RESEARCH_FAQS
from .quantitative_research import FAQS as QUANTITATIVE_RESEARCH_FAQS
from .research_fundamentals import FAQS as RESEARCH_FUNDAMENTALS_FAQS
from .website_features import FAQS as WEBSITE_FEATURES_FAQS

FAQ_ENTRIES = (
    *RESEARCH_FUNDAMENTALS_FAQS,
    *QUALITATIVE_RESEARCH_FAQS,
    *QUANTITATIVE_RESEARCH_FAQS,
    *WEBSITE_FEATURES_FAQS,
)


def suggested_questions(faq, language, limit=3):
    category_entries = [
        entry for entry in FAQ_ENTRIES
        if entry["category"] == faq["category"]
    ]
    if len(category_entries) < 2:
        return []

    current_index = category_entries.index(faq)
    following = category_entries[current_index + 1:] + category_entries[:current_index]
    return [entry["questions"][language] for entry in following[:limit]]