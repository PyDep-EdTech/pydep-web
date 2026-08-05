/**
 * Расчёт длительности занятия и итоговой стоимости в форме урока.
 */
(function () {
    'use strict';

    function parseTime(value) {
        if (!value || !/^\d{2}:\d{2}/.test(value)) return null;
        const [h, m] = value.split(':').map(Number);
        return h * 60 + m;
    }

    function formatDuration(minutes) {
        if (minutes <= 0) return null;
        const h = Math.floor(minutes / 60);
        const m = minutes % 60;
        const parts = [];
        if (h) parts.push(`${h} ч`);
        if (m) parts.push(`${m} мин`);
        return parts.join(' ') || '0 мин';
    }

    function formatMoney(amount) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            maximumFractionDigits: amount % 1 === 0 ? 0 : 2,
        }).format(amount);
    }

    function init(options) {
        const startEl = document.getElementById(options.startId);
        const endEl = document.getElementById(options.endId);
        const rateEl = options.rateId ? document.getElementById(options.rateId) : null;
        const summaryEl = document.getElementById(options.summaryId);
        const durationEl = document.getElementById(options.durationTextId);
        const costWrapEl = options.costWrapId
            ? document.getElementById(options.costWrapId) : null;
        const costEl = options.costTextId
            ? document.getElementById(options.costTextId) : null;
        const warningEl = options.warningId
            ? document.getElementById(options.warningId) : null;

        if (!startEl || !endEl || !summaryEl || !durationEl) return null;

        function update() {
            const start = parseTime(startEl.value);
            const end = parseTime(endEl.value);

            if (start === null || end === null) {
                summaryEl.hidden = true;
                return;
            }

            summaryEl.hidden = false;
            const minutes = end > start ? end - start : 0;
            const durationText = formatDuration(minutes);

            if (!durationText) {
                summaryEl.classList.add('is-invalid');
                durationEl.textContent = 'Укажите корректное время';
                if (warningEl) warningEl.hidden = false;
                if (costWrapEl) costWrapEl.hidden = true;
                return;
            }

            summaryEl.classList.remove('is-invalid');
            durationEl.textContent = durationText;
            if (warningEl) warningEl.hidden = true;

            const rate = rateEl ? parseFloat(String(rateEl.value).replace(',', '.')) : NaN;
            if (costWrapEl && costEl && Number.isFinite(rate) && rate > 0) {
                const total = Math.round(rate * (minutes / 60) * 100) / 100;
                costEl.textContent = formatMoney(total);
                costWrapEl.hidden = false;
            } else if (costWrapEl) {
                costWrapEl.hidden = true;
            }
        }

        [startEl, endEl, rateEl].filter(Boolean).forEach((el) => {
            el.addEventListener('change', update);
            el.addEventListener('input', update);
        });

        update();
        return { update };
    }

    window.PyDepLessonDuration = { init };
})();
