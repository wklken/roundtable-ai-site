(() => {
  const picker = document.getElementById('site-language');
  if (!picker) return;
  const storageKey = 'roundtable-site-language';
  const options = [...picker.options];
  picker.addEventListener('change', () => {
    const option = picker.selectedOptions[0];
    try { localStorage.setItem(storageKey, option.value); } catch (_) { /* Storage can be disabled. */ }
    location.assign(option.dataset.url + location.hash);
  });
  // Honor a previous choice only on the unqualified homepage. Shared localized
  // URLs and direct legal links always keep their explicitly requested language.
  if (document.documentElement.dataset.locale === 'en' &&
      document.documentElement.dataset.route === '' && !location.hash) {
    let preference;
    try { preference = localStorage.getItem(storageKey); } catch (_) { return; }
    const option = options.find(item => item.value === preference);
    if (option && preference !== 'en') location.replace(option.dataset.url);
  }
})();
