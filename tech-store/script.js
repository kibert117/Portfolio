const products = [
    { id: 1, name: "iPhone 17 Pro Max", category: "iphone", price: 159990, rating: 5, desc: "A19 Pro, титановый корпус, камера 48 Мп с 5× зумом, 33 ч батареи",
      img: "https://img.appledb.dev/device@512/iPhone16,2/Natural%20Titanium.png" },
    { id: 2, name: "iPhone 17 Pro", category: "iphone", price: 129990, rating: 5, desc: "A19 Pro, камера 48 Мп, 3× оптический зум, титан",
      img: "https://img.appledb.dev/device@512/iPhone16,1/Natural%20Titanium.png" },
    { id: 3, name: "iPhone 16", category: "iphone", price: 79990, rating: 4, desc: "A18, камера 48 Мп, Dynamic Island, USB-C",
      img: "https://img.appledb.dev/device@512/iPhone15,4/Black.png" },
    { id: 4, name: "iPhone 16 Plus", category: "iphone", price: 89990, rating: 4, desc: "A18, большой 6.7\" дисплей, батарея на весь день",
      img: "https://img.appledb.dev/device@512/iPhone15,5/Black.png" },
    { id: 5, name: "MacBook Pro M4 Pro", category: "mac", price: 249990, rating: 5, desc: "Чип M4 Pro, 24 ГБ RAM, Liquid Retina XDR, 22 ч батареи",
      img: "https://img.appledb.dev/device@512/Mac15,7/Space%20Black.png" },
    { id: 6, name: "MacBook Pro M4", category: "mac", price: 179990, rating: 5, desc: "Чип M4, 16 ГБ RAM, Liquid Retina XDR дисплей",
      img: "https://img.appledb.dev/device@512/Mac15,3/Space%20Black.png" },
    { id: 7, name: "MacBook Air M3", category: "mac", price: 109990, rating: 5, desc: "Чип M3, ультратонкий, 18 часов батареи, Retina",
      img: "https://img.appledb.dev/device@512/Mac15,12/Midnight.png" },
    { id: 8, name: "MacBook Air M2", category: "mac", price: 89990, rating: 4, desc: "Чип M2, 13.6\" Liquid Retina, до 18 ч работы",
      img: "https://img.appledb.dev/device@512/Mac14,15/Midnight.png" },
    { id: 9, name: "AirPods Pro 2", category: "airpods", price: 19990, rating: 5, desc: "Адаптивное аудио, USB-C, пространственный звук, ANC",
      img: "https://img.appledb.dev/device@512/AirPodsPro2,1/default.png" },
    { id: 10, name: "AirPods Max", category: "airpods", price: 54990, rating: 5, desc: "Полноразмерные, ANC, пространственный звук, 20 ч",
      img: "https://img.appledb.dev/device@512/AirPodsMax1,1/Space%20Gray.png" },
    { id: 11, name: "AirPods 4", category: "airpods", price: 13990, rating: 4, desc: "Новый дизайн, USB-C, адаптивное аудио",
      img: "https://img.appledb.dev/device@512/AirPods4,1/default.png" },
    { id: 12, name: "Apple Watch Ultra 2", category: "watch", price: 64990, rating: 5, desc: "Титан, двухчастотный GPS, 36 ч батареи",
      img: "https://img.appledb.dev/device@512/Watch6,10/Natural%20Titanium.png" },
    { id: 13, name: "Apple Watch Series 10", category: "watch", price: 39990, rating: 5, desc: "Тоньше корпус, экран Always-On, пульсоксиметр",
      img: "https://img.appledb.dev/device@512/Watch6,9/Black%20Aluminum.png" },
    { id: 14, name: "Apple Watch SE", category: "watch", price: 24990, rating: 4, desc: "Доступные умные часы, все базовые функции Apple",
      img: "https://img.appledb.dev/device@512/Watch5,9/Midnight.png" },
    { id: 15, name: "MagSafe зарядка", category: "accessories", price: 4490, rating: 4, desc: "Беспроводная зарядка 25 Вт, совместимость со всеми iPhone",
      img: "" },
    { id: 16, name: "AirTag 4-pack", category: "accessories", price: 10990, rating: 4, desc: "Точное отслеживание, UWB, замена батарейки",
      img: "" },
    { id: 17, name: "Apple Pencil Pro", category: "accessories", price: 12990, rating: 5, desc: "Хват, вращение, тактильная отдача, магнитное крепление",
      img: "" },
    { id: 18, name: "Magic Keyboard", category: "accessories", price: 29990, rating: 5, desc: "Для iPad Pro, подсветка, USB-C, трекпад",
      img: "" },
];

const categoryIcons = {
    iphone: "📱", mac: "💻", airpods: "🎧", watch: "⌚", accessories: "📦"
};

const bgClasses = {
    iphone: "iphone", mac: "mac", airpods: "airpods", watch: "watch", accessories: "accessories"
};

let cart = JSON.parse(localStorage.getItem('cart')) || [];
let user = JSON.parse(localStorage.getItem('user')) || null;
let reviews = JSON.parse(localStorage.getItem('reviews')) || [
    { name: "Алексей", rating: 5, text: "Купил iPhone 17 Pro Max — камера просто космос! Доставка за день.", date: "01.07.2026" },
    { name: "Мария", rating: 5, text: "MacBook Pro M4 Pro — лучший ноутбук, который у меня был.", date: "03.07.2026" },
    { name: "Дмитрий", rating: 4, text: "AirPods Pro 2 — шумоподавление на высоте. Рекомендую этот магазин.", date: "04.07.2026" },
];
let orders = JSON.parse(localStorage.getItem('orders')) || [];

function save() {
    localStorage.setItem('cart', JSON.stringify(cart));
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('reviews', JSON.stringify(reviews));
    localStorage.setItem('orders', JSON.stringify(orders));
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

function productImg(p) {
    if (p.img) return `<img src="${p.img}" alt="${p.name}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="product-icon-fallback" style="display:none">${categoryIcons[p.category]}</div>`;
    return `<div class="product-icon-fallback" style="display:flex">${categoryIcons[p.category]}</div>`;
}

function initReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('revealed');
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale').forEach(el => {
        if (!el.classList.contains('revealed')) observer.observe(el);
    });
}

function createParticles() {
    const container = document.getElementById('heroParticles');
    if (!container) return;
    const colors = ['#0071e3', '#5856d6', '#fff'];
    for (let i = 0; i < 20; i++) {
        const p = document.createElement('div');
        p.classList.add('particle');
        const size = Math.random() * 4 + 1;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + '%';
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        p.style.animationDuration = (Math.random() * 18 + 12) + 's';
        p.style.animationDelay = (Math.random() * 10) + 's';
        p.style.boxShadow = `0 0 ${size * 3}px ${p.style.background}`;
        container.appendChild(p);
    }
}

function animateCounters() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                entry.target.dataset.animated = 'true';
                const target = +entry.target.dataset.target;
                const duration = 1800;
                const step = target / (duration / 16);
                let current = 0;
                const update = () => {
                    current += step;
                    if (current < target) {
                        entry.target.textContent = Math.floor(current).toLocaleString();
                        requestAnimationFrame(update);
                    } else {
                        entry.target.textContent = target.toLocaleString();
                    }
                };
                update();
            }
        });
    }, { threshold: 0.5 });
    document.querySelectorAll('.hero-stat-num, .stats-num').forEach(c => observer.observe(c));
}

function initNavbar() {
    const header = document.getElementById('header');
    if (header) {
        window.addEventListener('scroll', () => {
            header.classList.toggle('scrolled', window.scrollY > 60);
        });
    }
    const burger = document.getElementById('burger');
    const navLinks = document.getElementById('navLinks');
    if (burger && navLinks) {
        burger.addEventListener('click', () => navLinks.classList.toggle('active'));
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => navLinks.classList.remove('active'));
        });
    }
}

function initAccordion() {
    document.querySelectorAll('.accordion-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const item = btn.parentElement;
            const wasActive = item.classList.contains('active');
            document.querySelectorAll('.accordion-item').forEach(i => i.classList.remove('active'));
            if (!wasActive) item.classList.add('active');
        });
    });
}

function renderProducts(list) {
    const grid = document.getElementById('productGrid');
    grid.innerHTML = list.map((p, i) => `
        <div class="product-card reveal" data-id="${p.id}" style="transition-delay:${i * 0.05}s">
            <div class="product-image ${bgClasses[p.category]}">${productImg(p)}</div>
            <div class="product-info">
                <h3>${p.name}</h3>
                <div class="rating">${'★'.repeat(p.rating)}${'☆'.repeat(5 - p.rating)}</div>
                <div class="price">${p.price.toLocaleString()} ₽</div>
                <button class="add-to-cart" onclick="event.stopPropagation();addToCart(${p.id})">В корзину</button>
            </div>
        </div>
    `).join('');
    grid.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', () => showProductDetail(+card.dataset.id));
    });
    initReveal();
}

function renderReviews() {
    const list = document.getElementById('reviewsList');
    list.innerHTML = reviews.map((r, i) => `
        <div class="review-card reveal" style="transition-delay:${i * 0.08}s">
            <div class="review-header">
                <span class="review-author">${r.name}</span>
                <span class="review-date">${r.date}</span>
            </div>
            <div class="review-rating">${'★'.repeat(r.rating)}</div>
            <p>${r.text}</p>
        </div>
    `).join('');
    initReveal();
}

function updateCartCount() {
    document.getElementById('cartCount').textContent = cart.reduce((s, i) => s + i.qty, 0);
}

function addToCart(id) {
    const product = products.find(p => p.id === id);
    const existing = cart.find(i => i.id === id);
    if (existing) { existing.qty++; } else { cart.push({ ...product, qty: 1 }); }
    save(); updateCartCount();
    showToast(`${product.name} добавлен в корзину!`);
}

function renderCart() {
    const items = document.getElementById('cartItems');
    if (cart.length === 0) {
        items.innerHTML = '<p style="text-align:center;color:#999;padding:36px;">Корзина пуста</p>';
    } else {
        items.innerHTML = cart.map(i => `
            <div class="cart-item">
                <div class="cart-item-icon">${i.img ? `<img src="${i.img}" alt="${i.name}" style="height:40px" onerror="this.style.display='none';this.insertAdjacentHTML('afterend','<span>${categoryIcons[i.category]}</span>')">` : categoryIcons[i.category]}</div>
                <div class="cart-item-info">
                    <h4>${i.name}</h4>
                    <div class="cart-item-price">${i.price.toLocaleString()} ₽</div>
                </div>
                <div class="cart-item-qty">
                    <button onclick="changeQty(${i.id},-1)">-</button>
                    <span>${i.qty}</span>
                    <button onclick="changeQty(${i.id},1)">+</button>
                    <button class="cart-item-remove" onclick="removeFromCart(${i.id})">✕</button>
                </div>
            </div>
        `).join('');
    }
    document.getElementById('cartTotal').textContent = cart.reduce((s, i) => s + i.price * i.qty, 0).toLocaleString();
}

function changeQty(id, delta) {
    const item = cart.find(i => i.id === id);
    if (item) {
        item.qty += delta;
        if (item.qty <= 0) cart = cart.filter(i => i.id !== id);
        save(); renderCart(); updateCartCount();
    }
}

function removeFromCart(id) {
    cart = cart.filter(i => i.id !== id);
    save(); renderCart(); updateCartCount();
    showToast("Товар удалён из корзины");
}

function showProductDetail(id) {
    const p = products.find(x => x.id === id);
    document.getElementById('productDetail').innerHTML = `
        <div class="product-detail-image ${bgClasses[p.category]}">${productImg(p)}</div>
        <div class="product-detail-info">
            <h2>${p.name}</h2>
            <div class="detail-rating">${'★'.repeat(p.rating)}</div>
            <div class="detail-price">${p.price.toLocaleString()} ₽</div>
            <p class="detail-desc">${p.desc}</p>
            <button class="add-to-cart" onclick="addToCart(${p.id})">Добавить в корзину</button>
        </div>
    `;
    document.getElementById('productModal').classList.add('active');
}

function renderProfile() {
    if (user) {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('profileInfo').style.display = 'block';
        document.getElementById('profileName').textContent = user.name;
        document.getElementById('profileEmail').textContent = user.email;
        document.getElementById('orderCount').textContent = orders.length;
        document.getElementById('totalSpent').textContent = orders.reduce((s, o) => s + o.total, 0).toLocaleString();
        const hist = document.getElementById('orderHistory');
        hist.innerHTML = orders.length === 0
            ? '<p style="color:#999">Нет заказов</p>'
            : orders.map(o => `<div class="order-item"><strong>${o.date}</strong> — ${o.total.toLocaleString()} ₽<br><small>${o.items.map(i => i.name).join(', ')}</small></div>`).join('');
    } else {
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('profileInfo').style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    initNavbar();
    initAccordion();
    animateCounters();
    renderProducts(products);
    renderReviews();
    updateCartCount();

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const f = btn.dataset.filter;
            renderProducts(f === 'all' ? products : products.filter(p => p.category === f));
        });
    });

    document.getElementById('searchInput')?.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        if (!q) { renderProducts(products); return; }
        renderProducts(products.filter(p => p.name.toLowerCase().includes(q) || p.desc.toLowerCase().includes(q)));
    });

    document.getElementById('cartBtn').addEventListener('click', (e) => { e.preventDefault(); renderCart(); document.getElementById('cartModal').classList.add('active'); });
    document.getElementById('profileBtn').addEventListener('click', (e) => { e.preventDefault(); renderProfile(); document.getElementById('profileModal').classList.add('active'); });
    const ctaBtn = document.getElementById('ctaBtn');
    if (ctaBtn) ctaBtn.addEventListener('click', () => { const m = document.getElementById('ctaModal'); if (m) m.classList.add('active'); });

    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => btn.closest('.modal').classList.remove('active'));
    });
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('active'); });
    });

    document.getElementById('checkoutBtn').addEventListener('click', () => {
        if (!cart.length) { showToast("Корзина пуста!"); return; }
        if (!user) { showToast("Сначала войдите в аккаунт!"); return; }
        orders.push({ date: new Date().toLocaleDateString('ru-RU'), items: [...cart], total: cart.reduce((s, i) => s + i.price * i.qty, 0) });
        cart = []; save(); renderCart(); updateCartCount();
        document.getElementById('cartModal').classList.remove('active');
        showToast("Заказ оформлен!");
    });

    document.getElementById('loginBtn').addEventListener('click', () => {
        const name = document.getElementById('loginName').value.trim();
        const email = document.getElementById('loginEmail').value.trim();
        if (!name || !email) { showToast("Заполните все поля!"); return; }
        user = { name, email }; save(); renderProfile();
        showToast(`Добро пожаловать, ${name}!`);
    });

    document.getElementById('logoutBtn').addEventListener('click', () => {
        user = null; save(); renderProfile(); showToast("Вы вышли из аккаунта");
    });

    document.getElementById('submitReview').addEventListener('click', () => {
        const name = document.getElementById('reviewName').value.trim();
        const rating = +document.getElementById('reviewRating').value;
        const text = document.getElementById('reviewText').value.trim();
        if (!name || !text) { showToast("Заполните все поля!"); return; }
        reviews.unshift({ name, rating, text, date: new Date().toLocaleDateString('ru-RU') });
        save(); renderReviews();
        document.getElementById('reviewName').value = '';
        document.getElementById('reviewText').value = '';
        showToast("Отзыв добавлен!");
    });

    const ctaForm = document.getElementById('ctaForm');
    if (ctaForm) ctaForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const m = document.getElementById('ctaModal');
        if (m) m.classList.remove('active');
        showToast("Заявка отправлена!");
    });

    initReveal();
});
