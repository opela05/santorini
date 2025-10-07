import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Santorini Board Setup"

TILE_SIZE = 90  


class Tile(arcade.SpriteSolidColor):
    def __init__(self, width, height, x, y):
        super().__init__(width, height, arcade.color.WHITE)
        self.center_x = x
        self.center_y = y
        self.alpha = 100  
        self.highlighted = False

    def toggle_highlight(self):
        self.highlighted = not self.highlighted
        self.alpha = 180 if self.highlighted else 100


class SantoriniUI(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLUE)

        bg_path = os.path.join("assets", "background.png")
        self.background = arcade.Sprite(bg_path, scale=1)
        self.background.center_x = SCREEN_WIDTH / 2
        self.background.center_y = SCREEN_HEIGHT / 2
        self.background.width = SCREEN_WIDTH
        self.background.height = SCREEN_HEIGHT

        self.background_list = arcade.SpriteList()
        self.background_list.append(self.background)

        self.tile_list = arcade.SpriteList()
        self.tile_offset_x = 210
        self.tile_offset_y = 220
        self.create_tiles()

    def create_tiles(self):
        self.tile_list.clear()
        for row in range(5):
            for col in range(5):
                x = self.tile_offset_x + col * TILE_SIZE
                y = self.tile_offset_y + row * TILE_SIZE
                tile = Tile(TILE_SIZE, TILE_SIZE, x, y)
                self.tile_list.append(tile)

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        self.tile_list.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for tile in self.tile_list:
            if tile.left < x < tile.right and tile.bottom < y < tile.top:
                tile.toggle_highlight()

    def on_key_press(self, key, modifiers):
        """Arrow keys move grid, +/- resize tiles"""
        global TILE_SIZE
        if key == arcade.key.UP:
            self.tile_offset_y += 10
        elif key == arcade.key.DOWN:
            self.tile_offset_y -= 10
        elif key == arcade.key.RIGHT:
            self.tile_offset_x += 10
        elif key == arcade.key.LEFT:
            self.tile_offset_x -= 10
        elif key in (arcade.key.PLUS, arcade.key.EQUAL):
            TILE_SIZE += 5
        elif key == arcade.key.MINUS:
            TILE_SIZE -= 5

        self.create_tiles()


def main():
    SantoriniUI()
    arcade.run()


if __name__ == "__main__":
    main()
