import pygame
import random
import time

# Game state
current_player = 1
game_over = False
winner = None

# Function to switch players
def switch_player():
    global current_player
    current_player = 2 if current_player == 1 else 1

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Snakes and Ladders")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (200, 230, 255)
DARK_BLUE = (160, 200, 255)
BROWN = (139, 69, 19)
BRIGHT_GREEN = (50, 255, 50)

# Board settings
GRID_SIZE = 10
CELL_SIZE = 50
BOARD_PADDING = 50

# Player settings
class Player:
    def __init__(self, color):
        self.position = 1
        self.color = color
        self.x = 0
        self.y = 0

# Create players
player1 = Player(RED)
player2 = Player(GREEN)

# Create ladders and snakes - randomly place 5 of each
ladders = {}
snakes = {}
num_ladders = 5
num_snakes = 5

possible_positions = list(range(2, GRID_SIZE * GRID_SIZE - 1))  # Exclude 1 and final cell
random.shuffle(possible_positions)

# Place ladders
for i in range(num_ladders):
    start = possible_positions[i]
    min_end = start + GRID_SIZE  # Ensure vertical movement
    max_end = GRID_SIZE * GRID_SIZE - 1
    possible_ends = [x for x in range(min_end, max_end + 1, GRID_SIZE)]
    if possible_ends:
        end = random.choice(possible_ends)
        ladders[start] = end
    
# Place snakes - avoid ladder positions
snake_positions = [pos for pos in possible_positions[num_ladders:] if pos > 2]
random.shuffle(snake_positions)

for i in range(num_snakes):
    start = snake_positions[i]
    min_end = 2
    max_end = start - GRID_SIZE  # Ensure vertical movement
    possible_ends = [x for x in range(min_end, max_end + 1, GRID_SIZE)]
    if possible_ends:
        end = random.choice(possible_ends)
        snakes[start] = end

# Create board coordinates - optimized to calculate once with alternating pattern
board_positions = {}
for row in range(GRID_SIZE):
    if row % 2 == 0:  # Left to right
        for col in range(GRID_SIZE):
            pos = row * GRID_SIZE + col + 1
            board_positions[pos] = (
                BOARD_PADDING + col * CELL_SIZE,
                WINDOW_SIZE[1] - BOARD_PADDING - CELL_SIZE - row * CELL_SIZE
            )
    else:  # Right to left
        for col in range(GRID_SIZE-1, -1, -1):
            pos = row * GRID_SIZE + (GRID_SIZE - 1 - col) + 1
            board_positions[pos] = (
                BOARD_PADDING + col * CELL_SIZE,
                WINDOW_SIZE[1] - BOARD_PADDING - CELL_SIZE - row * CELL_SIZE
            )

def roll_dice():
    return random.randint(1, 6)

def draw_board():
    # Draw grid more efficiently using a single surface
    board_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            rect = pygame.Rect(
                BOARD_PADDING + j * CELL_SIZE,
                BOARD_PADDING + i * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            # Alternate cell colors in a checkerboard pattern
            cell_color = LIGHT_BLUE if (i + j) % 2 == 0 else DARK_BLUE
            pygame.draw.rect(board_surface, cell_color, rect)
            pygame.draw.rect(board_surface, BLACK, rect, 1)
    
    # Draw ladders
    for start, end in ladders.items():
        start_pos = board_positions[start]
        end_pos = board_positions[end]
        # Draw ladder lines
        pygame.draw.line(board_surface, BROWN, 
                        (start_pos[0] + CELL_SIZE//2, start_pos[1] + CELL_SIZE//2),
                        (end_pos[0] + CELL_SIZE//2, end_pos[1] + CELL_SIZE//2), 5)
    
    # Draw snakes as curvy lines
    for start, end in snakes.items():
        start_pos = board_positions[start]
        end_pos = board_positions[end]
        # Calculate control points for curve
        ctrl1_x = start_pos[0] + CELL_SIZE//2 + 20
        ctrl1_y = (start_pos[1] + end_pos[1])//2
        ctrl2_x = end_pos[0] + CELL_SIZE//2 - 20
        ctrl2_y = (start_pos[1] + end_pos[1])//2
        
        # Draw curved snake line
        points = [(start_pos[0] + CELL_SIZE//2, start_pos[1] + CELL_SIZE//2)]
        for t in range(1, 100):
            t = t/100
            x = (1-t)**3 * (start_pos[0] + CELL_SIZE//2) + \
                3*(1-t)**2*t * ctrl1_x + \
                3*(1-t)*t**2 * ctrl2_x + \
                t**3 * (end_pos[0] + CELL_SIZE//2)
            y = (1-t)**3 * (start_pos[1] + CELL_SIZE//2) + \
                3*(1-t)**2*t * ctrl1_y + \
                3*(1-t)*t**2 * ctrl2_y + \
                t**3 * (end_pos[1] + CELL_SIZE//2)
            points.append((x, y))
        pygame.draw.lines(board_surface, BRIGHT_GREEN, False, points, 5)
    
    return board_surface

def draw_player(player):
    x, y = board_positions[player.position]
    pygame.draw.circle(screen, player.color, (x + CELL_SIZE//2, y + CELL_SIZE//2), 15)

def draw_winner_card(winner_player):
    # Create semi-transparent overlay
    overlay = pygame.Surface(WINDOW_SIZE)
    overlay.fill(WHITE)
    overlay.set_alpha(200)
    screen.blit(overlay, (0,0))
    
    # Draw winner text
    winner_text = font.render(f"Player {winner_player} Wins!", True, BLACK)
    text_rect = winner_text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))
    screen.blit(winner_text, text_rect)
    
    # Draw exit instruction
    exit_text = font.render("Press ESC to exit", True, BLACK)
    exit_rect = exit_text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2 + 50))
    screen.blit(exit_text, exit_rect)

# Pre-render static elements
board_surface = draw_board()
font = pygame.font.Font(None, 36)
instruction_text = font.render("Press SPACE to roll dice", True, BLACK)
number_texts = {
    i: font.render(str(i), True, BLACK) for i in range(1, GRID_SIZE * GRID_SIZE + 1)
}

# Game loop
running = True
dice_value = 0
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_over:
                running = False
            elif event.key == pygame.K_SPACE and not game_over:
                dice_value = roll_dice()
                current_player_obj = player1 if current_player == 1 else player2
                
                if current_player_obj.position + dice_value <= GRID_SIZE * GRID_SIZE:
                    current_player_obj.position += dice_value
                    
                    # Check for ladder
                    if current_player_obj.position in ladders:
                        current_player_obj.position = ladders[current_player_obj.position]
                    
                    # Check for snake
                    if current_player_obj.position in snakes:
                        current_player_obj.position = snakes[current_player_obj.position]
                    
                    # Check for winner
                    if current_player_obj.position == GRID_SIZE * GRID_SIZE:
                        game_over = True
                        winner = current_player
                    else:
                        # Switch player after move only if game is not over
                        switch_player()

    # Draw game elements
    screen.blit(board_surface, (0, 0))
    draw_player(player1)
    draw_player(player2)
    
    # Draw cell numbers efficiently
    for i in range(1, GRID_SIZE * GRID_SIZE + 1):
        x, y = board_positions[i]
        text = number_texts[i]
        text_rect = text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
        screen.blit(text, text_rect)
    
    if not game_over:
        # Display current player and dice value
        current_player_text = font.render(f"Current Player: {current_player}", True, BLACK)
        dice_text = font.render(f"Dice: {dice_value}", True, BLACK)
        screen.blit(current_player_text, (WINDOW_SIZE[0] - 250, 80))
        screen.blit(dice_text, (WINDOW_SIZE[0] - 150, 50))
        screen.blit(instruction_text, (WINDOW_SIZE[0] - 250, 20))
    else:
        draw_winner_card(winner)
    
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS
    
pygame.quit()
