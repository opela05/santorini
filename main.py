import arcade
import sys

try:
    from gameplay import Santorini
    from background import BoardView  
    from worker import WorkerView
    from gods import GodSelectionView, InGameGodDisplay, GodPowerManager
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Santorini: Human vs AI (with God Powers)"

class MainWindow(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
        print("Initializing MainWindow with God Powers...")
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.ASH_GREY)
        
        # Game state management
        self.game_state = "god_selection"  # "god_selection", "playing", "game_over"
        
        # God Power system
        self.god_selection = GodSelectionView(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.god_manager = GodPowerManager()
        self.in_game_god_display = None
        
        # Game logic (initialize after god selection)
        self.game = None
        
        # HARDCODED CALIBRATION VALUES
        self.tile_size = 75
        self.margin = 15
        self.offset_x = 181
        self.offset_y = 184
        
        # Views (initialize after god selection)
        self.board_view = None
        self.worker_view = None
        
        # Human interaction state
        self.placement_index = 0
        self.selected_worker_idx = None
        self.move_selected = None
        self.move_pending_for_worker = None
        
        # AI state
        self.ai_move_timer = 0.0
        self.ai_move_delay = 2.0
        self.ai_needs_to_act = False
        
        # Game ending state
        self.game_ended = False
        self.end_screen_timer = 0.0
        self.show_end_screen = False
        
        # Text objects for better performance
        self.status_text = arcade.Text("", 10, SCREEN_HEIGHT - 35, 
                                     arcade.color.WHITE, 18, bold=True)
        self.winner_text = arcade.Text("", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50, 
                                     arcade.color.WHITE, 48, bold=True, anchor_x="center")
        self.restart_text = arcade.Text("Press R to Restart", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20,
                                      arcade.color.WHITE, 24, bold=True, anchor_x="center")
        
        # Tooltip for god powers
        self.tooltip_text = ""
        
        print("MainWindow initialized successfully!")
    
    def initialize_game(self):
        """Initialize game after god selection"""
        self.game = Santorini(self.god_manager)  # Pass god manager to game
        self.board_view = BoardView(self.game, self.tile_size, self.offset_x, self.offset_y, self.margin)
        self.worker_view = WorkerView(self.game, self.board_view, radius=self.tile_size*0.25, move_time=0.30)
        self.in_game_god_display = InGameGodDisplay(
            self.god_manager.human_god, 
            self.god_manager.ai_god
        )
    
    def update_status_text(self):
        """Update the status message"""
        if self.game_state != "playing":
            return
            
        if self.game.game_over and self.show_end_screen:
            if self.game.winner == 0:
                message = f"🎉 HUMAN ({self.god_manager.human_god.name}) WINS! 🎉 Press R to restart"
                self.winner_text.text = f"🎉 HUMAN ({self.god_manager.human_god.name}) WINS! 🎉"
                self.winner_text.color = arcade.color.RED
            elif self.game.winner == 1:
                message = f"🤖 AI ({self.god_manager.ai_god.name}) WINS! 🤖 Press R to restart"
                self.winner_text.text = f"🤖 AI ({self.god_manager.ai_god.name}) WINS! 🤖"
                self.winner_text.color = arcade.color.BLUE
            else:
                message = "Game Over! Press R to restart"
                self.winner_text.text = "GAME OVER"
                self.winner_text.color = arcade.color.WHITE
        elif self.game.game_over:
            if self.game.winner == 0:
                message = f"🎉 Human ({self.god_manager.human_god.name}) Wins!"
            elif self.game.winner == 1:
                message = f"🤖 AI ({self.god_manager.ai_god.name}) Wins!"
            else:
                message = "Game Over!"
        elif self.game.turn == 1:
            if self.ai_needs_to_act:
                message = f"🤖 AI ({self.god_manager.ai_god.name}) is calculating with Minimax..."
            else:
                message = f"🤖 AI ({self.god_manager.ai_god.name}) turn"
        else:
            human_god_name = self.god_manager.human_god.name
            if self.game.phase == 'placement':
                workers_placed = len([w for w in self.game.workers if w.owner == 0 and w.x is not None])
                if workers_placed == 0:
                    message = f"Human ({human_god_name}): Place your first worker"
                else:
                    message = f"Human ({human_god_name}): Place your second worker"
            else:
                if self.selected_worker_idx is None:
                    message = f"Human ({human_god_name}): Select a worker to move"
                elif self.move_selected is None:
                    message = f"Human ({human_god_name}): Choose where to move"
                else:
                    message = f"Human ({human_god_name}): Choose where to build"
        
        self.status_text.text = message
    
    def on_draw(self):
        self.clear()
        
        if self.game_state == "god_selection":
            # Draw god selection screen
            self.god_selection.draw()
            
        elif self.game_state == "playing":
            # Draw the game board and workers
            self.board_view.draw()
            
            # Game highlights (only when game is active)
            if not self.game.game_over and self.game.turn == 0 and self.selected_worker_idx is not None:
                w = self.game.workers[self.selected_worker_idx]
                cx, cy = self.board_view.cell_to_center((w.x, w.y))
                arcade.draw_circle_outline(cx, cy, self.tile_size*0.4, arcade.color.GOLD, 5)
                
                if self.move_selected is None:
                    moves = self.game.possible_moves(w)
                    for (mx, my) in moves:
                        mcx, mcy = self.board_view.cell_to_center((mx, my))
                        arcade.draw_circle_outline(mcx, mcy, self.tile_size*0.3, arcade.color.YELLOW, 4)
                else:
                    builds = self.game.possible_builds(w)
                    for (bx, by) in builds:
                        bcx, bcy = self.board_view.cell_to_center((bx, by))
                        arcade.draw_circle_outline(bcx, bcy, self.tile_size*0.3, arcade.color.GREEN, 4)
            
            # Draw workers
            self.worker_view.draw()
            
            # Draw in-game god power display
            if self.in_game_god_display:
                self.in_game_god_display.draw(SCREEN_WIDTH, SCREEN_HEIGHT, self.game.turn)
            
            # Draw status background
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, SCREEN_HEIGHT - 60, SCREEN_HEIGHT, (0, 0, 0, 180)
            )
            
            # Draw status text
            self.status_text.draw()
            
            # Draw tooltip if hovering over god cards
            if self.tooltip_text:
                arcade.draw_lrbt_rectangle_filled(
                    10, 300, 150, 200, (0, 0, 0, 200)
                )
                arcade.draw_text(self.tooltip_text, 15, 175, arcade.color.WHITE, 12, 
                               width=280, multiline=True)
            
            # Draw game over screen overlay
            if self.game.game_over and self.show_end_screen:
                arcade.draw_lrbt_rectangle_filled(
                    0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 150)
                )
                self.winner_text.draw()
                self.restart_text.draw()
    
    def on_update(self, delta_time):
        if self.game_state == "god_selection":
            # Check if god selection is complete
            if self.god_selection.selection_complete:
                # Set up god powers
                self.god_manager.set_gods(
                    self.god_selection.human_selected,
                    self.god_selection.ai_selected
                )
                # Initialize game
                self.initialize_game()
                self.game_state = "playing"
                
        elif self.game_state == "playing":
            # Update worker animations
            self.worker_view.update(delta_time)
            self.worker_view.sync_positions()
            
            # Clear pending moves when animation completes
            if self.move_pending_for_worker is not None and not self.worker_view.any_moving():
                self.move_pending_for_worker = None
            
            # Handle game ending
            if self.game.game_over and not self.game_ended:
                self.game_ended = True
                self.end_screen_timer = 0.0
                print(f"Game ended! Winner: {self.game.winner}")
            
            # Show end screen after brief delay
            if self.game_ended and not self.show_end_screen:
                self.end_screen_timer += delta_time
                if self.end_screen_timer >= 2.0:
                    self.show_end_screen = True
            
            # Handle AI turn (only if game is not over)
            if not self.game.game_over and self.game.turn == 1:
                if not self.ai_needs_to_act:
                    self.ai_needs_to_act = True
                    self.ai_move_timer = 0.0
                else:
                    self.ai_move_timer += delta_time
                    if self.ai_move_timer >= self.ai_move_delay:
                        self.execute_ai_turn()
                        self.ai_needs_to_act = False
            
            # Update status text
            self.update_status_text()
    
    def execute_ai_turn(self):
        """Execute AI's turn using minimax with god powers"""
        try:
            if self.game.phase == 'placement':
                move = self.game.ai_get_best_move()
                if move:
                    col, row = move
                    if self.game.place_worker_at(self.placement_index, col, row):
                        self.worker_view.sync_positions()
                        self.placement_index += 1
                        if self.placement_index < 4:
                            self.game.turn = self.placement_index // 2
            else:
                move_result = self.game.ai_get_best_move()
                if move_result:
                    worker, move_pos, build_pos = move_result
                    worker_idx = self.game.workers.index(worker)
                    game_won = self.game.execute_move(worker, move_pos, build_pos)
                    self.worker_view.start_move(worker_idx, move_pos)
                    self.move_pending_for_worker = worker_idx
        except Exception as e:
            print(f"Error in AI turn: {e}")
    
    def restart_game(self):
        """Restart the game (back to god selection)"""
        print("Restarting game...")
        self.game_state = "god_selection"
        self.god_selection = GodSelectionView(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.god_manager = GodPowerManager()
        
        # Reset all state
        self.game = None
        self.board_view = None
        self.worker_view = None
        self.in_game_god_display = None
        
        # Reset UI state
        self.placement_index = 0
        self.selected_worker_idx = None
        self.move_selected = None
        self.move_pending_for_worker = None
        
        # Reset AI state
        self.ai_move_timer = 0.0
        self.ai_needs_to_act = False
        
        # Reset game ending state
        self.game_ended = False
        self.end_screen_timer = 0.0
        self.show_end_screen = False
        
        self.tooltip_text = ""
    
    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.R and self.game_state == "playing" and self.game.game_over:
            self.restart_game()
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == "god_selection":
            # Handle god selection
            if not self.god_selection.selection_complete:
                clicked_god = self.god_selection.get_clicked_god(x, y)
                if clicked_god:
                    self.god_selection.select_god(clicked_god, for_human=True)
            else:
                # Check if start game button clicked
                if (350 < x < 450 and 75 < y < 125):
                    # Button clicked, transition handled in on_update
                    pass
                    
        elif self.game_state == "playing":
            # Block all input if game is over
            if self.game.game_over:
                return
                
            # Block input if not human turn or animations are playing
            if self.game.turn != 0 or self.worker_view.any_moving():
                return
            
            cell = self.board_view.pixel_to_cell(x, y)
            if cell is None:
                return  # Clicked in padding
            
            col, row = cell
            
            try:
                # Placement phase
                if self.game.phase == 'placement':
                    if self.game.place_worker_at(self.placement_index, col, row):
                        self.worker_view.sync_positions()
                        self.placement_index += 1
                        if self.placement_index < 4:
                            self.game.turn = self.placement_index // 2
                    return
                
                # Play phase with god power integration
                clicked_worker = self.game.get_worker_at(col, row)
                
                if self.selected_worker_idx is None:
                    # Select a worker
                    if clicked_worker is not None and clicked_worker.owner == 0:
                        idx = self.game.workers.index(clicked_worker)
                        # Only select if worker has valid moves (considering god powers)
                        if self.game.possible_moves(clicked_worker):
                            self.selected_worker_idx = idx
                    return
                
                selected_worker = self.game.workers[self.selected_worker_idx]
                
                if self.move_selected is None:
                    # Handle worker selection change
                    if clicked_worker is not None and clicked_worker.owner == 0:
                        new_idx = self.game.workers.index(clicked_worker)
                        if self.game.possible_moves(clicked_worker):
                            self.selected_worker_idx = new_idx
                        return
                    
                    # Handle move selection (with god power validation)
                    moves = self.game.possible_moves(selected_worker)
                    if (col, row) in moves:
                        old_pos = (selected_worker.x, selected_worker.y)
                        
                        # Move the worker
                        if selected_worker.x is not None:
                            self.game.occupants[selected_worker.y][selected_worker.x] = None
                        selected_worker.x, selected_worker.y = (col, row)
                        self.game.occupants[row][col] = selected_worker
                        
                        # Trigger god power on_move
                        self.god_manager.on_move(self.game, selected_worker, old_pos, (col, row))
                        
                        # Start animation
                        idx = self.selected_worker_idx
                        self.worker_view.start_move(idx, (col, row))
                        self.move_pending_for_worker = idx
                        self.move_selected = (col, row)
                        
                        # Check for wins (normal + special god power wins)
                        if self.game.has_won(selected_worker) or self.god_manager.check_special_win(self.game, selected_worker):
                            self.game.game_over = True
                            self.game.winner = 0
                            return
                    return
                
                # Handle build selection (with god power validation)
                builds = self.game.possible_builds(selected_worker)
                if (col, row) in builds:
                    # Build
                    self.game.board[row][col] += 1
                    
                    # Trigger god power on_build
                    self.god_manager.on_build(self.game, selected_worker, (col, row))
                    
                    # Switch turns
                    self.game.turn = 1
                    
                    # Reset selection state
                    self.selected_worker_idx = None
                    self.move_selected = None
                else:
                    # Invalid build - reset selection
                    self.selected_worker_idx = None
                    self.move_selected = None
            
            except Exception as e:
                print(f"Error in mouse press: {e}")
    
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion for tooltips"""
        if self.game_state == "playing" and self.in_game_god_display:
            self.tooltip_text = self.in_game_god_display.show_power_tooltip(x, y) or ""

def main():
    print("🏝️ Santorini: Human vs AI with God Powers")
    print("=" * 50)
    print("🎮 HOW TO PLAY:")
    print("   1. Select God Powers for each player")
    print("   2. Place your workers (red circles)")
    print("   3. Use god powers to gain advantage")
    print("   4. First to reach level 3 wins!")
    print()
    print("🕹️ CONTROLS:")
    print("   Click to select gods, workers and positions")
    print("   R = Restart game (when game over)")
    print("=" * 50)
    
    window = MainWindow()
    arcade.run()

if __name__ == "__main__":
    main()
