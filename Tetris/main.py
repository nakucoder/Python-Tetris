import pygame, sys
from game import Game
from colors import Colors   

pygame.init()

title_font = pygame.font.SysFont(None, 40)
score_surface = title_font.render("Score", True, Colors.white)
next_surface = title_font.render("Next", True, Colors.white)
game_over_surface = title_font.render("GaMe OvEr", True, Colors.red)
pause_surface = title_font.render("PAUSED", True, Colors.white)
level_surface = title_font.render("Level", True, Colors.white)
hold_surface = title_font.render("Hold", True, Colors.white)
hold_rect = pygame.Rect(20, 215, 170, 180) # Symmetrical to the 'Next' box on the left


score_rect = pygame.Rect(530, 50, 170, 60)
next_rect = pygame.Rect(530, 215, 170, 180)
level_rect = pygame.Rect(530, 450, 170, 60)

screen = pygame.display.set_mode((750, 620))
pygame.display.set_caption("Python Tetris")

clock = pygame.time.Clock()

game = Game()

GAME_UPDATE = pygame.USEREVENT 
pygame.time.set_timer(GAME_UPDATE, 200)

MOVE_DELAY = pygame.USEREVENT + 1   # 1. Initial wait before sliding starts
MOVE_REPEAT = pygame.USEREVENT + 2  # 2. The speed of the sliding itself
moving_left = False                 # 3. Tracks if Left is being held
moving_right = False                # 4. Tracks if Right is being held


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            # 1. Toggle Pause with ESC
            if event.key == pygame.K_ESCAPE and not game.game_over:
                game.toggle_pause()

            # --- STEP 1: RESTART ONLY ON ENTER ---
            if game.game_over == True:
                if event.key == pygame.K_RETURN: # The Enter key
                    game.game_over = False
                    game.reset()
            
            # 2. Movement keys (Only if NOT paused and NOT game over)
            if not game.paused and not game.game_over:
                if event.key == pygame.K_LEFT:
                    game.move_left()
                    moving_left = True 
                    moving_right = False 
                    pygame.time.set_timer(MOVE_DELAY, 200)

                if event.key == pygame.K_RIGHT:
                    game.move_right()
                    moving_right = True 
                    moving_left = False 
                    pygame.time.set_timer(MOVE_DELAY, 200)

                if event.key == pygame.K_DOWN:
                    game.move_down()
                    game.update_score(0, 1)

                if event.key == pygame.K_UP:
                    game.rotate()

                if event.key == pygame.K_SPACE:
                    game.hard_drop()

                if event.key == pygame.K_RSHIFT: # Right Shift key
                    game.hold()    

        # --- SLIDING AND REPEAT LOGIC ---
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
                pygame.time.set_timer(MOVE_DELAY, 0) 
                pygame.time.set_timer(MOVE_REPEAT, 0)
            if event.key == pygame.K_RIGHT:
                moving_right = False
                pygame.time.set_timer(MOVE_DELAY, 0) 
                pygame.time.set_timer(MOVE_REPEAT, 0)

        if event.type == MOVE_DELAY:
            pygame.time.set_timer(MOVE_DELAY, 0) 
            pygame.time.set_timer(MOVE_REPEAT, 50) 

        if event.type == MOVE_REPEAT:
            if moving_left: game.move_left()
            if moving_right: game.move_right()

        # 3. Automatic Gravity and Speed Update
        if event.type == GAME_UPDATE and not game.game_over and not game.paused:
            game.move_down()
            new_speed = max(50, 200 - (game.level - 1) * 20) 
            pygame.time.set_timer(GAME_UPDATE, new_speed)


    score_value_surface = title_font.render(str(game.score), True, Colors.white)    

    # 1. Clear the screen with the background color
    screen.fill(Colors.dark_blue)

    # 2. Draw the UI Boxes
    # Hold Box
    screen.blit(hold_surface, (75, 180))
    pygame.draw.rect(screen, Colors.light_blue, hold_rect, 0, 10)
    
    # Score Box
    screen.blit(score_surface, (575, 20))
    pygame.draw.rect(screen, Colors.light_blue, score_rect, 0, 10)
    
    # Next Box
    screen.blit(next_surface, (585, 180))
    pygame.draw.rect(screen, Colors.light_blue, next_rect, 0, 10)
    
    # Level Box
    screen.blit(level_surface, (580, 420))
    pygame.draw.rect(screen, Colors.light_blue, level_rect, 0, 10)

    # 3. Draw the actual Game Grid in the center
    # This uses the (210, 11) offset we added in game.py
    game.draw(screen)

    # 4. Draw the piece inside the NEXT box
    if game.next_block.id == 3: # O-Block (Square)
        game.next_block.draw(screen, 570, 280, True) # Nudged right
    elif game.next_block.id == 4: # I-Block (Long)
        game.next_block.draw(screen, 545, 270, True)
    elif game.next_block.id == 1 or game.next_block.id == 2: # L and J blocks
        game.next_block.draw(screen, 560, 280, True) # Nudged left
    else: # T, S, Z blocks
        game.next_block.draw(screen, 565, 280, True)

    # 5. Draw the piece inside the HOLD box
    if game.hold_block != None:
        if game.hold_block.id == 3: # O-Block
            game.hold_block.draw(screen, 80, 280, True) # Nudged right
        elif game.hold_block.id == 4: # I-Block
            game.hold_block.draw(screen, 55, 270, True)
        elif game.hold_block.id == 1 or game.hold_block.id == 2: # L and J
            game.hold_block.draw(screen, 70, 280, True)
        else:
            game.hold_block.draw(screen, 75, 280, True)

    # 6. Draw Text Values (Score and Level)
    score_value_surface = title_font.render(str(game.score), True, Colors.white)
    screen.blit(score_value_surface, score_value_surface.get_rect(centerx = score_rect.centerx, centery = score_rect.centery))
    
    level_value_surface = title_font.render(str(game.level), True, Colors.white)
    screen.blit(level_value_surface, level_value_surface.get_rect(centerx = level_rect.centerx, centery = level_rect.centery))

    # 7. Game Over and Pause Overlays
    if game.game_over == True:
        screen.blit(game_over_surface, (320, 530))
        instr_font = pygame.font.SysFont(None, 24)
        instr_surf = instr_font.render("Press ENTER to Restart", True, Colors.white)
        screen.blit(instr_surf, (315, 570))

    if game.paused:
        # Adjusted position to be over the new center of the grid
        screen.blit(pause_surface, (280, 250))

    # 8. Update the display
    pygame.display.update()
    clock.tick(60)