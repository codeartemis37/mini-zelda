import pygame
import os
from random import *
from time import *

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Zelda - Vue de Dessus")

# Couleurs
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Chemin des fichiers
ASSETS_DIR = r'C:\Users\Rectorat\Desktop\ \mini zelda izaya\assets'

# Dictionnaire pour stocker les sprites
sprites = {}
sounds = {}

# Charger les images
def load_image(name, filename, size):
    image = pygame.image.load(os.path.join(ASSETS_DIR, filename))
    sprites[name] = pygame.transform.scale(image, size)

def run_sound(channel, sound):
    global sounds
    if not sound in sounds.keys():
        sounds[sound] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, sound))
    #pygame.mixer.set_num_channels(2)
    #pygame.mixer.Channel(channel).play(sounds[sound])

def stop_sound(channel):
    pygame.mixer.Channel(channel).stop()

run_sound(0, 'zelda_theme.mp3')

# Charger tous les sprites
for sprite in ['link_right', 'link_left', 'link_up', 'link_down', 'enemy_up', 'enemy_down', 'enemy_right', 'enemy_left', 'maison', 'bordure', 'pnj']:
    load_image(sprite, f'{sprite}.png', (50, 50))

load_image('sword', 'sword.png', (48, 48))
load_image('health_potion', 'health_potion.png', (48, 48))
load_image('speed_potion', 'speed_potion.png', (48, 48))
load_image('ultracheat_potion', 'ultracheat_potion.png', (48, 48))
load_image('background', 'background.png', (WIDTH * 3, HEIGHT * 3))
# Charger les images des obstacles
load_image('obstacle_mur_pierre', 'obstacle_mur_pierre.png', (100, 100))  # Exemple de taille
load_image('obstacle_mur_lierre', 'obstacle_mur_lierre.png', (50, 50))  # Exemple de taille
load_image('chemin', 'chemin.png', (50, 50))  # Exemple de taille
load_image('bord_de_chemin', 'bord_de_chemin.png', (50, 50))  # Exemple de taille
load_image('arbre_no_collision', 'arbre_no_collision.png', (50, 50))  # Exemple de taille

# Position initiale du joueur et vitesse
max_health_total = 100
player = {
    'x': WIDTH // 2,
    'y': HEIGHT // 2,
    'speed': 5,
    'direction': 'down',
    'health': max_health_total
}

# Liste des obstacles avec leurs images et positions
obstacles = [
    {'rect': pygame.Rect(200, 200, 100, 100), 'image': 'obstacle_mur_pierre'},
    {'rect': pygame.Rect(500, 400, 100, 100), 'image': 'obstacle_mur_pierre'}
] + [
    {'rect': pygame.Rect(800 + ((i+1) * 50), 50, 50, 50), 'image': 'obstacle_mur_lierre'} for i in range(10)
] + [
    {'rect': pygame.Rect(800 + ((i+1) * 50), 550, 50, 50), 'image': 'obstacle_mur_lierre'} for i in range(10)
] + [
    {'rect': pygame.Rect(0, ((i+1) * 50) - 50, 50, 50), 'image': 'bordure'} for i in range(100)
] + [
    {'rect': pygame.Rect(((i+1) * 50) - 50, 0, 50, 50), 'image': 'bordure'} for i in range(100)
]

decorative_elements = [
    {'image': 'arbre_no_collision', 'x': 800 + ((i+1) * 50), 'y': 100} for i in range(10)
] + [
    {'image': 'bord_de_chemin', 'x': 800 + ((i+1) * 50), 'y': 150} for i in range(10)
] + [
    {'image': 'bord_de_chemin', 'x': 800 + ((i+1) * 50), 'y': 200} for i in range(10)
] + [
    {'image': 'chemin', 'x': 800 + ((i+1) * 50), 'y': 250} for i in range(10)
] + [
    {'image': 'chemin', 'x': 800 + ((i+1) * 50), 'y': 300} for i in range(10)
] + [
    {'image': 'chemin', 'x': 800 + ((i+1) * 50), 'y': 350} for i in range(10)
] + [
    {'image': 'bord_de_chemin', 'x': 800 + ((i+1) * 50), 'y': 400} for i in range(10)
] + [
    {'image': 'bord_de_chemin', 'x': 800 + ((i+1) * 50), 'y': 450} for i in range(10)
] + [
    {'image': 'arbre_no_collision', 'x': 800 + ((i+1) * 50), 'y': 500} for i in range(10)
]

portails = [
    {
        'x': 150, 'y': 150, 'new_x': 250, 'new_y': 250, 'icon': 'maison'
    }
]
for element in portails:
    decorative_elements.append({'image': element['icon'], 'x': element['x'], 'y': element['y']})


def create_pnj(x, y, text):
    return {
        'x': x,
        'y': y,
        'rect': pygame.Rect(x, y, 50, 50),
        'text': text + [''],
        'actual_selected': 0,
        'selected': 0
    }

pnjs = [create_pnj(150, 50, ['salut', 'comment tu vas'])]

# Liste des ennemis
enemy_speed = 2

def create_enemy(x, y, health):
    return {
        'rect': pygame.Rect(x, y, 50, 50),
        'health': health,
        'direction': 'down'
    }

enemies = [create_enemy(100, 100, 50), create_enemy(600, 400, 50), create_enemy(500, 500, 50)]

# Variables d'inventaire
inventory = [None] * 9
slot_selected = 0
attacking = False
attack_cooldown = 250
last_attack_time = 0
drops = [{'item': 'sword', 'x': 500, 'y': 500}]

# Liste des drops possibles
possible_drops = ['health_potion', 'speed_potion', 'ultracheat_potion']  # Ajoute d'autres objets si nécessaire

# Font pour le texte
font = pygame.font.Font(None, 36)

# Paramètres de l'inventaire
inventory_width = 9 * 54
inventory_height = 54
inventory_x = (WIDTH - inventory_width) // 2
inventory_y = HEIGHT - inventory_height - 10

def draw_health_bar(x, y, health, max_health, width=200, height=20):
    ratio = health / max_health
    pygame.draw.rect(SCREEN, RED, (x, y, width, height))
    pygame.draw.rect(SCREEN, GREEN, (x, y, width * ratio, height))

def display_text(message, color, size, position):
    text_surface = font.render(message, True, color)
    SCREEN.blit(text_surface, position)

def draw_inventory_background(screen):
    background = pygame.Surface((inventory_width, inventory_height))
    background.fill((64, 64, 64))
    screen.blit(background, (inventory_x, inventory_y))

def draw_inventory_slots(screen):
    for i in range(9):
        slot_x = inventory_x + i * 54
        pygame.draw.rect(screen, (32, 32, 32), (slot_x, inventory_y, 54, 54))
        pygame.draw.rect(screen, (128, 128, 128), (slot_x, inventory_y, 52, 52))
        pygame.draw.rect(screen, (80, 80, 80), (slot_x + 2, inventory_y + 2, 50, 50))

def draw_inventory_items(screen):
    for i, item in enumerate(inventory):
        if item:
            item_x = inventory_x + i * 54 + 3
            item_y = inventory_y + 3
            screen.blit(sprites[item], (item_x, item_y))
    
    mx, my = pygame.mouse.get_pos()
    for i in range(9):
        slot_x = inventory_x + i * 54
        if slot_x < mx < slot_x + 54 and inventory_y < my < inventory_y + 54:
            pygame.draw.rect(screen, (200, 200, 200), (slot_x + 2, inventory_y + 2, 50, 50), 2)

def draw_selected_slot(screen):
    selected_x = inventory_x + slot_selected * 54
    pygame.draw.rect(screen, (255, 255, 255), (selected_x, inventory_y, 54, 54), 2)

def create_drop(x, y):
    drop_item = choice(possible_drops)  # Choisit un objet aléatoire dans possible_drops
    drops.append({'item': drop_item, 'x': x, 'y': y})

def check_attack():
    attack_rect = pygame.Rect(player['x'], player['y'], 70, 70)
    if player['direction'] == 'right':
        attack_rect.x += 50
    elif player['direction'] == 'left':
        attack_rect.x -= 50
    elif player['direction'] == 'up':
        attack_rect.y -= 50
    else:  # down
        attack_rect.y += 50
    
    for enemy in enemies[:]:
        if attack_rect.colliderect(enemy['rect']):
            enemy['health'] -= 10
            if enemy['health'] <= 0:
                # Quand un ennemi meurt, il droppe un objet
                create_drop(enemy['rect'].x, enemy['rect'].y)
                enemies.remove(enemy)

def handle_collisions(rect, obstacles):
    for obstacle in obstacles:
        if rect.colliderect(obstacle['rect']):
            return True
    return False




def draw_player(screen, camera_x, camera_y):
    player_screen_x = player['x'] - camera_x
    player_screen_y = player['y'] - camera_y
    screen.blit(sprites[f'link_{player["direction"]}'], (player_screen_x, player_screen_y))

def draw_enemy(screen, enemy, camera_x, camera_y):
    enemy_screen_x = enemy['rect'].x - camera_x
    enemy_screen_y = enemy['rect'].y - camera_y
    screen.blit(sprites[f'enemy_{enemy["direction"]}'], (enemy_screen_x, enemy_screen_y))

def draw_pnj(screen, pnj, camera_x, camera_y):
    pnj_screen_x = pnj['rect'].x - camera_x
    pnj_screen_y = pnj['rect'].y - camera_y
    screen.blit(sprites['pnj'], (pnj_screen_x, pnj_screen_y))

def draw_drops(screen, camera_x, camera_y):
    for drop in drops:
        drop_screen_x = drop['x'] - camera_x
        drop_screen_y = drop['y'] - camera_y
        screen.blit(sprites[drop['item']], (drop_screen_x, drop_screen_y))

def check_pickup():
    player_rect = pygame.Rect(player['x'], player['y'], 50, 50)
    for drop in drops[:]:
        drop_rect = pygame.Rect(drop['x'], drop['y'], 50, 50)
        if player_rect.colliderect(drop_rect) and None in inventory:
            # Ajouter l'objet dans l'inventaire
            for i in range(len(inventory)):
                if inventory[i] is None:
                    inventory[i] = drop['item']
                    break
            drops.remove(drop)

def actions_e():
     if inventory[slot_selected] == 'health_potion':
         player['health'] = player['health']  + 50
         if player['health'] > max_health_total:
             player['health'] = max_health_total
         inventory[slot_selected] = None
     if inventory[slot_selected] == 'speed_potion':
         player['speed'] += 50
         inventory[slot_selected] = None
     if inventory[slot_selected] == 'ultracheat_potion':
         player['health'] = (player['health'] + 50000000000000000)
         inventory[slot_selected] = None

def actions_a():
    for i, pnj in enumerate(pnjs):
        if round(player['x']/50) == round(pnj['x']/50) and round(pnj['y']/50) == round(pnj['y']/50):
            pnj_screen_x = pnj['rect'].x - camera_x
            pnj_screen_y = pnj['rect'].y - camera_y
            display_text(str(pnj['text'][pnj['actual_selected']]), RED, 16, (pnj_screen_x, pnj_screen_y))
            if pnj['actual_selected']+1 < len(pnj['text']):
                pnjs[i]['actual_selected'] += 1


def draw_decorative_elements(screen, camera_x, camera_y):
    for element in decorative_elements:
        element_screen_x = element['x'] - camera_x
        element_screen_y = element['y'] - camera_y
        screen.blit(sprites[element['image']], (element_screen_x, element_screen_y))

def teleport():
    for portail in portails:
            if round(player['x']/50) == round(portail['x']/50) and round(player['y']/50) == round(portail['y']/50):
                player['x'] = portail['new_x']
                player['y'] = portail['new_y']

# Boucle de jeu principale
running = True
camera_x, camera_y = 0, 0
tick = 0

while running:
    tick +=1
    if tick % 60 == 0:
        enemies.append(create_enemy(100, 100, 50))
    SCREEN.fill(WHITE)
    pygame.time.Clock().tick(60)

    teleport()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                slot_selected = 0
            elif event.key == pygame.K_2:
                slot_selected = 1
            elif event.key == pygame.K_3:
                slot_selected = 2
            elif event.key == pygame.K_4:
                slot_selected = 3
            elif event.key == pygame.K_5:
                slot_selected = 4
            elif event.key == pygame.K_6:
                slot_selected = 5
            elif event.key == pygame.K_7:
                slot_selected = 6
            elif event.key == pygame.K_8:
                slot_selected = 7
            elif event.key == pygame.K_9:
                slot_selected = 8
    for i in range(int(player['speed'])):
        keys = pygame.key.get_pressed()
       
        if keys[pygame.K_LEFT]:
            new_x = player['x'] - 1
            new_rect = pygame.Rect(new_x, player['y'], 50, 50)
            if not handle_collisions(new_rect, obstacles):
                player['x'] = new_x
            player['direction'] = 'left'
        
        if keys[pygame.K_RIGHT]:
            new_x = player['x'] + 1
            new_rect = pygame.Rect(new_x, player['y'], 50, 50)
            if not handle_collisions(new_rect, obstacles):
                player['x'] = new_x
            player['direction'] = 'right'
        
        if keys[pygame.K_UP]:
            new_y = player['y'] - 1
            new_rect = pygame.Rect(player['x'], new_y, 50, 50)
            if not handle_collisions(new_rect, obstacles):
                player['y'] = new_y
            player['direction'] = 'up'
        
        if keys[pygame.K_DOWN]:
            new_y = player['y'] + 1
            new_rect = pygame.Rect(player['x'], new_y, 50, 50)
            if not handle_collisions(new_rect, obstacles):
                player['y'] = new_y
            player['direction'] = 'down'

    camera_x = max(0, min(player['x'] - WIDTH // 2, WIDTH * 2))
    camera_y = max(0, min(player['y'] - HEIGHT // 2, HEIGHT * 2))
    
    for enemy in enemies:
        dx = player['x'] - enemy['rect'].x
        dy = player['y'] - enemy['rect'].y
        dist = (dx**2 + dy**2)**0.5
        
        if dist != 0:
            dx, dy = dx / dist, dy / dist
        
        new_x = enemy['rect'].x + dx * enemy_speed
        new_y = enemy['rect'].y + dy * enemy_speed
        
        new_rect = pygame.Rect(new_x, new_y, 50, 50)
        if not handle_collisions(new_rect, obstacles):
            enemy['rect'].x, enemy['rect'].y = new_x, new_y
        
        if enemy['rect'].colliderect(pygame.Rect(player['x'], player['y'], 50, 50)):
            if inventory[slot_selected] == 'sword':
                player['health'] -= 0.5
    
    current_time = pygame.time.get_ticks()
    if keys[pygame.K_SPACE]:
        if inventory[slot_selected] == 'sword' and current_time - last_attack_time > attack_cooldown:
            attacking = True
            run_sound(1, 'sword.mp3')
            check_attack()
            last_attack_time = current_time
    elif not keys[pygame.K_SPACE]:
        attacking = False
        stop_sound(1)

    SCREEN.blit(sprites['background'], (-camera_x, -camera_y))
    
    draw_decorative_elements(SCREEN, camera_x, camera_y)
    
    for obstacle in obstacles:
        SCREEN.blit(sprites[obstacle['image']], (obstacle['rect'].x - camera_x, obstacle['rect'].y - camera_y))
    
    for enemy in enemies:
        draw_enemy(SCREEN, enemy, camera_x, camera_y)
        draw_health_bar(enemy['rect'].x - camera_x, enemy['rect'].y - camera_y - 30, enemy['health'], 50, width=70, height=10)
    
    for pnj in pnjs:
        draw_pnj(SCREEN, pnj, camera_x, camera_y)
    
    
    if keys[pygame.K_a]:
        actions_a()
        while pygame.key.get_pressed()[pygame.K_a]:
            pygame.display.flip()
            pygame.time.delay(10)
    if keys[pygame.K_e]:
        actions_e()
    
    draw_drops(SCREEN, camera_x, camera_y)
    draw_player(SCREEN, camera_x, camera_y)
    draw_health_bar(inventory_x, inventory_y - 40, player['health'], max_health_total, width=inventory_width)

    
    draw_inventory_background(SCREEN)
    draw_inventory_slots(SCREEN)
    draw_inventory_items(SCREEN)
    draw_selected_slot(SCREEN)
    
    pygame.display.flip()
    
    check_pickup()
    
    if player['health'] <= 0:
        SCREEN.fill(WHITE)
        display_text("Game Over", RED, 72, (WIDTH // 2 - 150, HEIGHT // 2 - 30))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

pygame.quit()
