import pygame
import sys
import random

pygame.init()

# ----- Fenêtre -----
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rumble in the Jungle")

# ----- Couleurs -----
BLUE = (135, 206, 250)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
PURPLE = (160, 32, 240)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRIS = (100, 100, 100)
VERT = (50, 205, 50)
ROUGE = (200, 0, 0)
BLEU = (0, 120, 255)

# ----- FPS -----
clock = pygame.time.Clock()
FPS = 60

# ----- Joueur -----
player_width, player_height = 50, 70
player_start_x = 100
player_start_y = HEIGHT - player_height - 100

# ----- Plateformes -----
platforms = [
    pygame.Rect(0, HEIGHT - 30, WIDTH, 30),
    pygame.Rect(200, 450, 120, 20),
    pygame.Rect(400, 350, 150, 20),
    pygame.Rect(600, 250, 100, 20),
]

# ----- Points de vie -----
MAX_HEALTH = 3

def draw_hearts(surface, health):
    for i in range(health):
        pygame.draw.rect(surface, RED, (WIDTH - (i + 1) * 40 - 10, HEIGHT - 40, 30, 30))

def reset_game():
    return {
        "player_rect": pygame.Rect(player_start_x, player_start_y, player_width, player_height),
        "player_vel_x": 0,
        "player_vel_y": 0,
        "on_ground": False,
        "enemy_rect": pygame.Rect(500, HEIGHT - 60 - 100, 50, 60),
        "enemy_vel_x": 2,
        "enemy_vel_y": 0,
        "enemy_on_ground": False,
        "jump_timer": 0,
        "current_health": MAX_HEALTH,
        "game_over": False
    }

# ----- Écran de menu -----
titre_font = pygame.font.SysFont("comicsans", 64)
bouton_font = pygame.font.SysFont("comicsans", 40)
niveau_font = pygame.font.SysFont("comicsans", 30)

bouton_play = pygame.Rect(300, 420, 200, 60)
bouton_facile = pygame.Rect(250, 280, 120, 60)
bouton_difficile = pygame.Rect(430, 280, 120, 60)
niveau_selectionne = "Facile"

def dessiner_menu():
    SCREEN.fill(BLACK)
    titre = titre_font.render("Rumble in the Jungle", True, WHITE)
    SCREEN.blit(titre, (WIDTH // 2 - titre.get_width() // 2, 80))

    pygame.draw.rect(SCREEN, BLEU, bouton_play)
    txt_play = bouton_font.render("Jouer", True, WHITE)
    SCREEN.blit(txt_play, (bouton_play.x + 50, bouton_play.y + 10))

    pygame.draw.rect(SCREEN, VERT if niveau_selectionne == "Facile" else GRIS, bouton_facile)
    txt_facile = bouton_font.render("Facile", True, BLACK)
    SCREEN.blit(txt_facile, (bouton_facile.x + 5, bouton_facile.y + 10))

    pygame.draw.rect(SCREEN, ROUGE if niveau_selectionne == "Difficile" else GRIS, bouton_difficile)
    txt_diff = bouton_font.render("Difficile", True, BLACK)
    SCREEN.blit(txt_diff, (bouton_difficile.x + 0, bouton_difficile.y + 10))

    txt_niveau = niveau_font.render(f"Niveau sélectionné : {niveau_selectionne}", True, WHITE)
    SCREEN.blit(txt_niveau, (WIDTH // 2 - txt_niveau.get_width() // 2, 360))

    pygame.display.update()

# ----- Boucle de menu -----
dans_menu = True
while dans_menu:
    dessiner_menu()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if bouton_facile.collidepoint((x, y)):
                niveau_selectionne = "Facile"
            elif bouton_difficile.collidepoint((x, y)):
                niveau_selectionne = "Difficile"
            elif bouton_play.collidepoint((x, y)):
                dans_menu = False

# ----- Lancement du jeu -----
state = reset_game()
game_running = True
while game_running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

    if state["game_over"] and keys[pygame.K_r]:
        state = reset_game()
        dans_menu = True
        # Revenir au menu
        while dans_menu:
            dessiner_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if bouton_facile.collidepoint((x, y)):
                        niveau_selectionne = "Facile"
                    elif bouton_difficile.collidepoint((x, y)):
                        niveau_selectionne = "Difficile"
                    elif bouton_play.collidepoint((x, y)):
                        dans_menu = False
        continue

    if not state["game_over"]:
        # Contrôles joueur : flèches
        state["player_vel_x"] = 0
        if keys[pygame.K_LEFT]:
            state["player_vel_x"] = -5
        if keys[pygame.K_RIGHT]:
            state["player_vel_x"] = 5
        if keys[pygame.K_UP] and state["on_ground"]:
            state["player_vel_y"] = -15
            state["on_ground"] = False

        # Gravité + déplacement joueur
        state["player_vel_y"] += 0.8
        state["player_rect"].x += state["player_vel_x"]
        state["player_rect"].y += state["player_vel_y"]

        # Collision plateformes joueur
        state["on_ground"] = False
        for platform in platforms:
            if state["player_rect"].colliderect(platform):
                if state["player_vel_y"] > 0 and state["player_rect"].bottom <= platform.bottom:
                    state["player_rect"].bottom = platform.top
                    state["player_vel_y"] = 0
                    state["on_ground"] = True

        # Ennemi déplacement
        state["enemy_rect"].x += state["enemy_vel_x"]
        if state["enemy_rect"].left <= 0 or state["enemy_rect"].right >= WIDTH:
            state["enemy_vel_x"] *= -1

        # Ennemi saut aléatoire
        state["jump_timer"] += 1
        if state["jump_timer"] > 60 and state["enemy_on_ground"]:
            if random.random() < 0.1:
                state["enemy_vel_y"] = -12
            state["jump_timer"] = 0

        # Gravité ennemi
        state["enemy_vel_y"] += 0.8
        state["enemy_rect"].y += state["enemy_vel_y"]
        state["enemy_on_ground"] = False
        for platform in platforms:
            if state["enemy_rect"].colliderect(platform):
                if state["enemy_vel_y"] > 0 and state["enemy_rect"].bottom <= platform.bottom:
                    state["enemy_rect"].bottom = platform.top
                    state["enemy_vel_y"] = 0
                    state["enemy_on_ground"] = True

        # Collision joueur/ennemi
        if state["player_rect"].colliderect(state["enemy_rect"]):
            if state["current_health"] > 0:
                state["current_health"] -= 1
                pygame.time.delay(300)

        if state["current_health"] <= 0:
            state["game_over"] = True

    # ----- Affichage -----
    SCREEN.fill(BLUE)
    for platform in platforms:
        pygame.draw.rect(SCREEN, BROWN, platform)

    pygame.draw.rect(SCREEN, GREEN, state["player_rect"])
    pygame.draw.rect(SCREEN, PURPLE, state["enemy_rect"])
    draw_hearts(SCREEN, state["current_health"])

    if state["game_over"]:
        font = pygame.font.SysFont(None, 72)
        text = font.render("💀 GAME OVER 💀", True, WHITE)
        SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
        retry_text = pygame.font.SysFont(None, 36).render("Appuie sur R pour revenir au menu", True, WHITE)
        SCREEN.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
