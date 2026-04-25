// Shared chat API + tiny markdown renderer used by all UI concepts.
window.HelpAgent = (() => {
  async function ask(question) {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
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

  return { ask, renderMarkdown };
})();
