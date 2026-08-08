# 🚀 Как выложить портфолио на GitHub Pages (пошагово)

Этот файл — инструкция для тебя. Я не могу запушить (на моей машине нет токена GitHub),
поэтому делаешь это сам за 5 минут в браузере или терминале.

## Вариант А: Через терминал (если настроишь git)

Замени `kibert117` на свой ник везде в файлах (index.html, script.js, README).

```bash
cd C:/Users/fallen
git init
git add .
git commit -m "portfolio + projects"
git branch -M main
git remote add origin https://github.com/kibert117/portfolio.git
git push -u origin main
```

Потом на GitHub: **Settings → Pages → Source: main → /root → Save**.
Сайт будет: https://kibert117.github.io/portfolio/

## Вариант Б: Через браузер (проще всего)

1. Зайди на github.com → New repository → имя `portfolio` → Public.
2. Нажми **uploading an existing file** и перетащи папки:
   - `portfolio/` (index.html, style.css, script.js)
   - `gta5-fam-bot/`, `discord-rpc/`, `project1/`, `tech-store/` (с их README)
   - `README.md`, `.gitignore`
3. Commit.
4. Settings → Pages → main → Save.

## ⚠️ Важно: замени заглушки на свои
В файлах написано `kibert117`, `your_telegram`, `you@example.com`:
- `portfolio/index.html` — ссылки в контактах
- `portfolio/script.js` — ссылки на проекты и TG
- `README.md` — ссылка на TG
- `gta5-fam-bot/.env` НЕ комить (он в .gitignore), токен бота приватный!

## Проверка локально
Открой `C:/Users/fallen/portfolio/index.html` в браузере — должны появиться
6 карточек проектов, навыки и контакты. Если пусто — проверь, что script.js рядом.
