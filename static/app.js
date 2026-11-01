const EDITOR_STORAGE_KEY = "siklayag.editor.v1";
let latestSearchId = 0;

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
    title.textContent = paper.title;

    const authors = document.createElement("p");
    authors.className = "text-xs text-slate-400 mb-2";
    authors.textContent = paper.authors?.join(", ") || "Hindi nakalista ang mga may-akda";

    const year = document.createElement("p");
    year.className = "text-xs text-slate-300 mb-3";
    year.textContent = paper.year || "Hindi nakalista ang taon ng publikasyon";

    card.append(title, authors, year);
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
    const params = new URLSearchParams({ q: query });
    const startYear = document.getElementById("start-year").value;
    const endYear = document.getElementById("end-year").value;
    if (startYear) params.set("start_year", startYear);
    if (endYear) params.set("end_year", endYear);

    const initial = document.getElementById("initial-search-state");
    const loading = document.getElementById("loading-state");
    const results = document.getElementById("results-list");
    initial.classList.add("hidden");
    results.classList.add("hidden");
    results.replaceChildren();
    loading.classList.remove("hidden");

    try {
        const response = await fetch(`/api/search?${params.toString()}`);
        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.error || "Hindi makumpleto ang paghahanap.");
        }
        if (searchId !== latestSearchId) return;

        if (!payload.results.length) {
            const empty = document.createElement("p");
            empty.className = "text-sm text-slate-300 text-center py-4";
            empty.textContent = "Walang nahanap na papel. Subukan ang ibang mga keyword.";
            results.append(empty);
        } else {
            payload.results.forEach((paper) => results.append(renderPaper(paper)));
        }
        results.classList.remove("hidden");
    } catch (error) {
        if (searchId !== latestSearchId) return;
        const message = document.createElement("p");
        message.className = "text-sm text-rose-300 text-center py-4";
        message.setAttribute("role", "alert");
        message.textContent = error.message || "Hindi makumpleto ang paghahanap.";
        results.append(message);
        results.classList.remove("hidden");
    } finally {
        if (searchId === latestSearchId) loading.classList.add("hidden");
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
