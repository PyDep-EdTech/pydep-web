/**
 * PyDep — умный поиск курсов: подсказки, горячие клавиши, авто-фильтры.
 */
(function () {
    var form = document.getElementById('courseSearchForm');
    var input = document.getElementById('courseSearchInput');
    var suggestions = document.getElementById('courseSearchSuggestions');
    if (!form || !input || !suggestions) {
        return;
    }

    var apiUrl = form.dataset.searchUrl;
    var debounceTimer = null;
    var activeIndex = -1;
    var latestItems = [];

    function currentParams() {
        return new URLSearchParams(new FormData(form));
    }

    function hideSuggestions() {
        suggestions.hidden = true;
        suggestions.innerHTML = '';
        activeIndex = -1;
        latestItems = [];
    }

    function escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function renderSuggestions(data) {
        if (!data.results || !data.results.length) {
            suggestions.innerHTML =
                '<div class="catalog-suggest-meta">Ничего не найдено — попробуйте другое слово или сбросьте фильтры</div>';
            suggestions.hidden = false;
            return;
        }

        var itemsHtml = data.results
            .map(function (item, index) {
                latestItems[index] = item;
                return (
                    '<a class="catalog-suggest-item" href="' +
                    escapeHtml(item.url) +
                    '" data-index="' +
                    index +
                    '">' +
                    (item.image
                        ? '<img src="' + escapeHtml(item.image) + '" alt="">'
                        : '<span></span>') +
                    '<div><div class="catalog-suggest-title">' +
                    escapeHtml(item.name) +
                    '</div><div class="catalog-suggest-sub">' +
                    escapeHtml(item.language) +
                    ' · ' +
                    escapeHtml(item.level) +
                    '</div></div>' +
                    '<span class="catalog-suggest-badge">от ' +
                    escapeHtml(String(item.monthly_price)) +
                    ' ₽</span></a>'
                );
            })
            .join('');

        suggestions.innerHTML =
            '<div class="catalog-suggest-meta">' +
            escapeHtml(String(data.total)) +
            ' ' +
            pluralCourses(data.total) +
            '</div>' +
            itemsHtml;
        suggestions.hidden = false;
    }

    function pluralCourses(n) {
        var mod10 = n % 10;
        var mod100 = n % 100;
        if (mod10 === 1 && mod100 !== 11) return 'курс';
        if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return 'курса';
        return 'курсов';
    }

    function fetchSuggestions() {
        var q = input.value.trim();
        if (q.length < 2) {
            hideSuggestions();
            return;
        }

        var params = currentParams();
        params.set('q', q);

        fetch(apiUrl + '?' + params.toString(), {
            headers: { Accept: 'application/json' },
        })
            .then(function (res) {
                return res.json();
            })
            .then(renderSuggestions)
            .catch(function () {
                hideSuggestions();
            });
    }

    function setActiveSuggestion(index) {
        var items = suggestions.querySelectorAll('.catalog-suggest-item');
        items.forEach(function (el, i) {
            el.classList.toggle('is-active', i === index);
        });
        activeIndex = index;
    }

    input.addEventListener('input', function () {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(fetchSuggestions, 220);
    });

    input.addEventListener('focus', function () {
        if (input.value.trim().length >= 2) {
            fetchSuggestions();
        }
    });

    input.addEventListener('keydown', function (event) {
        var items = suggestions.querySelectorAll('.catalog-suggest-item');
        if (!items.length || suggestions.hidden) {
            return;
        }

        if (event.key === 'ArrowDown') {
            event.preventDefault();
            var next = activeIndex + 1;
            if (next >= items.length) next = 0;
            setActiveSuggestion(next);
            items[next].scrollIntoView({ block: 'nearest' });
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            var prev = activeIndex - 1;
            if (prev < 0) prev = items.length - 1;
            setActiveSuggestion(prev);
            items[prev].scrollIntoView({ block: 'nearest' });
        } else if (event.key === 'Enter' && activeIndex >= 0) {
            event.preventDefault();
            window.location.href = latestItems[activeIndex].url;
        } else if (event.key === 'Escape') {
            hideSuggestions();
        }
    });

    suggestions.addEventListener('mouseover', function (event) {
        var item = event.target.closest('.catalog-suggest-item');
        if (!item) return;
        setActiveSuggestion(Number(item.dataset.index));
    });

    document.addEventListener('click', function (event) {
        if (!form.contains(event.target)) {
            hideSuggestions();
        }
    });

    form.querySelectorAll('.catalog-auto-submit').forEach(function (el) {
        el.addEventListener('change', function () {
            hideSuggestions();
            form.requestSubmit();
        });
    });

    form.addEventListener('submit', hideSuggestions);

    var filtersToggle = document.getElementById('catalogFiltersToggle');
    var filtersPanel = document.getElementById('catalogFiltersPanel');
    if (filtersToggle && filtersPanel) {
        function setFiltersOpen(open) {
            filtersToggle.classList.toggle('is-open', open);
            filtersToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            filtersPanel.setAttribute('aria-hidden', open ? 'false' : 'true');

            if (open) {
                window.requestAnimationFrame(function () {
                    window.requestAnimationFrame(function () {
                        filtersPanel.classList.add('is-open');
                    });
                });
                return;
            }

            filtersPanel.classList.remove('is-open');
        }

        filtersToggle.addEventListener('click', function () {
            setFiltersOpen(!filtersPanel.classList.contains('is-open'));
        });

        if (filtersPanel.classList.contains('is-open')) {
            filtersToggle.classList.add('is-open');
        }
    }
})();
