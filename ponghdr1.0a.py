import pygame, sys, random
import numpy as np

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

WIDTH, HEIGHT = 400, 300
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG: O3 Alpha | Right = You, Left = AI")
CLOCK = pygame.time.Clock()
FPS = 60

BG_COLOR      = (84, 84, 84)
PADDLE_COLOR  = (200, 200, 200)
BALL_COLOR    = (255, 220, 40)
TEXT_COLOR    = (255,255,255)

def beep(freq=880, duration=90):
    sample_rate = 22050
    t = np.linspace(0, duration/1000, int(sample_rate*duration/1000), False)
    wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    audio = np.int16(wave * 32767)
    sound = pygame.sndarray.make_sound(audio)
    sound.play()

PADDLE_W, PADDLE_H = 8, 44
BALL_SIZE = 8
PLAYER_X = WIDTH - 32
AI_X = 24

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = WIDTH // 2 - BALL_SIZE // 2
    ball_y = HEIGHT // 2 - BALL_SIZE // 2
    ball_dx = random.choice([-3,3])
    ball_dy = random.choice([-2,2])

def reset_game():
    global player_score, ai_score, player_y, ai_y
    player_score = 0
    ai_score = 0
    player_y = HEIGHT // 2 - PADDLE_H // 2
    ai_y = HEIGHT // 2 - PADDLE_H // 2
    reset_ball()

def game_over(winner):
    WIN.fill(BG_COLOR)
    font_big = pygame.font.SysFont('Courier New', 32, bold=True)
    font_small = pygame.font.SysFont('Courier New', 20)
    text = f"{winner} wins!"
    surf1 = font_big.render("GAME OVER!", True, TEXT_COLOR)
    surf2 = font_big.render(text, True, TEXT_COLOR)
    surf3 = font_small.render("Play again? (Y/N)", True, TEXT_COLOR)
    WIN.blit(surf1, (WIDTH//2-surf1.get_width()//2, 80))
    WIN.blit(surf2, (WIDTH//2-surf2.get_width()//2, 130))
    WIN.blit(surf3, (WIDTH//2-surf3.get_width()//2, 190))
    pygame.display.flip()
    beep(140)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    reset_game()
                    return
                if event.key == pygame.K_n:
                    pygame.quit()
                    sys.exit()
        CLOCK.tick(30)

reset_game()

# --- Main Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:    player_y -= 5
    if keys[pygame.K_DOWN]:  player_y += 5
    player_y = max(0, min(HEIGHT - PADDLE_H, player_y))

    # --- AI ---
    if ai_y + PADDLE_H//2 < ball_y: ai_y += 3
    elif ai_y + PADDLE_H//2 > ball_y: ai_y -= 3
    ai_y = max(0, min(HEIGHT - PADDLE_H, ai_y))

    # --- Ball Movement ---
    ball_x += ball_dx
    ball_y += ball_dy

    # Wall bounce
    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_dy *= -1
        beep(700 + random.randint(-40, 40))
    # Paddle bounce
    if (PLAYER_X < ball_x+BALL_SIZE < PLAYER_X+PADDLE_W+BALL_SIZE
        and player_y < ball_y+BALL_SIZE and ball_y < player_y+PADDLE_H):
        ball_dx *= -1
        beep(1200)
    if (AI_X < ball_x < AI_X+PADDLE_W
        and ai_y < ball_y+BALL_SIZE and ball_y < ai_y+PADDLE_H):
        ball_dx *= -1
        beep(900)

    # Score
    if ball_x < 0:
        player_score += 1
        beep(400)
        reset_ball()
    if ball_x > WIDTH:
        ai_score += 1
        beep(200)
        reset_ball()

    # --- Draw ---
    WIN.fill(BG_COLOR)
    pygame.draw.rect(WIN, PADDLE_COLOR, (PLAYER_X, player_y, PADDLE_W, PADDLE_H))
    pygame.draw.rect(WIN, PADDLE_COLOR, (AI_X, ai_y, PADDLE_W, PADDLE_H))
    pygame.draw.rect(WIN, BALL_COLOR, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))
    font = pygame.font.SysFont('Courier New', 24)
    sfc = font.render(f"{ai_score} : {player_score}", True, TEXT_COLOR)
    WIN.blit(sfc, (WIDTH//2 - sfc.get_width()//2, 16))
    pygame.display.flip()
    CLOCK.tick(FPS)

    # --- Game Over Check ---
    if player_score == 5 or ai_score == 5:
        winner = "YOU" if player_score == 5 else "AI"
        game_over(winner)
