/**
 * Кастомные выпадающие пикеры даты и времени в стиле PyDep.
 * Заменяют нативные OS-виджеты, которые нельзя стилизовать.
 */
(function () {
    'use strict';

    const MONTHS = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
    ];
    const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

    let activePopover = null;
    let activeInput = null;

    function pad2(n) {
        return String(n).padStart(2, '0');
    }

    function todayParts() {
        const n = new Date();
        return { y: n.getFullYear(), m: n.getMonth(), d: n.getDate() };
    }

    function parseDateValue(value) {
        if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
        const [y, m, d] = value.split('-').map(Number);
        return { y, m: m - 1, d };
    }

    function parseTimeValue(value) {
        if (!value || !/^\d{2}:\d{2}/.test(value)) return null;
        const [h, min] = value.split(':').map(Number);
        return { h, min };
    }

    function closePopover() {
        if (activePopover) {
            if (activePopover._cleanup) activePopover._cleanup();
            activePopover.remove();
            activePopover = null;
            activeInput = null;
        }
    }

    function positionPopover(popover, anchor) {
        const rect = anchor.getBoundingClientRect();
        const margin = 8;
        popover.style.position = 'fixed';
        popover.style.zIndex = '1090';
        popover.style.minWidth = `${Math.max(rect.width, 280)}px`;

        const width = popover.offsetWidth;
        let left = rect.left;
        if (left + width > window.innerWidth - margin) {
            left = window.innerWidth - width - margin;
        }
        if (left < margin) left = margin;

        let top = rect.bottom + 6;
        const height = popover.offsetHeight;
        if (top + height > window.innerHeight - margin) {
            top = rect.top - height - 6;
        }
        if (top < margin) top = margin;

        popover.style.left = `${left}px`;
        popover.style.top = `${top}px`;
    }

    function scrollListToSelected(list) {
        const item = list?.querySelector('.is-selected');
        if (!item || !list) return;
        const top = item.offsetTop - (list.clientHeight / 2) + (item.clientHeight / 2);
        list.scrollTop = Math.max(0, top);
    }

    function bindDismiss(popover, input) {
        const onDoc = (e) => {
            if (popover.contains(e.target) || e.target === input) return;
            closePopover();
        };
        const onKey = (e) => {
            if (e.key === 'Escape') closePopover();
        };
        const onScroll = (e) => {
            if (e.target instanceof Node && popover.contains(e.target)) return;
            closePopover();
        };

        setTimeout(() => {
            document.addEventListener('mousedown', onDoc);
            document.addEventListener('keydown', onKey);
            window.addEventListener('resize', closePopover);
            window.addEventListener('scroll', onScroll, true);
        }, 0);

        popover._cleanup = () => {
            document.removeEventListener('mousedown', onDoc);
            document.removeEventListener('keydown', onKey);
            window.removeEventListener('resize', closePopover);
            window.removeEventListener('scroll', onScroll, true);
        };
    }

    function openDatePicker(input) {
        if (activeInput === input && activePopover) return;
        closePopover();
        activeInput = input;

        const selected = parseDateValue(input.value);
        const now = todayParts();
        let year = selected ? selected.y : now.y;
        let month = selected ? selected.m : now.m;

        const popover = document.createElement('div');
        popover.className = 'platform-picker platform-picker--date';
        popover.setAttribute('role', 'dialog');
        popover.setAttribute('aria-label', 'Выбор даты');

        function renderDays() {
            const first = new Date(year, month, 1);
            const startOffset = (first.getDay() + 6) % 7;
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const today = todayParts();
            const todayStr = `${today.y}-${pad2(today.m + 1)}-${pad2(today.d)}`;

            let daysHtml = '';
            for (let i = 0; i < startOffset; i++) {
                daysHtml += '<span class="platform-picker__day platform-picker__day--empty"></span>';
            }
            for (let day = 1; day <= daysInMonth; day++) {
                const dateStr = `${year}-${pad2(month + 1)}-${pad2(day)}`;
                const isToday = dateStr === todayStr;
                const isSelected = input.value === dateStr;
                const cls = [
                    'platform-picker__day',
                    isToday ? 'is-today' : '',
                    isSelected ? 'is-selected' : '',
                ].filter(Boolean).join(' ');
                daysHtml += `<button type="button" class="${cls}" data-date="${dateStr}">${day}</button>`;
            }

            popover.innerHTML = `
              <div class="platform-picker__head">
                <button type="button" class="platform-picker__nav" data-dir="prev" aria-label="Предыдущий месяц">
                  <i class="bi bi-chevron-left"></i>
                </button>
                <div class="platform-picker__title">${MONTHS[month]} ${year}</div>
                <button type="button" class="platform-picker__nav" data-dir="next" aria-label="Следующий месяц">
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
              <div class="platform-picker__weekdays">
                ${WEEKDAYS.map((w) => `<span>${w}</span>`).join('')}
              </div>
              <div class="platform-picker__days">${daysHtml}</div>
              <div class="platform-picker__foot">
                <button type="button" class="platform-picker__foot-btn" data-action="today">Сегодня</button>
                <button type="button" class="platform-picker__foot-btn" data-action="clear">Очистить</button>
              </div>`;

            popover.querySelector('[data-dir="prev"]')?.addEventListener('click', (e) => {
                e.stopPropagation();
                month -= 1;
                if (month < 0) { month = 11; year -= 1; }
                renderDays();
                positionPopover(popover, input);
            });
            popover.querySelector('[data-dir="next"]')?.addEventListener('click', (e) => {
                e.stopPropagation();
                month += 1;
                if (month > 11) { month = 0; year += 1; }
                renderDays();
                positionPopover(popover, input);
            });
            popover.querySelector('[data-action="today"]')?.addEventListener('click', (e) => {
                e.stopPropagation();
                input.value = todayStr;
                input.dispatchEvent(new Event('change', { bubbles: true }));
                closePopover();
            });
            popover.querySelector('[data-action="clear"]')?.addEventListener('click', (e) => {
                e.stopPropagation();
                input.value = '';
                input.dispatchEvent(new Event('change', { bubbles: true }));
                closePopover();
            });
            popover.querySelectorAll('[data-date]').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    input.value = btn.dataset.date;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    closePopover();
                });
            });
        }

        document.body.appendChild(popover);
        activePopover = popover;
        renderDays();
        positionPopover(popover, input);
        bindDismiss(popover, input);
        popover.addEventListener('mousedown', (e) => e.preventDefault());
    }

    function openTimePicker(input) {
        if (activeInput === input && activePopover) return;
        closePopover();
        activeInput = input;

        const selected = parseTimeValue(input.value);
        let hour = selected ? selected.h : 10;
        let minute = selected ? selected.min : 0;

        const popover = document.createElement('div');
        popover.className = 'platform-picker platform-picker--time';
        popover.setAttribute('role', 'dialog');
        popover.setAttribute('aria-label', 'Выбор времени');

        const hours = Array.from({ length: 24 }, (_, i) => i);
        const minutes = Array.from({ length: 60 }, (_, i) => i);

        function renderTime() {
            popover.innerHTML = `
              <div class="platform-picker__head platform-picker__head--time">
                <div class="platform-picker__title">Время</div>
                <div class="platform-picker__time-preview">${pad2(hour)}:${pad2(minute)}</div>
              </div>
              <div class="platform-picker__time-cols">
                <div class="platform-picker__time-col">
                  <div class="platform-picker__time-label">Часы</div>
                  <div class="platform-picker__time-list" data-part="hour">
                    ${hours.map((h) => `
                      <button type="button" class="platform-picker__time-item${h === hour ? ' is-selected' : ''}" data-hour="${h}">
                        ${pad2(h)}
                      </button>`).join('')}
                  </div>
                </div>
                <div class="platform-picker__time-col">
                  <div class="platform-picker__time-label">Минуты</div>
                  <div class="platform-picker__time-list" data-part="minute">
                    ${minutes.map((m) => `
                      <button type="button" class="platform-picker__time-item${m === minute ? ' is-selected' : ''}" data-minute="${m}">
                        ${pad2(m)}
                      </button>`).join('')}
                  </div>
                </div>
              </div>
              <div class="platform-picker__foot">
                <button type="button" class="platform-picker__foot-btn" data-action="now">Сейчас</button>
                <button type="button" class="platform-picker__foot-btn platform-picker__foot-btn--primary" data-action="apply">Готово</button>
              </div>`;

            const hourList = popover.querySelector('[data-part="hour"]');
            const minList = popover.querySelector('[data-part="minute"]');
            scrollListToSelected(hourList);
            scrollListToSelected(minList);

            popover.querySelectorAll('[data-hour]').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    hour = Number(btn.dataset.hour);
                    renderTime();
                    positionPopover(popover, input);
                });
            });
            popover.querySelectorAll('[data-minute]').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    minute = Number(btn.dataset.minute);
                    renderTime();
                    positionPopover(popover, input);
                });
            });
            popover.querySelector('[data-action="now"]')?.addEventListener('click', (e) => {
                e.stopPropagation();
                const n = new Date();
                hour = n.getHours();
                minute = n.getMinutes();
                renderTime();
                positionPopover(popover, input);
            });
            popover.querySelector('[data-action="apply"]')?.addEventListener('click', (e) => {
                e.stopPropagation();
                input.value = `${pad2(hour)}:${pad2(minute)}`;
                input.dispatchEvent(new Event('change', { bubbles: true }));
                closePopover();
            });
        }

        document.body.appendChild(popover);
        activePopover = popover;
        renderTime();
        positionPopover(popover, input);
        bindDismiss(popover, input);
        popover.addEventListener('mousedown', (e) => e.preventDefault());
    }

    function initInput(input) {
        if (input.dataset.platformPickerInit) return;
        input.dataset.platformPickerInit = '1';

        const kind = input.classList.contains('platform-input-time')
            || input.type === 'time'
            ? 'time'
            : 'date';

        input.readOnly = true;
        input.setAttribute('inputmode', 'none');
        input.classList.add('platform-picker-input');

        let openedFromMouse = false;

        const open = (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (kind === 'time') openTimePicker(input);
            else openDatePicker(input);
        };

        input.addEventListener('mousedown', (e) => {
            openedFromMouse = true;
            open(e);
            setTimeout(() => { openedFromMouse = false; }, 0);
        });
        input.addEventListener('focus', (e) => {
            if (openedFromMouse) return;
            open(e);
        });
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                open(e);
            }
        });
    }

    function init(root) {
        const scope = root || document;
        scope.querySelectorAll(
            '.platform-input-date, .platform-input-time, '
            + '.platform-datetime-field input[type="date"], '
            + '.platform-datetime-field input[type="time"]'
        ).forEach(initInput);
    }

    document.addEventListener('DOMContentLoaded', () => init());

    window.PyDepPlatformPicker = { init, close: closePopover };
})();
