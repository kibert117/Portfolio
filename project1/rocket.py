import pygame
import sys
import math
import random

pygame.init()
pygame.display.set_caption("LAUNCH — Rocket Crash Simulator (Python)")
clock = pygame.time.Clock()

# Настройки
WIDTH, HEIGHT = 920, 720
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
canvas = screen

# Цвета
COLORS = {
    "bg": (11, 14, 20),
    "panel": (20, 25, 34),
    "panel2": (25, 31, 43),
    "line": (38, 46, 61),
    "orange": (255, 107, 53),
    "gold": (255, 183, 3),
    "cyan": (76, 201, 240),
    "red": (255, 77, 94),
    "text": (230, 233, 239),
    "dim": (136, 145, 163),
    "green": (124, 240, 160),
    "chip1": (85, 95, 114),
    "chip2": (255, 140, 150),
    "chip3": (76, 201, 240),
    "chip4": (255, 183, 3),
    "chip5": (181, 23, 158),
    "purple": (160, 60, 255),
}

# Шрифты
font_main = pygame.font.SysFont("segoeui", 26, bold=True)
font_huge = pygame.font.SysFont("segoeui", 56, bold=True)
font_code = pygame.font.SysFont("consolas", 16, bold=True)
font_small = pygame.font.SysFont("segoeui", 12, bold=True)
font_caption = pygame.font.SysFont("segoeui", 10, bold=True)
font_stats = pygame.font.SysFont("consolas", 15, bold=True)
font_btn = pygame.font.SysFont("segoeui", 16, bold=True)

# Звуки
def create_beep(freq, duration, volume=0.15):
    import struct
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    
    buffer = bytearray()
    for t in range(n_samples):
        sample = int(32767 * volume * math.sin(2 * math.pi * freq * t / sample_rate))
        buffer.extend(struct.pack('<h', sample))
    
    try:
        sound = pygame.mixer.Sound(buffer=bytes(buffer))
        return sound
    except (AttributeError, TypeError):
        return None

SOUND = {
    "tick": [create_beep(380 + i * 70, 0.09) for i in range(5)],
    "cashout": [create_beep(f, 0.18) for f in [660, 880, 1100]],
    "win": create_beep(523, 0.4),
    "lose": create_beep(150, 0.5),
    "blip": create_beep(880, 0.05),
}

class Game:
    def __init__(self):
        self.state = "waiting"
        self.balance = 1000
        self.bet = 50
        self.crash_point = 1.00
        self.current_mult = 1.00
        self.wait_remaining = 20
        self.wait_start_time = 0
        self.path = []
        self.particles = []
        self.trail = []
        self.history = []
        self.bot_list = []
        self.bet_placed = False
        self.cashed_out = False
        self.cashed_mult = 0.0
        self.muted = False
        self.forced_crash = None
        self.last_bot_update = 0
        self.promo_msg = "Попробуйте код ROCKET"
        self.promo_color = COLORS["gold"]
        self.stats = {
            "turnover": 0,
            "max_win": 1.00,
            "cashes": 0,
            "profit": 0,
        }
        self.achievements = {
            "ach1": False,
            "ach2": False,
            "ach3": False,
            "ach4": False,
        }
        self.show_meme = None
        self.meme_text = ""
        self.admin_active = False
        self.start_wait()

    def start_wait(self):
        self.state = "waiting"
        self.wait_remaining = 20
        self.wait_start_time = pygame.time.get_ticks()
        self.path = []
        self.particles = []
        self.trail = []
        self.crash_point = 1.00
        self.current_mult = 1.00
        self.bet_placed = False
        self.cashed_out = False
        self.show_meme = None
        self.generate_bots()
        self.timer_delay = 20

    def start_flight(self):
        self.state = "flying"
        if self.forced_crash is not None:
            self.crash_point = self.forced_crash
            self.forced_crash = None
        else:
            self.crash_point = max(1.00, min(0.97 / (1 - random.random()), 50))
        self.path = [{"t": 0, "m": 1.0}]
        self.current_mult = 1.0
        self.timer_delay = None

        for b in self.bot_list:
            b["status"] = "pending"
            b["cashed"] = None

    def end_flight(self):
        self.state = "ended"
        for b in self.bot_list:
            if b["status"] == "pending":
                b["status"] = "lost"
                b["cashed"] = "авария"

        if self.path:
            last = self.path[-1]
            x = self.get_x(last["t"])
            y = self.get_y(last["m"])
            self.create_explosion(x, y)

        if self.bet_placed and not self.cashed_out:
            self.show_meme = "lose"
            self.meme_text = "Ракета сделала БУМ 💥"
            if not self.muted:
                SOUND["lose"].play()
        elif self.bet_placed and self.cashed_out:
            self.show_meme = "win"
            win_text = random.choice([
                "Инвестор от бога 📈", "Мамкин трейдер в плюсе 😎", "Илон Маск плачет в сторонке 🚀", "Симуляция взломана 💰"
            ])
            self.meme_text = f"{win_text} (+{int(self.bet * self.cashed_mult)}) кр."
            if not self.muted:
                SOUND["win"].play()

        self.stats["turnover"] += self.bet if self.bet_placed else 0
        if self.bet_placed and self.cashed_out:
            self.stats["cashes"] += 1
            if self.cashed_mult > self.stats["max_win"]:
                self.stats["max_win"] = self.cashed_mult
            self.unlock_achievement("ach1", self.cashed_mult >= 2.00)
            self.unlock_achievement("ach2", self.cashed_mult >= 10.00)
        self.stats["profit"] = self.balance - 1000

        self.history.append(self.crash_point)
        if len(self.history) > 14:
            self.history.pop(0)
        self.unlock_achievement("ach3", self.bet >= 1000)

        self.timer_delay = 4 * FPS

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == "waiting":
            elapsed = (now - self.wait_start_time) / 1000
            self.wait_remaining = max(0, 20 - elapsed)
            if self.wait_remaining <= 0:
                self.start_flight()

        elif self.state == "flying":
            elapsed = (now - self.wait_start_time) / 1000
            self.current_mult = math.exp(0.16 * elapsed)
            self.path.append({"t": elapsed, "m": self.current_mult})

            if self.current_mult >= self.crash_point:
                self.current_mult = self.crash_point
                self.wait_start_time = now
                self.end_flight()

        elif self.state == "ended":
            if self.timer_delay is not None:
                self.timer_delay -= 1
                if self.timer_delay <= 0:
                    self.start_wait()

        if self.state == "flying" and now - self.last_bot_update > 50:
            self.last_bot_update = now
            for b in self.bot_list:
                if b["status"] == "pending" and b["target"] <= self.current_mult and b["target"] < self.crash_point:
                    b["status"] = "won"
                    b["cashed"] = b["target"]

        self.update_particles()

    def create_explosion(self, x, y):
        for _ in range(50):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "alpha": 1.0,
                "size": random.uniform(2, 5)
            })

    def update_particles(self):
        new_p = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["alpha"] -= 0.03
            p["size"] *= 0.97
            if p["alpha"] > 0:
                new_p.append(p)
        self.particles = new_p

        if self.state == "flying" and len(self.path) > 1:
            last = self.path[-1]
            prev = self.path[-2]
            dx = self.get_x(last["t"]) - self.get_x(prev["t"])
            dy = self.get_y(last["m"]) - self.get_y(prev["m"])
            angle = math.atan2(dy, dx)
            for _ in range(2):
                self.trail.append({
                    "x": self.get_x(last["t"]) - dx * 0.4,
                    "y": self.get_y(last["m"]) - dy * 0.4,
                    "vx": -math.cos(angle) * 1.5 + random.uniform(-0.75, 0.75),
                    "vy": -math.sin(angle) * 1.5 + random.uniform(-0.75, 0.75),
                    "alpha": 0.8,
                    "size": 4 + random.uniform(0, 5)
                })

        self.trail = [t for t in self.trail if t["alpha"] > 0]
        for t in self.trail:
            t["x"] += t["vx"]
            t["y"] += t["vy"]
            t["alpha"] -= 0.015
            t["size"] += 0.09

    def get_x(self, t):
        return 460 + t * 200

    def get_y(self, m):
        return 360 - 280 * (m - 1) / 9

    def draw(self):
        screen.fill(COLORS["bg"])

        pygame.draw.rect(screen, COLORS["panel"], (0, 0, WIDTH, 100))
        pygame.draw.line(screen, COLORS["line"], (0, 95), (WIDTH, 95), 1)

        self.draw_header()

        pygame.draw.rect(screen, COLORS["panel2"], (20, 110, WIDTH - 40, 380), border_radius=12)
        pygame.draw.line(screen, COLORS["line"], (20, 480), (WIDTH - 20, 480), 1)

        self.draw_game_canvas()

        pygame.draw.rect(screen, COLORS["panel"], (20, 490, WIDTH - 40, 40))
        self.draw_history()

        pygame.draw.rect(screen, COLORS["panel2"], (20, 530, WIDTH - 40, 160), border_radius=12)
        self.draw_players_panel()

        pygame.draw.rect(screen, COLORS["panel"], (20, 700 - 100, WIDTH - 40, 100), border_bottom_left_radius=12, border_bottom_right_radius=12)
        self.draw_controls()

        pygame.draw.rect(screen, COLORS["panel"], (0, HEIGHT - 60, WIDTH, 60))
        self.draw_promo()

        if self.admin_active:
            self.draw_admin_panel()

        if self.show_meme:
            self.draw_meme()

        pygame.display.flip()

    def draw_game_canvas(self):
        for i in range(11):
            x = 20 + i * (WIDTH - 40) / 10
            pygame.draw.line(screen, COLORS["line"], (x, 110), (x, 490), 1)

        for i in range(6):
            y = 110 + i * (380) / 5
            pygame.draw.line(screen, COLORS["line"], (20, y), (WIDTH - 20, y), 1)

        for _ in range(50):
            x = random.randint(40, WIDTH - 40)
            y = random.randint(120, 470)
            brightness = random.randint(100, 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)

        for i in range(len(self.path) - 1):
            p1 = self.path[i]
            p2 = self.path[i + 1]
            x1 = self.get_x(p1["t"])
            y1 = self.get_y(p1["m"])
            x2 = self.get_x(p2["t"])
            y2 = self.get_y(p2["m"])
            pygame.draw.line(screen, COLORS["gold"], (x1, y1), (x2, y2), 2)

        if self.state == "flying" and self.path:
            last = self.path[-1]
            rx = self.get_x(last["t"])
            ry = self.get_y(last["m"])
            pygame.draw.circle(screen, COLORS["orange"], (rx, ry), 8)

    def draw_stats(self):
        pygame.draw.rect(screen, COLORS["panel"], (WIDTH - 220, 110, 200, 380), border_radius=12)
        pygame.draw.line(screen, COLORS["line"], (WIDTH - 220, 110), (WIDTH - 220, 490), 1)

        y_offset = 130

        turnover_text = font_code.render(f" turnover: {int(self.stats['turnover'])} кр.", True, COLORS["cyan"])
        screen.blit(turnover_text, (WIDTH - 210, y_offset))
        y_offset += 30

        max_win_text = font_code.render(f" max win: {self.stats['max_win']:.2f}x", True, COLORS["green"])
        screen.blit(max_win_text, (WIDTH - 210, y_offset))
        y_offset += 30

        cashes_text = font_code.render(f" cashes: {self.stats['cashes']}", True, COLORS["gold"])
        screen.blit(cashes_text, (WIDTH - 210, y_offset))
        y_offset += 30

        profit_text = font_code.render(f" profit: {self.stats['profit']:+d} кр.", True, COLORS["orange"] if self.stats['profit'] < 0 else COLORS["green"])
        screen.blit(profit_text, (WIDTH - 210, y_offset))

        y_offset += 40

        pygame.draw.rect(screen, COLORS["panel2"], (WIDTH - 210, y_offset, 190, 60), border_radius=8)
        ach_text = font_small.render(" Достижения:", True, COLORS["text"])
        screen.blit(ach_text, (WIDTH - 200, y_offset + 5))

        if self.achievements["ach1"]:
            ach1_text = font_small.render(" ✅ >=2.00x", True, COLORS["green"])
            screen.blit(ach1_text, (WIDTH - 200, y_offset + 25))
        if self.achievements["ach2"]:
            ach2_text = font_small.render(" ✅ >=10.00x", True, COLORS["green"])
            screen.blit(ach2_text, (WIDTH - 200, y_offset + 35))
        if self.achievements["ach3"]:
            ach3_text = font_small.render(" ✅ >=1000 кр.", True, COLORS["green"])
            screen.blit(ach3_text, (WIDTH - 200, y_offset + 25))
        if self.achievements["ach4"]:
            ach4_text = font_small.render(" ✅ ROCKET", True, COLORS["purple"])
            screen.blit(ach4_text, (WIDTH - 200, y_offset + 25))

    def draw_header(self):
        logo = font_main.render("LAUNCH", True, COLORS["orange"])
        screen.blit(logo, (24, 16))
        sub = font_small.render("Игровые кредиты • Симулятор", True, COLORS["gold"])
        screen.blit(sub, (logo.get_width() + 30, 22))

        pygame.draw.rect(screen, COLORS["line"], (WIDTH - 180, 16, 150, 36), border_radius=6)
        bal_text = font_stats.render(f"{int(self.balance)} кр.", True, COLORS["cyan"])
        screen.blit(bal_text, (WIDTH - 170, 23))

        if self.admin_active:
            admin_text = font_small.render(" ADMIN", True, COLORS["red"])
            screen.blit(admin_text, (WIDTH - 170, 36))

        mute_text = font_small.render(" Мут" if not self.muted else " Звук", True, COLORS["green"] if not self.muted else COLORS["dim"])
        screen.blit(mute_text, (WIDTH - 170, 50))

    def draw_history(self):
        history_text = font_small.render("History:", True, COLORS["text"])
        screen.blit(history_text, (30, 495))

        for i, point in enumerate(self.history[-5:]):
            color = COLORS["green"] if point > 1.5 else COLORS["gold"]
            point_text = font_small.render(f" {point:.2f}", True, color)
            screen.blit(point_text, (90 + i * 40, 495))

    def draw_players_panel(self):
        y_offset = 540
        header_text = font_stats.render(" Players:", True, COLORS["text"])
        screen.blit(header_text, (30, y_offset))
        y_offset += 25

        for b in self.bot_list:
            status_color = COLORS["green"] if b["status"] == "won" else COLORS["dim"] if b["status"] == "pending" else COLORS["red"]
            status_text = font_small.render(f" {'✓' if b['status'] == 'won' else '⏳' if b['status'] == 'pending' else '✗'} {b.get('target', 0):.2f}x", True, status_color)
            screen.blit(status_text, (40, y_offset))
            if b["cashed"]:
                cash_text = font_small.render(f" → {b['cashed']:.2f}", True, COLORS["cyan"])
                screen.blit(cash_text, (140, y_offset))
            y_offset += 20

    def draw_controls(self):
        pygame.draw.rect(screen, COLORS["panel2"], (30, 600, 200, 40), border_radius=8)
        bet_text = font_btn.render(f"Bet: {self.bet} кр.", True, COLORS["text"])
        screen.blit(bet_text, (45, 610))

        pygame.draw.rect(screen, COLORS["orange"], (250, 600, 30, 40), border_radius=6)
        plus_text = font_btn.render("+", True, COLORS["text"])
        screen.blit(plus_text, (257, 605))

        pygame.draw.rect(screen, COLORS["orange"], (290, 600, 30, 40), border_radius=6)
        minus_text = font_btn.render("-", True, COLORS["text"])
        screen.blit(minus_text, (299, 605))

        crash_text = font_btn.render(f"Crash: {self.crash_point:.2f}x", True, COLORS["gold"])
        screen.blit(crash_text, (350, 610))

        cashout_rect = pygame.Rect(500, 600, 120, 40)
        if self.bet_placed and not self.cashed_out:
            pygame.draw.rect(screen, COLORS["green"], cashout_rect, border_radius=8)
            cashout_text = font_btn.render("Cashout", True, COLORS["text"])
            screen.blit(cashout_text, (540, 610))

        start_rect = pygame.Rect(700, 600, 120, 40)
        if self.state == "waiting":
            pygame.draw.rect(screen, COLORS["cyan"], start_rect, border_radius=8)
            start_text = font_btn.render("Start!", True, COLORS["text"])
            screen.blit(start_text, (730, 610))

    def draw_admin_panel(self):
        pygame.draw.rect(screen, COLORS["panel2"], (WIDTH - 220, 110, 200, 200), border_radius=12)
        pygame.draw.line(screen, COLORS["line"], (WIDTH - 220, 110), (WIDTH - 220, 310), 1)

        admin_text = font_stats.render(" Admin:", True, COLORS["red"])
        screen.blit(admin_text, (WIDTH - 200, 120))

        y_offset = 150

        crash_button = pygame.Rect(WIDTH - 190, y_offset, 170, 30)
        pygame.draw.rect(screen, COLORS["red"], crash_button, border_radius=6)
        crash_btn_text = font_small.render("Force Crash", True, COLORS["text"])
        screen.blit(crash_btn_text, (WIDTH - 175, y_offset + 8))

        promo_button = pygame.Rect(WIDTH - 190, y_offset + 40, 170, 30)
        pygame.draw.rect(screen, COLORS["gold"], promo_button, border_radius=6)
        promo_btn_text = font_small.render("Promo Code", True, COLORS["text"])
        screen.blit(promo_btn_text, (WIDTH - 175, y_offset + 40 + 8))

        mute_button = pygame.Rect(WIDTH - 190, y_offset + 80, 170, 30)
        pygame.draw.rect(screen, COLORS["cyan"], mute_button, border_radius=6)
        mute_btn_text = font_small.render("Toggle Mute", True, COLORS["text"])
        screen.blit(mute_btn_text, (WIDTH - 175, y_offset + 80 + 8))

    def draw_promo(self):
        promo_text = font_small.render(self.promo_msg, True, self.promo_color)
        screen.blit(promo_text, (20, HEIGHT - 48))
        promo_code = font_caption.render("Введите ROCKET для +1000 кр.", True, COLORS["dim"])
        screen.blit(promo_code, (20, HEIGHT - 38))

    def draw_meme(self):
        meme_bg = pygame.Surface((500, 150), pygame.SRCALPHA)
        meme_bg.fill((0, 0, 0, 200))
        screen.blit(meme_bg, (160, 270))
        meme_text = font_huge.render(self.meme_text, True, COLORS["text"])
        screen.blit(memo_text, (200, 310))

    def generate_bots(self):
        self.bot_list = []
        for _ in range(5):
            target = max(1.00, min(0.97 / (1 - random.random()), 50))
            self.bot_list.append({
                "status": "pending",
                "target": target,
                "cashed": None
            })

    def unlock_achievement(self, ach_id, condition):
        if condition and not self.achievements.get(ach_id, False):
            self.achievements[ach_id] = True
            if ach_id == "ach1":
                win_text = random.choice([
                    "Инвестор от бога 📈", "Мамкин трейдер в плюсе 😎", "Илон Маск плачет в сторонке 🚀", "Симуляция взломана 💰"
                ])
                self.meme_text = f"{win_text} (+{int(self.bet * self.cashed_mult)}) кр."
                self.show_meme = "win"
                if not self.muted:
                    SOUND["win"].play()

    def handle_click(self, pos):
        x, y = pos

        if 250 <= x <= 280 and 600 <= y <= 640 and self.state == "waiting":
            self.bet = min(self.bet + 50, self.balance)
            if not self.muted:
                SOUND["blip"].play()

        elif 290 <= x <= 320 and 600 <= y <= 640 and self.bet > 50 and self.state == "waiting":
            self.bet = max(50, self.bet - 50)
            if not self.muted:
                SOUND["blip"].play()

        elif 700 <= x <= 820 and 600 <= y <= 640 and self.state == "waiting" and self.bet > 0:
            self.bet_placed = True
            self.start_flight()
            if not self.muted:
                SOUND["blip"].play()

        elif 500 <= x <= 620 and 600 <= y <= 640 and self.bet_placed and not self.cashed_out and self.state == "flying":
            self.cashed_out = True
            self.cashed_mult = self.current_mult
            self.balance += int(self.bet * (self.cashed_mult - 1))
            if not self.muted:
                SOUND["cashout"].play()
            self.end_flight()

        elif WIDTH - 170 <= x <= WIDTH - 20 and 16 <= y <= 36:
            self.admin_active = not self.admin_active

        elif WIDTH - 170 <= x <= WIDTH - 20 and 48 <= y <= 68:
            self.muted = not self.muted

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.draw()
            clock.tick(FPS)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

game = Game()
game.run()
