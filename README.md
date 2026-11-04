# SikLayag

**An Educational Platform for Academic Research Writing**

SikLayag is a web-based educational platform designed to help students
understand and navigate the process of academic research writing. It provides
learning materials, research tools, and interactive features that support
students throughout different stages of developing a research paper.

The platform aims to make research writing more accessible and manageable
through guided lessons, academic literature discovery, and structured writing
assistance.

## Features

SikLayag is under development and currently includes these features:

### 1. Animated Video Lessons

Educational video lessons covering topics related to academic research writing.
Video content is still a prototype placeholder.

### 2. RRL Seek Engine

Searches academic papers using keywords and optional publication-year filters
through the **Semantic Scholar Academic Graph API**. The first version shows up
to ten relevant results per page with paper metadata, abstracts, and a link to
the paper. Each result can preview and copy an APA 7 narrative, parenthetical,
or reference-list citation.

### 3. Mga Kabanata

Learning materials and guides that introduce students to the different
chapters of a research paper. Chapter PDF downloads are still placeholders.

### 4. Interactive Research Editor

A guided writing environment where students can organize and develop research
content using predefined chapter structures. Drafts are stored in the current
browser with `localStorage`; they are not uploaded or synchronized.

### 5. Seeky

An FAQ-based assistant that matches questions to prepared answers about
academic research writing and the platform. It supports English and Filipino
answers, keyword preprocessing with recognized topic phrases, typo-tolerant
RapidFuzz matching, curated related-question suggestions, and friendly greeting
and farewell replies. A persistent chat-footer reminder encourages students to
double-check information; the reminder is kept separate from FAQ answers.
Seeky does not generate answers.

## Technology Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **FAQ matching:** Prepared Python FAQ entries and RapidFuzz
- **Academic search:** Semantic Scholar Academic Graph API
- **Version control:** Git and GitHub

Seeky's matching code is organized under [`seeky/`](./seeky/): preprocessing
and matching logic are separate from the chat response flow, while bilingual
FAQ entries live in category modules under [`seeky/faqs/`](./seeky/faqs/).
Suggested questions are selected from the matched FAQ's category, so adding
FAQs to a category also extends its related suggestions. The current FAQ text
is placeholder content for testing; replace it with the approved FAQ material
when it becomes available.

## Project Status

![In Development](https://img.shields.io/badge/status-in%20development-yellow)

SikLayag is under active development. Features, functionality, and interface
components are being implemented and tested. Content and final requirements
will be provided by the client.

## Getting Started

### Requirements

- Python 3.10 or later
- Git

### Run locally on Windows

1. Clone the repository and enter the project folder:

   ```powershell
   git clone https://github.com/fuhlisuhtee/SikLayag.git
   cd SikLayag
   ```

2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create your local environment file and add your Semantic Scholar key:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

   Set `SEMANTIC_SCHOLAR_API_KEY` in `.env`. The `.env` file is ignored by Git;
   **never commit or share it**. Keep the key out of source code, screenshots,
   and chat messages. The API key is optional, but unauthenticated requests may
   be rate-limited by Semantic Scholar.

5. Start the Flask development server:

   ```powershell
   py app.py
   ```

6. Open <http://127.0.0.1:5000>.

Check that the server is available at <http://127.0.0.1:5000/api/health>.

## Tests

Run the Flask and Seeky tests with:

```powershell
py -m unittest discover -s tests -v
```

Check the browser JavaScript syntax with:

```powershell
node --check static\app.js
```

Run the APA citation formatting and copy tests with:

```powershell
node --test tests\test_citations.js
```

## API Integration

The Flask server calls the Semantic Scholar Academic Graph API so the API key
is not exposed to browser JavaScript. Searches accept keywords and optional
publication-year bounds, request ten results per page, and cache identical
search pages in the Flask process for five minutes to reduce repeated requests.
Paper metadata is normalized when Semantic Scholar omits titles, abstracts,
authors, publication details, or links. The frontend displays abstracts and
provides a Load More button rather than fetching all matches at once.
Each result includes citation-type selectors that reveal the full citation
preview and a separate Copy button. Clipboard copying uses the Clipboard API
when available and falls back to a plain-text copy for local HTTP/LAN access.
APA 7 journal reference formatting is
implemented in `citation_generator.py`; the API requests publication type,
journal, DOI, and citation-count metadata. Missing publication years use APA's
`n.d.`, and missing authors use the title in the author position. Generated
citations should still be verified against the original source.
Provider requests are serialized and spaced at least 1.1 seconds apart to stay
below the API key's one-request-per-second limit. Identical concurrent cache
misses are coalesced, and the configured Gunicorn setup uses one worker with
multiple threads so requests in that deployment share the same limiter.
After a provider rate-limit response, the search button enforces a five-second
cooldown, honors `Retry-After` when supplied, and increases the delay on
repeated rate-limit responses up to 30 seconds. A successful search resets the
backoff.

The limiter and cache are process-local. Keep the app to one instance to
preserve the provider limit; if deploying multiple instances, use a shared
rate-limit coordinator such as Redis before scaling out. Provider availability
and unauthenticated rate limits are controlled by Semantic Scholar.

For hosted deployments, configure `SEMANTIC_SCHOLAR_API_KEY` as a private
environment variable in the hosting provider's dashboard. Do not upload `.env`
or add the key to GitHub.

## Deployment

Deployment is not configured yet. The repository includes starter
configurations for [Render](./render.yaml) and [Railway](./Procfile); the
deployment provider is still being evaluated. Configure the API key as a
provider secret before enabling hosted search.

## Notes

- This platform is intended for educational use.
- Academic paper availability and metadata depend on the external API.
- Some content and features are placeholders and will be updated as
  requirements are finalized.
- The current page uses the Tailwind CSS CDN to preserve the prototype design;
  compile and serve Tailwind locally before production deployment.

---

**SikLayag**
*Making the journey of academic research writing easier to navigate.*
