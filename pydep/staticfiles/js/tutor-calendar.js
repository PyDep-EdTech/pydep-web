/**
 * Месячный календарь занятий для раздела «Мой репетитор».
 */
(function () {
    'use strict';

    const MONTHS = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
    ];
    const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

    function parseLessons(root) {
        const id = root.dataset.jsonId;
        const el = id ? document.getElementById(id) : null;
        if (!el) return [];
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            console.error('Calendar lessons JSON error', e);
            return [];
        }
    }

    function lessonStatus(l) {
        if (l.isCanceled) {
            return { text: 'Отменено', mod: 'is-muted' };
        }
        if (!l.hasEnded) {
            return { text: l.statusLabel || 'Запланировано', mod: 'is-future' };
        }
        if (l.isPaid) {
            return { text: 'Оплачено', mod: 'is-paid' };
        }
        return { text: 'К оплате', mod: 'is-due' };
    }

    function dotClass(l) {
        if (l.isCanceled) return 'is-muted';
        if (!l.hasEnded) return 'is-future';
        if (l.isPaid) return 'is-paid';
        return 'is-due';
    }

    function initCalendar(root) {
        const lessons = parseLessons(root);
        const canEdit = root.dataset.canEdit === 'true';
        const now = new Date();
        let year = now.getFullYear();
        let month = now.getMonth();

        const head = root.querySelector('.tutor-cal__head');
        const titleEl = root.querySelector('.tutor-cal__title');
        const grid = root.querySelector('.tutor-cal__grid');
        const detail = root.querySelector('.tutor-cal__detail');

        if (!head || !titleEl || !grid) return;

        function lessonsOnDay(dateStr) {
            return lessons
                .filter((l) => l.date === dateStr)
                .sort((a, b) => a.start.localeCompare(b.start));
        }

        function renderDetail(dayLessons, dateStr) {
            if (!detail) return;
            if (!dayLessons.length) {
                detail.hidden = true;
                detail.innerHTML = '';
                return;
            }
            const d = new Date(dateStr + 'T12:00:00');
            const heading = d.toLocaleDateString('ru-RU', {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
            });
            let html = `<div class="tutor-cal__detail-title">${heading}</div><div class="tutor-cal__cards">`;
            dayLessons.forEach((l) => {
                const st = lessonStatus(l);
                const meta = [l.person, l.format].filter(Boolean).join(' · ');
                const cost = l.totalCost ? `${l.totalCost} ₽` : '';
                const href = canEdit && l.editUrl ? l.editUrl : null;
                const tag = href ? 'a' : 'article';
                const attrs = href
                    ? `href="${href}" class="tutor-cal__card ${st.mod}"`
                    : `class="tutor-cal__card ${st.mod}"`;
                html += `
                  <${tag} ${attrs}>
                    <div class="tutor-cal__card-top">
                      <span class="tutor-cal__card-time">${l.start}–${l.end}</span>
                      <span class="tutor-cal__card-status">${st.text}</span>
                    </div>
                    <strong class="tutor-cal__card-title">${l.title}</strong>
                    <p class="tutor-cal__card-meta">${meta}${cost ? ` · ${cost}` : ''}</p>
                    ${href ? '<span class="tutor-cal__card-link">Открыть <i class="bi bi-arrow-right-short"></i></span>' : ''}
                  </${tag}>`;
            });
            html += '</div>';
            detail.hidden = false;
            detail.innerHTML = html;
        }

        function selectDay(btn, dateStr) {
            grid.querySelectorAll('.tutor-cal__day').forEach((el) => {
                el.classList.remove('is-selected');
            });
            btn.classList.add('is-selected');
            renderDetail(lessonsOnDay(dateStr), dateStr);
        }

        function render() {
            titleEl.textContent = `${MONTHS[month]} ${year}`;

            const first = new Date(year, month, 1);
            const startOffset = (first.getDay() + 6) % 7;
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const todayStr = [
                now.getFullYear(),
                String(now.getMonth() + 1).padStart(2, '0'),
                String(now.getDate()).padStart(2, '0'),
            ].join('-');

            let html = '<div class="tutor-cal__weekdays">';
            WEEKDAYS.forEach((w) => { html += `<span>${w}</span>`; });
            html += '</div><div class="tutor-cal__days">';

            for (let i = 0; i < startOffset; i++) {
                html += '<div class="tutor-cal__day tutor-cal__day--empty"></div>';
            }

            for (let day = 1; day <= daysInMonth; day++) {
                const dateStr = [
                    year,
                    String(month + 1).padStart(2, '0'),
                    String(day).padStart(2, '0'),
                ].join('-');
                const dayLessons = lessonsOnDay(dateStr);
                const isToday = dateStr === todayStr;
                const classes = [
                    'tutor-cal__day',
                    dayLessons.length ? 'has-events' : '',
                    isToday ? 'is-today' : '',
                ].filter(Boolean).join(' ');

                let dots = '<div class="tutor-cal__dots">';
                dayLessons.slice(0, 4).forEach((l) => {
                    dots += `<span class="tutor-cal__dot ${dotClass(l)}"></span>`;
                });
                if (dayLessons.length > 4) {
                    dots += `<span class="tutor-cal__more">+${dayLessons.length - 4}</span>`;
                }
                dots += '</div>';

                html += `
                  <button type="button" class="${classes}" data-date="${dateStr}" aria-label="${day} ${MONTHS[month]}">
                    <span class="tutor-cal__num">${day}</span>
                    ${dots}
                  </button>`;
            }
            html += '</div>';
            grid.innerHTML = html;

            grid.querySelectorAll('.tutor-cal__day[data-date]').forEach((btn) => {
                btn.addEventListener('click', () => selectDay(btn, btn.dataset.date));
            });

            const preferred = grid.querySelector(`.tutor-cal__day[data-date="${todayStr}"]`)
                || grid.querySelector('.tutor-cal__day.has-events');
            if (preferred) {
                selectDay(preferred, preferred.dataset.date);
            } else if (detail) {
                detail.hidden = true;
                detail.innerHTML = '';
            }
        }

        head.querySelector('[data-cal-prev]')?.addEventListener('click', () => {
            month -= 1;
            if (month < 0) { month = 11; year -= 1; }
            render();
        });
        head.querySelector('[data-cal-next]')?.addEventListener('click', () => {
            month += 1;
            if (month > 11) { month = 0; year += 1; }
            render();
        });
        head.querySelector('[data-cal-today]')?.addEventListener('click', () => {
            year = now.getFullYear();
            month = now.getMonth();
            render();
        });

        render();
    }

    function setPaneView(group, view) {
        const pane = group.closest('.tab-pane')
            || group.closest('.container')
            || group.parentElement;
        if (!pane) return;
        const listView = pane.querySelector('.schedule-list-view');
        const calView = pane.querySelector('.schedule-calendar-view');
        group.querySelectorAll('[data-view]').forEach((btn) => {
            const active = btn.dataset.view === view;
            btn.classList.toggle('active', active);
            btn.classList.toggle('btn-primary', active);
            btn.classList.toggle('btn-ghost', !active);
        });
        if (listView) listView.hidden = view !== 'list';
        if (calView) calView.hidden = view !== 'calendar';
    }

    function initViewSwitch() {
        document.querySelectorAll('[data-schedule-view]').forEach((group) => {
            const defaultView = group.dataset.defaultView || 'calendar';
            group.querySelectorAll('[data-view]').forEach((btn) => {
                btn.addEventListener('click', () => setPaneView(group, btn.dataset.view));
            });
            setPaneView(group, defaultView);
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.tutor-calendar').forEach(initCalendar);
        initViewSwitch();
    });
})();
