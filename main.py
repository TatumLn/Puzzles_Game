import pygame
import random
import heapq

# --- Configurations de base ---
SCREEN_SIZE = 600
SIDE_PANEL_WIDTH = 200  # Largeur du panneau latéral
FONT_SIZE = 30
SWAP_INTERVAL = 3  # Nombre de déplacements avant un swap

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)  # Fond gris
BUTTON_COLOR = (200, 200, 200)
HIGHLIGHT_COLOR = (100, 100, 100)

# Initialisation de Pygame
pygame.init()
font = pygame.font.Font(None, FONT_SIZE)

# --- Classe principale du puzzle ---
class NPuzzle:
    def __init__(self, grid_size, swap_interval):
        global TILE_SIZE
        self.grid_size = grid_size
        self.swap_interval = swap_interval
        TILE_SIZE = (SCREEN_SIZE - SIDE_PANEL_WIDTH) // grid_size
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
        inversions = 0
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] and tiles[j] and tiles[i] > tiles[j]:
                    inversions += 1
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

# --- Algorithme de résolution automatique (A*) ---
def solve_puzzle(grid):
    def heuristic(grid):
        dist = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                value = grid[i][j]
                if value != 0:
                    target_x = (value - 1) // len(grid)
                    target_y = (value - 1) % len(grid)
                    dist += abs(i - target_x) + abs(j - target_y)
        return dist

    def serialize(grid):
        return tuple(tuple(row) for row in grid)

    start = grid
    goal = [[(i * len(grid) + j + 1) % (len(grid) ** 2) for j in range(len(grid))] for i in range(len(grid))]
    frontier = [(heuristic(start), 0, start, [])]  # (heuristique, coût, état, chemin)
    visited = set()

    while frontier:
        _, cost, current, path = heapq.heappop(frontier)
        if serialize(current) in visited:
            continue
        visited.add(serialize(current))
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

# --- Menu principal ---
def main_menu():
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("n-Puzzle Menu")
    running = True
    while running:
        screen.fill(GRAY)

        title = font.render("Choisissez la taille du puzzle:", True, BLACK)
        screen.blit(title, (SCREEN_SIZE // 4, SCREEN_SIZE // 4))

        # Boutons
        button_3x3 = pygame.Rect(SCREEN_SIZE // 4, SCREEN_SIZE // 2 - 50, SCREEN_SIZE // 2, 50)
        button_4x4 = pygame.Rect(SCREEN_SIZE // 4, SCREEN_SIZE // 2 + 50, SCREEN_SIZE // 2, 50)

        pygame.draw.rect(screen, BUTTON_COLOR, button_3x3)
        pygame.draw.rect(screen, BUTTON_COLOR, button_4x4)

        text_3x3 = font.render("3x3", True, BLACK)
        text_4x4 = font.render("4x4", True, BLACK)
        screen.blit(text_3x3, button_3x3.center)
        screen.blit(text_4x4, button_4x4.center)

        pygame.display.flip()

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

# --- Affichage de la grille ---
def draw_grid(screen, puzzle, show_solve_button):
    screen.fill(GRAY)

    # Dessiner la grille
    for i in range(puzzle.grid_size):
        for j in range(puzzle.grid_size):
            value = puzzle.grid[i][j]
            rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, WHITE if value != 0 else GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            if value != 0:
                text = font.render(str(value), True, BLACK)
                screen.blit(text, rect.center)

    # Afficher le panneau latéral
    side_panel = pygame.Rect(SCREEN_SIZE - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_SIZE)
    pygame.draw.rect(screen, WHITE, side_panel)

    instructions = [
        "Instructions:",
        "- Flèches: Déplacer",
        "- Solve: Résolution auto",
    ]
    y_offset = 20
    for line in instructions:
        text = font.render(line, True, BLACK)
        screen.blit(text, (SCREEN_SIZE - SIDE_PANEL_WIDTH + 10, y_offset))
        y_offset += FONT_SIZE + 10

    # Bouton Solve (seulement pour 3x3)
    solve_button = None
    if show_solve_button:
        solve_button = pygame.Rect(SCREEN_SIZE - SIDE_PANEL_WIDTH + 10, SCREEN_SIZE - 100, SIDE_PANEL_WIDTH - 20, 50)
        pygame.draw.rect(screen, BUTTON_COLOR, solve_button)
        text_solve = font.render("Solve", True, BLACK)
        screen.blit(text_solve, solve_button.center)

    pygame.display.flip()
    return solve_button

# --- Main ---
def main():
    grid_size = main_menu()
    if grid_size is None:
        pygame.quit()
        return

    screen = pygame.display.set_mode((SCREEN_SIZE + SIDE_PANEL_WIDTH, SCREEN_SIZE))
    puzzle = NPuzzle(grid_size, SWAP_INTERVAL)

    clock = pygame.time.Clock()
    running = True
    while running:
        show_solve_button = grid_size == 3
        solve_button = draw_grid(screen, puzzle, show_solve_button)

        if puzzle.is_solved():
            text = font.render("Vous avez gagné!", True, BLACK)
            screen.blit(text, (SCREEN_SIZE // 4, SCREEN_SIZE // 4))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    puzzle.move((-1, 0))
                elif event.key == pygame.K_DOWN:
                    puzzle.move((1, 0))
                elif event.key == pygame.K_LEFT:
                    puzzle.move((0, -1))
                elif event.key == pygame.K_RIGHT:
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

if __name__ == "__main__":
    main()
import pygame
import random
import heapq

# --- Configurations de base ---
SCREEN_SIZE = 600
SIDE_PANEL_WIDTH = 200  # Largeur du panneau latéral
FONT_SIZE = 30
SWAP_INTERVAL = 3  # Nombre de déplacements avant un swap

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)  # Fond gris
BUTTON_COLOR = (200, 200, 200)
HIGHLIGHT_COLOR = (100, 100, 100)

# Initialisation de Pygame
pygame.init()
font = pygame.font.Font(None, FONT_SIZE)

# --- Classe principale du puzzle ---
class NPuzzle:
    def __init__(self, grid_size, swap_interval):
        global TILE_SIZE
        self.grid_size = grid_size
        self.swap_interval = swap_interval
        TILE_SIZE = (SCREEN_SIZE - SIDE_PANEL_WIDTH) // grid_size
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
        inversions = 0
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] and tiles[j] and tiles[i] > tiles[j]:
                    inversions += 1
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

# --- Algorithme de résolution automatique (A*) ---
def solve_puzzle(grid):
    def heuristic(grid):
        dist = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                value = grid[i][j]
                if value != 0:
                    target_x = (value - 1) // len(grid)
                    target_y = (value - 1) % len(grid)
                    dist += abs(i - target_x) + abs(j - target_y)
        return dist

    def serialize(grid):
        return tuple(tuple(row) for row in grid)

    start = grid
    goal = [[(i * len(grid) + j + 1) % (len(grid) ** 2) for j in range(len(grid))] for i in range(len(grid))]
    frontier = [(heuristic(start), 0, start, [])]  # (heuristique, coût, état, chemin)
    visited = set()

    while frontier:
        _, cost, current, path = heapq.heappop(frontier)
        if serialize(current) in visited:
            continue
        visited.add(serialize(current))
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

# --- Menu principal ---
def main_menu():
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("n-Puzzle Menu")
    running = True
    while running:
        screen.fill(GRAY)

        title = font.render("Choisissez la taille du puzzle:", True, BLACK)
        screen.blit(title, (SCREEN_SIZE // 4, SCREEN_SIZE // 4))

        # Boutons
        button_3x3 = pygame.Rect(SCREEN_SIZE // 4, SCREEN_SIZE // 2 - 50, SCREEN_SIZE // 2, 50)
        button_4x4 = pygame.Rect(SCREEN_SIZE // 4, SCREEN_SIZE // 2 + 50, SCREEN_SIZE // 2, 50)

        pygame.draw.rect(screen, BUTTON_COLOR, button_3x3)
        pygame.draw.rect(screen, BUTTON_COLOR, button_4x4)

        text_3x3 = font.render("3x3", True, BLACK)
        text_4x4 = font.render("4x4", True, BLACK)
        screen.blit(text_3x3, button_3x3.center)
        screen.blit(text_4x4, button_4x4.center)

        pygame.display.flip()

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

# --- Affichage de la grille ---
def draw_grid(screen, puzzle, show_solve_button):
    screen.fill(GRAY)

    # Dessiner la grille
    for i in range(puzzle.grid_size):
        for j in range(puzzle.grid_size):
            value = puzzle.grid[i][j]
            rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, WHITE if value != 0 else GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            if value != 0:
                text = font.render(str(value), True, BLACK)
                screen.blit(text, rect.center)

    # Afficher le panneau latéral
    side_panel = pygame.Rect(SCREEN_SIZE - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_SIZE)
    pygame.draw.rect(screen, WHITE, side_panel)

    instructions = [
        "Instructions:",
        "- Flèches: Déplacer",
        "- Solve: Résolution auto",
    ]
    y_offset = 20
    for line in instructions:
        text = font.render(line, True, BLACK)
        screen.blit(text, (SCREEN_SIZE - SIDE_PANEL_WIDTH + 10, y_offset))
        y_offset += FONT_SIZE + 10

    # Bouton Solve (seulement pour 3x3)
    solve_button = None
    if show_solve_button:
        solve_button = pygame.Rect(SCREEN_SIZE - SIDE_PANEL_WIDTH + 10, SCREEN_SIZE - 100, SIDE_PANEL_WIDTH - 20, 50)
        pygame.draw.rect(screen, BUTTON_COLOR, solve_button)
        text_solve = font.render("Solve", True, BLACK)
        screen.blit(text_solve, solve_button.center)

    pygame.display.flip()
    return solve_button

# --- Main ---
def main():
    grid_size = main_menu()
    if grid_size is None:
        pygame.quit()
        return

    screen = pygame.display.set_mode((SCREEN_SIZE + SIDE_PANEL_WIDTH, SCREEN_SIZE))
    puzzle = NPuzzle(grid_size, SWAP_INTERVAL)

    clock = pygame.time.Clock()
    running = True
    while running:
        show_solve_button = grid_size == 3
        solve_button = draw_grid(screen, puzzle, show_solve_button)

        if puzzle.is_solved():
            text = font.render("Vous avez gagné!", True, BLACK)
            screen.blit(text, (SCREEN_SIZE // 4, SCREEN_SIZE // 4))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    puzzle.move((-1, 0))
                elif event.key == pygame.K_DOWN:
                    puzzle.move((1, 0))
                elif event.key == pygame.K_LEFT:
                    puzzle.move((0, -1))
                elif event.key == pygame.K_RIGHT:
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

if __name__ == "__main__":
    main()
