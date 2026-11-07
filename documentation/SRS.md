# SikLayag Software Requirements Specification

## 1. Purpose and scope

SikLayag is a browser-based educational prototype for Grade 11 students learning academic research writing. It provides research search, chapter guidance, a local writing editor, video lesson placeholders, and a prepared FAQ assistant. This document describes the current implementation; it is not a plan for unimplemented features.

## 2. Users and operating environment

- Students use the site through a modern browser on desktop or mobile.
- A maintainer runs the Flask application with Python 3.10 or later.
- Research searches require internet access to the Semantic Scholar Academic Graph API. A private API key is optional, but requests without one may be rate-limited.

## 3. Functional requirements

| ID | Requirement |
| --- | --- |
| FR-01 | The system shall display a single-page learning interface with navigation to the research search, Mga Kabanata, editor, and video lesson sections. |
| FR-02 | Users shall search Semantic Scholar by required keywords and optional start and end publication years. Search shall return up to 10 papers per page and allow loading more results up to the configured offset limit. |
| FR-03 | Search results shall show available paper metadata, abstract, source link, citation count, and APA 7 narrative, parenthetical, and reference-list citation previews with copy actions. |
| FR-04 | Users shall load the available chapter writing templates into the editor, write or edit text, view word and character counts, copy text, and clear the editor after confirmation. |
| FR-05 | The editor shall save draft text in the current browser's local storage and restore it when the page is reopened in that browser. |
| FR-06 | Users shall open lesson previews in a modal. The current video content is a placeholder and does not play lessons. |
| FR-07 | Users shall submit questions to Seeky and receive a prepared English or Filipino FAQ answer, related-question suggestions where available, or a fallback response. Seeky shall not generate novel answers. |
| FR-08 | The application shall expose a health endpoint for deployment availability checks. |

## 4. Quality and constraint requirements

- The interface shall adapt to common desktop and mobile viewport sizes.
- User drafts shall remain client-side; there is no account, server-side draft storage, or cross-device synchronization.
- Search shall handle invalid query/year/offset values with a client error and provider/network failures with an error response.
- Repeated identical search pages shall be cached in process for five minutes; outbound provider requests shall be spaced to respect rate limits.
- Third-party services and externally loaded fonts/icons/CSS require network availability.

## 5. Current limitations and exclusions

- Chapter PDF buttons display a preparation message; they do not download a PDF.
- Lesson buttons open a descriptive placeholder; animated video assets are not connected.
- The interface contains engine/aggregator labels, but academic search is currently implemented through Semantic Scholar only.
- Search availability, metadata, and rate limits depend on Semantic Scholar. Generated citations are aids and should be checked against the source.
- The FAQ content is curated in the repository and currently described as prototype content; Seeky can return the fallback when it cannot confidently match a question.
- There is no user authentication, backend database, or cloud persistence for drafts.

## 6. Acceptance summary

The current system meets this specification when the Flask page is reachable, users can use the implemented search/editor/FAQ flows described above, local editor drafts persist in the same browser, and placeholder controls are presented as such. The API health check returns `{"status":"ok"}` while the application is running.
