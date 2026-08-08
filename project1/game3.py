import pygame
import math
import sys
import random
import struct

pygame.init()
pygame.mixer.init(22050, -16, 1, 512)

WIDTH, HEIGHT = 1024, 640
HALF_W = WIDTH // 2
HALF_H = HEIGHT // 2
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BLOOD CORRIDOR")
clock = pygame.time.Clock()

# --- TEXTURES ---
TEX_SIZE = 64

def _noise2d(x, y, seed=0):
    n = x + y * 57 + seed * 131
    n = (n << 13) ^ n
    return ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483647.0

def gen_texture(base_r, base_g, base_b, pattern="brick"):
    surf = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):
        for x in range(TEX_SIZE):
            r, g, b = base_r, base_g, base_b
            n1 = _noise2d(x, y, 0)
            n2 = _noise2d(x // 4, y // 4, 42)
            n3 = _noise2d(x // 8, y // 8, 99)

            if pattern == "brick":
                bx = x % 32
                by = y % 16
                row = y // 16
                offset = 16 if row % 2 else 0
                bx2 = (x + offset) % 32
                mortar = (by == 0 or bx2 == 0)
                if mortar:
                    r = int(r * 0.4 + 30)
                    g = int(g * 0.4 + 25)
                    b = int(b * 0.4 + 20)
                else:
                    variation = (n1 - 0.5) * 40
                    r = max(0, min(255, int(r + variation + n2 * 20 - 10)))
                    g = max(0, min(255, int(g + variation * 0.7 + n2 * 15 - 7)))
                    b = max(0, min(255, int(b + variation * 0.5 + n2 * 10 - 5)))
                    crack = abs(math.sin(x * 0.8 + y * 0.3 + n1 * 5) * math.cos(y * 0.6 - x * 0.2))
                    if crack > 0.97:
                        r, g, b = int(r * 0.6), int(g * 0.6), int(b * 0.6)
                    edge_dist = min(bx2, 32 - bx2, by, 16 - by)
                    if edge_dist < 2:
                        shade = 0.8 + 0.2 * (edge_dist / 2)
                        r, g, b = int(r * shade), int(g * shade), int(b * shade)

            elif pattern == "stone":
                base_var = n3 * 30 - 15
                r = max(0, min(255, int(r + base_var + (n1 - 0.5) * 25)))
                g = max(0, min(255, int(g + base_var + (n1 - 0.5) * 25)))
                b = max(0, min(255, int(b + base_var + (n1 - 0.5) * 25)))
                block_x = x % 32
                block_y = y % 16
                row = y // 16
                offset = 16 if row % 2 else 0
                bx2 = (x + offset) % 32
                if block_y == 0 or bx2 == 0:
                    r, g, b = int(r * 0.35), int(g * 0.35), int(b * 0.35)
                moss = max(0, n2 - 0.85) * 20
                if moss > 0 and y > TEX_SIZE // 2:
                    g = min(255, int(g + moss * 3))
                    r = max(0, int(r - moss))

            elif pattern == "metal":
                stripe_h = math.sin(y * 0.4) * 8
                stripe_v = math.sin(x * 0.3) * 5
                r = max(0, min(255, int(r + stripe_h + stripe_v + (n1 - 0.5) * 15)))
                g = max(0, min(255, int(g + stripe_h + stripe_v + (n1 - 0.5) * 15)))
                b = max(0, min(255, int(b + stripe_h + stripe_v + (n1 - 0.5) * 18)))
                if x % 16 < 1 or y % 16 < 1:
                    r, g, b = min(255, r + 30), min(255, g + 30), min(255, b + 35)
                rivet = ((x - 8) % 16 == 0 and (y - 8) % 16 == 0)
                if rivet:
                    r, g, b = min(255, r + 50), min(255, g + 50), min(255, b + 50)
                scratch = abs(math.sin(x * 2.1 + y * 0.7) * math.cos(x * 0.3 + y * 1.9))
                if scratch > 0.98:
                    r, g, b = min(255, r + 40), min(255, g + 40), min(255, b + 40)
                rust = max(0, n2 - 0.8) * 60
                if rust > 0:
                    r = min(255, int(r + rust))
                    g = max(0, int(g - rust * 0.3))

            elif pattern == "wood":
                grain = math.sin(y * 0.8 + x * 0.05 + n1 * 3) * 20
                ring = math.sin(math.sqrt((x - 32) ** 2 + (y - 32) ** 2) * 0.5) * 15
                r = max(0, min(255, int(r + grain + ring + (n1 - 0.5) * 12)))
                g = max(0, min(255, int(g + grain * 0.6 + ring * 0.5 + (n1 - 0.5) * 8)))
                b = max(0, min(255, int(b + (n1 - 0.5) * 6)))
                knot = math.sqrt((x - 48) ** 2 + (y - 20) ** 2)
                if knot < 5:
                    k = 1.0 - knot / 5
                    r = int(r * (1 - k * 0.4))
                    g = int(g * (1 - k * 0.5))
                plank = y % 32
                if plank < 1 or plank > 30:
                    r, g, b = int(r * 0.6), int(g * 0.6), int(b * 0.6)

            elif pattern == "tech":
                panel = (x // 16, y // 16)
                r, g, b = int(r + n1 * 10 - 5), int(g + n1 * 10 - 5), int(b + n1 * 12 - 6)
                if x % 16 < 1 or y % 16 < 1:
                    r, g, b = min(255, r + 50), min(255, g + 50), min(255, b + 60)
                cx, cy = 32, 32
                dist_center = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if 10 < dist_center < 18:
                    glow = int(40 + 20 * math.sin(_noise2d(x, y, 77) * 10))
                    g = min(255, g + glow)
                    r = min(255, r + glow // 2)
                if 22 < x < 42 and 22 < y < 42:
                    pulse = int(30 + 15 * math.sin(x * 0.3 + y * 0.2))
                    r, g, b = min(255, r + pulse), min(255, g + pulse + 40), min(255, b + pulse)
                screen_glitch = _noise2d(x, y, 123)
                if screen_glitch > 0.99:
                    r, g, b = min(255, r + 80), min(255, g + 120), min(255, b + 80)

            elif pattern == "hell":
                vein = abs(math.sin(x * 0.3 + y * 0.5 + n1 * 8) * math.cos(x * 0.7 - y * 0.4))
                base_var = (n1 - 0.5) * 40
                r = max(0, min(255, int(r + base_var + vein * 50)))
                g = max(0, min(255, int(g + base_var * 0.3 + vein * 20)))
                b = max(0, min(255, int(b + base_var * 0.2 + vein * 10)))
                ember = _noise2d(x * 3, y * 3, 200)
                if ember > 0.94:
                    glow = int((ember - 0.94) * 25 * 16)
                    r = min(255, r + glow)
                    g = min(255, g + glow // 3)
                crack = abs(math.sin(x * 0.5 + n2 * 10) * math.cos(y * 0.4 + n1 * 7))
                if crack > 0.95:
                    r = min(255, int(r + 60))
                    g = min(255, int(g + 15))
                drip = math.sin(x * 1.5) * 0.5 + 0.5
                if y > TEX_SIZE * drip and n3 > 0.6:
                    r = min(255, int(r + 30))

            surf.set_at((x, y), (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))

    return surf

textures = {
    1: gen_texture(100, 35, 35, "brick"),
    2: gen_texture(35, 90, 35, "stone"),
    3: gen_texture(35, 35, 100, "metal"),
    4: gen_texture(100, 85, 35, "wood"),
    5: gen_texture(55, 55, 70, "tech"),
    6: gen_texture(90, 25, 20, "hell"),
    7: gen_texture(25, 25, 30, "stone"),
    8: gen_texture(110, 90, 50, "wood"),
}

# --- SKYBOX ---
sky_surf = pygame.Surface((WIDTH, HALF_H))
for y in range(HALF_H):
    t = y / HALF_H
    r = int(35 + t * 40)
    g = int(15 + t * 20)
    b = int(15 + t * 15)
    pygame.draw.line(sky_surf, (r, g, b), (0, y), (WIDTH, y))
for _ in range(30):
    sx = random.randint(0, WIDTH - 1)
    sy = random.randint(0, HALF_H // 3)
    brightness = random.randint(40, 80)
    pygame.draw.circle(sky_surf, (brightness, brightness, brightness + 10), (sx, sy), random.choice([1, 1, 2]))
mountain_pts = []
mx = 0
while mx <= WIDTH:
    mh = random.randint(HALF_H // 6, HALF_H // 2)
    mw = random.randint(40, 120)
    peak_x = mx + mw // 2
    mountain_pts.append((mx, HALF_H))
    mountain_pts.append((peak_x - mw // 4, HALF_H - mh + random.randint(-10, 10)))
    mountain_pts.append((peak_x, HALF_H - mh + random.randint(-5, 15)))
    mountain_pts.append((peak_x + mw // 4, HALF_H - mh + random.randint(-10, 10)))
    mx += mw
mountain_pts.append((WIDTH, HALF_H))
dark_color = (20, 15, 15)
if len(mountain_pts) >= 3:
    pygame.draw.polygon(sky_surf, dark_color, mountain_pts)
for _ in range(25):
    sx = random.randint(0, WIDTH - 1)
    sy = random.randint(HALF_H // 4, HALF_H - 10)
    brightness = random.randint(30, 60)
    pygame.draw.circle(sky_surf, (brightness, brightness, brightness), (sx, sy), 1)

# --- SOUNDS ---
def make_beep(freq, dur, vol=0.1, wave="sine"):
    sr = 22050
    n = int(sr * dur)
    buf = bytearray()
    for i in range(n):
        t = i / sr
        env = max(0, 1.0 - t / dur)
        if wave == "sine":
            s = vol * env * math.sin(2 * math.pi * freq * t)
        elif wave == "square":
            s = vol * env * (1 if math.sin(2 * math.pi * freq * t) > 0 else -1)
        elif wave == "noise":
            s = vol * env * random.uniform(-1, 1)
        else:
            s = vol * env * math.sin(2 * math.pi * freq * t)
        buf.extend(struct.pack('<h', max(-32767, min(32767, int(s * 32767)))))
    try:
        return pygame.mixer.Sound(buffer=bytes(buf))
    except:
        return None

snd_pistol = make_beep(300, 0.08, 0.15, "square")
snd_shotgun = make_beep(150, 0.12, 0.2, "noise")
snd_machinegun = make_beep(400, 0.04, 0.12, "square")
snd_railgun = make_beep(800, 0.3, 0.15, "sine")
snd_hit = make_beep(100, 0.1, 0.12, "noise")
snd_kill = make_beep(500, 0.15, 0.12, "sine")
snd_levelup = make_beep(600, 0.3, 0.15, "sine")
snd_menu = make_beep(440, 0.1, 0.1, "sine")
snd_hurt = make_beep(80, 0.15, 0.15, "noise")
snd_empty = make_beep(200, 0.05, 0.08, "square")
snd_pickup = make_beep(800, 0.15, 0.12, "sine")

# --- WEAPONS ---
WEAPONS = {
    "pistol": {"name": "PISTOL", "damage": 1, "cooldown": 300, "spread": 0, "bullets": 1, "ammo_use": 1, "speed": 0.4, "range": 40, "color": (255, 255, 100)},
    "shotgun": {"name": "SHOTGUN", "damage": 1, "cooldown": 700, "spread": 0.15, "bullets": 5, "ammo_use": 2, "speed": 0.35, "range": 15, "color": (255, 180, 50)},
    "machinegun": {"name": "M.GUN", "damage": 1, "cooldown": 100, "spread": 0.08, "bullets": 1, "ammo_use": 1, "speed": 0.5, "range": 30, "color": (255, 255, 50)},
    "railgun": {"name": "RAIL", "damage": 3, "cooldown": 1200, "spread": 0, "bullets": 1, "ammo_use": 3, "speed": 0.8, "range": 60, "color": (100, 200, 255)},
}
WEAPON_LIST = ["pistol", "shotgun", "machinegun", "railgun"]

# --- LEVELS ---
LEVELS = [
    {
        "name": "THE AWAKENING",
        "desc": "Jump the gap, find the ruby...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,1,
            1,0,0,0,0,0,7,7,7,0,0,0,0,0,0,0,0,8,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,7,1,1,0,0,0,0,0,0,7,7,7,7,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,8,0,1,
            1,0,0,0,0,0,0,7,7,7,0,0,0,0,0,0,8,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (17, 2),
        "enemies": [("zombie", 10, 10)],
        "ammo": [(5, 5, 10)],
        "health": [(10, 5)],
        "floor": (30, 30, 35),
        "ceil": (15, 15, 22),
    },
    {
        "name": "BLOODY CORRIDORS",
        "desc": "Gaps and crates...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,8,8,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,7,7,7,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,1,
            1,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,1,
            1,7,7,7,0,0,0,0,8,0,0,0,0,0,7,7,7,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,7,7,7,0,0,0,0,0,0,8,8,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,7,7,1,
            1,0,0,0,0,0,0,0,0,8,8,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,8,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (18, 18),
        "enemies": [("zombie", 9, 9), ("zombie", 5, 14)],
        "ammo": [(5, 5, 10), (14, 14, 10)],
        "health": [(10, 10)],
        "floor": (40, 25, 25),
        "ceil": (20, 12, 12),
    },
    {
        "name": "THE PIT",
        "desc": "Jump or fall...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,7,7,7,7,7,7,7,7,7,7,7,7,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,7,7,7,0,0,0,0,0,7,7,7,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,7,7,7,0,0,0,0,0,7,7,7,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,7,7,7,7,7,7,7,7,7,7,7,7,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (18, 18),
        "enemies": [("zombie", 9, 9), ("skeleton", 5, 14)],
        "ammo": [(2, 10, 8), (17, 10, 8)],
        "health": [(9, 2), (9, 17)],
        "floor": (25, 22, 35),
        "ceil": (12, 10, 20),
    },
    {
        "name": "FROZEN HALLS",
        "desc": "Ice and gaps...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,8,0,0,0,0,0,0,0,0,0,0,8,0,0,0,1,
            1,0,0,0,8,0,0,0,0,0,0,0,0,0,0,8,0,0,0,1,
            1,0,0,0,0,0,0,0,7,7,7,7,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,7,0,0,0,0,0,0,7,0,0,0,0,0,1,
            1,0,8,8,0,0,7,0,0,0,0,0,0,7,0,0,8,8,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,8,8,0,0,7,0,0,0,0,0,0,7,0,0,8,8,0,1,
            1,0,0,0,0,0,7,0,0,0,0,0,0,7,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,8,0,0,0,0,7,7,7,7,0,0,0,8,0,0,1,
            1,0,0,0,8,0,0,0,0,0,0,0,0,0,0,0,8,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (18, 18),
        "enemies": [("skeleton", 9, 2), ("skeleton", 9, 17), ("skeleton", 5, 9)],
        "ammo": [(1, 4, 10), (18, 4, 10)],
        "health": [(10, 1), (1, 10)],
        "floor": (30, 35, 50),
        "ceil": (15, 18, 30),
    },
    {
        "name": "INFERNOS BREACH",
        "desc": "Lava and danger...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,7,7,7,0,0,0,0,0,0,7,7,7,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,8,8,8,8,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,1,
            1,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,1,
            1,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,8,8,8,8,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,7,7,7,0,0,0,0,0,0,7,7,7,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (9, 9),
        "enemies": [("demon", 5, 5), ("demon", 14, 14)],
        "ammo": [(10, 10, 10)],
        "health": [(10, 10)],
        "floor": (50, 22, 18),
        "ceil": (25, 10, 10),
    },
    {
        "name": "STEEL LABS",
        "desc": "Crates and corridors...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,8,0,0,0,7,7,0,0,0,0,7,7,0,0,0,8,0,1,
            1,0,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,1,
            1,0,0,0,0,0,0,0,0,8,8,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,7,7,0,0,0,0,0,8,0,0,8,0,0,0,0,0,7,7,1,
            1,0,0,0,0,0,0,0,8,0,0,8,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,8,0,0,8,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,8,0,0,8,0,0,0,0,0,0,0,1,
            1,7,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,7,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,8,8,0,0,0,0,0,0,0,0,1,
            1,0,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,1,
            1,0,8,0,0,0,7,7,0,0,0,0,7,7,0,0,0,8,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (9, 9),
        "enemies": [("skeleton", 4, 4), ("skeleton", 15, 15), ("zombie", 9, 2)],
        "ammo": [(8, 1, 15), (1, 18, 15)],
        "health": [(9, 1), (18, 10)],
        "floor": (30, 35, 40),
        "ceil": (15, 18, 22),
    },
    {
        "name": "CATACOMBS",
        "desc": "The maze of death...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,1,0,0,0,7,7,7,7,0,0,0,1,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,8,0,0,0,0,0,0,8,0,0,0,0,0,1,
            1,1,0,0,0,0,8,0,0,0,0,0,0,8,0,0,0,0,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,8,8,0,0,0,0,0,0,0,0,1,
            1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
            1,0,0,0,0,0,0,0,0,8,8,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,0,0,0,0,8,0,0,0,0,0,0,8,0,0,0,0,1,1,
            1,0,0,0,0,0,8,0,0,0,0,0,0,8,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,1,0,0,0,7,7,7,7,0,0,0,1,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (9, 9),
        "enemies": [("skeleton", 5, 5), ("skeleton", 14, 14), ("skeleton", 3, 10)],
        "ammo": [(3, 3, 10), (16, 16, 10)],
        "health": [(10, 5), (5, 10)],
        "floor": (38, 35, 30),
        "ceil": (18, 16, 15),
    },
    {
        "name": "WAR ZONE",
        "desc": "Jump and fight...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,7,0,0,0,0,0,0,7,0,0,0,0,0,1,
            1,0,0,0,0,0,7,0,0,0,0,0,0,7,0,0,0,0,0,1,
            1,0,0,0,8,8,0,0,0,0,0,0,0,0,8,8,0,0,0,1,
            1,0,0,0,0,0,0,0,0,8,8,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,1,
            1,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,1,
            1,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,1,
            1,0,0,0,0,0,0,0,0,8,8,0,0,0,0,0,0,0,0,1,
            1,0,0,0,8,8,0,0,0,0,0,0,0,0,8,8,0,0,0,1,
            1,0,0,0,0,0,7,0,0,0,0,0,0,7,0,0,0,0,0,1,
            1,0,0,0,0,0,7,0,0,0,0,0,0,7,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (9, 9),
        "enemies": [("zombie", 3, 3), ("zombie", 16, 16), ("demon", 9, 2)],
        "ammo": [(5, 5, 15), (14, 5, 15)],
        "health": [(10, 10), (2, 2)],
        "floor": (38, 30, 25),
        "ceil": (18, 14, 12),
    },
    {
        "name": "GATES OF HELL",
        "desc": "Precision jumps...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,7,0,0,0,0,0,0,0,0,7,0,0,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,8,0,0,0,0,7,7,0,0,0,0,8,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,0,0,8,0,0,0,0,8,0,0,0,0,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,8,0,0,8,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,8,0,0,8,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,0,0,8,0,0,0,0,8,0,0,0,0,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,8,0,0,0,0,7,7,0,0,0,0,8,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,7,0,0,0,0,0,0,0,0,7,0,0,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (9, 9),
        "enemies": [("demon", 9, 2), ("demon", 2, 9), ("demon", 17, 9)],
        "ammo": [(5, 1, 20), (1, 5, 20)],
        "health": [(10, 10), (3, 3)],
        "floor": (55, 18, 15),
        "ceil": (28, 8, 8),
    },
    {
        "name": "THE FINAL STAND",
        "desc": "Parkour mastery...",
        "walls": [
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,7,0,0,0,7,7,0,0,7,7,0,0,0,7,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,8,0,0,0,0,8,8,0,0,0,0,8,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,0,7,0,0,0,0,0,0,7,0,0,0,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,8,0,0,8,0,0,8,0,0,8,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,8,0,0,8,0,0,8,0,0,8,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,0,0,0,7,0,0,0,0,0,0,7,0,0,0,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,8,0,0,0,0,8,8,0,0,0,0,8,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,7,7,0,0,0,7,7,0,0,7,7,0,0,0,7,7,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        ],
        "player": (1.5, 1.5, 0),
        "ruby": (9, 9),
        "enemies": [("demon", 9, 2), ("demon", 2, 9), ("demon", 17, 9), ("demon", 9, 17)],
        "ammo": [(5, 5, 20), (14, 5, 20), (5, 14, 20)],
        "health": [(10, 10), (3, 3), (16, 16)],
        "floor": (60, 15, 12),
        "ceil": (30, 6, 6),
    },
]

MAP_W = 20
MAP_H = 20
MAX_DEPTH = 24

# --- GAME STATE ---
class GameState:
    def __init__(self):
        self.state = "menu"
        self.level = 0
        self.kills = 0
        self.total_kills = 0
        self.player_x = 2.5
        self.player_y = 2.5
        self.player_angle = 0
        self.player_z = 0.0
        self.vel_z = 0.0
        self.on_ground = True
        self.player_health = 100
        self.player_ammo = 50
        self.shield = 0
        self.weapon = "pistol"
        self.weapon_idx = 0
        self.weapons_owned = ["pistol"]
        self.last_shot_time = 0
        self.enemies = []
        self.bullets = []
        self.pickups = []
        self.damage_flash = 0
        self.level_complete_timer = 0
        self.menu_selection = 0
        self.transition_alpha = 0
        self.transition_dir = 0
        self.weapon_switch_time = 0
        self.score = 0
        self.time_played = 0
        self.particles = []
        self.depth_buffer = []
        self.ruby_x = 0
        self.ruby_y = 0
        self.ruby_found = False
        self.sprinting = False
        self.step_timer = 0

gs = GameState()

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH
DELTA_ANGLE = FOV / NUM_RAYS
PROJ_DIST = HALF_W / math.tan(HALF_FOV)
MOVE_SPEED = 0.045
SPRINT_MULT = 1.8
ROT_SPEED = 0.003
JUMP_VEL = 0.12
GRAVITY = 0.006
WALL_HEIGHTS = {7: 0.35, 8: 0.55}
JUMP_CLEAR = {7: 0.25, 8: 0.45}

# --- HELPERS ---
def get_map(mx, my):
    level = LEVELS[gs.level]
    ix, iy = int(mx), int(my)
    if 0 <= ix < MAP_W and 0 <= iy < MAP_H:
        return level["walls"][iy * MAP_W + ix]
    return 1

def has_line_of_sight(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 0.01:
        return True
    steps = int(dist * 4) + 1
    for i in range(steps + 1):
        t = i / steps
        if get_map(x1 + dx * t, y1 + dy * t) > 0:
            return False
    return True

def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return (int(c1[0] + (c2[0] - c1[0]) * t), int(c1[1] + (c2[1] - c1[1]) * t), int(c1[2] + (c2[2] - c1[2]) * t))

# --- INIT LEVEL ---
def init_level():
    level = LEVELS[gs.level]
    gs.player_x, gs.player_y, pa = level["player"]
    gs.player_angle = pa
    gs.player_z = 0.0
    gs.vel_z = 0.0
    gs.on_ground = True
    gs.player_health = 100
    gs.kills = 0
    gs.bullets = []
    gs.particles = []
    gs.damage_flash = 0
    gs.level_complete_timer = 0
    gs.enemies = []
    gs.pickups = []
    gs.time_played = 0
    gs.depth_buffer = [MAX_DEPTH] * WIDTH
    gs.ruby_x = level["ruby"][0] + 0.5
    gs.ruby_y = level["ruby"][1] + 0.5
    gs.ruby_found = False
    gs.sprinting = False

    ENEMY_HP = {"zombie": 3, "skeleton": 3, "demon": 6}
    ENEMY_SPEED = {"zombie": 0.015, "skeleton": 0.02, "demon": 0.012}

    for etype, ex, ey in level["enemies"]:
        hp = ENEMY_HP.get(etype, 3)
        gs.enemies.append({
            "x": ex + 0.5, "y": ey + 0.5, "hp": hp, "max_hp": hp,
            "alive": True, "type": etype,
            "speed": ENEMY_SPEED.get(etype, 0.015),
            "last_hit": 0, "anim": 0, "alert": False,
            "attack_anim": 0, "attack_dir": 0,
        })

    for ax, ay, amount in level.get("ammo", []):
        gs.pickups.append({"x": ax + 0.5, "y": ay + 0.5, "type": "ammo", "amount": amount, "alive": True})

    for hx, hy in level.get("health", []):
        gs.pickups.append({"x": hx + 0.5, "y": hy + 0.5, "type": "health", "amount": 25, "alive": True})

# --- PARTICLES ---
def spawn_particles(x, y, color, count=5, speed=0.02, life=30, size=3):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(speed * 0.5, speed)
        gs.particles.append({
            "x": x, "y": y,
            "dx": math.cos(angle) * spd,
            "dy": math.sin(angle) * spd,
            "life": random.randint(life // 2, life),
            "max_life": life,
            "color": color,
            "size": random.randint(max(1, size // 2), size),
        })

def spawn_blood(x, y):
    spawn_particles(x, y, (200, 0, 0), count=8, speed=0.03, life=20, size=3)
    spawn_particles(x, y, (150, 0, 0), count=4, speed=0.015, life=15, size=2)

def spawn_spark(x, y, color=(255, 200, 50)):
    spawn_particles(x, y, color, count=4, speed=0.02, life=12, size=2)

def spawn_death(x, y, etype):
    colors = {"zombie": (80, 160, 60), "skeleton": (200, 200, 180), "demon": (180, 40, 40)}
    c = colors.get(etype, (150, 150, 150))
    spawn_particles(x, y, c, count=15, speed=0.04, life=30, size=4)
    spawn_particles(x, y, (255, 255, 100), count=5, speed=0.05, life=15, size=2)

def spawn_wall_hit(x, y):
    spawn_particles(x, y, (200, 180, 140), count=3, speed=0.02, life=10, size=2)

def update_particles():
    for p in gs.particles[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["dx"] *= 0.95
        p["dy"] *= 0.95
        p["life"] -= 1
        if p["life"] <= 0:
            gs.particles.remove(p)

def draw_particles():
    for p in gs.particles:
        dx = p["x"] - gs.player_x
        dy = p["y"] - gs.player_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.1 or dist > MAX_DEPTH:
            continue

        angle_to = math.atan2(dy, dx)
        angle_diff = angle_to - gs.player_angle
        while angle_diff > math.pi: angle_diff -= 2 * math.pi
        while angle_diff < -math.pi: angle_diff += 2 * math.pi

        if abs(angle_diff) > HALF_FOV + 0.3:
            continue

        sx = int(HALF_W + angle_diff / HALF_FOV * HALF_W)
        proj_h = max(int(PROJ_DIST / dist), 1)
        sy = HALF_H

        t = p["life"] / p["max_life"]
        alpha = max(0, min(255, int(t * 255)))
        c = p["color"]
        shade = max(0.3, t)
        color = (int(c[0] * shade), int(c[1] * shade), int(c[2] * shade))
        sz = max(1, int(p["size"] * t * proj_h / 64))
        sz = min(sz, 15)

        if sz > 0:
            pygame.draw.circle(screen, color, (sx, sy), sz)

# --- RAYCASTING ---
def ray_cast():
    walls = []
    for ray in range(NUM_RAYS):
        ray_angle = gs.player_angle - HALF_FOV + ray * DELTA_ANGLE
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        map_x = int(gs.player_x)
        map_y = int(gs.player_y)

        delta_dist_x = abs(1 / cos_a) if cos_a != 0 else 1e30
        delta_dist_y = abs(1 / sin_a) if sin_a != 0 else 1e30

        if cos_a < 0:
            step_x = -1
            side_dist_x = (gs.player_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - gs.player_x) * delta_dist_x

        if sin_a < 0:
            step_y = -1
            side_dist_y = (gs.player_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - gs.player_y) * delta_dist_y

        hit = False
        side = 0
        depth = 0
        tile = 1

        for _ in range(MAX_DEPTH * 2):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            tile = get_map(map_x, map_y)
            if tile > 0:
                hit = True
                break

        if hit:
            if side == 0:
                depth = side_dist_x - delta_dist_x
            else:
                depth = side_dist_y - delta_dist_y

            corrected = depth * math.cos(gs.player_angle - ray_angle)
            corrected = max(corrected, 0.01)

            gs.depth_buffer[ray] = corrected

            texture_x = 0
            if side == 0:
                wall_hit_y = gs.player_y + depth * sin_a
                texture_x = wall_hit_y - int(wall_hit_y)
            else:
                wall_hit_x = gs.player_x + depth * cos_a
                texture_x = wall_hit_x - int(wall_hit_x)

            walls.append((ray, corrected, tile, side, texture_x))

    return walls

# --- DRAWING ---
def draw_textured_walls(walls):
    level = LEVELS[gs.level]
    floor_c = level["floor"]
    ceil_c = level["ceil"]

    sky_offset = int(gs.player_angle * 100) % WIDTH
    screen.blit(sky_surf, (-sky_offset, 0))
    screen.blit(sky_surf, (-sky_offset + WIDTH, 0))

    for y in range(HALF_H, HEIGHT - BAR_H, 2):
        row = y - HALF_H
        if row == 0:
            row = 1
        shade_f = max(0.08, 1.0 - (row / (HALF_H - BAR_H / 2)) ** 1.8)
        dist_f = row / (HALF_H - BAR_H / 2)
        r_c = int(floor_c[0] * shade_f * (1.0 - dist_f * 0.5))
        g_c = int(floor_c[1] * shade_f * (1.0 - dist_f * 0.5))
        b_c = int(floor_c[2] * shade_f * (1.0 - dist_f * 0.5))
        c = (max(0, min(255, r_c)), max(0, min(255, g_c)), max(0, min(255, b_c)))
        pygame.draw.line(screen, c, (0, y), (WIDTH, y))

    for y in range(0, HALF_H, 2):
        row = HALF_H - y
        if row == 0:
            row = 1
        shade_c = max(0.04, (1.0 - row / HALF_H) ** 1.8) * 0.35
        c = (int(ceil_c[0] * shade_c), int(ceil_c[1] * shade_c), int(ceil_c[2] * shade_c))
        pygame.draw.line(screen, c, (0, y), (WIDTH, y))

    for ray, depth, tile, side, tex_x in walls:
        depth = max(depth, 0.1)

        wall_h_factor = WALL_HEIGHTS.get(tile, 1.0)
        proj_h = PROJ_DIST / depth * wall_h_factor
        if proj_h > HEIGHT * 3:
            proj_h = HEIGHT * 3
        wall_top = HALF_H - proj_h / 2 - gs.player_z * 60

        tex = textures.get(tile, textures[1])

        tex_x_int = int(tex_x * TEX_SIZE) % TEX_SIZE

        shade = max(0.08, 0.9 - depth / MAX_DEPTH * 0.85)
        if side == 1:
            shade *= 0.55

        try:
            tex_col = tex.get_at((tex_x_int, 0))
            r = int(tex_col[0] * shade)
            g = int(tex_col[1] * shade)
            b = int(tex_col[2] * shade)
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        except:
            color = (int(100 * shade), int(100 * shade), int(100 * shade))

        draw_h = int(proj_h)
        if draw_h > 0 and ray >= 0 and ray < WIDTH:
            pygame.draw.rect(screen, color, (ray, int(wall_top), 1, draw_h))

            if draw_h > 30:
                stripe = int((ray * 0.4 + wall_top * 0.2) % 8)
                if stripe == 0:
                    darker = (max(0, color[0] - 15), max(0, color[1] - 15), max(0, color[2] - 15))
                    pygame.draw.rect(screen, darker, (ray, int(wall_top), 1, draw_h))
                elif stripe == 4:
                    lighter = (min(255, color[0] + 8), min(255, color[1] + 8), min(255, color[2] + 8))
                    pygame.draw.rect(screen, lighter, (ray, int(wall_top), 1, draw_h))

    vig = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(40):
        alpha = int((40 - i) * 3)
        pygame.draw.rect(vig, (0, 0, 0, alpha), (i, i, WIDTH - i * 2, HEIGHT - i * 2), 1)
    screen.blit(vig, (0, 0))

def draw_enemies():
    for e in gs.enemies:
        if not e["alive"]:
            continue

        dx = e["x"] - gs.player_x
        dy = e["y"] - gs.player_y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.3:
            continue

        if not has_line_of_sight(gs.player_x, gs.player_y, e["x"], e["y"]):
            continue

        angle_to = math.atan2(dy, dx)
        angle_diff = angle_to - gs.player_angle

        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        if abs(angle_diff) > HALF_FOV + 0.2:
            continue

        screen_x = int(HALF_W + angle_diff / HALF_FOV * HALF_W)
        sprite_h = min(int(PROJ_DIST / dist), HEIGHT)
        sprite_w = sprite_h // 2

        if screen_x >= 0 and screen_x < WIDTH and dist > gs.depth_buffer[screen_x]:
            continue

        shade = max(0.2, 1.0 - dist / MAX_DEPTH)

        cx = screen_x
        cy = HALF_H

        atk = e.get("attack_anim", 0)
        anim = e["anim"]

        if e["type"] == "zombie":
            draw_zombie_sprite(cx, cy, sprite_w, sprite_h, shade, anim, atk, dist)
        elif e["type"] == "skeleton":
            draw_skeleton_sprite(cx, cy, sprite_w, sprite_h, shade, anim, atk, dist)
        else:
            draw_demon_sprite(cx, cy, sprite_w, sprite_h, shade, anim, atk, dist)

        max_hp = e.get("max_hp", 3)
        if e["hp"] < max_hp:
            bar_w = max(sprite_w, 20)
            bar_h = 4
            bar_x = cx - bar_w // 2
            bar_y = cy - sprite_h // 2 - 12
            pygame.draw.rect(screen, (40, 0, 0), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
            pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            hp_w = int(bar_w * e["hp"] / max_hp)
            hp_c = (0, 200, 0) if e["hp"] > max_hp // 2 else (200, 200, 0) if e["hp"] > 1 else (200, 0, 0)
            pygame.draw.rect(screen, hp_c, (bar_x, bar_y, hp_w, bar_h))

        if dist < 3:
            warning = max(0, int(255 * (1 - dist / 3)))
            if warning > 50:
                pygame.draw.circle(screen, (255, 0, 0), (cx, cy), sprite_w // 2 + 5, 2)

def draw_zombie_sprite(cx, cy, sw, sh, shade, anim, atk, dist):
    bw = max(sw // 3, 6)
    bh = int(sh * 0.5)
    leg_w = max(sw // 7, 3)
    leg_h = int(sh * 0.35)
    arm_w = max(sw // 8, 3)
    arm_h = int(sh * 0.4)
    head_r = max(sw // 4, 4)

    skin = (int(90 * shade), int(140 * shade), int(70 * shade))
    dark = (int(60 * shade), int(100 * shade), int(50 * shade))

    if atk > 0:
        t = atk / 15.0
        lunge = int(math.sin(t * math.pi) * sw * 0.3)
        lo = 0
        af = int(t * sw * 0.5)
        au = int(t * sh * 0.15)
    else:
        lunge = 0; af = 0; au = 0
        lo = int(math.sin(anim * 0.15) * sw * 0.08)

    base_y = cy + bh // 2
    pygame.draw.rect(screen, dark, (cx - leg_w - lo, base_y, leg_w, leg_h))
    pygame.draw.rect(screen, dark, (cx + lo, base_y, leg_w, leg_h))

    pygame.draw.rect(screen, skin, (cx - arm_w * 2 - af - lunge, cy - arm_h // 3 - au, arm_w, arm_h))
    pygame.draw.rect(screen, skin, (cx + bw // 2 + af + lunge, cy - arm_h // 3 - au, arm_w, arm_h))

    if atk > 0:
        cl = max(arm_w, 3)
        pygame.draw.polygon(screen, dark, [
            (cx - arm_w * 2 - af - lunge, cy - arm_h // 3 - au),
            (cx - arm_w * 2 - af - lunge - cl, cy - arm_h // 3 - au + cl),
            (cx - arm_w * 2 - af - lunge + cl, cy - arm_h // 3 - au + cl),
        ])

    pygame.draw.rect(screen, skin, (cx - bw // 2, cy - bh // 2, bw, bh))
    pygame.draw.circle(screen, skin, (cx, cy - bh // 2 - head_r), head_r)
    pygame.draw.circle(screen, dark, (cx, cy - bh // 2 - head_r), head_r - 1)

    er = max(head_r // 4, 2)
    ey = cy - bh // 2 - head_r - 1
    pygame.draw.circle(screen, (255, int(200 * shade), 0), (cx - er * 2, ey), er)
    pygame.draw.circle(screen, (255, int(200 * shade), 0), (cx + er * 2, ey), er)
    pygame.draw.circle(screen, (int(40 * shade), int(20 * shade), 0), (cx - er * 2, ey), max(er // 2, 1))
    pygame.draw.circle(screen, (int(40 * shade), int(20 * shade), 0), (cx + er * 2, ey), max(er // 2, 1))

    if atk > 0:
        mw = max(head_r, 3)
        mh = max(head_r // 3, 2)
        my = cy - bh // 2 - head_r + head_r // 2
        pygame.draw.ellipse(screen, (int(100 * shade), int(10 * shade), int(10 * shade)), (cx - mw // 2, my, mw, mh))
    else:
        mw = max(head_r // 2, 2)
        mh = max(head_r // 4, 1)
        my = cy - bh // 2 - head_r + head_r // 2
        pygame.draw.rect(screen, (int(120 * shade), int(30 * shade), int(30 * shade)), (cx - mw // 2, my, mw, mh))

def draw_skeleton_sprite(cx, cy, sw, sh, shade, anim, atk, dist):
    bw = max(sw // 4, 5)
    bh = int(sh * 0.5)
    leg_w = max(sw // 10, 2)
    leg_h = int(sh * 0.4)
    head_r = max(sw // 4, 4)

    bone = (int(220 * shade), int(210 * shade), int(190 * shade))
    dark = (int(160 * shade), int(150 * shade), int(130 * shade))

    if atk > 0:
        t = atk / 15.0
        lunge = int(math.sin(t * math.pi) * sw * 0.3)
        lo = 0
        af = int(t * sw * 0.7)
        au = int(t * sh * 0.1)
    else:
        lunge = 0; af = 0; au = 0
        lo = int(math.sin(anim * 0.18) * sw * 0.1)

    base_y = cy + bh // 2
    pygame.draw.rect(screen, dark, (cx - leg_w * 2 - lo, base_y, leg_w, leg_h))
    pygame.draw.rect(screen, dark, (cx + lo, base_y, leg_w, leg_h))
    pygame.draw.line(screen, bone, (cx, base_y), (cx - leg_w - lo, base_y + leg_h), 2)
    pygame.draw.line(screen, bone, (cx, base_y), (cx + lo, base_y + leg_h), 2)

    arm_len = int(sh * 0.45)
    if atk > 0:
        pygame.draw.line(screen, bone, (cx - bw, cy - bh // 4), (cx - bw - af - lunge, cy - bh // 4 - au), 3)
        pygame.draw.line(screen, bone, (cx + bw, cy - bh // 4), (cx + bw + af + lunge, cy - bh // 4 - au), 3)
        bl = max(sw // 4, 4)
        pygame.draw.line(screen, (200, 200, 220), (cx - bw - af - lunge, cy - bh // 4 - au), (cx - bw - af - lunge - bl, cy - bh // 4 - au - bl), 3)
        pygame.draw.line(screen, (200, 200, 220), (cx + bw + af + lunge, cy - bh // 4 - au), (cx + bw + af + lunge + bl, cy - bh // 4 - au - bl), 3)
    else:
        ao = int(math.sin(anim * 0.18 + math.pi) * sw * 0.12)
        pygame.draw.line(screen, bone, (cx - bw, cy - bh // 4), (cx - bw - arm_len // 2 + ao, cy + ao), 3)
        pygame.draw.line(screen, bone, (cx + bw, cy - bh // 4), (cx + bw + arm_len // 2 - ao, cy - ao), 3)

    pygame.draw.rect(screen, bone, (cx - bw // 2, cy - bh // 2, bw, bh))
    for i in range(3):
        ry = cy - bh // 4 + i * (bh // 4)
        pygame.draw.line(screen, dark, (cx - bw // 2 + 2, ry), (cx + bw // 2 - 2, ry), 1)

    pygame.draw.circle(screen, bone, (cx, cy - bh // 2 - head_r), head_r)
    pygame.draw.circle(screen, dark, (cx, cy - bh // 2 - head_r), head_r - 2)

    er = max(head_r // 3, 2)
    ey = cy - bh // 2 - head_r - 2
    if atk > 0:
        pygame.draw.circle(screen, (255, 50, 0), (cx - er * 2, ey), er)
        pygame.draw.circle(screen, (255, 50, 0), (cx + er * 2, ey), er)
    else:
        pygame.draw.circle(screen, (0, 0, 0), (cx - er * 2, ey), er)
        pygame.draw.circle(screen, (0, 0, 0), (cx + er * 2, ey), er)
        pygame.draw.circle(screen, (200, 0, 0), (cx - er * 2, ey), max(er - 1, 1))
        pygame.draw.circle(screen, (200, 0, 0), (cx + er * 2, ey), max(er - 1, 1))

def draw_demon_sprite(cx, cy, sw, sh, shade, anim, atk, dist):
    bw = max(sw // 2, 8)
    bh = int(sh * 0.55)
    leg_w = max(sw // 6, 4)
    leg_h = int(sh * 0.35)
    head_r = max(sw // 3, 5)

    skin = (int(180 * shade), int(50 * shade), int(50 * shade))
    dark = (int(130 * shade), int(30 * shade), int(30 * shade))

    if atk > 0:
        t = atk / 15.0
        lunge = int(math.sin(t * math.pi) * sw * 0.25)
        lo = 0
        af = int(t * sw * 0.5)
        au = int(t * sh * 0.1)
    else:
        lunge = 0; af = 0; au = 0
        lo = int(math.sin(anim * 0.12) * sw * 0.06)

    base_y = cy + bh // 2
    pygame.draw.rect(screen, dark, (cx - leg_w * 2 - lo, base_y, leg_w, leg_h))
    pygame.draw.rect(screen, dark, (cx + lo, base_y, leg_w, leg_h))

    arm_w = max(sw // 5, 3)
    arm_h = int(sh * 0.5)
    if atk > 0:
        pygame.draw.rect(screen, skin, (cx - bw // 2 - arm_w - af - lunge, cy - arm_h // 3 - au, arm_w, arm_h))
        pygame.draw.rect(screen, skin, (cx + bw // 2 + af + lunge, cy - arm_h // 3 - au, arm_w, arm_h))
        cl = max(arm_w * 2, 6)
        pygame.draw.polygon(screen, dark, [
            (cx - bw // 2 - arm_w - af - lunge, cy - arm_h // 3 - au + arm_h),
            (cx - bw // 2 - arm_w - af - lunge + cl, cy - arm_h // 3 - au + arm_h),
            (cx - bw // 2 - arm_w - af - lunge - cl // 2, cy - arm_h // 3 - au + arm_h + cl),
        ])
    else:
        ao = int(math.sin(anim * 0.12 + math.pi) * sw * 0.08)
        pygame.draw.rect(screen, skin, (cx - bw // 2 - arm_w - ao, cy - arm_h // 3, arm_w, arm_h))
        pygame.draw.rect(screen, skin, (cx + bw // 2 + ao, cy - arm_h // 3, arm_w, arm_h))

    pygame.draw.rect(screen, skin, (cx - bw // 2, cy - bh // 2, bw, bh))

    horn = max(head_r // 2, 3)
    pygame.draw.polygon(screen, dark, [(cx - head_r + 2, cy - bh // 2 - head_r + 2), (cx - head_r - horn, cy - bh // 2 - head_r - horn), (cx - head_r + 4, cy - bh // 2 - head_r - 2)])
    pygame.draw.polygon(screen, dark, [(cx + head_r - 2, cy - bh // 2 - head_r + 2), (cx + head_r + horn, cy - bh // 2 - head_r - horn), (cx + head_r - 4, cy - bh // 2 - head_r - 2)])

    pygame.draw.circle(screen, skin, (cx, cy - bh // 2 - head_r), head_r)
    pygame.draw.circle(screen, dark, (cx, cy - bh // 2 - head_r), head_r - 2)

    er = max(head_r // 3, 2)
    ey = cy - bh // 2 - head_r - 1
    if atk > 0:
        pygame.draw.circle(screen, (255, 255, 0), (cx - er * 2, ey), er + 1)
        pygame.draw.circle(screen, (255, 255, 0), (cx + er * 2, ey), er + 1)
        pygame.draw.circle(screen, (255, 0, 0), (cx - er * 2, ey), er)
        pygame.draw.circle(screen, (255, 0, 0), (cx + er * 2, ey), er)
    else:
        pygame.draw.circle(screen, (0, 0, 0), (cx - er * 2, ey), er + 1)
        pygame.draw.circle(screen, (0, 0, 0), (cx + er * 2, ey), er + 1)
        pygame.draw.circle(screen, (255, 255, int(50 * shade)), (cx - er * 2, ey), er)
        pygame.draw.circle(screen, (255, 255, int(50 * shade)), (cx + er * 2, ey), er)

    mw = max(head_r, 4)
    mh = max(head_r // 2, 2)
    my = cy - bh // 2 - head_r + head_r // 2 + 2
    if atk > 0:
        ow = max(head_r + 4, 6)
        oh = max(head_r // 2 + 2, 4)
        pygame.draw.ellipse(screen, (int(100 * shade), int(10 * shade), int(10 * shade)), (cx - ow // 2, my, ow, oh))
    else:
        pygame.draw.ellipse(screen, (int(80 * shade), int(10 * shade), int(10 * shade)), (cx - mw // 2, my, mw, mh))

# --- PICKUPS ---
def draw_pickups():
    for p in gs.pickups:
        if not p["alive"]:
            continue
        dx = p["x"] - gs.player_x
        dy = p["y"] - gs.player_y
        dist = math.sqrt(dx * dx + dy * dy)

        if not has_line_of_sight(gs.player_x, gs.player_y, p["x"], p["y"]):
            continue

        angle_to = math.atan2(dy, dx)
        angle_diff = angle_to - gs.player_angle
        while angle_diff > math.pi: angle_diff -= 2 * math.pi
        while angle_diff < -math.pi: angle_diff += 2 * math.pi

        if abs(angle_diff) > HALF_FOV + 0.2:
            continue

        sx = int(HALF_W + angle_diff / HALF_FOV * HALF_W)
        if sx >= 0 and sx < WIDTH and dist > gs.depth_buffer[sx]:
            continue

        proj_h = min(int(PROJ_DIST / max(dist, 0.1)), HEIGHT)
        sy = HALF_H + proj_h // 4

        t = pygame.time.get_ticks() / 300.0
        bob = int(math.sin(t + p["x"]) * 4)

        if p["type"] == "ammo":
            size = max(proj_h // 8, 3)
            pygame.draw.rect(screen, (255, 200, 0), (sx - size // 2, sy - size // 2 + bob, size, size))
            pygame.draw.rect(screen, (200, 150, 0), (sx - size // 2 + 1, sy - size // 2 + bob + 1, size - 2, size - 2))
        elif p["type"] == "health":
            size = max(proj_h // 8, 3)
            pygame.draw.rect(screen, (0, 200, 0), (sx - size // 2, sy - size // 2 + bob, size, size))
            pygame.draw.rect(screen, (255, 255, 255), (sx - 1, sy - size // 2 + bob + 2, 2, size - 4))
            pygame.draw.rect(screen, (255, 255, 255), (sx - size // 2 + 2, sy - 1 + bob, size - 4, 2))

def check_pickups():
    for p in gs.pickups:
        if not p["alive"]:
            continue
        dx = p["x"] - gs.player_x
        dy = p["y"] - gs.player_y
        if math.sqrt(dx * dx + dy * dy) < 0.5:
            p["alive"] = False
            if p["type"] == "ammo":
                gs.player_ammo = min(gs.player_ammo + p["amount"], 999)
            elif p["type"] == "health":
                gs.player_health = min(gs.player_health + p["amount"], 100)
            snd_pickup.play()

# --- RUBY ---
def draw_ruby():
    if gs.ruby_found:
        return
    dx = gs.ruby_x - gs.player_x
    dy = gs.ruby_y - gs.player_y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 0.1 or dist > MAX_DEPTH:
        return
    if not has_line_of_sight(gs.player_x, gs.player_y, gs.ruby_x, gs.ruby_y):
        return
    angle_to = math.atan2(dy, dx)
    angle_diff = angle_to - gs.player_angle
    while angle_diff > math.pi: angle_diff -= 2 * math.pi
    while angle_diff < -math.pi: angle_diff += 2 * math.pi
    if abs(angle_diff) > HALF_FOV + 0.2:
        return
    sx = int(HALF_W + angle_diff / HALF_FOV * HALF_W)
    if sx >= 0 and sx < WIDTH and dist > gs.depth_buffer[sx]:
        return
    proj_h = min(int(PROJ_DIST / max(dist, 0.1)), HEIGHT)
    sy = HALF_H - int(gs.player_z * 60)
    t = pygame.time.get_ticks() / 400.0
    bob = int(math.sin(t) * 4)
    size = max(proj_h // 6, 4)
    glow = int(150 + 105 * math.sin(t * 2))
    glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (glow, 20, 20, 40), (size * 2, size * 2), size * 2)
    screen.blit(glow_surf, (sx - size * 2, sy - size // 2 + bob - size * 2))
    pts = [
        (sx, sy - size // 2 + bob - size),
        (sx + size // 2, sy - size // 2 + bob),
        (sx, sy - size // 2 + bob + size // 3),
        (sx - size // 2, sy - size // 2 + bob),
    ]
    pygame.draw.polygon(screen, (220, 20, 20), pts)
    pygame.draw.polygon(screen, (255, 80, 80), pts, 1)
    hl = [(sx, sy - size // 2 + bob - size + 2), (sx - size // 4, sy - size // 2 + bob)]
    pygame.draw.lines(screen, (255, 150, 150), False, hl, 1)

def check_ruby():
    if gs.ruby_found:
        return
    dx = gs.ruby_x - gs.player_x
    dy = gs.ruby_y - gs.player_y
    if math.sqrt(dx * dx + dy * dy) < 0.6:
        gs.ruby_found = True
        gs.score += 500
        snd_levelup.play()
        gs.level_complete_timer = 1

# --- PHYSICS ---
def update_physics():
    if not gs.on_ground:
        gs.vel_z -= GRAVITY
        gs.player_z += gs.vel_z
        if gs.player_z <= 0:
            gs.player_z = 0
            gs.vel_z = 0
            gs.on_ground = True

def player_jump():
    if gs.on_ground:
        gs.vel_z = JUMP_VEL
        gs.on_ground = False

# --- WEAPONS ---
def draw_weapon():
    now = pygame.time.get_ticks()
    w = WEAPONS[gs.weapon]

    bob_t = now / 200.0
    move_active = any([pygame.key.get_pressed()[k] for k in (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)])
    bob_scale = 1.0 if move_active else 0.2
    bob_x = int(math.sin(bob_t) * 4 * bob_scale)
    bob_y = int(math.cos(bob_t * 2) * 3 * bob_scale)

    flash = now - gs.last_shot_time
    recoil = max(0, 15 - flash // 4)
    side_recoil = max(0, 8 - flash // 6) * (1 if gs.weapon == "shotgun" else -1 if gs.weapon == "railgun" else 0)

    gun_x = HALF_W - 30 + bob_x + int(side_recoil)
    gun_y = HEIGHT - 130 + bob_y + recoil

    if gs.weapon == "pistol":
        pygame.draw.rect(screen, (55, 55, 58), (gun_x + 20, gun_y + 25, 20, 80))
        pygame.draw.rect(screen, (40, 40, 43), (gun_x + 18, gun_y + 25, 24, 10))
        pygame.draw.rect(screen, (60, 60, 63), (gun_x + 10, gun_y + 85, 40, 30))
        pygame.draw.rect(screen, (35, 35, 38), (gun_x + 5, gun_y + 110, 50, 12))
        pygame.draw.rect(screen, (70, 70, 73), (gun_x + 24, gun_y + 35, 12, 3))
        pygame.draw.rect(screen, (70, 70, 73), (gun_x + 24, gun_y + 45, 12, 3))
    elif gs.weapon == "shotgun":
        pygame.draw.rect(screen, (70, 50, 30), (gun_x + 15, gun_y + 20, 30, 85))
        pygame.draw.rect(screen, (50, 50, 53), (gun_x + 20, gun_y + 10, 8, 30))
        pygame.draw.rect(screen, (50, 50, 53), (gun_x + 32, gun_y + 10, 8, 30))
        pygame.draw.rect(screen, (55, 40, 25), (gun_x + 8, gun_y + 90, 44, 25))
        pygame.draw.rect(screen, (40, 30, 18), (gun_x + 3, gun_y + 110, 54, 14))
        pygame.draw.rect(screen, (85, 60, 35), (gun_x + 17, gun_y + 20, 2, 80))
        pygame.draw.rect(screen, (85, 60, 35), (gun_x + 41, gun_y + 20, 2, 80))
    elif gs.weapon == "machinegun":
        pygame.draw.rect(screen, (50, 50, 53), (gun_x + 18, gun_y + 15, 24, 90))
        pygame.draw.rect(screen, (42, 42, 45), (gun_x + 15, gun_y + 10, 30, 15))
        pygame.draw.rect(screen, (55, 55, 58), (gun_x + 10, gun_y + 90, 40, 20))
        pygame.draw.rect(screen, (35, 35, 38), (gun_x + 5, gun_y + 105, 50, 15))
        for i in range(3):
            pygame.draw.rect(screen, (60, 60, 63), (gun_x + 18 + i * 8, gun_y + 25, 4, 4))
        pygame.draw.rect(screen, (65, 65, 68), (gun_x + 22, gun_y + 18, 16, 2))
        pygame.draw.rect(screen, (65, 65, 68), (gun_x + 22, gun_y + 22, 16, 2))
    elif gs.weapon == "railgun":
        pygame.draw.rect(screen, (35, 55, 80), (gun_x + 15, gun_y + 10, 30, 95))
        pygame.draw.rect(screen, (42, 70, 105), (gun_x + 18, gun_y + 5, 24, 15))
        pygame.draw.rect(screen, (28, 42, 70), (gun_x + 8, gun_y + 90, 44, 25))
        pygame.draw.rect(screen, (20, 35, 55), (gun_x + 3, gun_y + 110, 54, 14))
        glow = int(80 + 80 * math.sin(now / 100.0))
        pygame.draw.rect(screen, (glow, glow, 180), (gun_x + 20, gun_y + 15, 20, 3))
        pygame.draw.rect(screen, (50, 90, 130), (gun_x + 19, gun_y + 10, 22, 2))
        pygame.draw.rect(screen, (50, 90, 130), (gun_x + 19, gun_y + 20, 22, 2))

    if flash < 80:
        t = flash / 80.0
        alpha = max(0, 1.0 - t)
        spread = int(t * 25) + 5
        if gs.weapon == "railgun":
            glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            gr = int(25 * alpha)
            pygame.draw.circle(glow_surf, (80, 140, 220, int(180 * alpha)), (30, 30), gr)
            pygame.draw.circle(glow_surf, (150, 200, 255, int(250 * alpha)), (30, 30), gr // 2)
            screen.blit(glow_surf, (gun_x + 15, gun_y - 15))
            for i in range(8):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(5, 20) * alpha
                px = int(gun_x + 30 + math.cos(angle) * dist)
                py = int(gun_y + 5 + math.sin(angle) * dist)
                sz = random.randint(1, 3)
                pygame.draw.circle(screen, (100 + random.randint(0, 100), 180, 255), (px, py), sz)
        elif gs.weapon == "shotgun":
            for i in range(12):
                ox = random.randint(-spread, spread)
                oy = random.randint(-spread, spread // 2)
                r = random.randint(1, int(5 * alpha))
                brightness = random.randint(150, 255)
                pygame.draw.circle(screen, (brightness, int(brightness * 0.7), 30), (gun_x + 30 + ox, gun_y + 10 + oy), r)
            for i in range(6):
                ox = random.randint(-spread // 2, spread // 2)
                oy = random.randint(-spread, 0)
                r = random.randint(1, int(3 * alpha))
                pygame.draw.circle(screen, (180, 180, 180), (gun_x + 30 + ox, gun_y + 5 + oy), r)
        else:
            fc = [(255, 240, 120), (255, 180, 60), (255, 130, 20)]
            c = fc[now % 3]
            glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            gr = int(18 * alpha)
            pygame.draw.circle(glow_surf, (c[0], c[1], c[2], int(200 * alpha)), (20, 20), gr)
            pygame.draw.circle(glow_surf, (255, 255, 200, int(250 * alpha)), (20, 20), gr // 2)
            screen.blit(glow_surf, (gun_x + 18, gun_y - 12))
            for i in range(5):
                ox = random.randint(-spread // 2, spread // 2)
                oy = random.randint(-spread, 2)
                r = random.randint(1, int(3 * alpha))
                pygame.draw.circle(screen, c, (gun_x + 30 + ox, gun_y + 10 + oy), r)

        smoke_count = 2 if gs.weapon == "shotgun" else 1
        for _ in range(smoke_count):
            sx = gun_x + 30 + random.randint(-5, 5)
            sy = gun_y + random.randint(-15, 0)
            spawn_particles(
                gs.player_x + math.cos(gs.player_angle) * 0.5,
                gs.player_y + math.sin(gs.player_angle) * 0.5,
                (180, 180, 180), count=1, speed=0.01, life=20, size=4
            )

    if flash < 10:
        screen_shake_x = random.randint(-2, 2)
        screen_shake_y = random.randint(-1, 1)
    else:
        screen_shake_x = 0
        screen_shake_y = 0

def shoot():
    w = WEAPONS[gs.weapon]
    now = pygame.time.get_ticks()

    if now - gs.last_shot_time < w["cooldown"]:
        return
    if gs.player_ammo < w["ammo_use"]:
        snd_empty.play()
        return

    gs.last_shot_time = now
    gs.player_ammo -= w["ammo_use"]

    snds = {"pistol": snd_pistol, "shotgun": snd_shotgun, "machinegun": snd_machinegun, "railgun": snd_railgun}
    snds[gs.weapon].play()

    for _ in range(w["bullets"]):
        spread = random.uniform(-w["spread"], w["spread"])
        gs.bullets.append({
            "x": gs.player_x, "y": gs.player_y,
            "dx": math.cos(gs.player_angle + spread) * w["speed"],
            "dy": math.sin(gs.player_angle + spread) * w["speed"],
            "life": int(w["range"] / w["speed"]),
            "damage": w["damage"],
        })

# --- ENEMIES ---
def move_enemies():
    for e in gs.enemies:
        if not e["alive"]:
            continue

        dx = gs.player_x - e["x"]
        dy = gs.player_y - e["y"]
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0.5 and dist < 15 and has_line_of_sight(e["x"], e["y"], gs.player_x, gs.player_y):
            e["alert"] = True

        if not e["alert"]:
            continue

        if e.get("attack_anim", 0) > 0:
            e["attack_anim"] -= 1
            e["anim"] += 2

        if dist < 15:
            speed = e["speed"]
            if dist > 1.0:
                nx = dx / dist
                ny = dy / dist
                margin = 0.25

                new_x = e["x"] + nx * speed
                if get_map(new_x + margin, e["y"]) == 0 and get_map(new_x - margin, e["y"]) == 0:
                    e["x"] = new_x
                else:
                    alt = e["x"] + ny * speed
                    if get_map(alt + margin, e["y"]) == 0 and get_map(alt - margin, e["y"]) == 0:
                        e["x"] = alt

                new_y = e["y"] + ny * speed
                if get_map(e["x"], new_y + margin) == 0 and get_map(e["x"], new_y - margin) == 0:
                    e["y"] = new_y
                else:
                    alt = e["y"] + nx * speed
                    if get_map(e["x"], alt + margin) == 0 and get_map(e["x"], alt - margin) == 0:
                        e["y"] = alt

                e["anim"] += 1
        else:
            wander = e.get("wander_angle", random.uniform(0, 6.28))
            if random.random() < 0.02:
                wander = random.uniform(0, 6.28)
            e["wander_angle"] = wander
            wx = math.cos(wander) * e["speed"] * 0.5
            wy = math.sin(wander) * e["speed"] * 0.5
            margin = 0.25
            nx = e["x"] + wx
            ny = e["y"] + wy
            if get_map(nx + margin, e["y"]) == 0 and get_map(nx - margin, e["y"]) == 0:
                e["x"] = nx
            else:
                e["wander_angle"] = random.uniform(0, 6.28)
            if get_map(e["x"], ny + margin) == 0 and get_map(e["x"], ny - margin) == 0:
                e["y"] = ny
            else:
                e["wander_angle"] = random.uniform(0, 6.28)
            e["anim"] += 1

def update_bullets():
    for b in gs.bullets[:]:
        b["x"] += b["dx"]
        b["y"] += b["dy"]
        b["life"] -= 1

        if get_map(b["x"], b["y"]) > 0:
            spawn_wall_hit(b["x"], b["y"])
            gs.bullets.remove(b)
            continue
        if b["life"] <= 0:
            spawn_spark(b["x"], b["y"], (255, 200, 50))
            gs.bullets.remove(b)
            continue

        for e in gs.enemies:
            if not e["alive"]:
                continue
            dx = b["x"] - e["x"]
            dy = b["y"] - e["y"]
            if math.sqrt(dx * dx + dy * dy) < 0.5:
                if not has_line_of_sight(b["x"], b["y"], e["x"], e["y"]):
                    continue
                e["hp"] -= b["damage"]
                e["alert"] = True
                snd_hit.play()
                spawn_blood(e["x"], e["y"])
                if e["hp"] <= 0:
                    e["alive"] = False
                    gs.kills += 1
                    gs.total_kills += 1
                    gs.score += {"zombie": 100, "skeleton": 150, "demon": 300}.get(e["type"], 100)
                    spawn_death(e["x"], e["y"], e["type"])
                    snd_kill.play()
                if b in gs.bullets:
                    gs.bullets.remove(b)
                break

def update_enemies_damage():
    now = pygame.time.get_ticks()
    for e in gs.enemies:
        if not e["alive"]:
            continue
        dx = e["x"] - gs.player_x
        dy = e["y"] - gs.player_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1.0 and now - e["last_hit"] > 600:
            e["last_hit"] = now
            e["attack_anim"] = 15
            gs.player_health -= 10
            gs.damage_flash = 15
            spawn_blood(gs.player_x, gs.player_y)
            snd_hurt.play()
            if gs.player_health < 0:
                gs.player_health = 0

def draw_bullets():
    w = WEAPONS[gs.weapon]
    for b in gs.bullets:
        bdx = b["x"] - gs.player_x
        bdy = b["y"] - gs.player_y
        bdist = math.sqrt(bdx * bdx + bdy * bdy)
        bangle = math.atan2(bdy, bdx) - gs.player_angle
        while bangle > math.pi: bangle -= 2 * math.pi
        while bangle < -math.pi: bangle += 2 * math.pi
        if abs(bangle) < HALF_FOV + 0.1 and bdist > 0.1:
            bsx = int(HALF_W + bangle / HALF_FOV * HALF_W)
            bsh = max(int(PROJ_DIST / bdist), 2)
            bsy = HALF_H
            r = max(bsh // 5, 2)
            color = w["color"]

            if gs.weapon == "railgun":
                trail_len = min(r * 3, 40)
                for i in range(trail_len):
                    t = i / trail_len
                    tx = int(bsx - math.sin(bangle) * i * 0.3)
                    ty = int(bsy)
                    alpha_t = 1.0 - t
                    tc = (int(color[0] * alpha_t), int(color[1] * alpha_t), int(min(255, color[2] + 50) * alpha_t))
                    sz = max(1, int(r * alpha_t))
                    pygame.draw.circle(screen, tc, (tx, ty), sz)
                glow_r = r * 2
                glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (100, 180, 255, 40), (glow_r, glow_r), glow_r)
                screen.blit(glow_surf, (bsx - glow_r, bsy - glow_r))
            elif gs.weapon == "shotgun":
                for i in range(3):
                    trail_t = i / 3.0
                    tx = int(bsx - math.cos(bangle) * i * 2)
                    ty = int(bsy - math.sin(bangle) * i * 1)
                    tc = (int(color[0] * (1 - trail_t * 0.5)), int(color[1] * (1 - trail_t * 0.3)), int(color[2] * (1 - trail_t * 0.3)))
                    pygame.draw.circle(screen, tc, (tx, ty), max(r - i, 1))
            else:
                pygame.draw.circle(screen, color, (bsx, bsy), r + 1)
                lighter = (min(255, color[0] + 80), min(255, color[1] + 80), min(255, color[2] + 80))
                pygame.draw.circle(screen, lighter, (bsx, bsy), r)
                pygame.draw.circle(screen, (255, 255, 255), (bsx, bsy), max(r // 2, 1))

                trail_len = min(r * 2, 20)
                for i in range(1, trail_len):
                    t = i / trail_len
                    tx = int(bsx + math.cos(gs.player_angle + math.pi) * i * 0.5)
                    ty = int(bsy)
                    tc = (int(color[0] * (1 - t)), int(color[1] * (1 - t)), int(color[2] * (1 - t)))
                    pygame.draw.circle(screen, tc, (tx, ty), max(1, int(r * (1 - t))))

# --- HUD ---
BAR_H = 40

def draw_hud():
    now = pygame.time.get_ticks()
    level = LEVELS[gs.level]
    total = len(gs.enemies)

    bar_y = HEIGHT - BAR_H
    pygame.draw.rect(screen, (60, 60, 60), (0, bar_y, WIDTH, BAR_H))
    pygame.draw.rect(screen, (80, 80, 80), (0, bar_y, WIDTH, 2))
    pygame.draw.rect(screen, (40, 40, 40), (0, bar_y + BAR_H - 2, WIDTH, 2))
    pygame.draw.line(screen, (50, 50, 50), (WIDTH // 3, bar_y + 4, ), (WIDTH // 3, bar_y + BAR_H - 4), 1)
    pygame.draw.line(screen, (50, 50, 50), (WIDTH * 2 // 3, bar_y + 4), (WIDTH * 2 // 3, bar_y + BAR_H - 4), 1)

    slot_font = pygame.font.SysFont("consolas", 10, bold=True)
    big_font = pygame.font.SysFont("consolas", 28, bold=True)
    med_font = pygame.font.SysFont("consolas", 16, bold=True)
    small_font = pygame.font.SysFont("consolas", 12)

    pygame.draw.rect(screen, (40, 0, 0), (4, bar_y + 4, 100, 14))
    hp_pct = max(0, gs.player_health)
    hp_color = (0, 200, 0) if hp_pct > 60 else (200, 200, 0) if hp_pct > 30 else (200, 0, 0)
    pygame.draw.rect(screen, hp_color, (4, bar_y + 4, int(100 * hp_pct / 100), 14))
    pygame.draw.rect(screen, (80, 80, 80), (4, bar_y + 4, 100, 14), 1)
    hp_lbl = med_font.render(f"{gs.player_health}%", True, (255, 255, 255))
    screen.blit(hp_lbl, (8, bar_y + 3))

    fc = max(0, min(255, int(200 * gs.player_health / 100)))
    face_x = WIDTH // 2
    face_y = bar_y + BAR_H // 2
    pygame.draw.circle(screen, (80, 60, 50), (face_x, face_y), 14)
    pygame.draw.circle(screen, (180, 140, 110), (face_x, face_y), 12)
    eye_y = face_y - 3
    pygame.draw.circle(screen, (255, 255, 255), (face_x - 4, eye_y), 3)
    pygame.draw.circle(screen, (255, 255, 255), (face_x + 4, eye_y), 3)
    if gs.player_health > 60:
        pygame.draw.circle(screen, (20, 20, 20), (face_x - 4, eye_y), 1)
        pygame.draw.circle(screen, (20, 20, 20), (face_x + 4, eye_y), 1)
        pygame.draw.line(screen, (140, 80, 60), (face_x - 3, face_y + 5), (face_x + 3, face_y + 5), 1)
    elif gs.player_health > 30:
        pygame.draw.circle(screen, (20, 20, 20), (face_x - 4, eye_y), 2)
        pygame.draw.circle(screen, (20, 20, 20), (face_x + 4, eye_y), 2)
        pygame.draw.line(screen, (140, 80, 60), (face_x - 4, face_y + 4), (face_x + 4, face_y + 6), 2)
    else:
        pygame.draw.circle(screen, (20, 20, 20), (face_x - 4, eye_y), 2)
        pygame.draw.circle(screen, (20, 20, 20), (face_x + 4, eye_y), 2)
        pygame.draw.line(screen, (160, 40, 40), (face_x - 5, face_y + 3), (face_x + 5, face_y + 7), 2)
        pygame.draw.circle(screen, (180, 30, 30), (face_x + 8, face_y - 2), 2)

    pygame.draw.rect(screen, (40, 0, 0), (WIDTH - 108, bar_y + 4, 100, 14))
    armor = gs.shield
    pygame.draw.rect(screen, (0, 80, 200), (WIDTH - 108, bar_y + 4, int(100 * armor / 100), 14))
    pygame.draw.rect(screen, (80, 80, 80), (WIDTH - 108, bar_y + 4, 100, 14), 1)
    arm_lbl = med_font.render(f"{armor}%", True, (100, 180, 255))
    screen.blit(arm_lbl, (WIDTH - 104, bar_y + 3))

    w = WEAPONS[gs.weapon]
    weapon_names = ["1", "2", "3", "4"]
    for i, wn in enumerate(weapon_names):
        if i < len(gs.weapons_owned):
            wx = 4 + i * 28
            wy = bar_y + 20
            if gs.weapons_owned[i] == gs.weapon:
                pygame.draw.rect(screen, (80, 80, 20), (wx, wy, 24, 16))
                pygame.draw.rect(screen, (180, 180, 80), (wx, wy, 24, 16), 1)
            else:
                pygame.draw.rect(screen, (40, 40, 40), (wx, wy, 24, 16))
                pygame.draw.rect(screen, (60, 60, 60), (wx, wy, 24, 16), 1)
            sl = slot_font.render(wn, True, (200, 200, 200) if i < len(gs.weapons_owned) else (60, 60, 60))
            screen.blit(sl, (wx + 8, wy + 1))

    ammo_color = (255, 255, 255) if gs.player_ammo > w["ammo_use"] * 3 else (255, 80, 80)
    ammo_lbl = big_font.render(str(gs.player_ammo), True, ammo_color)
    screen.blit(ammo_lbl, (WIDTH - 80, bar_y + 2))

    kill_lbl = small_font.render(f"{gs.kills}/{total}", True, (200, 100, 100))
    screen.blit(kill_lbl, (WIDTH // 3 + 8, bar_y + 22))

    time_lbl = small_font.render(f"{gs.time_played // 60}:{gs.time_played % 60:02d}", True, (150, 150, 150))
    screen.blit(time_lbl, (WIDTH * 2 // 3 + 8, bar_y + 22))

    lvl_lbl = small_font.render(f"LVL {gs.level + 1}", True, (150, 150, 200))
    screen.blit(lvl_lbl, (WIDTH * 2 // 3 + 8, bar_y + 4))

    score_lbl = small_font.render(f"{gs.score}", True, (200, 200, 100))
    screen.blit(score_lbl, (WIDTH // 3 + 8, bar_y + 4))

    draw_minimap()

    ruby_c = (255, 60, 60) if not gs.ruby_found else (60, 255, 60)
    ruby_t = "RUBY" if not gs.ruby_found else "OK"
    ruby_lbl = small_font.render(f"[{ruby_t}]", True, ruby_c)
    screen.blit(ruby_lbl, (4, bar_y - 14))

    if gs.sprinting:
        sp = small_font.render("SPRINT", True, (255, 200, 50))
        screen.blit(sp, (WIDTH - 55, bar_y - 14))

    ctrl = pygame.font.SysFont("consolas", 11)
    info = ctrl.render("WASD=move Shift=sprint Space=jump LClick=shoot 1-4=weapon ESC=quit", True, (70, 70, 70))
    screen.blit(info, (5, 5))

    if gs.damage_flash > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = int(gs.damage_flash / 15 * 120)
        overlay.fill((255, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        gs.damage_flash -= 1

    if gs.player_health <= 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        die_font = pygame.font.SysFont("consolas", 60, bold=True)
        death = die_font.render("YOU DIED", True, (255, 0, 0))
        screen.blit(death, (HALF_W - death.get_width() // 2, HALF_H - 60))
        ki = med_font.render(f"Kills: {gs.kills}/{total}  Score: {gs.score}", True, (255, 200, 100))
        screen.blit(ki, (HALF_W - ki.get_width() // 2, HALF_H + 5))
        hint = med_font.render("Press R to retry or ESC for menu", True, (200, 200, 200))
        screen.blit(hint, (HALF_W - hint.get_width() // 2, HALF_H + 40))

    if gs.ruby_found and gs.player_health > 0:
        gs.level_complete_timer += 1
        if gs.level_complete_timer < 180:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, min(gs.level_complete_timer, 60) * 2))
            screen.blit(overlay, (0, 0))
            big_font2 = pygame.font.SysFont("consolas", 50, bold=True)
            if gs.level < len(LEVELS) - 1:
                txt = big_font2.render("RUBY FOUND!", True, (255, 50, 50))
                screen.blit(txt, (HALF_W - txt.get_width() // 2, HALF_H - 50))
                ni = med_font.render(f"Next: {LEVELS[gs.level + 1]['name']}", True, (200, 200, 255))
                screen.blit(ni, (HALF_W - ni.get_width() // 2, HALF_H + 10))
            else:
                txt = big_font2.render("VICTORY!", True, (255, 215, 0))
                screen.blit(txt, (HALF_W - txt.get_width() // 2, HALF_H - 60))
                vi = med_font.render("All 10 rubies collected!", True, (255, 255, 200))
                screen.blit(vi, (HALF_W - vi.get_width() // 2, HALF_H))
                fi = med_font.render(f"Final Score: {gs.score}  Time: {gs.time_played // 60}:{gs.time_played % 60:02d}", True, (255, 200, 100))
                screen.blit(fi, (HALF_W - fi.get_width() // 2, HALF_H + 30))
        elif gs.level_complete_timer > 240:
            if gs.level < len(LEVELS) - 1:
                gs.level += 1
                init_level()

def draw_minimap():
    mm_size = 80
    mm_scale = mm_size / MAP_W
    mm_x = WIDTH - mm_size - 8
    mm_y = 8

    mm_surf = pygame.Surface((mm_size, mm_size), pygame.SRCALPHA)
    mm_surf.fill((0, 0, 0, 100))

    level = LEVELS[gs.level]
    for y in range(MAP_H):
        for x in range(MAP_W):
            t = level["walls"][y * MAP_W + x]
            if t > 0:
                c = {1: (100, 40, 40), 2: (40, 100, 40), 3: (40, 40, 100), 4: (100, 85, 40), 5: (55, 55, 70), 6: (90, 25, 20)}.get(t, (80, 80, 80))
                pygame.draw.rect(mm_surf, c, (x * mm_scale, y * mm_scale, mm_scale, mm_scale))

    for e in gs.enemies:
        if not e["alive"]:
            continue
        if not has_line_of_sight(gs.player_x, gs.player_y, e["x"], e["y"]):
            continue
        pygame.draw.circle(mm_surf, (200, 40, 40), (int(e["x"] * mm_scale), int(e["y"] * mm_scale)), 1)

    px = int(gs.player_x * mm_scale)
    py = int(gs.player_y * mm_scale)
    pygame.draw.circle(mm_surf, (0, 180, 0), (px, py), 2)
    ex = int(px + math.cos(gs.player_angle) * 5)
    ey = int(py + math.sin(gs.player_angle) * 5)
    pygame.draw.line(mm_surf, (0, 180, 0), (px, py), (ex, ey), 1)

    screen.blit(mm_surf, (mm_x, mm_y))

def draw_crosshair():
    c = (200, 200, 200)
    pygame.draw.circle(screen, c, (HALF_W, HALF_H), 2)
    pygame.draw.line(screen, c, (HALF_W - 8, HALF_H), (HALF_W - 3, HALF_H), 1)
    pygame.draw.line(screen, c, (HALF_W + 3, HALF_H), (HALF_W + 8, HALF_H), 1)
    pygame.draw.line(screen, c, (HALF_W, HALF_H - 8), (HALF_W, HALF_H - 3), 1)
    pygame.draw.line(screen, c, (HALF_W, HALF_H + 3), (HALF_W, HALF_H + 8), 1)

# --- MAIN MENU ---
def draw_menu():
    screen.fill((5, 2, 8))

    t = pygame.time.get_ticks() / 1000.0

    for i in range(15):
        x = int((math.sin(t * 0.2 + i * 1.7) * 0.5 + 0.5) * WIDTH)
        y = int((math.cos(t * 0.15 + i * 2.1) * 0.5 + 0.5) * HEIGHT)
        alpha = int(25 + 15 * math.sin(t + i))
        pygame.draw.circle(screen, (alpha, 0, 0), (x, y), random.randint(1, 2))

    for i in range(3):
        y = int(HEIGHT * 0.35 + i * 2 + math.sin(t * 1.5 + i) * 1.5)
        pygame.draw.line(screen, (50 + i * 10, 0, 0), (0, y), (WIDTH, y), 1)

    title_font = pygame.font.SysFont("consolas", 72, bold=True)
    shadow = title_font.render("BLOOD CORRIDOR", True, (40, 0, 0))
    screen.blit(shadow, (HALF_W - shadow.get_width() // 2 + 3, 83))
    title = title_font.render("BLOOD CORRIDOR", True, (160, 20, 20))
    screen.blit(title, (HALF_W - title.get_width() // 2, 80))

    sub_font = pygame.font.SysFont("consolas", 18)
    sub = sub_font.render("A Raycasting FPS Adventure", True, (80, 50, 50))
    screen.blit(sub, (HALF_W - sub.get_width() // 2, 160))

    menu_font = pygame.font.SysFont("consolas", 28, bold=True)

    options = ["START GAME", "QUIT"]
    for i, opt in enumerate(options):
        y = 280 + i * 60
        if i == gs.menu_selection:
            glow = int(140 + 60 * math.sin(t * 3))
            txt = menu_font.render(f"> {opt} <", True, (glow, 30, 30))
            pygame.draw.rect(screen, (30, 8, 8), (HALF_W - 150, y - 5, 300, 35))
            pygame.draw.rect(screen, (60, 15, 15), (HALF_W - 150, y - 5, 300, 35), 2)
        else:
            txt = menu_font.render(opt, True, (70, 70, 70))
        screen.blit(txt, (HALF_W - txt.get_width() // 2, y))

    info_font = pygame.font.SysFont("consolas", 14)
    info = info_font.render("Arrow keys / Mouse to select  ENTER to confirm", True, (55, 55, 55))
    screen.blit(info, (HALF_W - info.get_width() // 2, HEIGHT - 40))

    stats_font = pygame.font.SysFont("consolas", 14)
    stats = stats_font.render(f"10 Levels  |  4 Weapons  |  3 Enemy Types", True, (40, 40, 55))
    screen.blit(stats, (HALF_W - stats.get_width() // 2, HEIGHT - 70))

# --- PLAYER ---
def move_player(dx, dy):
    margin = 0.2
    new_x = gs.player_x + dx
    tile_x1 = get_map(new_x + margin, gs.player_y)
    tile_x2 = get_map(new_x - margin, gs.player_y)
    can_move_x = (tile_x1 == 0) or (tile_x1 in WALL_HEIGHTS and gs.player_z >= JUMP_CLEAR.get(tile_x1, 0.5))
    can_move_x = can_move_x and ((tile_x2 == 0) or (tile_x2 in WALL_HEIGHTS and gs.player_z >= JUMP_CLEAR.get(tile_x2, 0.5)))
    if can_move_x:
        gs.player_x = new_x
    new_y = gs.player_y + dy
    tile_y1 = get_map(gs.player_x, new_y + margin)
    tile_y2 = get_map(gs.player_x, new_y - margin)
    can_move_y = (tile_y1 == 0) or (tile_y1 in WALL_HEIGHTS and gs.player_z >= JUMP_CLEAR.get(tile_y1, 0.5))
    can_move_y = can_move_y and ((tile_y2 == 0) or (tile_y2 in WALL_HEIGHTS and gs.player_z >= JUMP_CLEAR.get(tile_y2, 0.5)))
    if can_move_y:
        gs.player_y = new_y

# --- MAIN LOOP ---
def main():
    global MAX_DEPTH
    running = True
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    gs.depth_buffer = [MAX_DEPTH] * WIDTH
    frame_count = 0

    while running:
        dt = clock.tick(FPS)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if gs.state == "menu":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        gs.menu_selection = (gs.menu_selection - 1) % 2
                        snd_menu.play()
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        gs.menu_selection = (gs.menu_selection + 1) % 2
                        snd_menu.play()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if gs.menu_selection == 0:
                            gs.state = "game"
                            gs.level = 0
                            gs.score = 0
                            gs.total_kills = 0
                            gs.time_played = 0
                            gs.weapon = "pistol"
                            gs.weapon_idx = 0
                            gs.weapons_owned = ["pistol"]
                            gs.player_ammo = 50
                            init_level()
                        else:
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif gs.state == "game":
                    if event.key == pygame.K_ESCAPE:
                        gs.state = "menu"
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                    if event.key == pygame.K_r and gs.player_health <= 0:
                        init_level()
                    if event.key == pygame.K_r and gs.level_complete_timer > 180:
                        if gs.level < len(LEVELS) - 1:
                            gs.level += 1
                            init_level()

                    if event.key in (pygame.K_SPACE, pygame.K_LALT, pygame.K_RALT) and gs.player_health > 0 and gs.level_complete_timer == 0:
                        player_jump()

                    if event.key == pygame.K_1 and len(gs.weapons_owned) > 0:
                        gs.weapon_idx = 0
                        gs.weapon = gs.weapons_owned[gs.weapon_idx]
                    if event.key == pygame.K_2 and len(gs.weapons_owned) > 1:
                        gs.weapon_idx = 1
                        gs.weapon = gs.weapons_owned[gs.weapon_idx]
                    if event.key == pygame.K_3 and len(gs.weapons_owned) > 2:
                        gs.weapon_idx = 2
                        gs.weapon = gs.weapons_owned[gs.weapon_idx]
                    if event.key == pygame.K_4 and len(gs.weapons_owned) > 3:
                        gs.weapon_idx = 3
                        gs.weapon = gs.weapons_owned[gs.weapon_idx]

                    if event.key == pygame.K_q:
                        gs.weapon_idx = (gs.weapon_idx - 1) % len(gs.weapons_owned)
                        gs.weapon = gs.weapons_owned[gs.weapon_idx]

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if gs.state == "menu":
                    if event.button == 1:
                        gs.menu_selection = (gs.menu_selection + 1) % 2
                    elif event.button == 3:
                        gs.menu_selection = (gs.menu_selection - 1) % 2
                elif gs.state == "game":
                    if event.button == 1 and gs.player_health > 0:
                        shoot()
                    elif event.button in (4, 5):
                        if event.button == 4:
                            gs.weapon_idx = (gs.weapon_idx - 1) % len(gs.weapons_owned)
                        else:
                            gs.weapon_idx = (gs.weapon_idx + 1) % len(gs.weapons_owned)
                        gs.weapon = gs.weapons_owned[gs.weapon_idx]

        if gs.state == "menu":
            draw_menu()

        elif gs.state == "game":
            if gs.player_health > 0 and gs.level_complete_timer == 0:
                keys = pygame.key.get_pressed()
                move_dx = 0
                move_dy = 0
                gs.sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                speed = MOVE_SPEED * (SPRINT_MULT if gs.sprinting else 1.0)

                if keys[pygame.K_w]:
                    move_dx += math.cos(gs.player_angle) * speed
                    move_dy += math.sin(gs.player_angle) * speed
                if keys[pygame.K_s]:
                    move_dx -= math.cos(gs.player_angle) * speed
                    move_dy -= math.sin(gs.player_angle) * speed
                if keys[pygame.K_a]:
                    move_dx += math.cos(gs.player_angle - math.pi / 2) * speed
                    move_dy += math.sin(gs.player_angle - math.pi / 2) * speed
                if keys[pygame.K_d]:
                    move_dx += math.cos(gs.player_angle + math.pi / 2) * speed
                    move_dy += math.sin(gs.player_angle + math.pi / 2) * speed

                move_player(move_dx, move_dy)

                if keys[pygame.K_LEFT]:
                    gs.player_angle -= ROT_SPEED
                if keys[pygame.K_RIGHT]:
                    gs.player_angle += ROT_SPEED

                if keys[pygame.K_LCTRL]:
                    shoot()

                mx, _ = pygame.mouse.get_rel()
                gs.player_angle += mx * 0.002

                update_physics()

                if frame_count % 60 == 0:
                    gs.time_played += 1

            if gs.level_complete_timer == 0:
                move_enemies()
                update_bullets()
                update_enemies_damage()
                check_pickups()
                check_ruby()
                update_particles()

            screen.fill((0, 0, 0))
            walls = ray_cast()
            draw_textured_walls(walls)
            draw_pickups()
            draw_ruby()
            draw_enemies()
            draw_bullets()
            draw_particles()
            draw_weapon()
            draw_crosshair()
            draw_hud()

        pygame.display.flip()

    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
