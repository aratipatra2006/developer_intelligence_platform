(function () {
    const output = document.getElementById('terminal-output');
    if (!output) return;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const script = [
        { text: '$ dip analyze github.com/acme/orbit-api', cls: '' },
        { text: '  scanning 214 files across 18 directories…', cls: 'line-dim' },
        { text: '  + src/services/payments/*.ts', cls: 'line-path' },
        { text: '  + src/routes/webhooks.ts', cls: 'line-path' },
        { text: '  stack detected: Node.js, PostgreSQL, Redis', cls: 'line-add' },
        { text: '  warning: hardcoded API key in config/dev.js', cls: 'line-warn' },
        { text: '  health score: 82/100', cls: 'line-add' },
        { text: '  architecture map ready', cls: 'line-add' },
        { text: '$ ready for questions_', cls: '' },
    ];

    // Reduced motion: render the final state instantly, no animation.
    if (prefersReducedMotion) {
        output.innerHTML = script
            .map(l => `<span class="${l.cls}">${l.text}</span>`)
            .join('\n');
        return;
    }

    let lineIndex = 0;
    let charIndex = 0;
    let currentLine = document.createElement('span');
    output.appendChild(currentLine);

    function typeNext() {
        if (lineIndex >= script.length) {
            const cursor = document.createElement('span');
            cursor.className = 'cursor';
            output.appendChild(cursor);
            return;
        }

        const entry = script[lineIndex];
        if (charIndex === 0) {
            currentLine = document.createElement('span');
            currentLine.className = entry.cls;
            output.appendChild(currentLine);
        }

        if (charIndex < entry.text.length) {
            currentLine.textContent += entry.text[charIndex];
            charIndex++;
            setTimeout(typeNext, 14 + Math.random() * 18);
        } else {
            output.appendChild(document.createTextNode('\n'));
            lineIndex++;
            charIndex = 0;
            setTimeout(typeNext, 220);
        }
    }

    setTimeout(typeNext, 400);
})();

// Home Page Feature Cards
document.addEventListener("DOMContentLoaded", () => {
  const featureCards = document.querySelectorAll(".card.feature-card");

  const showWarning = () => {
    // Replace with a toast/snackbar if you have one — alert() blocks the UI thread
    showToast("⚠️ Please analyze a repository first.");
  };

  featureCards.forEach((card) => {
    // Make it accessible: focusable + keyboard-activatable if it's not already a <button>
    if (!card.hasAttribute("tabindex")) card.setAttribute("tabindex", "0");
    card.setAttribute("role", "button");

    card.addEventListener("click", showWarning);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        showWarning();
      }
    });
  });

  console.log(`${featureCards.length} feature card(s) initialized`);
});

// Minimal toast helper (swap for your UI library's toast if you have one)
function showToast(message, duration = 2500) {
  let toast = document.getElementById("app-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "app-toast";
    toast.style.cssText = `
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
      background: #1f2937; color: #fff; padding: 10px 16px; border-radius: 8px;
      font-size: 14px; z-index: 9999; opacity: 0; transition: opacity 0.2s;
      pointer-events: none;
    `;
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.style.opacity = "1";
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => (toast.style.opacity = "0"), duration);
}