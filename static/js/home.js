(() => {
    const videoPlayer = document.querySelector("[data-video-player]");
    const videoPlayButton = videoPlayer?.querySelector("[data-video-play]");

    videoPlayButton?.addEventListener("click", () => {
        const embedUrl = videoPlayButton.dataset.embedUrl;
        const title = videoPlayButton.dataset.videoTitle || "TreadJoy video";

        if (!embedUrl?.startsWith("https://www.youtube-nocookie.com/embed/")) {
            return;
        }

        videoPlayButton.disabled = true;

        const iframe = document.createElement("iframe");
        iframe.src = embedUrl;
        iframe.title = title;
        iframe.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share";
        iframe.referrerPolicy = "strict-origin-when-cross-origin";
        iframe.allowFullscreen = true;

        videoPlayer.replaceChildren(iframe);
    });

    const waitlistForm = document.querySelector(".home-waitlist-form");
    const waitlistSubmit = waitlistForm?.querySelector("[data-waitlist-submit]");

    waitlistForm?.addEventListener("submit", () => {
        if (!waitlistForm.checkValidity() || !waitlistSubmit) {
            return;
        }

        waitlistSubmit.disabled = true;
        waitlistSubmit.setAttribute("aria-busy", "true");
        waitlistSubmit.classList.add("is-loading");
        waitlistSubmit.replaceChildren();

        const label = document.createElement("span");
        label.textContent = "Joining…";

        waitlistSubmit.append(label);
    });
})();
