# Combined 5 worlds, 3 stages each with Smash Bros Brawl vibes
import pygame, sys, random, math

# -----------------------------
# SUPER MARIO‑STYLE CONSTANTS
# -----------------------------
WIDTH, HEIGHT = 800, 480       # window size
TILE          = 32             # size of one tile (px)
FPS           = 60
GRAVITY       = 0.7            # closer to NES SMB1 gravity
JUMP_VEL      = -12            # initial jump velocity
GROUND_ACCEL  = 0.6            # horizontal acceleration when on ground
AIR_ACCEL     = 0.3            # horizontal acceleration when in air
FRICTION      = 0.5            # horizontal deceleration when no input
MAX_XSPEED    = 5              # cap horizontal speed
SCROLL_EDGE   = WIDTH // 3     # start scrolling when the player is this far from the screen edge

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Mario – Worlds & Stages")
clock = pygame.time.Clock()

# -----------------------------
# COLOUR PALETTE (dynamic per world)
# -----------------------------
BASE_PALETTES = [
    {"sky": (92, 148, 252), "ground": (146, 144, 255)},   # World 1
    {"sky": (255, 200, 200), "ground": (255, 150, 150)},   # World 2
    {"sky": (200, 255, 200), "ground": (150, 255, 150)},   # World 3
    {"sky": (200, 200, 255), "ground": (150, 150, 255)},   # World 4
    {"sky": (255, 255, 200), "ground": (255, 255, 150)},   # World 5
]
EXTRA_COLORS = {"brick": (198, 92, 16), "outline": (0, 0, 0), "player": (255, 0, 0), "enemy": (206, 169, 101), "shadow": (0, 0, 0, 90)}

# -----------------------------
# 5 WORLDS × 3 STAGES EACH
# Smash‑style variant layouts
# Legend: = ground, # brick, g Goomba, F flag
# -----------------------------
BASE_STAGE = [
    "................................................................................................", 
    "................................................................................................", 
    "................................................................................................", 
    ".........................g......................g...............................................", 
    "..............................................#####.............................................", 
    ".......................#####.........................#####.......................................", 
    ".....................................###...................................F.....................", 
    "=============================    ===============================     ============================"
]

WORLDS = []
for w in range(5):
    stages = []
    for s in range(3):
        # copy base and shift Goombas & platforms randomly
        lvl = [list(row) for row in BASE_STAGE]
        # random tweaks
        for i in range(3):
            ty = random.randint(2, 5)
            tx = random.randint(10, len(lvl[0]) - 10)
            lvl[ty][tx] = '#'
        stages.append([''.join(r) for r in lvl])
    WORLDS.append(stages)

SOLIDS = {"=", "#"}

def tile_at(level, tx, ty):
    if 0 <= ty < len(level) and 0 <= tx < len(level[ty]): return level[ty][tx]
    return "."

def rect_for_tile(tx, ty):
    return pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)

class Player:
    def __init__(self, x, y):
        self.x, self.y = x*TILE, y*TILE
        self.vx, self.vy = 0, 0
        self.on_ground, self.alive = False, True
    @property
    def rect(self): return pygame.Rect(self.x, self.y, TILE, TILE*2)
    def handle_input(self):
        keys = pygame.key.get_pressed()
        ax = 0
        if keys[pygame.K_LEFT]: ax = - (GROUND_ACCEL if self.on_ground else AIR_ACCEL)
        elif keys[pygame.K_RIGHT]: ax = (GROUND_ACCEL if self.on_ground else AIR_ACCEL)
        else:
            if self.vx>0: self.vx = max(0, self.vx - FRICTION)
            elif self.vx<0: self.vx = min(0, self.vx + FRICTION)
        self.vx = max(-MAX_XSPEED, min(MAX_XSPEED, self.vx + ax))
        if self.on_ground and keys[pygame.K_z]: self.vy, self.on_ground = JUMP_VEL, False
    def physics_step(self, level):
        self.vy = min(10, self.vy + GRAVITY)
        self.x += self.vx; self._hcoll(level)
        self.y += self.vy; self._vcoll(level)
    def _hcoll(self, level):
        r = self.rect; tx1, tx2 = r.left//TILE, r.right//TILE
        for ty in range(r.top//TILE, (r.bottom-1)//TILE+1):
            for tx in (tx1, tx2):
                if tile_at(level, tx, ty) in SOLIDS:
                    trect = rect_for_tile(tx, ty)
                    if r.colliderect(trect):
                        self.x = trect.left - r.width if self.vx>0 else trect.right
                        self.vx=0
    def _vcoll(self, level):
        self.on_ground=False; r=self.rect
        for tx in range(r.left//TILE, r.right//TILE+1):
            for ty in (r.top//TILE, (r.bottom-1)//TILE):
                c=tile_at(level, tx, ty)
                if c in SOLIDS and r.colliderect(rect_for_tile(tx,ty)):
                    trect=rect_for_tile(tx,ty)
                    if self.vy>0:
                        self.y, self.vy, self.on_ground = trect.top-r.height, 0, True
                    else:
                        self.y, self.vy = trect.bottom, 0
    def stomp(self, e): e.alive=False; self.vy=JUMP_VEL/1.5
    def draw(self, camx, pal):
        body=self.rect.move(-camx,0)
        pygame.draw.rect(screen, pal['player'], body)
        srect=pygame.Rect(body.left+4, body.bottom-4, TILE-8,6)
        surf=pygame.Surface(srect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(surf, pal['shadow'], surf.get_rect())
        screen.blit(surf, srect)

class Goomba:
    def __init__(self,x,y): self.x,self.y,self.vx, self.alive, self.squash= x*TILE,y*TILE,-1,True,0
    @property
    def rect(self): return pygame.Rect(self.x,self.y+TILE,TILE,TILE)
    def update(self,lev):
        if not self.alive: self.squash-=1; return
        ahead=int((self.x+(self.vx>0)*TILE+(self.vx<0))//TILE)
        foot=(self.y+2*TILE)//TILE
        if tile_at(lev,ahead,foot) not in SOLIDS or tile_at(lev,ahead,foot-1) in SOLIDS: self.vx*=-1
        self.x+=self.vx
    def draw(self,camx,pal):
        if not self.alive and self.squash<=0: return
        r=self.rect.move(-camx,0)
        if self.alive: pygame.draw.rect(screen,pal['enemy'],r)
        else: pygame.draw.rect(screen,pal['enemy'],(r.left,r.bottom-6,r.width,6))

# Rendering

def draw_tile(c,sx,sy,pal):
    if c=='=': pygame.draw.rect(screen,pal['ground'],(sx,sy,TILE,TILE))
    elif c=='#': pygame.draw.rect(screen,EXTRA_COLORS['brick'],(sx,sy,TILE,TILE))
    elif c=='F':
        pygame.draw.line(screen,pal['outline'],(sx+TILE//2,sy-6*TILE),(sx+TILE//2,sy+TILE),2)
        pygame.draw.polygon(screen,pal['outline'],[(sx+TILE//2,sy-5*TILE),(sx+TILE//2+TILE,sy-4.5*TILE),(sx+TILE//2,sy-4*TILE)])

def draw_level(level,camx,pal):
    screen.fill(pal['sky'])
    for y,row in enumerate(level):
        for x,c in enumerate(row):
            if c!='.': draw_tile(c,x*TILE-camx,y*TILE,pal)

# Main

def run_all():
    world_idx, stage_idx = 0, 0
    while world_idx< len(WORLDS):
        level = WORLDS[world_idx][stage_idx]
        player = Player(2,5)
        enemies = [Goomba(x,y) for y,row in enumerate(level) for x,c in enumerate(row) if c=='g']
        camx=0
        pal = {**BASE_PALETTES[world_idx], **EXTRA_COLORS}
        running=True
        while running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            player.handle_input(); player.physics_step(level)
            for e in enemies: e.update(level)
            for e in enemies:
                if e.alive and player.rect.colliderect(e.rect):
                    if player.vy>0 and player.rect.bottom - e.rect.top < TILE: player.stomp(e); e.squash=FPS//2
                    else: running=False
            if player.x-camx>WIDTH-SCROLL_EDGE: camx=player.x-(WIDTH-SCROLL_EDGE)
            elif player.x-camx<SCROLL_EDGE: camx=player.x-SCROLL_EDGE
            camx=max(0,camx)
            # level end
            cx,cy=int(player.rect.centerx//TILE), int(player.rect.centery//TILE)
            if tile_at(level,cx,cy)=='F':
                running=False; win=True
            else: win=False
            draw_level(level,camx,pal)
            for e in enemies: e.draw(camx,pal)
            player.draw(camx,pal)
            pygame.display.flip(); clock.tick(FPS)
        # end stage loop
        if win:
            stage_idx+=1
            if stage_idx>=3:
                world_idx+=1; stage_idx=0
                if world_idx>=len(WORLDS):
                    pygame.font.init(); f=pygame.font.SysFont("Arial",48)
                    txt=f.render("GAME COMPLETE!",True,pal['outline'])
                    screen.blit(txt,(WIDTH//2-txt.get_width()//2,HEIGHT//2-txt.get_height()//2)); pygame.display.flip(); pygame.time.wait(3000)
                    return
            else:
                # stage clear message
                pygame.font.init(); f=pygame.font.SysFont("Arial",48)
                msg=f.render(f"WORLD {world_idx+1}-{stage_idx+1}",True,pal['outline'])
                screen.blit(msg,(WIDTH//2-msg.get_width()//2,HEIGHT//2-msg.get_height()//2)); pygame.display.flip(); pygame.time.wait(2000)
        else:
            # death
            pygame.font.init(); f=pygame.font.SysFont("Arial",48)
            msg=f.render("GAME OVER",True,pal['outline']); screen.blit(msg,(WIDTH//2-msg.get_width()//2,HEIGHT//2-msg.get_height()//2)); pygame.display.flip(); pygame.time.wait(2500)
            return

if __name__ == "__main__": run_all()
