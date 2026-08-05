/* PyDep motion: intro splash, page-enter stagger, platform transition. */
(function () {
    'use strict';

    var reduce = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function resetTransition() {
        var overlay = document.getElementById('fx-transition');
        if (!overlay) return;
        overlay.classList.remove('is-active');
        overlay.style.clipPath = '';
    }

    window.addEventListener('pageshow', function (e) {
        if (e.persisted) {
            resetTransition();
            document.documentElement.classList.remove('intro');
        }
    });
    window.addEventListener('pagehide', resetTransition);

    /* ---------- Logo build ---------- */
    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    function easeOutBack(t) {
        var c1 = 1.70158;
        var c3 = c1 + 1;
        return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
    }

    function resetPart(part) {
        if (part.getAnimations) {
            part.getAnimations().forEach(function (a) { a.cancel(); });
        }
        part.style.opacity = '';
        part.style.transform = '';
    }

    function showPart(part) {
        if (part.getAnimations) {
            part.getAnimations().forEach(function (a) { a.cancel(); });
        }
        part.style.opacity = '1';
        part.style.transform = 'none';
    }

    function fitLogoViewBox(svg) {
        if (!svg || typeof svg.getBBox !== 'function') return;

        svg.querySelectorAll('.platform-logo__part').forEach(showPart);

        var bb;
        try {
            bb = svg.getBBox();
        } catch (e) {
            return;
        }
        if (!bb.width && !bb.height) return;

        var pad = Math.max(bb.width, bb.height) * 0.08;
        var side = Math.max(bb.width, bb.height) + pad * 2;
        var cx = bb.x + bb.width / 2;
        var cy = bb.y + bb.height / 2;

        svg.setAttribute('viewBox', [
            (cx - side / 2).toFixed(2),
            (cy - side / 2).toFixed(2),
            side.toFixed(2),
            side.toFixed(2)
        ].join(' '));
        svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    }

    function layoutLogo(svg) {
        if (!svg) return;
        fitLogoViewBox(svg);
    }

    function prepPart(part) {
        part.style.transformBox = 'fill-box';
        part.style.transformOrigin = part.getAttribute('data-origin') || 'center center';
        part.style.opacity = '0';
        part.style.transform = 'none';
    }

    function animateWithKeyframes(part, keyframes, delayMs, durMs, easing) {
        prepPart(part);
        if (!part.animate) {
            showPart(part);
            return delayMs + durMs;
        }
        part.animate(keyframes, {
            duration: durMs,
            delay: delayMs,
            fill: 'forwards',
            easing: easing || 'cubic-bezier(.22,.61,.36,1)'
        });
        return delayMs + durMs;
    }

    function animateSnake(part, delayMs, durMs) {
        prepPart(part);
        if (reduce) {
            showPart(part);
            return delayMs;
        }
        var start = null;
        function frame(ts) {
            if (start === null) start = ts;
            var elapsed = ts - start;
            if (elapsed < delayMs) {
                requestAnimationFrame(frame);
                return;
            }
            var t = Math.min(1, (elapsed - delayMs) / durMs);
            var ease = easeOutCubic(t);
            // Дуга сверху-слева с извиванием змейки
            var arc = Math.sin(t * Math.PI * 0.85);
            var x = (-55 + arc * 18) * (1 - ease) + Math.sin(t * Math.PI * 5) * 12 * (1 - t);
            var y = (-95 * (1 - ease)) + Math.cos(t * Math.PI * 3) * 6 * (1 - t);
            var rot = -22 * (1 - ease) + Math.sin(t * Math.PI * 4) * 7 * (1 - t);
            var scale = 0.75 + 0.25 * easeOutBack(Math.min(1, t * 1.05));
            if (t > 0.78) {
                y += Math.sin((t - 0.78) / 0.22 * Math.PI) * 6;
            }
            part.style.opacity = String(Math.min(1, t * 2));
            part.style.transform =
                'translate(' + x.toFixed(2) + 'px,' + y.toFixed(2) + 'px) ' +
                'rotate(' + rot.toFixed(2) + 'deg) ' +
                'scale(' + scale.toFixed(3) + ')';
            if (t < 1) {
                requestAnimationFrame(frame);
            } else {
                showPart(part);
            }
        }
        requestAnimationFrame(frame);
        return delayMs + durMs;
    }

    var PRESETS = {
        'flip-in': function () {
            return [
                { opacity: 0, transform: 'translateX(-36px) rotate(-18deg) scale(0.5)' },
                { opacity: 1, transform: 'translateX(4px) rotate(3deg) scale(1.04)', offset: 0.7 },
                { opacity: 1, transform: 'translateX(0) rotate(0deg) scale(1)' }
            ];
        },
        'fly-right': function () {
            return [
                { opacity: 0, transform: 'translate(72px,-28px) rotate(8deg) scale(0.78)' },
                { opacity: 1, transform: 'translate(-6px,3px) rotate(-2deg) scale(1.03)', offset: 0.72 },
                { opacity: 1, transform: 'translate(0,0) rotate(0deg) scale(1)' }
            ];
        },
        'fly-left': function () {
            return [
                { opacity: 0, transform: 'translate(-68px,-20px) rotate(-10deg) scale(0.8)' },
                { opacity: 1, transform: 'translate(5px,2px) rotate(2deg) scale(1.02)', offset: 0.72 },
                { opacity: 1, transform: 'translate(0,0) rotate(0deg) scale(1)' }
            ];
        },
        'swing-in': function () {
            return [
                { opacity: 0, transform: 'translateX(64px) rotate(24deg) scale(0.7)' },
                { opacity: 1, transform: 'translateX(-8px) rotate(-6deg) scale(1.05)', offset: 0.55 },
                { opacity: 1, transform: 'translateX(3px) rotate(2deg) scale(0.98)', offset: 0.78 },
                { opacity: 1, transform: 'translateX(0) rotate(0deg) scale(1)' }
            ];
        },
        'orbit-pop': function () {
            return [
                { opacity: 0, transform: 'translate(-22px,-22px) scale(0)' },
                { opacity: 1, transform: 'translate(6px,-8px) scale(1.35)', offset: 0.55 },
                { opacity: 1, transform: 'translate(-2px,2px) scale(0.92)', offset: 0.78 },
                { opacity: 1, transform: 'translate(0,0) scale(1)' }
            ];
        },
        pop: function () {
            return [
                { opacity: 0, transform: 'scale(0.1)' },
                { opacity: 1, transform: 'scale(1.18)', offset: 0.68 },
                { opacity: 1, transform: 'scale(1)' }
            ];
        },
        'slide-right': function () {
            return [
                { opacity: 0, transform: 'translateX(52px) scale(0.92)' },
                { opacity: 1, transform: 'translateX(-4px) scale(1.02)', offset: 0.78 },
                { opacity: 1, transform: 'translateX(0) scale(1)' }
            ];
        },
        'slide-left': function () {
            return [
                { opacity: 0, transform: 'translateX(-52px) rotate(6deg) scale(0.92)' },
                { opacity: 1, transform: 'translateX(3px) rotate(-1deg) scale(1.02)', offset: 0.78 },
                { opacity: 1, transform: 'translateX(0) rotate(0deg) scale(1)' }
            ];
        },
        rise: function () {
            return [
                { opacity: 0, transform: 'translateY(48px) scale(0.86)' },
                { opacity: 1, transform: 'translateY(-5px) scale(1.03)', offset: 0.72 },
                { opacity: 1, transform: 'translateY(0) scale(1)' }
            ];
        },
        drop: function () {
            return [
                { opacity: 0, transform: 'translateY(-52px) scale(0.9)' },
                { opacity: 1, transform: 'translateY(6px) scale(1.02)', offset: 0.78 },
                { opacity: 1, transform: 'translateY(0) scale(1)' }
            ];
        },
        'drop-flip': function () {
            return [
                { opacity: 0, transform: 'translateY(-56px) rotate(-14deg) scale(0.84)' },
                { opacity: 1, transform: 'translateY(7px) rotate(4deg) scale(1.03)', offset: 0.7 },
                { opacity: 1, transform: 'translateY(0) rotate(0deg) scale(1)' }
            ];
        },
        'drop-bounce': function () {
            return [
                { opacity: 0, transform: 'translateY(-50px) scale(0.82)' },
                { opacity: 1, transform: 'translateY(8px) scale(1.04)', offset: 0.65 },
                { opacity: 1, transform: 'translateY(-3px) scale(0.98)', offset: 0.85 },
                { opacity: 1, transform: 'translateY(0) scale(1)' }
            ];
        },
        'fade-scale': function () {
            return [
                { opacity: 0, transform: 'scale(0.8)' },
                { opacity: 1, transform: 'scale(1)' }
            ];
        },
        spark: function () {
            return [
                { opacity: 0, transform: 'scale(0) rotate(-50deg)' },
                { opacity: 1, transform: 'scale(1.3) rotate(12deg)', offset: 0.6 },
                { opacity: 1, transform: 'scale(0.95) rotate(-3deg)', offset: 0.82 },
                { opacity: 1, transform: 'scale(1) rotate(0deg)' }
            ];
        }
    };

    function animatePart(part) {
        var type = part.getAttribute('data-anim') || 'pop';
        var delay = parseFloat(part.getAttribute('data-delay') || '0') * 1000;
        var dur = parseFloat(part.getAttribute('data-dur') || '0.65') * 1000;

        if (reduce) {
            showPart(part);
            return delay;
        }

        if (type === 'snake') {
            return animateSnake(part, delay, dur);
        }

        var preset = PRESETS[type];
        if (!preset) {
            showPart(part);
            return delay;
        }

        var bounceTypes = { pop: 1, spark: 1, 'orbit-pop': 1 };
        return animateWithKeyframes(
            part,
            preset(),
            delay,
            dur,
            bounceTypes[type]
                ? 'cubic-bezier(.34,1.45,.64,1)'
                : 'cubic-bezier(.22,.61,.36,1)'
        );
    }

    function pulseGlow(stage, afterMs) {
        if (reduce || !stage) return;
        var glow = stage.querySelector('.fx-logo-glow');
        if (!glow || !glow.animate) return;
        setTimeout(function () {
            glow.animate([
                { opacity: glow.style.opacity || 0.45, transform: 'scale(1)' },
                { opacity: 0.75, transform: 'scale(1.14)' },
                { opacity: 0.45, transform: 'scale(1)' }
            ], { duration: 480, easing: 'ease-out' });
        }, afterMs);
    }

    function finalizeLogo(svg) {
        if (!svg) return;
        svg.style.transform = '';
        svg.querySelectorAll('.platform-logo__part').forEach(showPart);
        fitLogoViewBox(svg);
    }

    function runLogoBuild(svg) {
        if (!svg) return;
        var parts = svg.querySelectorAll('.platform-logo__part');
        if (!parts.length) return;

        function start() {
            try { layoutLogo(svg); } catch (e) {}

            var stage = svg.closest('.fx-logo-stage');
            var endAt = 0;

            parts.forEach(function (part) {
                resetPart(part);
                var finish = animatePart(part);
                if (finish > endAt) endAt = finish;
            });

            pulseGlow(stage, endAt + 60);
            setTimeout(function () { finalizeLogo(svg); }, endAt + 120);
        }

        requestAnimationFrame(function () {
            requestAnimationFrame(start);
        });
    }

    function playIntroLogo() {
        if (!document.documentElement.classList.contains('intro')) return;
        var intro = document.getElementById('fx-intro');
        if (!intro) return;
        var svg = intro.querySelector('.platform-logo.fx-logo') || intro.querySelector('.platform-logo');
        if (svg) runLogoBuild(svg);
        window.setTimeout(function () {
            document.documentElement.classList.remove('intro');
        }, 2600);
    }

    function playTransitionLogo(platform) {
        if (!overlay) return;
        var svg = overlay.querySelector('.fx-tr-badge--' + platform);
        if (svg) runLogoBuild(svg);
    }

    function bootIntroLogo() {
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                playIntroLogo();
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootIntroLogo);
    } else {
        bootIntroLogo();
    }

    /* ---------- Platform transition ---------- */
    function platformOf(path) {
        if (/^\/tutor(\/|$)/.test(path)) return 'tutor';
        if (/^\/studio(\/|$)/.test(path)) return 'studio';
        return 'pydep';
    }
    var TRANSITION_DELAY = 2500;
    var current = platformOf(window.location.pathname);
    var overlay = document.getElementById('fx-transition');

    function showTransition(target, href) {
        if (!overlay) { window.location.href = href; return; }
        try { sessionStorage.setItem(target + '_intro', '1'); } catch (e) {}
        overlay.setAttribute('data-platform', target);
        overlay.classList.remove('is-active');
        void overlay.offsetWidth;
        overlay.classList.add('is-active');
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                playTransitionLogo(target);
            });
        });
        setTimeout(function () { window.location.href = href; }, TRANSITION_DELAY);
    }

    function isPlainLeftClick(e) {
        return e.button === 0 && !e.metaKey && !e.ctrlKey &&
            !e.shiftKey && !e.altKey;
    }

    document.addEventListener('click', function (e) {
        if (reduce) return;
        var a = e.target.closest && e.target.closest('a');
        if (!a || !isPlainLeftClick(e)) return;
        if (a.target === '_blank' || a.hasAttribute('download')) return;
        var href = a.getAttribute('href');
        if (!href || href[0] === '#' || /^(mailto:|tel:|javascript:)/i.test(href)) return;

        var url;
        try { url = new URL(href, window.location.href); } catch (err) { return; }
        if (url.origin !== window.location.origin) return;
        if (/logout/i.test(url.pathname)) return;

        var target = platformOf(url.pathname);
        if (target === current) return;

        e.preventDefault();
        showTransition(target, url.href);
    }, true);

})();
