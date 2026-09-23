(() => {
  "use strict";

  const boot = document.getElementById("boot");
  const status = document.getElementById("status-text");

  // The visual boot layer owns only presentation. The application owns all
  // business logic, authentication, database work, and application state.
  const phases = [
    [0, "INITIALIZING OPERATING ENVIRONMENT"],
    [550, "LOADING CORPORATE IDENTITY"],
    [1050, "ESTABLISHING SYSTEM CONTEXT"],
    [1550, "PREPARING PIEROLOOS"],
  ];

  const start = performance.now();
  const minimumDisplay = 2100;
  let appReady = false;

  phases.forEach(([delay, text]) => {
    window.setTimeout(() => {
      if (status) status.textContent = text;
    }, delay);
  });

  // A production gateway can set this before redirecting to the app.
  // Without a gateway signal, the boot layer remains deterministic.
  window.addEventListener("pieroloos:app-ready", () => {
    appReady = true;
    maybeEnterApp();
  }, { once: true });

  function maybeEnterApp() {
    const elapsed = performance.now() - start;
    const wait = Math.max(0, minimumDisplay - elapsed);

    window.setTimeout(() => {
      if (status) status.textContent = "SYSTEM READY";
      boot.classList.add("is-exiting");

      window.setTimeout(() => {
        window.location.replace("/app/");
      }, 640);
    }, wait);
  }

  // Default path: the gateway controls actual application readiness.
  // This fallback prevents a stranded splash if the readiness signal isn't
  // wired yet. It still keeps the visual layer independent from Streamlit.
  window.setTimeout(() => {
    if (!appReady) maybeEnterApp();
  }, 2300);
})();
