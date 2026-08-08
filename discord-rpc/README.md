# ⚡ Discord RPC Manager

Менеджер Discord Rich Presence на **Node.js** (Express + WebSocket + Multer). Позволяет ставить кастомную активность в Discord через веб-интерфейс.

## Возможности
- Веб-интерфейс (в `public/index.html`) для управления Rich Presence
- Профили активности (`data/profiles.json`), история (`history.json`)
- Кастомные пресеты (`custom_presets.json`)
- Загрузка картинок через Multer (`public/uploads/`)
- WebSocket (`ws`) для живого обновления статуса

## Структура
- `server.js` — сервер (Express + WS), логика RPC
- `package.json` — зависимости и скрипты
- `public/index.html` — фронтенд
- `data/` — файлы состояния (создаются автоматически)
- `start.bat` — быстрый запуск на Windows

## Установка и запуск
```bash
npm install
npm start
# открой http://localhost:3000
```

> Для работы Rich Presence требуется локальный Discord-клиент и настройка приложения в Discord Developer Portal.

---
© Dev Portfolio
