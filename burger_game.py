import pygame
import os
import sys
import random
import time
import math
import json
from pygame.math import Vector2

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
TRANSPARENT = (0, 0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Burger Bun Bakery Simulator")
clock = pygame.time.Clock()

# Create folders for assets if they don't exist
if not os.path.exists("images"):
    os.makedirs("images")
if not os.path.exists("sounds"):
    os.makedirs("sounds")
if not os.path.exists("data"):
    os.makedirs("data")

# Function to create placeholder images (first run only)
def create_placeholder_images():
    # Create placeholder images if they don't exist
    placeholders = {
        "bun_bottom.png": (150, 30, (220, 170, 60)),      # Golden brown bun bottom
        "bun_top.png": (150, 30, (240, 200, 100)),        # Lighter golden bun top with more contrast
        "bun_bottom_toasted.png": (150, 30, (200, 140, 40)),  # Toasted bottom bun
        "bun_top_toasted.png": (150, 30, (210, 160, 60)),  # Toasted top bun
        "lettuce.png": (140, 20, (50, 200, 50)),          # Bright green lettuce
        "tomato.png": (130, 15, (255, 50, 50)),           # Bright red tomato
        "tomato_sliced.png": (130, 8, (255, 60, 60)),     # Sliced tomato
        "patty.png": (130, 25, (120, 60, 20)),            # Dark brown patty
        "patty_raw.png": (130, 25, (180, 100, 80)),       # Raw patty
        "patty_overcooked.png": (130, 25, (80, 40, 10)),  # Overcooked patty
        "cheese.png": (135, 10, (255, 220, 50)),          # Bright yellow cheese
        "cheese_melted.png": (140, 8, (255, 200, 50)),    # Melted cheese
        "onion.png": (125, 10, (230, 230, 250)),          # Brighter white onion
        "onion_grilled.png": (125, 10, (210, 180, 170)),  # Grilled onion
        "bacon.png": (120, 8, (200, 80, 80)),             # More reddish bacon
        "bacon_crispy.png": (115, 7, (180, 60, 60)),      # Crispy bacon
        "background.png": (WIDTH, HEIGHT, (135, 206, 235)), # Sky blue background
        "table.png": (WIDTH, 200, (150, 75, 0)),          # Brown table
        "menu_bg.png": (WIDTH, HEIGHT, (0, 50, 100)),     # Dark blue menu background
        "grill.png": (200, 100, (50, 50, 50)),            # Grill surface
        "cutting_board.png": (200, 100, (220, 190, 140)), # Cutting board
        "knife.png": (80, 20, (200, 200, 200)),           # Knife
        "spatula.png": (60, 40, (180, 180, 180)),         # Spatula
        "customer_happy.png": (100, 100, (0, 255, 0)),    # Happy customer icon
        "customer_neutral.png": (100, 100, (255, 255, 0)), # Neutral customer icon
        "customer_angry.png": (100, 100, (255, 0, 0)),    # Angry customer icon
        "coin.png": (30, 30, (255, 215, 0)),              # Gold coin
        "shop_background.png": (WIDTH, HEIGHT, (100, 50, 150)), # Shop background
        "tutorial_bg.png": (400, 300, (200, 230, 255)),   # Tutorial background
    }
    
    for filename, (width, height, color) in placeholders.items():
        path = os.path.join("images", filename)
        if not os.path.exists(path):
            img = pygame.Surface((width, height))
            img.fill(color)
            pygame.image.save(img, path)
            print(f"Created placeholder image: {path}")

# Function to create placeholder sounds (first run only)
def create_placeholder_sounds():
    sound_info = [
        ("place.wav", 0.3),
        ("success.wav", 0.5),
        ("wrong.wav", 0.3),
        ("bonus.wav", 0.5),
        ("levelup.wav", 0.5),
        ("coin.wav", 0.4),
        ("sizzle.wav", 0.3),
        ("chop.wav", 0.4),
        ("customer_happy.wav", 0.5),
        ("customer_angry.wav", 0.5),
        ("purchase.wav", 0.5),
        ("click.wav", 0.2),
    ]
    
    for filename, volume in sound_info:
        path = os.path.join("sounds", filename)
        if not os.path.exists(path):
            # Create a default notification for missing sound files
            print(f"Sound file {path} doesn't exist. The game will run with default sounds.")

# Create default game data file
def create_default_game_data():
    data_path = os.path.join("data", "game_data.json")
    if not os.path.exists(data_path):
        default_data = {
            "high_score": 0,
            "unlocked_ingredients": ["bun_bottom", "bun_top", "patty", "cheese", "lettuce"],
            "locked_ingredients": ["tomato", "onion", "bacon"],
            "money": 0,
            "upgrades": {
                "grill_speed": 1,
                "customer_patience": 1,
                "tips": 1,
            },
            "tutorial_completed": False
        }
        
        try:
            with open(data_path, 'w') as f:
                json.dump(default_data, f)
            print(f"Created default game data at {data_path}")
        except Exception as e:
            print(f"Error creating game data: {e}")

# Create placeholder assets on first run
create_placeholder_images()
create_placeholder_sounds()
create_default_game_data()

# Load images
def load_image(filename, scale=1):
    try:
        path = os.path.join("images", filename)
        image = pygame.image.load(path).convert_alpha()
        if scale != 1:
            new_width = int(image.get_width() * scale)
            new_height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (new_width, new_height))
        return image
    except pygame.error as e:
        print(f"Cannot load image: {path}")
        print(f"Error: {e}")
        return pygame.Surface((50, 50))  # Return a small square as fallback

# Load sounds
def load_sound(filename, volume=1.0):
    try:
        path = os.path.join("sounds", filename)
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except:
        print(f"Cannot load sound: {filename}")
        # Create a silent sound
        return pygame.mixer.Sound(buffer=bytearray([0] * 44))

# Load game data
def load_game_data():
    data_path = os.path.join("data", "game_data.json")
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading game data: {e}")
        create_default_game_data()
        with open(data_path, 'r') as f:
            return json.load(f)

# Save game data
def save_game_data(data):
    data_path = os.path.join("data", "game_data.json")
    try:
        with open(data_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving game data: {e}")

# Load images
background = load_image("background.png")
table_img = load_image("table.png")
menu_bg = load_image("menu_bg.png")
shop_bg = load_image("shop_background.png")
tutorial_bg = load_image("tutorial_bg.png")
grill_img = load_image("grill.png")
cutting_board_img = load_image("cutting_board.png")
knife_img = load_image("knife.png")
spatula_img = load_image("spatula.png")
coin_img = load_image("coin.png")

# Customer images
customer_images = {
    "happy": load_image("customer_happy.png"),
    "neutral": load_image("customer_neutral.png"),
    "angry": load_image("customer_angry.png")
}

# Ingredient images
ingredient_images = {
    # Basic ingredients
    "bun_bottom": load_image("bun_bottom.png"),
    "bun_top": load_image("bun_top.png"),
    "patty": load_image("patty.png"),
    "cheese": load_image("cheese.png"),
    "lettuce": load_image("lettuce.png"),
    "tomato": load_image("tomato.png"),
    "onion": load_image("onion.png"),
    "bacon": load_image("bacon.png"),
    
    # Processed ingredients
    "bun_bottom_toasted": load_image("bun_bottom_toasted.png"),
    "bun_top_toasted": load_image("bun_top_toasted.png"),
    "patty_raw": load_image("patty_raw.png"),
    "patty_overcooked": load_image("patty_overcooked.png"),
    "cheese_melted": load_image("cheese_melted.png"),
    "tomato_sliced": load_image("tomato_sliced.png"),
    "onion_grilled": load_image("onion_grilled.png"),
    "bacon_crispy": load_image("bacon_crispy.png"),
}

# Load sounds
place_sound = load_sound("place.wav", 0.3)
success_sound = load_sound("success.wav", 0.5)
wrong_sound = load_sound("wrong.wav", 0.3)
bonus_sound = load_sound("bonus.wav", 0.5)
levelup_sound = load_sound("levelup.wav", 0.5)
coin_sound = load_sound("coin.wav", 0.4)
sizzle_sound = load_sound("sizzle.wav", 0.3)
chop_sound = load_sound("chop.wav", 0.4)
customer_happy_sound = load_sound("customer_happy.wav", 0.5)
customer_angry_sound = load_sound("customer_angry.wav", 0.5)
purchase_sound = load_sound("purchase.wav", 0.5)
click_sound = load_sound("click.wav", 0.2)

# Font setup
font_small = pygame.font.Font(None, 36)
font_medium = pygame.font.Font(None, 48)
font_large = pygame.font.Font(None, 74)

# Define game states
GAME_STATES = {
    "MENU": 0,
    "TUTORIAL": 1,
    "PLAYING": 2,
    "GAME_OVER": 3,
    "SHOP": 4,
    "PAUSE": 5
}

# Ingredient definitions with properties
INGREDIENT_PROPERTIES = {
    "bun_bottom": {
        "can_toast": True,
        "toasted_name": "bun_bottom_toasted",
        "cook_time": 3.0,  # seconds
        "base_quality": 1.0,
        "quality_range": 0.3,
        "price": 5,
    },
    "bun_top": {
        "can_toast": True,
        "toasted_name": "bun_top_toasted",
        "cook_time": 3.0,
        "base_quality": 1.0,
        "quality_range": 0.3,
        "price": 5,
    },
    "patty": {
        "can_cook": True,
        "raw_name": "patty_raw",
        "overcooked_name": "patty_overcooked",
        "cook_time": 5.0,
        "overcook_time": 8.0,
        "base_quality": 1.0,
        "quality_range": 0.5,
        "price": 10,
    },
    "cheese": {
        "can_melt": True,
        "melted_name": "cheese_melted",
        "melt_time": 2.0,
        "base_quality": 1.0,
        "quality_range": 0.3,
        "price": 8,
    },
    "lettuce": {
        "base_quality": 1.0,
        "quality_range": 0.2,
        "price": 5,
    },
    "tomato": {
        "can_slice": True,
        "sliced_name": "tomato_sliced",
        "slice_time": 2.0,
        "base_quality": 1.0,
        "quality_range": 0.3,
        "price": 7,
    },
    "onion": {
        "can_grill": True,
        "grilled_name": "onion_grilled",
        "grill_time": 4.0,
        "base_quality": 1.0,
        "quality_range": 0.3,
        "price": 6,
    },
    "bacon": {
        "can_cook": True,
        "crispy_name": "bacon_crispy",
        "cook_time": 4.0,
        "base_quality": 1.0,
        "quality_range": 0.4,
        "price": 12,
    }
}

# Create a text box to show messages
class TextBox:
    def __init__(self):
        self.message = ""
        self.color = WHITE
        self.timer = 0
        self.duration = 0
        
    def show(self, message, color=WHITE, duration=2.0):
        self.message = message
        self.color = color
        self.timer = time.time()
        self.duration = duration
        
    def update(self):
        if self.timer > 0 and time.time() - self.timer > self.duration:
            self.timer = 0
            self.message = ""
            
    def draw(self, surface):
        if self.timer > 0:
            text = font_medium.render(self.message, True, self.color)
            # Semi-transparent background
            bg_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            bg_rect.inflate_ip(20, 10)  # Make background slightly larger
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))  # Semi-transparent black
            
            surface.blit(bg_surface, bg_rect.topleft)
            surface.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 200), hover_color=(150, 150, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.disabled = False
        
    def draw(self, surface):
        if self.disabled:
            color = (100, 100, 100)  # Gray for disabled
        else:
            color = self.hover_color if self.is_hovered else self.color
            
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)
        
        text_color = GRAY if self.disabled else WHITE
        text_surf = font_medium.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos) and not self.disabled
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and not self.disabled:
                click_sound.play()
                return True
        return False

class Ingredient(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        super().__init__()
        self.name = name
        self.original_image = ingredient_images[name]
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.original_pos = (x, y)
        self.dragging = False
        self.processing = False
        self.process_start_time = 0
        self.process_time = 0
        self.quality = self.get_base_quality()
        self.wobble = 0
        self.wobble_dir = 1
        self.velocity = Vector2(0, 0)
        
    def get_base_quality(self):
        if self.name in INGREDIENT_PROPERTIES:
            props = INGREDIENT_PROPERTIES[self.name]
            base = props.get("base_quality", 1.0)
            quality_range = props.get("quality_range", 0.2)
            # Return a random quality value around the base
            return base + random.uniform(-quality_range, quality_range)
        return 1.0  # Default quality
        
    def update(self, mouse_pos):
        if self.dragging:
            self.rect.center = mouse_pos
            # Add some physics-based movement
            self.velocity = Vector2(mouse_pos) - Vector2(self.rect.center)
            self.velocity *= 0.2  # Dampen movement
            
        if self.processing:
            # Update processing animation/status
            pass
        
        # Update wobble animation if the ingredient is not being dragged
        if not self.dragging and not self.processing:
            self.wobble += 0.1 * self.wobble_dir
            if abs(self.wobble) > 2:
                self.wobble_dir *= -1
            
            # Apply wobble to position if it's in the burger stack
            if self.rect.centery > HEIGHT - 250:  # Only apply wobble to stacked ingredients
                self.rect.x += self.wobble * 0.5
            
    def reset_position(self):
        self.rect.center = self.original_pos
        self.dragging = False
        self.velocity = Vector2(0, 0)
        
    def start_drag(self):
        self.dragging = True
        
    def stop_drag(self):
        self.dragging = False
        
    def start_processing(self, process_type, duration):
        self.processing = True
        self.process_start_time = time.time()
        self.process_time = duration
        
    def is_processing_done(self):
        if not self.processing:
            return False
        return time.time() - self.process_start_time >= self.process_time
        
    def finish_processing(self, new_name=None):
        self.processing = False
        if new_name and new_name in ingredient_images:
            self.name = new_name
            self.original_image = ingredient_images[new_name]
            self.image = self.original_image.copy()
            # Maintain position
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
            
            # Update quality based on processing
            self.quality *= 1.2  # Processing generally improves quality
        
    def get_copy(self):
        copy = Ingredient(self.name, self.rect.centerx, self.rect.centery)
        copy.quality = self.quality
        return copy
        
    def can_process(self, process_type):
        if self.name not in INGREDIENT_PROPERTIES:
            return False
            
        props = INGREDIENT_PROPERTIES[self.name]
        if process_type == "toast":
            return props.get("can_toast", False)
        elif process_type == "cook":
            return props.get("can_cook", False)
        elif process_type == "slice":
            return props.get("can_slice", False)
        elif process_type == "grill":
            return props.get("can_grill", False)
        elif process_type == "melt":
            return props.get("can_melt", False)
            
        return False

class CookingStation(pygame.sprite.Sprite):
    def __init__(self, station_type, x, y):
        super().__init__()
        self.station_type = station_type
        
        if station_type == "grill":
            self.image = grill_img
        elif station_type == "cutting_board":
            self.image = cutting_board_img
        else:
            # Default image
            self.image = pygame.Surface((100, 100))
            self.image.fill((150, 150, 150))
            
        self.rect = self.image.get_rect(center=(x, y))
        self.current_ingredient = None
        self.process_start_time = 0
        self.process_time = 0
        self.processing = False
        self.progress = 0  # 0 to 1
        self.tool = None  # For cutting board: knife, for grill: spatula
        
        # Set up the tool
        if station_type == "grill":
            self.tool = spatula_img
        elif station_type == "cutting_board":
            self.tool = knife_img
            
    def update(self):
        if self.processing and self.current_ingredient:
            current_time = time.time()
            elapsed = current_time - self.process_start_time
            self.progress = min(1.0, elapsed / self.process_time)
            
            if self.progress >= 1.0:
                self.finish_processing()
                
    def start_processing(self, ingredient):
        if not ingredient:
            return False
            
        if self.station_type == "grill":
            if ingredient.can_process("cook") or ingredient.can_process("grill") or ingredient.can_process("toast"):
                process_type = "cook" if ingredient.can_process("cook") else "grill" if ingredient.can_process("grill") else "toast"
                props = INGREDIENT_PROPERTIES[ingredient.name]
                
                if process_type == "cook":
                    self.process_time = props.get("cook_time", 5.0)
                elif process_type == "grill":
                    self.process_time = props.get("grill_time", 4.0)
                elif process_type == "toast":
                    self.process_time = props.get("cook_time", 3.0)
                    
                self.current_ingredient = ingredient
                self.process_start_time = time.time()
                self.processing = True
                self.progress = 0
                sizzle_sound.play(-1)  # Loop the sizzle sound
                return True
                
        elif self.station_type == "cutting_board":
            if ingredient.can_process("slice"):
                props = INGREDIENT_PROPERTIES[ingredient.name]
                self.process_time = props.get("slice_time", 2.0)
                self.current_ingredient = ingredient
                self.process_start_time = time.time()
                self.processing = True
                self.progress = 0
                chop_sound.play()
                return True
                
        return False
        
    def finish_processing(self):
        if not self.current_ingredient or not self.processing:
            return
            
        # Stop any looping sounds
        sizzle_sound.stop()
        
        # Determine the new state of the ingredient
        props = INGREDIENT_PROPERTIES[self.current_ingredient.name]
        new_name = None
        
        if self.station_type == "grill":
            if self.current_ingredient.can_process("cook"):
                # Check if overcooked
                if self.progress > 1.2:  # Allow slight overcooking
                    new_name = props.get("overcooked_name")
                else:
                    new_name = self.current_ingredient.name.replace("_raw", "")
            elif self.current_ingredient.can_process("grill"):
                new_name = props.get("grilled_name")
            elif self.current_ingredient.can_process("toast"):
                new_name = props.get("toasted_name")
            elif self.current_ingredient.can_process("melt"):
                new_name = props.get("melted_name")
                
        elif self.station_type == "cutting_board":
            if self.current_ingredient.can_process("slice"):
                new_name = props.get("sliced_name")
                
        # Apply the transformation
        if new_name:
            self.current_ingredient.finish_processing(new_name)
            
        self.processing = False
        self.current_ingredient = None
        self.progress = 0
        
    def draw(self, surface):
        # Draw the station
        surface.blit(self.image, self.rect)
        
        # Draw the current ingredient if any
        if self.current_ingredient:
            surface.blit(self.current_ingredient.image, 
                        (self.rect.centerx - self.current_ingredient.image.get_width()//2, 
                         self.rect.centery - self.current_ingredient.image.get_height()//2))
            
        # Draw progress bar if processing
        if self.processing:
            bar_width = self.rect.width * 0.8
            bar_height = 10
            bar_x = self.rect.x + (self.rect.width - bar_width) / 2
            bar_y = self.rect.y - 20
            
            # Background bar
            pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar
            progress_width = bar_width * self.progress
            progress_color = GREEN if self.progress <= 1.0 else RED  # Turn red if overcooking
            pygame.draw.rect(surface, progress_color, (bar_x, bar_y, progress_width, bar_height))
            
            # Draw tool animation
            if self.tool:
                tool_x = self.rect.centerx - self.tool.get_width()//2
                tool_y = self.rect.centery - self.tool.get_height()//2
                
                # Animate the tool based on progress
                if self.station_type == "cutting_board":
                    # Knife moves up and down
                    offset_y = math.sin(time.time() * 10) * 10
                    surface.blit(self.tool, (tool_x, tool_y + offset_y))
                elif self.station_type == "grill":
                    # Spatula moves side to side
                    offset_x = math.sin(time.time() * 5) * 15
                    surface.blit(self.tool, (tool_x + offset_x, tool_y))

class BonusText(pygame.sprite.Sprite):
    def __init__(self, value, x, y):
        super().__init__()
        self.value = value
        self.text = f"+{value}"
        self.color = YELLOW
        self.creation_time = time.time()
        self.lifespan = 2.0  # Seconds to live
        self.y = y
        self.font = font_medium
        self.update_position(x, y)
        
    def update_position(self, x, y):
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        # Float upward
        self.y -= 1
        self.rect.y = int(self.y)
        
        # Fade out when nearing end of lifespan
        age = time.time() - self.creation_time
        if age > self.lifespan * 0.7:
            alpha = int(255 * (1 - (age - self.lifespan * 0.7) / (self.lifespan * 0.3)))
            self.color = (YELLOW[0], YELLOW[1], YELLOW[2], alpha)
            
        if age >= self.lifespan:
            self.kill()

class Customer(pygame.sprite.Sprite):
    def __init__(self, difficulty=1):
        super().__init__()
        self.difficulty = difficulty
        self.satisfaction = 0.5  # 0 to 1
        self.mood = "neutral"
        self.image = customer_images[self.mood]
        self.rect = self.image.get_rect()
        self.order = None
        self.served = False
        self.waiting_time = 0
        self.patience = 60  # seconds
        self.tip = 0
        
    def update(self):
        if not self.served and self.order:
            self.waiting_time += 1/60  # Add one frame worth of seconds
            
            # Update mood based on waiting time
            patience_percent = self.waiting_time / self.patience
            
            if patience_percent < 0.5:
                new_mood = "neutral"
            elif patience_percent < 0.8:
                new_mood = "neutral"  # Still neutral but getting impatient
            else:
                new_mood = "angry"
                
            if new_mood != self.mood:
                self.mood = new_mood
                self.image = customer_images[self.mood]
                
            # Check if customer leaves due to impatience
            if self.waiting_time >= self.patience:
                return "left"
            
    def serve_burger(self, burger_stack):
        if not self.order or self.served:
                return False
            
        # Check if burger matches order
        order_quality = self.order.check_burger(burger_stack)
        
        if order_quality > 0:
            self.served = True
            
            # Calculate satisfaction based on burger quality and waiting time
            quality_factor = order_quality / 1.0  # Normalize to 0-1
            time_factor = max(0, 1 - (self.waiting_time / self.patience))
            
            # Overall satisfaction
            self.satisfaction = (quality_factor * 0.7) + (time_factor * 0.3)
            
            # Update mood
            if self.satisfaction > 0.8:
                self.mood = "happy"
                customer_happy_sound.play()
            elif self.satisfaction > 0.4:
                self.mood = "neutral"
            else:
                self.mood = "angry"
                customer_angry_sound.play()
                
            self.image = customer_images[self.mood]
            
            # Calculate tip
            if self.satisfaction > 0.5:
                # Better satisfaction = better tip
                base_tip = int(20 * self.satisfaction)
                self.tip = base_tip
                
            return True
        else:
            # Wrong burger
            self.mood = "angry"
            self.image = customer_images[self.mood]
            customer_angry_sound.play()
            return False

class Order:
    def __init__(self, difficulty=1):
        # Generate an order based on difficulty
        self.ingredients = ["bun_bottom"]
        
        # Always include patty
        if random.random() < 0.7:  # 70% chance for regular patty
            self.ingredients.append("patty")
        else:  # 30% chance for cooked variations
            self.ingredients.append(random.choice(["patty", "patty_overcooked"]))
        
        # Add random ingredients based on difficulty
        possible_ingredients = [
            "cheese", "cheese_melted",
            "lettuce",
            "tomato", "tomato_sliced",
            "onion", "onion_grilled",
            "bacon", "bacon_crispy"
        ]
        
        # Harder difficulties have more ingredients
        num_extras = random.randint(1, min(difficulty + 1, len(possible_ingredients) // 2))
        
        # Select unique base ingredients (no duplicates of same category)
        base_ingredients = []
        for _ in range(num_extras):
            available = [ing for ing in possible_ingredients 
                        if ing.split('_')[0] not in [x.split('_')[0] for x in base_ingredients]]
            if available:
                selected = random.choice(available)
                base_ingredients.append(selected)
        
        # For each base ingredient, decide if we want the processed version
        for ing in base_ingredients:
            base_name = ing.split('_')[0]
            processed_version = None
            
            # Find processed version if it exists
            for p_ing in possible_ingredients:
                if p_ing.startswith(base_name + '_'):
                    processed_version = p_ing
                    break
            
            # Higher difficulty = higher chance of processed ingredients
            if processed_version and random.random() < (0.3 + difficulty * 0.1):
                self.ingredients.append(processed_version)
            else:
                self.ingredients.append(base_name)
        
        # Always end with top bun, sometimes toasted in higher difficulties
        if difficulty > 2 and random.random() < 0.4:
            self.ingredients.append("bun_top_toasted")
        else:
            self.ingredients.append("bun_top")
        
        # Print the ingredients order for debugging
        print(f"New order created with ingredients: {self.ingredients}")
        
        self.time_limit = max(60 - (difficulty * 5), 30)  # Decreasing time based on difficulty
        self.score_value = 50 + (difficulty * 25)  # Higher score for harder orders
        self.start_time = time.time()
        self.completed = False
        
    def time_remaining(self):
        if self.completed:
            return self.time_limit  # Return full time if completed
        elapsed = time.time() - self.start_time
        return max(0, self.time_limit - elapsed)
    
    def time_percent(self):
        return self.time_remaining() / self.time_limit * 100
    
    def is_expired(self):
        return not self.completed and self.time_remaining() <= 0
    
    def check_burger(self, burger_stack):
        # Convert burger stack to list of names
        burger_names = [item.name for item in burger_stack]
        
        # Calculate a quality score for this burger
        if len(burger_names) != len(self.ingredients):
            return 0  # Wrong number of ingredients
            
        quality_score = 0
        all_correct = True
        
        for i, ingredient in enumerate(self.ingredients):
            required_base = ingredient.split('_')[0]
            actual_base = burger_names[i].split('_')[0]
            
            if required_base != actual_base:
                all_correct = False
                break
                
            # Check exact match (including processing state)
            if ingredient == burger_names[i]:
                quality_score += 1.0  # Perfect match
            else:
                # Base ingredient is correct but processing state is different
                # This is partially acceptable but with lower quality
                quality_score += 0.5
                
        # Calculate final quality: 0 for wrong burger, otherwise average quality of ingredients
        if not all_correct:
            return 0
        
        return quality_score / len(self.ingredients)
        
    def complete(self):
        self.completed = True
        
    def draw(self, surface, x, y, width=180, height=300):
        # Draw order card
        order_card = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, LIGHT_BLUE, order_card, border_radius=10)
        pygame.draw.rect(surface, WHITE, order_card, 3, border_radius=10)
        
        # Draw order title
        order_title = font_small.render("ORDER", True, BLACK)
        surface.blit(order_title, (order_card.centerx - order_title.get_width()//2, order_card.y + 20))
        
        # Draw time bar
        time_bar_bg = pygame.Rect(order_card.x + 20, order_card.y + 60, order_card.width - 40, 20)
        time_bar_fill = pygame.Rect(order_card.x + 20, order_card.y + 60, 
                                  int((order_card.width - 40) * self.time_percent() / 100), 20)
        
        pygame.draw.rect(surface, GRAY, time_bar_bg)
        
        # Color changes based on time remaining
        if self.time_percent() < 30:
            bar_color = RED
        elif self.time_percent() < 60:
            bar_color = YELLOW
        else:
            bar_color = GREEN
            
        pygame.draw.rect(surface, bar_color, time_bar_fill)
        
        # Draw time text
        time_text = font_small.render(f"{int(self.time_remaining())}s", True, BLACK)
        surface.blit(time_text, (order_card.centerx - time_text.get_width()//2, order_card.y + 85))
        
        # Draw ingredients list
        y_offset = order_card.y + 120
        for ingredient_name in self.ingredients:
            if ingredient_name in ingredient_images:
                img = pygame.transform.scale(ingredient_images[ingredient_name], 
                                            (ingredient_images[ingredient_name].get_width() // 2,
                                             ingredient_images[ingredient_name].get_height() // 2))
                surface.blit(img, (order_card.centerx - img.get_width()//2, y_offset))
                y_offset += img.get_height() + 5

class ShopItem:
    def __init__(self, name, description, price, item_type, unlocks=None):
        self.name = name
        self.description = description
        self.price = price
        self.item_type = item_type  # "ingredient", "upgrade", "station"
        self.unlocks = unlocks  # For ingredients, what it unlocks
        self.button = None  # Will be set when displayed
        
    def can_afford(self, money):
        return money >= self.price
        
    def purchase(self, game_data):
        if not self.can_afford(game_data["money"]):
            return False
            
        # Process the purchase
        game_data["money"] -= self.price
        
        if self.item_type == "ingredient":
            if self.unlocks in game_data["locked_ingredients"]:
                game_data["locked_ingredients"].remove(self.unlocks)
                game_data["unlocked_ingredients"].append(self.unlocks)
                
        elif self.item_type == "upgrade":
            if self.unlocks in game_data["upgrades"]:
                game_data["upgrades"][self.unlocks] += 1
                
        save_game_data(game_data)
        purchase_sound.play()
        return True

class TutorialStep:
    def __init__(self, title, description, target_area=None, completion_action=None):
        self.title = title
        self.description = description
        self.target_area = target_area  # Rect to highlight
        self.completion_action = completion_action  # Function that returns True when step is complete
        self.completed = False
        
    def draw(self, surface):
        # Draw tutorial card
        tutorial_card = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(surface, LIGHT_BLUE, tutorial_card, border_radius=10)
        pygame.draw.rect(surface, WHITE, tutorial_card, 3, border_radius=10)
        
        # Draw title
        title_text = font_medium.render(self.title, True, BLACK)
        surface.blit(title_text, (tutorial_card.centerx - title_text.get_width()//2, tutorial_card.y + 20))
        
        # Draw description (multi-line)
        line_height = 30
        lines = self.description.split('\n')
        
        for i, line in enumerate(lines):
            line_text = font_small.render(line, True, BLACK)
            surface.blit(line_text, (tutorial_card.centerx - line_text.get_width()//2, 
                                    tutorial_card.y + 70 + i * line_height))
        
        # Draw continue button
        continue_button = pygame.Rect(tutorial_card.centerx - 75, tutorial_card.bottom - 60, 150, 40)
        pygame.draw.rect(surface, (100, 100, 200), continue_button, border_radius=5)
        pygame.draw.rect(surface, WHITE, continue_button, 2, border_radius=5)
        
        button_text = font_small.render("Continue", True, WHITE)
        surface.blit(button_text, (continue_button.centerx - button_text.get_width()//2, 
                                  continue_button.centery - button_text.get_height()//2))
        
        # Highlight target area if any
        if self.target_area:
            # Draw a semi-transparent highlight around the target
            highlight = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            highlight.fill((0, 0, 0, 150))  # Dark overlay
            
            # Cut out the target area
            target_rect = pygame.Rect(self.target_area)
            target_rect.inflate_ip(20, 20)  # Make highlight slightly larger than target
            highlight.fill((0, 0, 0, 0), target_rect)  # Transparent hole
            
            # Draw a glowing border around the target
            pygame.draw.rect(highlight, (255, 255, 0, 180), target_rect, 4, border_radius=5)
            
            surface.blit(highlight, (0, 0))
            
        return continue_button

class Game:
    def __init__(self):
        self.state = GAME_STATES["MENU"]
        self.score = 0
        self.level = 1
        self.money = 0
        self.ingredients_shelf = pygame.sprite.Group()
        self.burger_stack = []
        self.selected_ingredient = None
        self.burger_base_y = HEIGHT - 150
        self.order = None
        self.next_level_time = 0
        self.text_box = TextBox()
        self.bonus_texts = pygame.sprite.Group()
        self.time_bonus = 0
        self.game_data = load_game_data()
        self.customers = []
        self.current_customer = None
        self.cooking_stations = pygame.sprite.Group()
        self.dragged_to_station = None
        
        # Set up cooking stations
        self.grill = CookingStation("grill", WIDTH - 200, 150)
        self.cutting_board = CookingStation("cutting_board", WIDTH - 200, 300)
        self.cooking_stations.add(self.grill, self.cutting_board)
        
        # Create buttons
        self.play_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, "PLAY")
        self.retry_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, "RETRY")
        self.shop_button = Button(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 60, "SHOP")
        self.back_button = Button(50, HEIGHT - 70, 100, 50, "BACK")
        
        # Shop items
        self.shop_items = []
        
        # Tutorial
        self.tutorial_steps = []
        self.current_tutorial_step = 0
        
        self.setup_shop_items()
        self.setup_tutorial()
        self.setup_ingredients_shelf()
        
    def setup_shop_items(self):
        # Ingredient unlocks
        for ingredient_name in self.game_data["locked_ingredients"]:
            props = INGREDIENT_PROPERTIES.get(ingredient_name, {})
            price = props.get("price", 10) * 10  # Base price x10 for unlock
            
            self.shop_items.append(
                ShopItem(
                    name=ingredient_name.replace("_", " ").title(),
                    description=f"Unlock {ingredient_name.replace('_', ' ')} for your burgers",
                    price=price,
                    item_type="ingredient",
                    unlocks=ingredient_name
                )
            )
            
        # Upgrades
        upgrade_descriptions = {
            "grill_speed": ("Faster Cooking", "Speed up all cooking processes"),
            "customer_patience": ("Customer Patience", "Customers will wait longer"),
            "tips": ("Better Tips", "Increase tips from satisfied customers")
        }
        
        for upgrade, (name, desc) in upgrade_descriptions.items():
            level = self.game_data["upgrades"][upgrade]
            price = 50 * (level + 1)  # Price increases with level
            
            self.shop_items.append(
                ShopItem(
                    name=f"{name} (Lvl {level+1})",
                    description=desc,
                    price=price,
                    item_type="upgrade",
                    unlocks=upgrade
                )
            )
        
    def setup_tutorial(self):
        if self.game_data["tutorial_completed"]:
            return
            
        # Create tutorial steps
        self.tutorial_steps = [
            TutorialStep(
                "Welcome to Burger Simulator!",
                "In this game, you'll be making burgers to satisfy customers.\nFollow the steps to learn how to play."
            ),
            TutorialStep(
                "Ingredients",
                "These are your ingredients on the left.\nClick and drag them to build your burger."
            ),
            TutorialStep(
                "Cooking Stations",
                "Use these stations to improve your ingredients.\nThe grill cooks patties and toasts buns.\nThe cutting board slices vegetables."
            ),
            TutorialStep(
                "Orders",
                "Each customer will have a specific burger order.\nMake burgers according to the order shown here."
            ),
            TutorialStep(
                "Time Limit",
                "You have a limited time to complete each order.\nFaster completion earns time bonus points!"
            ),
            TutorialStep(
                "Earn Money",
                "Satisfied customers leave tips.\nUse money to unlock new ingredients and upgrades."
            ),
            TutorialStep(
                "Ready to Begin?",
                "Let's make some delicious burgers!\nGood luck!"
            )
        ]
        
    def start_tutorial(self):
        if self.tutorial_steps and not self.game_data["tutorial_completed"]:
            self.state = GAME_STATES["TUTORIAL"]
            self.current_tutorial_step = 0
        else:
            self.start_game()
            
    def next_tutorial_step(self):
        self.current_tutorial_step += 1
        if self.current_tutorial_step >= len(self.tutorial_steps):
            # Tutorial complete
            self.game_data["tutorial_completed"] = True
            save_game_data(self.game_data)
            self.start_game()
        
    def setup_ingredients_shelf(self):
        self.ingredients_shelf.empty()
        
        # Position ingredients shelf on the left side
        shelf_x = 90
        shelf_y = 150
        
        # Add unlocked ingredients to the shelf in a vertical column
        ingredients = self.game_data["unlocked_ingredients"]
        
        for i, name in enumerate(ingredients):
            y = shelf_y + i * 50
            self.ingredients_shelf.add(Ingredient(name, shelf_x, y))
    
    def start_game(self):
        self.state = GAME_STATES["PLAYING"]
        self.score = 0
        self.level = 1
        self.burger_stack = []
        self.money = self.game_data["money"]  # Load saved money
        self.create_new_customer()
        self.text_box.show("Let's make some burgers!", GREEN, 3.0)
    
    def create_new_customer(self):
        self.current_customer = Customer(difficulty=self.level)
        self.current_customer.order = Order(difficulty=self.level)
        self.current_customer.rect.center = (WIDTH - 80, 80)
        
        # Adjust customer patience based on upgrades
        patience_upgrade = self.game_data["upgrades"]["customer_patience"]
        self.current_customer.patience += patience_upgrade * 10  # +10 seconds per level
        
        self.text_box.show(f"New customer (Level {self.level})!", GREEN, 2.0)
    
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT:
                return False
                
            if self.state == GAME_STATES["MENU"]:
                if self.play_button.is_clicked(event):
                    self.start_tutorial()
                elif self.shop_button.is_clicked(event):
                    self.state = GAME_STATES["SHOP"]
                    
            elif self.state == GAME_STATES["TUTORIAL"]:
                # Handle tutorial interaction
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    continue_button = self.tutorial_steps[self.current_tutorial_step].draw(pygame.Surface((0,0)))
                    if continue_button.collidepoint(event.pos):
                        self.next_tutorial_step()
                    
            elif self.state == GAME_STATES["SHOP"]:
                if self.back_button.is_clicked(event):
                    self.state = GAME_STATES["MENU"]
                    
                # Handle shop item purchase
                for item in self.shop_items:
                    if item.button and item.button.is_clicked(event):
                        if item.purchase(self.game_data):
                            self.money = self.game_data["money"]
                            # Refresh shop items after purchase
                            self.setup_shop_items()
                            # Update ingredients shelf if needed
                            self.setup_ingredients_shelf()
                
            elif self.state == GAME_STATES["GAME_OVER"]:
                if self.retry_button.is_clicked(event):
                    self.state = GAME_STATES["MENU"]
                elif self.shop_button.is_clicked(event):
                    self.state = GAME_STATES["SHOP"]
                    
            elif self.state == GAME_STATES["PLAYING"]:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if we're clicking an ingredient on the shelf
                    for ingredient in self.ingredients_shelf:
                        if ingredient.rect.collidepoint(event.pos):
                            # Create a copy of the ingredient
                            self.selected_ingredient = ingredient.get_copy()
                            self.selected_ingredient.start_drag()
                            break
                            
                    # Check if we're clicking on a cooking station with an ingredient
                    for station in self.cooking_stations:
                        if station.rect.collidepoint(event.pos) and station.current_ingredient:
                            # Take the ingredient from the station
                            self.selected_ingredient = station.current_ingredient
                            self.selected_ingredient.start_drag()
                            station.current_ingredient = None
                            station.processing = False
                            break
                
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.selected_ingredient:
                        # Check if we're dropping on a cooking station
                        for station in self.cooking_stations:
                            if station.rect.collidepoint(event.pos) and not station.current_ingredient:
                                # Place on station
                                station.start_processing(self.selected_ingredient)
                                self.selected_ingredient = None
                                self.dragged_to_station = True
                                break
                                
                        if not self.dragged_to_station and self.selected_ingredient:
                            # Check if we're dropping on the burger area
                            if self.selected_ingredient.rect.bottom > HEIGHT - 200 and self.selected_ingredient.rect.centerx > WIDTH//4 and self.selected_ingredient.rect.centerx < 3*WIDTH//4:
                                # Place the ingredient on the burger stack
                                y_pos = self.burger_base_y - sum(item.rect.height for item in self.burger_stack)
                                self.selected_ingredient.rect.midbottom = (WIDTH//2, y_pos)
                                self.burger_stack.append(self.selected_ingredient)
                                place_sound.play()
                                
                                # Check if the burger is complete (has a top bun)
                                if self.selected_ingredient.name.startswith("bun_top"):
                                    self.check_burger_complete()
                            else:
                                # Not dropping on burger area or station, discard
                                pass
                            
                            self.selected_ingredient = None
                            
                        self.dragged_to_station = False
        
        # Update buttons based on mouse position
        if self.state == GAME_STATES["MENU"]:
            self.play_button.update(mouse_pos)
            self.shop_button.update(mouse_pos)
        elif self.state == GAME_STATES["SHOP"]:
            self.back_button.update(mouse_pos)
            # Update shop item buttons
            for item in self.shop_items:
                if item.button:
                    item.button.update(mouse_pos)
                    item.button.disabled = not item.can_afford(self.money)
        elif self.state == GAME_STATES["GAME_OVER"]:
            self.retry_button.update(mouse_pos)
            self.shop_button.update(mouse_pos)
            
        return True
    
    def check_burger_complete(self):
        if len(self.burger_stack) < 3:
            self.text_box.show("Your burger is too small!", RED, 2.0)
            wrong_sound.play()
            return
            
        if not self.current_customer:
            return
            
        # Attempt to serve the burger to the customer
        if self.current_customer.serve_burger(self.burger_stack):
            # Burger accepted
            success_sound.play()
            
            # Calculate scores and money
            base_score = self.current_customer.order.score_value
            satisfaction_bonus = int(self.current_customer.satisfaction * 100)
            time_bonus = int(self.current_customer.order.time_remaining() * 2)
            
            total_score = base_score + satisfaction_bonus + time_bonus
            self.score += total_score
            
            # Add customer tip to money
            tip_multiplier = 1.0 + (0.2 * self.game_data["upgrades"]["tips"])  # 20% increase per upgrade
            self.money += int(self.current_customer.tip * tip_multiplier)
            self.game_data["money"] = self.money
            save_game_data(self.game_data)
            
            # Show bonus text
            bonus_text = BonusText(total_score, WIDTH//2, HEIGHT//2)
            self.bonus_texts.add(bonus_text)
            
            if self.current_customer.tip > 0:
                tip_text = BonusText(int(self.current_customer.tip * tip_multiplier), WIDTH//2, HEIGHT//2 + 40)
                tip_text.text = f"+${tip_text.value}"
                self.bonus_texts.add(tip_text)
                coin_sound.play()
            
            # Show success message
            satisfaction_text = "perfect" if self.current_customer.satisfaction > 0.9 else "good" if self.current_customer.satisfaction > 0.6 else "acceptable"
            self.text_box.show(f"{satisfaction_text.title()} burger! +{time_bonus} time bonus!", GREEN, 2.0)
            
            # Level up
            self.level += 1
            
            # Wait before next customer
            self.next_level_time = time.time() + 2  # Wait 2 seconds before next customer
        else:
            # Wrong burger!
            wrong_sound.play()
            self.text_box.show("Wrong burger! Try again.", RED, 2.0)
            # Clear the stack after a delay
            self.next_level_time = time.time() + 1.5
    
    def clear_burger_stack(self):
        self.burger_stack = []
        self.next_level_time = 0
    
    def update(self):
        # Update text box
        self.text_box.update()
        
        # Update bonus texts
        self.bonus_texts.update()
        
        if self.state == GAME_STATES["PLAYING"]:
            # Update ingredients
            self.ingredients_shelf.update(pygame.mouse.get_pos())
            
            # Update cooking stations
            self.cooking_stations.update()
            
            if self.selected_ingredient:
                self.selected_ingredient.update(pygame.mouse.get_pos())
            
            # Update customer
            if self.current_customer:
                customer_status = self.current_customer.update()
                
                # Check if customer left due to impatience
                if customer_status == "left":
                    customer_angry_sound.play()
                    self.text_box.show("Customer left angry!", RED, 2.0)
                    self.state = GAME_STATES["GAME_OVER"]
            
            # Check if it's time for a new customer
            if self.next_level_time > 0 and time.time() > self.next_level_time:
                if self.current_customer and self.current_customer.served:
                    # Start a new level with a new customer
                    levelup_sound.play()
                    self.create_new_customer()
                else:
                    # Clear failed burger and try again
                    self.clear_burger_stack()
                
                self.next_level_time = 0
            
            # Check if the current order has expired
            if self.current_customer and self.current_customer.order.is_expired() and self.next_level_time == 0:
                self.text_box.show("Time's up! Game Over.", RED, 3.0)
                self.state = GAME_STATES["GAME_OVER"]
                
            # Update high score if needed
            if self.score > self.game_data["high_score"]:
                self.game_data["high_score"] = self.score
                save_game_data(self.game_data)
    
    def draw(self, surface):
        if self.state == GAME_STATES["MENU"]:
            # Draw menu
            surface.blit(menu_bg, (0, 0))
            
            # Draw title
            title_text = font_large.render("Burger Bun Bakery", True, WHITE)
            subtitle_text = font_medium.render("Simulator", True, WHITE)
            
            surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))
            surface.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//3 + 80))
            
            # Draw high score
            high_score_text = font_small.render(f"High Score: {self.game_data['high_score']}", True, WHITE)
            surface.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//3 + 130))
            
            # Draw play button
            self.play_button.draw(surface)
            
            # Draw shop button
            self.shop_button.draw(surface)
            
            # Draw instructions
            instructions = [
                "- Drag ingredients to build burgers",
                "- Use cooking stations to prepare ingredients",
                "- Follow customer orders carefully",
                "- Earn money for upgrades and new ingredients!"
            ]
            
            for i, line in enumerate(instructions):
                instr_text = font_small.render(line, True, WHITE)
                surface.blit(instr_text, (WIDTH//2 - instr_text.get_width()//2, HEIGHT//2 + 190 + i*30))
            
        elif self.state == GAME_STATES["TUTORIAL"]:
            # Draw game background
            surface.blit(background, (0, 0))
            
            # Draw current tutorial step
            if self.current_tutorial_step < len(self.tutorial_steps):
                step = self.tutorial_steps[self.current_tutorial_step]
                step.draw(surface)
            
        elif self.state == GAME_STATES["SHOP"]:
            # Draw shop background
            surface.blit(shop_bg, (0, 0))
            
            # Draw title
    
            title_text = font_large.render("Shop", True, WHITE)
            surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
            
            # Draw money
            money_text = font_medium.render(f"Money: ${self.money}", True, YELLOW)
            surface.blit(money_text, (WIDTH//2 - money_text.get_width()//2, 120))
            
            # Draw back button
            self.back_button.draw(surface)
            
            # Draw shop items in a grid
            items_per_row = 3
            item_width = 200
            item_height = 150
            item_margin = 20
            start_x = (WIDTH - (items_per_row * (item_width + item_margin) - item_margin)) // 2
            start_y = 180
            
            for i, item in enumerate(self.shop_items):
                row = i // items_per_row
                col = i % items_per_row
                
                x = start_x + col * (item_width + item_margin)
                y = start_y + row * (item_height + item_margin)
                
                # Create item card
                card_rect = pygame.Rect(x, y, item_width, item_height)
                
                # Create or update button
                if not item.button:
                    item.button = Button(x + item_width//2 - 50, y + item_height - 40, 100, 30, f"${item.price}")
                else:
                    item.button.rect = pygame.Rect(x + item_width//2 - 50, y + item_height - 40, 100, 30)
                    item.button.text = f"${item.price}"
                
                # Draw item card
                pygame.draw.rect(surface, LIGHT_BLUE, card_rect, border_radius=10)
                pygame.draw.rect(surface, WHITE, card_rect, 2, border_radius=10)
                
                # Draw item name
                name_text = font_small.render(item.name, True, BLACK)
                surface.blit(name_text, (x + item_width//2 - name_text.get_width()//2, y + 10))
                
                # Draw item description (truncated if needed)
                desc_text = font_small.render(item.description[:20] + "..." if len(item.description) > 20 else item.description, True, BLACK)
                surface.blit(desc_text, (x + item_width//2 - desc_text.get_width()//2, y + 40))
                
                # Draw purchase button
                item.button.disabled = not item.can_afford(self.money)
                item.button.draw(surface)
            
        elif self.state == GAME_STATES["PLAYING"] or self.state == GAME_STATES["GAME_OVER"]:
            # Draw game background
            surface.blit(background, (0, 0))
            
            # Draw table at the bottom
            surface.blit(table_img, (0, HEIGHT - 200))
            
            # Draw score, level and money at the top center
            # Create a background for score text to make it visible
            header_bg = pygame.Surface((400, 70), pygame.SRCALPHA)
            header_bg.fill((0, 0, 0, 150))  # Semi-transparent black
            
            surface.blit(header_bg, (WIDTH//2 - 200, 10))
            
            score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
            level_text = font_medium.render(f"Level: {self.level}", True, WHITE)
            money_text = font_medium.render(f"${self.money}", True, YELLOW)
            
            surface.blit(score_text, (WIDTH//2 - 150, 15))
            surface.blit(level_text, (WIDTH//2 - 150, 50))
            surface.blit(money_text, (WIDTH//2 + 100, 35))
            surface.blit(coin_img, (WIDTH//2 + 80, 40))
            
            # Draw cooking stations
            for station in self.cooking_stations:
                station.draw(surface)
            
            # Draw customer
            if self.current_customer:
                surface.blit(self.current_customer.image, self.current_customer.rect)
            
            # Draw order
            if self.current_customer and self.current_customer.order:
                self.current_customer.order.draw(surface, WIDTH - 200, 20)
            
            # Draw burger stack
            for ingredient in self.burger_stack:
                surface.blit(ingredient.image, ingredient.rect)
            
            # Draw ingredients shelf
            self.ingredients_shelf.draw(surface)
            
            # Draw dragged ingredient (should be on top of everything)
            if self.selected_ingredient:
                surface.blit(self.selected_ingredient.image, self.selected_ingredient.rect)
            
            # Draw bonus texts
            self.bonus_texts.draw(surface)
            
            # Draw text box
            self.text_box.draw(surface)
            
            # Draw game over
            if self.state == GAME_STATES["GAME_OVER"]:
                # Semi-transparent overlay
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                surface.blit(overlay, (0, 0))
                
                # Game over text
                gameover_text = font_large.render("Game Over!", True, WHITE)
                score_text = font_medium.render(f"Final Score: {self.score}", True, WHITE)
                level_text = font_medium.render(f"You reached Level {self.level}", True, WHITE)
                money_text = font_medium.render(f"Money earned: ${self.money - self.game_data['money']}", True, YELLOW)
                
                surface.blit(gameover_text, (WIDTH//2 - gameover_text.get_width()//2, HEIGHT//3))
                surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//3 + 80))
                surface.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//3 + 130))
                surface.blit(money_text, (WIDTH//2 - money_text.get_width()//2, HEIGHT//3 + 180))
                
                # Draw retry button
                self.retry_button.draw(surface)
                
                # Draw shop button
                self.shop_button.rect.y = self.retry_button.rect.bottom + 20
                self.shop_button.draw(surface)

# Main game function
def main():
    game = Game()
    running = True
    
    # Print instructions for the user
    print("\n=== BURGER BUN BAKERY SIMULATOR ===")
    print("\nEnhanced Edition with:")
    print("- Cooking stations for ingredient preparation")
    print("- Customer satisfaction system")
    print("- Money and shop system")
    print("- Upgrades and unlockable ingredients")
    print("- Physics-based ingredient stacking")
    print("\nINSTRUCTIONS:")
    print("1. Click on ingredients from the shelf on the left")
    print("2. Drag to cooking stations to prepare them (grill, cutting board)")
    print("3. Drag prepared ingredients to build your burger")
    print("4. Follow customer orders and satisfy them for tips")
    print("5. Use earned money to unlock upgrades and new ingredients")
    print("\nCUSTOMIZATION OPTIONS:")
    print("- Add custom images to the 'images' folder")
    print("- Add sound effects to the 'sounds' folder")
    print("\nHave fun baking burgers!\n")
    
    while running:
        events = pygame.event.get()
        running = game.handle_events(events)
        
        game.update()
        
        screen.fill(BLACK)
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()