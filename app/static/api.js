// Shared chat API + tiny markdown renderer.
window.HelpAgent = (() => {
  /**
   * @param {string} question — latest user message
   * @param {{role:string, content:string}[]} [history] — prior turns
   */
  async function ask(question, history) {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        question,
        history: history && history.length ? history : [],
      }),
    });
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }

  /**
   * SSE from POST /api/chat/stream: {t:'meta'|'d'|'done', ...}
   * Resolves when stream finishes; calls onToken for each text delta, onMeta first.
   */
  function askStream(question, history, cb) {
    return (async function () {
      const r = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          question,
          history: history && history.length ? history : [],
        }),
      });
      if (!r.ok) {
        if (cb.onError) cb.onError(new Error("HTTP " + r.status));
        throw new Error("HTTP " + r.status);
      }
      const reader = r.body.getReader();
      const dec = new TextDecoder();
      let buffer = "";
      for (;;) {
        const { value, done } = await reader.read();
        if (value) buffer += dec.decode(value, { stream: true });
        for (;;) {
          const idx = buffer.indexOf("\n\n");
          if (idx < 0) break;
          const block = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);
          for (const line of block.split("\n")) {
            if (!line.startsWith("data: ")) continue;
            let j;
            try {
              j = JSON.parse(line.slice(6));
            } catch (e) {
              continue;
            }
            if (j.t === "meta" && cb.onMeta) cb.onMeta(j);
            if (j.t === "d" && j.d && cb.onToken) cb.onToken(j.d);
            if (j.t === "done") {
              if (cb.onDone) cb.onDone();
              return;
            }
          }
        }
        if (done) {
          for (const line of buffer.split("\n")) {
            if (!line.startsWith("data: ")) continue;
            try {
              const j = JSON.parse(line.slice(6));
              if (j.t === "done" && cb.onDone) cb.onDone();
            } catch (e) { /* */ }
          }
          if (cb.onDone) cb.onDone();
          return;
        }
      }
    })();
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function renderMarkdown(md) {
    let s = escapeHtml(md);
    s = s.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    s = s.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
    s = s.replace(/^- (.+)$/gm, "<li>$1</li>");
    s = s.replace(/(<li>.*<\/li>\n?)+/g, (m) => "<ul>" + m + "</ul>");
    s = s.replace(/\[(\d+)\]/g, '<sup class="cite">[$1]</sup>');
    s = s.replace(/\n\n+/g, "</p><p>");
    s = s.replace(/\n/g, "<br/>");
    return "<p>" + s + "</p>";
  }

  return { ask, askStream, renderMarkdown };
})();
