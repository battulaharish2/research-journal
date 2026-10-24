const buttons = [...document.querySelectorAll('[data-photo]')];
const dialog = document.querySelector('dialog');
let current = 0;
function show(index) {
  current = (index + buttons.length) % buttons.length;
  const button = buttons[current];
  dialog.querySelector('img').src = button.dataset.photo;
  dialog.querySelector('img').alt = button.dataset.caption;
  dialog.querySelector('p').textContent = button.dataset.caption;
  dialog.querySelector('[data-count]').textContent = `${current + 1} / ${buttons.length}`;
}
buttons.forEach((button, index) => button.addEventListener('click', () => { show(index); dialog.showModal(); }));
if (dialog) {
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.querySelector('[data-prev]').addEventListener('click', () => show(current - 1));
  dialog.querySelector('[data-next]').addEventListener('click', () => show(current + 1));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); show(current - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); show(current + 1); }
  });
}
