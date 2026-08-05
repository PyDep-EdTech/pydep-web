/**
 * Конфетти при полном завершении курса.
 */
(function () {
    var canvas = document.createElement('canvas');
    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.cssText =
        'position:fixed;inset:0;z-index:10060;pointer-events:none;width:100%;height:100%';
    document.body.appendChild(canvas);

    var ctx = canvas.getContext('2d');
    var particles = [];
    var colors = ['#FFB020', '#FF9D2E', '#FFC24B', '#54D6B4', '#F1EFEA', '#E8920A'];
    var running = true;
    var frame = 0;
    var maxFrames = 280;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function spawn(count) {
        for (var i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: -20 - Math.random() * canvas.height * 0.4,
                w: 6 + Math.random() * 8,
                h: 10 + Math.random() * 14,
                color: colors[Math.floor(Math.random() * colors.length)],
                vx: -2 + Math.random() * 4,
                vy: 2 + Math.random() * 5,
                rot: Math.random() * Math.PI,
                vr: -0.15 + Math.random() * 0.3,
                opacity: 0.85 + Math.random() * 0.15,
            });
        }
    }

    function tick() {
        if (!running) return;
        frame += 1;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (var i = particles.length - 1; i >= 0; i--) {
            var p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.06;
            p.rot += p.vr;

            ctx.save();
            ctx.globalAlpha = p.opacity * Math.max(0, 1 - frame / maxFrames);
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rot);
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
            ctx.restore();

            if (p.y > canvas.height + 40) {
                particles.splice(i, 1);
            }
        }

        if (frame < maxFrames) {
            if (frame % 12 === 0) spawn(14);
            requestAnimationFrame(tick);
        } else {
            running = false;
            canvas.remove();
        }
    }

    resize();
    window.addEventListener('resize', resize);
    spawn(120);
    requestAnimationFrame(tick);
})();
