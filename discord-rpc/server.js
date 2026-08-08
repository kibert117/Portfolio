const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const multer = require('multer');
const fs = require('fs');
const net = require('net');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });
const PORT = process.env.PORT || 3000;

const DATA_DIR = path.join(__dirname, 'data');
const UPLOADS_DIR = path.join(__dirname, 'public', 'uploads');
const PROFILES_FILE = path.join(DATA_DIR, 'profiles.json');
const HISTORY_FILE = path.join(DATA_DIR, 'history.json');
const CUSTOM_PRESETS_FILE = path.join(DATA_DIR, 'custom_presets.json');
const SETTINGS_FILE = path.join(DATA_DIR, 'settings.json');

[DATA_DIR, UPLOADS_DIR].forEach(d => { if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true }); });

function loadJson(file, fallback) {
    try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return fallback; }
}
function saveJson(file, data) {
    fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

let profiles = loadJson(PROFILES_FILE, {});
let history = loadJson(HISTORY_FILE, []);
let customPresets = loadJson(CUSTOM_PRESETS_FILE, {});
let settings = loadJson(SETTINGS_FILE, { autoConnect: false, lastClientId: '' });

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, UPLOADS_DIR),
    filename: (req, file, cb) => cb(null, `img_${Date.now()}${path.extname(file.originalname)}`)
});
const upload = multer({
    storage,
    limits: { fileSize: 8 * 1024 * 1024 },
    fileFilter: (req, file, cb) => {
        const ok = /\.(jpe?g|png|gif|webp)$/i.test(path.extname(file.originalname)) && /^image\//.test(file.mimetype);
        cb(null, ok);
    }
});

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

let rpcConnected = false;
let currentActivity = null;
let rpcSocket = null;
let rpcReady = false;
let rpcCallbacks = new Map();
let rpcNonce = 0;
let lastClientId = null;
let autoReconnectTimer = null;

function getIpcPaths() {
    const paths = [];
    if (process.platform === 'win32') {
        for (let i = 0; i < 10; i++) paths.push(String.raw`\\?\pipe\discord-ipc-${i}`);
    } else {
        for (let i = 0; i < 10; i++) paths.push(`/tmp/discord-ipc-${i}`);
        if (process.env.XDG_RUNTIME_DIR) {
            for (let i = 0; i < 10; i++) paths.push(path.join(process.env.XDG_RUNTIME_DIR, `discord-ipc-${i}`));
        }
    }
    return paths;
}

function rpcSend(cmd, args) {
    return new Promise((resolve, reject) => {
        if (!rpcSocket || !rpcReady) return reject(new Error('RPC not ready'));
        const nonce = String(++rpcNonce);
        const payload = JSON.stringify({ cmd, args, nonce });
        const header = Buffer.alloc(8);
        header.writeUInt32LE(1, 0);
        header.writeUInt32LE(Buffer.byteLength(payload), 4);
        const timer = setTimeout(() => {
            rpcCallbacks.delete(nonce);
            reject(new Error('Таймаут ответа'));
        }, 10000);
        rpcCallbacks.set(nonce, { resolve, reject, timer });
        rpcSocket.write(Buffer.concat([header, Buffer.from(payload)]));
    });
}

function setupRpcHandlers() {
    let buffer = Buffer.alloc(0);
    rpcSocket.removeAllListeners();

    rpcSocket.on('data', (data) => {
        buffer = Buffer.concat([buffer, data]);
        while (buffer.length >= 8) {
            const opcode = buffer.readUInt32LE(0);
            const length = buffer.readUInt32LE(4);
            if (buffer.length < 8 + length) break;
            const payload = buffer.slice(8, 8 + length).toString('utf8');
            buffer = buffer.slice(8 + length);
            try {
                const msg = JSON.parse(payload);
                if (msg.cmd === 'AUTH' && msg.evt === 'READY') {
                    rpcReady = true;
                    rpcConnected = true;
                    console.log('[RPC] Discord RPC готов!');
                    broadcast({ type: 'connected' });
                }
                if (msg.evt === 'ERROR') console.error('[RPC] Discord ошибка:', msg.data);
                const cb = rpcCallbacks.get(String(msg.nonce));
                if (cb) {
                    clearTimeout(cb.timer);
                    rpcCallbacks.delete(String(msg.nonce));
                    msg.evt === 'ERROR' ? cb.reject(new Error(msg.data.message)) : cb.resolve(msg);
                }
            } catch (e) { console.error('[RPC] Parse error:', e.message); }
        }
    });

    rpcSocket.on('close', () => {
        console.log('[RPC] Socket closed');
        rpcConnected = false;
        rpcReady = false;
        rpcSocket = null;
        broadcast({ type: 'disconnected' });
        scheduleReconnect();
    });

    rpcSocket.on('error', (err) => {
        console.error('[RPC] Socket error:', err.message);
    });
}

function rpcHandshake(clientId) {
    return new Promise((resolve, reject) => {
        const handshake = JSON.stringify({ v: 1, client_id: clientId, encoding: 'json' });
        const header = Buffer.alloc(8);
        header.writeUInt32LE(0, 0);
        header.writeUInt32LE(Buffer.byteLength(handshake), 4);
        rpcSocket.write(Buffer.concat([header, Buffer.from(handshake)]));

        const timeout = setTimeout(() => reject(new Error('Таймаут хэндшейка')), 5000);
        const check = setInterval(() => {
            if (rpcReady) { clearTimeout(timeout); clearInterval(check); resolve(); }
        }, 50);
        setTimeout(() => { clearInterval(check); clearTimeout(timeout); if (!rpcReady) reject(new Error('Таймаут хэндшейка')); }, 5000);
    });
}

function scheduleReconnect() {
    if (autoReconnectTimer) clearTimeout(autoReconnectTimer);
    if (!settings.autoConnect || !lastClientId) return;
    console.log('[RPC] Переподключение через 5 сек...');
    autoReconnectTimer = setTimeout(() => {
        if (!rpcConnected && lastClientId) {
            console.log('[RPC] Автоподключение...');
            connectDiscord(lastClientId).catch(e => console.log('[RPC] Автоподключение не удалось:', e.message));
        }
    }, 5000);
}

async function connectDiscord(clientId) {
    if (rpcSocket) { rpcSocket.destroy(); rpcSocket = null; rpcConnected = false; rpcReady = false; }
    if (autoReconnectTimer) { clearTimeout(autoReconnectTimer); autoReconnectTimer = null; }

    const paths = getIpcPaths();
    lastClientId = clientId;
    settings.lastClientId = clientId;
    saveJson(SETTINGS_FILE, settings);

    return new Promise((mainResolve, mainReject) => {
        let idx = 0, done = false;
        function tryNext() {
            if (done) return;
            if (idx >= paths.length) { done = true; mainReject(new Error('Discord не найден. Убедитесь, что Discord запущен.')); return; }
            const p = paths[idx++];
            console.log(`[RPC] Пробуем: ${p}`);
            const sock = net.createConnection(p);
            let connected = false;
            const timeout = setTimeout(() => { sock.destroy(); tryNext(); }, 2000);
            sock.on('connect', () => {
                connected = true; clearTimeout(timeout);
                rpcSocket = sock; setupRpcHandlers();
                rpcHandshake(clientId).then(() => { if (!done) { done = true; mainResolve(); } })
                    .catch(err => { console.log(`[RPC] Handshake failed (${p}): ${err.message}`); if (rpcSocket) rpcSocket.destroy(); rpcSocket = null; rpcConnected = false; rpcReady = false; tryNext(); });
            });
            sock.on('error', (err) => { if (!connected) { clearTimeout(timeout); console.log(`[RPC] Error (${p}): ${err.message}`); tryNext(); } });
        }
        tryNext();
    });
}

function addToHistory(activity) {
    history.unshift({ ...activity, timestamp: Date.now() });
    if (history.length > 50) history = history.slice(0, 50);
    saveJson(HISTORY_FILE, history);
    broadcast({ type: 'history_updated', history });
}

function broadcast(data) {
    const msg = JSON.stringify(data);
    wss.clients.forEach(c => { if (c.readyState === WebSocket.OPEN) c.send(msg); });
}

// === API Routes ===
app.post('/api/connect', async (req, res) => {
    try {
        const { clientId } = req.body;
        if (!clientId) return res.status(400).json({ error: 'Client ID обязателен' });
        await connectDiscord(clientId);
        res.json({ success: true, message: 'Подключено к Discord!' });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

app.post('/api/activity', async (req, res) => {
    try {
        if (!rpcConnected || !rpcReady) return res.status(400).json({ error: 'Сначала подключитесь к Discord' });
        const activity = req.body;
        const act = {};
        if (activity.details) act.details = activity.details;
        if (activity.state) act.state = activity.state;
        const resolveImageUrl = (val) => val && val.startsWith('/uploads/') ? `http://localhost:${PORT}${val}` : val;
        if (activity.largeImageKey) act.large_image_key = resolveImageUrl(activity.largeImageKey);
        if (activity.largeImageText) act.large_image_text = activity.largeImageText;
        if (activity.smallImageKey) act.small_image_key = resolveImageUrl(activity.smallImageKey);
        if (activity.smallImageText) act.small_image_text = activity.smallImageText;
        if (activity.buttons && activity.buttons.length > 0) act.buttons = activity.buttons.filter(b => b.label && b.url);
        if (activity.startTimestamp) act.start = Math.floor(Date.now() / 1000);
        if (activity.endTimestamp) act.end = Math.floor(Date.now() / 1000) + activity.endTimestamp;
        await rpcSend('SET_ACTIVITY', { pid: process.pid, activity: act });
        currentActivity = activity;
        addToHistory(activity);
        broadcast({ type: 'activity_updated', activity: currentActivity });
        res.json({ success: true, message: 'Активность установлена!' });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

app.post('/api/clear', async (req, res) => {
    try {
        if (!rpcConnected || !rpcReady) return res.status(400).json({ error: 'Сначала подключитесь к Discord' });
        await rpcSend('SET_ACTIVITY', { pid: process.pid, activity: null });
        currentActivity = null;
        broadcast({ type: 'activity_cleared' });
        res.json({ success: true, message: 'Активность очищена!' });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

app.post('/api/disconnect', (req, res) => {
    try {
        if (autoReconnectTimer) { clearTimeout(autoReconnectTimer); autoReconnectTimer = null; }
        if (rpcSocket) { rpcSocket.destroy(); rpcSocket = null; }
        rpcConnected = false; rpcReady = false; currentActivity = null;
        rpcCallbacks.forEach(cb => { clearTimeout(cb.timer); cb.reject(new Error('Отключено')); });
        rpcCallbacks.clear();
        broadcast({ type: 'disconnected' });
        res.json({ success: true, message: 'Отключено от Discord' });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

app.get('/api/status', (req, res) => {
    res.json({ connected: rpcConnected, activity: currentActivity });
});

// Profiles
app.get('/api/profiles', (req, res) => res.json(profiles));
app.put('/api/profiles/:name', (req, res) => {
    if (!/^[\w-]{1,64}$/.test(req.params.name)) return res.status(400).json({ error: 'Недопустимое имя профиля' });
    if (!req.body || typeof req.body !== 'object' || Array.isArray(req.body)) return res.status(400).json({ error: 'Профиль должен быть JSON-объектом' });
    profiles[req.params.name] = req.body;
    saveJson(PROFILES_FILE, profiles);
    res.json({ success: true });
});
app.delete('/api/profiles/:name', (req, res) => {
    if (!/^[\w-]{1,64}$/.test(req.params.name)) return res.status(400).json({ error: 'Недопустимое имя профиля' });
    delete profiles[req.params.name];
    saveJson(PROFILES_FILE, profiles);
    res.json({ success: true });
});

// History
app.get('/api/history', (req, res) => res.json(history));
app.delete('/api/history', (req, res) => {
    history = [];
    saveJson(HISTORY_FILE, history);
    res.json({ success: true });
});

// Custom presets
app.get('/api/custom-presets', (req, res) => res.json(customPresets));
app.put('/api/custom-presets', (req, res) => {
    customPresets = req.body;
    saveJson(CUSTOM_PRESETS_FILE, customPresets);
    res.json({ success: true });
});

// Settings
app.get('/api/settings', (req, res) => res.json(settings));
app.put('/api/settings', (req, res) => {
    settings = { ...settings, ...req.body };
    saveJson(SETTINGS_FILE, settings);
    if ('autoConnect' in req.body) {
        if (req.body.autoConnect && rpcConnected) scheduleReconnect();
        else if (!req.body.autoConnect && autoReconnectTimer) { clearTimeout(autoReconnectTimer); autoReconnectTimer = null; }
    }
    res.json({ success: true });
});

// Export/Import
app.get('/api/export', (req, res) => {
    res.json({ profiles, customPresets, history, settings, exportedAt: new Date().toISOString() });
});
app.post('/api/import', (req, res) => {
    try {
        const data = req.body;
        if (data.profiles) { profiles = data.profiles; saveJson(PROFILES_FILE, profiles); }
        if (data.customPresets) { customPresets = data.customPresets; saveJson(CUSTOM_PRESETS_FILE, customPresets); }
        if (data.history) { history = data.history; saveJson(HISTORY_FILE, history); }
        if (data.settings) { settings = { ...settings, ...data.settings }; saveJson(SETTINGS_FILE, settings); }
        res.json({ success: true, message: 'Настройки импортированы!' });
    } catch (err) { res.status(400).json({ error: 'Неверный формат файла' }); }
});

// Upload
app.post('/api/upload', upload.single('image'), (req, res) => {
    if (!req.file) return res.status(400).json({ error: 'Файл не загружен (jpg, png, gif, webp, макс. 8 МБ)' });
    res.json({ success: true, url: `/uploads/${req.file.filename}`, filename: req.file.filename });
});

app.use((err, req, res, next) => {
    if (err instanceof multer.MulterError) {
        if (err.code === 'LIMIT_FILE_SIZE') {
            return res.status(400).json({ error: 'Файл слишком большой (макс. 8 МБ)' });
        }
        return res.status(400).json({ error: `Ошибка загрузки: ${err.message}` });
    }
    if (err) {
        return res.status(500).json({ error: err.message });
    }
    next();
});
app.delete('/api/upload/:filename', (req, res) => {
    const fp = path.join(UPLOADS_DIR, path.basename(req.params.filename));
    if (fs.existsSync(fp)) { fs.unlinkSync(fp); res.json({ success: true }); }
    else res.status(404).json({ error: 'Файл не найден' });
});
app.get('/api/uploads', (req, res) => {
    const files = fs.readdirSync(UPLOADS_DIR).filter(f => /\.(jpe?g|png|gif|webp)$/i.test(f));
    res.json(files.map(f => ({ name: f, url: `/uploads/${f}` })));
});

wss.on('connection', (ws) => {
    ws.send(JSON.stringify({ type: 'status', connected: rpcConnected, activity: currentActivity, history }));
});

server.listen(PORT, '127.0.0.1', () => {
    console.log(`\n[Server] Discord RPC Manager запущен!`);
    console.log(`[Server] http://localhost:${PORT}\n`);
});
