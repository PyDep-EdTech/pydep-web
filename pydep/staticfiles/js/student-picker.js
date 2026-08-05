(function () {
    'use strict';

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function cardHtml(user, defaultAvatar) {
        const avatar = user.avatar_url || defaultAvatar;
        return (
            '<button type="button" class="student-picker-card" data-user-id="' +
            user.id +
            '">' +
            '<img src="' +
            escapeHtml(avatar) +
            '" alt="" class="student-picker-card__avatar" loading="lazy">' +
            '<span class="student-picker-card__name">' +
            escapeHtml(user.full_name) +
            '</span>' +
            '<span class="student-picker-card__login">@' +
            escapeHtml(user.username) +
            '</span>' +
            '</button>'
        );
    }

    function previewHtml(user, defaultAvatar, placeholder) {
        if (!user) {
            return (
                '<div class="student-picker-preview student-picker-preview--empty">' +
                '<i class="bi bi-person-plus"></i>' +
                '<span>' +
                escapeHtml(placeholder || 'Выберите ученика') +
                '</span>' +
                '</div>'
            );
        }
        const avatar = user.avatar_url || defaultAvatar;
        return (
            '<div class="student-picker-preview">' +
            '<img src="' +
            escapeHtml(avatar) +
            '" alt="" class="student-picker-preview__avatar">' +
            '<div class="student-picker-preview__text">' +
            '<strong>' +
            escapeHtml(user.full_name) +
            '</strong>' +
            '<span>@' +
            escapeHtml(user.username) +
            '</span>' +
            '</div>' +
            '<i class="bi bi-chevron-down student-picker-preview__chevron"></i>' +
            '</div>'
        );
    }

    function findUser(cards, id) {
        const numericId = Number(id);
        return cards.find(function (card) {
            return Number(card.id) === numericId;
        });
    }

    function filterCards(cards, query) {
        const q = (query || '').trim().toLowerCase();
        if (!q) {
            return cards;
        }
        return cards.filter(function (card) {
            return (
                card.username.toLowerCase().includes(q) ||
                card.full_name.toLowerCase().includes(q)
            );
        });
    }

    window.PyDepStudentPicker = {
        init: function (config) {
            const modalEl = document.getElementById(config.modalId);
            const gridEl = document.getElementById(config.gridId);
            const searchEl = config.searchId
                ? document.getElementById(config.searchId)
                : null;
            const inputEl = config.inputId
                ? document.getElementById(config.inputId)
                : null;
            const previewEl = config.previewId
                ? document.getElementById(config.previewId)
                : null;
            const triggerEl = config.triggerId
                ? document.getElementById(config.triggerId)
                : null;
            const cards = config.cards || [];
            const defaultAvatar = config.defaultAvatar || '';
            const mode = config.mode || 'select';
            const inviteBaseUrl = config.inviteBaseUrl || '';
            const csrfToken = config.csrfToken || '';

            if (!modalEl || !gridEl) {
                return;
            }

            function renderGrid(list) {
                if (!list.length) {
                    gridEl.innerHTML =
                        '<div class="student-picker-empty">' +
                        '<i class="bi bi-search"></i>' +
                        '<p>Никого не найдено</p>' +
                        '</div>';
                    return;
                }
                gridEl.innerHTML = list.map(function (user) {
                    return cardHtml(user, defaultAvatar);
                }).join('');
            }

            function updatePreview(user) {
                if (!previewEl) {
                    return;
                }
                previewEl.innerHTML = previewHtml(
                    user,
                    defaultAvatar,
                    config.placeholder
                );
            }

            function selectUser(userId) {
                const user = findUser(cards, userId);
                if (!user) {
                    return;
                }

                if (mode === 'invite') {
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = inviteBaseUrl.replace('/0/', '/' + userId + '/');
                    const csrf = document.createElement('input');
                    csrf.type = 'hidden';
                    csrf.name = 'csrfmiddlewaretoken';
                    csrf.value = csrfToken;
                    form.appendChild(csrf);
                    document.body.appendChild(form);
                    form.submit();
                    return;
                }

                if (inputEl) {
                    inputEl.value = user.id;
                }
                updatePreview(user);
                if (typeof config.onSelect === 'function') {
                    config.onSelect(user);
                }
                bootstrap.Modal.getOrCreateInstance(modalEl).hide();
            }

            renderGrid(cards);

            if (inputEl && inputEl.value) {
                updatePreview(findUser(cards, inputEl.value));
            } else {
                updatePreview(null);
            }

            if (triggerEl) {
                triggerEl.addEventListener('click', function () {
                    if (searchEl) {
                        searchEl.value = '';
                    }
                    renderGrid(cards);
                    bootstrap.Modal.getOrCreateInstance(modalEl).show();
                });
            }

            if (searchEl) {
                searchEl.addEventListener('input', function () {
                    renderGrid(filterCards(cards, searchEl.value));
                });
            }

            gridEl.addEventListener('click', function (event) {
                const card = event.target.closest('.student-picker-card');
                if (!card) {
                    return;
                }
                selectUser(card.dataset.userId);
            });

            modalEl.addEventListener('shown.bs.modal', function () {
                if (searchEl) {
                    searchEl.focus();
                }
            });
        },
    };
})();
