// Shared brief renderer + storage helpers, used by interviews.html and brief.html.
// Exposes window.briefUtils.

(function () {
  const TODO_KEY = "cotton-todos-v1";
  const LANG_KEY = "cottonBriefLang";

  // todoId -> [{footnote, document, url, archive_url, cited_for, page}], the underlying
  // source documents Cotton cites in her book (resolved from footnotes to validated URLs).
  let sourceIndex = {};
  async function loadSourceIndex(url) {
    try {
      const r = await fetch(url || "./book_followup_sources.data.json", { cache: "no-cache" });
      if (r.ok) {
        const groups = await r.json();
        const idx = {};
        for (const g of groups) for (const t of (g.todos || [])) {
          if (t.sources && t.sources.length) idx[t.id] = t.sources;
        }
        sourceIndex = idx;
      }
    } catch (e) { console.warn("Could not load book_followup_sources.data.json", e); }
    return sourceIndex;
  }
  function setSourceIndex(idx) { sourceIndex = idx || {}; }

  const esc = (s) =>
    String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );

  const tsToSeconds = (ts) => {
    if (!ts) return 0;
    const parts = String(ts).split(":").map((n) => parseInt(n, 10));
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    return parts[0] || 0;
  };

  const videoTimeUrl = (v, ts) => {
    const s = tsToSeconds(ts);
    if (!s) return v.url;
    if (v.platform === "YouTube") return v.url + (v.url.includes("?") ? "&" : "?") + "t=" + s + "s";
    if (v.platform === "Dailymotion") return v.url + (v.url.includes("?") ? "&" : "?") + "start=" + s;
    return v.url;
  };

  function loadTodos() {
    try { return JSON.parse(localStorage.getItem(TODO_KEY)) || {}; }
    catch { return {}; }
  }
  function saveTodos(state) { localStorage.setItem(TODO_KEY, JSON.stringify(state)); }
  function setTodoChecked(id, checked) {
    const s = loadTodos();
    if (checked) s[id] = { checked: true, checkedAt: new Date().toISOString() };
    else delete s[id];
    saveTodos(s);
  }
  function loadLang() { return localStorage.getItem(LANG_KEY) === "fr" ? "fr" : "en"; }
  function saveLang(l) { localStorage.setItem(LANG_KEY, l); }

  function renderStubBody(v) {
    return `<p class="stub-msg">
      <span class="en-only">In Brief for this interview is not yet authored. Transcript: <a href="../archive/transcripts/${esc(v.id)}_EN.md">EN</a> · <a href="../archive/transcripts/${esc(v.id)}_FR.md">FR</a>.</span>
      <span class="fr-only">Le « En bref » de cette interview n'est pas encore rédigé. Transcription : <a href="../archive/transcripts/${esc(v.id)}_EN.md">EN</a> · <a href="../archive/transcripts/${esc(v.id)}_FR.md">FR</a>.</span>
    </p>`;
  }

  // Renders the inner contents of `.brief-body` (everything below the optional summary line).
  // The caller wraps it in <details><summary>…</summary><div class="brief-body" data-lang …>…</div></details>
  // for inline use, or in a plain <article> for the dedicated page.
  function renderBriefBody(v, brief, opts = {}) {
    const includeResetButton = opts.includeResetButton !== false;
    const todosState = loadTodos();

    const headerBits = [];
    if (brief.date) headerBits.push(`<span>📅 ${esc(brief.date)}</span>`);
    const interviewer = brief.interviewer || {};
    if (interviewer.en) {
      headerBits.push(`<span>🎙️ <span class="en-only">${esc(interviewer.en)}</span><span class="fr-only">${esc(interviewer.fr || interviewer.en)}</span></span>`);
    }
    const outlet = brief.outlet || {};
    if (outlet.en) {
      headerBits.push(`<span>📺 <span class="en-only">${esc(outlet.en)}</span><span class="fr-only">${esc(outlet.fr || outlet.en)}</span></span>`);
    }
    if (brief.duration_min) headerBits.push(`<span>⏱ ${brief.duration_min} min</span>`);

    const langButtonsHTML = `<div class="lang-toggle" role="group" aria-label="Language">
      <button type="button" data-lang-set="en">EN</button>
      <button type="button" data-lang-set="fr">FR</button>
    </div>`;

    const pullQuoteHTML = brief.pull_quote
      ? `<blockquote class="pull-quote">
          <span class="en-only">“${esc(brief.pull_quote.en)}”</span>
          <span class="fr-only">«&nbsp;${esc(brief.pull_quote.fr || brief.pull_quote.en)}&nbsp;»</span>
        </blockquote>`
      : "";

    const claimsHTML = (brief.claims || [])
      .map((c) => {
        const tsChip = c.timestamp
          ? `<a class="ts-chip" href="${esc(videoTimeUrl(v, c.timestamp))}" target="_blank" rel="noopener">▶ ${esc(c.timestamp)}</a>`
          : "";
        const topicChip = c.topic ? `<span class="topic-chip">${esc(c.topic)}</span>` : "";
        const sources = c.documents && c.documents.length
          ? `<div class="claim-sources">
               <span class="en-only">Sources: ${c.documents.map(esc).join("; ")}</span>
               <span class="fr-only">Sources : ${c.documents.map(esc).join(" ; ")}</span>
             </div>`
          : "";
        return `<li class="claim">
          <span class="claim-text">
            <span class="en-only">${esc(c.en)}</span>
            <span class="fr-only">${esc(c.fr || c.en)}</span>
          </span>
          <span class="claim-meta">${tsChip}${topicChip}</span>
          ${sources}
        </li>`;
      })
      .join("");

    const docsHTML = (brief.documents_cited || [])
      .map((d) => {
        const where = d.where ? ` <span class="where">— ${esc(d.where)}</span>` : "";
        return `<li>${esc(d.name)}${where}</li>`;
      })
      .join("");

    const renderTodoSources = (id) => {
      const srcs = sourceIndex[id] || [];
      if (!srcs.length) return "";
      const items = srcs.map((s) => {
        const fn = (s.footnote && s.footnote !== "none")
          ? `<span class="fn-num" title="Footnote ${esc(s.footnote)} in the book">${esc(s.footnote)}</span> ` : "";
        const label = s.url
          ? `<a href="${esc(s.url)}" target="_blank" rel="noopener"${s.cited_for ? ` title="${esc(s.cited_for)}"` : ""}>${esc(s.document)}</a>`
          : `<span${s.cited_for ? ` title="${esc(s.cited_for)}"` : ""}>${esc(s.document)}</span>`;
        const arch = s.archive_url
          ? ` <a class="arch-link" href="${esc(s.archive_url)}" target="_blank" rel="noopener" title="Archived copy (Internet Archive) — use if the link above is down">⧉ archived</a>` : "";
        return `<li>${fn}${label}${arch}</li>`;
      }).join("");
      return `<div class="todo-sources">
        <span class="docs-label en-only">Sources she cites in the book</span>
        <span class="docs-label fr-only">Sources qu'elle cite dans le livre</span>
        <ul>${items}</ul>
      </div>`;
    };

    const todosHTML = (brief.todos || [])
      .map((t) => {
        const done = !!todosState[t.id]?.checked;
        return `<li class="todo-item ${done ? "done" : ""}" data-todo-row="${esc(t.id)}">
          <input type="checkbox" id="cb-${esc(t.id)}" data-todo-id="${esc(t.id)}" ${done ? "checked" : ""}>
          <label for="cb-${esc(t.id)}">
            <span class="en-only">${esc(t.text.en)}</span>
            <span class="fr-only">${esc(t.text.fr || t.text.en)}</span>
            ${t.context ? `<span class="todo-context">${esc(t.context)}</span>` : ""}
          </label>
          ${renderTodoSources(t.id)}
        </li>`;
      })
      .join("");

    const statusClass = brief.status || "draft";
    const statusLabelEN = { complete: "Complete", draft: "Draft", stub: "Stub" }[statusClass] || "Draft";
    const statusLabelFR = { complete: "Complet", draft: "Brouillon", stub: "Ébauche" }[statusClass] || "Brouillon";
    const translationNote = brief.translation_note
      ? `<span><span class="en-only">${esc(brief.translation_note.en)}</span><span class="fr-only">${esc(brief.translation_note.fr || brief.translation_note.en)}</span></span>`
      : "";

    return `<div class="brief-header">
      ${headerBits.join("")}
      ${langButtonsHTML}
    </div>
    ${pullQuoteHTML}
    ${brief.claims && brief.claims.length ? `<div class="brief-section">
      <h4><span class="en-only">Key statements</span><span class="fr-only">Déclarations clés</span></h4>
      <ul class="claims-list">${claimsHTML}</ul>
    </div>` : ""}
    ${brief.documents_cited && brief.documents_cited.length ? `<div class="brief-section">
      <h4><span class="en-only">Documents cited</span><span class="fr-only">Documents cités</span></h4>
      <ul class="docs-list">${docsHTML}</ul>
    </div>` : ""}
    ${brief.todos && brief.todos.length ? `<div class="brief-section">
      <h4 class="todos-h"><span class="en-only">Research follow-ups</span><span class="fr-only">Suivis de recherche</span></h4>
      <ul class="todo-list">${todosHTML}</ul>
    </div>` : ""}
    <div class="brief-footer">
      ${brief.last_reviewed ? `<span><span class="en-only">Last reviewed: ${esc(brief.last_reviewed)}</span><span class="fr-only">Dernière révision : ${esc(brief.last_reviewed)}</span></span>` : ""}
      <span><span class="en-only">Status: ${statusLabelEN}</span><span class="fr-only">Statut : ${statusLabelFR}</span></span>
      ${includeResetButton && brief.todos && brief.todos.length ? `<button type="button" class="reset" data-reset-video="${esc(v.id)}">
        <span class="en-only">Clear checks for this interview</span>
        <span class="fr-only">Décocher cette interview</span>
      </button>` : ""}
      ${translationNote}
    </div>`;
  }

  // Apply current EN/FR selection to the buttons inside a brief-body element.
  function syncLangButtons(root) {
    const lang = loadLang();
    root.querySelectorAll(".brief-body").forEach((el) => (el.dataset.lang = lang));
    root.querySelectorAll(".lang-toggle button").forEach((b) => {
      b.classList.toggle("on", b.dataset.langSet === lang);
    });
  }

  window.briefUtils = {
    TODO_KEY, LANG_KEY,
    esc, tsToSeconds, videoTimeUrl,
    loadTodos, saveTodos, setTodoChecked,
    loadLang, saveLang,
    loadSourceIndex, setSourceIndex,
    renderBriefBody, renderStubBody, syncLangButtons
  };
})();
