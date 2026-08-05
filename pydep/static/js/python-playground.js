/**
 * Python-песочница PyDep — CodeMirror + Pyodide в sandbox-iframe.
 * Код выполняется в изолированном iframe (без доступа к DOM/cookies родителя).
 * Проверка заданий — на сервере (ожидаемый вывод не попадает в HTML).
 */
(function () {
    'use strict';

    var MAX_CODE_LENGTH = 20000;
    var EXEC_LIMIT_S = 10;
    var PROTO = 1;

    var els = {};
    var cm = null;
    var runnerFrame = null;
    var runnerReady = false;
    var runnerInitPromise = null;
    var running = false;
    var activeRunId = null;
    var runAbortTimer = null;
    var inputResolver = null;
    var inputRequestId = null;
    var stdoutBuffer = '';
    var inputWaitMs = 0;
    var inputShownAt = 0;

    var tasks = [];
    var currentTask = null;
    var currentIdx = -1;
    var lessonId = null;
    var solvedSet = null;
    var checkUrl = '';
    var csrfToken = '';

    /* ---------- editor ---------- */
    function getCode() {
        return cm ? cm.getValue() : (els.editor ? els.editor.value : '');
    }
    function setCode(code) {
        if (cm) { cm.setValue(code); cm.focus(); cm.setCursor(cm.lineCount(), 0); }
        else if (els.editor) { els.editor.value = code; }
    }

    /* ---------- output ---------- */
    function appendOutput(text, stream) {
        if (text == null || text === '') return;
        if (stream === 'stdout') stdoutBuffer += text + '\n';
        var ph = els.output.querySelector('.pg-output__placeholder');
        if (ph) ph.remove();
        var block = document.createElement('div');
        block.className = 'pg-out-line pg-out-line--' + (stream || 'stdout');
        block.textContent = String(text).replace(/\n$/, '');
        els.output.appendChild(block);
        els.output.scrollTop = els.output.scrollHeight;
    }
    function clearOutput() {
        els.output.innerHTML =
            '<div class="pg-output__placeholder"><i class="bi bi-chevron-right"></i>' +
            '<span>Ожидание запуска…</span></div>';
    }
    function setStatus(text, kind) {
        if (els.status) els.status.textContent = text;
        var pill = els.status ? els.status.closest('.pg-status-pill') : null;
        if (pill) pill.dataset.kind = kind || '';
    }
    function setRunning(state) {
        running = state;
        if (els.runBtn) {
            els.runBtn.disabled = state || !runnerReady;
            els.runBtn.innerHTML = state
                ? '<i class="bi bi-arrow-repeat pg-spin"></i><span>Выполняется…</span>'
                : '<i class="bi bi-play-fill"></i><span>Запустить</span>';
        }
        if (els.checkBtn) els.checkBtn.disabled = state || !runnerReady;
    }

    /* ---------- input modal ---------- */
    function requestInput(promptText, requestId) {
        var label = (promptText || '').trim() || 'Введите значение:';
        els.inputLabel.textContent = label;
        els.inputField.value = '';
        els.inputModal.hidden = false;
        inputShownAt = performance.now();
        inputRequestId = requestId;
        setTimeout(function () { els.inputField.focus(); }, 40);
        return new Promise(function (resolve) { inputResolver = resolve; });
    }
    function submitInput() {
        if (!inputResolver || !activeRunId) return;
        var v = els.inputField.value;
        els.inputModal.hidden = true;
        inputWaitMs += performance.now() - inputShownAt;
        var r = inputResolver;
        var reqId = inputRequestId;
        inputResolver = null;
        inputRequestId = null;
        r(v);
        postToRunner({
            v: PROTO,
            type: 'input-response',
            id: activeRunId,
            requestId: reqId,
            value: v,
        });
    }

    function escapeHtml(s) {
        return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function showCheckResult(ok, expected, got) {
        if (!els.taskResult) return;
        els.taskResult.hidden = false;
        els.taskResult.className = 'pg-current-task__result ' + (ok ? 'is-ok' : 'is-fail');
        if (ok) {
            els.taskResult.innerHTML = '<i class="bi bi-check-circle-fill"></i> Верно! Вывод совпал с ожидаемым.';
        } else {
            els.taskResult.innerHTML =
                '<div><i class="bi bi-x-circle-fill"></i> Пока не совпадает.</div>' +
                '<div class="pg-diff"><span>Ожидалось:</span><pre>' + escapeHtml(expected) + '</pre></div>' +
                '<div class="pg-diff"><span>Получено:</span><pre>' + escapeHtml(got || '(пусто)') + '</pre></div>';
        }
    }

    /* ---------- sandbox runner (iframe) ---------- */
    function newRunId() {
        return 'run-' + Date.now() + '-' + Math.random().toString(36).slice(2);
    }

    function postToRunner(msg) {
        if (runnerFrame && runnerFrame.contentWindow) {
            runnerFrame.contentWindow.postMessage(msg, '*');
        }
    }

    function clearRunAbortTimer() {
        if (runAbortTimer) {
            clearTimeout(runAbortTimer);
            runAbortTimer = null;
        }
    }

    function scheduleRunAbort(runId) {
        clearRunAbortTimer();
        runAbortTimer = setTimeout(function () {
            if (activeRunId !== runId) return;
            postToRunner({ v: PROTO, type: 'abort', id: runId });
            resetRunnerFrame();
            appendOutput('⏱ Превышено время выполнения (' + EXEC_LIMIT_S + ' с).', 'stderr');
            setStatus('Прервано', 'error');
            setRunning(false);
            activeRunId = null;
        }, (EXEC_LIMIT_S + 2) * 1000);
    }

    function resetRunnerFrame() {
        if (!runnerFrame || !els.runnerHost) return;
        runnerReady = false;
        runnerInitPromise = null;
        runnerFrame.remove();
        runnerFrame = document.createElement('iframe');
        runnerFrame.id = 'pg-runner';
        runnerFrame.className = 'pg-runner-frame';
        runnerFrame.title = 'Python runner';
        runnerFrame.setAttribute('sandbox', 'allow-scripts');
        runnerFrame.setAttribute('referrerpolicy', 'no-referrer');
        runnerFrame.src = els.runnerHost.getAttribute('data-runner-url');
        els.runnerHost.appendChild(runnerFrame);
        runnerInitPromise = new Promise(function (resolve) {
            runnerFrame.addEventListener('load', function onLoad() {
                runnerFrame.removeEventListener('load', onLoad);
                resolve();
            });
        });
        if (els.runBtn) els.runBtn.disabled = true;
        if (els.checkBtn) els.checkBtn.disabled = true;
    }

    function ensureRunner() {
        if (!runnerFrame) resetRunnerFrame();
        if (runnerReady) return Promise.resolve();
        if (!runnerInitPromise) resetRunnerFrame();
        return runnerInitPromise.then(function () {
            if (runnerReady) return;
            return new Promise(function (resolve) {
                var timer = setTimeout(function () {
                    window.removeEventListener('message', onReady);
                    resolve();
                }, 60000);
                function onReady(event) {
                    if (event.source !== runnerFrame.contentWindow) return;
                    var data = event.data;
                    if (!data || data.v !== PROTO) return;
                    if (data.type === 'ready') {
                        runnerReady = true;
                        clearTimeout(timer);
                        window.removeEventListener('message', onReady);
                        setStatus('Готов к запуску', 'ok');
                        if (els.runBtn) els.runBtn.disabled = false;
                        if (els.checkBtn) els.checkBtn.disabled = false;
                        resolve();
                    }
                    if (data.type === 'fatal') {
                        clearTimeout(timer);
                        window.removeEventListener('message', onReady);
                        setStatus('Ошибка загрузки', 'error');
                        appendOutput('Не удалось загрузить интерпретатор. Обновите страницу.', 'stderr');
                        resolve();
                    }
                }
                window.addEventListener('message', onReady);
            });
        });
    }

    function serverCheckTask(taskId, output) {
        return fetch(checkUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ task_id: taskId, output: output }),
        }).then(function (resp) {
            if (!resp.ok) throw new Error('check_failed');
            return resp.json();
        });
    }

    function runCode(checkMode) {
        if (running) return;
        var code = getCode();
        if (code.length > MAX_CODE_LENGTH) {
            clearOutput();
            appendOutput('Слишком длинный код (макс. ' + MAX_CODE_LENGTH + ' символов).', 'stderr');
            return;
        }

        ensureRunner().then(function () {
            if (!runnerReady) return;

            clearOutput();
            stdoutBuffer = '';
            if (els.taskResult) els.taskResult.hidden = true;
            setRunning(true);
            setStatus(checkMode ? 'Проверка…' : 'Выполнение…', 'loading');

            var runId = newRunId();
            activeRunId = runId;
            var t0 = performance.now();
            inputWaitMs = 0;

            scheduleRunAbort(runId);

            function onRunnerMessage(event) {
                if (event.source !== runnerFrame.contentWindow) return;
                var data = event.data;
                if (!data || data.v !== PROTO || data.id !== runId) return;

                if (data.type === 'stdout') {
                    appendOutput(data.text, 'stdout');
                    return;
                }
                if (data.type === 'stderr') {
                    appendOutput(data.text, 'stderr');
                    return;
                }
                if (data.type === 'input-request') {
                    requestInput(data.prompt, data.requestId);
                    return;
                }
                if (data.type === 'done' || data.type === 'error') {
                    window.removeEventListener('message', onRunnerMessage);
                    clearRunAbortTimer();
                    activeRunId = null;

                    if (data.type === 'error' && data.message) {
                        appendOutput(data.message, 'stderr');
                        setStatus('Ошибка', 'error');
                        if (checkMode && els.taskResult) {
                            els.taskResult.hidden = false;
                            els.taskResult.className = 'pg-current-task__result is-fail';
                            els.taskResult.innerHTML = '<i class="bi bi-x-circle-fill"></i> В коде ошибка — исправьте её и попробуйте снова.';
                        }
                        setRunning(false);
                        return;
                    }

                    var outBuf = data.stdout != null ? data.stdout : stdoutBuffer;
                    var ms = Math.max(1, Math.round(performance.now() - t0 - inputWaitMs));
                    if (!els.output.querySelector('.pg-out-line')) {
                        appendOutput('(программа завершилась без вывода)', 'muted');
                    }

                    if (checkMode && currentTask && currentTask.has_check) {
                        serverCheckTask(currentTask.id, outBuf)
                            .then(function (result) {
                                showCheckResult(result.ok, result.expected || '', result.got || outBuf);
                                setStatus(result.ok ? 'Верно ✓' : 'Не совпало', result.ok ? 'ok' : 'error');
                                if (result.ok) onTaskSolved(currentIdx);
                            })
                            .catch(function () {
                                appendOutput('Не удалось проверить задание на сервере.', 'stderr');
                                setStatus('Ошибка проверки', 'error');
                            })
                            .finally(function () { setRunning(false); });
                    } else {
                        setStatus('Готово за ' + ms + ' мс', 'ok');
                        setRunning(false);
                    }
                }
            }

            window.addEventListener('message', onRunnerMessage);

            postToRunner({
                v: PROTO,
                type: 'run',
                id: runId,
                code: code,
                stdin: els.stdin && els.stdin.value ? els.stdin.value : '',
                limit: EXEC_LIMIT_S,
            });
        });
    }

    /* ---------- practice tasks ---------- */
    function storageKey() { return 'pg-solved-' + (lessonId || 'x'); }
    function loadSolved() {
        solvedSet = {};
        try {
            var raw = localStorage.getItem(storageKey());
            if (raw) JSON.parse(raw).forEach(function (id) { solvedSet[id] = true; });
        } catch (e) {}
    }
    function persistSolved() {
        try { localStorage.setItem(storageKey(), JSON.stringify(Object.keys(solvedSet))); } catch (e) {}
    }
    function checkableTasks() { return tasks.filter(function (t) { return t.has_check; }); }
    function solvedCount() {
        return checkableTasks().filter(function (t) { return solvedSet[t.id]; }).length;
    }

    function updateProgress() {
        var total = checkableTasks().length;
        if (!total) {
            if (els.progressWrap) els.progressWrap.style.display = 'none';
            if (els.progressCount) els.progressCount.style.display = 'none';
            return;
        }
        var done = solvedCount();
        if (els.progressBar) els.progressBar.style.width = Math.round((done / total) * 100) + '%';
        if (els.progressCount) els.progressCount.textContent = done + ' / ' + total;
        if (els.allDone) els.allDone.hidden = done < total;
    }

    function markTaskItemSolved(idx) {
        var btn = els.taskList.children[idx];
        if (!btn) return;
        btn.classList.add('is-solved');
        var check = btn.querySelector('.pg-task-item__check');
        if (check) check.className = 'bi bi-check-circle-fill pg-task-item__check';
    }

    function celebrate() {
        var box = document.createElement('div');
        box.className = 'pg-confetti';
        var colors = ['#FFB020', '#54d6b4', '#7c9cff', '#ff7c9c', '#ffe08a'];
        for (var i = 0; i < 70; i++) {
            var p = document.createElement('span');
            p.className = 'pg-confetti__bit';
            p.style.left = Math.random() * 100 + '%';
            p.style.background = colors[i % colors.length];
            p.style.animationDelay = (Math.random() * 0.4) + 's';
            p.style.animationDuration = (1.6 + Math.random() * 1.4) + 's';
            p.style.transform = 'rotate(' + (Math.random() * 360) + 'deg)';
            box.appendChild(p);
        }
        document.body.appendChild(box);
        setTimeout(function () { box.remove(); }, 3400);
    }

    function selectTask(idx) {
        currentTask = tasks[idx];
        currentIdx = idx;
        if (!currentTask) return;
        document.querySelectorAll('.pg-task-item').forEach(function (b, i) {
            b.classList.toggle('is-active', i === idx);
        });
        els.taskCardCurrent.hidden = false;
        els.taskNum.textContent = 'Задание ' + (idx + 1) + ' из ' + tasks.length;
        els.taskTitle.textContent = currentTask.title;
        els.taskStatement.textContent = currentTask.statement;
        els.taskResult.hidden = true;
        if (els.taskNext) els.taskNext.hidden = true;
        if (els.checkBtn) els.checkBtn.hidden = !currentTask.has_check;
        setCode(currentTask.starter || '# Решение задания\n');
    }

    function nextUnsolvedIdx(from) {
        for (var step = 1; step <= tasks.length; step++) {
            var i = (from + step) % tasks.length;
            if (tasks[i].has_check && !solvedSet[tasks[i].id]) return i;
        }
        return -1;
    }

    function onTaskSolved(idx) {
        var t = tasks[idx];
        if (!t || !t.has_check) return;
        var wasNew = !solvedSet[t.id];
        solvedSet[t.id] = true;
        persistSolved();
        markTaskItemSolved(idx);
        updateProgress();
        var nxt = nextUnsolvedIdx(idx);
        if (els.taskNext) {
            if (nxt !== -1) {
                els.taskNext.hidden = false;
                els.taskNext.onclick = function () { selectTask(nxt); };
            } else {
                els.taskNext.hidden = true;
            }
        }
        if (wasNew && solvedCount() === checkableTasks().length) celebrate();
    }

    function initTasks() {
        var node = document.getElementById('pg-tasks-data');
        if (!node) return;
        try { tasks = JSON.parse(node.textContent) || []; } catch (e) { tasks = []; }
        if (!tasks.length) return;

        var m = location.search.match(/[?&]lesson=(\d+)/);
        lessonId = m ? m[1] : 'anon';
        loadSolved();

        if (els.examplesCard) els.examplesCard.hidden = true;
        els.taskCard.hidden = false;

        tasks.forEach(function (t, i) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'pg-task-item' + (solvedSet[t.id] ? ' is-solved' : '');
            var icon = solvedSet[t.id]
                ? '<i class="bi bi-check-circle-fill pg-task-item__check"></i>'
                : (t.has_check ? '<i class="bi bi-patch-check pg-task-item__check"></i>' : '');
            btn.innerHTML =
                '<span class="pg-task-item__num">' + (i + 1) + '</span>' +
                '<span class="pg-task-item__title">' + escapeHtml(t.title) + '</span>' + icon;
            btn.addEventListener('click', function () { selectTask(i); });
            els.taskList.appendChild(btn);
        });
        updateProgress();
        selectTask(0);
    }

    /* ---------- CodeMirror ---------- */
    function initCodeMirror() {
        if (typeof CodeMirror === 'undefined' || !els.editor) return;
        cm = CodeMirror.fromTextArea(els.editor, {
            mode: 'python', theme: 'default', lineNumbers: true,
            indentUnit: 4, tabSize: 4, indentWithTabs: false,
            matchBrackets: true, autoCloseBrackets: true,
            extraKeys: {
                Tab: function (e) {
                    if (e.somethingSelected()) e.indentSelection('add');
                    else e.replaceSelection('    ', 'end');
                },
                'Ctrl-Enter': function () { runCode(false); },
                'Cmd-Enter': function () { runCode(false); },
            },
        });
        cm.on('change', function () { cm.save(); });
        requestAnimationFrame(function () { cm.setSize(null, '100%'); cm.refresh(); });
    }
    function watchThemeChange() {
        if (!window.MutationObserver) return;
        new MutationObserver(function () {
            if (cm) requestAnimationFrame(function () { cm.refresh(); });
        }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    }

    document.addEventListener('DOMContentLoaded', function () {
        els.editor = document.getElementById('pg-editor');
        els.output = document.getElementById('pg-output');
        els.runBtn = document.getElementById('pg-run');
        els.checkBtn = document.getElementById('pg-check');
        els.status = document.getElementById('pg-status');
        els.clearBtn = document.getElementById('pg-clear');
        els.stdin = document.getElementById('pg-stdin');
        els.inputModal = document.getElementById('pg-input-modal');
        els.inputField = document.getElementById('pg-input-field');
        els.inputLabel = document.getElementById('pg-input-label');
        els.inputSubmit = document.getElementById('pg-input-submit');
        els.taskCard = document.getElementById('pg-tasks-card');
        els.taskList = document.getElementById('pg-tasks-list');
        els.taskCardCurrent = document.getElementById('pg-current-task');
        els.taskNum = document.getElementById('pg-task-num');
        els.taskTitle = document.getElementById('pg-task-title');
        els.taskStatement = document.getElementById('pg-task-statement');
        els.taskResult = document.getElementById('pg-task-result');
        els.taskReset = document.getElementById('pg-task-reset');
        els.taskNext = document.getElementById('pg-task-next');
        els.progressBar = document.getElementById('pg-progress-bar');
        els.progressCount = document.getElementById('pg-progress-count');
        els.progressWrap = document.querySelector('.pg-progress');
        els.allDone = document.getElementById('pg-all-done');
        els.examplesCard = document.getElementById('pg-examples-card');
        els.runnerHost = document.getElementById('pg-runner-host');
        if (!els.editor) return;

        checkUrl = (els.runnerHost && els.runnerHost.getAttribute('data-check-url')) || '';
        var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        csrfToken = csrfInput ? csrfInput.value : '';

        if (isTouchDevice()) {
            document.documentElement.classList.add('pg-mobile-gate-on');
            return;
        }

        initCodeMirror();
        watchThemeChange();
        initTasks();

        document.querySelectorAll('[data-example]').forEach(function (btn) {
            btn.addEventListener('click', function () { setCode(btn.getAttribute('data-example')); });
        });

        if (els.runBtn) { els.runBtn.disabled = true; els.runBtn.addEventListener('click', function () { runCode(false); }); }
        if (els.checkBtn) els.checkBtn.addEventListener('click', function () { runCode(true); });
        if (els.clearBtn) els.clearBtn.addEventListener('click', clearOutput);
        if (els.taskReset) els.taskReset.addEventListener('click', function () {
            if (currentTask) setCode(currentTask.starter || '# Решение задания\n');
        });

        if (els.inputSubmit) els.inputSubmit.addEventListener('click', submitInput);
        if (els.inputField) els.inputField.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') { e.preventDefault(); submitInput(); }
        });

        setStatus('Загрузка Python…', 'loading');
        ensureRunner();
    });

    function isTouchDevice() {
        try {
            if (window.matchMedia && window.matchMedia('(hover: none) and (pointer: coarse)').matches) return true;
        } catch (e) {}
        var ua = navigator.userAgent || '';
        if (navigator.maxTouchPoints > 1 && /Macintosh/.test(ua)) return true;
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|Tablet|Silk|Kindle|PlayBook/i.test(ua);
    }
})();
