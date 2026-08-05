/**
 * Изолированный раннер Pyodide для sandbox-iframe.
 * Общается с родительской страницей через postMessage.
 */
(function () {
    'use strict';

    var PYODIDE_INDEX = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
    var EXEC_LIMIT_S = 10;
    var PROTO = 1;

    var pyodide = null;
    var pyodideReady = null;
    var activeRun = null;
    var stdinLines = [];
    var stdinPos = 0;
    var stdoutBuffer = '';

    var PREAMBLE = [
        'import sys, time, ast',
        'import js as __pg_js',
        '',
        'class __PGClock:',
        '    def __init__(self, limit):',
        '        self.limit = limit; self.t0 = time.time(); self._p = None; self._paused = 0.0',
        '    def pause(self):',
        '        self._p = time.time()',
        '    def resume(self):',
        '        if self._p is not None:',
        '            self._paused += time.time() - self._p; self._p = None',
        '    def check(self):',
        '        if self._p is not None:',
        '            return',
        '        if time.time() - self.t0 - self._paused > self.limit:',
        '            raise TimeoutError("PG_TIMEOUT")',
        '',
        '__pg_clock = None',
        '__pg_orig_settrace = sys.settrace',
        '',
        'def __pg_trace(frame, event, arg):',
        '    if __pg_clock is not None:',
        '        __pg_clock.check()',
        '    return __pg_trace',
        '',
        'def __pg_guard_settrace(fn):',
        '    if fn is not None and fn is not __pg_trace:',
        '        raise RuntimeError("PG_FORBIDDEN")',
        '    return __pg_orig_settrace(fn)',
        '',
        'sys.settrace = __pg_guard_settrace',
        '',
        'async def __pg_ainput(prompt=""):',
        '    if prompt:',
        '        print(prompt, end="")',
        '    if __pg_clock is not None:',
        '        __pg_clock.pause()',
        '    try:',
        '        val = await __pg_js.__pg_request_input(str(prompt))',
        '    finally:',
        '        if __pg_clock is not None:',
        '            __pg_clock.resume()',
        '    return "" if val is None else str(val)',
        '',
        'def __pg_input_mode(src):',
        '    try:',
        '        tree = ast.parse(src)',
        '    except SyntaxError:',
        '        return "none"',
        '    state = {"has": False, "nested": False, "depth": 0}',
        '    class V(ast.NodeVisitor):',
        '        def _fn(self, node):',
        '            state["depth"] += 1; self.generic_visit(node); state["depth"] -= 1',
        '        visit_FunctionDef = _fn',
        '        visit_AsyncFunctionDef = _fn',
        '        visit_Lambda = _fn',
        '        def visit_Call(self, node):',
        '            if isinstance(node.func, ast.Name) and node.func.id == "input":',
        '                state["has"] = True',
        '                if state["depth"] > 0:',
        '                    state["nested"] = True',
        '            self.generic_visit(node)',
        '    V().visit(tree)',
        '    if not state["has"]:',
        '        return "none"',
        '    return "sync" if state["nested"] else "async"',
        '',
        'def __pg_run_sync(src, limit):',
        '    global __pg_clock',
        '    __pg_clock = __PGClock(limit)',
        '    ns = {"__name__": "__main__"}',
        '    code = compile(src, "<program>", "exec")',
        '    __pg_orig_settrace(__pg_trace)',
        '    try:',
        '        exec(code, ns)',
        '    finally:',
        '        __pg_orig_settrace(None); __pg_clock = None',
        '',
        'async def __pg_run_async(src, limit):',
        '    global __pg_clock',
        '    __pg_clock = __PGClock(limit)',
        '    tree = ast.parse(src)',
        '    class T(ast.NodeTransformer):',
        '        def visit_Call(self, node):',
        '            self.generic_visit(node)',
        '            if isinstance(node.func, ast.Name) and node.func.id == "input":',
        '                return ast.Await(value=node)',
        '            return node',
        '    new = T().visit(tree)',
        '    body = new.body or [ast.Pass()]',
        '    func = ast.AsyncFunctionDef(name="__pg_main__",',
        '        args=ast.arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),',
        '        body=body, decorator_list=[], returns=None)',
        '    mod = ast.Module(body=[func], type_ignores=[])',
        '    ast.fix_missing_locations(mod)',
        '    ns = {"__name__": "__main__", "input": __pg_ainput}',
        '    code = compile(mod, "<program>", "exec")',
        '    __pg_orig_settrace(__pg_trace)',
        '    try:',
        '        exec(code, ns)',
        '        await ns["__pg_main__"]()',
        '    finally:',
        '        __pg_orig_settrace(None); __pg_clock = None',
        '',
    ].join('\n');

    var INTERNAL_FRAME = /_pyodide\/_base|eval_code_async|run_async|CodeRunner|coroutine = eval|await CodeRunner|eval\(self\.code|File "<exec>"|File "<string>"|__pg_run|__pg_main__|sys\.settrace|exec\(code|await ns|\/lib\/python/;

    function post(msg) {
        if (window.parent && window.parent !== window) {
            window.parent.postMessage(msg, '*');
        }
    }

    function cleanTraceback(msg, limit) {
        if (!msg) return 'Ошибка выполнения.';
        if (msg.indexOf('PG_TIMEOUT') !== -1) {
            return '⏱ Превышено время выполнения (' + limit + ' с). Упростите цикл или логику.';
        }
        if (msg.indexOf('PG_FORBIDDEN') !== -1) {
            return '⛔ Нельзя отключать ограничение времени выполнения.';
        }
        var lines = String(msg).split('\n');
        var start = -1;
        for (var i = 0; i < lines.length; i++) {
            if (lines[i].indexOf('File "<program>"') !== -1) { start = i; break; }
        }
        if (start === -1) {
            return lines.filter(function (l) {
                return l.trim() && !INTERNAL_FRAME.test(l) && l.indexOf('Traceback (most recent') === -1;
            }).join('\n').trim() || msg;
        }
        var out = ['Traceback (most recent call last):'];
        for (var j = start; j < lines.length; j++) {
            var ln = lines[j];
            if (INTERNAL_FRAME.test(ln)) {
                var src = lines[j + 1];
                if (/^\s+\S/.test(src || '') && !/^\s*File "/.test(src || '')) j++;
                continue;
            }
            out.push(ln);
        }
        return out.join('\n').replace(/\n{3,}/g, '\n\n').trim();
    }

    function readStdin() {
        if (stdinPos < stdinLines.length) return stdinLines[stdinPos++] + '\n';
        var v = window.prompt('Программа запросила ввод (input):');
        return (v == null ? '' : v) + '\n';
    }

    window.__pg_request_input = function (promptText) {
        if (!activeRun) return Promise.resolve('');
        var requestId = 'in-' + Date.now() + '-' + Math.random().toString(36).slice(2);
        return new Promise(function (resolve) {
            activeRun.pendingInput = { requestId: requestId, resolve: resolve };
            post({
                v: PROTO,
                type: 'input-request',
                id: activeRun.id,
                requestId: requestId,
                prompt: String(promptText || ''),
            });
        });
    };

    function initPyodide() {
        if (pyodideReady) return pyodideReady;
        pyodideReady = window.loadPyodide({ indexURL: PYODIDE_INDEX })
            .then(function (py) {
                pyodide = py;
                py.setStdout({
                    batched: function (s) {
                        stdoutBuffer += s + '\n';
                        if (activeRun) {
                            post({ v: PROTO, type: 'stdout', id: activeRun.id, text: String(s) });
                        }
                    },
                });
                py.setStderr({
                    batched: function (s) {
                        if (activeRun) {
                            post({ v: PROTO, type: 'stderr', id: activeRun.id, text: String(s) });
                        }
                    },
                });
                py.setStdin({ stdin: readStdin, isatty: false });
                py.runPython(PREAMBLE);
                post({ v: PROTO, type: 'ready' });
                return py;
            })
            .catch(function (err) {
                post({
                    v: PROTO,
                    type: 'fatal',
                    message: err && err.message ? err.message : 'Pyodide load failed',
                });
            });
        return pyodideReady;
    }

    function finishRun(state) {
        if (!activeRun || activeRun.id !== state.id) return;
        var run = activeRun;
        activeRun = null;
        post({
            v: PROTO,
            type: state.type,
            id: run.id,
            message: state.message,
            stdout: stdoutBuffer,
        });
    }

    function runCode(msg) {
        if (activeRun) {
            post({ v: PROTO, type: 'error', id: msg.id, message: 'Runner busy' });
            return;
        }
        var limit = msg.limit || EXEC_LIMIT_S;
        activeRun = { id: msg.id, pendingInput: null };
        stdoutBuffer = '';
        stdinLines = msg.stdin ? String(msg.stdin).replace(/\n$/, '').split('\n') : [];
        stdinPos = 0;

        initPyodide().then(function () {
            if (!pyodide || !activeRun || activeRun.id !== msg.id) return;

            try { pyodide.globals.set('__pg_src', msg.code); } catch (e) {}

            var mode = 'none';
            try { mode = pyodide.runPython('__pg_input_mode(__pg_src)'); } catch (e) {}

            var call = (mode === 'async')
                ? 'await __pg_run_async(__pg_src, ' + limit + '.0)'
                : '__pg_run_sync(__pg_src, ' + limit + '.0)';

            return pyodide.runPythonAsync(call);
        }).then(function () {
            if (!activeRun || activeRun.id !== msg.id) return;
            finishRun({ id: msg.id, type: 'done' });
        }).catch(function (err) {
            if (!activeRun || activeRun.id !== msg.id) return;
            finishRun({
                id: msg.id,
                type: 'error',
                message: cleanTraceback(err && err.message, limit),
            });
        }).finally(function () {
            try { if (pyodide) pyodide.globals.delete('__pg_src'); } catch (e) {}
        });
    }

    function abortRun(id) {
        if (!activeRun || activeRun.id !== id) return;
        if (activeRun.pendingInput) {
            activeRun.pendingInput.resolve('');
            activeRun.pendingInput = null;
        }
        finishRun({ id: id, type: 'error', message: '⏱ Выполнение прервано.' });
    }

    window.addEventListener('message', function (event) {
        var data = event.data;
        if (!data || data.v !== PROTO) return;

        if (data.type === 'run') {
            runCode(data);
            return;
        }
        if (data.type === 'abort') {
            abortRun(data.id);
            return;
        }
        if (data.type === 'input-response' && activeRun && activeRun.id === data.id) {
            if (activeRun.pendingInput && activeRun.pendingInput.requestId === data.requestId) {
                var pending = activeRun.pendingInput;
                activeRun.pendingInput = null;
                pending.resolve(data.value == null ? '' : String(data.value));
            }
        }
    });

    if (typeof window.loadPyodide === 'function') initPyodide();
    else window.addEventListener('load', initPyodide);
})();
