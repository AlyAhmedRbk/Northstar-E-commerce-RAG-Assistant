document.addEventListener("DOMContentLoaded", () => {
    const $ = (selector) => document.querySelector(selector);
    const $$ = (selector) => [...document.querySelectorAll(selector)];

    const elements = {
        panel: $("#chat-panel"),
        launcher: $("#chat-launcher"),
        close: $("#chat-close"),
        form: $("#chat-form"),
        input: $("#question-input"),
        send: $("#send-button"),
        messages: $("#chat-messages"),
        intro: $("#chat-intro"),
        error: $("#chat-error"),
        status: $("#assistant-status"),
        themeToggle: $("#theme-toggle"),
        themeIcon: $(".theme-icon"),
        search: $("#product-search"),
        products: $$(".product-card"),
        filters: $$(".filter-button"),
        noProducts: $("#no-products"),
    };

    let isOpen = false;
    let isSending = false;
    let activeCategory = "all";

    $("#current-year").textContent = new Date().getFullYear();

    // Theme preference
    function applyTheme(theme) {
        const selectedTheme = theme === "dark" ? "dark" : "light";
        document.documentElement.dataset.theme = selectedTheme;

        const isDark = selectedTheme === "dark";
        elements.themeIcon.textContent = isDark ? "☀" : "☾";
        elements.themeToggle.setAttribute(
            "aria-label",
            isDark ? "Switch to light mode" : "Switch to dark mode"
        );
        elements.themeToggle.setAttribute("aria-pressed", String(isDark));

        const themeColor = document.querySelector('meta[name="theme-color"]');
        if (themeColor) {
            themeColor.content = isDark ? "#111318" : "#f7f8fa";
        }

        try {
            localStorage.setItem("northstar-theme", selectedTheme);
        } catch (_) {
            // The selected theme still works for the current page.
        }
    }

    let initialTheme = "light";
    try {
        const savedTheme = localStorage.getItem("northstar-theme");
        if (savedTheme === "light" || savedTheme === "dark") {
            initialTheme = savedTheme;
        }
    } catch (_) {
        // Use the default theme when browser storage is unavailable.
    }

    applyTheme(initialTheme);

    elements.themeToggle.addEventListener("click", () => {
        const current = document.documentElement.dataset.theme;
        applyTheme(current === "dark" ? "light" : "dark");
    });

    // Product search and category filters
    function filterProducts() {
        const query = elements.search.value.trim().toLowerCase();
        let visibleCount = 0;

        elements.products.forEach((product) => {
            const name = (product.dataset.name || "").toLowerCase();
            const category = product.dataset.category || "";
            const text = product.textContent.toLowerCase();

            const matchesSearch = !query || name.includes(query) || text.includes(query);
            const matchesCategory = activeCategory === "all" || category === activeCategory;
            const visible = matchesSearch && matchesCategory;

            product.hidden = !visible;
            if (visible) visibleCount += 1;
        });

        elements.noProducts.hidden = visibleCount !== 0;
    }

    elements.search.addEventListener("input", filterProducts);

    elements.filters.forEach((button) => {
        button.addEventListener("click", () => {
            activeCategory = button.dataset.category || "all";
            elements.filters.forEach((item) => {
                const selected = item === button;
                item.classList.toggle("active", selected);
                item.setAttribute("aria-pressed", String(selected));
            });
            filterProducts();
        });
    });

    $("#clear-filters").addEventListener("click", () => {
        elements.search.value = "";
        activeCategory = "all";
        elements.filters.forEach((button) => {
            const selected = button.dataset.category === "all";
            button.classList.toggle("active", selected);
            button.setAttribute("aria-pressed", String(selected));
        });
        filterProducts();
    });

    // "/" focuses product search when the customer is not typing.
    document.addEventListener("keydown", (event) => {
        const target = event.target;
        const typing = target instanceof HTMLElement &&
            (target.isContentEditable || ["INPUT", "TEXTAREA"].includes(target.tagName));

        if (event.key === "/" && !typing) {
            event.preventDefault();
            elements.search.focus();
        }

        if (event.key === "Escape" && isOpen) {
            closeChat();
        }
    });

    // Chat panel controls
    function openChat() {
        isOpen = true;
        elements.panel.classList.add("is-open");
        elements.panel.setAttribute("aria-hidden", "false");
        elements.launcher.classList.add("is-open");
        elements.launcher.setAttribute("aria-expanded", "true");

        window.setTimeout(() => elements.input.focus(), 180);
    }

    function closeChat() {
        isOpen = false;
        elements.panel.classList.remove("is-open");
        elements.panel.setAttribute("aria-hidden", "true");
        elements.launcher.classList.remove("is-open");
        elements.launcher.setAttribute("aria-expanded", "false");
    }

    elements.launcher.addEventListener("click", () => {
        if (isOpen) closeChat();
        else openChat();
    });

    elements.close.addEventListener("click", closeChat);

    ["header-help", "hero-chat", "banner-chat"].forEach((id) => {
        document.getElementById(id).addEventListener("click", openChat);
    });

    // Chat message rendering
    function scrollToLatest() {
        elements.messages.scrollTop = elements.messages.scrollHeight;
    }

    function hideIntro() {
        elements.intro.hidden = true;
    }

    function showError(message) {
        elements.error.textContent = message;
        elements.error.hidden = false;
    }

    function clearError() {
        elements.error.textContent = "";
        elements.error.hidden = true;
    }

    function createMessage(role, messageText) {
        const wrapper = document.createElement("article");
        wrapper.className = `message message-${role}`;

        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.textContent = role === "assistant" ? "✦" : "Y";
        avatar.setAttribute("aria-hidden", "true");

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.textContent = messageText;

        wrapper.append(avatar, bubble);
        elements.messages.appendChild(wrapper);

        return { wrapper, bubble };
    }

    function showTyping() {
        const message = createMessage("assistant", "");
        message.wrapper.classList.add("typing-message");

        const dots = document.createElement("span");
        dots.className = "typing-dots";
        dots.setAttribute("aria-label", "Northstar is thinking");

        for (let index = 0; index < 3; index += 1) {
            dots.appendChild(document.createElement("i"));
        }

        message.bubble.appendChild(dots);
        scrollToLatest();

        return message.wrapper;
    }

    function setSending(sending) {
        isSending = sending;
        elements.send.disabled = sending;
        elements.input.disabled = sending;
        elements.send.classList.toggle("is-loading", sending);
        elements.send.innerHTML = sending ? "<span>…</span>" : "<span>↑</span>";
    }

    async function sendMessage(question) {
        const cleanQuestion = question.trim();

        if (!cleanQuestion || isSending) return;

        if (cleanQuestion.length > 1000) {
            showError("Please keep your question under 1,000 characters.");
            return;
        }

        clearError();
        hideIntro();
        openChat();

        createMessage("user", cleanQuestion);
        elements.input.value = "";
        elements.input.style.height = "auto";
        setSending(true);

        const typingMessage = showTyping();

        try {
            const response = await fetch("/api/chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body: JSON.stringify({ question: cleanQuestion }),
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    result.error || "The assistant could not process your question."
                );
            }

            if (result.status !== "success" || typeof result.answer !== "string") {
                throw new Error("The assistant returned an unexpected response.");
            }

            typingMessage.remove();

            // Customer-facing UI intentionally renders only the natural-language answer.
            // Source filenames, references, similarity scores, and retrieval metadata
            // are not displayed.
            createMessage("assistant", result.answer);
            scrollToLatest();
        } catch (error) {
            typingMessage.remove();
            showError(
                error.message || "Unable to connect to Northstar. Please try again."
            );
        } finally {
            setSending(false);
            elements.input.focus();
        }
    }

    elements.form.addEventListener("submit", (event) => {
        event.preventDefault();
        sendMessage(elements.input.value);
    });

    elements.input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            elements.form.requestSubmit();
        }
    });

    elements.input.addEventListener("input", () => {
        elements.input.style.height = "auto";
        elements.input.style.height =
            `${Math.min(elements.input.scrollHeight, 110)}px`;
    });

    $$("[data-question]").forEach((button) => {
        button.addEventListener("click", () => {
            sendMessage(button.dataset.question || "");
        });
    });

    $$(".ask-product").forEach((button) => {
        button.addEventListener("click", () => {
            const product = button.dataset.product;
            if (!product) return;

            openChat();
            elements.input.value = `Tell me about the ${product}.`;
            elements.input.focus();
        });
    });

    // Backend readiness indicator
    async function checkBackend() {
        try {
            const response = await fetch("/api/ready", {
                headers: { "Accept": "application/json" },
            });
            const result = await response.json();

            elements.status.textContent =
                response.ok && result.status === "ready"
                    ? "Here to help"
                    : "Temporarily unavailable";
        } catch (_) {
            elements.status.textContent = "Connection unavailable";
        }
    }

    checkBackend();
});
