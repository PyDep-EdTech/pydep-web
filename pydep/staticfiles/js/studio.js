/**
 * PyDep Studio — навигация, сортировка
 */
(function () {
    'use strict';

    function getCsrfToken() {
        var input = document.querySelector('[name=csrfmiddlewaretoken]');
        return input ? input.value : '';
    }

    /* ── Sortable lists (native drag & drop) ────────────── */
    function initTree() {
        document.querySelectorAll('.studio-tree__module').forEach(function (mod) {
            if (mod.querySelector('.is-active') || mod.classList.contains('is-open')) {
                mod.classList.add('is-open');
            }
        });
        document.querySelectorAll('.studio-tree__toggle').forEach(function (btn) {
            if (btn.dataset.studioBound) return;
            btn.dataset.studioBound = '1';
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                var mod = btn.closest('.studio-tree__module');
                if (mod) mod.classList.toggle('is-open');
            });
        });
    }

    /* ── Sortable lists (native drag & drop) ────────────── */
    function initSortable(listEl, options) {
        if (!listEl || listEl.dataset.studioSortable) return;
        listEl.dataset.studioSortable = '1';

        var hiddenInput = options.hiddenInput;
        var onReorder = options.onReorder;
        var reorderUrl = options.reorderUrl;
        var reorderPayload = options.reorderPayload;

        function currentOrder() {
            return Array.from(listEl.querySelectorAll('[data-id]')).map(function (el) {
                return parseInt(el.getAttribute('data-id'), 10);
            }).filter(function (id) { return !isNaN(id); });
        }

        function syncHidden() {
            var order = currentOrder();
            if (hiddenInput) hiddenInput.value = order.join(',');
            if (onReorder) onReorder(order);
            if (reorderUrl && reorderPayload) {
                fetch(reorderUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify(reorderPayload(order)),
                }).catch(function () {});
            }
            var hint = document.querySelector('.studio-save-hint');
            if (hint) hint.classList.add('is-dirty');
        }

        var dragged = null;

        listEl.querySelectorAll('.studio-sortable__item').forEach(function (item) {
            item.setAttribute('draggable', 'true');

            item.addEventListener('dragstart', function (e) {
                dragged = item;
                item.classList.add('is-dragging');
                e.dataTransfer.effectAllowed = 'move';
            });

            item.addEventListener('dragend', function () {
                item.classList.remove('is-dragging');
                dragged = null;
                syncHidden();
            });

            item.addEventListener('dragover', function (e) {
                e.preventDefault();
                if (!dragged || dragged === item) return;
                var rect = item.getBoundingClientRect();
                var after = e.clientY > rect.top + rect.height / 2;
                if (after) {
                    item.parentNode.insertBefore(dragged, item.nextSibling);
                } else {
                    item.parentNode.insertBefore(dragged, item);
                }
            });
        });

        if (hiddenInput && hiddenInput.value) {
            /* keep server order */
        } else {
            syncHidden();
        }
    }

    function initDetachButtons() {
        document.querySelectorAll('.studio-detach-btn').forEach(function (btn) {
            if (btn.dataset.studioDetachBound) return;
            btn.dataset.studioDetachBound = '1';
            btn.addEventListener('click', function () {
                var message = btn.getAttribute('data-confirm') || 'Продолжить?';
                if (!window.confirm(message)) return;
                var formId = btn.getAttribute('data-detach-form');
                var form = formId ? document.getElementById(formId) : null;
                if (!form) return;
                var idInput = form.querySelector('[name="module_id"], [name="lesson_id"]');
                if (idInput) {
                    idInput.value = btn.getAttribute('data-detach-id') || '';
                }
                form.submit();
            });
        });
    }

    window.Studio = {
        initTree: initTree,
        initSortable: initSortable,
        initDetachButtons: initDetachButtons,
    };

    document.addEventListener('DOMContentLoaded', function () {
        initTree();
        initDetachButtons();

        var modulesList = document.getElementById('studio-modules-sortable');
        if (modulesList) {
            var modulesInput = document.getElementById('modules_order');
            var reorderUrl = modulesList.getAttribute('data-reorder-url');
            var courseId = modulesList.getAttribute('data-course-id');
            initSortable(modulesList, {
                hiddenInput: modulesInput,
                reorderUrl: reorderUrl,
                reorderPayload: function (order) {
                    return { type: 'modules', course_id: parseInt(courseId, 10), order: order };
                },
            });
        }

        var lessonsList = document.getElementById('studio-lessons-sortable');
        if (lessonsList) {
            var lessonsInput = document.getElementById('lessons_order');
            var lessonsReorderUrl = lessonsList.getAttribute('data-reorder-url');
            var lessonsCourseId = lessonsList.getAttribute('data-course-id');
            var moduleId = lessonsList.getAttribute('data-module-id');
            initSortable(lessonsList, {
                hiddenInput: lessonsInput,
                reorderUrl: lessonsReorderUrl,
                reorderPayload: function (order) {
                    return {
                        type: 'lessons',
                        course_id: parseInt(lessonsCourseId, 10),
                        module_id: parseInt(moduleId, 10),
                        order: order,
                    };
                },
            });
        }
    });
})();
