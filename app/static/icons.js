// Apple Creator Studio app icons (SVG, original artwork inspired by Apple's
// public branding — colors and motifs only, no copied bitmaps).
// Each entry returns an SVG string sized to the given pixel dimension.
window.APP_ICONS = (() => {
  const squircle = (size, defs, content, bg) => `
<svg viewBox="0 0 60 60" width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>${defs || ""}</defs>
  <rect width="60" height="60" rx="14" ry="14" fill="${bg || "#222"}"/>
  ${content}
</svg>`;

  const ICONS = {
    "Final Cut Pro": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="fcpBg" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#2a2a2c"/>
           <stop offset="1" stop-color="#0a0a0a"/>
         </linearGradient>`,
        `<polygon points="14,16 30,30 14,44" fill="#FF3B30"/>
         <polygon points="26,16 42,30 26,44" fill="#FFB200" opacity="0.95"/>
         <polygon points="38,16 50,24 50,36 38,44" fill="#34C759" opacity="0.9"/>`,
        "url(#fcpBg)",
      ),

    "Motion": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="motBg" x1="0" y1="0" x2="1" y2="1">
           <stop offset="0" stop-color="#7B2CBF"/>
           <stop offset="1" stop-color="#FF6FB5"/>
         </linearGradient>`,
        `<path d="M14 42 Q30 6 46 42" stroke="white" stroke-width="3.5" fill="none" stroke-linecap="round"/>
         <circle cx="46" cy="42" r="3.6" fill="white"/>
         <circle cx="14" cy="42" r="3.6" fill="white"/>`,
        "url(#motBg)",
      ),

    "Compressor": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="cmpBg" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#FF8C00"/>
           <stop offset="1" stop-color="#E0245E"/>
         </linearGradient>`,
        `<path d="M14 30 H22 M26 22 V38 M30 26 V34 M34 22 V38 M38 30 H46" stroke="white" stroke-width="3" stroke-linecap="round" fill="none"/>`,
        "url(#cmpBg)",
      ),

    "Logic Pro": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="lpBg" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#FFB200"/>
           <stop offset="1" stop-color="#FF7A1F"/>
         </linearGradient>`,
        `<path d="M10 30 L18 30 L22 18 L26 42 L30 22 L34 38 L38 26 L42 32 L50 30" stroke="white" stroke-width="2.6" fill="none" stroke-linejoin="round" stroke-linecap="round"/>`,
        "url(#lpBg)",
      ),

    "MainStage": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="msBg" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#1c1c1e"/>
           <stop offset="1" stop-color="#000"/>
         </linearGradient>`,
        `<rect x="14" y="22" width="32" height="20" rx="3" fill="#FF3B30"/>
         <circle cx="22" cy="32" r="2.5" fill="#1c1c1e"/>
         <circle cx="30" cy="32" r="2.5" fill="#1c1c1e"/>
         <circle cx="38" cy="32" r="2.5" fill="#1c1c1e"/>`,
        "url(#msBg)",
      ),

    "Pixelmator Pro": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="pxBg" x1="0" y1="0" x2="1" y2="1">
           <stop offset="0" stop-color="#FF3B30"/>
           <stop offset="0.33" stop-color="#FFB200"/>
           <stop offset="0.66" stop-color="#34C759"/>
           <stop offset="1" stop-color="#0A84FF"/>
         </linearGradient>`,
        `<path d="M16 44 L34 16 L46 24 L28 50 Z" fill="white" opacity="0.9"/>
         <circle cx="40" cy="20" r="3" fill="white"/>`,
        "url(#pxBg)",
      ),

    "Keynote": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="knBg" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#0A84FF"/>
           <stop offset="1" stop-color="#0066CC"/>
         </linearGradient>`,
        `<rect x="12" y="16" width="36" height="22" rx="2" fill="white"/>
         <rect x="28" y="38" width="4" height="6" fill="white"/>
         <rect x="20" y="44" width="20" height="2" rx="1" fill="white"/>`,
        "url(#knBg)",
      ),

    "Pages": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="pgBg" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#FFB948"/>
           <stop offset="1" stop-color="#FF8C00"/>
         </linearGradient>`,
        `<rect x="16" y="12" width="28" height="36" rx="3" fill="white"/>
         <rect x="20" y="20" width="20" height="2" rx="1" fill="#FF8C00"/>
         <rect x="20" y="26" width="20" height="2" rx="1" fill="#FF8C00"/>
         <rect x="20" y="32" width="14" height="2" rx="1" fill="#FF8C00"/>`,
        "url(#pgBg)",
      ),

    "Numbers": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="nmBg" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#34C759"/>
           <stop offset="1" stop-color="#1F8F3D"/>
         </linearGradient>`,
        `<rect x="18" y="32" width="5" height="14" rx="1" fill="white"/>
         <rect x="26" y="22" width="5" height="24" rx="1" fill="white"/>
         <rect x="34" y="14" width="5" height="32" rx="1" fill="white"/>`,
        "url(#nmBg)",
      ),

    "Freeform": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="ffBg" x1="0" y1="0" x2="1" y2="1">
           <stop offset="0" stop-color="#FF8C00"/>
           <stop offset="1" stop-color="#7B2CBF"/>
         </linearGradient>`,
        `<circle cx="22" cy="22" r="6" fill="white" opacity="0.9"/>
         <rect x="32" y="16" width="14" height="14" rx="2" fill="white" opacity="0.9"/>
         <path d="M18 38 L30 50 L42 38 Z" fill="white" opacity="0.9"/>`,
        "url(#ffBg)",
      ),

    "Final Cut Camera": (s = 40) =>
      squircle(
        s,
        `<linearGradient id="fccBg" x1="0" y1="0" x2="0" y2="1">
           <stop offset="0" stop-color="#1c1c1e"/>
           <stop offset="1" stop-color="#000"/>
         </linearGradient>`,
        `<rect x="14" y="22" width="32" height="20" rx="3" fill="#fff"/>
         <circle cx="30" cy="32" r="6" fill="#1c1c1e"/>
         <circle cx="30" cy="32" r="2.6" fill="#FF3B30"/>
         <rect x="38" y="18" width="6" height="4" rx="1" fill="#fff"/>`,
        "url(#fccBg)",
      ),

    Default: (s = 40) =>
      squircle(s, "", `<text x="30" y="38" text-anchor="middle" fill="white" font-size="22" font-weight="700">?</text>`, "#5b5b5f"),
  };

  return {
    list: () => [
      "Final Cut Pro", "Logic Pro", "Pixelmator Pro", "Motion", "Compressor",
      "MainStage", "Keynote", "Pages", "Numbers", "Freeform", "Final Cut Camera",
    ],
    get: (name, size = 40) => (ICONS[name] || ICONS.Default)(size),
  };
})();
