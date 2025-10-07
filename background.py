import arcade
import os

class BoardView:
    def __init__(self, game, tile_size, offset_x, offset_y, margin=4):
        self.game = game
        self.tile_size = tile_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.margin = margin  # Space between tiles
        
        # Load background if it exists
        bg_path = os.path.join("assets", "background.png")
        self.background_sprite_list = arcade.SpriteList()
        
        if os.path.exists(bg_path):
            self.background = arcade.Sprite(bg_path, scale=1)
            self.background.center_x = 400
            self.background.center_y = 400
            self.background.width = 800
            self.background.height = 800
            self.background_sprite_list.append(self.background)
        
        # Create text objects for level numbers
        self.level_texts = {}
        for level in range(5):
            self.level_texts[level] = arcade.Text(
                str(level), 0, 0, arcade.color.BLACK, 20,
                anchor_x="center", anchor_y="center", bold=True
            )
    
    def cell_to_center(self, cell):
        """Convert grid cell (col, row) to pixel center coordinates with margin"""
        col, row = cell
        # Account for margins: each cell is tile_size + margin, but center is at tile_size/2
        x = self.offset_x + col * (self.tile_size + self.margin) + self.tile_size // 2
        y = self.offset_y + row * (self.tile_size + self.margin) + self.tile_size // 2
        return x, y
    
    def cell_to_bounds(self, cell):
        """Get the actual bounds of a cell (excluding margins)"""
        col, row = cell
        x = self.offset_x + col * (self.tile_size + self.margin)
        y = self.offset_y + row * (self.tile_size + self.margin)
        return x, y, x + self.tile_size, y + self.tile_size
    
    def pixel_to_cell(self, x, y):
        """Convert pixel coordinates to grid cell (col, row) accounting for margins"""
        # Adjust for offset
        adj_x = x - self.offset_x
        adj_y = y - self.offset_y
        
        # Calculate which cell we're in, accounting for margins
        if adj_x < 0 or adj_y < 0:
            return None
        
        # Each cell occupies (tile_size + margin) pixels
        cell_width = self.tile_size + self.margin
        col = int(adj_x // cell_width)
        row = int(adj_y // cell_width)
        
        # Check if we're within bounds
        if col >= 5 or row >= 5:
            return None
        
        # Check if we're actually in the tile (not in the margin)
        tile_x = adj_x % cell_width
        tile_y = adj_y % cell_width
        
        # If we're in the margin area, return None
        if tile_x >= self.tile_size or tile_y >= self.tile_size:
            return None
        
        return (col, row)
    
    def draw(self):
        # Draw background if available
        if len(self.background_sprite_list) > 0:
            self.background_sprite_list.draw()
        
        # Draw grid elements (but not borders since background provides them)
        for row in range(5):
            for col in range(5):
                left, bottom, right, top = self.cell_to_bounds((col, row))
                
                # Get level and draw number with background if needed
                level = self.game.board[row][col]
                
                # Draw level number with white circle background for visibility
                if level > 0:
                    center_x, center_y = self.cell_to_center((col, row))
                    # Draw white circle background
                    arcade.draw_circle_filled(center_x, center_y, 15, arcade.color.WHITE)
                    arcade.draw_circle_outline(center_x, center_y, 15, arcade.color.BLACK, 2)
                    # Draw the number
                    self.level_texts[level].x = center_x
                    self.level_texts[level].y = center_y
                    self.level_texts[level].draw()
