import arcade
import os
import math

class BoardView:
    def __init__(self, game, tile_size, offset_x, offset_y, margin=4):
        self.game = game
        self.tile_size = tile_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.margin = margin
        
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
        
        # Define colors that match the actual Santorini game
        self.ground_color = (144, 194, 109)  # Green ground color
        self.building_base = (250, 248, 240)  # Off-white/cream building color
        self.building_shadow = (220, 218, 210)  # Slightly darker for depth
        self.building_highlight = (255, 255, 255)  # Pure white for highlights
        self.dome_color = (65, 125, 185)  # Blue dome color
        self.dome_highlight = (85, 145, 205)  # Lighter blue for dome highlight
        self.window_color = (40, 40, 40)  # Dark windows/doors
        
        # Building dimensions
        self.base_building_size = 0.7  # Fraction of tile size for building base
        self.floor_height = 8  # Height of each floor in pixels
    
    def cell_to_center(self, cell):
        """Convert grid cell (col, row) to pixel center coordinates with margin"""
        col, row = cell
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
        adj_x = x - self.offset_x
        adj_y = y - self.offset_y
        
        if adj_x < 0 or adj_y < 0:
            return None
        
        cell_width = self.tile_size + self.margin
        col = int(adj_x // cell_width)
        row = int(adj_y // cell_width)
        
        if col >= 5 or row >= 5:
            return None
        
        tile_x = adj_x % cell_width
        tile_y = adj_y % cell_width
        
        if tile_x >= self.tile_size or tile_y >= self.tile_size:
            return None
        
        return (col, row)
    
    def draw_greek_building(self, center_x, center_y, level):
        """Draw a Greek-style building matching the actual Santorini game"""
        if level == 0:
            return  # No building on ground level
        
        building_width = int(self.tile_size * self.base_building_size)
        building_height = level * self.floor_height
        
        # Calculate building bounds
        left = center_x - building_width // 2
        right = center_x + building_width // 2
        bottom = center_y - building_height // 2
        top = bottom + building_height
        
        # Draw building levels from bottom to top
        for floor in range(level):
            floor_bottom = bottom + (floor * self.floor_height)
            floor_top = floor_bottom + self.floor_height
            
            # Slight variation in width for each level (narrower as we go up)
            level_inset = floor * 2
            level_left = left + level_inset
            level_right = right - level_inset
            
            if level_right <= level_left:
                continue
            
            # Main building body
            arcade.draw_lrbt_rectangle_filled(
                level_left, level_right, floor_bottom, floor_top, 
                self.building_base
            )
            
            # Add architectural details
            self.draw_building_details(level_left, level_right, floor_bottom, floor_top, floor, level)
            
            # Building outline
            arcade.draw_lrbt_rectangle_outline(
                level_left, level_right, floor_bottom, floor_top,
                self.building_shadow, 2
            )
        
        # Add dome for level 4 (winning condition)
        if level == 4:
            self.draw_dome(center_x, top)
    
    def draw_building_details(self, left, right, bottom, top, floor, total_levels):
        """Add architectural details like windows, doors, and Greek elements"""
        width = right - left
        height = top - bottom
        center_x = (left + right) // 2
        center_y = (bottom + top) // 2
        
        # Add windows/doors for ground floor
        if floor == 0 and width > 20:
            # Draw arched doorway
            door_width = min(12, width // 3)
            door_height = height - 4
            door_left = center_x - door_width // 2
            door_right = center_x + door_width // 2
            door_bottom = bottom + 2
            door_top = door_bottom + door_height
            
            # Door opening
            arcade.draw_lrbt_rectangle_filled(
                door_left, door_right, door_bottom, door_top,
                self.window_color
            )
            
            # Arched top (using arc_filled which exists in arcade 3.x)
            if door_height > 8:
                arcade.draw_arc_filled(
                    center_x, door_top - 2, door_width, door_width // 2,
                    self.window_color, 0, 180
                )
        
        # Add small windows for upper floors
        elif floor > 0 and width > 16:
            window_size = min(6, width // 4)
            window_y = center_y
            
            # Two small windows
            if width > 24:
                # Left window - using lrbt_rectangle_filled instead
                window_left = center_x - width // 4 - window_size // 2
                window_right = window_left + window_size
                window_bottom = window_y - window_size // 2
                window_top = window_bottom + window_size
                
                arcade.draw_lrbt_rectangle_filled(
                    window_left, window_right, window_bottom, window_top,
                    self.window_color
                )
                
                # Right window
                window_left = center_x + width // 4 - window_size // 2
                window_right = window_left + window_size
                
                arcade.draw_lrbt_rectangle_filled(
                    window_left, window_right, window_bottom, window_top,
                    self.window_color
                )
            else:
                # Single central window
                window_left = center_x - window_size // 2
                window_right = window_left + window_size
                window_bottom = window_y - window_size // 2
                window_top = window_bottom + window_size
                
                arcade.draw_lrbt_rectangle_filled(
                    window_left, window_right, window_bottom, window_top,
                    self.window_color
                )
        
        # Add column details for higher levels
        if floor >= 2 and width > 20:
            column_width = 3
            # Left column
            arcade.draw_lrbt_rectangle_filled(
                left + 2, left + 2 + column_width, bottom, top,
                self.building_highlight
            )
            # Right column
            arcade.draw_lrbt_rectangle_filled(
                right - 2 - column_width, right - 2, bottom, top,
                self.building_highlight
            )
    
    def draw_dome(self, center_x, base_y):
        """Draw a blue dome on top of level 4 buildings"""
        dome_radius = int(self.tile_size * 0.25)
        dome_center_y = base_y + dome_radius // 2
        
        # Main dome body
        arcade.draw_circle_filled(
            center_x, dome_center_y, dome_radius, 
            self.dome_color
        )
        
        # Dome highlight (to make it look 3D)
        highlight_offset_x = -dome_radius // 3
        highlight_offset_y = dome_radius // 3
        arcade.draw_circle_filled(
            center_x + highlight_offset_x, dome_center_y + highlight_offset_y,
            dome_radius // 3, self.dome_highlight
        )
        
        # Dome outline
        arcade.draw_circle_outline(
            center_x, dome_center_y, dome_radius,
            self.building_shadow, 2
        )
        
        # Small cross or finial on top
        finial_y = dome_center_y + dome_radius - 2
        arcade.draw_line(
            center_x, finial_y, center_x, finial_y + 6,
            self.building_highlight, 2
        )
        arcade.draw_line(
            center_x - 3, finial_y + 3, center_x + 3, finial_y + 3,
            self.building_highlight, 2
        )
    
    def draw_ground_tile(self, left, bottom, right, top):
        """Draw the ground tile with a subtle texture"""
        # Base ground color
        arcade.draw_lrbt_rectangle_filled(
            left + 2, right - 2, bottom + 2, top - 2,
            self.ground_color
        )
        
        # Subtle border
        arcade.draw_lrbt_rectangle_outline(
            left + 2, right - 2, bottom + 2, top - 2,
            (120, 160, 90), 1
        )
    
    def draw(self):
        # Draw background if available
        if len(self.background_sprite_list) > 0:
            self.background_sprite_list.draw()
        
        # Draw buildings and ground tiles
        for row in range(5):
            for col in range(5):
                left, bottom, right, top = self.cell_to_bounds((col, row))
                level = self.game.board[row][col]
                center_x, center_y = self.cell_to_center((col, row))
                
                # Always draw ground tile
                self.draw_ground_tile(left, bottom, right, top)
                
                # Draw building if level > 0
                if level > 0:
                    self.draw_greek_building(center_x, center_y, level)
