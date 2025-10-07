import arcade
print("Arcade imported successfully")

try:
    from gameplay import Santorini
    print("Gameplay imported successfully")
except Exception as e:
    print(f"Error importing gameplay: {e}")
    exit()

try:
    from background import BoardView
    print("Background imported successfully")
except Exception as e:
    print(f"Error importing background: {e}")
    exit()

try:
    from worker import WorkerView
    print("Worker imported successfully")
except Exception as e:
    print(f"Error importing worker: {e}")
    exit()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Santorini Debug"

class DebugWindow(arcade.Window):
    def __init__(self):
        print("Initializing window...")
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        print("Window initialized")
        arcade.set_background_color(arcade.color.BLUE)
        print("Background color set")
        
    def on_draw(self):
        print("Drawing...")
        self.clear()
        arcade.draw_text("Hello World!", 400, 400, arcade.color.WHITE, 50, anchor_x="center")
        print("Draw complete")

def main():
    print("Starting main...")
    try:
        window = DebugWindow()
        print("Window created, starting arcade.run()")
        arcade.run()
        print("Arcade.run() finished")
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
