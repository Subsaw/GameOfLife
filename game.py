import pygame
import numpy as np

class Command:
    def execute(self):
        pass

class NextGenerationCommand(Command):
    def __init__(self, game):
        self.game = game

    def execute(self):
        self.game.next_generation()

class PauseResumeCommand(Command):
    def __init__(self, game):
        self.game = game

    def execute(self):
        self.game.simulation_active = not self.game.simulation_active

class SaveCommand(Command):
    def __init__(self, game):
        self.game = game

    def execute(self):
        np.save('game_state.npy', self.game.game_state)

class LoadCommand(Command):
    def __init__(self, game):
        self.game = game

    def execute(self):
        try:
            self.game.game_state = np.load('game_state.npy')
        except FileNotFoundError:
            print("No saved state found.")

class Button:
    def __init__(self, screen, color, x, y, width, height, text, text_color, font_size, command=None):
        self.screen = screen
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.command = command

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class GameOfLife:
    def __init__(self, width, height, n_cells_x, n_cells_y, fps):
        self.width = width
        self.height = height
        self.n_cells_x = n_cells_x
        self.n_cells_y = n_cells_y
        self.cell_width = width // n_cells_x
        self.cell_height = height // n_cells_y
        self.fps = fps

        self.game_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])
        self.simulation_active = False

    def next_generation(self):
        new_state = np.copy(self.game_state)

        for y in range(self.n_cells_y):
            for x in range(self.n_cells_x):
                n_neighbors = self.game_state[(x - 1) % self.n_cells_x, (y - 1) % self.n_cells_y] + \
                              self.game_state[(x) % self.n_cells_x, (y - 1) % self.n_cells_y] + \
                              self.game_state[(x + 1) % self.n_cells_x, (y - 1) % self.n_cells_y] + \
                              self.game_state[(x - 1) % self.n_cells_x, (y) % self.n_cells_y] + \
                              self.game_state[(x + 1) % self.n_cells_x, (y) % self.n_cells_y] + \
                              self.game_state[(x - 1) % self.n_cells_x, (y + 1) % self.n_cells_y] + \
                              self.game_state[(x) % self.n_cells_x, (y + 1) % self.n_cells_y] + \
                              self.game_state[(x + 1) % self.n_cells_x, (y + 1) % self.n_cells_y]

                if self.game_state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                    new_state[x, y] = 0
                elif self.game_state[x, y] == 0 and n_neighbors == 3:
                    new_state[x, y] = 1

        self.game_state = new_state

    def draw_grid(self, screen):
        for y in range(0, self.height, self.cell_height):
            for x in range(0, self.width, self.cell_width):
                cell = pygame.Rect(x, y, self.cell_width, self.cell_height)
                pygame.draw.rect(screen, (128, 128, 128), cell, 1)

    def draw_cells(self, screen):
        for y in range(self.n_cells_y):
            for x in range(self.n_cells_x):
                cell = pygame.Rect(x * self.cell_width, y * self.cell_height, self.cell_width, self.cell_height)
                if self.game_state[x, y] == 1:
                    pygame.draw.rect(screen, (0, 0, 0), cell)

    def save_state(self):
        np.save('game_state.npy', self.game_state)

    def load_state(self):
        try:
            self.game_state = np.load('game_state.npy')
        except FileNotFoundError:
            print("No saved state found.")

# Initialize Pygame
pygame.init()

clock = pygame.time.Clock()
fps = 10

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

game = GameOfLife(width, height, 40, 30, 10)

white = (255, 255, 255)
green = (0, 255, 0)

button_width, button_height = 200, 50
button_x, button_y = (width - button_width) // 2, height - button_height - 10

# Buttons with associated commands
buttons = [
    Button(screen, green, button_x, button_y, button_width, button_height,
           "Next Generation", (0, 0, 0), 36, command=NextGenerationCommand(game)),
    Button(screen, green, button_x, button_y - 60, button_width, button_height,
           "Pause/Resume", (0, 0, 0), 36, command=PauseResumeCommand(game)),
    Button(screen, green, button_x - 250, button_y, button_width, button_height,
           "Save", (0, 0, 0), 36, command=SaveCommand(game)),
    Button(screen, green, button_x + 250, button_y, button_width, button_height,
           "Load", (0, 0, 0), 36, command=LoadCommand(game))
]

running = True
while running:
    screen.fill(white)
    game.draw_grid(screen)
    game.draw_cells(screen)

    for button in buttons:
        button.draw()

    pygame.display.flip()

    if game.simulation_active:
        game.next_generation()

    clock.tick(game.fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.is_clicked(event.pos) and button.command:
                    button.command.execute()

            x, y = event.pos[0] // game.cell_width, event.pos[1] // game.cell_height
            game.game_state[x, y] = not game.game_state[x, y]

pygame.quit()