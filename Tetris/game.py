from grid import Grid
from blocks import *
import random

class Game:
    def __init__(self):
        self.grid = Grid()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.game_over = False
        self.score = 0
        self.level = 1           # Start at Level 1
        self.lines_cleared_count = 0 # Track total lines
        self.paused = False
        self.lock_delay_threshold = 4  # Number of GAME_UPDATE ticks to wait
        self.lock_delay_counter = 0
        self.hold_block = None
        self.can_hold = True # Set to False after a swap, True when a new block spawns


    def toggle_pause(self):
            self.paused = not self.paused

    def update_score(self, lines_cleared, move_down_points):
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared == 4:
            self.score += 1200 # Standard Tetris score
        
        self.score += move_down_points
        
        # Increase level every 10 lines
        self.lines_cleared_count += lines_cleared
        self.level = (self.lines_cleared_count // 10) + 1
        

    def get_random_block(self):
        if len(self.blocks) == 0:
            self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        block = random.choice(self.blocks)
        self.blocks.remove(block)
        return block    
    
    def move_left(self):
        self.current_block.move(0, -1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, 1)
        else:
            self.lock_delay_counter = 0 # Reset timer on move

    def move_right(self):
        self.current_block.move(0, 1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, -1)
        else:
            self.lock_delay_counter = 0 # Reset timer on move

    def move_down(self):
        self.current_block.move(1, 0)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(-1, 0)
            
            # Instead of locking immediately, we wait
            self.lock_delay_counter += 1
            if self.lock_delay_counter >= self.lock_delay_threshold:
                self.lock_block()
                self.lock_delay_counter = 0 # Reset for next piece
        else:
            # If the block is still falling freely, reset the counter
            self.lock_delay_counter = 0


    def hard_drop(self):
        # Keep moving down while the position is valid
        while self.block_inside() and self.block_fits():
            self.current_block.move(1, 0)
            self.update_score(0, 2) 

        # Once it hits something, move it back up one step and lock it
        self.current_block.move(-1, 0)
        self.lock_block()
        self.lock_delay_counter = 0 # Reset timer on hard drop        


    def lock_block(self):
        tiles = self.current_block.get_cell_positions()
        for position in tiles:
            self.grid.grid[position.row][position.column] = self.current_block.id
        self.current_block = self.next_block
        self.next_block = self.get_random_block()
        rows_cleared = self.grid.clear_full_rows()
        self.update_score(rows_cleared, 0)
        if self.block_fits() == False:
            self.game_over = True

        self.can_hold = True # Allow hold again after locking a block    


    def reset(self):    
        self.grid.reset()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.score = 0
        self.level = 1           # Reset level
        self.lines_cleared_count = 0 # Reset count
        self.hold_block = None
        self.can_hold = True # Allow hold after reset


    def block_fits(self):
        tiles = self.current_block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_empty(tile.row, tile.column) == False:
                return False
        return True


    def rotate(self):
        self.current_block.rotate()
        # 1. Check if it fits. If not, try "kicking" it
        if self.block_inside() == False or self.block_fits() == False:
            # Try moving it 1 step right
            self.current_block.move(0, 1)
            if self.block_inside() and self.block_fits():
                self.lock_start_time = 0 # SUCCESS! Reset the delay
                return 

            # Try moving it 1 step left
            self.current_block.move(0, -2) 
            if self.block_inside() and self.block_fits():
                self.lock_start_time = 0 # SUCCESS! Reset the delay
                return 

            # Try moving it 2 steps right (for I-Blocks)
            self.current_block.move(0, 3) 
            if self.block_inside() and self.block_fits():
                self.lock_start_time = 0 # SUCCESS! Reset the delay
                return

            # 2. If no kicks worked, undo everything
            self.current_block.move(0, -2) 
            self.current_block.undo_rotation()
        else:
            # 3. Fits perfectly on the first try!
            self.lock_start_time = 0 # SUCCESS! Reset the delay
                


    def block_inside(self):
        tiles = self.current_block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_inside(tile.row, tile.column) == False:
                return False
        return True

    

    def draw(self, screen):
        # The grid and current block are NOT in the sidebar, so we leave it as False
        self.grid.draw(screen, 210, 11)
        self.current_block.draw(screen, 210, 11, False)


    def hold(self):
        if not self.can_hold:
            return
        
        if self.hold_block is None:
            self.hold_block = self.current_block
            self.current_block = self.next_block
            self.next_block = self.get_random_block()
        else:
            self.hold_block, self.current_block = self.current_block, self.hold_block
        
        # --- RESET PIECE STATE ---
        self.hold_block.rotation_state = 0 # Reset rotation so it looks flat in the box
        self.current_block.rotation_state = 0 # Reset the new piece spawning in
        
        self.current_block.row_offset = 0
        self.current_block.column_offset = 3
        self.can_hold = False

