// плавный скролл по якорям
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

document.querySelectorAll('a[target="_blank"]').forEach((link) => {
  link.setAttribute('rel', 'noreferrer noopener');
});

// случайный "глитч"-сдвиг блоков шума (уважает reduced-motion)
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (reduced) document.documentElement.style.scrollBehavior = 'auto';

if (!reduced) {
  const targets = document.querySelectorAll('.glitch, .case-noise');
  setInterval(() => {
    const el = targets[Math.floor(Math.random() * targets.length)];
    if (!el) return;
    el.style.transform += ' translateX(3px)';
    setTimeout(() => {
      el.style.transform = el.style.transform.replace(' translateX(3px)', '');
    }, 90);
  }, 1400);
}

// подсветка активной секции в навигации
const chips = [...document.querySelectorAll('.topnav .chip[href^="#"]')];
const sections = [...document.querySelectorAll('main section[id]')];
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      chips.forEach((chip) => {
        chip.style.background = chip.hash === `#${entry.target.id}` ? '#ff1f1f' : '';
        chip.style.color = chip.hash === `#${entry.target.id}` ? '#fff' : '';
      });
    });
  }, { rootMargin: '-40% 0px -50% 0px' });
  sections.forEach((section) => observer.observe(section));
}

if (document.documentElement.scrollWidth > window.innerWidth + 1) {
  console.warn('[kibert] horizontal overflow detected');
}

console.info('[kibert] glitch portfolio ready; images:', document.images.length);
document.body.dataset.portfolioReady = 'true';
