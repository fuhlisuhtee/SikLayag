import re
import unicodedata
from difflib import SequenceMatcher


FALLBACK_ANSWER = (
    "I don't have the answer for this one just yet! "
    "Try asking me something about research writing or the website."
)
KEYWORD_THRESHOLD = 3
KEYWORD_MATCH_MARGIN = 2
FUZZY_THRESHOLD = 0.82
FUZZY_MATCH_MARGIN = 0.05


def _faq(
    question_en,
    question_fil,
    answer_en,
    answer_fil,
    keywords_en,
    keywords_fil,
    phrases_en=(),
    phrases_fil=(),
):
    return {
        "questions": {"en": question_en, "fil": question_fil},
        "answers": {"en": answer_en, "fil": answer_fil},
        "phrases": {"en": phrases_en, "fil": phrases_fil},
        "keywords": {"en": keywords_en, "fil": keywords_fil},
    }


FAQ_ENTRIES = [
    _faq(
        "What is this website?",
        "Ano ang website na ito?",
        "This website is an educational platform designed to help students understand and practice academic research writing through learning materials and interactive tools.",
        "Ang website na ito ay isang platapormang pang-edukasyon na ginawa upang tulungan ang mga mag-aaral na maunawaan at maisagawa ang akademikong pananaliksik sa pamamagitan ng mga materyales sa pag-aaral at mga interactive na kagamitan.",
        [("website", 1), ("educational platform", 4), ("learning materials", 3), ("interactive tools", 3)],
        [("website", 1), ("plataporma", 4), ("pook sapot", 3), ("site", 1)],
        ("what is siklayag", "what is this site"),
        ("ano ang siklayag", "ano ang site na ito", "ano itong website"),
    ),
    _faq(
        "What is the purpose of this website?",
        "Ano ang layunin ng website na ito?",
        "Its purpose is to provide students with accessible learning resources and tools that support different stages of the research-writing process.",
        "Layunin nitong magbigay ng madaling ma-access na mga kagamitan sa pag-aaral at mga tool na makatutulong sa mga mag-aaral sa iba't ibang yugto ng proseso ng pagsulat ng pananaliksik.",
        [("purpose", 4), ("learning resources", 4), ("research writing process", 4)],
        [("layunin", 4), ("para saan", 4), ("pagsulat ng pananaliksik", 3), ("kagamitan sa pag aaral", 3)],
        ("purpose of siklayag", "why was this website created"),
        ("ano ang layunin ng siklayag", "para saan ang website na ito", "bakit ginawa ang website na ito"),
    ),
    _faq(
        "What is Seeky?",
        "Ano ang Seeky?",
        "Seeky is the website's FAQ assistant. It answers common questions about research writing and the platform's features.",
        "Ang Seeky ay ang FAQ assistant ng website. Sumasagot ito sa mga karaniwang tanong tungkol sa pagsulat ng pananaliksik at sa mga tampok ng platform.",
        [("seeky", 5), ("faq assistant", 4), ("chatbot", 3)],
        [("seeky", 5), ("faq assistant", 4), ("chatbot", 3), ("katulong", 2)],
        ("who is seeky", "what does seeky do"),
        ("sino si seeky", "ano ang ginagawa ni seeky"),
    ),
    _faq(
        "What are the features of this website?",
        "Ano-ano ang mga tampok ng website na ito?",
        "The website includes Animated Video Lessons, RRL Seek Engine, Mga Kabanata, Interactive Research Editor, and Seeky.",
        "Kabilang sa mga tampok ng website ang Animated Video Lessons, RRL Seek Engine, Mga Kabanata, Interactive Research Editor, at Seeky.",
        [("features", 4), ("video lessons", 2), ("rrl seek engine", 2), ("research editor", 2)],
        [("tampok", 4), ("feature", 4), ("mga kabanata", 2), ("seeky", 1)],
        ("what features does siklayag have", "what are the website features"),
        ("ano ang mga tampok ng siklayag", "ano ang mga feature ng website", "ano ano ang features ng website na ito"),
    ),
    _faq(
        "Do I need an account to use the website?",
        "Kailangan ko ba ng account upang magamit ang website?",
        "No account is required to access the website's features.",
        "Hindi na kailangan ng account upang ma-access at magamit ang mga tampok ng website.",
        [("account", 4), ("sign up", 4), ("register", 3), ("login", 3)],
        [("account", 4), ("mag sign up", 4), ("magrehistro", 4), ("mag log in", 3)],
        ("is an account required", "do i need to sign up"),
        ("kailangan ba ng account", "kailangan ko bang mag sign up", "kailangan bang magrehistro"),
    ),
    _faq(
        "Can I use this website for free?",
        "Libre ko bang magagamit ang website na ito?",
        "Yes. The platform is intended to be freely accessible to its target student users.",
        "Oo. Nilalayon na maging libre at madaling ma-access ang platform para sa mga mag-aaral na gagamit nito.",
        [("free", 4), ("cost", 4), ("price", 4), ("payment", 3)],
        [("libre", 5), ("bayad", 4), ("magkano", 3)],
        ("is siklayag free", "does this website cost anything"),
        ("libre ba ang siklayag", "libre ba ito", "may bayad ba ang website na ito"),
    ),
    _faq(
        "What are Animated Video Lessons?",
        "Ano ang Animated Video Lessons?",
        "Animated Video Lessons provide educational videos that introduce and explain different topics related to academic research writing.",
        "Ang Animated Video Lessons ay nagbibigay ng mga bidyong pang-edukasyon na nagpapakilala at nagpapaliwanag ng iba't ibang paksang may kaugnayan sa akademikong pananaliksik.",
        [("animated video lessons", 5), ("video lessons", 4), ("educational videos", 3)],
        [("animated video lessons", 5), ("mga bidyo", 3), ("bidyong pang edukasyon", 4), ("aralin sa bidyo", 4)],
        ("what are the research videos", "what are animated lessons"),
        ("ano ang mga bidyo sa pananaliksik", "para saan ang animated video lessons"),
    ),
    _faq(
        "What is the RRL Seek Engine?",
        "Ano ang RRL Seek Engine?",
        "The RRL Seek Engine allows students to search for academic papers and discover literature related to their research topics.",
        "Ang RRL Seek Engine ay nagbibigay-daan sa mga mag-aaral na maghanap ng mga akademikong papel at makatuklas ng mga babasahin na may kaugnayan sa kanilang paksa ng pananaliksik.",
        [("rrl seek engine", 5), ("academic papers", 3), ("search for papers", 3), ("related literature", 2)],
        [("rrl seek engine", 5), ("rrl", 4), ("akademikong papel", 3), ("maghanap ng literatura", 3), ("babasahin", 2)],
        ("what does the rrl seek engine do", "what is the rrl search"),
        ("ano ang ginagawa ng rrl seek engine", "para saan ang rrl seek engine", "ano ang rrl search"),
    ),
    _faq(
        "What is Mga Kabanata?",
        "Ano ang Mga Kabanata?",
        "Mga Kabanata provides learning materials and guides related to the different chapters of a research paper.",
        "Ang Mga Kabanata ay naglalaman ng mga materyales at gabay tungkol sa iba't ibang kabanata ng isang papel-pananaliksik.",
        [("mga kabanata", 5), ("chapter guides", 4), ("chapters", 3)],
        [("mga kabanata", 5), ("kabanata", 4), ("papel pananaliksik", 2), ("mga gabay", 2)],
        ("what does mga kabanata provide", "what are the chapter guides"),
        ("ano ang nilalaman ng mga kabanata", "para saan ang mga kabanata", "ano ang mga gabay sa kabanata"),
    ),
    _faq(
        "What is the Interactive Research Editor?",
        "Ano ang Interactive Research Editor?",
        "The Interactive Research Editor is a guided writing tool where students can organize and write their research content using provided chapter structures.",
        "Ang Interactive Research Editor ay isang gabay na kagamitan sa pagsulat kung saan maaaring ayusin at isulat ng mga mag-aaral ang kanilang nilalaman ng pananaliksik gamit ang mga nakahandang estruktura ng bawat kabanata.",
        [("interactive research editor", 5), ("research editor", 4), ("writing pad", 4), ("guided writing", 3)],
        [("interactive research editor", 5), ("research editor", 4), ("writing pad", 4), ("editor", 2), ("kagamitan sa pagsulat", 3)],
        ("what does the research editor do", "what is the writing pad"),
        ("ano ang ginagawa ng research editor", "para saan ang interactive research editor", "ano ang writing pad"),
    ),
    _faq(
        "Can I save my work in the Research Editor?",
        "Maaari ko bang i-save ang aking ginagawa sa Research Editor?",
        "The Research Editor saves drafts locally in the browser, allowing students to continue working on the same device and browser.",
        "Dinisenyo ang Research Editor upang awtomatikong mag-save ng mga draft sa browser. Dahil dito, maaari mong ipagpatuloy ang iyong ginagawa gamit ang parehong device at browser.",
        [("save my work", 5), ("save", 3), ("draft", 3), ("local storage", 4), ("autosave", 4)],
        [("i save", 4), ("isave", 4), ("nase save", 5), ("naka save", 4), ("awtomatikong mag save", 5), ("draft", 3), ("browser", 2)],
        ("does the editor save my work", "will my draft be saved"),
        ("nase save ba ang aking ginagawa sa editor", "awtomatiko bang nase save ang draft", "nase save ba ang draft ko"),
    ),
    _faq(
        "What is research?",
        "Ano ang pananaliksik?",
        "Research is a systematic process of gathering, analyzing, and interpreting information to answer questions or investigate a particular topic.",
        "Ang pananaliksik ay isang sistematikong proseso ng pangangalap, pagsusuri, at pagbibigay-kahulugan sa impormasyon upang masagot ang mga katanungan o masuri ang isang partikular na paksa.",
        [("research", 1), ("systematic process", 3), ("gathering information", 3)],
        [("pananaliksik", 2), ("sistematikong proseso", 4), ("pangangalap ng impormasyon", 4)],
        ("define research",),
        ("ano ang ibig sabihin ng pananaliksik", "kahulugan ng pananaliksik", "ipaliwanag ang pananaliksik"),
    ),
    _faq(
        "What is qualitative research?",
        "Ano ang qualitative research?",
        "Qualitative research focuses on understanding experiences, opinions, behaviors, and perspectives using non-numerical information.",
        "Ang qualitative research ay nakatuon sa pag-unawa sa mga karanasan, opinyon, kilos, at pananaw ng mga tao gamit ang mga impormasyong hindi nakabatay sa numero.",
        [("qualitative research", 5), ("qualitative", 4), ("non numerical information", 3), ("experiences and opinions", 3)],
        [("qualitative research", 5), ("kwalitatibong pananaliksik", 5), ("qualitative", 4), ("hindi nakabatay sa numero", 3), ("karanasan at opinyon", 3)],
        ("define qualitative research",),
        ("ano ang kwalitatibong pananaliksik", "kahulugan ng qualitative research"),
    ),
    _faq(
        "What is quantitative research?",
        "Ano ang quantitative research?",
        "Quantitative research focuses on collecting and analyzing numerical data to identify patterns, relationships, or measurable results.",
        "Ang quantitative research ay nakatuon sa pangangalap at pagsusuri ng mga numerikal na datos upang matukoy ang mga pattern, ugnayan, o mga resultang maaaring masukat.",
        [("quantitative research", 5), ("quantitative", 4), ("numerical data", 4), ("measurable results", 3)],
        [("quantitative research", 5), ("kwantitatibong pananaliksik", 5), ("quantitative", 4), ("numerikal na datos", 4), ("datos na numero", 3)],
        ("define quantitative research",),
        ("ano ang kwantitatibong pananaliksik", "kahulugan ng quantitative research"),
    ),
    _faq(
        "What is a variable?",
        "Ano ang variable?",
        "A variable is a characteristic, factor, or element that can change or take different values in a research study.",
        "Ang variable ay isang katangian, salik, o elemento na maaaring magbago o magkaroon ng iba't ibang halaga sa isang pag-aaral.",
        [("variable", 5), ("variables", 5), ("factor that changes", 3), ("different values", 3)],
        [("variable", 5), ("baryabol", 5), ("salik na nagbabago", 3), ("ibat ibang halaga", 3)],
        ("define variable", "what are variables in research"),
        ("ano ang ibig sabihin ng variable", "kahulugan ng variable"),
    ),
    _faq(
        "What is RRL?",
        "Ano ang RRL?",
        "RRL stands for Review of Related Literature. It is a section of a research paper that discusses existing literature and studies relevant to the research topic.",
        "Ang RRL o Review of Related Literature ay isang bahagi ng papel-pananaliksik na tumatalakay sa mga umiiral na literatura at pag-aaral na may kaugnayan sa paksa ng pananaliksik.",
        [("rrl", 5), ("review of related literature", 5), ("related literature review", 5)],
        [("rrl", 5), ("kahulugan ng rrl", 5), ("ibig sabihin ng rrl", 5), ("kaugnay na literatura", 4), ("review of related literature", 5)],
        ("what does rrl stand for", "meaning of rrl", "what is the review of related literature"),
        ("ano ang ibig sabihin ng review of related literature",),
    ),
    _faq(
        "What is a research title?",
        "Ano ang pamagat ng pananaliksik?",
        "A research title is the name given to a research study. It summarizes the main subject or focus of the investigation.",
        "Ang pamagat ng pananaliksik ay ang pangalan na ibinibigay sa isang pag-aaral. Ipinapakita nito ang pangunahing paksa o pokus ng pananaliksik.",
        [("research title", 5), ("title of a study", 4), ("study title", 4)],
        [("pamagat ng pananaliksik", 5), ("pamagat", 3), ("pangunahing paksa", 2)],
        ("what makes a research title", "define research title"),
        ("ano ang ibig sabihin ng pamagat ng pananaliksik", "kahulugan ng pamagat ng pananaliksik"),
    ),
    _faq(
        "What is a research problem?",
        "Ano ang suliranin sa pananaliksik?",
        "A research problem is the specific issue, concern, or gap that a research study aims to investigate.",
        "Ang suliranin sa pananaliksik ay ang partikular na isyu, problema, o kakulangan sa kaalaman na nais siyasatin ng isang pag-aaral.",
        [("research problem", 5), ("problem statement", 4), ("research gap", 3)],
        [("suliranin sa pananaliksik", 5), ("problema sa pananaliksik", 5), ("suliranin", 3), ("kakulangan sa kaalaman", 3)],
        ("define research problem",),
        ("ano ang problema sa pananaliksik", "kahulugan ng suliranin sa pananaliksik", "ano ang suliranin sa research"),
    ),
    _faq(
        "What is a hypothesis?",
        "Ano ang hypothesis?",
        "A hypothesis is a proposed explanation or prediction about a relationship between variables that can be tested through research.",
        "Ang hypothesis ay isang mungkahing paliwanag o prediksyon tungkol sa ugnayan ng mga variable na maaaring subukan o patunayan sa pamamagitan ng pananaliksik.",
        [("hypothesis", 5), ("prediction", 3), ("proposed explanation", 4), ("testable statement", 3)],
        [("hypothesis", 5), ("haypotesis", 5), ("prediksyon", 3), ("mungkahing paliwanag", 4)],
        ("define hypothesis",),
        ("ano ang haypotesis", "kahulugan ng hypothesis", "ano ang ibig sabihin ng hypothesis"),
    ),
    _faq(
        "What is a methodology?",
        "Ano ang methodology?",
        "Research methodology refers to the methods and procedures used to conduct a research study and collect and analyze data.",
        "Ang research methodology ay tumutukoy sa mga pamamaraan at hakbang na ginagamit sa pagsasagawa ng isang pag-aaral, gayundin sa pangangalap at pagsusuri ng mga datos.",
        [("methodology", 5), ("research methods", 3), ("methods and procedures", 3), ("collect and analyze data", 3)],
        [("methodology", 5), ("metodolohiya", 5), ("pamamaraan ng pananaliksik", 4), ("pangangalap at pagsusuri ng datos", 3)],
        ("what is research methodology", "define methodology"),
        ("ano ang metodolohiya", "kahulugan ng methodology", "ano ang pamamaraan ng pananaliksik"),
    ),
    _faq(
        "What is a respondent?",
        "Ano ang respondent?",
        "A respondent is an individual who provides information or answers questions as part of a research study.",
        "Ang respondent ay isang indibidwal na nagbibigay ng impormasyon o sumasagot sa mga katanungan bilang bahagi ng isang pag-aaral.",
        [("respondent", 5), ("respondents", 5), ("answers questions", 3), ("research participant", 3)],
        [("respondent", 5), ("tagatugon", 5), ("sumasagot sa mga katanungan", 3), ("nagbibigay ng impormasyon", 3)],
        ("who is a respondent", "define respondent"),
        ("sino ang respondent", "ano ang tagatugon", "kahulugan ng respondent"),
    ),
]

FILIPINO_MARKERS = {
    "ako", "ang", "ano", "atin", "ba", "bakit", "ito", "ko", "mga",
    "ng", "para", "paano", "saan", "sino", "sa", "namin", "mo",
    "kailangan", "ibig", "kahulugan", "pananaliksik", "libre",
}


def normalize(text):
    decomposed = unicodedata.normalize("NFD", text.casefold())
    without_accents = "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", without_accents)).strip()


def _contains_phrase(normalized_text, phrase):
    normalized_phrase = normalize(phrase)
    return bool(normalized_phrase) and f" {normalized_phrase} " in f" {normalized_text} "


def _exact_match(normalized_question):
    for faq in FAQ_ENTRIES:
        for language in ("en", "fil"):
            candidates = (
                faq["questions"][language],
                *faq["phrases"][language],
            )
            if any(normalize(candidate) == normalized_question for candidate in candidates):
                return faq, language
    return None


def _keyword_match(normalized_question):
    ranked = []
    for faq in FAQ_ENTRIES:
        for language in ("en", "fil"):
            score = sum(
                weight
                for phrase, weight in faq["keywords"][language]
                if _contains_phrase(normalized_question, phrase)
            )
            if score >= KEYWORD_THRESHOLD:
                ranked.append((score, faq, language))

    ranked.sort(key=lambda result: result[0], reverse=True)
    if not ranked:
        return None
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < KEYWORD_MATCH_MARGIN:
        if ranked[0][1] is ranked[1][1]:
            language = "fil" if _is_filipino(normalized_question) else "en"
            for score, faq, _ in ranked:
                if faq is ranked[0][1] and score == ranked[0][0]:
                    return faq, language
        return None
    return ranked[0][1], ranked[0][2]


def _is_filipino(normalized_question):
    marker_count = sum(
        word in FILIPINO_MARKERS for word in normalized_question.split()
    )
    return marker_count >= 2


def _fuzzy_match(normalized_question):
    ranked = []
    for faq in FAQ_ENTRIES:
        for language in ("en", "fil"):
            question = normalize(faq["questions"][language])
            score = SequenceMatcher(None, normalized_question, question).ratio()
            ranked.append((score, faq, language))

    ranked.sort(key=lambda result: result[0], reverse=True)
    if not ranked or ranked[0][0] < FUZZY_THRESHOLD:
        return None
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < FUZZY_MATCH_MARGIN:
        return None
    return ranked[0][1], ranked[0][2]


def match_question(question):
    normalized_question = normalize(question)
    if not normalized_question:
        return {
            "answer": FALLBACK_ANSWER,
            "matched_question": None,
            "language": None,
            "match_type": "fallback",
        }

    match = _exact_match(normalized_question)
    match_type = "exact"
    if match is None:
        match = _keyword_match(normalized_question)
        match_type = "keyword"
    if match is None:
        match = _fuzzy_match(normalized_question)
        match_type = "fuzzy"
    if match is None:
        return {
            "answer": FALLBACK_ANSWER,
            "matched_question": None,
            "language": None,
            "match_type": "fallback",
        }

    faq, language = match
    return {
        "answer": faq["answers"][language],
        "matched_question": faq["questions"][language],
        "language": language,
        "match_type": match_type,
    }
