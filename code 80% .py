import pygame
import sys
from pytmx.util_pygame import load_pygame
import random

# --- Init ---
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("🌴 Rumble in the Jungle")
clock = pygame.time.Clock()
FPS = 60

# --- Couleurs ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# --- Joueur ---
player_img = pygame.Surface((18, 24))
player_img.fill(RED)
player_rect = pygame.Rect(67 * 18, 100, 18, 24)
player_vel = pygame.Vector2(0, 0)
gravity = 0.8
on_ground = False

# --- Map ---
tmx_data = load_pygame("map/map.tmx")
tile_width = tmx_data.tilewidth
tile_height = tmx_data.tileheight

# Scroll
scroll_x = 0
scroll_y = 0

# --- Plateformes solides ---
solid_tiles = []
for layer in tmx_data.visible_layers:
    if hasattr(layer, "tiles") and layer.name == "map":
        for x, y, gid in layer:
            if gid != 0:
                tile_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                solid_tiles.append(tile_rect)

# --- Crocodiles ---
def reset_crocodiles():
    return [
        pygame.Rect(287 * tile_width, 40 * tile_height, tile_width, tile_height),
        pygame.Rect(178 * tile_width, 38 * tile_height, tile_width, tile_height),
        pygame.Rect(186 * tile_width, 38 * tile_height, tile_width, tile_height),
        pygame.Rect(194 * tile_width, 38 * tile_height, tile_width, tile_height),
        pygame.Rect(364 * tile_width, 40 * tile_height, tile_width, tile_height),
        pygame.Rect(359 * tile_width, 40 * tile_height, tile_width, tile_height),
        pygame.Rect(360 * tile_width, 40 * tile_height, tile_width, tile_height),
        pygame.Rect(238 * tile_width, 40 * tile_height, tile_width, tile_height),
    ]

crocodiles = reset_crocodiles()

# --- Singes ---
class Monkey:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x * tile_width, y * tile_height)
        self.projectiles = []
        self.ready = False  # prêt à tirer

    def shoot(self):
        self.projectiles.append({
            "rect": pygame.Rect(self.pos.x + tile_width // 2, self.pos.y + tile_height // 2, 10, 10),
            "vel": pygame.Vector2(-4, -5)
        })

    def update(self):
        for banana in self.projectiles:
            banana["vel"].y += 0.3
            banana["rect"].x += banana["vel"].x
            banana["rect"].y += banana["vel"].y
        self.projectiles = [b for b in self.projectiles if b["rect"].x > 0 and b["rect"].y < HEIGHT]

    def draw(self, surface):
        pygame.draw.rect(surface, (139, 69, 19), (self.pos.x - scroll_x, self.pos.y - scroll_y, tile_width, tile_height))
        for banana in self.projectiles:
            pygame.draw.circle(surface, (255, 255, 0), (banana["rect"].x - scroll_x, banana["rect"].y - scroll_y), 5)

monkeys = [
    Monkey(320, 25),
    Monkey(304, 26),
    Monkey(310, 21),
    Monkey(332, 22)
]

current_monkey_index = 0
monkey_timer = 0

# --- Serpents (ennemis rampants qui se déplacent sur les plateformes) ---
class Snake:
    def __init__(self, path_tiles):
        self.path = [pygame.Vector2(x * tile_width, y * tile_height) for x, y in path_tiles]
        self.index = 0
        self.forward = True
        self.rect = pygame.Rect(self.path[0].x, self.path[0].y, tile_width, tile_height)
        self.speed = 1

    def update(self):
        target = self.path[self.index]
        dx = target.x - self.rect.x
        dy = target.y - self.rect.y

        if abs(dx) > self.speed:
            self.rect.x += self.speed if dx > 0 else -self.speed
        elif abs(dy) > self.speed:
            self.rect.y += self.speed if dy > 0 else -self.speed
        else:
            if self.forward:
                if self.index + 1 < len(self.path):
                    self.index += 1
                else:
                    self.forward = False
                    self.index -= 1
            else:
                if self.index - 1 >= 0:
                    self.index -= 1
                else:
                    self.forward = True
                    self.index += 1

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 165, 0), (self.rect.x - scroll_x, self.rect.y - scroll_y, self.rect.width, self.rect.height))

snakes = [
    Snake([(100, 34), (101, 34), (102, 34), (103, 33), (104, 33), (105, 33), (106, 32), (107, 32), (108, 32), (109, 32), (110, 32), (111, 32), (112, 32), (113, 32), (114, 32), (115, 32)]),
    Snake([(166, 37), (167, 37), (168, 37), (170, 37), (169, 37), (170, 37), (171, 37), (172, 37), (173, 37)]),
    Snake([(198, 37), (199, 37), (200, 37), (201, 37), (202, 36), (203, 36), (204, 35), (205, 35), (206, 35), (207, 35), (208, 35), (209, 35), (210, 35), (211, 35), (212, 35), (213, 35), (214, 35), (215, 35), (216, 35), (217, 35), (218, 35), (219, 35), (220, 35), (221, 36), (222, 36), (223, 36), (224, 37), (225, 37), (226, 38), (227, 39), (228, 39), (229, 39), (230, 39), (231, 39), (232, 39), (233, 39), (234, 39)]),
    Snake([(234, 39), (233, 39), (232, 39), (231, 39), (230, 39), (229, 39), (228, 39), (227, 39),(226, 38), (225, 37), (224, 37), (223, 36), (222, 36), (221, 36), (220, 35), (219, 35),(218, 35), (217, 35), (216, 35), (215, 35), (214, 35), (213, 35), (212, 35), (211, 35),(210, 35), (209, 35), (208, 35), (207, 35), (206, 35), (205, 35), (204, 35), (203, 36),(202, 36), (201, 37), (200, 37), (199, 37), (198, 37)]),
]

class GorillaBoss:
    def __init__(self, path_tiles):
        if not path_tiles:
            raise ValueError("Le chemin du gorille est vide.")
        self.path = [pygame.Vector2(x * tile_width, y * tile_height) for x, y in path_tiles]
        self.pos = self.path[0].copy()
        self.vel = pygame.Vector2(0, 0)
        self.gravity = 0.8
        self.on_ground = True
        self.timer = 0
        self.width = int(tile_width * 1.7)
        self.height = int(tile_height * 1.7)
        self.rect = pygame.Rect(int(self.pos.x), int(self.pos.y), self.width, self.height)
        self.target = self.pos.copy()
        self.jump_duration = 40
        self.mode = "walk"  # ou "jump"
        self.walk_direction = 0  # -1 pour gauche, 1 pour droite

    def update(self, dt):
        # Appliquer la gravité
        self.vel.y += self.gravity
        self.vel.y = min(self.vel.y, 20)
        self.pos.y += self.vel.y

        # Appliquer déplacement horizontal
        self.pos.x += self.vel.x

        # Sécurité anti-chute
        if self.pos.y > 2000:
            self.pos = self.path[0].copy()
            self.vel = pygame.Vector2(0, 0)
            self.on_ground = True

        # Atterrissage
        if self.vel.y > 0 and self.pos.y >= self.target.y:
            self.pos.y = self.target.y
            self.vel.y = 0
            self.on_ground = True
            if self.mode == "jump":
                self.vel.x = 0  # stop horizontal après saut

        # Timer pour changer de mode
        self.timer += dt
        if self.timer > 1500 and self.on_ground:
            self.timer = 0
            self.mode = random.choice(["walk", "jump"])
            if self.mode == "walk":
                self.walk_direction = random.choice([-1, 1])
                self.vel.x = self.walk_direction * 2  # vitesse de marche
            elif self.mode == "jump":
                self.target = random.choice(self.path)
                dx = self.target.x - self.pos.x
                dy = self.target.y - self.pos.y
                self.vel.x = dx / self.jump_duration
                self.vel.y = dy / self.jump_duration - 0.5 * self.gravity * self.jump_duration
                self.on_ground = False

        # Limiter le boss à sa zone
        min_x = min(p.x for p in self.path)
        max_x = max(p.x for p in self.path)
        if self.pos.x < min_x:
            self.pos.x = min_x
            self.vel.x = abs(self.vel.x)
        elif self.pos.x + self.width > max_x + tile_width:
            self.pos.x = max_x + tile_width - self.width
            self.vel.x = -abs(self.vel.x)

        # Mise à jour du rect
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            (80, 40, 20),
            (self.rect.x - scroll_x, self.rect.y - scroll_y, self.width, self.height)
        )

# --- Appel du gorille comme pour les serpents ---
gorilla_bosses = [
    GorillaBoss([(338, 30), (339, 30), (340, 30), (341, 30), (342, 30), (343, 30), (344, 30), (345, 30),
                  (346, 30), (347, 30), (348, 30), (349, 30), (350, 30), (351, 30), (352, 30), (353, 30),
                  (354, 30), (355, 30)])
]


# --- Points de vie ---
invincible = False
invincibility_timer = 0
hearts = 3
heart_img = pygame.Surface((20, 20))
heart_img.fill((255, 0, 0))

# --- Boucle principale ---
running = True
font = pygame.font.SysFont(None, 72)
game_over = False
crocodiles = reset_crocodiles()
fullscreen = True

while running:
    dt = clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((800, 600))
                    WIDTH, HEIGHT = 800, 600
            elif game_over:
                player_rect.x, player_rect.y = 67 * 18, 100
                player_vel = pygame.Vector2(0, 0)
                crocodiles = reset_crocodiles()
                game_over = False
                hearts = 3
                invincible = False

    if not game_over:
        # --- Contrôles ---
        player_vel.x = 0
        if keys[pygame.K_q]:
            player_vel.x = -4
        if keys[pygame.K_d]:
            player_vel.x = 4
        if keys[pygame.K_SPACE] and on_ground:
            player_vel.y = -15
            on_ground = False

        # --- Physique ---
        if invincible:
            invincibility_timer -= dt
            if invincibility_timer <= 0:
                invincible = False
        player_vel.y += gravity
        player_rect.y += player_vel.y

        # --- Collision verticale ---
        on_ground = False
        for tile in solid_tiles:
            if player_rect.colliderect(tile):
                if player_vel.y > 0:
                    player_rect.bottom = tile.top
                    player_vel.y = 0
                    on_ground = True
                elif player_vel.y < 0:
                    player_rect.top = tile.bottom
                    player_vel.y = 0

        # --- Crocodiles ---
        for croc in crocodiles[:]:
            if player_rect.colliderect(croc) and player_vel.y > 0:
                crocodiles.remove(croc)
                player_rect.bottom = croc.top
                player_vel.y = 0
                on_ground = True

        # --- Déplacement horizontal ---
        player_rect.x += player_vel.x
        for tile in solid_tiles:
            if player_rect.colliderect(tile):
                if player_vel.x > 0:
                    player_rect.right = tile.left
                elif player_vel.x < 0:
                    player_rect.left = tile.right

        if player_rect.y - scroll_y > HEIGHT + 200 or hearts <= 0:
            game_over = True

        # --- Scrolling ---
        margin_x = WIDTH // 2 - 100
        margin_y = HEIGHT // 2 - 30

        if player_rect.centerx - scroll_x < margin_x:
            scroll_x = max(0, player_rect.centerx - margin_x)
        elif player_rect.centerx - scroll_x > WIDTH - margin_x:
            scroll_x = min(tmx_data.width * tile_width - WIDTH, player_rect.centerx - (WIDTH - margin_x))

        if player_rect.centery - scroll_y < margin_y:
            scroll_y = max(0, player_rect.centery - margin_y)
        elif player_rect.centery - scroll_y > HEIGHT - margin_y:
            scroll_y = min(tmx_data.height * tile_height - HEIGHT, player_rect.centery - (HEIGHT - margin_y))

    # --- Affichage ---
    screen.fill((0, 0, 0))

    for layer in tmx_data.visible_layers:
        if hasattr(layer, "tiles"):
            x_min = max(0, scroll_x // tile_width)
            x_max = min(tmx_data.width, (scroll_x + WIDTH) // tile_width + 1)
            y_min = max(0, scroll_y // tile_height)
            y_max = min(tmx_data.height, (scroll_y + HEIGHT) // tile_height + 1)

            for x in range(x_min, x_max):
                for y in range(y_min, y_max):
                    gid = layer.data[y][x]
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * tile_width - scroll_x, y * tile_height - scroll_y))

    for croc in crocodiles:
        pygame.draw.rect(screen, (0, 255, 0), (croc.x - scroll_x, croc.y - scroll_y, croc.width, croc.height))

# --- Tir séquentiel des singes ---
    monkey_timer += dt
    if monkey_timer > 500:  # 1 seconde entre chaque tir de singe
        monkeys[current_monkey_index].shoot()
        current_monkey_index = (current_monkey_index + 1) % len(monkeys)
        monkey_timer = 0

    for monkey in monkeys:
        monkey.update()
        for banana in monkey.projectiles:
            if player_rect.colliderect(banana["rect"]) and not invincible:
                hearts -= 1
                invincible = True
                invincibility_timer = 2000
                player_vel = pygame.Vector2(0, 0)
                break
        monkey.draw(screen)

    for snake in snakes:
        if player_rect.colliderect(snake.rect) and not invincible:
            hearts -= 1
            invincible = True
            invincibility_timer = 2000
            # dégâts du serpent sans retour au spawn
            player_vel = pygame.Vector2(0, 0)
            break
        snake.update()
        snake.draw(screen)

   # --- Update gorilles ---
    for gorilla in gorilla_bosses:
        if not game_over:
            gorilla.update(dt)
        if player_rect.colliderect(gorilla.rect) and not invincible:
            hearts -= 1
            invincible = True
            invincibility_timer = 2000
            player_vel = pygame.Vector2(0, 0)

    # --- Draw gorilles ---
    for gorilla in gorilla_bosses:
        gorilla.draw(screen)

    if not game_over:
        if not invincible or (pygame.time.get_ticks() // 200) % 2 == 0:
            screen.blit(player_img, (player_rect.x - scroll_x, player_rect.y - scroll_y))

    if game_over:
        text = font.render("GAME OVER", True, WHITE)
        screen.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT // 2 - 50))
        subtext = pygame.font.SysFont(None, 36).render("Appuie sur une touche pour recommencer", True, WHITE)
        screen.blit(subtext, ((WIDTH - subtext.get_width()) // 2, HEIGHT // 2 + 20))

    for i in range(hearts):
        screen.blit(heart_img, (10 + i * 25, 10))

    fps_counter = pygame.font.SysFont(None, 24)
    screen.blit(fps_counter.render(str(int(clock.get_fps())), True, (255, 255, 0)), (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
