from . import _faq


FAQS = [
    _faq(
        "What is research?",
        "Ano ang pananaliksik?",
        "Research is a systematic process of gathering, analyzing, and interpreting information to answer questions or investigate a particular topic.",
        "Ang pananaliksik ay isang sistematikong proseso ng pangangalap, pagsusuri, at pagbibigay-kahulugan sa impormasyon upang masagot ang mga katanungan o masuri ang isang partikular na paksa.",
        [("research", 1), ("systematic process", 3), ("gathering information", 3)],
        [("pananaliksik", 2), ("sistematikong proseso", 4), ("pangangalap ng impormasyon", 4)],
        ("define research",),
        ("ano ang ibig sabihin ng pananaliksik", "kahulugan ng pananaliksik", "ipaliwanag ang pananaliksik"),
        category="research_fundamentals"
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
        category="research_fundamentals"
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
        category="research_fundamentals"
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
        category="research_fundamentals"
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
        category="research_fundamentals"
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
        category="research_fundamentals"
    ),
]
