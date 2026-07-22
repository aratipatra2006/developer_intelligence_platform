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

const featureCards = document.querySelectorAll(".card.feature-card");

featureCards.forEach((card) => {
    card.addEventListener("click", function () {
        alert("⚠️ Please analyze a repository first.");
    });
});

console.log(featureCards.length);
console.log("JS Loaded");