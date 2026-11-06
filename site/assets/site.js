document.querySelectorAll('[data-copy]').forEach((button) => {
  button.addEventListener('click', async () => {
    const source = document.getElementById(button.dataset.copy);
    if (!source) return;
    const original = button.textContent;
    const ru = document.documentElement.lang === 'ru';
    try {
      await navigator.clipboard.writeText(source.textContent.trim());
      button.textContent = ru ? 'Скопировано ✓' : 'Copied ✓';
    } catch {
      button.textContent = ru ? 'Выделите и скопируйте текст' : 'Select and copy the text';
    }
    window.setTimeout(() => { button.textContent = original; }, 2500);
  });
});
