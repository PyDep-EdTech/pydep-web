/**
 * PyDep Studio — модальное окно выбора модуля/урока с поиском
 */
(function () {
    'use strict';

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function cardHtml(item, iconClass) {
        var subtitle = item.subtitle
            ? '<span class="student-picker-card__login">' + escapeHtml(item.subtitle) + '</span>'
            : '';
        return (
            '<button type="button" class="student-picker-card studio-picker-card" data-item-id="' +
            item.id +
            '">' +
            '<span class="studio-picker-card__icon"><i class="bi ' +
            escapeHtml(iconClass) +
            '"></i></span>' +
            '<span class="studio-picker-card__text">' +
            '<span class="student-picker-card__name">' +
            escapeHtml(item.title) +
            '</span>' +
            subtitle +
            '</span>' +
            '</button>'
        );
    }

    function filterItems(items, query) {
        var q = (query || '').trim().toLowerCase();
        if (!q) {
            return items;
        }
        return items.filter(function (item) {
            return (
                String(item.title).toLowerCase().includes(q) ||
                String(item.subtitle || '').toLowerCase().includes(q)
            );
        });
    }

    window.PyDepStudioAttachPicker = {
        init: function (config) {
            var modalEl = document.getElementById(config.modalId);
            var gridEl = document.getElementById(config.gridId);
            var searchEl = document.getElementById(config.searchId);
            var formEl = document.getElementById(config.formId);
            var idInputEl = document.getElementById(config.idInputId);
            var triggerEl = config.triggerId
                ? document.getElementById(config.triggerId)
                : null;
            var items = config.items || [];
            var iconClass = config.iconClass || 'bi-file-earmark-text';

            if (!modalEl || !gridEl || !formEl || !idInputEl) {
                return;
            }

            var modal = bootstrap.Modal.getOrCreateInstance(modalEl);

            function renderGrid(list) {
                if (!list.length) {
                    gridEl.innerHTML =
                        '<div class="student-picker-empty">' +
                        '<i class="bi bi-search"></i>' +
                        '<p>Ничего не найдено</p>' +
                        '</div>';
                    return;
                }
                gridEl.innerHTML = list
                    .map(function (item) {
                        return cardHtml(item, iconClass);
                    })
                    .join('');
            }

            function openModal() {
                if (searchEl) {
                    searchEl.value = '';
                }
                renderGrid(items);
                modal.show();
                window.setTimeout(function () {
                    if (searchEl) {
                        searchEl.focus();
                    }
                }, 200);
            }

            if (triggerEl) {
                triggerEl.addEventListener('click', openModal);
            }

            if (searchEl) {
                searchEl.addEventListener('input', function () {
                    renderGrid(filterItems(items, searchEl.value));
                });
            }

            gridEl.addEventListener('click', function (event) {
                var card = event.target.closest('.student-picker-card');
                if (!card) {
                    return;
                }
                var itemId = card.getAttribute('data-item-id');
                if (!itemId) {
                    return;
                }
                idInputEl.value = itemId;
                modal.hide();
                formEl.submit();
            });

            modalEl.addEventListener('hidden.bs.modal', function () {
                if (searchEl) {
                    searchEl.value = '';
                }
            });
        },
    };
})();
