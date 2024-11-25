import pygame
import random
import heapq
import os
import time
import subprocess

# Configurations de base 
SCREEN_WIDTH = 600  # Largeur de l'écran
SCREEN_HEIGHT = 400  # Hauteur de l'écran
SIDE_PANEL_WIDTH = 200
FONT_SIZE = 20

# Chemin de base des ressources
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# Path des images et des fonts
LOGO_IMAGE_PATH = os.path.join(ASSETS_DIR, 'icons', 'lol.png') 
FOOTER_IMAGE_PATH = os.path.join(ASSETS_DIR, 'backgrounds', 'grille.png')
FRAME_IMAGE_PATH = os.path.join(ASSETS_DIR, 'backgrounds', 'cadre.png')
ARCADE_FONT_PATH = os.path.join(ASSETS_DIR, 'fonts', 'arcade.ttf')

# Initialisation des couleurs
BACKGROUND_COLOR = (14, 22, 35)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
BUTTON_COLOR = (200, 200, 200)
DEBUG_COLOR = (10, 36, 254)

# Initialisation de Pygame
pygame.init()
font = pygame.font.Font(None, FONT_SIZE)
arcade_font = pygame.font.Font(ARCADE_FONT_PATH, 11)
arcade_font_small =pygame.font.Font(ARCADE_FONT_PATH, 8)
small_font = pygame.font.Font(None, FONT_SIZE // 2)

# -------------------------------------------------- Classe principale du puzzle --------------------------------------------
class NPuzzle:
    def __init__(self, grid_size, swap_after=None):
        self.grid_size = grid_size
        self.swap_after = swap_after
        puzzle_area_width = SCREEN_WIDTH - SIDE_PANEL_WIDTH
        self.tile_size = min(puzzle_area_width, SCREEN_HEIGHT) // grid_size
        self.grid = self.generate_solvable_puzzle()
        self.empty_pos = self.find_empty_tile()
        self.total_moves = 0  # Compteur total de mouvements
        self.move_count = 0   # Compteur pour le swap
        self.swap_mode = False

    def generate_solvable_puzzle(self):
        nums = list(range(self.grid_size ** 2))
        random.shuffle(nums)
        while not self.is_solvable(nums):
            random.shuffle(nums)
        return [nums[i:i + self.grid_size] for i in range(0, len(nums), self.grid_size)]

    def is_solvable(self, tiles):
        inversions = sum(1 for i in range(len(tiles)) for j in range(i + 1, len(tiles)) if tiles[i] and tiles[j] and tiles[i] > tiles[j])
        return inversions % 2 == 0

    def find_empty_tile(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == 0:
                    return i, j

    def move(self, direction):
        if self.swap_after and self.move_count >= self.swap_after:
            self.swap_mode = True
            
        x, y = self.empty_pos
        dx, dy = direction
        new_x, new_y = x + dx, y + dy
        
        #SWAP
        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            if self.swap_mode:
                # En mode swap, on peut échanger n'importe quelles tuiles adjacentes
                self.grid[x][y], self.grid[new_x][new_y] = self.grid[new_x][new_y], self.grid[x][y]
                self.swap_mode = False  # Désactiver le mode swap après utilisation
                self.move_count = 0  # Réinitialiser le compteur de déplacements

            else:
                # Mode normal : seulement la case vide peut être déplacée
                if self.grid[x][y] == 0:
                    self.grid[x][y], self.grid[new_x][new_y] = self.grid[new_x][new_y], self.grid[x][y]
                
            self.empty_pos = (new_x, new_y)
            self.total_moves += 1  # Incrémenter le total
            self.move_count += 1   # Incrémenter pour le swap
            
            # Activer le mode swap après le nombre requis de déplacements
            if self.swap_after and self.move_count >= self.swap_after:
                self.swap_mode = True

    def is_solved(self):
        expected = list(range(1, self.grid_size ** 2)) + [0]
        return self.grid == [expected[i:i + self.grid_size] for i in range(0, len(expected), self.grid_size)]

# ------------------------------------------------- Algorithme de résolution automatique  A*------------------------------------------
def solve_puzzle(grid):
    
    def get_position(value, grid_size):
        if value == 0:
            return grid_size - 1, grid_size - 1
        value -= 1
        return value // grid_size, value % grid_size

    # Distance de manhattan
    def manhattan_distance(grid):
        grid_size = len(grid)
        distance = 0
        for i in range(grid_size):
            for j in range(grid_size):
                value = grid[i][j]
                if value != 0:
                    target_x, target_y = get_position(value, grid_size)
                    distance += abs(i - target_x) + abs(j - target_y)
        return distance

    # Conflit lineaire
    def get_linear_conflicts(grid):
        grid_size = len(grid)
        conflicts = 0
        
        # Verification des lignes
        for i in range(grid_size):
            for j in range(grid_size):
                if grid[i][j] == 0:
                    continue
                target_x, _ = get_position(grid[i][j], grid_size)
                if target_x == i:
                    for k in range(j + 1, grid_size):
                        if grid[i][k] != 0:
                            target_x_k, _ = get_position(grid[i][k], grid_size)
                            if target_x_k == i and grid[i][j] > grid[i][k]:
                                conflicts += 2

        # Verification des colonnes
        for j in range(grid_size):
            for i in range(grid_size):
                if grid[i][j] == 0:
                    continue
                _, target_y = get_position(grid[i][j], grid_size)
                if target_y == j:  # Tile is in correct column
                    for k in range(i + 1, grid_size):
                        if grid[k][j] != 0:
                            _, target_y_k = get_position(grid[k][j], grid_size)
                            if target_y_k == j and grid[i][j] > grid[k][j]:
                                conflicts += 2

        return conflicts
    
    # Heuristique
    def heuristic(grid):
        return manhattan_distance(grid) + get_linear_conflicts(grid)
    
    def get_state_string(grid):
        return ''.join(str(cell) for row in grid for cell in row)

    grid_size = len(grid)
    initial_state = [row[:] for row in grid]
    goal_state = [[i * grid_size + j + 1 for j in range(grid_size)] for i in range(grid_size)]
    goal_state[-1][-1] = 0

    queue = [(heuristic(initial_state), 0, initial_state, [])]
    visited = {get_state_string(initial_state)}
    
    # Augmenté la limite pour le 4x4
    max_iterations = 200000 if grid_size == 4 else 100000
    
    while queue and len(queue) < max_iterations:  # Preventions des boucles infinies
        _, cost, current, path = heapq.heappop(queue)
        
        if current == goal_state:
            return path

        # Trouver la tuile càvide
        empty_x, empty_y = None, None
        for i in range(grid_size):
            for j in range(grid_size):
                if current[i][j] == 0:
                    empty_x, empty_y = i, j
                    break
            if empty_x is not None:
                break

        # Essayer toutes les deplacements possibles
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = empty_x + dx, empty_y + dy
            
            if 0 <= new_x < grid_size and 0 <= new_y < grid_size:
                # Creer une nouvelle etat
                new_state = [row[:] for row in current]
                new_state[empty_x][empty_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[empty_x][empty_y]
                
                state_string = get_state_string(new_state)
                if state_string not in visited:
                    visited.add(state_string)
                    h_score = heuristic(new_state)
                    heapq.heappush(queue, (h_score + cost + 1, cost + 1, new_state, path + [(dx, dy)]))

    # Pas de solution possible
    return None

# ------------------------------------------------- Menu principal ---------------------------------------------------------
def main_menu():
    screen = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("LOL Puzzle")
    running = True
    
    # Charger le logo
    logo_image = pygame.image.load(LOGO_IMAGE_PATH)
    logo_image = pygame.transform.scale(logo_image, (200, 400))
    logo_rect = logo_image.get_rect(center=(400 // 2, 600 // 4))
    
    # Charger l'image du cadre
    y_offset = 50
    frame_image = pygame.image.load(FRAME_IMAGE_PATH)
    frame_image = pygame.transform.scale(frame_image, (320 , 900))
    frame_rect = frame_image.get_rect(center=(400 // 2, 600 // 3 + y_offset))
        
    # Charger l'image footer
    footer_image = pygame.image.load(FOOTER_IMAGE_PATH)
    footer_image = pygame.transform.scale(footer_image, (400 , 400))
    footer_rect = footer_image.get_rect(midbottom=(400 // 2, 600))
    
    # Curseurs
    default_cursor = pygame.SYSTEM_CURSOR_ARROW
    pointer_cursor = pygame.SYSTEM_CURSOR_HAND
    
    # Texte défilant
    scrolling_text = "Développé par:  Prosper, HARITIANA, Feno, Toby, Daddy, Tsinjo!"
    text_scroll = font.render(scrolling_text, True, WHITE)
    text_width = text_scroll.get_width()
    
    # Position initiale du texte défilant
    text_x = 400  # Commence à droite
    text_y = 585  # Position verticale pour le footer
    scroll_speed = 0.5  # Vitesse de défilement
    
    # Valeur par défaut de k : nombre de deplacement avant lactivation du SWAP
    k_value = 10
    
    # Calcul des positions boutons et du titre
    button_width = 120
    button_height = 20
    button_spacing = 20
    center_x = 400 // 2
    title_y = 250
    buttons_start_y = title_y + 30

    buttons = [
     {"label": "8-P Classic", "mode": 3, "swap": 0, "rect": pygame.Rect(center_x - button_width - button_spacing // 2, buttons_start_y, button_width, button_height)},
     {"label": "8-P avec SWAP", "mode": 3, "swap": "k", "rect": pygame.Rect(center_x + button_spacing // 2, buttons_start_y, button_width, button_height)},
     {"label": "15-P avec SWAP", "mode": 4, "swap": "k", "rect": pygame.Rect(center_x - button_width // 2, 320, button_width, button_height)},
    ]
    
    # Boutons pour modifier K
    k_button_size = 30
    k_spacing = 1  # Réduire l'espace
    k_increase = pygame.Rect(center_x + k_spacing + k_button_size // 2, 400, k_button_size, k_button_size)
    k_decrease = pygame.Rect(center_x - k_spacing - k_button_size // 2 - k_button_size, 400, k_button_size, k_button_size)
    
    while running:
        screen.fill(BACKGROUND_COLOR)
        
        # Afficher l'image du background
        screen.blit(footer_image, footer_rect)

        # Afficher le cadre au milieu
        screen.blit(frame_image, frame_rect)
        
        # Afficher le logo
        screen.blit(logo_image, logo_rect)
        
        # Choix
        title = arcade_font.render("Choisissez la taille du puzzle", True, WHITE)
        title_rect = title.get_rect(center=(400 // 2, title_y))
        screen.blit(title, title_rect)
        
        # Nom du Jeu
        puzzletxt = arcade_font.render("PUZZLE", True, WHITE)
        puzzletxt_rect = puzzletxt.get_rect()
        puzzletxt_rect.centerx = logo_rect.centerx  # Centré horizontalement avec le logo
        puzzletxt_rect.top = logo_rect.bottom + 5   # 5 pixels sous le logo

        k_prompt = arcade_font.render(f"SWAP (K): {k_value}", True, WHITE)
        k_rect = k_prompt.get_rect(center=(400 // 2, 380))
        screen.blit(k_prompt, k_rect)
        
        
        
        # Dessiner les boutons
        for button in buttons:
            pygame.draw.rect(screen, BUTTON_COLOR, button["rect"], border_radius=10)
            text_surface = font.render(button["label"], True, BLACK)
            text_rect = text_surface.get_rect(center=button["rect"].center)
            screen.blit(text_surface, text_rect)

        # Dessiner les boutons pour modifier K
        pygame.draw.rect(screen, BUTTON_COLOR, k_increase, border_radius=10)
        pygame.draw.rect(screen, BUTTON_COLOR, k_decrease, border_radius=10)

        screen.blit(font.render("+", True, BLACK), k_increase.center)
        screen.blit(font.render("-", True, BLACK), k_decrease.center)
        
        # Animation de defilement des developpeurs du JEU
        # Défilement du texte
        text_x -= scroll_speed
        if text_x + text_width < 0:  # Réinitialiser le texte lorsqu'il sort de l'écran
            text_x = 400
        screen.blit(text_scroll, (text_x, text_y))
        
        pygame.display.flip()
        

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                # Vérifier si un bouton de mode est cliqué
                for button in buttons:
                    if button["rect"].collidepoint(x, y):
                        if button["swap"] == "k":
                            return button["mode"], k_value  # Mode avec SWAP
                        else:
                            return button["mode"], button["swap"]  # Mode classique

                # Modifier la valeur de K
                if k_increase.collidepoint(x, y):
                    k_value += 1
                elif k_decrease.collidepoint(x, y) and k_value > 1:
                    k_value -= 1
               
        # Vérifier si la souris survole un bouton
        mouse_pos = pygame.mouse.get_pos()
        if any(button["rect"].collidepoint(mouse_pos) for button in buttons) or k_increase.collidepoint(mouse_pos) or k_decrease.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pointer_cursor)
        else:
            pygame.mouse.set_cursor(default_cursor)
     

# --------------------------------------------- Affichage de la grille du jeu ----------------------------------------------
def draw_grid(screen, puzzle, show_solve_button, start_time):
 
    # Efface uniquement la zone de la grille
    grid_area = pygame.Rect(0, 0, SCREEN_WIDTH - SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, GRAY, grid_area)
    
    # Panneau lateral pour instruction et information
    side_panel = pygame.Rect(SCREEN_WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, BACKGROUND_COLOR, side_panel)
    
    """ Débogage visuel (contour bleu du panneau latéral)
    pygame.draw.rect(screen, DEBUG_COLOR, side_panel, 2)  # Contour noir pour le panneau"""

    # Grille pour le puzzle
    for i in range(puzzle.grid_size):
        for j in range(puzzle.grid_size):
            value = puzzle.grid[i][j]
            rect = pygame.Rect(
                j * puzzle.tile_size, 
                i * puzzle.tile_size, 
                puzzle.tile_size,
                puzzle.tile_size)          
            #Couleur des cases
            pygame.draw.rect(screen, WHITE if value != 0 else GRAY, rect)           
            #Contours de la cellule
            pygame.draw.rect(screen, BLACK, rect, 2)
            if value != 0:
                text = font.render(str(value), True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, rect.center)
                
    # Calcul de la largeur du panneau latéral pour le centrage
    panel_left = SCREEN_WIDTH - SIDE_PANEL_WIDTH
    
    # Stats  
    tmp = int(time.time() - start_time)
    stats_txt = arcade_font_small.render(f"Mouvs: {puzzle.total_moves} Temps: {tmp}s", True, WHITE)
    stats_rect = stats_txt.get_rect()
    stats_rect.centerx = panel_left + (SIDE_PANEL_WIDTH // 2)
    stats_rect.top = 10
    screen.blit(stats_txt, stats_rect)

    # Titre "Instructions" centré
    instruct_txt = arcade_font.render("Instructions", True, WHITE)
    instruct_rect = instruct_txt.get_rect()
    instruct_rect.centerx = panel_left + (SIDE_PANEL_WIDTH // 2)
    instruct_rect.top = 40
    screen.blit(instruct_txt, instruct_rect)

    # Instructions sur le JEU   
    y_offset = instruct_rect.bottom + 25
    
    # Première instruction avec licon rouge
    try:
        red_yo = pygame.image.load(os.path.join(ASSETS_DIR, 'icons', 'red-yo.png'))
        red_yo = pygame.transform.scale(red_yo, (15, 30))
        yo_icon_rect = red_yo.get_rect(left=panel_left + 10, top=y_offset)
        screen.blit(red_yo, yo_icon_rect)
    except:
        pygame.draw.circle(screen, (255, 0, 0), 
                         (panel_left + 25, y_offset + 15), 15)
        
    # Texte "UTILISER" 
    text_lines_1 = ["UTILISER LES TOUCHES", "POUR DEPLACER LES", "TUILES."]
    text_y = y_offset
    for line in text_lines_1:
            text_surf = arcade_font_small.render(line, True, WHITE)
            text_rect = text_surf.get_rect(
                left=yo_icon_rect.right + 10,
                top=text_y
            )
            screen.blit(text_surf, text_rect)
            text_y += text_rect.height + 5

    """# Flèches sur la ligne suivante
    arrow_x =text_rect.right + 10
    arrows = ["→", "←", "↑", "↓"]
    total_width = len(arrows) * 30  # Largeur totale pour les flèches
    arrow_x = panel_left + (SIDE_PANEL_WIDTH - total_width) // 2  # Centrer les flèches

    for arrow in arrows:
        arrow_surf = arcade_font.render(arrow, True, WHITE)
        arrow_rect = arrow_surf.get_rect(
        left=arrow_x,  # Aligner chaque flèche après la précédente
        centery=text_rect.centery  # Aligner verticalement avec "UTILISER"
    )
    screen.blit(arrow_surf, arrow_rect)
    arrow_x += arrow_rect.width + 10  # Ajoute un espacement entre les flèches"""
    
    # Espace avant la deuxième instruction
    y_offset = text_rect.bottom + 20
    
    # Deuxieme instruction avec licon rouge
    try:
       pink_yo = pygame.image.load(os.path.join(ASSETS_DIR, 'icons', 'pink-yo.png'))
       pink_yo = pygame.transform.scale(pink_yo, (15, 30))
       yo_icon_rect = pink_yo.get_rect(left=panel_left + 10, top=y_offset)
       screen.blit(pink_yo, yo_icon_rect)
    except:
       pygame.draw.circle(screen, (0, 255, 255), 
                        (panel_left + 25, y_offset + 15), 15)
       
    # Texte de la deuxième instruction sur plusieurs lignes
    text_lines_2 = ["UTILISER LA ", "COMBINAISON DE DEUX ", "TOUCHES POUR LE SWAP."]
       
    text_y = y_offset
    for line in text_lines_2:
        text_surf = arcade_font_small.render(line, True, WHITE)
        text_rect = text_surf.get_rect(
              left=yo_icon_rect.right + 10,
              top=text_y
        )
        screen.blit(text_surf, text_rect)
        text_y += text_rect.height + 5
           
    # Espace avant la deuxième instruction
    y_offset = text_rect.bottom + 20
    
    # Troisieme instruction avec licon bleu
    try:
       blue_yo = pygame.image.load(os.path.join(ASSETS_DIR, 'icons', 'blue-yo.png'))
       blue_yo = pygame.transform.scale(blue_yo, (15, 30))
       yo_icon_rect = blue_yo.get_rect(left=panel_left + 10, top=y_offset)
       screen.blit(blue_yo, yo_icon_rect)
    except:
       pygame.draw.circle(screen, (0, 255, 255), 
                        (panel_left + 25, y_offset + 15), 15)
    
    
    # Texte de la deuxième instruction sur plusieurs lignes
    text_lines_3 = ["APPUYER SUR AUTO EN", "BAS POUR RESOUDRE LE", "PUZZLE AVEC L'IA."]
    
    text_y = y_offset
    for line in text_lines_3:
        text_surf = arcade_font_small.render(line, True, WHITE)
        text_rect = text_surf.get_rect(
            left=yo_icon_rect.right + 10,
            top=text_y
        )
        screen.blit(text_surf, text_rect)
        text_y += text_rect.height + 5
        
    # Affichage du mode swap
    swap_y = SCREEN_HEIGHT - 70 
    if puzzle.swap_mode:
            # Afficher SWAP ACTIF
            swap_text = arcade_font_small.render("SWAP ACTIF", True, WHITE)
            swap_rect = swap_text.get_rect(centerx=SCREEN_WIDTH - SIDE_PANEL_WIDTH/2, top=swap_y)
            screen.blit(swap_text, swap_rect)
            
    elif puzzle.swap_after:
            # Afficher le compte à rebours avant le prochain swap
            compteur = puzzle.swap_after - puzzle.move_count
            swap_text = arcade_font_small.render(f"SWAP DANS: {compteur}", True, WHITE)
            swap_rect = swap_text.get_rect(centerx=SCREEN_WIDTH - SIDE_PANEL_WIDTH / 2, top=swap_y)
            screen.blit(swap_text, swap_rect)
            
    # Bouton de resolution automatique du puzzle
    solve_button = pygame.Rect(SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10, SCREEN_HEIGHT - 130, SIDE_PANEL_WIDTH - 20, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, solve_button)
    text_solve = font.render("AUTO", True, BLACK)
    text_rect = text_solve.get_rect(center=solve_button.center)
    screen.blit(text_solve, text_rect)
            
    # Calcul des dimensions pour les trois boutons
    button_width = (SIDE_PANEL_WIDTH - 40) // 3  # 40 pixels pour les marges (20px de chaque côté)
    button_height = 30
    button_y = SCREEN_HEIGHT - 40  # Position Y des boutons (au-dessus du bouton AUTO)
    spacing = 10  # Espacement entre les boutons
    
    # Position X initiale (commence depuis la gauche du panneau)
    start_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10
    
    # Bouton Reset
    reset_button = pygame.Rect(start_x, button_y, button_width, button_height)
    reset_text = arcade_font_small.render("RESET", True, WHITE)
    reset_text_rect = reset_text.get_rect(center=reset_button.center)
    screen.blit(reset_text, reset_text_rect)
    
    # Bouton Menu
    menu_button = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)
    menu_text = arcade_font_small.render("MENU", True, WHITE)
    menu_text_rect = menu_text.get_rect(center=menu_button.center)
    screen.blit(menu_text, menu_text_rect)
    
    # Bouton Quit
    quit_button = pygame.Rect(start_x + 2 * (button_width + spacing), button_y, button_width, button_height)
    quit_text = arcade_font_small.render("QUITTER", True, WHITE)
    quit_text_rect = quit_text.get_rect(center=quit_button.center)
    screen.blit(quit_text, quit_text_rect)

    pygame.display.flip()
    return solve_button, reset_button, menu_button, quit_button
                
    pygame.display.flip()
    return solve_button

# --- Main ---
def main():
    grid_size, swap_after = main_menu()
    if grid_size is None:
        pygame.quit()
        return

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("LOL Puzzle")

    puzzle = NPuzzle(grid_size, swap_after)
    clock = pygame.time.Clock()
    running = True
    start_time = time.time() 
    solving = False  # Flag pour indiquer si la résolution est en cours
    
    while running:
        solve_button, reset_button, menu_button, quit_button = draw_grid(screen, puzzle, True, start_time) 

        if puzzle.is_solved():
            # Calculer le temps et les mouvements
            end_time = time.time()
            completion_time = end_time - start_time
            moves_count = puzzle.total_moves
            
            # Créer le fichier SVG
            svg_path = stats_svg(completion_time, moves_count, grid_size)
            
            # Afficher la fenêtre de statistiques
            open_button, restart_button = stats_file(screen, completion_time, moves_count, svg_path)
            pygame.display.flip()
            
            # Attendre l'action de l'utilisateur
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                    if open_button.collidepoint(x, y):
                        file_location(os.path.dirname(svg_path))
                    elif restart_button.collidepoint(x, y):
                        return main()  # Redémarrer le jeu
                    elif event.type == pygame.QUIT:
                        running = False
                        waiting_for_input = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not solving:
                if event.key == pygame.K_DOWN:
                    puzzle.move((-1, 0))
                elif event.key == pygame.K_UP:
                    puzzle.move((1, 0))
                elif event.key == pygame.K_RIGHT:
                    puzzle.move((0, -1))
                elif event.key == pygame.K_LEFT:
                    puzzle.move((0, 1))
            elif event.type == pygame.MOUSEBUTTONDOWN and not solving:
                x, y = pygame.mouse.get_pos()
                if solve_button.collidepoint(x, y):
                    solving = True
                    solution = solve_puzzle(puzzle.grid)
                    if solution:
                        for move in solution:
                            puzzle.move(move)
                            draw_grid(screen, puzzle, True, start_time)
                            pygame.time.wait(200)
                            pygame.event.pump()  # Maintenir la réactivité
                            solving = False
                elif reset_button.collidepoint(x, y):
                    # Réinitialiser le puzzle
                    puzzle = NPuzzle(grid_size, swap_after)
                    start_time = time.time()  # Réinitialiser le temps
                elif menu_button.collidepoint(x, y):
                    return main()
                elif quit_button.collidepoint(x, y):
                    running = False

        clock.tick(30)
        pygame.display.flip()
#------------------------Creation du fichier SVG -----------------------------------------
def stats_svg(completion_time, moves_count, grid_size):
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <style>
            text {{ font-family: Arial; fill: black; }}
            .title {{ font-size: 24px; }}
            .stats {{ font-size: 18px; }}
        </style>
        <rect width="100%" height="100%" fill="#f0f0f0"/>
        <text x="200" y="50" text-anchor="middle" class="title">Statistiques du Puzzle</text>
        <text x="50" y="100" class="stats">Taille du puzzle: {grid_size}x{grid_size}</text>
        <text x="50" y="140" class="stats">Temps: {int(completion_time)} secondes</text>
        <text x="50" y="180" class="stats">Mouvements: {moves_count}</text>
    </svg>'''
    
    # Créer le dossier stats s'il n'existe pas
    os.makedirs('stats', exist_ok=True)
    filepath = f'stats/puzzle_stats_{int(time.time())}.svg'
    
    with open(filepath, 'w') as f:
        f.write(svg_content)
    
    return filepath

#-------------------------Fenetre stats final------------------------------------------------------------------------
def stats_file(screen, completion_time, moves_count, svg_path):
    # Créer une surface pour la fenêtre de statistiques
    stats_window = pygame.Surface((300, 200))
    stats_window.fill(BUTTON_COLOR)
    stats_window_rect = stats_window.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    
    # Texte des statistiques
    time_text = arcade_font.render(f"Temps: {int(completion_time)} secondes", True, BLACK)
    moves_text = arcade_font.render(f"Mouvements: {moves_count}", True, BLACK)
    
    # Deux boutons côte à côte
    button_width = 100
    button_height = 30 
    button_spacing = 20
    buttons_y = stats_window_rect.bottom - 40
    
    # Bouton Ouvrir
    open_button = pygame.Rect(stats_window_rect.centerx - button_width - button_spacing//2, buttons_y, button_width, button_height)
    pygame.draw.rect(screen, WHITE, open_button)
    open_text = arcade_font.render("SVG", True, BLACK)
    
    # Bouton Recommencer à droite
    restart_button = pygame.Rect(stats_window_rect.centerx + button_spacing//2,
                           buttons_y, button_width, button_height)  
    pygame.draw.rect(screen, WHITE, restart_button)
    restart_text = arcade_font.render("REJOUER", True, BLACK)
    
    # Afficher tout
    screen.blit(stats_window, stats_window_rect)
    screen.blit(time_text, (stats_window_rect.centerx - time_text.get_width()//2, stats_window_rect.top + 40))
    screen.blit(moves_text, (stats_window_rect.centerx - moves_text.get_width()//2, stats_window_rect.top + 80))
    screen.blit(open_text, (open_button.centerx - open_text.get_width()//2, open_button.centery - open_text.get_height()//2))
    screen.blit(restart_text, (restart_button.centerx - restart_text.get_width()//2, restart_button.centery - restart_text.get_height()//2))
    
    return open_button, restart_button

#----------------------- Path du fichier SVG ----------------------------------------------------------------
def file_location(path):
    if os.name == 'nt':  # Windows
        os.startfile(path)
    elif os.name == 'posix':  # Linux/Mac
        subprocess.Popen(['xdg-open', path])

    pygame.quit()

# Exécution du menu principal
if __name__ == "__main__":
    main()
    
pygame.quit()