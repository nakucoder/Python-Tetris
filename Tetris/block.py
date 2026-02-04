from colors import Colors
import pygame
from position import Position

class Block:
    def __init__(self, id):
        self.id = id
        self.cells = {}  # Dictionary to hold cell positions relative to the block's origin
        self.cell_size = 30  # Size of each cell in pixels
        self.row_offset = 0  # Row offset on the grid
        self.column_offset = 0  # Column offset on the grid
        self.rotation_state = 0  # Current rotation state
        self.colors = Colors.get_cell_colors()


    def move(self, rows, columns):
        self.row_offset += rows
        self.column_offset += columns


    def get_cell_positions(self):
        tiles = self.cells[self.rotation_state]
        moved_tiles = []
        for position in tiles:
            position = Position(position.row + self.row_offset, position.column + self.column_offset)
            moved_tiles.append(position)
        return moved_tiles
    

    def rotate(self):
        self.rotation_state += 1
        if self.rotation_state == len(self.cells):
            self.rotation_state = 0


    def undo_rotation(self):
        self.rotation_state -= 1
        if self.rotation_state < 0:
            self.rotation_state = len(self.cells) - 1
               

    def draw(self, screen, offset_x, offset_y, is_sidebar=False):
        tiles = self.get_cell_positions()
        for tile in tiles:
            if is_sidebar:
                # We subtract the offsets to 'reset' the block to its original shape
                # This prevents it from being shifted by its position in the grid
                tile_x = (tile.column - self.column_offset) * self.cell_size + offset_x
                tile_y = (tile.row - self.row_offset) * self.cell_size + offset_y
                tile_rect = pygame.Rect(tile_x, tile_y, self.cell_size - 1, self.cell_size - 1)
            else:
                tile_rect = pygame.Rect(tile.column * self.cell_size + offset_x, 
                                        tile.row * self.cell_size + offset_y, 
                                        self.cell_size - 1, self.cell_size - 1)
            pygame.draw.rect(screen, self.colors[self.id], tile_rect)
