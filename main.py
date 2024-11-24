import pygame
import random
import heapq

# Configurations de base 
SCREEN_WIDTH = 600  # Largeur de l'écran
SCREEN_HEIGHT = 400  # Hauteur de l'écran
SIDE_PANEL_WIDTH = 200
FONT_SIZE = 20
SWAP_INTERVAL = 3

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
small_font = pygame.font.Font(None, FONT_SIZE // 2)

# -------------------------------------------------- Classe principale du puzzle --------------------------------------------
class NPuzzle:
    def __init__(self, grid_size, swap_interval):
        self.grid_size = grid_size
        self.swap_interval = swap_interval
        total_width = SCREEN_WIDTH - SIDE_PANEL_WIDTH
        total_height = SCREEN_HEIGHT
        self.tile_size = min(total_width // grid_size, total_height // grid_size)
        self.grid = self.generate_solvable_puzzle()
        self.empty_pos = self.find_empty_tile()
        self.move_count = 0

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
        x, y = self.empty_pos
        dx, dy = direction
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            self.grid[x][y], self.grid[new_x][new_y] = self.grid[new_x][new_y], self.grid[x][y]
            self.empty_pos = (new_x, new_y)
            self.move_count += 1

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
    
    while running:
        screen.fill(BACKGROUND_COLOR)
        
        # Afficher l'image du background
        screen.blit(footer_image, footer_rect)

        # Afficher le cadre au milieu
        screen.blit(frame_image, frame_rect)

        
        # Afficher le logo
        screen.blit(logo_image, logo_rect)
        
        # Calcul des positions  du titre et boutons
        button_width = 400 // 4
        button_height = 25  
        button_gap = 400 // 22
        button_corner_radius = 20
        button_y_position = 600 // 2  # Position des boutons sur l'axe vertical
        title_y_position = button_y_position - button_height - 20
        
        # Choix
        title = arcade_font.render("Choisissez la taille du puzzle", True, WHITE)
        title_rect = title.get_rect(center=(400 // 2, title_y_position))
        screen.blit(title, title_rect)
        
        # Nom du Jeu
        puzzletxt = arcade_font.render("PUZZLE", True, WHITE)
        puzzletxt_rect = puzzletxt.get_rect(center=(logo_rect.centerx, logo_rect.bottom + 5))
        screen.blit(puzzletxt, puzzletxt_rect)

        #Bouton    
        button_3x3 = pygame.Rect(
            (400 // 2 - button_gap - button_width),
             600 // 2,
             button_width,
             button_height,
            )
        
        button_4x4 = pygame.Rect(
            (400 // 2 + button_gap),
            600 // 2,
            button_width,
            button_height,
            )

        pygame.draw.rect(screen, BUTTON_COLOR, button_3x3, border_radius=button_corner_radius)
        pygame.draw.rect(screen, BUTTON_COLOR, button_4x4, border_radius=button_corner_radius)

        #Texte des boutons
        text_3x3 = font.render("3x3", True, BLACK)
        text_4x4 = font.render("4x4", True, BLACK)
        
        # Centrage du texte dans les boutons
        text_3x3_rect = text_3x3.get_rect(center=button_3x3.center)
        text_4x4_rect = text_4x4.get_rect(center=button_4x4.center)

        screen.blit(text_3x3, text_3x3_rect)
        screen.blit(text_4x4, text_4x4_rect)
        
        pygame.display.flip()

        # Gestion des événements
        mouse_over_button = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if button_3x3.collidepoint(x, y):
                    return 3
                elif button_4x4.collidepoint(x, y):
                    return 4
               
        # Vérifier si la souris survole un bouton
        mouse_pos = pygame.mouse.get_pos()
        if button_3x3.collidepoint(mouse_pos) or button_4x4.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pointer_cursor)  # Curseur "main pointer"
            mouse_over_button = True
        else:
            pygame.mouse.set_cursor(default_cursor)  # Curseur par défaut
     

# --------------------------------------------- Affichage de la grille du jeu ----------------------------------------------
def draw_grid(screen, puzzle, show_solve_button):
 
    # Efface uniquement la zone de la grille
    grid_area = pygame.Rect(0, 0, SCREEN_WIDTH - SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, GRAY, grid_area)  # Fond gris pour la grille
    
    # Panneau lateral pour instruction et information
    side_panel = pygame.Rect(SCREEN_WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, WHITE, side_panel)
    
    # Débogage visuel (contour bleu du panneau latéral)
    pygame.draw.rect(screen, DEBUG_COLOR, side_panel, 2)  # Contour noir pour le panneau

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

    # Instructions sur le JEU
    instructions = ["Instructions:", "- Flèches: Déplacer", "- Solve: Résolution auto"]
    y_offset = 20
    for line in instructions:
        text = font.render(line, True, BLACK)
        screen.blit(text, (SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10, y_offset))
        y_offset += FONT_SIZE + 10

    # Bouton de resolution automatique du puzzle
    solve_button = None
    if show_solve_button:
        solve_button = pygame.Rect(SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10, SCREEN_HEIGHT - 100, SIDE_PANEL_WIDTH - 20, 50)
        pygame.draw.rect(screen, BUTTON_COLOR, solve_button)
        text_solve = font.render("Mode Auto", True, BLACK)
        text_rect = text_solve.get_rect(center=solve_button.center)
        screen.blit(text_solve, text_rect)

    pygame.display.flip()
    return solve_button

# --- Main ---
def main():
    grid_size = main_menu()
    if grid_size is None:
        pygame.quit()
        return

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("LOL Puzzle")

    puzzle = NPuzzle(grid_size, SWAP_INTERVAL)
    clock = pygame.time.Clock()
    running = True

    while running:
        show_solve_button = grid_size == 3
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
