import pygame
import random
import heapq

# Configurations de base 
SCREEN_WIDTH = 600  # Largeur de l'écran
SCREEN_HEIGHT = 400  # Hauteur de l'écran
SIDE_PANEL_WIDTH = 200
FONT_SIZE = 20

# Path des images et des fonts
LOGO_IMAGE_PATH = "assets/icons/lol.png" 
FOOTER_IMAGE_PATH = "assets/backgrounds/grille.png"
FRAME_IMAGE_PATH = "assets/backgrounds/cadre.png"
ARCADE_FONT_PATH = "assets/fonts/arcade.ttf"

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
        self.move_count = 0
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
            self.move_count += 1
            
            # Activer le mode swap après le nombre requis de déplacements
            if self.swap_after and self.move_count >= self.swap_after:
                self.swap_mode = True

    def is_solved(self):
        expected = list(range(1, self.grid_size ** 2)) + [0]
        return self.grid == [expected[i:i + self.grid_size] for i in range(0, len(expected), self.grid_size)]

# ------------------------------------------------- Algorithme de résolution automatique  --------------------------------
def solve_puzzle(grid):
    def heuristic(grid):
        dist = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                value = grid[i][j]
                if value != 0:
                    target_x, target_y = (value - 1) // len(grid), (value - 1) % len(grid)
                    dist += abs(i - target_x) + abs(j - target_y)
        return dist

    goal = [[(i * len(grid) + j + 1) % (len(grid) ** 2) for j in range(len(grid))] for i in range(len(grid))]
    frontier = [(heuristic(grid), 0, grid, [])]
    visited = set()

    while frontier:
        _, cost, current, path = heapq.heappop(frontier)
        if tuple(map(tuple, current)) in visited:
            continue
        visited.add(tuple(map(tuple, current)))
        if current == goal:
            return path

        empty_x, empty_y = next((i, j) for i, row in enumerate(current) for j, v in enumerate(row) if v == 0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = empty_x + dx, empty_y + dy
            if 0 <= new_x < len(current) and 0 <= new_y < len(current[0]):
                new_grid = [row[:] for row in current]
                new_grid[empty_x][empty_y], new_grid[new_x][new_y] = new_grid[new_x][new_y], new_grid[empty_x][empty_y]
                heapq.heappush(frontier, (heuristic(new_grid) + cost + 1, cost + 1, new_grid, path + [(dx, dy)]))

    return None

# ------------------------------------------------- Menu principal ---------------------------------------------------------
def main_menu():
    screen = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("LOL Puzzle")
    running = True
    
    # Charger le logo
    logo_image = pygame.image.load(LOGO_IMAGE_PATH)
    logo_image = pygame.transform.scale(logo_image, (100, 200))
    logo_rect = logo_image.get_rect(center=(400 // 2, 600 // 8))
    
    # Charger l'image du cadre
    y_offset = 40
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
    
    # Valeur par défaut de k : nombre de deplacement avant lactivation du SWAP
    k_value = 10
    
    # Calcul des positions boutons et du titre
    button_width = 120
    button_height = 20
    button_spacing = 20  # Espace entre les boutons 3x3
    center_x = 400 // 2
    title_y = 250  # Position du titre
    buttons_start_y = title_y + 30

    buttons = [
     {"label": "8-P Classic", "mode": 3, "swap": 0, "rect": pygame.Rect(center_x - button_width - button_spacing // 2, buttons_start_y, button_width, button_height)},
     {"label": "8-P avec SWAP", "mode": 3, "swap": "k", "rect": pygame.Rect(center_x + button_spacing // 2, buttons_start_y, button_width, button_height)},
     {"label": "15-P avec SWAP", "mode": 4, "swap": "k", "rect": pygame.Rect(center_x - button_width // 2, 320, button_width, button_height)},
    ]
    
    # Boutons pour modifier K
    k_button_size = 30
    k_spacing = 1  # Réduire l'espace
    k_increase = pygame.Rect(center_x + k_spacing + k_button_size // 2, 490, k_button_size, k_button_size)
    k_decrease = pygame.Rect(center_x - k_spacing - k_button_size // 2 - k_button_size, 490, k_button_size, k_button_size)
    
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
        puzzletxt_rect = puzzletxt.get_rect(center=(logo_rect.centerx, logo_rect.bottom + 5))
        screen.blit(puzzletxt, puzzletxt_rect)

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
def draw_grid(screen, puzzle, show_solve_button):
 
    # Efface uniquement la zone de la grille
    grid_area = pygame.Rect(0, 0, SCREEN_WIDTH - SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, GRAY, grid_area)  # Fond gris pour la grille
    
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

    # Titre "Instructions" centré
    instruct_txt = arcade_font.render("Instructions", True, WHITE)
    instruct_rect = instruct_txt.get_rect()
    instruct_rect.centerx = panel_left + (SIDE_PANEL_WIDTH // 2)
    instruct_rect.top = 20
    screen.blit(instruct_txt, instruct_rect)

    # Instructions sur le JEU   
    y_offset = instruct_rect.bottom + 25
    
    # Première instruction avec licon rouge
    try:
        red_yo = pygame.image.load("assets/icons/red-yo.png")
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
       pink_yo = pygame.image.load("assets/icons/pink-yo.png")
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
       blue_yo = pygame.image.load("assets/icons/blue-yo.png")
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

    # Bouton de resolution automatique du puzzle
    solve_button = None
    if show_solve_button:
        solve_button = pygame.Rect(SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10, SCREEN_HEIGHT - 100, SIDE_PANEL_WIDTH - 20, 50)
        pygame.draw.rect(screen, BUTTON_COLOR, solve_button)
        text_solve = font.render("AUTO", True, BLACK)
        text_rect = text_solve.get_rect(center=solve_button.center)
        screen.blit(text_solve, text_rect)
        
    # Affichage du mode swap
    if puzzle.swap_mode:
            swap_text = arcade_font.render("MODE SWAP ACTIF", True, WHITE)
            swap_rect = swap_text.get_rect(centerx=SCREEN_WIDTH - SIDE_PANEL_WIDTH/2, top=20)
            screen.blit(swap_text, swap_rect)
    elif puzzle.swap_after:
            # Afficher le compte à rebours avant le prochain swap
            moves_left = puzzle.swap_after - puzzle.move_count
            swap_text = arcade_font_small.render(f"SWAP DANS: {moves_left}", True, WHITE)
            swap_y = SCREEN_HEIGHT - 40 if show_solve_button else SCREEN_HEIGHT - 50
            swap_rect = swap_text.get_rect(centerx=SCREEN_WIDTH - SIDE_PANEL_WIDTH / 2, top=swap_y)
            screen.blit(swap_text, swap_rect)
                
    # Position du texte swap juste en dessous du bouton AUTO ou en bas si pas de bouton
            if show_solve_button:
                swap_y = SCREEN_HEIGHT - 40  # En dessous du bouton AUTO
            else:
                swap_y = SCREEN_HEIGHT - 50  # Position par défaut si pas de bouton
            
            swap_rect = swap_text.get_rect(
            centerx=SCREEN_WIDTH - SIDE_PANEL_WIDTH/2,
            top=swap_y
            )
            screen.blit(swap_text, swap_rect)

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

    while running:
        show_solve_button = grid_size == 3 and not puzzle.swap_mode
        solve_button = draw_grid(screen, puzzle, show_solve_button)

        if puzzle.is_solved():
            text = font.render("Vous avez gagné!", True, BLACK)
            screen.blit(text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    puzzle.move((-1, 0))
                elif event.key == pygame.K_UP:
                    puzzle.move((1, 0))
                elif event.key == pygame.K_RIGHT:
                    puzzle.move((0, -1))
                elif event.key == pygame.K_LEFT:
                    puzzle.move((0, 1))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if solve_button and solve_button.collidepoint(x, y):
                    solution = solve_puzzle(puzzle.grid)
                    if solution:
                        for move in solution:
                            puzzle.move(move)
                            draw_grid(screen, puzzle, show_solve_button)
                            pygame.time.wait(300)

        clock.tick(30)

    pygame.quit()

# Exécution du menu principal
if __name__ == "__main__":
    main()
