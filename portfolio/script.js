const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

const header = document.querySelector('.site-header');
const updateHeader = () => header?.classList.toggle('scrolled', window.scrollY > 20);
window.addEventListener('scroll', updateHeader, { passive: true });
updateHeader();

document.querySelectorAll('a[target="_blank"]').forEach((link) => {
  link.setAttribute('rel', 'noreferrer noopener');
});

const navLinks = [...document.querySelectorAll('.site-header nav a')];
const sections = [...document.querySelectorAll('main section[id]')];
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      navLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
    });
  }, { rootMargin: '-35% 0px -55% 0px' });
  sections.forEach((section) => observer.observe(section));
}

const style = document.createElement('style');
style.textContent = '.site-header.scrolled{box-shadow:0 1px 0 #d9d9d9;background:rgba(255,255,255,.94)}.site-header nav a.active{font-weight:700;text-decoration:underline;text-underline-offset:4px}';
document.head.appendChild(style);

console.info('[portfolio] ready; css visuals:', document.querySelectorAll('.project-art').length);
console.info('[portfolio] external images:', document.querySelectorAll('img').length);
console.info('[portfolio] placeholders:', document.querySelectorAll('a[href*="you@example"], a[href*="your_telegram"]').length);
document.body.dataset.portfolioReady = 'true';

window.addEventListener('hashchange', () => {
  const target = document.querySelector(window.location.hash);
  if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

if (document.documentElement.scrollWidth > window.innerWidth + 1) {
  console.warn('[portfolio] horizontal overflow detected');
}

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.documentElement.style.scrollBehavior = 'auto';
}

// Сайт остаётся полностью статическим: внешние изображения и блокирующие загрузчики не используются.
void 0;
