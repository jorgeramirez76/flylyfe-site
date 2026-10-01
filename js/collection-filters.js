(() => {
  const buttons = [...document.querySelectorAll('[data-fit-filter]')];
  const sections = [...document.querySelectorAll('[data-fit-section]')];
  const count = document.querySelector('.collection-fit-count');
  if (!buttons.length || !sections.length) return;
  function apply(fit) {
    if (!['all', 'relaxed', 'fitted'].includes(fit)) fit = 'all';
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.fitFilter === fit)));
    sections.forEach(section => { section.hidden = fit !== 'all' && section.dataset.fitSection !== fit; });
    if (count) count.textContent = fit === 'all' ? '28 tees · 14 designs in two fits' : `14 ${fit} tees · 3 colors per design`;
  }
  buttons.forEach(button => button.addEventListener('click', () => {
    const fit = button.dataset.fitFilter;
    apply(fit);
    history.replaceState(null, '', fit === 'all' ? location.pathname + location.search : '#' + fit);
  }));
  window.addEventListener('hashchange', () => apply(location.hash.slice(1)));
  apply(location.hash.slice(1));
})();
