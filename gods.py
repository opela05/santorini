import arcade
import os
from abc import ABC, abstractmethod

class GodPower(ABC):
    """Base class for all God Powers"""
    # Class variables for consistent dimensions (set by GodSelectionView)
    CARD_WIDTH = 180
    CARD_HEIGHT = 240
    
    def __init__(self, name, description, image_path):
        self.name = name
        self.description = description
        self.image_path = image_path
        self.sprite = None
        self.sprite_list = None
        self.center_x = 0
        self.center_y = 0
        self.scale = 1.0
        self.is_active = False
        
    def load_sprite(self, scale=1.0):
        """Load the god card sprite"""
        if os.path.exists(self.image_path):
            self.sprite = arcade.Sprite(self.image_path, scale)
            self.sprite_list = arcade.SpriteList()
            self.sprite_list.append(self.sprite)
        else:
            print(f"Warning: Could not find god card image: {self.image_path}")
        
    def draw(self):
        """Draw the god card"""
        if self.sprite and self.sprite_list:
            self.sprite.center_x = self.center_x
            self.sprite.center_y = self.center_y
            self.sprite_list.draw()
    
    def collides_with_point(self, point):
        """Check if point collides with god card"""
        if not self.sprite:
            return False
        
        x, y = point
        # Use class variables that are automatically set by GodSelectionView
        return (self.center_x - self.CARD_WIDTH/2 <= x <= self.center_x + self.CARD_WIDTH/2 and
                self.center_y - self.CARD_HEIGHT/2 <= y <= self.center_y + self.CARD_HEIGHT/2)
        
    @abstractmethod
    def can_move(self, game, worker, target_pos):
        """Override movement rules"""
        return True
        
    @abstractmethod
    def can_build(self, game, worker, target_pos):
        """Override building rules"""
        return True
        
    @abstractmethod
    def on_move(self, game, worker, old_pos, new_pos):
        """Triggered after a move"""
        pass
        
    @abstractmethod
    def on_build(self, game, worker, build_pos):
        """Triggered after a build"""
        pass
        
    @abstractmethod
    def has_won(self, game, worker):
        """Override win conditions"""
        return False

# God Power Implementations with ACTIVE LOGIC

class Pan(GodPower):
    """Also wins by jumping down 2 levels"""
    def __init__(self):
        super().__init__(
            "Pan", 
            "You also win by jumping down 2 levels.",
            "assets/gods/pan.png"
        )
        
    def can_move(self, game, worker, target_pos):
        return True  # Normal movement rules
        
    def can_build(self, game, worker, target_pos):
        return True  # Normal building rules
        
    def on_move(self, game, worker, old_pos, new_pos):
        # Store previous height for win condition check
        if old_pos:
            worker.previous_height = game.board[old_pos[1]][old_pos[0]]
        
    def on_build(self, game, worker, build_pos):
        pass
        
    def has_won(self, game, worker):
        # ACTIVE: Check if worker moved down 2+ levels
        if hasattr(worker, 'previous_height') and worker.x is not None:
            current_height = game.board[worker.y][worker.x]
            if worker.previous_height - current_height >= 2:
                return True
        return False

class Atlas(GodPower):
    """Build domes as if they were blocks"""
    def __init__(self):
        super().__init__(
            "Atlas",
            "Build domes as if they were blocks.",
            "assets/gods/atlas.png"
        )
        
    def can_move(self, game, worker, target_pos):
        return True
        
    def can_build(self, game, worker, target_pos):
        # ACTIVE: Can build domes at any level (not just level 3)
        x, y = target_pos
        if game.board[y][x] >= 4 or game.occupants[y][x] is not None:
            return False
        return True  # Atlas can build domes anywhere
        
    def on_move(self, game, worker, old_pos, new_pos):
        pass
        
    def on_build(self, game, worker, build_pos):
        pass
        
    def has_won(self, game, worker):
        return False

class Artemis(GodPower):
    """May move a builder twice before building"""
    def __init__(self):
        super().__init__(
            "Artemis",
            "You may move a builder twice before building.",
            "assets/gods/artemis.png"
        )
        self.has_first_move = False
        self.first_move_from = None
        self.current_worker = None
        
    def can_move(self, game, worker, target_pos):
        # ACTIVE: Can't return to starting position on second move
        if (self.has_first_move and 
            self.current_worker == worker and 
            target_pos == self.first_move_from):
            return False
        return True
        
    def can_build(self, game, worker, target_pos):
        return True
        
    def on_move(self, game, worker, old_pos, new_pos):
        # ACTIVE: Track double move
        if not self.has_first_move or self.current_worker != worker:
            self.first_move_from = old_pos
            self.has_first_move = True
            self.current_worker = worker
        else:
            # Second move completed
            self.has_first_move = False
            self.first_move_from = None
            self.current_worker = None
        
    def on_build(self, game, worker, build_pos):
        # Reset after building
        self.has_first_move = False
        self.first_move_from = None
        self.current_worker = None
        
    def has_won(self, game, worker):
        return False

class Demeter(GodPower):
    """Build an additional block on a different space than the first block"""
    def __init__(self):
        super().__init__(
            "Demeter",
            "Build an additional block on a different space than the first block.",
            "assets/gods/demeter.png"
        )
        self.first_build_pos = None
        self.can_build_second = False
        self.current_worker = None
        
    def can_move(self, game, worker, target_pos):
        return True
        
    def can_build(self, game, worker, target_pos):
        # ACTIVE: Second build can't be on same space as first
        if (self.can_build_second and 
            self.current_worker == worker and 
            target_pos == self.first_build_pos):
            return False
        return True
        
    def on_move(self, game, worker, old_pos, new_pos):
        pass
        
    def on_build(self, game, worker, build_pos):
        # ACTIVE: Track double build
        if not self.can_build_second or self.current_worker != worker:
            self.first_build_pos = build_pos
            self.can_build_second = True
            self.current_worker = worker
        else:
            # Second build completed
            self.can_build_second = False
            self.first_build_pos = None
            self.current_worker = None
            
    def has_won(self, game, worker):
        return False

class Athena(GodPower):
    """After stepping up a level, no other builders may step up a level until your next turn"""
    def __init__(self):
        super().__init__(
            "Athena",
            "After stepping up a level, no other builders may step up a level until your next turn.",
            "assets/gods/athena.png"
        )
        self.blocked_player = None
        
    def can_move(self, game, worker, target_pos):
        # ACTIVE: Block opponent from moving up if Athena moved up last turn
        if (self.blocked_player == worker.owner and 
            worker.x is not None and worker.y is not None):
            current_height = game.board[worker.y][worker.x]
            target_height = game.board[target_pos[1]][target_pos[0]]
            if target_height > current_height:
                return False  # Blocked by Athena
        return True
        
    def can_build(self, game, worker, target_pos):
        return True
        
    def on_move(self, game, worker, old_pos, new_pos):
        # ACTIVE: Check if this worker moved up
        if old_pos and worker.x is not None:
            old_height = game.board[old_pos[1]][old_pos[0]]
            new_height = game.board[new_pos[1]][new_pos[0]]
            if new_height > old_height:
                # Block the opponent player
                self.blocked_player = 1 - worker.owner
            else:
                self.blocked_player = None
        
    def on_build(self, game, worker, build_pos):
        pass
        
    def has_won(self, game, worker):
        return False

class Poseidon(GodPower):
    """At the end of your turn, build up to three blocks neighboring any builder on the ground level that did not move"""
    def __init__(self):
        super().__init__(
            "Poseidon",
            "At the end of your turn, build up to three blocks neighboring any builder on the ground level that did not move.",
            "assets/gods/poseidon.png"
        )
        self.unmoved_workers = set()
        
    def can_move(self, game, worker, target_pos):
        return True
        
    def can_build(self, game, worker, target_pos):
        return True
        
    def on_move(self, game, worker, old_pos, new_pos):
        # ACTIVE: Track which workers moved
        worker_id = (worker.owner, worker.worker_id)
        if worker_id in self.unmoved_workers:
            self.unmoved_workers.remove(worker_id)
        
    def on_build(self, game, worker, build_pos):
        # ACTIVE: Poseidon's extra builds (simplified for now)
        # In a full implementation, this would allow up to 3 extra builds
        # near unmoved ground-level workers
        pass
        
    def has_won(self, game, worker):
        return False

class GodSelectionView:
    """Handles the God Power selection screen with clean uniform layout"""
    def __init__(self, screen_width=800, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Available gods
        self.available_gods = [
            Pan(), Atlas(), Artemis(), 
            Demeter(), Athena(), Poseidon()
        ]
        
        # UNIFORM CARD DIMENSIONS - Change these to resize all cards
        self.card_width = 160    # Change this value to resize card frames
        self.card_height = 220   # Change this value to resize card frames  
        self.card_scale = 0.22   # Change this value to resize sprite images
        
        # Set class variables for consistent collision detection
        GodPower.CARD_WIDTH = self.card_width
        GodPower.CARD_HEIGHT = self.card_height
        
        # Load sprites for all gods with uniform scale
        for god in self.available_gods:
            god.load_sprite(scale=self.card_scale)
            
        # Selection state
        self.human_selected = None
        self.ai_selected = None
        self.selection_complete = False
        
        # IMPROVED GRID LAYOUT WITH MORE SPACING
        self.cards_per_row = 3
        self.horizontal_spacing = 50  # Spacing between cards horizontally
        self.vertical_spacing = 80    # Spacing between rows
        
        # Calculate grid dimensions
        self.grid_width = (self.cards_per_row * self.card_width + 
                          (self.cards_per_row - 1) * self.horizontal_spacing)
        self.grid_height = (2 * self.card_height + self.vertical_spacing)
        
        # Center the grid perfectly
        self.grid_start_x = (screen_width - self.grid_width) // 2 + self.card_width // 2
        self.grid_start_y = (screen_height + self.grid_height) // 2 - self.card_height // 2
        
        # Text objects
        self.title_text = arcade.Text("SELECT GOD POWERS", screen_width//2, screen_height - 40,
                                    arcade.color.WHITE, 32, bold=True, anchor_x="center")
        self.instruction_text = arcade.Text("Click a god for Human Player", screen_width//2, screen_height - 85,
                                          arcade.color.YELLOW, 20, anchor_x="center")
        
    def update_positions(self):
        """Update card positions in uniform grid with better spacing"""
        for i, god in enumerate(self.available_gods):
            if god.sprite:
                row = i // self.cards_per_row
                col = i % self.cards_per_row
                
                x = self.grid_start_x + col * (self.card_width + self.horizontal_spacing)
                y = self.grid_start_y - row * (self.card_height + self.vertical_spacing)
                
                god.center_x = x
                god.center_y = y
    
    def get_clicked_god(self, x, y):
        """Get which god was clicked"""
        for god in self.available_gods:
            if god.sprite and god.collides_with_point((x, y)):
                return god
        return None
    
    def select_god(self, god, for_human=True):
        """Select a god for human or AI"""
        if for_human and self.human_selected is None:
            self.human_selected = god
            self.instruction_text.text = "AI is selecting..."
            # AI selects randomly from remaining gods
            remaining = [g for g in self.available_gods if g != god]
            import random
            self.ai_selected = random.choice(remaining)
            self.selection_complete = True
            
    def draw(self):
        """Draw the selection screen with clean uniform layout (NO NAMES)"""
        # Background
        arcade.draw_lrbt_rectangle_filled(0, self.screen_width, 0, self.screen_height, (30, 40, 60))
        
        # Update card positions
        self.update_positions()
        
        # Draw god cards with uniform sizes (NO NAMES, NO DESCRIPTIONS)
        for god in self.available_gods:
            if god.sprite:
                god.draw()
                
                # Draw uniform card frame with consistent width
                # arcade.draw_lrbt_rectangle_outline(
                #     god.center_x - self.card_width//2,
                #     god.center_x + self.card_width//2,
                #     god.center_y - self.card_height//2,
                #     god.center_y + self.card_height//2,
                #     arcade.color.WHITE, 3
                # )
                
                # Highlight selected cards with thicker uniform frames
                if god == self.human_selected:
                    arcade.draw_lrbt_rectangle_outline(
                        god.center_x - self.card_width//2 - 5,
                        god.center_x + self.card_width//2 + 5,
                        god.center_y - self.card_height//2 - 5,
                        god.center_y + self.card_height//2 + 5,
                        arcade.color.RED, 8
                    )
                    # Selection label below card
                    arcade.draw_text("HUMAN", god.center_x, god.center_y - self.card_height//2 - 35,
                                   arcade.color.RED, 18, anchor_x="center", bold=True)
                elif god == self.ai_selected:
                    arcade.draw_lrbt_rectangle_outline(
                        god.center_x - self.card_width//2 - 5,
                        god.center_x + self.card_width//2 + 5,
                        god.center_y - self.card_height//2 - 5,
                        god.center_y + self.card_height//2 + 5,
                        arcade.color.BLUE, 8
                    )
                    # Selection label below card
                    arcade.draw_text("AI", god.center_x, god.center_y - self.card_height//2 - 35,
                                   arcade.color.BLUE, 18, anchor_x="center", bold=True)
        
        # Draw UI text
        self.title_text.draw()
        self.instruction_text.draw()
        
        # Draw continue button if selection complete
        if self.selection_complete:
            button_x = self.screen_width // 2
            button_y = 70
            arcade.draw_lrbt_rectangle_filled(button_x - 130, button_x + 130, button_y - 35, button_y + 35,
                                            arcade.color.GREEN)
            arcade.draw_text("START GAME", button_x, button_y, arcade.color.WHITE, 22,
                           anchor_x="center", anchor_y="center", bold=True)

class InGameGodDisplay:
    """Handles displaying god powers during gameplay"""
    def __init__(self, human_god, ai_god):
        self.human_god = human_god
        self.ai_god = ai_god
        
        # Load smaller sprites for in-game display
        if self.human_god:
            self.human_god.load_sprite(scale=0.12)
        if self.ai_god:
            self.ai_god.load_sprite(scale=0.12)
            
    def draw(self, screen_width, screen_height, current_turn):
        """Draw god power cards during gameplay"""
        # Human god card (bottom left)
        if self.human_god and self.human_god.sprite:
            self.human_god.center_x = 70
            self.human_god.center_y = 70
            
            # Highlight if it's human's turn
            if current_turn == 0:
                arcade.draw_circle_outline(70, 70, 45, arcade.color.RED, 3)
            
            self.human_god.draw()
            arcade.draw_text("HUMAN", 70, 20, arcade.color.RED, 10, anchor_x="center", bold=True)
        
        # AI god card (bottom right)
        if self.ai_god and self.ai_god.sprite:
            self.ai_god.center_x = screen_width - 70
            self.ai_god.center_y = 70
            
            # Highlight if it's AI's turn
            if current_turn == 1:
                arcade.draw_circle_outline(screen_width - 70, 70, 45, arcade.color.BLUE, 3)
            
            self.ai_god.draw()
            arcade.draw_text("AI", screen_width - 70, 20, arcade.color.BLUE, 10, anchor_x="center", bold=True)
    
    def show_power_tooltip(self, x, y):
        """Show god power description when hovering"""
        # Check if mouse is over human god card
        if self.human_god and abs(x - 70) < 45 and abs(y - 70) < 45:
            return f"{self.human_god.name}: {self.human_god.description}"
        # Check if mouse is over AI god card  
        elif self.ai_god and abs(x - (800 - 70)) < 45 and abs(y - 70) < 45:
            return f"{self.ai_god.name}: {self.ai_god.description}"
        return None

class GodPowerManager:
    """Manages god power integration with game logic"""
    def __init__(self):
        self.human_god = None
        self.ai_god = None
        
    def set_gods(self, human_god, ai_god):
        """Set the selected god powers"""
        self.human_god = human_god
        self.ai_god = ai_god
        print(f"God powers set: Human={human_god.name}, AI={ai_god.name}")
        
    def get_god_for_player(self, player):
        """Get the god power for a specific player"""
        return self.human_god if player == 0 else self.ai_god
        
    def can_move(self, game, worker, target_pos):
        """ACTIVE: Check if move is allowed with god power modifications"""
        god = self.get_god_for_player(worker.owner)
        if god:
            return god.can_move(game, worker, target_pos)
        return True
        
    def can_build(self, game, worker, target_pos):
        """ACTIVE: Check if build is allowed with god power modifications"""
        god = self.get_god_for_player(worker.owner)
        if god:
            return god.can_build(game, worker, target_pos)
        return True
        
    def on_move(self, game, worker, old_pos, new_pos):
        """ACTIVE: Trigger god power effects after move"""
        god = self.get_god_for_player(worker.owner)
        if god:
            god.on_move(game, worker, old_pos, new_pos)
            
    def on_build(self, game, worker, build_pos):
        """ACTIVE: Trigger god power effects after build"""
        god = self.get_god_for_player(worker.owner)
        if god:
            god.on_build(game, worker, build_pos)
            
    def check_special_win(self, game, worker):
        """ACTIVE: Check for special win conditions"""
        god = self.get_god_for_player(worker.owner)
        if god:
            return god.has_won(game, worker)
        return False

# Factory function to create gods by name
def create_god(name):
    """Create a god instance by name"""
    god_classes = {
        "Pan": Pan,
        "Atlas": Atlas, 
        "Artemis": Artemis,
        "Demeter": Demeter,
        "Athena": Athena,
        "Poseidon": Poseidon
    }
    
    if name in god_classes:
        return god_classes[name]()
    return None
