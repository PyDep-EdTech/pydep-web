/**
 * Модальное окно настройки доступа к файлу ProjectBox (группа + поиск пользователей).
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

    function groupLabel(choices, value) {
        const found = (choices || []).find(function (item) {
            return item[0] === value;
        });
        return found ? found[1] : value;
    }

    window.PyDepFileAccessModal = {
        init: function (config) {
            const modalEl = document.getElementById('fileAccessModal');
            const subtitleEl = document.getElementById('fileAccessModalSubtitle');
            const groupEl = document.getElementById('fileAccessGroup');
            const groupWrapEl = document.getElementById('fileAccessGroupWrap');
            const chipsEl = document.getElementById('fileAccessChips');
            const countEl = document.getElementById('fileAccessSelectedCount');
            const searchEl = document.getElementById('fileAccessSearch');
            const gridEl = document.getElementById('fileAccessGrid');
            const saveBtn = document.getElementById('fileAccessSaveBtn');
            const csrfToken = config.csrfToken || '';
            const users = config.users || [];
            const accessGroups = config.accessGroups || [];
            const defaultAvatar = config.defaultAvatar || '';
            const saveUrlTemplate = config.saveUrlTemplate || '';
            const getCsrf = config.getCsrf || function () { return csrfToken; };

            if (!modalEl || !groupEl || !gridEl || !saveBtn) {
                return null;
            }

            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            const state = {
                mode: 'file',
                fileId: null,
                fileName: '',
                accessGroup: accessGroups[0] ? accessGroups[0][0] : 'all',
                selectedIds: new Set(),
                listItem: null,
                onDraftSave: null,
            };

            function populateGroups(selected) {
                groupEl.innerHTML = accessGroups.map(function (item) {
                    const selectedAttr = item[0] === selected ? ' selected' : '';
                    return (
                        '<option value="' +
                        escapeHtml(item[0]) +
                        '"' +
                        selectedAttr +
                        '>' +
                        escapeHtml(item[1]) +
                        '</option>'
                    );
                }).join('');
            }

            function cardHtml(user, isSelected) {
                const avatar = user.avatar_url || defaultAvatar;
                const selectedClass = isSelected ? ' student-picker-card--selected' : '';
                return (
                    '<button type="button" class="student-picker-card' +
                    selectedClass +
                    '" data-user-id="' +
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
                    (isSelected
                        ? '<i class="bi bi-check-lg student-picker-card__check"></i>'
                        : '') +
                    '</button>'
                );
            }

            function renderChips() {
                const ids = Array.from(state.selectedIds);
                if (!ids.length) {
                    chipsEl.innerHTML =
                        '<span class="file-access-chips__empty text-muted small">Никто не выбран</span>';
                    countEl.textContent = '';
                    return;
                }
                countEl.textContent = ids.length + ' выбрано';
                chipsEl.innerHTML = ids
                    .map(function (id) {
                        const user = findUser(users, id);
                        if (!user) {
                            return '';
                        }
                        return (
                            '<span class="file-access-chip">' +
                            '<span>' +
                            escapeHtml(user.full_name) +
                            '</span>' +
                            '<button type="button" class="file-access-chip__remove" data-user-id="' +
                            id +
                            '" aria-label="Убрать">' +
                            '<i class="bi bi-x"></i>' +
                            '</button>' +
                            '</span>'
                        );
                    })
                    .join('');
            }

            function renderGrid() {
                const query = searchEl ? searchEl.value : '';
                const list = filterCards(users, query);
                if (!list.length) {
                    gridEl.innerHTML =
                        '<div class="student-picker-empty">' +
                        '<i class="bi bi-search"></i>' +
                        '<p>Никого не найдено</p>' +
                        '</div>';
                    return;
                }
                gridEl.innerHTML = list
                    .map(function (user) {
                        return cardHtml(user, state.selectedIds.has(Number(user.id)));
                    })
                    .join('');
            }

            function toggleUser(userId) {
                const id = Number(userId);
                if (state.selectedIds.has(id)) {
                    state.selectedIds.delete(id);
                } else {
                    state.selectedIds.add(id);
                }
                renderChips();
                renderGrid();
            }

            function accessSummary(group, extraCount) {
                let text = groupLabel(accessGroups, group);
                if (extraCount > 0) {
                    text += ' +' + extraCount;
                }
                return text;
            }

            function updateListItem(data) {
                if (!state.listItem) {
                    return;
                }
                const group = data.access_group || state.accessGroup;
                const count =
                    data.allowed_users_count !== undefined
                        ? data.allowed_users_count
                        : state.selectedIds.size;
                const label =
                    data.access_group_label || groupLabel(accessGroups, group);
                state.listItem.dataset.accessGroup = label;
                state.listItem.dataset.extraUsers = String(count);
                const badge = state.listItem.querySelector('.file-access-badge');
                if (badge) {
                    badge.textContent = label + (count > 0 ? ' +' + count : '');
                }
            }

            function openDraft(options) {
                state.mode = 'draft';
                state.fileId = null;
                state.fileName = options.title || 'Новый файл';
                state.accessGroup = options.accessGroup || 'all';
                state.selectedIds = new Set(
                    (options.allowedUserIds || []).map(Number)
                );
                state.listItem = null;
                state.onDraftSave = options.onSave || null;
                subtitleEl.textContent = state.fileName;
                groupWrapEl.classList.add('d-none');
                populateGroups(state.accessGroup);
                if (searchEl) {
                    searchEl.value = '';
                }
                renderChips();
                renderGrid();
                modal.show();
            }

            function openFile(fileId, fileName, listItem) {
                state.mode = 'file';
                state.fileId = fileId;
                state.fileName = fileName || '';
                state.listItem = listItem || null;
                state.onDraftSave = null;
                subtitleEl.textContent = state.fileName;
                groupWrapEl.classList.remove('d-none');
                if (searchEl) {
                    searchEl.value = '';
                }
                renderChips();
                gridEl.innerHTML =
                    '<div class="student-picker-empty"><p>Загрузка…</p></div>';

                const url = saveUrlTemplate.replace('/0/', '/' + fileId + '/');
                fetch(url, {
                    credentials: 'same-origin',
                    headers: { Accept: 'application/json' },
                })
                    .then(function (r) {
                        return r.ok ? r.json() : Promise.reject();
                    })
                    .then(function (data) {
                        if (!data.ok || !data.file) {
                            return Promise.reject();
                        }
                        state.accessGroup = data.file.access_group;
                        state.selectedIds = new Set(
                            (data.file.allowed_user_ids || []).map(Number)
                        );
                        populateGroups(state.accessGroup);
                        renderChips();
                        renderGrid();
                    })
                    .catch(function () {
                        gridEl.innerHTML =
                            '<div class="student-picker-empty">' +
                            '<p>Не удалось загрузить настройки</p>' +
                            '</div>';
                    });

                modal.show();
            }

            function saveDraft() {
                const uploadGroup = document.getElementById('id_access_group');
                state.accessGroup = uploadGroup
                    ? uploadGroup.value
                    : groupEl.value;
                const ids = Array.from(state.selectedIds);
                if (typeof state.onDraftSave === 'function') {
                    state.onDraftSave({
                        accessGroup: state.accessGroup,
                        allowedUserIds: ids,
                        summary: accessSummary(state.accessGroup, ids.length),
                    });
                }
                modal.hide();
            }

            function saveFile() {
                const url = saveUrlTemplate.replace('/0/', '/' + state.fileId + '/');
                const body = new FormData();
                body.append('access_group', groupEl.value);
                Array.from(state.selectedIds).forEach(function (id) {
                    body.append('allowed_users', String(id));
                });
                body.append('csrfmiddlewaretoken', getCsrf());

                saveBtn.disabled = true;
                fetch(url, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        Accept: 'application/json',
                    },
                    body: body,
                })
                    .then(function (r) {
                        return r.json().then(function (data) {
                            return { ok: r.ok, data: data };
                        });
                    })
                    .then(function (result) {
                        if (!result.ok || !result.data.ok) {
                            return Promise.reject(result.data);
                        }
                        state.accessGroup = result.data.file.access_group;
                        updateListItem(result.data.file);
                        if (typeof config.onSaved === 'function') {
                            config.onSaved(result.data.file);
                        }
                        modal.hide();
                    })
                    .catch(function () {
                        window.alert('Не удалось сохранить доступ. Попробуйте ещё раз.');
                    })
                    .finally(function () {
                        saveBtn.disabled = false;
                    });
            }

            saveBtn.addEventListener('click', function () {
                if (state.mode === 'draft') {
                    saveDraft();
                } else {
                    saveFile();
                }
            });

            gridEl.addEventListener('click', function (event) {
                const card = event.target.closest('.student-picker-card');
                if (!card) {
                    return;
                }
                toggleUser(card.dataset.userId);
            });

            chipsEl.addEventListener('click', function (event) {
                const btn = event.target.closest('.file-access-chip__remove');
                if (!btn) {
                    return;
                }
                toggleUser(btn.dataset.userId);
            });

            if (searchEl) {
                searchEl.addEventListener('input', renderGrid);
            }

            modalEl.addEventListener('shown.bs.modal', function () {
                if (searchEl) {
                    searchEl.focus();
                }
            });

            populateGroups(state.accessGroup);

            return {
                openFile: openFile,
                openDraft: openDraft,
                accessSummary: accessSummary,
            };
        },
    };
})();
