const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

const revealObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add('visible');
    observer.unobserve(entry.target);
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', () => document.body.classList.remove('menu-open'));
});

const navLinks = [...document.querySelectorAll('.topbar nav a')];
const sections = [...document.querySelectorAll('main section[id]')];
const activeObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    navLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
  });
}, { rootMargin: '-35% 0px -55% 0px' });
sections.forEach((section) => activeObserver.observe(section));

const activeStyle = document.createElement('style');
activeStyle.textContent = '.topbar nav a.active{color:var(--red)}';
document.head.appendChild(activeStyle);
