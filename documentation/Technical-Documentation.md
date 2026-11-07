# SikLayag Technical Documentation

## 1. System overview

SikLayag is a Flask-served single-page web application. Flask renders `templates/Siklayag.html` and provides JSON endpoints. Browser behavior is implemented in `static/app.js` and inline page scripts; styling is in `static/styles.css` with Tailwind CSS, Font Awesome, and Google Fonts loaded from CDNs.

## 2. Components

| Component | Responsibility |
| --- | --- |
| `app.py` | Flask routes, search input validation, Semantic Scholar requests, result normalization, in-process cache/rate limiter, FAQ endpoint, health check. |
| `citation_generator.py` | Builds APA 7 reference-list, narrative, and parenthetical citation text and HTML from normalized paper metadata. |
| `seeky/preprocessing.py` | Normalizes questions, removes common stop words, recognizes FAQ phrases, and identifies Filipino language markers. |
| `seeky/matcher.py` | Applies exact, weighted keyword, typo-tolerant fuzzy, and topic matching with ambiguity thresholds. |
| `seeky/chatbot.py` | Handles greetings/farewells, selects matching FAQ responses or fallback, and returns related questions. |
| `seeky/faqs/` | Stores bilingual prepared FAQ content by topic category; related suggestions come from the matched category. |
| `templates/Siklayag.html` | Page structure, feature copy, chapter templates, and video/chat modals. |
| `static/app.js` | Search UI and pagination, citation display/copy, local editor persistence/counts, and Seeky chat requests. |
| `static/styles.css` | Additional page styling. |

## 3. Request flow and endpoints

| Method and path | Behavior |
| --- | --- |
| `GET /` | Renders the main page and supplies the current year for year-filter controls. |
| `GET /api/health` | Returns `{"status":"ok"}` for health checks. |
| `GET /api/search?q=...&start_year=...&end_year=...&offset=...` | Validates inputs, calls Semantic Scholar when needed, normalizes results, generates APA citations, and returns JSON results. |
| `POST /api/seeky` | Accepts JSON `{ "question": "..." }`; returns answer, matched FAQ, language, match type, and suggestions. |

Search requires a non-empty query of at most 300 characters. Years, when supplied, must be between 1800 and the current year, and start year cannot exceed end year. Offset must be a multiple of 10 from 0 through 1000. Search requests ask for up to 10 papers at a time. Identical concurrent cache misses are coalesced; search cache entries last 300 seconds and the cache holds at most 256 entries. Provider calls are serialized with a minimum 1.1-second interval. These controls are process-local.

The backend reads `SEMANTIC_SCHOLAR_API_KEY` from the environment and sends it only to Semantic Scholar in the `x-api-key` header. It maps provider failures to API errors and forwards `Retry-After` when available. The browser applies a retry cooldown after a rate-limit response.

## 4. Data and persistence

- Paper metadata and abstracts come from Semantic Scholar; search results are not stored in a database.
- Draft text is stored under the browser local-storage key `siklayag.editor.v1`. It is isolated to that browser profile and origin. Clearing browser site data removes it.
- FAQ questions, bilingual answers, keywords, and phrases are source-controlled Python data. No generative AI service is used.

## 5. Configuration and deployment

- `SEMANTIC_SCHOLAR_API_KEY`: optional API credential; configure as a private environment variable in hosted environments.
- `PORT`: optional listening port; defaults to `5000`.
- `FLASK_DEBUG`: set to `true` only for local development to enable Flask debug mode.
- `render.yaml` and `Procfile` contain starter Gunicorn commands. Gunicorn is configured for one worker and eight threads so the process-local provider limiter is shared within that instance. Multiple app instances do not share cache or rate-limiting state.

## 6. External dependencies and operational notes

Python packages are listed in `requirements.txt`: Flask, Gunicorn, python-dotenv, and RapidFuzz. The page also loads Tailwind CSS, Font Awesome, and Google Fonts from CDNs. Semantic Scholar availability and unauthenticated request quotas are outside the application's control. Verify generated citations against the original publication.
