/* Progressive enhancement: every design, fit link and inch chart is in the HTML. */
(() => {
  const finder = document.querySelector('[data-vibe-finder]');
  if (finder) {
    const form = finder.querySelector('[data-vibe-controls]');
    const search = form.querySelector('input[type="search"]');
    const buttons = [...form.querySelectorAll('[data-theme]')];
    const cards = [...finder.querySelectorAll('.vibe-card')];
    const count = finder.querySelector('[data-vibe-count]');
    const empty = finder.querySelector('[data-vibe-empty]');
    const labels = { all: 'all vibes', house: 'House music', nyc: 'NYC', heritage: 'Heritage' };
    const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
    const index = cards.map(card => ({ card, text: normalize(card.dataset.search), themes: card.dataset.vibes.split(' ') }));
    let theme = 'all';

    function render() {
      const terms = normalize(search.value).split(' ').filter(Boolean);
      let visible = 0;
      index.forEach(({ card, text, themes }) => {
        const matches = (theme === 'all' || themes.includes(theme)) && terms.every(term => text.includes(term));
        card.hidden = !matches;
        if (matches) visible++;
      });
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.theme === theme)));
      count.textContent = `${visible} ${visible === 1 ? 'design' : 'designs'}${theme !== 'all' ? ' · ' + labels[theme] : ''}${search.value.trim() ? ' matching “' + search.value.trim() + '”' : ''}`;
      empty.hidden = visible !== 0;
    }
    function save(push = false) {
      const params = new URLSearchParams();
      if (theme !== 'all') params.set('theme', theme);
      if (search.value.trim()) params.set('q', search.value.trim());
      const hash = params.toString();
      const next = location.pathname + location.search + (hash ? '#' + hash : '');
      if (next !== location.pathname + location.search + location.hash) {
        history[push ? 'pushState' : 'replaceState'](null, '', next);
      }
    }
    function restore() {
      const params = new URLSearchParams(location.hash.slice(1));
      theme = Object.hasOwn(labels, params.get('theme')) ? params.get('theme') : 'all';
      search.value = (params.get('q') || '').slice(0, 200);
      render();
    }
    buttons.forEach(button => button.addEventListener('click', () => {
      theme = button.dataset.theme;
      render(); save(true);
    }));
    search.addEventListener('input', () => { render(); save(); });
    form.addEventListener('submit', event => { event.preventDefault(); render(); save(); });
    form.addEventListener('reset', event => {
      event.preventDefault(); search.value = ''; theme = 'all'; render(); save(true); search.focus();
    });
    window.addEventListener('hashchange', restore);
    window.addEventListener('popstate', restore);
    restore(); form.hidden = false;
  }

  const charts = document.querySelector('[data-fit-charts]');
  if (charts) {
    const controls = charts.querySelector('[data-unit-controls]');
    const buttons = [...controls.querySelectorAll('[data-unit]')];
    buttons.forEach(button => button.addEventListener('click', () => {
      const unit = button.dataset.unit;
      charts.querySelectorAll('[data-inches]').forEach(cell => {
        cell.textContent = unit === 'cm' ? (Number(cell.dataset.inches) * 2.54).toFixed(1) : cell.dataset.inches;
      });
      charts.querySelectorAll('[data-unit-label]').forEach(label => { label.textContent = unit; });
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      charts.querySelector('[data-unit-note]').textContent = unit === 'cm'
        ? 'Measurements in centimeters, converted from inches and rounded to one decimal.'
        : 'Measurements in inches. Compare the garment dimensions with a tee you own.';
    }));
    controls.hidden = false;
  }
})();
