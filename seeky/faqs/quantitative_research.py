from . import _faq


FAQS = [
    _faq(
        "What is quantitative research?",
        "Ano ang quantitative research?",
        "Quantitative research focuses on collecting and analyzing numerical data to identify patterns, relationships, or measurable results.",
        "Ang quantitative research ay nakatuon sa pangangalap at pagsusuri ng mga numerikal na datos upang matukoy ang mga pattern, ugnayan, o mga resultang maaaring masukat.",
        [("quantitative research", 5), ("quantitative", 4), ("numerical data", 4), ("statistics", 3), ("measurement", 3), ("numbers", 3)],
        [("quantitative research", 5), ("kwantitatibong pananaliksik", 5), ("numerikal na datos", 4), ("estadistika", 3), ("pagsukat", 3), ("bilang", 3)],
        ("define quantitative research", "explain quantitative research", "what does quantitative mean"),
        ("ano ang kwantitatibong pananaliksik", "kahulugan ng kwantitatibong pananaliksik"),
        category="quantitative_research"
    ),
    _faq(
        "What is a variable?",
        "Ano ang variable?",
        "A variable is a characteristic, factor, or element that can change or take different values in a research study.",
        "Ang variable ay isang katangian, salik, o elemento na maaaring magbago o magkaroon ng iba't ibang halaga sa isang pag-aaral.",
        [("variable", 5), ("variables", 5), ("independent variable", 4), ("dependent variable", 4), ("factors", 3), ("measurement", 3), ("factor that changes", 3), ("different values", 3)],
        [("variable", 5), ("baryabol", 5), ("baryabol na independiyente", 4), ("baryabol na di dependiyente", 4), ("salik", 3), ("pagsukat", 3), ("salik na nagbabago", 3), ("ibat ibang halaga", 3)],
        ("define variable", "what are variables in research"),
        ("ano ang ibig sabihin ng variable", "kahulugan ng variable"),
        category="quantitative_research"
    ),
    _faq(
        "What is a survey?",
        "Ano ang sarbey?",
        "A survey is a data collection method that gathers information from people through a set of questions, often using questionnaires.",
        "Ang sarbey ay isang paraan ng pangangalap ng datos na kumukuha ng impormasyon mula sa mga tao sa pamamagitan ng isang hanay ng mga tanong, kadalasang gamit ang talatanungan.",
        [("survey", 5), ("questionnaire", 5), ("responses", 3), ("respondents", 3), ("data collection", 3)],
        [("sarbey", 5), ("talatanungan", 5), ("mga sagot", 3), ("respondente", 3), ("pangangalap ng datos", 3)],
        ("survey questionnaire", "survey as a data collection method"),
        ("sarbey bilang paraan ng pangangalap ng datos",),
        category="quantitative_research"
    ),
    _faq(
        "What is statistical analysis?",
        "Ano ang statistical analysis?",
        "Statistical analysis is the process of organizing, examining, and interpreting numerical data using statistical techniques to identify patterns or draw conclusions.",
        "Ang statistical analysis ay proseso ng pag-aayos, pagsusuri, at pagbibigay-kahulugan sa numerikal na datos gamit ang mga pamamaraang estadistikal upang matukoy ang mga padron o makabuo ng konklusyon.",
        [("statistical analysis", 5), ("statistics", 4), ("data analysis", 4), ("numerical data", 3), ("computation", 3)],
        [("statistical analysis", 5), ("pagsusuring estadistikal", 5), ("estadistika", 4), ("pagsusuri ng datos", 4), ("numerikal na datos", 3), ("pagkukuwenta", 3)],
        ("analyzing numerical data statistically", "statistical data analysis"),
        ("pagsusuring estadistikal ng datos",),
        category="quantitative_research"
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
        category="quantitative_research"
    ),
]
