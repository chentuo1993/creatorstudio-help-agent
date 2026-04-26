// Apple-style squircle app icons: original SVG, unique gradient IDs per render.
// Inspired by public Apple branding; not official assets.
(function () {
  const mkId = () => "a" + (/* @__PURE__ */ (function () {
    if (typeof crypto !== "undefined" && crypto.randomUUID) {
      return crypto.randomUUID().replace(/-/g, "").slice(0, 12);
    }
    return String(Math.random()).slice(2, 16);
  })()) + "_";

  const R = 14; // corner radius
  const squircle = (w, p, defs, content, fill) => `
<svg viewBox="0 0 60 60" width="${w}" height="${w}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" shape-rendering="geometricPrecision">
  <defs>${defs}</defs>
  <rect width="60" height="60" rx="${R}" ry="${R}" fill="${fill}"/>
  ${content}
</svg>`;

  const ICONS = {
    "Final Cut Pro": (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#2c2c2e"/><stop offset="1" stop-color="#000"/>
         </linearGradient>`,
        `<path d="M12 20 L30 8 L30 20 Z" fill="#4CD964"/>
         <path d="M12 20 L12 40 L30 32 L30 20 Z" fill="#FFCC00"/>
         <path d="M12 40 L30 32 L30 52 Z" fill="#FF3B30"/>`,
        "url(#" + p + "g)",
      ),

    Motion: (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="1" y2="1">
           <stop offset="0" stop-color="#5E2B97"/><stop offset="1" stop-color="#D946B0"/>
         </linearGradient>`,
        `<path d="M10 32 Q30 4 50 32" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>
         <circle cx="10" cy="32" r="3" fill="#fff"/><circle cx="50" cy="32" r="3" fill="#fff"/>`,
        `url(#${p}g)`,
      ),

    Compressor: (s, p) =>
      squircle(
        s, p,
        `<radialGradient id="${p}g" cx="0.3" cy="0.2" r="0.9">
           <stop offset="0" stop-color="#FF9500"/><stop offset="1" stop-color="#C41E5C"/>
         </radialGradient>`,
        `<g fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round">
         <path d="M20 20 A 18 18 0 0 1 40 20"/>
         <path d="M22 24 A 12 12 0 0 1 36 24"/>
         <path d="M25 30 A 6 6 0 0 1 33 30"/>
         <circle cx="30" cy="32" r="1.2" fill="#fff" stroke="none"/>
         </g>`,
        `url(#${p}g)`,
      ),

    "Logic Pro": (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#FFD60A"/><stop offset="0.5" stop-color="#FF8C00"/><stop offset="1" stop-color="#E65100"/>
         </linearGradient>`,
        `<rect x="10" y="10" width="40" height="40" rx="9" fill="url(#${p}g)"/>
         <path d="M16 32 Q22 20 28 32 T40 20 T50 32" fill="none" stroke="#1c1c1e" stroke-width="2.2" stroke-linecap="round"/>`,
        "#0a0a0a",
      ),

    MainStage: (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#1c1c1e"/><stop offset="1" stop-color="#000"/>
         </linearGradient>`,
        `<rect x="8" y="20" width="44" height="24" rx="2" fill="#E50914"/>
         <g fill="none" stroke="#fff" stroke-width="1.2">
           <line x1="14" y1="25" x2="46" y2="25"/><line x1="14" y1="32" x2="46" y2="32"/><line x1="14" y1="39" x2="46" y2="39"/>
         </g>
         <circle cx="20" cy="32" r="1.2" fill="#1c1c1e"/>`,
        `url(#${p}g)`,
      ),

    "Pixelmator Pro": (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="1" y2="1">
           <stop offset="0" stop-color="#0A84FF"/>
           <stop offset="0.4" stop-color="#BF5AF2"/>
           <stop offset="0.7" stop-color="#FF2D55"/>
           <stop offset="1" stop-color="#FF9500"/>
         </linearGradient>`,
        `<rect x="10" y="10" width="40" height="40" rx="10" fill="url(#${p}g)"/>
         <path d="M22 44 L32 12 L40 20 L32 50 Z" fill="white" fill-opacity="0.92"/>`,
        "#0a0a0a",
      ),

    Keynote: (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#0A84FF"/><stop offset="1" stop-color="#004C9A"/>
         </linearGradient>`,
        `<rect x="10" y="14" width="40" height="26" rx="2" fill="#fff" opacity="0.95"/>
         <path d="M8 12 L8 8 L52 8 L52 12" fill="none" stroke="url(#${p}g)" stroke-width="4" stroke-linecap="round"/>`,
        "url(#" + p + "g)",
      ),

    Pages: (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#FFCC3B"/><stop offset="1" stop-color="#E68600"/>
         </linearGradient>`,
        `<rect x="12" y="8" width="36" height="44" rx="3" fill="#fff"/>
         <line x1="18" y1="18" x2="44" y2="18" stroke="url(#${p}g)" stroke-width="2" stroke-linecap="round"/>
         <line x1="18" y1="25" x2="40" y2="25" stroke="url(#${p}g)" stroke-width="1.4" stroke-opacity="0.9" stroke-linecap="round"/>`,
        "url(#" + p + "g)",
      ),

    Numbers: (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#2FD565"/><stop offset="1" stop-color="#0E8F3A"/>
         </linearGradient>`,
        `<rect x="14" y="34" width="7" height="12" rx="1" fill="#fff"/>
         <rect x="26" y="22" width="7" height="24" rx="1" fill="#fff"/>
         <rect x="38" y="12" width="7" height="34" rx="1" fill="#fff"/>`,
        `url(#${p}g)`,
      ),

    Freeform: (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="1" y2="1">
           <stop offset="0" stop-color="#5856D6"/><stop offset="0.5" stop-color="#AF52DE"/><stop offset="1" stop-color="#FF9500"/>
         </linearGradient>`,
        `<circle cx="20" cy="20" r="6" fill="#fff" opacity="0.95"/>
         <rect x="32" y="10" width="16" height="16" rx="2" fill="#fff" opacity="0.9"/>
         <path d="M10 50 L30 32 L50 50 Z" fill="#fff" opacity="0.9"/>`,
        `url(#${p}g)`,
      ),

    "Final Cut Camera": (s, p) =>
      squircle(
        s, p,
        `<linearGradient id="${p}g" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#3a3a3c"/><stop offset="1" stop-color="#0a0a0a"/>
         </linearGradient>`,
        `<rect x="10" y="10" width="40" height="40" rx="6" fill="#0a0a0a" stroke="#3a3a3c" stroke-width="1"/>
         <rect x="14" y="24" width="32" height="20" rx="2" fill="#1c1c1e" stroke="#444" stroke-width="0.5"/>
         <circle cx="30" cy="34" r="6" fill="#0a0a0a" stroke="#fff" stroke-width="0.8"/>
         <circle cx="30" cy="34" r="2.2" fill="#2ecc71"/>
         <rect x="25" y="8" width="10" height="3" rx="0.5" fill="#1c1c1e"/>`,
        "url(#" + p + "g)",
      ),

    Default: (s, p) =>
      squircle(
        s, p, "",
        `<text x="30" y="38" text-anchor="middle" fill="white" font-size="20" font-weight="700" font-family="system-ui,sans-serif">?</text>`,
        "#6e6e73",
      ),
  };

  window.APP_ICONS = {
    list: () => [
      "Final Cut Pro", "Final Cut Camera", "Logic Pro", "Pixelmator Pro",
      "Motion", "Compressor", "MainStage",
      "Keynote", "Pages", "Numbers", "Freeform",
    ],
    get: (name, size = 40) => (ICONS[name] || ICONS.Default)(size, mkId()),
  };
})();
