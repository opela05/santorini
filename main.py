import arcade
import sys

try:
    from gameplay import Santorini
    from background import BoardView  
    from worker import WorkerView
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Santorini: Human vs AI (Minimax)"

class MainWindow(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
        print("Initializing MainWindow with margin-aware grid...")
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.ASH_GREY)
        
        # Logic
        self.game = Santorini()
        
        # CALIBRATED VALUES WITH MARGINS
        self.tile_size = 86      # Actual tile size (excluding margins)
        self.margin = 6          # Space between tiles
        self.offset_x = 150      # Starting position
        self.offset_y = 150      # Starting position
        
        # Views
        self.board_view = BoardView(self.game, self.tile_size, self.offset_x, self.offset_y, self.margin)
        self.worker_view = WorkerView(self.game, self.board_view, radius=self.tile_size*0.25, move_time=0.30)
        
        # Human interaction state
        self.placement_index = 0
        self.selected_worker_idx = None
        self.move_selected = None
        self.move_pending_for_worker = None
        
        # AI state
        self.ai_move_timer = 0.0
        self.ai_move_delay = 2.0
        self.ai_needs_to_act = False
        
        # Status text
        self.status_text = arcade.Text("Human (Red): Place your first worker", 10, SCREEN_HEIGHT - 30, 
                                     arcade.color.WHITE, 18, bold=True)
        
        # Calibration mode
        self.calibration_mode = False
        
        print("MainWindow initialization complete")
    
    def on_key_press(self, key, modifiers):
        """Enhanced calibration controls with margin adjustment"""
        if key == arcade.key.C:
            self.calibration_mode = not self.calibration_mode
            print(f"Calibration mode: {'ON' if self.calibration_mode else 'OFF'}")
            return
        
        if not self.calibration_mode:
            return
            
        # Fine-tuning controls
        if key == arcade.key.UP:
            self.offset_y += 1
            self.board_view.offset_y += 1
        elif key == arcade.key.DOWN:
            self.offset_y -= 1
            self.board_view.offset_y -= 1
        elif key == arcade.key.RIGHT:
            self.offset_x += 1
            self.board_view.offset_x += 1
        elif key == arcade.key.LEFT:
            self.offset_x -= 1
            self.board_view.offset_x -= 1
        elif key == arcade.key.PLUS or key == arcade.key.EQUAL:
            self.tile_size += 1
            self.board_view.tile_size += 1
            self.worker_view.radius = self.tile_size * 0.25
        elif key == arcade.key.MINUS:
            self.tile_size -= 1
            self.board_view.tile_size -= 1
            self.worker_view.radius = self.tile_size * 0.25
        elif key == arcade.key.M:  # 'M' for margin adjustment
            self.margin += 1
            self.board_view.margin += 1
        elif key == arcade.key.N:  # 'N' to decrease margin
            self.margin = max(0, self.margin - 1)
            self.board_view.margin = max(0, self.board_view.margin - 1)
        
        if self.calibration_mode:
            print(f"Calibration - Offset: ({self.offset_x}, {self.offset_y}), Tile: {self.tile_size}, Margin: {self.margin}")
    
    def update_status_text(self):
        """Update the status message"""
        if self.calibration_mode:
            self.status_text.text = f"CALIBRATION: Offset({self.offset_x},{self.offset_y}) Tile:{self.tile_size} Margin:{self.margin} | C=toggle M/N=margin"
        elif self.game.game_over:
            if self.game.winner == 0:
                self.status_text.text = "🎉 Human (Red) Wins!"
            elif self.game.winner == 1:
                self.status_text.text = "🤖 AI (Blue) Wins!"
        elif self.game.turn == 1:  # AI turn
            if self.ai_needs_to_act:
                self.status_text.text = "🤖 AI (Blue) is calculating with Minimax..."
            else:
                self.status_text.text = "🤖 AI (Blue) turn"
        else:  # Human turn
            if self.game.phase == 'placement':
                workers_placed = len([w for w in self.game.workers if w.owner == 0 and w.x is not None])
                if workers_placed == 0:
                    self.status_text.text = "Human (Red): Place your first worker"
                else:
                    self.status_text.text = "Human (Red): Place your second worker"
            else:
                if self.selected_worker_idx is None:
                    self.status_text.text = "Human (Red): Select a worker to move"
                elif self.move_selected is None:
                    self.status_text.text = "Human (Red): Choose where to move"
                else:
                    self.status_text.text = "Human (Red): Choose where to build"
    
    def on_draw(self):
        self.clear()
        
        # Draw status background
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, SCREEN_HEIGHT - 60, SCREEN_HEIGHT, (0, 0, 0, 120)
        )
        
        self.board_view.draw()
        
        # Draw calibration overlay showing tile bounds and margins
        if self.calibration_mode:
            for row in range(5):
                for col in range(5):
                    left, bottom, right, top = self.board_view.cell_to_bounds((col, row))
                    
                    # Draw tile boundary (actual clickable area)
                    arcade.draw_lrbt_rectangle_outline(
                        left, right, bottom, top,
                        arcade.color.YELLOW, 2
                    )
                    
                    # Draw center point
                    center_x, center_y = self.board_view.cell_to_center((col, row))
                    arcade.draw_circle_filled(center_x, center_y, 3, arcade.color.RED)
                    
                    # Draw cell coordinates for debugging
                    arcade.draw_text(f"{col},{row}", left + 2, top - 15, 
                                   arcade.color.WHITE, 10, bold=True)
        
        # Highlight selected worker & options (only for human player)
        if self.game.turn == 0 and self.selected_worker_idx is not None and not self.calibration_mode:
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
        
        # Draw status text
        self.status_text.draw()
    
    # Rest of the methods remain the same as before...
    def on_update(self, delta_time):
        self.worker_view.update(delta_time)
        self.worker_view.sync_positions()
        
        if self.move_pending_for_worker is not None and not self.worker_view.any_moving():
            self.move_pending_for_worker = None
        
        if not self.calibration_mode and self.game.turn == 1 and not self.game.game_over:
            if not self.ai_needs_to_act:
                self.ai_needs_to_act = True
                self.ai_move_timer = 0.0
            else:
                self.ai_move_timer += delta_time
                if self.ai_move_timer >= self.ai_move_delay:
                    self.execute_ai_turn()
                    self.ai_needs_to_act = False
        
        self.update_status_text()
    
    def execute_ai_turn(self):
        """Execute AI's turn using minimax"""
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
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.calibration_mode:
            # Show what cell was clicked for debugging
            cell = self.board_view.pixel_to_cell(x, y)
            print(f"Clicked at ({x}, {y}) -> Cell: {cell}")
            return
            
        if self.game.turn != 0 or self.game.game_over or self.worker_view.any_moving():
            return
        
        cell = self.board_view.pixel_to_cell(x, y)
        if cell is None:
            return
        
        col, row = cell
        
        try:
            if self.game.phase == 'placement':
                if self.game.place_worker_at(self.placement_index, col, row):
                    self.worker_view.sync_positions()
                    self.placement_index += 1
                    if self.placement_index < 4:
                        self.game.turn = self.placement_index // 2
                return
            
            clicked_worker = self.game.get_worker_at(col, row)
            
            if self.selected_worker_idx is None:
                if clicked_worker is not None and clicked_worker.owner == 0:
                    idx = self.game.workers.index(clicked_worker)
                    self.selected_worker_idx = idx
                return
            
            selected_worker = self.game.workers[self.selected_worker_idx]
            
            if self.move_selected is None:
                if clicked_worker is not None and clicked_worker.owner == 0:
                    self.selected_worker_idx = self.game.workers.index(clicked_worker)
                    return
                
                moves = self.game.possible_moves(selected_worker)
                if (col, row) in moves:
                    if selected_worker.x is not None:
                        self.game.occupants[selected_worker.y][selected_worker.x] = None
                    selected_worker.x, selected_worker.y = (col, row)
                    self.game.occupants[row][col] = selected_worker
                    
                    idx = self.selected_worker_idx
                    self.worker_view.start_move(idx, (col, row))
                    self.move_pending_for_worker = idx
                    self.move_selected = (col, row)
                return
            
            builds = self.game.possible_builds(selected_worker)
            if (col, row) in builds:
                self.game.board[row][col] += 1
                
                if self.game.has_won(selected_worker):
                    self.game.game_over = True
                    self.game.winner = 0
                else:
                    self.game.turn = 1
                
                self.selected_worker_idx = None
                self.move_selected = None
            else:
                self.selected_worker_idx = None
                self.move_selected = None
        
        except Exception as e:
            print(f"Error in mouse press: {e}")

def main():
    print("Starting Santorini with margin-aware grid alignment...")
    print("Calibration Controls:")
    print("  C = Toggle calibration mode")
    print("  Arrow keys = Move grid position")
    print("  +/- = Adjust tile size")
    print("  M/N = Adjust margin size")
    window = MainWindow()
    arcade.run()

if __name__ == "__main__":
    main()
