(() => {
  const root = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const themeIcon = themeToggle.querySelector(".theme-icon");
  const themeLabel = themeToggle.querySelector(".theme-label");
  const themeColor = document.querySelector('meta[name="theme-color"]');
  const navButtons = [...document.querySelectorAll("[data-filter], [data-scroll]")];
  const projectCards = [...document.querySelectorAll(".project-card")];
  const projectCount = document.getElementById("projectCount");
  const modal = document.getElementById("projectModal");
  const modalPanel = modal.querySelector(".modal-panel");
  const modalClose = document.getElementById("modalClose");
  const modalTitle = document.getElementById("modalTitle");
  const modalKicker = document.getElementById("modalKicker");
  const modalBody = document.getElementById("modalBody");
  let lastFocusedElement = null;

  const projectDetails = {
    gta5: {
      title: "GTA5 FAM BOT//",
      kicker: "01 / bots / discord.py",
      paragraphs: [
        "Discord-бот для игрового сообщества. Закрывает базу: модерацию каналов, систему тикетов для обращений и автоматическую выдачу ролей.",
        "Собран на discord.py. Логика разбита на модули — проще добавлять команды и править поведение без переписывания всего бота."
      ],
      tags: ["discord.py", "модерация", "тикеты", "роли"]
    },
    rpc: {
      title: "DISCORD RPC//",
      kicker: "02 / bots / node.js",
      paragraphs: [
        "Менеджер Discord Rich Presence с веб-панелью. Статус в профиле управляется из браузера через WebSocket-соединение.",
        "Стек: Node.js + Express на бэкенде и vanilla JS на фронте. Никаких тяжёлых фреймворков — только нужный минимум."
      ],
      tags: ["node.js", "express", "websocket", "rich presence"]
    },
    pygame: {
      title: "PYGAME PACK//",
      kicker: "03 / games / pygame",
      paragraphs: [
        "Коллекция из 6 игр на Pygame с собственными механиками: Змейка, Rocket, DOOM Legacy и другие.",
        "Каждая игра — отдельный модуль с игровым циклом, обработкой ввода и уровнями. Хорошая практика по архитектуре 2D-игр."
      ],
      tags: ["pygame", "2d", "игровой цикл", "механики"]
    },
    store: {
      title: "TECH STORE//",
      kicker: "04 / web / html",
      paragraphs: [
        "Интернет-магазин техники на чистом HTML/CSS/JS. Каталог товаров, живой поиск и корзина без бэкенда.",
        "Работает как статичный сайт — открывается сразу, без сборки и зависимостей. Ссылка на живую версию есть на карточке."
      ],
      tags: ["html", "css", "vanilla js", "корзина"]
    },
    tgbot: {
      title: "TG BOT TEMPLATE//",
      kicker: "05 / bots / aiogram",
      paragraphs: [
        "Шаблон Telegram-бота на aiogram: пользователь отправляет заявку, админ видит её в админке и обрабатывает.",
        "Стартовая точка для новых заказов — базовая логика уже готова, остаётся дописать конкретную задачу."
      ],
      tags: ["aiogram", "заявки", "админка", "шаблон"]
    },
    site: {
      title: "PORTFOLIO//",
      kicker: "06 / web / html",
      paragraphs: [
        "Этот сайт. Тёмная и светлая темы с сохранением выбора, фильтры проектов по категориям, модальные окна кейсов.",
        "Один файл стилей, ванильный JavaScript, ноль внешних зависимостей. Деплой — на GitHub Pages."
      ],
      tags: ["html", "css", "vanilla js", "github pages"]
    }
  };

  const setTheme = (theme) => {
    const isDark = theme === "dark";
    root.dataset.theme = isDark ? "dark" : "light";
    themeIcon.textContent = isDark ? "☾" : "☼";
    themeLabel.textContent = isDark ? "dark" : "light";
    themeToggle.setAttribute("aria-pressed", String(!isDark));
    themeToggle.setAttribute("aria-label", isDark ? "Переключить на светлую тему" : "Переключить на тёмную тему");
    themeColor.setAttribute("content", isDark ? "#0b0b0b" : "#f3f3f1");
    try {
      localStorage.setItem("kibert-theme", isDark ? "dark" : "light");
    } catch (error) {
      // localStorage может быть недоступен в приватном режиме — сайт всё равно работает.
    }
  };

  let savedTheme = null;
  try {
    savedTheme = localStorage.getItem("kibert-theme");
  } catch (error) {
    savedTheme = null;
  }
  setTheme(savedTheme === "light" || savedTheme === "dark" ? savedTheme : "dark");

  themeToggle.addEventListener("click", () => {
    setTheme(root.dataset.theme === "dark" ? "light" : "dark");
  });

  const updateCount = (visibleCount) => {
    const suffix = visibleCount === 1 ? "проект" : visibleCount >= 2 && visibleCount <= 4 ? "проекта" : "проектов";
    projectCount.textContent = `${String(visibleCount).padStart(2, "0")} ${suffix}`;
  };

  const applyFilter = (filter) => {
    let visibleCount = 0;
    projectCards.forEach((card) => {
      const visible = filter === "all" || card.dataset.category === filter;
      card.classList.toggle("is-hidden", !visible);
      if (visible) visibleCount += 1;
    });
    updateCount(visibleCount);
    navButtons.forEach((button) => {
      if (button.dataset.filter) button.classList.toggle("is-active", button.dataset.filter === filter);
    });
  };

  navButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.filter) {
        applyFilter(button.dataset.filter);
        document.getElementById("portfolio").scrollIntoView({ behavior: "smooth", block: "start" });
      }
      if (button.dataset.scroll) {
        document.getElementById(button.dataset.scroll).scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  const openModal = (projectId, trigger) => {
    const project = projectDetails[projectId];
    if (!project) return;
    lastFocusedElement = trigger;
    modalTitle.textContent = project.title;
    modalKicker.textContent = project.kicker;
    modalBody.replaceChildren();
    project.paragraphs.forEach((paragraph) => {
      const paragraphElement = document.createElement("p");
      paragraphElement.className = "modal-copy";
      paragraphElement.textContent = paragraph;
      modalBody.appendChild(paragraphElement);
    });
    const tagsElement = document.createElement("div");
    tagsElement.className = "tags-cloud modal-tags";
    project.tags.forEach((tag) => {
      const tagElement = document.createElement("span");
      tagElement.className = "tag";
      tagElement.textContent = `{${tag}}`;
      tagsElement.appendChild(tagElement);
    });
    modalBody.appendChild(tagsElement);
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    modalClose.focus();
  };

  const closeModal = () => {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (lastFocusedElement) lastFocusedElement.focus();
  };

  document.querySelectorAll("[data-open-project]").forEach((button) => {
    button.addEventListener("click", () => openModal(button.dataset.openProject, button));
  });

  modalClose.addEventListener("click", closeModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("is-open")) closeModal();
    if (event.key === "Tab" && modal.classList.contains("is-open")) {
      const focusable = [modalClose, ...modalPanel.querySelectorAll("a, button")];
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });
})();
