const EDITOR_STORAGE_KEY = "siklayag.editor.v1";
let latestSearchId = 0;
let activeSearch = null;

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
    const queryInput = document.getElementById("rrl-query");
    const query = queryInput.value.trim();
    if (!query) return;
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
        showSearchError(
            error instanceof TypeError
                ? new Error("Search is temporarily unavailable.")
                : error,
            false,
        );
        results.classList.remove("hidden");
    } finally {
        if (searchId === latestSearchId) loading.classList.add("hidden");
    }
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
            throw new Error(payload.error || "Search is temporarily unavailable.");
        }
        if (
            !Array.isArray(payload.results) ||
            !Number.isInteger(payload.limit) ||
            typeof payload.has_more !== "boolean"
        ) {
            throw new Error("Search is temporarily unavailable.");
        }
        if (searchId !== latestSearchId) return;

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
        label.textContent = "Seek-y: ";
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
        appendChatMessage(payload.answer, false);
    } catch (error) {
        console.error("Hindi makuha ang sagot mula kay Seek-y.", error);
        appendChatMessage(
            "Hindi ko maiproseso ang tanong sa ngayon. Pakisubukan muli mamaya.",
            false,
        );
    } finally {
        if (submitButton) submitButton.disabled = false;
        input.focus();
    }
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
