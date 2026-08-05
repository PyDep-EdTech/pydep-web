/**
 * PyDep — переключатель темы.
 * Лёгкий круговой reveal: один сплошной слой, анимация только через
 * transform: scale (композитинг GPU). Без клонирования DOM и маски.
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'pydep-theme';
    var THEMES = ['dark', 'light'];
    var META_COLORS = { dark: '#141416', light: '#f4f1ea' };
    var REVEAL_BG = {
        dark: 'radial-gradient(circle at center, rgba(255,176,32,.10), transparent 70%), #141416',
        light: 'radial-gradient(circle at center, rgba(255,176,32,.12), transparent 70%), #f4f1ea',
    };
    var REVEAL_DURATION = 560;
    var animating = false;

    function normalize(theme) {
        return THEMES.indexOf(theme) >= 0 ? theme : 'dark';
    }

    function prefersReducedMotion() {
        return (
            window.matchMedia &&
            window.matchMedia('(prefers-reduced-motion: reduce)').matches
        );
    }

    function preferredTheme() {
        try {
            var saved = localStorage.getItem(STORAGE_KEY);
            if (saved === 'light' || saved === 'dark') {
                return saved;
            }
        } catch (e) {}
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            return 'light';
        }
        return 'dark';
    }

    function syncToggleButtons(theme) {
        var isLight = theme === 'light';
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.setAttribute('aria-pressed', isLight ? 'true' : 'false');
            btn.setAttribute(
                'aria-label',
                isLight ? 'Включить тёмную тему' : 'Включить светлую тему'
            );
            btn.title = isLight ? 'Тёмная тема' : 'Светлая тема';
            var icon = btn.querySelector('i');
            if (icon) {
                icon.className = isLight ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
            }
        });
    }

    function applyTheme(theme, persist) {
        var next = normalize(theme);
        document.documentElement.setAttribute('data-theme', next);
        document.documentElement.setAttribute('data-bs-theme', next);

        var meta = document.querySelector('meta[name="theme-color"]');
        if (meta) {
            meta.setAttribute('content', META_COLORS[next]);
        }

        if (persist !== false) {
            try {
                localStorage.setItem(STORAGE_KEY, next);
            } catch (e) {}
        }

        syncToggleButtons(next);
        return next;
    }

    function getOrigin(btn) {
        if (btn && btn.getBoundingClientRect) {
            var rect = btn.getBoundingClientRect();
            return {
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2,
            };
        }
        return { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    }

    function getRevealRadius(x, y) {
        var w = window.innerWidth;
        var h = window.innerHeight;
        return Math.hypot(Math.max(x, w - x), Math.max(y, h - y)) + 24;
    }

    /* ── Основной путь: View Transitions API ──
       Браузер снимает старую/новую страницы как GPU-слои; анимируем
       только clip-path нового снимка — реальная новая тема «расходится»
       кругом из кнопки. Дёшево для композитора и эффектно. */
    function viewTransitionSwitch(nextTheme, origin, triggerBtn) {
        var endRadius = getRevealRadius(origin.x, origin.y);
        var cx = origin.x + 'px';
        var cy = origin.y + 'px';

        animating = true;
        if (triggerBtn) {
            triggerBtn.classList.add('is-switching');
        }
        document.documentElement.classList.add('vt-theming');

        var transition = document.startViewTransition(function () {
            applyTheme(nextTheme);
        });

        transition.ready
            .then(function () {
                document.documentElement.animate(
                    {
                        clipPath: [
                            'circle(0px at ' + cx + ' ' + cy + ')',
                            'circle(' + endRadius + 'px at ' + cx + ' ' + cy + ')',
                        ],
                    },
                    {
                        duration: 620,
                        easing: 'cubic-bezier(.22, .61, .36, 1)',
                        pseudoElement: '::view-transition-new(root)',
                    }
                );
            })
            .catch(function () {});

        transition.finished.finally(function () {
            document.documentElement.classList.remove('vt-theming');
            if (triggerBtn) {
                triggerBtn.classList.remove('is-switching');
            }
            animating = false;
        });
    }

    /* ── Fallback: сплошной слой растёт из кнопки (старые браузеры) ── */
    function veilSwitch(nextTheme, origin, triggerBtn) {
        animating = true;
        if (triggerBtn) {
            triggerBtn.classList.add('is-switching');
        }

        var size = getRevealRadius(origin.x, origin.y) * 2;
        var veil = document.createElement('div');
        veil.className = 'theme-reveal';
        veil.style.left = origin.x + 'px';
        veil.style.top = origin.y + 'px';
        veil.style.width = size + 'px';
        veil.style.height = size + 'px';
        veil.style.setProperty('--reveal-bg', REVEAL_BG[nextTheme] || REVEAL_BG.dark);
        veil.style.setProperty('--reveal-dur', REVEAL_DURATION + 'ms');
        document.body.appendChild(veil);

        var done = false;
        function finish() {
            if (done) {
                return;
            }
            done = true;
            applyTheme(nextTheme);
            if (veil.parentNode) {
                veil.parentNode.removeChild(veil);
            }
            if (triggerBtn) {
                triggerBtn.classList.remove('is-switching');
            }
            animating = false;
        }

        void veil.offsetWidth;
        veil.classList.add('is-armed');
        veil.addEventListener('transitionend', finish, { once: true });
        window.setTimeout(finish, REVEAL_DURATION + 120);
    }

    function toggleTheme(event) {
        var current = document.documentElement.getAttribute('data-theme') || 'dark';
        var next = current === 'dark' ? 'light' : 'dark';
        var btn = event && event.currentTarget;

        if (animating) {
            return next;
        }
        if (prefersReducedMotion()) {
            return applyTheme(next);
        }
        if (typeof document.startViewTransition === 'function') {
            viewTransitionSwitch(next, getOrigin(btn), btn);
        } else {
            veilSwitch(next, getOrigin(btn), btn);
        }
        return next;
    }

    window.PyDepTheme = {
        apply: applyTheme,
        toggle: toggleTheme,
        get: function () {
            return document.documentElement.getAttribute('data-theme') || 'dark';
        },
        preferred: preferredTheme,
    };

    document.addEventListener('DOMContentLoaded', function () {
        var current = document.documentElement.getAttribute('data-theme');
        if (!current) {
            applyTheme(preferredTheme(), false);
        } else {
            syncToggleButtons(normalize(current));
        }
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.addEventListener('click', toggleTheme);
        });
    });
})();
