#worker.py
import arcade

class WorkerView:
    def __init__(self, game, board_view, radius=25, move_time=0.3):
        self.game = game
        self.board_view = board_view
        self.radius = radius
        self.move_time = move_time
        
        # Animation state
        self.worker_positions = {}  # worker_index -> (x, y) visual positions
        self.animations = {}  # worker_index -> animation data
        
        # Worker colors
        self.colors = [arcade.color.RED, arcade.color.BLUE]
    
    def sync_positions(self):
        """Sync visual positions with logical positions for all workers"""
        for i, worker in enumerate(self.game.workers):
            if worker.x is not None and worker.y is not None:
                target_x, target_y = self.board_view.cell_to_center((worker.x, worker.y))
                self.worker_positions[i] = (target_x, target_y)
    
    def start_move(self, worker_index, target_cell):
        """Start animation for moving a worker to target cell"""
        if worker_index not in self.worker_positions:
            return
        
        start_x, start_y = self.worker_positions[worker_index]
        target_x, target_y = self.board_view.cell_to_center(target_cell)
        
        self.animations[worker_index] = {
            'start_pos': (start_x, start_y),
            'target_pos': (target_x, target_y),
            'elapsed': 0.0,
            'duration': self.move_time
        }
    
    def update(self, delta_time):
        """Update worker animations"""
        finished_animations = []
        
        for worker_index, anim in self.animations.items():
            anim['elapsed'] += delta_time
            
            if anim['elapsed'] >= anim['duration']:
                # Animation finished
                self.worker_positions[worker_index] = anim['target_pos']
                finished_animations.append(worker_index)
            else:
                # Interpolate position
                progress = anim['elapsed'] / anim['duration']
                # Smooth easing
                progress = progress * progress * (3.0 - 2.0 * progress)
                
                start_x, start_y = anim['start_pos']
                target_x, target_y = anim['target_pos']
                
                current_x = start_x + (target_x - start_x) * progress
                current_y = start_y + (target_y - start_y) * progress
                
                self.worker_positions[worker_index] = (current_x, current_y)
        
        # Remove finished animations
        for worker_index in finished_animations:
            del self.animations[worker_index]
    
    def any_moving(self):
        """Check if any worker is currently animating"""
        return len(self.animations) > 0
    
    def draw(self):
        """Draw all workers"""
        for i, worker in enumerate(self.game.workers):
            if i in self.worker_positions:
                x, y = self.worker_positions[i]
                color = self.colors[worker.owner]
                
                # Draw worker as a circle
                arcade.draw_circle_filled(x, y, self.radius, color)
                # Draw border
                arcade.draw_circle_outline(x, y, self.radius, arcade.color.BLACK, 2)
