/* Departures — Language Translator
   LANGUAGES is injected by templates/index.html as {"english": "en", ...} */

function titleCase(str) {
  return str.replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Builds a searchable language picker inside `container` and wires up
 * its open/close/search/select behaviour.
 * Returns { getCode, setCode } so the caller can read/drive the selection.
 */
function createDropdown(container, { languages, includeAuto, defaultCode, eyebrow, onChange }) {
  const entries = Object.entries(languages)
    .map(([name, code]) => ({ name: titleCase(name), code }))
    .sort((a, b) => a.name.localeCompare(b.name));

  if (includeAuto) {
    entries.unshift({ name: "Detect Language", code: "auto" });
  }

  container.innerHTML = `
    <button type="button" class="dropdown-toggle">
      <span>
        <span class="eyebrow">${eyebrow}</span>
        <span class="label-row">
          <span class="lang-name"></span>
          <span class="lang-code"></span>
        </span>
      </span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
    </button>
    <div class="dropdown-menu hidden">
      <input type="text" class="dropdown-search" placeholder="Search language…" autocomplete="off" />
      <ul class="dropdown-list"></ul>
    </div>
  `;

  const toggle = container.querySelector(".dropdown-toggle");
  const menu = container.querySelector(".dropdown-menu");
  const search = container.querySelector(".dropdown-search");
  const list = container.querySelector(".dropdown-list");
  const nameEl = container.querySelector(".lang-name");
  const codeEl = container.querySelector(".lang-code");
  const labelRow = container.querySelector(".label-row");

  let currentCode = defaultCode;

  function renderList(filter) {
    const q = (filter || "").trim().toLowerCase();
    const filtered = q ? entries.filter((e) => e.name.toLowerCase().includes(q)) : entries;
    list.innerHTML = "";
    if (!filtered.length) {
      list.innerHTML = '<li class="empty">No languages match.</li>';
      return;
    }
    filtered.forEach((e) => {
      const li = document.createElement("li");
      li.className = e.code === currentCode ? "active" : "";
      li.innerHTML = `<span>${e.name}</span><span class="lang-code">${e.code.toUpperCase()}</span>`;
      li.addEventListener("click", () => {
        select(e.code, e.name, true);
        closeMenu();
      });
      list.appendChild(li);
    });
  }

  function select(code, name, animate) {
    currentCode = code;
    nameEl.textContent = name;
    codeEl.textContent = code.toUpperCase();
    if (animate) {
      labelRow.classList.remove("flip");
      void labelRow.offsetWidth; // restart the animation
      labelRow.classList.add("flip");
      if (onChange) onChange(code, name);
    }
  }

  function openMenu() {
    document.querySelectorAll(".dropdown-menu").forEach((m) => m.classList.add("hidden"));
    menu.classList.remove("hidden");
    search.value = "";
    renderList("");
    setTimeout(() => search.focus(), 0);
  }

  function closeMenu() {
    menu.classList.add("hidden");
  }

  toggle.addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.contains("hidden") ? openMenu() : closeMenu();
  });

  search.addEventListener("input", () => renderList(search.value));
  search.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeMenu();
      toggle.focus();
    }
  });

  document.addEventListener("click", (e) => {
    if (!container.contains(e.target)) closeMenu();
  });

  const initial = entries.find((e) => e.code === defaultCode) || entries[0];
  select(initial.code, initial.name, false);

  return {
    getCode: () => currentCode,
    setCode: (code) => {
      const found = entries.find((e) => e.code === code);
      if (found) select(found.code, found.name, true);
    },
  };
}

document.addEventListener("DOMContentLoaded", () => {
  const inputText = document.getElementById("input-text");
  const outputText = document.getElementById("output-text");
  const charCount = document.getElementById("char-count");
  const translateBtn = document.getElementById("translate-btn");
  const swapBtn = document.getElementById("swap-btn");
  const clearBtn = document.getElementById("clear-btn");
  const copyBtn = document.getElementById("copy-btn");
  const speakInputBtn = document.getElementById("speak-input-btn");
  const speakOutputBtn = document.getElementById("speak-output-btn");
  const statusPill = document.getElementById("status-pill");
  const errorBanner = document.getElementById("error-banner");
  const themeToggle = document.getElementById("theme-toggle");

  const MAX_CHARS = 4900;
  let debounceTimer = null;
  let requestSeq = 0; // ignore stale responses if a newer request has started

  const sourceDropdown = createDropdown(document.getElementById("source-dropdown"), {
    languages: LANGUAGES,
    includeAuto: true,
    defaultCode: "auto",
    eyebrow: "From",
    onChange: () => scheduleTranslate(0),
  });

  const targetDropdown = createDropdown(document.getElementById("target-dropdown"), {
    languages: LANGUAGES,
    includeAuto: false,
    defaultCode: "en",
    eyebrow: "To",
    onChange: () => scheduleTranslate(0),
  });

  function setStatus(text) {
    statusPill.textContent = text;
    statusPill.classList.remove("flip");
    void statusPill.offsetWidth;
    statusPill.classList.add("flip");
  }

  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.classList.remove("hidden");
  }

  function hideError() {
    errorBanner.classList.add("hidden");
  }

  function scheduleTranslate(delay) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(runTranslate, delay === undefined ? 600 : delay);
  }

  async function runTranslate() {
    const text = inputText.value.trim();
    hideError();

    if (!text) {
      outputText.value = "";
      setStatus("READY");
      return;
    }

    const seq = ++requestSeq;
    setStatus("TRANSLATING…");

    try {
      const res = await fetch("/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          source: sourceDropdown.getCode(),
          target: targetDropdown.getCode(),
        }),
      });

      const data = await res.json();
      if (seq !== requestSeq) return; // superseded by a more recent request

      if (!res.ok) throw new Error(data.error || "Something went wrong.");

      outputText.value = data.translated_text;
      setStatus("TRANSLATED");
    } catch (err) {
      if (seq !== requestSeq) return;
      setStatus("READY");
      showError(err.message || "Couldn't reach the translator. Check your connection and try again.");
    }
  }

  inputText.addEventListener("input", () => {
    charCount.textContent = `${inputText.value.length} / ${MAX_CHARS}`;
    scheduleTranslate(600);
  });

  inputText.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") scheduleTranslate(0);
  });

  translateBtn.addEventListener("click", () => scheduleTranslate(0));

  swapBtn.addEventListener("click", () => {
    const sourceCode = sourceDropdown.getCode();
    if (sourceCode === "auto") {
      showError('Pick a specific "From" language before swapping.');
      return;
    }
    const targetCode = targetDropdown.getCode();
    sourceDropdown.setCode(targetCode);
    targetDropdown.setCode(sourceCode);

    const tmp = inputText.value;
    inputText.value = outputText.value;
    outputText.value = tmp;
    charCount.textContent = `${inputText.value.length} / ${MAX_CHARS}`;

    scheduleTranslate(0);
  });

  clearBtn.addEventListener("click", () => {
    inputText.value = "";
    outputText.value = "";
    charCount.textContent = `0 / ${MAX_CHARS}`;
    hideError();
    setStatus("READY");
    inputText.focus();
  });

  copyBtn.addEventListener("click", async () => {
    if (!outputText.value) return;
    try {
      await navigator.clipboard.writeText(outputText.value);
      setStatus("COPIED");
      setTimeout(() => setStatus(outputText.value ? "TRANSLATED" : "READY"), 1000);
    } catch {
      showError("Could not copy — try selecting and copying the text manually.");
    }
  });

  function speak(text, langCode) {
    if (!text) return;
    if (!("speechSynthesis" in window)) {
      showError("Text-to-speech isn't supported in this browser.");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    if (langCode) utterance.lang = langCode;
    window.speechSynthesis.speak(utterance);
  }

  speakInputBtn.addEventListener("click", () => {
    const code = sourceDropdown.getCode();
    speak(inputText.value, code === "auto" ? undefined : code);
  });

  speakOutputBtn.addEventListener("click", () => {
    speak(outputText.value, targetDropdown.getCode());
  });

  // ---- Theme ----
  function applyTheme(theme) {
    document.body.classList.toggle("dark", theme === "dark");
  }

  const savedTheme = localStorage.getItem("departures-theme");
  if (savedTheme) {
    applyTheme(savedTheme);
  } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    applyTheme("dark");
  }

  themeToggle.addEventListener("click", () => {
    const isDark = document.body.classList.toggle("dark");
    localStorage.setItem("departures-theme", isDark ? "dark" : "light");
  });
});
