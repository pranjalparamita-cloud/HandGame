import cv2
import mediapipe as mp
import pygame
import random
import math
import numpy as np

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1280, 720  # Window size
CAM_WIDTH, CAM_HEIGHT = 640, 480 # Camera capture size
SMOOTHING = 5 # Higher = smoother movement, lower = faster response
PINCH_THRESHOLD = 30 # Distance between fingers to trigger click

# --- COLORS (Neon Palette) ---
BLACK = (10, 10, 15)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
WHITE = (255, 255, 255)
RED = (255, 50, 50)

# --- INITIALIZATION ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Void Hunter - Hand Gesture Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30, bold=True)
large_font = pygame.font.SysFont("Arial", 80, bold=True)

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
cap = cv2.VideoCapture(0)
cap.set(3, CAM_WIDTH)
cap.set(4, CAM_HEIGHT)

# --- CLASSES ---

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 8)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255  # Opacity/Life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 10 # Fade out speed
        self.size -= 0.1

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.life), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Target:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.radius = 0
        self.max_radius = random.randint(30, 50)
        self.growth_speed = 2
        self.color = random.choice([NEON_PINK, NEON_GREEN, RED])
        self.active = True
        self.spawn_anim = True
        
    def update(self):
        # Grow animation
        if self.spawn_anim:
            self.radius += self.growth_speed
            if self.radius >= self.max_radius:
                self.radius = self.max_radius
                self.spawn_anim = False
        
        # Jiggle effect
        self.offset_x = random.randint(-1, 1)
        self.offset_y = random.randint(-1, 1)

    def draw(self, surface):
        if self.active:
            # Glow effect (draw larger translucent circle)
            s = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, 50), (self.radius*2, self.radius*2), self.radius + 10)
            surface.blit(s, (self.x - self.radius*2 + self.offset_x, self.y - self.radius*2 + self.offset_y))
            
            # Solid center
            pygame.draw.circle(surface, self.color, (self.x + self.offset_x, self.y + self.offset_y), self.radius, 3)
            pygame.draw.circle(surface, WHITE, (self.x + self.offset_x, self.y + self.offset_y), self.radius - 10)

# --- HELPER FUNCTIONS ---

def get_hand_pos(results, width, height):
    """
    Returns (index_x, index_y, pinch_distance)
    Coordinates are mapped to the Pygame screen resolution.
    """
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get Index Tip (8) and Thumb Tip (4)
            index_tip = hand_landmarks.landmark[8]
            thumb_tip = hand_landmarks.landmark[4]

            # Convert to screen coordinates
            # Note: We subtract x from 1 to mirror the movement
            ix, iy = int((1 - index_tip.x) * width), int(index_tip.y * height)
            tx, ty = int((1 - thumb_tip.x) * width), int(thumb_tip.y * height)

            # Calculate distance between thumb and index
            distance = math.hypot(ix - tx, iy - ty)
            
            return ix, iy, distance
    return None, None, None

# --- MAIN GAME LOOP ---

def main():
    run = True
    
    # Game State
    particles = []
    targets = []
    score = 0
    start_time = pygame.time.get_ticks()
    game_duration = 60000 # 60 seconds
    game_over = False
    
    # Cursor smooth tracking variables
    curr_x, curr_y = WIDTH // 2, HEIGHT // 2
    prev_x, prev_y = WIDTH // 2, HEIGHT // 2
    
    # Click State
    is_pinching = False
    was_pinching = False # For debounce (detect single click)

    while run:
        # 1. READ WEBCAM
        success, img = cap.read()
        if not success:
            break
        
        # 2. DETECT HANDS
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        # 3. GAME LOGIC UPDATES
        
        # Get Hand Coordinates
        target_x, target_y, pinch_dist = get_hand_pos(results, WIDTH, HEIGHT)
        
        # Smooth Movement (Linear Interpolation)
        if target_x is not None:
            curr_x = prev_x + (target_x - prev_x) / SMOOTHING
            curr_y = prev_y + (target_y - prev_y) / SMOOTHING
            prev_x, prev_y = curr_x, curr_y
            
            # Check Pinch
            if pinch_dist < PINCH_THRESHOLD:
                is_pinching = True
            else:
                is_pinching = False
        
        # Pygame Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Reset Game
                    score = 0
                    targets = []
                    particles = []
                    start_time = pygame.time.get_ticks()
                    game_over = False

        # Draw Background
        screen.fill(BLACK)
        
        if not game_over:
            # Spawn Targets periodically
            if len(targets) < 5 and random.randint(0, 50) == 0:
                targets.append(Target())
                
            # Update and Draw Targets
            for target in targets[:]:
                target.update()
                target.draw(screen)
                
                # COLLISION DETECTION (Cursor overlaps Target + PINCH)
                dist_to_target = math.hypot(curr_x - target.x, curr_y - target.y)
                
                # Check for "Click" (Transition from Not Pinching -> Pinching)
                if is_pinching and not was_pinching: 
                    if dist_to_target < target.radius:
                        # HIT!
                        targets.remove(target)
                        score += 10
                        # Spawn explosion
                        for _ in range(15):
                            particles.append(Particle(target.x, target.y, target.color))
            
            # Update Click State
            was_pinching = is_pinching

            # Update and Draw Particles
            for p in particles[:]:
                p.update()
                p.draw(screen)
                if p.life <= 0:
                    particles.remove(p)

            # Draw Cursor
            cursor_color = NEON_CYAN if not is_pinching else NEON_PINK
            cursor_radius = 20 if not is_pinching else 15
            
            # Draw Crosshair lines
            pygame.draw.line(screen, cursor_color, (curr_x - 30, curr_y), (curr_x + 30, curr_y), 2)
            pygame.draw.line(screen, cursor_color, (curr_x, curr_y - 30), (curr_x, curr_y + 30), 2)
            # Draw Circle
            pygame.draw.circle(screen, cursor_color, (int(curr_x), int(curr_y)), cursor_radius, 2)
            
            # Draw Time and Score
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
            time_left = max(0, 60 - elapsed_time)
            
            score_text = font.render(f"SCORE: {score}", True, WHITE)
            time_text = font.render(f"TIME: {int(time_left)}", True, WHITE)
            
            screen.blit(score_text, (20, 20))
            screen.blit(time_text, (WIDTH - 150, 20))
            
            if time_left <= 0:
                game_over = True

        else:
            # Game Over Screen
            game_over_text = large_font.render("GAME OVER", True, RED)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            restart_text = font.render("Press 'R' to Restart", True, NEON_CYAN)
            
            screen.blit(game_over_text, (WIDTH//2 - 200, HEIGHT//2 - 100))
            screen.blit(final_score_text, (WIDTH//2 - 90, HEIGHT//2))
            screen.blit(restart_text, (WIDTH//2 - 120, HEIGHT//2 + 60))

        # Show OpenCV small preview in corner (Optional)
        # Resize frame to small box
        img_small = cv2.resize(img, (240, 180))
        img_small = cv2.flip(img_small, 1) # Mirror
        img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
        img_small = np.rot90(img_small) # Pygame surfaces are different orientation sometimes, but usually swapaxes works better
        img_small = pygame.surfarray.make_surface(img_small)
        img_small = pygame.transform.rotate(img_small, -90) # Correct rotation
        
        # Draw camera feed with a border
        screen.blit(img_small, (WIDTH - 250, HEIGHT - 190))
        pygame.draw.rect(screen, WHITE, (WIDTH - 250, HEIGHT - 190, 240, 180), 2)

        # Update Display
        pygame.display.flip()
        clock.tick(60)

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()