(() => {
    const header = document.querySelector("[data-site-header]");

    if (!header) {
        return;
    }

    const focusableSelector = [
        "a[href]",
        "button:not([disabled])",
        "input:not([disabled])",
        "select:not([disabled])",
        "textarea:not([disabled])",
        "[tabindex]:not([tabindex='-1'])",
    ].join(",");

    const disclosures = [...header.querySelectorAll("[data-nav-disclosure]")];

    const setDisclosureOpen = (disclosure, isOpen) => {
        const toggle = disclosure.querySelector("[data-nav-disclosure-toggle]");
        disclosure.dataset.open = String(isOpen);

        if (isOpen) {
            delete disclosure.dataset.dismissed;
        } else {
            delete disclosure.dataset.clickOpen;
        }

        toggle?.setAttribute("aria-expanded", String(isOpen));

        if (toggle?.hasAttribute("aria-label")) {
            toggle.setAttribute(
                "aria-label",
                toggle.getAttribute("aria-label").replace(
                    /^(Show|Hide)/,
                    isOpen ? "Hide" : "Show",
                ),
            );
        }
    };

    const closeDisclosures = (except = null) => {
        disclosures.forEach((disclosure) => {
            if (disclosure !== except) {
                setDisclosureOpen(disclosure, false);
            }
        });
    };

    disclosures.forEach((disclosure) => {
        const toggle = disclosure.querySelector("[data-nav-disclosure-toggle]");

        disclosure.addEventListener("pointerenter", () => {
            closeDisclosures(disclosure);
            setDisclosureOpen(disclosure, true);
        });

        disclosure.addEventListener("pointerleave", () => {
            if (!disclosure.contains(document.activeElement)) {
                delete disclosure.dataset.dismissed;
                setDisclosureOpen(disclosure, false);
            }
        });

        disclosure.addEventListener("focusin", () => {
            closeDisclosures(disclosure);
            setDisclosureOpen(disclosure, true);
        });

        disclosure.addEventListener("focusout", (event) => {
            if (!disclosure.contains(event.relatedTarget)) {
                delete disclosure.dataset.dismissed;
                setDisclosureOpen(disclosure, false);
            }
        });

        toggle?.addEventListener("click", () => {
            const wasOpenedByClick = disclosure.dataset.clickOpen === "true";
            closeDisclosures(disclosure);

            if (wasOpenedByClick) {
                setDisclosureOpen(disclosure, false);
                disclosure.dataset.dismissed = "true";
            } else {
                setDisclosureOpen(disclosure, true);
                disclosure.dataset.clickOpen = "true";
            }
        });
    });

    const searchPanel = header.querySelector("[data-search-panel]");
    const searchToggles = [...header.querySelectorAll("[data-search-toggle]")];
    const searchInput = searchPanel?.querySelector("input[type='search']");

    const setSearchOpen = (isOpen, { restoreFocus = false } = {}) => {
        if (!searchPanel) {
            return;
        }

        searchPanel.hidden = !isOpen;
        searchToggles.forEach((toggle) => {
            toggle.setAttribute("aria-expanded", String(isOpen));
        });

        if (isOpen) {
            closeDisclosures();
            searchInput?.focus();
        } else if (restoreFocus) {
            searchToggles[0]?.focus();
        }
    };

    if (searchPanel) {
        setSearchOpen(false);

        searchToggles.forEach((toggle) => {
            toggle.addEventListener("click", () => {
                setSearchOpen(toggle.getAttribute("aria-expanded") !== "true");
            });
        });
    }

    const mobileNavigation = header.querySelector("[data-mobile-navigation]");
    const mobileOpenButton = header.querySelector("[data-mobile-menu-open]");
    const mobileCloseButton = header.querySelector("[data-mobile-menu-close]");
    const mobileSubmenuToggles = [
        ...header.querySelectorAll("[data-mobile-submenu-toggle]"),
    ];
    let mobileMenuOpen = false;

    const setMobileMenuOpen = (isOpen, { restoreFocus = false } = {}) => {
        if (!mobileNavigation || !mobileOpenButton) {
            return;
        }

        mobileMenuOpen = isOpen;
        mobileNavigation.classList.toggle("is-open", isOpen);
        mobileNavigation.setAttribute("aria-hidden", String(!isOpen));
        mobileOpenButton.setAttribute("aria-expanded", String(isOpen));
        mobileOpenButton.setAttribute(
            "aria-label",
            isOpen ? "Close navigation" : "Open navigation",
        );
        document.body.classList.toggle("navigation-open", isOpen);

        if (isOpen) {
            setSearchOpen(false);
            closeDisclosures();
            mobileNavigation.setAttribute("role", "dialog");
            mobileNavigation.setAttribute("aria-modal", "true");
            mobileCloseButton?.focus();
        } else {
            mobileNavigation.removeAttribute("role");
            mobileNavigation.removeAttribute("aria-modal");

            if (restoreFocus) {
                mobileOpenButton.focus();
            }
        }
    };

    if (mobileNavigation) {
        mobileNavigation.setAttribute("aria-hidden", "true");
        mobileOpenButton?.addEventListener("click", () => {
            setMobileMenuOpen(true);
        });
        mobileCloseButton?.addEventListener("click", () => {
            setMobileMenuOpen(false, { restoreFocus: true });
        });
    }

    mobileSubmenuToggles.forEach((toggle) => {
        const panelId = toggle.getAttribute("aria-controls");
        const panel = panelId ? document.getElementById(panelId) : null;

        if (!panel) {
            return;
        }

        panel.hidden = true;

        toggle.addEventListener("click", () => {
            const isOpen = toggle.getAttribute("aria-expanded") === "true";
            toggle.setAttribute("aria-expanded", String(!isOpen));
            panel.hidden = isOpen;
        });
    });

    document.addEventListener("click", (event) => {
        if (!event.target.closest("[data-nav-disclosure]")) {
            closeDisclosures();
        }

        if (
            searchPanel
            && !searchPanel.hidden
            && !event.target.closest("[data-search-panel]")
            && !event.target.closest("[data-search-toggle]")
        ) {
            setSearchOpen(false);
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            if (mobileMenuOpen) {
                setMobileMenuOpen(false, { restoreFocus: true });
                return;
            }

            if (searchPanel && !searchPanel.hidden) {
                setSearchOpen(false, { restoreFocus: true });
                return;
            }

            const openDisclosure = disclosures.find(
                (disclosure) => disclosure.dataset.open === "true",
            );

            if (openDisclosure) {
                const toggle = openDisclosure.querySelector(
                    "[data-nav-disclosure-toggle]",
                );
                setDisclosureOpen(openDisclosure, false);
                openDisclosure.dataset.dismissed = "true";
                toggle?.focus();
            }
        }

        if (event.key === "Tab" && mobileMenuOpen && mobileNavigation) {
            const focusableElements = [
                ...mobileNavigation.querySelectorAll(focusableSelector),
            ].filter((element) => element.offsetParent !== null);
            const firstElement = focusableElements[0];
            const lastElement = focusableElements.at(-1);

            if (event.shiftKey && document.activeElement === firstElement) {
                event.preventDefault();
                lastElement?.focus();
            } else if (
                !event.shiftKey
                && document.activeElement === lastElement
            ) {
                event.preventDefault();
                firstElement?.focus();
            }
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth >= 1024 && mobileMenuOpen) {
            setMobileMenuOpen(false);
        }
    });
})();
