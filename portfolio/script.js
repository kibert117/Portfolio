// Данные проектов — правь здесь, чтобы обновить портфолио
const PROJECTS = [
    {
        icon: '🤖',
        title: 'GTA5 Fam Bot',
        desc: 'Discord-бот на discord.py: модерация чата, авто-выдача ролей, система тикетов, фильтр мата, мемы и развлекательные команды.',
        tags: ['discord.py', 'Python', 'Модерация'],
        link: 'https://github.com/kibert117/gta5-fam-bot',
        linkText: 'Код на GitHub'
    },
    {
        icon: '🎮',
        title: 'Pygame Games',
        desc: 'Сборник из 6 игр: Змейка (3 варианта), Rocket, DOOM Legacy, game3. Полностью на Python + pygame, с игровым циклом и физикой.',
        tags: ['Python', 'pygame', '2D'],
        link: 'https://github.com/kibert117/project1',
        linkText: 'Код на GitHub'
    },
    {
        icon: '🌐',
        title: 'TechZone Store',
        desc: 'Статический интернет-магазин техники: каталог, поиск, корзина, модалки, личный кабинет, отзывы. Чистый HTML/CSS/JS.',
        tags: ['HTML', 'CSS', 'JavaScript'],
        link: 'https://github.com/kibert117/tech-store',
        linkText: 'Код на GitHub'
    },
    {
        icon: '⚡',
        title: 'Discord RPC Manager',
        desc: 'Node.js + Express + WebSocket менеджер Discord Rich Presence: профили активности, история, кастомные пресеты, загрузка картинок.',
        tags: ['Node.js', 'Express', 'WebSocket'],
        link: 'https://github.com/kibert117/discord-rpc',
        linkText: 'Код на GitHub'
    },
    {
        icon: '🤖',
        title: 'TG-бот (шаблон)',
        desc: 'Готовый каркас Telegram-бота на aiogram 3 + SQLite: приём заявок, уведомления админу, админ-панель. База для заказов.',
        tags: ['aiogram', 'Python', 'SQLite'],
        link: 'https://github.com/kibert117/tg_bot_template',
        linkText: 'Код на GitHub'
    },
    {
        icon: '💬',
        title: 'Telegram-боты (услуга)',
        desc: 'Пишу Telegram-ботов на aiogram: боты-ассистенты, приём заявок, админ-панели, интеграции API, Mini Apps. Работаю через Safe Deal.',
        tags: ['aiogram', 'Python', 'Заказы'],
        link: 'https://t.me/your_telegram',
        linkText: 'Написать в TG'
    },
    {
        icon: '🛠️',
        title: 'Лендинги (услуга)',
        desc: 'Верстаю одностраничные сайты на чистом HTML/CSS/JS: адаптив, анимации, формы заявок. Быстро и без тяжёлых конструкторов.',
        tags: ['HTML', 'CSS', 'JS'],
        link: 'https://t.me/your_telegram',
        linkText: 'Написать в TG'
    }
];

function renderProjects() {
    const grid = document.getElementById('projectGrid');
    if (!grid) return;
    grid.innerHTML = PROJECTS.map(p => `
        <div class="card">
            <div class="card-icon">${p.icon}</div>
            <h3>${p.title}</h3>
            <p>${p.desc}</p>
            <div class="card-tags">${p.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>
            <a class="card-link" href="${p.link}" target="_blank" rel="noopener">${p.linkText} →</a>
        </div>
    `).join('');
}

document.addEventListener('DOMContentLoaded', () => {
    renderProjects();
    const y = document.getElementById('year');
    if (y) y.textContent = new Date().getFullYear();
});
