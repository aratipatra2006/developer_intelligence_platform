/*
  ABOUT PAGE INTERACTIONS
  Developer Intelligence Platform

  - Marks <html> as JS-capable so CSS can safely hide/animate elements
    (page is fully visible and functional if this script never runs)
  - Types out each terminal window's command line, then reveals the
    rest of its output line by line, once it scrolls into view
  - Fades sections in on scroll
  - Adds a sticky-header blur state and a scroll progress bar
  - Wires up "copy" buttons on the terminal windows
*/

(function () {
    var docEl = document.documentElement;
    docEl.classList.add('js');

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* Scroll progress bar */

    var progressBar = document.getElementById('scrollProgress');

    function updateProgress() {
        if (!progressBar) return;
        var scrollTop = window.scrollY || docEl.scrollTop;
        var height = docEl.scrollHeight - docEl.clientHeight;
        var pct = height > 0 ? (scrollTop / height) * 100 : 0;
        progressBar.style.width = pct + '%';
    }

    /* Sticky header state */

    var header = document.getElementById('siteHeader');

    function updateHeader() {
        if (!header) return;
        if (window.scrollY > 10) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }

    function onScroll() {
        updateProgress();
        updateHeader();
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* Scroll-triggered section reveals */

    var revealEls = document.querySelectorAll('.reveal');

    if ('IntersectionObserver' in window && revealEls.length) {
        var revealObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

        revealEls.forEach(function (el) {
            revealObserver.observe(el);
        });
    } else {
        revealEls.forEach(function (el) {
            el.classList.add('in-view');
        });
    }

    /* Terminal typing effect */

    function typeText(el, fullText, speed, onDone) {
        if (reduceMotion) {
            el.textContent = fullText;
            if (onDone) onDone();
            return;
        }
        el.textContent = '';
        var i = 0;
        var timer = setInterval(function () {
            i += 1;
            el.textContent = fullText.slice(0, i);
            if (i >= fullText.length) {
                clearInterval(timer);
                if (onDone) onDone();
            }
        }, speed);
    }

    function revealLines(lines, stagger, onDone) {
        if (reduceMotion) {
            lines.forEach(function (line) { line.classList.add('show'); });
            if (onDone) onDone();
            return;
        }
        lines.forEach(function (line, index) {
            setTimeout(function () {
                line.classList.add('show');
                if (index === lines.length - 1 && onDone) {
                    setTimeout(onDone, 150);
                }
            }, index * stagger);
        });
    }

    function runTerminal(terminalEl) {
        var lines = Array.prototype.slice.call(terminalEl.querySelectorAll('.term-line'));
        var cmdLine = terminalEl.querySelector('.cmd-line');
        var cmdText = terminalEl.querySelector('.cmd-text');
        var cursor = terminalEl.querySelector('[data-cursor]');
        var otherLines = lines.filter(function (l) { return l !== cmdLine; });

        if (cmdLine) cmdLine.classList.add('show');

        function afterTyping() {
            revealLines(otherLines, 110, function () {
                if (cursor) cursor.classList.add('visible');
            });
        }

        if (cmdText) {
            var full = cmdText.getAttribute('data-full') || cmdText.textContent;
            typeText(cmdText, full, 40, afterTyping);
        } else {
            afterTyping();
        }
    }

    var terminals = document.querySelectorAll('[data-terminal]');

    if ('IntersectionObserver' in window && terminals.length) {
        var termObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    runTerminal(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });

        terminals.forEach(function (t) {
            termObserver.observe(t);
        });
    } else {
        terminals.forEach(runTerminal);
    }

    /* Copy buttons */

    var copyButtons = document.querySelectorAll('.copy-btn');

    copyButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var targetId = btn.getAttribute('data-copy-target');
            var target = document.getElementById(targetId);
            if (!target) return;

            var text = Array.prototype.slice.call(target.querySelectorAll('.term-line'))
                .map(function (line) { return line.textContent.trim(); })
                .join('\n');

            function showCopied() {
                var original = btn.textContent;
                btn.textContent = 'copied';
                btn.classList.add('copied');
                setTimeout(function () {
                    btn.textContent = original;
                    btn.classList.remove('copied');
                }, 1500);
            }

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(showCopied).catch(function () {
                    fallbackCopy(text, showCopied);
                });
            } else {
                fallbackCopy(text, showCopied);
            }
        });
    });

    function fallbackCopy(text, done) {
        var textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            /* no-op — clipboard unavailable */
        }
        document.body.removeChild(textarea);
        if (done) done();
    }
})();