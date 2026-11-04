const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

class FakeElement {
    constructor() {
        this.value = "";
        this.textContent = "";
        this.children = [];
        this.listeners = {};
        this.attributes = {};
        this.dataset = {};
        this.style = {};
        this.classList = {
            add() {},
            remove() {},
            toggle() {},
        };
    }

    addEventListener(event, callback) {
        this.listeners[event] = callback;
    }

    append(...children) {
        this.children.push(...children);
    }

    replaceChildren(...children) {
        this.children = children;
    }

    setAttribute(name, value) {
        this.attributes[name] = value;
        if (name.startsWith("data-")) {
            const key = name
                .slice(5)
                .replace(/-([a-z])/g, (_, character) => character.toUpperCase());
            this.dataset[key] = value;
        }
    }

    select() {}

    focus() {}

    remove() {}

    matches(selector) {
        const attribute = selector.match(/^\[([^\]]+)\]$/)?.[1];
        return attribute ? attribute in this.attributes : false;
    }

    querySelector(selector) {
        return this.querySelectorAll(selector)[0];
    }

    querySelectorAll(selector) {
        return this.children.flatMap((child) => {
            if (!(child instanceof FakeElement)) return [];
            return [
                ...(child.matches(selector) ? [child] : []),
                ...child.querySelectorAll(selector),
            ];
        });
    }
}

function loadApp({ clipboardSupported = true, richClipboardWrite } = {}) {
    let fallbackClipboardText = "";
    const document = {
        getElementById() {
            return new FakeElement();
        },
        querySelector() {
            return new FakeElement();
        },
        createElement() {
            return new FakeElement();
        },
        createTextNode(text) {
            return text;
        },
        body: {
            append(input) {
                fallbackClipboardText = input.value;
            },
        },
        execCommand(command) {
            return command === "copy";
        },
    };
    const clipboard = { text: "" };
    const context = {
        URL,
        URLSearchParams,
        document,
        localStorage: {
            getItem() {
                return null;
            },
            setItem() {},
        },
        navigator: clipboardSupported
            ? {
                  clipboard: {
                      ...(richClipboardWrite
                          ? { write: richClipboardWrite }
                          : {}),
                async writeText(text) {
                    clipboard.text = text;
                },
                  },
              }
            : {},
        ClipboardItem: class ClipboardItem {
            constructor(items) {
                this.items = items;
            }
        },
        Blob,
        window: {
            setTimeout,
            clearTimeout,
            setInterval() {
                return 1;
            },
            clearInterval() {},
        },
        console,
        confirm() {
            return true;
        },
        alert() {},
    };

    vm.runInNewContext(
        fs.readFileSync(path.join(__dirname, "..", "static", "app.js"), "utf8"),
        context,
    );
    return { context, clipboard, getFallbackClipboardText: () => fallbackClipboardText };
}

test("citation selectors display the selected citation preview", () => {
    const { context } = loadApp();
    const card = context.renderPaper({
        title: "Research paper",
        authors: ["Jane Doe"],
        year: 2024,
        citations: {
            reference: "Doe, J. (2024). Research paper.",
            narrative: "Doe (2024)",
            parenthetical: "(Doe, 2024)",
        },
    });
    const tools = card.children.at(-1);
    const narrativeButton = tools.querySelectorAll("[data-citation-type]")[1];
    const preview = tools.children[1];

    narrativeButton.listeners.click();

    assert.equal(preview.hidden, false);
    assert.equal(preview.querySelector("[data-citation-preview]").textContent, "Doe (2024)");
    assert.equal(preview.dataset.selectedCitation, "narrative");
    assert.equal(
        tools.querySelectorAll("[data-citation-type]")[1].attributes["aria-pressed"],
        "true",
    );
});

test("copy button puts the previewed citation on the clipboard", async () => {
    const { context, clipboard } = loadApp();
    const card = context.renderPaper({
        title: "Research paper",
        citations: {
            reference: "Doe, J. (2024). Research paper.",
            narrative: "Doe (2024)",
            parenthetical: "(Doe, 2024)",
        },
    });
    const tools = card.children.at(-1);
    const buttons = tools.querySelectorAll("[data-citation-type]");
    const preview = tools.children[1];
    buttons[2].listeners.click();

    const copyButton = preview.querySelector("[data-copy-citation]");
    const citationButtons = tools.querySelectorAll("[data-citation-type]");
    const originalQuerySelectorAll = tools.querySelectorAll.bind(tools);
    tools.querySelectorAll = () => ({
        [Symbol.iterator]: function* () {
            yield* citationButtons;
        },
        forEach(callback) {
            citationButtons.forEach(callback);
        },
    });
    await copyButton.listeners.click();

    assert.equal(clipboard.text, "(Doe, 2024)");
    const feedback = preview.querySelector("[data-citation-feedback]");
    assert.equal(feedback.textContent, "Parenthetical copied successfully.");
    assert.equal(buttons[2].textContent, "Parenthetical");
    assert.equal(buttons[0].textContent, "Full reference");
    assert.equal(buttons[1].textContent, "Narrative");
    assert.equal(feedback.attributes.role, "status");

    tools.querySelectorAll = originalQuerySelectorAll;
    buttons[1].listeners.click();
    assert.equal(buttons[1].textContent, "Narrative");
    assert.equal(
        feedback.textContent,
        "Double-check this citation; source metadata may be incomplete.",
    );
    await preview.querySelector("[data-copy-citation]").listeners.click();
    assert.equal(feedback.textContent, "Narrative copied successfully.");
});

test("copy falls back when Clipboard API is unavailable on an HTTP LAN origin", async () => {
    const { context, getFallbackClipboardText } = loadApp({
        clipboardSupported: false,
    });

    await context.copyTextToClipboard("(Doe, 2024)");

    assert.equal(getFallbackClipboardText(), "(Doe, 2024)");
});

test("copy falls back to plain text when rich-text clipboard write fails", async () => {
    const { context, clipboard } = loadApp({
        richClipboardWrite: async () => {
            throw new Error("rich clipboard denied");
        },
    });

    await context.copyTextToClipboard(
        "Doe, J. (2024). Research paper.",
        "<em>Journal</em>",
    );

    assert.equal(clipboard.text, "Doe, J. (2024). Research paper.");
});

test("busy response cooldown disables search and shows a retry countdown", () => {
    const { context } = loadApp();
    const button = new FakeElement();
    const status = new FakeElement();

    context.startSearchCooldown(button, status);

    assert.equal(button.disabled, true);
    assert.match(status.textContent, /receiving too many requests/);
    assert.match(status.textContent, /wait 5s before trying again/);
});

test("busy cooldown backs off and respects provider Retry-After", () => {
    const { context } = loadApp();
    const button = new FakeElement();
    const status = new FakeElement();

    context.startSearchCooldown(button, status, "12");
    assert.match(status.textContent, /wait 12s before trying again/);

    context.startSearchCooldown(button, status, "3");
    assert.match(status.textContent, /wait 10s before trying again/);
});
