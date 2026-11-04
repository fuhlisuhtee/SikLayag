"""Generate APA 7 citations from normalized Semantic Scholar paper data."""

from html import escape
import re
from collections.abc import Mapping, Sequence


_UNAVAILABLE_TITLES = {"", "title unavailable", "untitled work", "[title unavailable]"}


def _clean_text(value):
    return value.strip() if isinstance(value, str) else ""


def _author_parts(name):
    name = _clean_text(name)
    if not name:
        return "", []
    if "," in name:
        surname, given_names = name.split(",", 1)
        return surname.strip(), re.findall(r"[^\s-]+", given_names)

    parts = name.split()
    if len(parts) == 1:
        return parts[0], []
    return parts[-1], parts[:-1]


def _author_surname(name):
    surname, _ = _author_parts(name)
    return surname or _clean_text(name)


def _format_author(name):
    surname, given_names = _author_parts(name)
    if not surname:
        return _clean_text(name)
    initials = " ".join(f"{part[0].upper()}." for part in given_names if part)
    return f"{surname}, {initials}" if initials else surname


def _format_reference_authors(authors):
    formatted = [_format_author(author) for author in authors]
    if len(formatted) > 20:
        return f"{', '.join(formatted[:19])}, ..., {formatted[-1]}"
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]}, & {formatted[1]}"
    return f"{', '.join(formatted[:-1])}, & {formatted[-1]}"


def _normalized_authors(paper):
    raw_authors = paper.get("authors")
    if not isinstance(raw_authors, Sequence) or isinstance(
        raw_authors, (str, bytes)
    ):
        return []
    return [
        author.strip()
        for author in raw_authors
        if isinstance(author, str) and author.strip()
    ]


def _title(paper):
    title = _clean_text(paper.get("title"))
    return title if title.casefold() not in _UNAVAILABLE_TITLES else "[Title unavailable]"


def _year(paper):
    year = paper.get("year")
    if isinstance(year, int) and not isinstance(year, bool):
        return str(year)
    return "n.d."


def _short_citation_title(title):
    words = title.split()
    if len(words) <= 5:
        return title
    return f"{' '.join(words[:5])}..."


def _doi_url(value):
    doi = _clean_text(value)
    if not doi:
        return ""
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    return f"https://doi.org/{doi}"


def _reference_html(paper, authors, title, year):
    if authors:
        parts = [
            f"{escape(_format_reference_authors(authors))} ({escape(year)}).",
            f"{escape(title)}.",
        ]
    else:
        parts = [f"{escape(title)} ({escape(year)})."]

    journal = _clean_text(paper.get("venue"))
    volume = _clean_text(paper.get("volume"))
    issue = _clean_text(paper.get("issue"))
    pages = _clean_text(paper.get("pages"))
    if journal:
        italicized = escape(journal)
        if volume:
            italicized += f", {escape(volume)}"
        journal_part = f"<em>{italicized}</em>"
        if volume and issue:
            journal_part += f"({escape(issue)})"
        if pages:
            journal_part += f", {escape(pages)}"
        parts.append(f"{journal_part}.")

    doi_url = _doi_url(paper.get("doi"))
    if doi_url:
        parts.append(escape(doi_url))
    return " ".join(parts)


def generate_apa7_citations(paper: Mapping):
    """Return reference-list, narrative, and parenthetical APA 7 citation text."""
    authors = _normalized_authors(paper)
    title = _title(paper)
    year = _year(paper)
    has_title = title != "[Title unavailable]"

    if authors:
        author_text = _format_reference_authors(authors)
        narrative_author = _author_surname(authors[0])
        parenthetical_author = narrative_author
        if len(authors) > 1:
            narrative_author += " et al." if len(authors) > 2 else f" and {_author_surname(authors[1])}"
            parenthetical_author += " et al." if len(authors) > 2 else f" & {_author_surname(authors[1])}"
        narrative = f"{narrative_author} ({year})"
        parenthetical = f"({parenthetical_author}, {year})"
        reference_parts = [f"{author_text} ({year}).", f"{title}."]
    else:
        citation_title = title if has_title else "[Title unavailable]"
        in_text_title = f'"{_short_citation_title(citation_title)}"'
        narrative = f"{in_text_title} ({year})"
        parenthetical = f"({in_text_title}, {year})"
        reference_parts = [f"{citation_title} ({year})."]

    journal = _clean_text(paper.get("venue"))
    volume = _clean_text(paper.get("volume"))
    issue = _clean_text(paper.get("issue"))
    pages = _clean_text(paper.get("pages"))
    if journal:
        journal_part = journal
        if volume:
            journal_part += f", {volume}"
            if issue:
                journal_part += f"({issue})"
        if pages:
            journal_part += f", {pages}"
        reference_parts.append(f"{journal_part}.")

    doi_url = _doi_url(paper.get("doi"))
    if doi_url:
        reference_parts.append(doi_url)

    return {
        "reference": " ".join(reference_parts),
        "reference_html": _reference_html(paper, authors, title, year),
        "narrative": narrative,
        "parenthetical": parenthetical,
    }
