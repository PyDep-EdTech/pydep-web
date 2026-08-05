/**
 * ProjectBox: предпросмотр текстовых файлов, скачивание только по кнопке.
 */
(function () {
    'use strict';

    function guessType(name) {
        const lower = (name || '').toLowerCase();
        if (/\.(txt|md|markdown|csv|json|py|html|css|js|xml|yml|yaml|log)$/.test(lower)) {
            return 'text';
        }
        return 'other';
    }

    function accessHint(accessGroup, extraUsers) {
        let hint = accessGroup || '';
        if (extraUsers > 0) {
            hint += ' · +' + extraUsers + ' польз.';
        }
        return hint;
    }

    function syncUploadHiddenInputs(container, ids) {
        if (!container) {
            return;
        }
        container.innerHTML = '';
        ids.forEach(function (id) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'allowed_users';
            input.value = String(id);
            container.appendChild(input);
        });
    }

    function initUploadAccess(modalApi) {
        const btn = document.getElementById('uploadAccessBtn');
        const summaryEl = document.getElementById('uploadAccessSummary');
        const hiddenWrap = document.getElementById('uploadAllowedUsers');
        const groupEl = document.getElementById('id_access_group');
        if (!btn || !modalApi) {
            return;
        }

        let allowedUserIds = [];

        function refreshSummary() {
            const group = groupEl ? groupEl.value : 'all';
            if (summaryEl) {
                summaryEl.textContent =
                    allowedUserIds.length > 0
                        ? modalApi.accessSummary(group, allowedUserIds.length)
                        : 'Не выбраны';
            }
            syncUploadHiddenInputs(hiddenWrap, allowedUserIds);
        }

        btn.addEventListener('click', function () {
            modalApi.openDraft({
                title: 'При загрузке файла',
                accessGroup: groupEl ? groupEl.value : 'all',
                allowedUserIds: allowedUserIds,
                onSave: function (data) {
                    allowedUserIds = data.allowedUserIds || [];
                    if (groupEl && data.accessGroup) {
                        groupEl.value = data.accessGroup;
                    }
                    refreshSummary();
                },
            });
        });

        if (groupEl) {
            groupEl.addEventListener('change', refreshSummary);
        }

        refreshSummary();
    }

    function init() {
        const preview = document.getElementById('filePreview');
        const items = document.querySelectorAll('.file-list-item');
        const modalApi = window.pydepFileAccess;
        if (!preview) {
            return;
        }

        initUploadAccess(modalApi);

        function clearPreview() {
            preview.innerHTML =
                '<div class="file-preview-empty text-muted">Выберите файл слева для предпросмотра</div>';
        }

        function showPreview(btn) {
            const url = btn.dataset.url;
            const displayName = btn.dataset.name || '';
            const typeName = btn.dataset.extname || '';
            const accessGroup = btn.dataset.accessGroup || '';
            const extraUsers = parseInt(btn.dataset.extraUsers || '0', 10);
            const canManage = btn.dataset.canManage === '1';
            const fileId = btn.dataset.fileId;
            const type = guessType(typeName || displayName || url);
            preview.innerHTML = '';

            const header = document.createElement('div');
            header.className = 'file-preview-head';
            header.innerHTML = '<strong>' + (displayName || 'Файл') + '</strong>';
            const hint = accessHint(accessGroup, extraUsers);
            if (hint) {
                const meta = document.createElement('div');
                meta.className = 'text-muted small mt-1';
                meta.textContent = 'Доступ: ' + hint;
                header.appendChild(meta);
            }
            preview.appendChild(header);

            const actions = document.createElement('div');
            actions.className = 'file-preview-actions d-flex flex-wrap gap-2';
            const download = document.createElement('a');
            download.href = url;
            download.download = displayName || '';
            download.className = 'btn btn-sm btn-primary';
            download.innerHTML = '<i class="bi bi-download me-1"></i>Скачать';
            actions.appendChild(download);

            if (canManage && modalApi && fileId) {
                const access = document.createElement('button');
                access.type = 'button';
                access.className = 'btn btn-sm btn-ghost';
                access.innerHTML =
                    '<i class="bi bi-shield-lock me-1"></i>Настроить доступ';
                access.addEventListener('click', function () {
                    modalApi.openFile(fileId, displayName, btn);
                });
                actions.appendChild(access);
            }
            preview.appendChild(actions);

            if (type === 'text') {
                const loading = document.createElement('div');
                loading.className = 'text-muted small';
                loading.textContent = 'Загрузка…';
                preview.appendChild(loading);

                fetch(url, { credentials: 'same-origin' })
                    .then(function (r) {
                        return r.ok ? r.text() : Promise.reject();
                    })
                    .then(function (text) {
                        loading.remove();
                        const pre = document.createElement('pre');
                        pre.className = 'file-preview-code';
                        pre.textContent = text;
                        preview.appendChild(pre);
                    })
                    .catch(function () {
                        loading.textContent =
                            'Предпросмотр недоступен. Скачайте файл кнопкой выше.';
                    });
                return;
            }

            const info = document.createElement('p');
            info.className = 'file-preview-hint text-muted mb-0';
            info.textContent =
                'Предпросмотр для этого типа файла недоступен. Скачайте файл кнопкой «Скачать».';
            preview.appendChild(info);
        }

        items.forEach(function (btn, index) {
            btn.addEventListener('click', function () {
                items.forEach(function (el) {
                    el.classList.remove('active');
                });
                btn.classList.add('active');
                showPreview(btn);
            });
            if (index === 0) {
                btn.click();
            }
        });

        if (!items.length) {
            clearPreview();
        }
    }

    document.addEventListener('DOMContentLoaded', init);
})();
