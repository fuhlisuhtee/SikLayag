from . import _faq


FAQS = [
    _faq(
        "What is this website?",
        "Ano ang website na ito?",
        "This website is an educational platform designed to help students understand and practice academic research writing through learning materials and interactive tools.",
        "Ang website na ito ay isang platapormang pang-edukasyon na ginawa upang tulungan ang mga mag-aaral na maunawaan at maisagawa ang akademikong pananaliksik sa pamamagitan ng mga materyales sa pag-aaral at mga interactive na kagamitan.",
        [("website", 1), ("educational platform", 4), ("learning materials", 3), ("interactive tools", 3)],
        [("website", 1), ("plataporma", 4), ("pook sapot", 3), ("site", 1)],
        ("what is siklayag", "what is this site"),
        ("ano ang siklayag", "ano ang site na ito", "ano itong website"),
        category="website_features"
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
        category="website_features"
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
        category="website_features"
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
        category="website_features"
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
        category="website_features"
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
        category="website_features"
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
        category="website_features"
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
        category="website_features"
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
        category="website_features"
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
        category="website_features"
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
        category="website_features"
    ),
]
