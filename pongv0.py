import pygame, sys, random

# --- INIT ---
pygame.init()
WIDTH, HEIGHT = 400, 300
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG VIBESR ONLY - FAMICOM BEEPS")
CLOCK = pygame.time.Clock()
FPS = 60

# --- NES PALETTE ---
BG_COLOR = (84, 84, 84)
WHITE = (255, 255, 255)
PADDLE_COLOR = (192, 192, 192)
BALL_COLOR = (240, 188, 60)

# --- SOUNDS ---
def beep(freq, dur=80):
    # Generate NES-style square wave beep in RAM, no files
    arr = pygame.sndarray.make_sound(
        (4096 * (pygame.surfarray.pixels2d(
            pygame.Surface((dur, 1))).copy() * 0 + (
            [1 if (i * freq // 44100) % 2 == 0 else -1 for i in range(dur)]
        ))).astype("int16")
    )
    arr.play(maxtime=dur)

# --- GAME VARS ---
PADDLE_W, PADDLE_H = 8, 48
BALL_SIZE = 8
PLAYER_X = 16
AI_X = WIDTH - 16 - PADDLE_W
player_y = HEIGHT // 2 - PADDLE_H // 2
ai_y = HEIGHT // 2 - PADDLE_H // 2
ball_x = WIDTH // 2 - BALL_SIZE // 2
ball_y = HEIGHT // 2 - BALL_SIZE // 2
ball_dx = random.choice([-3, 3])
ball_dy = random.choice([-2, 2])
player_score = 0
ai_score = 0

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = WIDTH // 2 - BALL_SIZE // 2
    ball_y = HEIGHT // 2 - BALL_SIZE // 2
    ball_dx = random.choice([-3, 3])
    ball_dy = random.choice([-2, 2])

# --- MAIN LOOP ---
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:    player_y -= 5
    if keys[pygame.K_DOWN]:  player_y += 5
    player_y = max(0, min(HEIGHT - PADDLE_H, player_y))

    # --- AI ---
    if ai_y + PADDLE_H//2 < ball_y: ai_y += 3
    elif ai_y + PADDLE_H//2 > ball_y: ai_y -= 3
    ai_y = max(0, min(HEIGHT - PADDLE_H, ai_y))

    # --- BALL MOVE ---
    ball_x += ball_dx
    ball_y += ball_dy

    # Wall bounce
    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_dy *= -1
        beep(600 + random.randint(-40, 40))
    # Paddle bounce
    if (PLAYER_X < ball_x < PLAYER_X+PADDLE_W and
        player_y < ball_y+BALL_SIZE and ball_y < player_y+PADDLE_H):
        ball_dx *= -1
        beep(1000)
    if (AI_X < ball_x+BALL_SIZE < AI_X+PADDLE_W+BALL_SIZE and
        ai_y < ball_y+BALL_SIZE and ball_y < ai_y+PADDLE_H):
        ball_dx *= -1
        beep(800)

    # Score
    if ball_x < 0:
        ai_score += 1
        beep(200)
        reset_ball()
    if ball_x > WIDTH:
        player_score += 1
        beep(400)
        reset_ball()

    # --- DRAW ---
    WIN.fill(BG_COLOR)
    pygame.draw.rect(WIN, PADDLE_COLOR, (PLAYER_X, player_y, PADDLE_W, PADDLE_H))
    pygame.draw.rect(WIN, PADDLE_COLOR, (AI_X, ai_y, PADDLE_W, PADDLE_H))
    pygame.draw.rect(WIN, BALL_COLOR, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))
    font = pygame.font.SysFont('Courier', 24)
    sfc = font.render(f"{player_score}   {ai_score}", 1, WHITE)
    WIN.blit(sfc, (WIDTH//2 - sfc.get_width()//2, 16))
    pygame.display.flip()
    CLOCK.tick(FPS)
