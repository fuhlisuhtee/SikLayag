const EDITOR_STORAGE_KEY = "siklayag.editor.v1";
let latestSearchId = 0;
let activeSearch = null;
let searchCooldownTimer = null;
let searchRequestInFlight = false;
let consecutiveBusyResponses = 0;
const SEARCH_BUSY_COOLDOWN_BASE_SECONDS = 5;
const SEARCH_BUSY_COOLDOWN_MAX_SECONDS = 30;

function setSaveStatus(message, failed = false) {
    const status = document.getElementById("save-status");
    status.textContent = message;
    status.classList.toggle("text-rose-400", failed);
    status.classList.toggle("text-emerald-400", !failed);
}

function saveEditorText() {
    try {
        localStorage.setItem(
            EDITOR_STORAGE_KEY,
            document.getElementById("live-editor-text").value,
        );
        setSaveStatus("Naka-save sa browser");
    } catch (error) {
        console.error("Hindi ma-save sa browser storage.", error);
        setSaveStatus("Hindi ma-save sa browser storage", true);
    }
}

function updateWordCount() {
    const text = document.getElementById("live-editor-text").value;
    const trimmed = text.trim();
    document.getElementById("word-count").textContent = trimmed
        ? trimmed.split(/\s+/).length
        : "0";
    document.getElementById("char-count").textContent = text.length;
    saveEditorText();
}

function loadTemplateIntoEditor(chapterNum) {
    const textarea = document.getElementById("live-editor-text");
    textarea.value = templates[chapterNum] || "";
    updateWordCount();
    setSaveStatus(`Na-load ang Kabanata ${chapterNum} Template!`);
}

async function copyEditorText() {
    const text = document.getElementById("live-editor-text").value;
    try {
        await navigator.clipboard.writeText(text);
        setSaveStatus("Na-kopya sa clipboard");
    } catch (error) {
        console.error("Hindi ma-access ang clipboard.", error);
        setSaveStatus("Hindi makopya; piliin at kopyahin ang teksto", true);
    }
}

function clearEditor() {
    if (!confirm("Sigurado ka bang nais mong i-clear ang editor?")) return;
    document.getElementById("live-editor-text").value = "";
    updateWordCount();
}

function makeSearchLink(label, url) {
    const link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.className =
        "inline-flex items-center gap-1.5 px-3 py-1.5 bg-brand-blue hover:bg-blue-600 text-white text-xs font-bold rounded-lg transition-colors";
    link.textContent = label;
    return link;
}

async function copyTextToClipboard(text, html = "") {
    if (navigator.clipboard) {
        if (
            html &&
            navigator.clipboard.write &&
            typeof ClipboardItem !== "undefined"
        ) {
            try {
                await navigator.clipboard.write([
                    new ClipboardItem({
                        "text/html": new Blob([html], { type: "text/html" }),
                        "text/plain": new Blob([text], { type: "text/plain" }),
                    }),
                ]);
                return;
            } catch (error) {
                console.warn("Rich-text clipboard unavailable; trying plain text.", error);
            }
        }

        try {
            await navigator.clipboard.writeText(text);
            return;
        } catch (error) {
            console.warn("Clipboard API unavailable; trying browser copy fallback.", error);
        }
    }

    const temporaryInput = document.createElement("textarea");
    temporaryInput.value = text;
    temporaryInput.setAttribute("readonly", "");
    temporaryInput.style.position = "fixed";
    temporaryInput.style.opacity = "0";
    document.body.append(temporaryInput);
    temporaryInput.focus();
    temporaryInput.select();
    let copied;
    try {
        copied = document.execCommand("copy");
    } finally {
        temporaryInput.remove();
    }
    if (!copied) throw new Error("Clipboard copy is unavailable.");
}

function makeCitationButton(label, type, tools, citation) {
    const button = document.createElement("button");
    button.type = "button";
    button.className =
        "px-2.5 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-semibold rounded-lg transition-colors";
    button.textContent = label;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => {
        tools.querySelectorAll("[data-citation-type]").forEach((option) => {
            option.setAttribute("aria-pressed", String(option === button));
        });
        const panel = tools.querySelector("[data-citation-panel]");
        panel.hidden = false;
        panel.classList.remove("hidden");
        panel.querySelector("[data-citation-preview]").textContent = citation;
        panel.dataset.selectedCitation = type;
        panel.querySelector("[data-copy-citation]").disabled = !citation;
        const feedback = panel.querySelector("[data-citation-feedback]");
        feedback.textContent =
            "Double-check this citation; source metadata may be incomplete.";
        feedback.classList.remove("text-emerald-300", "text-rose-300");
        feedback.classList.add("text-slate-400");
    });
    button.setAttribute("data-citation-type", type);
    button.dataset.citationLabel = label;
    return button;
}

function makeCitationTools(paper) {
    const citations = paper.citations || {};
    const tools = document.createElement("div");
    tools.className =
        "mt-2 pt-2 border-t border-slate-700 space-y-2";

    const options = document.createElement("div");
    options.className = "flex flex-wrap items-center gap-2";
    const label = document.createElement("span");
    label.className = "text-xs text-slate-400";
    label.textContent = "APA 7:";
    options.append(
        label,
        makeCitationButton("Full reference", "reference", tools, citations.reference || ""),
        makeCitationButton("Narrative", "narrative", tools, citations.narrative || ""),
        makeCitationButton(
            "Parenthetical",
            "parenthetical",
            tools,
            citations.parenthetical || "",
        ),
    );

    const preview = document.createElement("div");
    preview.className = "hidden rounded-lg bg-slate-900 p-2 space-y-1.5";
    preview.hidden = true;
    preview.setAttribute("data-citation-panel", "");
    const previewText = document.createElement("p");
    previewText.className = "text-xs text-slate-200 leading-snug break-words";
    previewText.setAttribute("data-citation-preview", "");
    const copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className =
        "px-2.5 py-1 bg-brand-blue hover:bg-sky-500 text-white text-xs font-bold rounded-lg transition-colors disabled:opacity-50";
    copyButton.textContent = "Copy citation";
    copyButton.setAttribute("data-copy-citation", "");
    const disclaimer = document.createElement("p");
    disclaimer.className = "text-[10px] leading-tight text-slate-400";
    disclaimer.textContent =
        "Double-check this citation; source metadata may be incomplete.";
    disclaimer.setAttribute("role", "status");
    disclaimer.setAttribute("data-citation-feedback", "");
    copyButton.addEventListener("click", async () => {
        try {
            const referenceHtml =
                preview.dataset.selectedCitation === "reference"
                    ? citations.reference_html || ""
                    : "";
            await copyTextToClipboard(previewText.textContent, referenceHtml);
            const selectedButton = Array.from(
                tools.querySelectorAll("[data-citation-type]"),
            )
                .find(
                    (button) =>
                        button.dataset.citationType ===
                        preview.dataset.selectedCitation,
                );
            disclaimer.textContent = `${selectedButton.dataset.citationLabel} copied successfully.`;
            disclaimer.classList.remove("text-slate-400", "text-rose-300");
            disclaimer.classList.add("text-emerald-300");
        } catch (error) {
            console.error("Hindi makopya ang citation.", error);
            disclaimer.textContent =
                "Copy unavailable; please select and copy the citation manually.";
            disclaimer.classList.remove("text-emerald-300", "text-slate-400");
            disclaimer.classList.add("text-rose-300");
        }
    });
    const copyActions = document.createElement("div");
    copyActions.className = "flex flex-wrap items-center gap-x-2 gap-y-1";
    copyActions.append(copyButton, disclaimer);
    preview.append(previewText, copyActions);
    tools.append(options, preview);
    return tools;
}

function renderPaper(paper) {
    const card = document.createElement("article");
    card.className =
        "bg-slate-800 p-4 rounded-2xl border border-slate-700 hover:border-brand-sky transition-colors";

    const title = document.createElement("h3");
    title.className = "font-bold text-white text-sm mb-1";
    title.textContent = paper.title || "Title unavailable";

    const abstract = document.createElement("p");
    abstract.className = "text-sm text-slate-300 leading-relaxed mb-3";
    abstract.textContent = paper.abstract
        ? `${paper.abstract.slice(0, 600)}${paper.abstract.length > 600 ? "..." : ""}`
        : "Abstract unavailable.";

    const authors = document.createElement("p");
    authors.className = "text-xs text-slate-400 mb-2";
    authors.textContent = paper.authors?.join(", ") || "Hindi nakalista ang mga may-akda";

    const details = [];
    if (paper.year) details.push(String(paper.year));
    if (paper.venue) details.push(paper.venue);
    if (paper.publication_types?.length) {
        details.push(paper.publication_types.join(", "));
    }
    if (Number.isInteger(paper.citation_count)) {
        details.push(`${paper.citation_count} citations`);
    }
    const metadata = document.createElement("p");
    metadata.className = "text-xs text-slate-300 mb-3";
    metadata.textContent = details.join(" · ") || "Publication details unavailable.";

    card.append(title, authors, abstract, metadata);
    if (safeHttpUrl(paper.url)) {
        card.append(makeSearchLink("Buksan ang papel", paper.url));
    }
    card.append(makeCitationTools(paper));
    return card;
}

function safeHttpUrl(value) {
    try {
        const url = new URL(value);
        return url.protocol === "https:" || url.protocol === "http:";
    } catch {
        return false;
    }
}

async function handleSearch(event) {
    event.preventDefault();
    if (searchRequestInFlight || searchCooldownTimer) return;
    const queryInput = document.getElementById("rrl-query");
    const query = queryInput.value.trim();
    if (!query) return;
    const searchButton = document.getElementById("rrl-search-button");
    const searchStatus = document.getElementById("search-button-status");
    searchRequestInFlight = true;
    searchButton.disabled = true;
    searchButton.classList.add("opacity-50", "cursor-not-allowed");
    searchStatus.textContent = "";
    searchStatus.classList.add("hidden");
    const searchId = ++latestSearchId;
    activeSearch = {
        query,
        startYear: document.getElementById("start-year").value,
        endYear: document.getElementById("end-year").value,
        nextOffset: 0,
    };

    const initial = document.getElementById("initial-search-state");
    const loading = document.getElementById("loading-state");
    const results = document.getElementById("results-list");
    const loadMore = document.getElementById("load-more-results");
    initial.classList.add("hidden");
    results.classList.add("hidden");
    results.replaceChildren();
    loadMore.classList.add("hidden");
    loadMore.disabled = false;
    loading.classList.remove("hidden");

    try {
        await loadSearchPage(0, searchId);
    } catch (error) {
        if (searchId !== latestSearchId) return;
        if (error.status === 503) {
            startSearchCooldown(searchButton, searchStatus, error.retryAfter);
        } else {
            searchStatus.classList.add("hidden");
        }
        showSearchError(
            error instanceof TypeError
                ? new Error("Search is temporarily unavailable.")
                : error,
            false,
        );
        results.classList.remove("hidden");
    } finally {
        if (searchId === latestSearchId) {
            loading.classList.add("hidden");
            if (!searchCooldownTimer) {
                searchButton.disabled = false;
                searchButton.classList.remove("opacity-50", "cursor-not-allowed");
                searchStatus.classList.add("hidden");
                searchStatus.textContent = "";
            }
            searchRequestInFlight = false;
        }
    }
}

function startSearchCooldown(button, status, retryAfter = null) {
    const backoffSeconds = Math.min(
        SEARCH_BUSY_COOLDOWN_BASE_SECONDS * 2 ** consecutiveBusyResponses,
        SEARCH_BUSY_COOLDOWN_MAX_SECONDS,
    );
    consecutiveBusyResponses += 1;
    const providerRetrySeconds = Number(retryAfter);
    const cooldownSeconds = Math.max(
        backoffSeconds,
        Number.isFinite(providerRetrySeconds) && providerRetrySeconds > 0
            ? providerRetrySeconds
            : 0,
    );
    const expiresAt = Date.now() + cooldownSeconds * 1000;
    status.classList.remove("hidden");
    button.disabled = true;
    if (searchCooldownTimer) window.clearInterval(searchCooldownTimer);

    const updateCooldown = () => {
        const remaining = Math.ceil((expiresAt - Date.now()) / 1000);
        if (remaining <= 0) {
            window.clearInterval(searchCooldownTimer);
            searchCooldownTimer = null;
            button.disabled = false;
            button.classList.remove("opacity-50", "cursor-not-allowed");
            status.classList.add("hidden");
            status.textContent = "";
            return;
        }
        status.textContent =
            `The search service is receiving too many requests. Please wait ${remaining}s before trying again.`;
    };

    updateCooldown();
    searchCooldownTimer = window.setInterval(updateCooldown, 250);
}

async function loadSearchPage(offset, searchId) {
    const loading = document.getElementById("loading-state");
    const loadingMessage = document.getElementById("loading-message");
    const results = document.getElementById("results-list");
    const loadMore = document.getElementById("load-more-results");
    const params = new URLSearchParams({
        q: activeSearch.query,
        offset: String(offset),
    });
    if (activeSearch.startYear) params.set("start_year", activeSearch.startYear);
    if (activeSearch.endYear) params.set("end_year", activeSearch.endYear);

    loadingMessage.textContent = "Searching Semantic Scholar...";
    loading.classList.remove("hidden");
    if (offset > 0) {
        loadMore.disabled = true;
        loadMore.textContent = "Loading...";
    }
    const queuedMessageTimer = window.setTimeout(() => {
        if (searchId === latestSearchId) {
            loadingMessage.textContent = "Search is queued; please wait.";
        }
    }, 700);

    try {
        const response = await fetch(`/api/search?${params.toString()}`);
        let payload;
        try {
            payload = await response.json();
        } catch {
            throw new Error("Search is temporarily unavailable.");
        }
        if (!response.ok) {
            const error = new Error(
                payload.error || "Search is temporarily unavailable.",
            );
            error.status = response.status;
            error.retryAfter = response.headers.get("Retry-After");
            throw error;
        }
        if (
            !Array.isArray(payload.results) ||
            !Number.isInteger(payload.limit) ||
            typeof payload.has_more !== "boolean"
        ) {
            throw new Error("Search is temporarily unavailable.");
        }
        if (searchId !== latestSearchId) return;
        if (offset === 0) consecutiveBusyResponses = 0;

        results.querySelectorAll('[role="alert"]').forEach((message) => message.remove());
        if (offset === 0 && payload.results.length === 0) {
            const empty = document.createElement("p");
            empty.className = "text-sm text-slate-300 text-center py-4";
            empty.textContent = "No papers found for your search.";
            results.append(empty);
        } else {
            payload.results.forEach((paper) => results.append(renderPaper(paper)));
        }
        activeSearch.nextOffset = offset + payload.limit;
        loadMore.classList.toggle("hidden", !payload.has_more);
        loadMore.textContent = "Load More";
        results.classList.remove("hidden");
    } finally {
        window.clearTimeout(queuedMessageTimer);
        if (searchId === latestSearchId) {
            loading.classList.add("hidden");
            loadMore.disabled = false;
            if (loadMore.textContent === "Loading...") {
                loadMore.textContent = "Load More";
            }
        }
    }
}

function showSearchError(error, append) {
    const results = document.getElementById("results-list");
    if (!append) results.replaceChildren();
    const message = document.createElement("p");
    message.className = "text-sm text-rose-300 text-center py-4";
    message.setAttribute("role", "alert");
    message.textContent = error.message || "Search is temporarily unavailable.";
    results.append(message);
}

async function handleLoadMore() {
    if (!activeSearch) return;
    const searchId = latestSearchId;
    try {
        await loadSearchPage(activeSearch.nextOffset, searchId);
    } catch (error) {
        if (searchId !== latestSearchId) return;
        showSearchError(
            error instanceof TypeError
                ? new Error("Search is temporarily unavailable.")
                : error,
            true,
        );
    }
}

function toggleChat() {
    document.getElementById("chat-box").classList.toggle("hidden");
}

function appendChatMessage(message, isUser) {
    const bubble = document.createElement("div");
    bubble.className = isUser
        ? "bg-brand-blue text-white p-3 rounded-2xl shadow-sm text-xs leading-relaxed max-w-[85%] ml-auto"
        : "bg-white p-3 rounded-2xl border border-slate-200 shadow-sm text-slate-700 leading-relaxed max-w-[85%]";
    if (!isUser) {
        const label = document.createElement("strong");
        label.textContent = "Seeky: ";
        bubble.append(label);
    }
    bubble.append(document.createTextNode(message));
    const messages = document.getElementById("chat-messages");
    messages.append(bubble);
    messages.scrollTop = messages.scrollHeight;
}

async function handleChatSubmit(event) {
    event.preventDefault();
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;

    appendChatMessage(message, true);
    input.value = "";
    const submitButton = event.submitter;
    if (submitButton) submitButton.disabled = true;
    try {
        const response = await fetch("/api/seeky", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: message }),
        });
        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.error || "Hindi maiproseso ang tanong.");
        }
        updateChatDisclaimer(payload.language);
        appendChatMessage(payload.answer, false);
        appendSuggestedQuestions(payload.suggested_questions, payload.language);
    } catch (error) {
        console.error("Hindi makuha ang sagot mula kay Seeky.", error);
        appendChatMessage(
            "Hindi ko maiproseso ang tanong sa ngayon. Pakisubukan muli mamaya.",
            false,
        );
    } finally {
        if (submitButton) submitButton.disabled = false;
        input.focus();
    }
}

function updateChatDisclaimer(language) {
    const disclaimer = document.getElementById("chat-disclaimer");
    disclaimer.textContent =
        language === "fil"
            ? "Maaari pa ring magkamali si Seeky, kaya tiyaking suriin muli ang mahahalagang impormasyon."
            : "Seeky can still make mistakes, so please double-check important information.";
}

function appendSuggestedQuestions(questions, language) {
    if (!Array.isArray(questions) || questions.length === 0) return;

    const messages = document.getElementById("chat-messages");
    const suggestions = document.createElement("div");
    suggestions.className = "space-y-2 text-xs";
    const prompt = document.createElement("p");
    prompt.className = "text-slate-500";
    prompt.textContent =
        language === "fil"
            ? "Gusto mo pa bang malaman ang tungkol sa?"
            : "Would you like to know more about?";
    suggestions.append(prompt);

    questions.forEach((question) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className =
            "block w-full rounded-xl border border-brand-blue/20 bg-white px-3 py-2 text-left text-brand-blue hover:bg-blue-50";
        button.textContent = question;
        button.addEventListener("click", () => {
            const input = document.getElementById("chat-input");
            input.value = question;
            input.form.requestSubmit();
        });
        suggestions.append(button);
    });

    messages.append(suggestions);
    messages.scrollTop = messages.scrollHeight;
}

function openVideoModal(title, _url, description) {
    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-desc").textContent = description;
    document.getElementById("video-modal").classList.remove("hidden");
}

function closeVideoModal() {
    document.getElementById("video-modal").classList.add("hidden");
}

function downloadPDF(filename) {
    alert(`Salamat sa pag-click! Ang PDF template na "${filename}" ay inihahanda pa.`);
}

document.getElementById("rrl-form").addEventListener("submit", handleSearch);
document.getElementById("load-more-results").addEventListener("click", handleLoadMore);
document.getElementById("live-editor-text").addEventListener("input", updateWordCount);
document
    .querySelector("#chat-box form")
    .addEventListener("submit", handleChatSubmit);

try {
    document.getElementById("live-editor-text").value =
        localStorage.getItem(EDITOR_STORAGE_KEY) || "";
} catch (error) {
    console.error("Hindi mabasa ang browser storage.", error);
    setSaveStatus("Hindi mabasa ang browser storage", true);
}
updateWordCount();
