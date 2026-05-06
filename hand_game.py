import cv2
import mediapipe as mp
import pygame
import random
import math
import numpy as np

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1280, 720
CAM_WIDTH, CAM_HEIGHT = 640, 480
SMOOTHING = 5
PINCH_THRESHOLD = 30

# --- COLORS ---
BLACK = (10, 10, 15)
DARK_BG = (5, 5, 20)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 140, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
DARK_CYAN = (0, 100, 100)
PURPLE = (150, 0, 255)

# --- INITIALIZATION ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Void Hunter - Hand Gesture Game")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont("Arial", 22, bold=True)
font = pygame.font.SysFont("Arial", 30, bold=True)
font_medium = pygame.font.SysFont("Arial", 45, bold=True)
font_large = pygame.font.SysFont("Arial", 80, bold=True)
font_title = pygame.font.SysFont("Arial", 100, bold=True)

# MediaPipe Setup - ONLY HANDS
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    model_complexity=1
)

cap = cv2.VideoCapture(0)
cap.set(3, CAM_WIDTH)
cap.set(4, CAM_HEIGHT)


# ---------------------------------------------
#  PARTICLE CLASS
# ---------------------------------------------
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        # Make sure color is a clean RGB tuple of ints
        self.color = (int(color[0]), int(color[1]), int(color[2]))
        self.size = random.randint(4, 10)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 9)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255
        self.gravity = 0.15

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98
        self.life -= 8
        self.size = max(0, self.size - 0.12)

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            sz = max(1, int(self.size))
            s = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
            alpha = max(0, min(255, int(self.life)))
            r = max(0, min(255, self.color[0]))
            g = max(0, min(255, self.color[1]))
            b = max(0, min(255, self.color[2]))
            pygame.draw.circle(s, (r, g, b, alpha), (sz, sz), sz)
            surface.blit(s, (int(self.x - sz), int(self.y - sz)))


# ---------------------------------------------
#  FLOATING STAR
# ---------------------------------------------
class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.2, 1.5)
        self.size = random.uniform(1, 3)
        self.brightness = random.randint(80, 255)
        self.twinkle_speed = random.uniform(1, 4)
        self.twinkle_dir = 1

    def update(self):
        self.y += self.speed
        self.brightness += self.twinkle_speed * self.twinkle_dir
        if self.brightness >= 255 or self.brightness <= 60:
            self.twinkle_dir *= -1
        if self.y > HEIGHT:
            self.reset()
            self.y = 0

    def draw(self, surface):
        b = int(max(0, min(255, self.brightness)))
        pygame.draw.circle(surface, (b, b, b), (int(self.x), int(self.y)), int(self.size))


# ---------------------------------------------
#  TARGET CLASS
# ---------------------------------------------
class Target:
    def __init__(self):
        self.x = random.randint(120, WIDTH - 120)
        self.y = random.randint(120, HEIGHT - 120)
        self.radius = 0
        self.max_radius = random.randint(28, 50)
        self.growth_speed = 2
        # Store as clean tuple
        raw = random.choice([NEON_PINK, NEON_GREEN, RED, NEON_ORANGE, PURPLE])
        self.color = (int(raw[0]), int(raw[1]), int(raw[2]))
        self.active = True
        self.spawn_anim = True
        self.pulse = 0
        self.pulse_dir = 1
        self.offset_x = 0
        self.offset_y = 0
        self.lifetime = random.randint(180, 360)
        self.age = 0

    def update(self):
        self.age += 1
        if self.age >= self.lifetime:
            self.active = False

        if self.spawn_anim:
            self.radius += self.growth_speed
            if self.radius >= self.max_radius:
                self.radius = self.max_radius
                self.spawn_anim = False

        self.pulse += 0.05 * self.pulse_dir
        if self.pulse > 1 or self.pulse < 0:
            self.pulse_dir *= -1

        self.offset_x = random.randint(-1, 1)
        self.offset_y = random.randint(-1, 1)

    def draw(self, surface):
        if not self.active or self.radius < 2:
            return

        r = int(self.radius)
        glow_r = int(r * 2 + 10 + self.pulse * 8)

        # Glow circle
        glow_size = glow_r * 2 + 4
        if glow_size > 0:
            s = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(
                s,
                (self.color[0], self.color[1], self.color[2], 40),
                (glow_r, glow_r),
                glow_r
            )
            surface.blit(s, (self.x - glow_r + self.offset_x, self.y - glow_r + self.offset_y))

        cx = self.x + self.offset_x
        cy = self.y + self.offset_y

        # Outer ring
        pygame.draw.circle(surface, self.color, (cx, cy), r, 3)

        # Inner white dot
        if r > 12:
            inner = max(2, r - 12)
            pygame.draw.circle(surface, WHITE, (cx, cy), inner)

        # Blink warning when about to expire
        if self.lifetime - self.age < 90:
            alpha = int(128 + 127 * math.sin(self.age * 0.2))
            alpha = max(0, min(255, alpha))
            warn_size = r * 2 + 12
            if warn_size > 0:
                warn_s = pygame.Surface((warn_size, warn_size), pygame.SRCALPHA)
                pygame.draw.circle(
                    warn_s,
                    (255, 50, 50, alpha),
                    (warn_size // 2, warn_size // 2),
                    warn_size // 2 - 1,
                    2
                )
                surface.blit(warn_s, (self.x - warn_size // 2, self.y - warn_size // 2))


# ---------------------------------------------
#  HELPER - Hand position
# ---------------------------------------------
def get_hand_pos(results, width, height):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            ix = int((1 - index_tip.x) * width)
            iy = int(index_tip.y * height)
            tx = int((1 - thumb_tip.x) * width)
            ty = int(thumb_tip.y * height)

            distance = math.hypot(ix - tx, iy - ty)
            return ix, iy, distance
    return None, None, None


# ---------------------------------------------
#  HELPER - Draw centered text
# ---------------------------------------------
def draw_text_centered(surface, text, font_obj, color, y, glow=False, glow_color=None):
    # Sanitize color
    color = (int(color[0]), int(color[1]), int(color[2]))

    if glow and glow_color:
        gc = (int(glow_color[0]), int(glow_color[1]), int(glow_color[2]))
        for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2),
                       (0, -3), (0, 3), (-3, 0), (3, 0)]:
            gs = font_obj.render(text, True, gc)
            r = gs.get_rect(center=(WIDTH // 2 + ox, y + oy))
            surface.blit(gs, r)

    ts = font_obj.render(text, True, color)
    r = ts.get_rect(center=(WIDTH // 2, y))
    surface.blit(ts, r)
    return r


def draw_text(surface, text, font_obj, color, x, y):
    color = (int(color[0]), int(color[1]), int(color[2]))
    ts = font_obj.render(text, True, color)
    surface.blit(ts, (x, y))
    return ts.get_rect(topleft=(x, y))


# ---------------------------------------------
#  HELPER - Neon button
# ---------------------------------------------
def draw_neon_button(surface, text, font_obj, rect, base_color, hover=False):
    base_color = (int(base_color[0]), int(base_color[1]), int(base_color[2]))
    border_color = WHITE if hover else base_color
    fill_alpha = 120 if hover else 60

    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((base_color[0], base_color[1], base_color[2], fill_alpha))
    surface.blit(s, rect.topleft)

    pygame.draw.rect(surface, border_color, rect, 2, border_radius=10)

    txt_color = WHITE if hover else base_color
    txt = font_obj.render(text, True, txt_color)
    tr = txt.get_rect(center=rect.center)
    surface.blit(txt, tr)


# ---------------------------------------------
#  BACKGROUND STARS
# ---------------------------------------------
stars = [Star() for _ in range(120)]


def draw_background():
    screen.fill(DARK_BG)
    for star in stars:
        star.update()
        star.draw(screen)


# ---------------------------------------------
#  PAGE 1 - WELCOME SCREEN
# ---------------------------------------------
def welcome_screen():
    tick = 0
    btn_rect = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2 + 120, 280, 60)

    while True:
        draw_background()
        tick += 1

        # Animated glow value
        glow_val = int(128 + 127 * math.sin(tick * 0.04))
        glow_val = max(0, min(255, glow_val))

        # Title
        draw_text_centered(
            screen, "NEON  VOID", font_title, NEON_CYAN, HEIGHT // 2 - 160,
            glow=True, glow_color=(0, glow_val, glow_val)
        )
        draw_text_centered(
            screen, "HUNTER", font_title, NEON_PINK, HEIGHT // 2 - 50,
            glow=True, glow_color=(glow_val, 0, glow_val // 2)
        )

        draw_text_centered(
            screen,
            "Control with your HAND  --  no mouse needed!",
            font_small, NEON_GREEN, HEIGHT // 2 + 40
        )
        draw_text_centered(
            screen,
            "Make sure your webcam is ON and your hand is visible.",
            font_small, WHITE, HEIGHT // 2 + 75
        )

        # Button
        mouse_pos = pygame.mouse.get_pos()
        hover = btn_rect.collidepoint(mouse_pos)
        draw_neon_button(screen, "START", font_medium, btn_rect, NEON_CYAN, hover)

        # Border pulse
        # Border pulse (stable - no blinking)
        pulse_w = int(2 + abs(2 * math.sin(tick * 0.05)))
        pygame.draw.rect(screen, NEON_CYAN, (0, 0, WIDTH, HEIGHT), pulse_w)

        # Version
        draw_text(screen, "v1.0  |  Hand Gesture Edition", font_small, DARK_CYAN, 10, HEIGHT - 30)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "instructions"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    return "instructions"


# ---------------------------------------------
#  PAGE 2 - INSTRUCTIONS SCREEN
# ---------------------------------------------
def instructions_screen():
    tick = 0
    btn_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 300, 60)

    instructions = [
        ("Show your HAND to the webcam",     "to control the cursor on screen."),
        ("PINCH Index finger + Thumb",        "together to SHOOT / click a target."),
        ("Aim the cursor over a target",      "then pinch to destroy it and earn points."),
        ("You have 60 seconds",               "Score as high as you can!"),
        ("Targets disappear if ignored",      "Be quick -- do not let them escape!"),
    ]

    while True:
        draw_background()
        tick += 1

        # Title
        draw_text_centered(
            screen, "HOW  TO  PLAY", font_large, NEON_YELLOW, 60,
            glow=True, glow_color=(100, 100, 0)
        )

        # Instruction cards
        card_x = 60
        card_y_start = 160
        card_h = 68
        card_gap = 10

        for i, (title_txt, desc_txt) in enumerate(instructions):
            y = card_y_start + i * (card_h + card_gap)
            card_rect = pygame.Rect(card_x, y, WIDTH - 460, card_h)

            # Card fill
            s = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            s.fill((0, 255, 255, 15))
            screen.blit(s, card_rect.topleft)
            pygame.draw.rect(screen, NEON_CYAN, card_rect, 1, border_radius=8)

            # Number badge
            badge_rect = pygame.Rect(card_x + 8, y + card_h // 2 - 14, 28, 28)
            pygame.draw.rect(screen, NEON_CYAN, badge_rect, border_radius=6)
            num_surf = font_small.render(str(i + 1), True, BLACK)
            screen.blit(num_surf, num_surf.get_rect(center=badge_rect.center))

            draw_text(screen, title_txt, font_small, NEON_CYAN, card_x + 46, y + 8)
            draw_text(screen, desc_txt,  font_small, WHITE,     card_x + 46, y + 36)

        # Live camera preview
        success, img = cap.read()
        if success:
            img_disp = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img_disp, cv2.COLOR_BGR2RGB)
            results_prev = hands_detector.process(img_rgb)

            if results_prev.multi_hand_landmarks:
                for hl in results_prev.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        img_disp, hl, mp_hands.HAND_CONNECTIONS
                    )

            preview = cv2.resize(img_disp, (300, 225))
            preview_rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
            preview_surf = pygame.surfarray.make_surface(
                np.transpose(preview_rgb, (1, 0, 2))
            )

            cam_x = WIDTH - 360
            cam_y = 150
            screen.blit(preview_surf, (cam_x, cam_y))
            pygame.draw.rect(screen, NEON_GREEN, (cam_x - 2, cam_y - 2, 304, 229), 2)
            draw_text(screen, "YOUR CAMERA", font_small, NEON_GREEN, cam_x + 70, cam_y + 233)

            if results_prev.multi_hand_landmarks:
                status_text = "Hand Detected!"
                status_color = NEON_GREEN
            else:
                status_text = "No Hand -- Show your hand!"
                status_color = RED

            draw_text_centered(screen, status_text, font_small, status_color, cam_y + 268)

        # Tip
        tip_y = card_y_start + len(instructions) * (card_h + card_gap) + 18
        draw_text_centered(
            screen,
            "TIP: Keep your hand well-lit and at arm's length from the camera.",
            font_small, NEON_YELLOW, tip_y
        )

        # Play button
        mouse_pos = pygame.mouse.get_pos()
        hover = btn_rect.collidepoint(mouse_pos)
        draw_neon_button(screen, "PLAY GAME", font_medium, btn_rect, NEON_GREEN, hover)

        # Back hint
        draw_text(screen, "BACKSPACE to go back", font_small, DARK_CYAN, 20, HEIGHT - 35)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "game"
                if event.key == pygame.K_BACKSPACE:
                    return "welcome"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    return "game"


# ---------------------------------------------
#  PAGE 3 - GAME SCREEN
# ---------------------------------------------
def game_screen():
    particles = []
    targets = []
    score = 0
    start_time = pygame.time.get_ticks()
    game_over = False

    curr_x, curr_y = float(WIDTH // 2), float(HEIGHT // 2)
    prev_x, prev_y = float(WIDTH // 2), float(HEIGHT // 2)

    is_pinching = False
    was_pinching = False

    combo = 0
    combo_timer = 0
    COMBO_TIMEOUT = 120

    # score popup: [label, x, y, life, color]
    score_popups = []

    spawn_timer = 0
    SPAWN_INTERVAL = 55

    run = True
    while run:
        # Read webcam
        success, img = cap.read()
        if not success:
            break

        # Detect hands ONLY
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands_detector.process(img_rgb)

        # Hand position
        target_x, target_y, pinch_dist = get_hand_pos(results, WIDTH, HEIGHT)

        if target_x is not None:
            curr_x = prev_x + (target_x - prev_x) / SMOOTHING
            curr_y = prev_y + (target_y - prev_y) / SMOOTHING
            prev_x, prev_y = curr_x, curr_y
            is_pinching = bool(pinch_dist < PINCH_THRESHOLD)
        else:
            is_pinching = False

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "welcome"
                if event.key == pygame.K_r and game_over:
                    return "game"

        # Background
        draw_background()

        if not game_over:
            # Spawn targets
            spawn_timer += 1
            if len(targets) < 6 and spawn_timer >= SPAWN_INTERVAL:
                spawn_timer = 0
                if random.randint(0, 2) != 0:
                    targets.append(Target())

            pinch_fired = is_pinching and not was_pinching

            # Update and draw targets
            for target in targets[:]:
                target.update()

                if not target.active:
                    targets.remove(target)
                    combo = 0
                    continue

                target.draw(screen)

                dist_to_target = math.hypot(curr_x - target.x, curr_y - target.y)
                if pinch_fired and dist_to_target < target.radius:
                    targets.remove(target)
                    combo += 1
                    combo_timer = COMBO_TIMEOUT

                    pts = 10 + (combo - 1) * 5
                    score += pts

                    for _ in range(20):
                        particles.append(Particle(target.x, target.y, target.color))

                    label = f"+{pts}"
                    if combo > 1:
                        label += f"  COMBO x{combo}"
                    pop_color = NEON_YELLOW if combo > 1 else WHITE
                    score_popups.append([label, float(target.x), float(target.y - 20), 80, pop_color])

            was_pinching = is_pinching

            # Combo timer
            if combo_timer > 0:
                combo_timer -= 1
            else:
                combo = 0

            # Particles
            for p in particles[:]:
                p.update()
                p.draw(screen)
                if p.life <= 0:
                    particles.remove(p)

            # Score popups
            for popup in score_popups[:]:
                popup[2] -= 1.5
                popup[3] -= 2
                if popup[3] <= 0:
                    score_popups.remove(popup)
                    continue
                alpha = max(0, min(255, int(popup[3] * 3)))
                col = (int(popup[4][0]), int(popup[4][1]), int(popup[4][2]))
                ps = font.render(popup[0], True, col)
                ps.set_alpha(alpha)
                screen.blit(ps, (int(popup[1]) - ps.get_width() // 2, int(popup[2])))

            # HUD bar
            hud_bg = pygame.Surface((WIDTH, 55), pygame.SRCALPHA)
            hud_bg.fill((0, 0, 0, 140))
            screen.blit(hud_bg, (0, 0))
            pygame.draw.line(screen, NEON_CYAN, (0, 55), (WIDTH, 55), 1)

            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
            time_left = max(0.0, 60.0 - elapsed_time)

            draw_text(screen, f"SCORE: {score}", font, WHITE, 20, 13)

            # Time bar
            bar_w = 300
            bar_h = 18
            bar_x = WIDTH // 2 - bar_w // 2
            bar_y = 18
            ratio = time_left / 60.0
            if ratio > 0.5:
                bar_color = NEON_GREEN
            elif ratio > 0.25:
                bar_color = NEON_YELLOW
            else:
                bar_color = RED

            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
            filled_w = max(0, int(bar_w * ratio))
            if filled_w > 0:
                pygame.draw.rect(screen, bar_color, (bar_x, bar_y, filled_w, bar_h), border_radius=5)
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=5)

            time_lbl = font_small.render(f"{int(time_left)}s", True, WHITE)
            screen.blit(time_lbl, (bar_x + bar_w + 8, bar_y))

            # Combo display
            if combo > 1:
                cx_text = font_medium.render(f"COMBO x{combo}", True, NEON_ORANGE)
                screen.blit(cx_text, (WIDTH - cx_text.get_width() - 20, 60))

            # Target count
            tgt_lbl = font_small.render(f"Targets: {len(targets)}/6", True, NEON_CYAN)
            screen.blit(tgt_lbl, (WIDTH - 150, 15))

            # Cursor
            cx_i = int(curr_x)
            cy_i = int(curr_y)
            cursor_color = NEON_CYAN if not is_pinching else NEON_PINK
            cursor_radius = 20 if not is_pinching else 12

            # Crosshair lines (gap in center)
            pygame.draw.line(screen, cursor_color, (cx_i - 35, cy_i), (cx_i - 8, cy_i), 2)
            pygame.draw.line(screen, cursor_color, (cx_i + 8,  cy_i), (cx_i + 35, cy_i), 2)
            pygame.draw.line(screen, cursor_color, (cx_i, cy_i - 35), (cx_i, cy_i - 8), 2)
            pygame.draw.line(screen, cursor_color, (cx_i, cy_i + 8),  (cx_i, cy_i + 35), 2)
            pygame.draw.circle(screen, cursor_color, (cx_i, cy_i), cursor_radius, 2)

            # Pinch flash ring
            if is_pinching:
                ring = pygame.Surface((64, 64), pygame.SRCALPHA)
                pygame.draw.circle(ring, (255, 20, 147, 80), (32, 32), 30)
                screen.blit(ring, (cx_i - 32, cy_i - 32))

            # No-hand warning
            if target_x is None:
                warn = font.render("Show your hand to the camera!", True, NEON_YELLOW)
                screen.blit(warn, (WIDTH // 2 - warn.get_width() // 2, HEIGHT // 2 - 20))

            if time_left <= 0:
                game_over = True

        else:
            # Game Over overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            draw_text_centered(screen, "GAME  OVER", font_large, RED,
                               HEIGHT // 2 - 160, glow=True, glow_color=(80, 0, 0))
            draw_text_centered(screen, f"Final Score:  {score}", font_medium, WHITE, HEIGHT // 2 - 60)

            if score >= 200:
                rating, col = "LEGENDARY!", NEON_YELLOW
            elif score >= 120:
                rating, col = "GREAT!", NEON_GREEN
            elif score >= 60:
                rating, col = "GOOD", NEON_CYAN
            else:
                rating, col = "Keep Practicing!", WHITE

            draw_text_centered(screen, rating, font_medium, col, HEIGHT // 2)
            draw_text_centered(screen, "Press  R  to Restart", font, NEON_CYAN, HEIGHT // 2 + 80)
            draw_text_centered(screen, "Press  ESC  for Main Menu", font, NEON_PINK, HEIGHT // 2 + 120)

        # Camera preview corner
        success2, img2 = cap.read()
        if success2:
            img_small = cv2.resize(img2, (200, 150))
            img_small = cv2.flip(img_small, 1)
            img_small_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
            img_surf = pygame.surfarray.make_surface(
                np.transpose(img_small_rgb, (1, 0, 2))
            )
            screen.blit(img_surf, (WIDTH - 210, HEIGHT - 160))
            pygame.draw.rect(screen, WHITE, (WIDTH - 210, HEIGHT - 160, 200, 150), 1)
            cam_lbl = font_small.render("CAM", True, WHITE)
            screen.blit(cam_lbl, (WIDTH - 210, HEIGHT - 178))

        pygame.display.flip()
        clock.tick(60)

    return "quit"


# ---------------------------------------------
#  MAIN ROUTER
# ---------------------------------------------
def main():
    page = "welcome"
    while page != "quit":
        if page == "welcome":
            page = welcome_screen()
        elif page == "instructions":
            page = instructions_screen()
        elif page == "game":
            page = game_screen()

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()


if __name__ == "__main__":
    main()
