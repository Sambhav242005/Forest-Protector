import asyncio
import pygame
import math
import random
import time
import os
from enum import Enum
# Initialize Pygame
pygame.init()
# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
PANEL_WIDTH = 300  # Width of the side panel
GAME_FIELD_WIDTH = SCREEN_WIDTH - PANEL_WIDTH  # Width of the game field
# Colors
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
BLUE = (64, 164, 223)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
PURPLE = (128, 0, 128)
MAGIC_PURPLE = (147, 0, 211)
CANNON_GRAY = (105, 105, 105)
ARCHER_GREEN = (0, 128, 0)
GOLD = (255, 215, 0)
DARK_BROWN = (101, 67, 33)
# Game settings
GRID_SIZE = 20
GRID_COLS = GAME_FIELD_WIDTH // GRID_SIZE
GRID_ROWS = SCREEN_HEIGHT // GRID_SIZE
PATH_WIDTH = 60
# Button class for UI elements
class Button:
    def __init__(self, x, y, width, height, text, color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False
        self.font = pygame.font.SysFont(None, 24)
        
    def draw(self, screen):
        # Draw button with hover effect
        color = LIGHT_GRAY if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
# Tower types
class TowerType(Enum):
    ARCHER = 1
    CANNON = 2
    MAGIC = 3
# Tower settings
TOWER_SETTINGS = {
    TowerType.ARCHER: {
        "cost": 35,
        "damage": 20,
        "range": 150,
        "fire_rate": 3,  # Shots per second
        "accuracy": 1,
        "color": ARCHER_GREEN,
        "projectile_speed": 8,
        "max_level": 5  # Maximum upgrade level
    },
    TowerType.CANNON: {
        "cost": 60,
        "damage": 40,
        "range": 100,
        "fire_rate": 1.25,  # Shots per second
        "accuracy": 0.65,
        "color": CANNON_GRAY,
        "projectile_speed": 5,
        "max_level": 3  # Maximum upgrade level
    },
    TowerType.MAGIC: {
        "cost": 90,
        "damage": 30,
        "range": 120,
        "fire_rate": 2.25,  # Shots per second
        "accuracy": 0.95,
        "color": MAGIC_PURPLE,
        "projectile_speed": 10,
        "max_level": 2  # Maximum upgrade level
    }
}
# Enemy settings
ENEMY_TYPES = {
    "goblin": {
        "health": 50,
        "speed": 3.0,
        "reward": 25,
        "size": 20,
        "color": (200, 50, 50)
    },
    "orc": {
        "health": 75,
        "speed": 2.5,
        "reward": 35,
        "size": 30,
        "color": (100, 50, 50)
    },
    "troll": {
        "health": 100,
        "speed": 2.0,
        "reward": 50,
        "size": 25,
        "color": (50, 25, 25)
    }
}
# Wave settings
WAVE_DELAY = 3  # Seconds between waves
ENEMIES_PER_WAVE = 5
WAVE_BONUS = 500
GAME_TIME_LIMIT = 300  # 5 minutes in seconds
# Difficulty settings
DIFFICULTY_SETTINGS = {
    1: {  # Easy
        "name": "Easy",
        "enemy_health_multiplier": 0.8,
        "enemy_speed_multiplier": 0.9,
        "enemy_reward_multiplier": 1.2,
        "tower_upgrade_effectiveness": 1.2,
        "starting_money": 200,
        "starting_lives": 4
    },
    2: {  # Normal
        "name": "Normal",
        "enemy_health_multiplier": 1.0,
        "enemy_speed_multiplier": 1.0,
        "enemy_reward_multiplier": 1.0,
        "tower_upgrade_effectiveness": 1.0,
        "starting_money": 150,
        "starting_lives": 3
    },
    3: {  # Hard
        "name": "Hard",
        "enemy_health_multiplier": 1.3,
        "enemy_speed_multiplier": 1.1,
        "enemy_reward_multiplier": 0.9,
        "tower_upgrade_effectiveness": 0.8,
        "starting_money": 120,
        "starting_lives": 2
    },
    4: {  # Expert
        "name": "Expert",
        "enemy_health_multiplier": 1.6,
        "enemy_speed_multiplier": 1.2,
        "enemy_reward_multiplier": 0.8,
        "tower_upgrade_effectiveness": 0.7,
        "starting_money": 100,
        "starting_lives": 2
    },
    5: {  # Insane
        "name": "Insane",
        "enemy_health_multiplier": 2.0,
        "enemy_speed_multiplier": 1.4,
        "enemy_reward_multiplier": 0.7,
        "tower_upgrade_effectiveness": 0.6,
        "starting_money": 80,
        "starting_lives": 1
    }
}
class Projectile:
    def __init__(self, x, y, target, damage, projectile_speed, color):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = projectile_speed
        self.color = color
        self.active = True
        
    def update(self, game_speed):
        if not self.target.alive:
            self.active = False
            return
            
        # Calculate direction to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 5:  # Hit the target
            self.target.take_damage(self.damage)
            self.active = False
        else:
            # Move towards target
            dx /= distance
            dy /= distance
            self.x += dx * self.speed * game_speed
            self.y += dy * self.speed * game_speed
    
    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)
class Tower:
    def __init__(self, x, y, tower_type, difficulty=1):
        self.x = x
        self.y = y
        self.type = tower_type
        self.settings = TOWER_SETTINGS[tower_type]
        self.damage = self.settings["damage"]
        self.range = self.settings["range"]
        self.fire_rate = self.settings["fire_rate"]
        self.accuracy = self.settings["accuracy"]
        self.last_shot = 0
        self.level = 1
        self.target = None
        self.selected = False
        self.projectiles = []
        self.projectile_speed = self.settings["projectile_speed"]
        self.color = self.settings["color"]
        self.total_cost = self.settings["cost"]  # Track total cost for refunds
        self.max_level = self.settings["max_level"]  # Maximum upgrade level
        self.difficulty = difficulty
        self.upgrade_effectiveness = DIFFICULTY_SETTINGS[difficulty]["tower_upgrade_effectiveness"]
        
        # Load tower image
        self.use_image = False
        try:
            # Construct image path based on tower type
            image_path = f"assets/{tower_type.name.lower()}.png"
            self.image = pygame.image.load(image_path).convert_alpha()
            # Scale image to appropriate size (40x40 pixels)
            self.image = pygame.transform.scale(self.image, (48 , 72))
            self.use_image = True
            print(f"Loaded tower image: {image_path}")
        except pygame.error as e:
            print(f"Could not load tower image {image_path}: {e}")
            self.use_image = False
        except Exception as e:
            print(f"Error loading tower image: {e}")
            self.use_image = False
        
    def update(self, enemies, current_time, game_speed):
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(game_speed)
            if not projectile.active:
                self.projectiles.remove(projectile)
        
        # Find target
        self.target = None
        min_distance = float('inf')
        
        for enemy in enemies:
            distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if distance < self.range and distance < min_distance:
                min_distance = distance
                self.target = enemy
        
        # Shoot at target
        if self.target and current_time - self.last_shot > 1 / (self.fire_rate * game_speed):
            self.last_shot = current_time
            
            # Check if shot hits based on accuracy
            if random.random() < self.accuracy:
                # For magic tower, predict enemy position
                if self.type == TowerType.MAGIC:
                    # Calculate time to reach enemy
                    distance = math.sqrt((self.target.x - self.x)**2 + (self.target.y - self.y)**2)
                    time_to_hit = distance / (self.projectile_speed * game_speed)
                    
                    # Predict enemy position
                    predicted_x = self.target.x
                    predicted_y = self.target.y
                    
                    # Get current and next waypoints
                    if self.target.path_index < len(self.target.path) - 1:
                        current = self.target.path[self.target.path_index]
                        next_point = self.target.path[self.target.path_index + 1]
                        
                        # Calculate direction
                        dx = next_point[0] - current[0]
                        dy = next_point[1] - current[1]
                        path_distance = math.sqrt(dx**2 + dy**2)
                        
                        if path_distance > 0:
                            dx /= path_distance
                            dy /= path_distance
                            
                            # Predict position
                            predicted_x = self.target.x + dx * self.target.speed * game_speed * time_to_hit
                            predicted_y = self.target.y + dy * self.target.speed * game_speed * time_to_hit
                    
                    # Create projectile with predicted position
                    projectile = Projectile(self.x, self.y, self.target, self.damage, 
                                          self.projectile_speed, self.color)
                    projectile.target.x = predicted_x
                    projectile.target.y = predicted_y
                    self.projectiles.append(projectile)
                else:
                    # For other towers, aim directly at enemy
                    projectile = Projectile(self.x, self.y, self.target, self.damage, 
                                          self.projectile_speed, self.color)
                    self.projectiles.append(projectile)
    
    def upgrade(self):
        # Check if tower can be upgraded further
        if self.level >= self.max_level:
            return False  # Cannot upgrade
        
        upgrade_cost = int(TOWER_SETTINGS[self.type]["cost"] * 0.75)
        self.total_cost += upgrade_cost
        self.level += 1
        
        # Apply upgrade effectiveness based on difficulty
        damage_increase = self.settings["damage"] * 0.15 * self.upgrade_effectiveness
        range_increase = self.settings["range"] * 0.1 * self.upgrade_effectiveness
        fire_rate_increase = self.settings["fire_rate"] * 0.05 * self.upgrade_effectiveness
        accuracy_increase = 0.02 * self.upgrade_effectiveness
        
        self.damage += damage_increase
        self.range += range_increase
        self.fire_rate += fire_rate_increase
        self.accuracy = min(1.0, self.accuracy + accuracy_increase)
        return True  # Upgrade successful
        
    def draw(self, screen):
        # Only draw if image is available
        if self.use_image:
            # Draw tower image
            rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, rect)
            
            # Draw tower level indicator
            font = pygame.font.SysFont(None, 20)
            level_text = font.render(f"{self.level}/{self.max_level}", True, WHITE)
            screen.blit(level_text, (self.x - 10, self.y + 10))
            
            # Draw range indicator when selected
            if self.selected:
                pygame.draw.circle(screen, (100, 100, 255, 50), (self.x, self.y), self.range, 1)
                
                # Draw upgrade status
                if self.level < self.max_level:
                    upgrade_text = font.render(f"Upgrade: ${TOWER_SETTINGS[self.type]['cost'] // 2}", True, YELLOW)
                else:
                    upgrade_text = font.render("MAX LEVEL", True, RED)
                screen.blit(upgrade_text, (self.x - 40, self.y + 25))
        
        # Draw projectiles regardless of image availability
        for projectile in self.projectiles:
            projectile.draw(screen)
class Enemy:
    def __init__(self, path, enemy_type="goblin", difficulty=1):
        self.path = path
        self.path_index = 0
        self.x = path[0][0]
        self.y = path[0][1]
        self.type = enemy_type
        self.properties = ENEMY_TYPES[enemy_type]
        
        # Apply difficulty multipliers
        difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        health_multiplier = difficulty_settings["enemy_health_multiplier"]
        speed_multiplier = difficulty_settings["enemy_speed_multiplier"]
        reward_multiplier = difficulty_settings["enemy_reward_multiplier"]
        
        self.health = self.properties["health"] * health_multiplier
        self.max_health = self.health
        self.speed = self.properties["speed"] * speed_multiplier
        self.reward = self.properties["reward"] * reward_multiplier
        self.alive = True
        self.progress = 0  # Progress along current path segment
        self.spawn_delay = random.uniform(0, 1)
        
        # Load enemy image
        self.use_image = False
        try:
            self.image = pygame.image.load(f"assets/{enemy_type}.png").convert_alpha()
            # Scale image to appropriate size
            size = self.properties["size"] * 2
            self.image = pygame.transform.scale(self.image, (size, size))
            self.use_image = True
        except Exception:
            self.use_image = False
        
    def update(self, game_speed):
        if not self.alive or self.path_index >= len(self.path) - 1:
            return
            
        # Get current and next waypoints
        current = self.path[self.path_index]
        next_point = self.path[self.path_index + 1]
        
        # Calculate direction
        dx = next_point[0] - current[0]
        dy = next_point[1] - current[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Move enemy
        self.x += dx * self.speed * game_speed
        self.y += dy * self.speed * game_speed
        self.progress += self.speed * game_speed
        
        # Check if reached next waypoint
        if self.progress >= distance:
            self.path_index += 1
            self.progress = 0
            
            # Check if reached the end
            if self.path_index >= len(self.path) - 1:
                self.alive = False
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            if self.use_image:
                # Draw enemy image
                rect = self.image.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(self.image, rect)
            else:
                # Draw enemy as circle if image not available
                pygame.draw.circle(screen, self.properties["color"], 
                                 (int(self.x), int(self.y)), self.properties["size"])
            
            # Draw health bar
            bar_width = 30
            bar_height = 4
            health_percentage = self.health / self.max_health
            pygame.draw.rect(screen, RED, 
                           (self.x - bar_width//2, self.y - self.properties["size"] - 10, 
                            bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, 
                           (self.x - bar_width//2, self.y - self.properties["size"] - 10, 
                            int(bar_width * health_percentage), bar_height))
class PathGenerator:
    @staticmethod
    def generate_circular_path():
        # Create a circular path with smooth curves
        center_x = GAME_FIELD_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        radius = min(GAME_FIELD_WIDTH, SCREEN_HEIGHT) // 3
        
        # Number of points on the circle
        num_points = 20
        path = []
        
        # Generate points around the circle
        for i in range(num_points + 1):
            angle = (i / num_points) * math.pi * 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            path.append((x, y))
        
        # Adjust start and end points
        path[0] = (0, center_y)
        path[-1] = (GAME_FIELD_WIDTH, center_y)
        
        return path
    
    @staticmethod
    def generate_straight_path():
        # Create a straight path with some curves
        path = []
        
        # Start point
        path.append((0, SCREEN_HEIGHT // 2))
        
        # Add some curves
        path.append((GAME_FIELD_WIDTH // 4, SCREEN_HEIGHT // 2))
        path.append((GAME_FIELD_WIDTH // 3, SCREEN_HEIGHT // 3))
        path.append((GAME_FIELD_WIDTH // 2, SCREEN_HEIGHT // 3))
        path.append((2 * GAME_FIELD_WIDTH // 3, SCREEN_HEIGHT // 2))
        path.append((3 * GAME_FIELD_WIDTH // 4, SCREEN_HEIGHT // 2))
        
        # End point
        path.append((GAME_FIELD_WIDTH, SCREEN_HEIGHT // 2))
        
        return path
    
    @staticmethod
    def generate_zigzag_path():
        # Create a zigzag path
        path = []
        
        # Start point
        path.append((0, SCREEN_HEIGHT // 2))
        
        # Create zigzag pattern
        segments = 6
        for i in range(segments):
            x = (i + 1) * GAME_FIELD_WIDTH // segments
            if i % 2 == 0:
                y = SCREEN_HEIGHT // 3
            else:
                y = 2 * SCREEN_HEIGHT // 3
            path.append((x, y))
        
        # End point
        path.append((GAME_FIELD_WIDTH, SCREEN_HEIGHT // 2))
        
        return path
    
    @staticmethod
    def generate_spiral_path():
        # Create a spiral path
        center_x = GAME_FIELD_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        path = []
        
        # Start point
        path.append((0, center_y))
        
        # Create spiral
        num_turns = 2
        points_per_turn = 20
        max_radius = min(GAME_FIELD_WIDTH, SCREEN_HEIGHT) // 3
        
        for i in range(num_turns * points_per_turn + 1):
            angle = (i / points_per_turn) * math.pi * 2
            radius = (i / (num_turns * points_per_turn)) * max_radius
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            path.append((x, y))
        
        # End point
        path.append((GAME_FIELD_WIDTH, center_y))
        
        return path
    
    @staticmethod
    def generate_wave_path():
        # Create a wave path
        path = []
        
        # Start point
        path.append((0, SCREEN_HEIGHT // 2))
        
        # Create wave pattern
        segments = 8
        amplitude = SCREEN_HEIGHT // 4
        
        for i in range(1, segments):
            x = i * GAME_FIELD_WIDTH // segments
            y = SCREEN_HEIGHT // 2 + amplitude * math.sin(i * math.pi / 2)
            path.append((x, y))
        
        # End point
        path.append((GAME_FIELD_WIDTH, SCREEN_HEIGHT // 2))
        
        return path
    
    @staticmethod
    def generate_random_path():
        # Generate a random path with waypoints
        path = []
        
        # Start point
        start_y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
        path.append((0, start_y))
        
        # Generate random waypoints
        num_waypoints = random.randint(3, 7)
        for i in range(1, num_waypoints):
            x = i * GAME_FIELD_WIDTH // (num_waypoints + 1)
            y = random.randint(SCREEN_HEIGHT // 5, 4 * SCREEN_HEIGHT // 5)
            path.append((x, y))
        
        # End point
        end_y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
        path.append((GAME_FIELD_WIDTH, end_y))
        
        return path
    
    @staticmethod
    def generate_all_paths():
        # Generate 50 different path combinations
        paths = []
        
        # Add the original 3 paths
        paths.append(PathGenerator.generate_circular_path())
        paths.append(PathGenerator.generate_straight_path())
        paths.append(PathGenerator.generate_zigzag_path())
        
        # Add spiral and wave paths
        paths.append(PathGenerator.generate_spiral_path())
        paths.append(PathGenerator.generate_wave_path())
        
        # Generate 45 random paths
        for _ in range(45):
            paths.append(PathGenerator.generate_random_path())
        
        return paths
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Forest Protector")
        self.clock = pygame.time.Clock()
        self.running = True
        self.restart_available = False
        self.game_state = "playing"  # playing, paused, game_over, victory
        self.score = 0
        self.difficulty = 2  # Default to Normal difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[self.difficulty]
        self.money = self.difficulty_settings["starting_money"]
        self.lives = self.difficulty_settings["starting_lives"]
        self.wave = 0
        self.enemies = []
        self.towers = []
        self.selected_tower = None
        self.last_wave_time = time.time()
        self.game_start_time = time.time()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)
        self.min_difficulty = 1
        self.max_difficulty = 5
        
        # Generate all 50 paths
        self.all_paths = PathGenerator.generate_all_paths()
        self.current_path_index = 0
        self.path = self.all_paths[self.current_path_index]
        
        self.hover_grid = None
        self.selected_tower_type = TowerType.ARCHER
        
        # Path change and refund settings
        self.enable_refund = True  # Toggle for refund system
        self.refund_percentage = 0.75  # 75% refund when path changes
        self.auto_change_path = True  # Automatically change path after each wave
        
        # Create assets directory if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
        
        # Enemy scaling settings
        self.base_enemies = 5  # Starting number of enemies
        self.enemy_increment = 2  # Additional enemies per wave
        self.max_enemies_per_wave = 25  # Maximum enemies in a wave
        
        # Game speed control
        self.game_speed = 1.0
        self.speed_increment = 0.1
        self.min_speed = 0.1
        self.max_speed = 2.0
        try:
            self.grass_texture = pygame.image.load("assets/grass.png").convert_alpha()
            # Scale grass texture to cover the game field
            self.grass_texture = pygame.transform.scale(self.grass_texture, (GAME_FIELD_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading grass texture: {e}")
            self.grass_texture = None

        try:
            self.road_texture = pygame.image.load("assets/road.png").convert_alpha()
            # Scale road texture to match path width
            self.road_texture = pygame.transform.scale(self.road_texture, (PATH_WIDTH, PATH_WIDTH))
        except Exception as e:
            print(f"Error loading road texture: {e}")
            self.road_texture = None

        # Create UI buttons
        self.create_ui_buttons()
        
    def create_ui_buttons(self):
        # Speed control buttons
        self.speed_up_button = Button(
            GAME_FIELD_WIDTH + 150, 200, 40, 40, "▲", GRAY, WHITE
        )
        self.speed_down_button = Button(
            GAME_FIELD_WIDTH + 150, 250, 40, 40, "▼", GRAY, WHITE
        )
        # Difficulty control buttons - positioned properly
        self.difficulty_up_button = Button(
            GAME_FIELD_WIDTH + 150, 320, 40, 40, "+", GRAY, WHITE
        )
        self.difficulty_down_button = Button(
            GAME_FIELD_WIDTH + 200, 320, 40, 40, "-", GRAY, WHITE
        )
        
        # Tower selection buttons
        self.tower_buttons = []
        button_y = 380  # Moved down to avoid overlap
        for i, (tower_type, settings) in enumerate(TOWER_SETTINGS.items()):
            button = Button(
                GAME_FIELD_WIDTH + 20, button_y + i * 80, 260, 70, 
                tower_type.name.capitalize(), settings["color"], WHITE
            )
            self.tower_buttons.append((button, tower_type))
        
        # Path change button
        self.path_button = Button(
            GAME_FIELD_WIDTH + 20, 650, 260, 50, 
            "Change Path", BLUE, WHITE
        )
        
        # Pause button
        self.pause_button = Button(
            GAME_FIELD_WIDTH + 20, 720, 260, 50, 
            "Pause (P)", YELLOW, BLACK
        )
        
    # Add this method to the Game class
    def restart_game(self):
        self.__init__()  # Reset all game attributes
        self.restart_available = True
    def get_enemies_in_wave(self, wave):
        """Calculate number of enemies for the given wave"""
        enemies = self.base_enemies + (wave - 1) * self.enemy_increment
        return min(enemies, self.max_enemies_per_wave)
    
    def get_enemy_type_for_wave(self, wave, enemy_index, total_enemies):
        """Determine enemy type based on wave and position in wave"""
        if wave < 3:
            # Early waves: only goblins
            return "goblin"
        elif wave < 6:
            # Mid waves: mix of goblins and orcs
            return "orc" if enemy_index % 2 == 0 else "goblin"
        else:
            # Late waves: mix of all enemies with increasing troll percentage
            troll_percentage = min(0.6, 0.2 + (wave - 5) * 0.1)  # 20% at wave 6, up to 60% at wave 10
            orc_percentage = 0.3
            
            # Calculate thresholds
            troll_threshold = int(total_enemies * troll_percentage)
            orc_threshold = troll_threshold + int(total_enemies * orc_percentage)
            
            if enemy_index < troll_threshold:
                return "troll"
            elif enemy_index < orc_threshold:
                return "orc"
            else:
                return "goblin"
    
    def change_difficulty(self, delta):
        new_difficulty = max(self.min_difficulty, min(self.max_difficulty, self.difficulty + delta))
        if new_difficulty != self.difficulty:
            self.difficulty = new_difficulty
            self.difficulty_settings = DIFFICULTY_SETTINGS[self.difficulty]
            
            # Update all towers' difficulty value
            for tower in self.towers:
                tower.difficulty = self.difficulty
                tower.upgrade_effectiveness = self.difficulty_settings["tower_upgrade_effectiveness"]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Add restart functionality
                elif event.key == pygame.K_SPACE and (self.game_state == "game_over" or self.game_state == "victory"):
                    self.restart_game()
                    return  # Skip other event processing when restarting
                elif event.key == pygame.K_1:
                    self.selected_tower_type = TowerType.ARCHER
                elif event.key == pygame.K_2:
                    self.selected_tower_type = TowerType.CANNON
                elif event.key == pygame.K_3:
                    self.selected_tower_type = TowerType.MAGIC
                elif event.key == pygame.K_p:  # Pause game
                    if self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                elif event.key == pygame.K_c:  # Change path manually
                    self.change_path()
                elif event.key == pygame.K_UP:  # Increase game speed
                    self.change_game_speed(self.speed_increment)
                elif event.key == pygame.K_DOWN:  # Decrease game speed
                    self.change_game_speed(-self.speed_increment)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.change_difficulty(1)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    self.change_difficulty(-1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Check if clicking in game field area
                    if mouse_x < GAME_FIELD_WIDTH:
                        # Check if clicking on a tower to upgrade
                        for tower in self.towers:
                            if math.sqrt((tower.x - mouse_x)**2 + (tower.y - mouse_y)**2) < 20:
                                if self.money >= TOWER_SETTINGS[tower.type]["cost"] // 2:
                                    self.money -= TOWER_SETTINGS[tower.type]["cost"] // 2
                                    tower.upgrade()
                                return
                        
                        # Place new tower
                        grid_x = mouse_x // GRID_SIZE
                        grid_y = mouse_y // GRID_SIZE
                        
                        # Check if position is valid (not on path)
                        valid_position = True
                        for i in range(len(self.path) - 1):
                            x1, y1 = self.path[i]
                            x2, y2 = self.path[i + 1]
                            
                            # Check if grid cell is near the path
                            cell_x = grid_x * GRID_SIZE + GRID_SIZE // 2
                            cell_y = grid_y * GRID_SIZE + GRID_SIZE // 2
                            
                            # Simple distance check to path segment
                            dist_to_segment = self.point_to_line_distance(
                                (cell_x, cell_y), (x1, y1), (x2, y2)
                            )
                            
                            if dist_to_segment < PATH_WIDTH / 2 + GRID_SIZE:
                                valid_position = False
                                break
                            
                        tower_cost = TOWER_SETTINGS[self.selected_tower_type]["cost"]
                        if valid_position and self.money >= tower_cost:
                            self.money -= tower_cost
                            tower_x = grid_x * GRID_SIZE + GRID_SIZE // 2
                            tower_y = grid_y * GRID_SIZE + GRID_SIZE // 2
                            self.towers.append(Tower(tower_x, tower_y, self.selected_tower_type, self.difficulty))
            
            # Handle button events
            if self.speed_up_button.handle_event(event):
                self.change_game_speed(self.speed_increment)
            if self.speed_down_button.handle_event(event):
                self.change_game_speed(-self.speed_increment)
            if self.path_button.handle_event(event):
                self.change_path()
            if self.pause_button.handle_event(event):
                if self.game_state == "playing":
                    self.game_state = "paused"
                elif self.game_state == "paused":
                    self.game_state = "playing"
            if self.difficulty_up_button.handle_event(event):
                self.change_difficulty(1)
            if self.difficulty_down_button.handle_event(event):
                self.change_difficulty(-1)
            # Handle tower selection buttons
            for button, tower_type in self.tower_buttons:
                if button.handle_event(event):
                    self.selected_tower_type = tower_type
    
    def change_game_speed(self, delta):
        self.game_speed = max(self.min_speed, min(self.max_speed, self.game_speed + delta))
    
    def point_to_line_distance(self, point, line_start, line_end):
        # Calculate distance from point to line segment
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Calculate line length squared
        line_length_sq = (x2 - x1)**2 + (y2 - y1)**2
        
        if line_length_sq == 0:
            return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)
        
        # Calculate projection of point onto line
        t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq))
        
        # Calculate closest point on line segment
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)
        
        # Return distance to closest point
        return math.sqrt((x0 - closest_x)**2 + (y0 - closest_y)**2)
    
    def change_path(self):
        # Move to the next path in the list (cycle through all 50)
        self.current_path_index = (self.current_path_index + 1) % len(self.all_paths)
        new_path = self.all_paths[self.current_path_index]
        
        # Refund all towers if enabled
        if self.enable_refund:
            total_refund = 0
            for tower in self.towers:
                refund_amount = int(tower.total_cost * self.refund_percentage)
                total_refund += refund_amount
            
            self.money += total_refund
            self.towers.clear()  # Remove all towers
        
        # Update the path
        self.path = new_path
        
        # Update enemy paths
        for enemy in self.enemies:
            enemy.path = new_path
    
    def update(self):
        if self.game_state != "playing":
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.game_start_time
        
        # Check if time is up
        if elapsed_time >= GAME_TIME_LIMIT:
            self.game_state = "game_over"
            return
        
        # Spawn waves
        if current_time - self.last_wave_time > WAVE_DELAY / self.game_speed and len(self.enemies) == 0:
            self.wave += 1
            self.last_wave_time = current_time
            
            # Change path automatically after each wave if enabled
            if self.auto_change_path and self.wave > 1:
                self.change_path()
            
            # Calculate number of enemies for this wave
            num_enemies = self.get_enemies_in_wave(self.wave)
            
            # Spawn enemies for this wave
            for i in range(num_enemies):
                # Determine enemy type based on wave and position
                enemy_type = self.get_enemy_type_for_wave(self.wave, i, num_enemies)
                
                enemy = Enemy(self.path, enemy_type, self.difficulty)
                self.enemies.append(enemy)
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy.spawn_delay > 0:
                enemy.spawn_delay -= 1/FPS * self.game_speed
                continue
                
            enemy.update(self.game_speed)
            
            if not enemy.alive:
                if enemy.path_index >= len(self.path) - 1:
                    # Enemy reached the end
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = "game_over"
                else:
                    # Enemy was killed
                    self.score += enemy.reward
                    self.money += enemy.reward // 2
                
                self.enemies.remove(enemy)
        
        # Update towers
        for tower in self.towers:
            tower.update(self.enemies, current_time, self.game_speed)
        
        # Check victory condition
        if self.wave >= 10 and len(self.enemies) == 0:
            self.game_state = "victory"
            self.score += WAVE_BONUS
        
        # Update hover position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x < GAME_FIELD_WIDTH:  # Only in game field area
            grid_x = mouse_x // GRID_SIZE
            grid_y = mouse_y // GRID_SIZE
            
            # Check if hover position is valid
            valid_hover = True
            for i in range(len(self.path) - 1):
                x1, y1 = self.path[i]
                x2, y2 = self.path[i + 1]
                
                cell_x = grid_x * GRID_SIZE + GRID_SIZE // 2
                cell_y = grid_y * GRID_SIZE + GRID_SIZE // 2
                
                dist_to_segment = self.point_to_line_distance(
                    (cell_x, cell_y), (x1, y1), (x2, y2)
                )
                
                if dist_to_segment < PATH_WIDTH / 2 + GRID_SIZE:
                    valid_hover = False
                    break
            
            tower_cost = TOWER_SETTINGS[self.selected_tower_type]["cost"]
            if valid_hover and self.money >= tower_cost:
                self.hover_grid = (grid_x, grid_y)
            else:
                self.hover_grid = None
        else:
            self.hover_grid = None
    
    def draw(self):
        # Draw background
        self.screen.fill(GREEN)
        
        # Draw game field area
        # game_field_rect = pygame.Rect(0, 0, GAME_FIELD_WIDTH, SCREEN_HEIGHT)
        # pygame.draw.rect(self.screen, GREEN, game_field_rect)
        
        # Draw grass texture
        # Draw grass texture tiled across screen
        if self.grass_texture:
            w, h = self.grass_texture.get_size()
            for x in range(0, GAME_FIELD_WIDTH, w):
                for y in range(0, SCREEN_HEIGHT, h):
                    self.screen.blit(self.grass_texture, (x, y))

        # Fallback to original road drawing
        for i in range(len(self.path) - 1):
            start = self.path[i]
            end = self.path[i + 1]
        
            # Draw path border (slightly wider than the road itself)
            pygame.draw.line(self.screen, DARK_BROWN, start, end, PATH_WIDTH + 4)
            # Draw main path
            pygame.draw.line(self.screen, BROWN, start, end, PATH_WIDTH)
        
            # Border around waypoints
            # pygame.draw.circle(self.screen, DARK_BROWN, (int(start[0]), int(start[1])), PATH_WIDTH // 2 + 2)
            # Main waypoint
            pygame.draw.circle(self.screen, BROWN, (int(start[0]), int(start[1])), PATH_WIDTH // 2)
        
        # Draw end point with border
        end_point = self.path[-1]
        # pygame.draw.circle(self.screen, DARK_BROWN, (int(end_point[0]), int(end_point[1])), PATH_WIDTH // 2 + 2)
        pygame.draw.circle(self.screen, BROWN, (int(end_point[0]), int(end_point[1])), PATH_WIDTH // 2)

        
        # Draw hover effect
        if self.hover_grid:
            grid_x, grid_y = self.hover_grid
            center_x = grid_x * GRID_SIZE + GRID_SIZE // 2
            center_y = grid_y * GRID_SIZE + GRID_SIZE // 2
            pygame.draw.circle(self.screen, PURPLE, (center_x, center_y), GRID_SIZE // 2, 2)
            
            # Draw tower preview
            tower_color = TOWER_SETTINGS[self.selected_tower_type]["color"]
            pygame.draw.circle(self.screen, tower_color, (center_x, center_y), 15, 2)
        
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw pause overlay if game is paused
        if self.game_state == "paused":
            self.draw_pause_overlay()
        
        # Draw game over or victory screen
        if self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "victory":
            self.draw_victory()
        
        pygame.display.flip()
    def draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.title_font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        # Draw instructions
        inst_text = self.font.render("Press P to resume", True, WHITE)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(inst_text, inst_rect)
    
    def draw_ui(self):
        # Draw top bar over game field only
        top_bar_rect = pygame.Rect(0, 0, GAME_FIELD_WIDTH, 80)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), top_bar_rect)
        pygame.draw.rect(self.screen, GOLD, top_bar_rect, 3)
        
        # Draw game title
        title_text = self.title_font.render("Forest Protector", True, GOLD)
        self.screen.blit(title_text, (GAME_FIELD_WIDTH // 2 - title_text.get_width() // 2, 5))
        
        # Draw stats background
        stats_rect = pygame.Rect(10, 45, GAME_FIELD_WIDTH - 20, 30)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), stats_rect)
        pygame.draw.rect(self.screen, GOLD, stats_rect, 2)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 50))
        
        # Draw money with coin icon
        pygame.draw.circle(self.screen, GOLD, (220, 60), 10)
        money_text = self.font.render(f"${self.money}", True, YELLOW)
        self.screen.blit(money_text, (235, 50))
        
        # Draw lives with heart icon
        pygame.draw.circle(self.screen, RED, (370, 60), 8)
        pygame.draw.polygon(self.screen, RED, [(370, 60), (365, 55), (365, 65)])
        pygame.draw.polygon(self.screen, RED, [(370, 60), (375, 55), (375, 65)])
        lives_text = self.font.render(f"Lives: {self.lives}", True, RED)
        self.screen.blit(lives_text, (385, 50))
        
        # Draw wave
        wave_text = self.font.render(f"Wave: {self.wave}/10", True, WHITE)
        self.screen.blit(wave_text, (500, 50))
        
        # Draw timer
        elapsed_time = time.time() - self.game_start_time
        remaining_time = max(0, GAME_TIME_LIMIT - elapsed_time)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        timer_color = RED if remaining_time < 60 else WHITE
        timer_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, timer_color)
        self.screen.blit(timer_text, (650, 50))
        
        # Draw current path indicator
        path_text = self.font.render(f"Path: {self.current_path_index + 1}/50", True, WHITE)
        self.screen.blit(path_text, (800, 50))
        
        # Draw next wave enemy count
        if self.game_state == "playing" and len(self.enemies) == 0:
            next_wave_enemies = self.get_enemies_in_wave(self.wave + 1) if self.wave < 10 else 0
            next_wave_text = self.font.render(f"Next: {next_wave_enemies} enemies", True, YELLOW)
            self.screen.blit(next_wave_text, (1000, 50))
        
        # Draw side panel
        panel_rect = pygame.Rect(GAME_FIELD_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 30), panel_rect)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)
        
        # Draw panel title
        panel_title = self.title_font.render("Controls", True, GOLD)
        self.screen.blit(panel_title, (GAME_FIELD_WIDTH + PANEL_WIDTH // 2 - panel_title.get_width() // 2, 20))
        
        # Draw speed control
        speed_text = self.font.render(f"Game Speed: {self.game_speed:.1f}x", True, WHITE)
        speed_x = GAME_FIELD_WIDTH + 20
        speed_y = 150
        self.screen.blit(speed_text, (speed_x, speed_y))
        
        # Draw speed buttons
        btn_y = speed_y + 30
        self.speed_up_button.rect.topleft = (speed_x, btn_y)
        self.speed_down_button.rect.topleft = (speed_x + 50, btn_y)
        # Draw speed up button with up arrow
        self.speed_up_button.draw(self.screen)
        pygame.draw.polygon(self.screen, WHITE, [
            (self.speed_up_button.rect.centerx, self.speed_up_button.rect.top + 5),
            (self.speed_up_button.rect.left + 5, self.speed_up_button.rect.bottom - 5),
            (self.speed_up_button.rect.right - 5, self.speed_up_button.rect.bottom - 5)
        ])
        self.speed_down_button.draw(self.screen)
        pygame.draw.polygon(self.screen, WHITE, [
            (self.speed_down_button.rect.centerx, self.speed_down_button.rect.bottom - 5),
            (self.speed_down_button.rect.left + 5, self.speed_down_button.rect.top + 5),
            (self.speed_down_button.rect.right - 5, self.speed_down_button.rect.top + 5)
        ])
        # Draw difficulty controls - Improved display with color and icon
        diff_name = self.difficulty_settings["name"]
        # Choose color based on difficulty
        if self.difficulty == 1:
            diff_color = GREEN
        elif self.difficulty == 2:
            diff_color = (100, 200, 100)
        elif self.difficulty == 3:
            diff_color = YELLOW
        elif self.difficulty == 4:
            diff_color = (255, 140, 0)
        else:
            diff_color = RED

        diff_text = self.font.render(f"Difficulty: {diff_name}", True, diff_color)
        diff_x = GAME_FIELD_WIDTH + 20
        diff_y = 250
        self.screen.blit(diff_text, (diff_x, diff_y))
        
        # Draw difficulty level indicator
        diff_level_text = self.small_font.render(f"({self.difficulty}/5)", True, WHITE)
        self.screen.blit(diff_level_text, (diff_x + diff_text.get_width() + 10, diff_y + 5))

        # Buttons in next line
        btn_y = diff_y + 30
        self.difficulty_up_button.rect.topleft = (diff_x, btn_y)
        self.difficulty_down_button.rect.topleft = (diff_x + 50, btn_y)
        
        # Draw difficulty buttons

        self.difficulty_up_button.draw(self.screen)
        self.difficulty_down_button.draw(self.screen)
        
        # Draw tower selection section
        tower_title = self.font.render("Select Tower:", True, WHITE)
        self.screen.blit(tower_title, (GAME_FIELD_WIDTH + 20, 350))
        
        # Draw tower buttons
        for button, tower_type in self.tower_buttons:
            button.draw(self.screen)
            # Draw tower info
            settings = TOWER_SETTINGS[tower_type]
            info_y = button.rect.y + 30
            cost_text = self.small_font.render(f"Cost: ${settings['cost']}", True, YELLOW)
            self.screen.blit(cost_text, (button.rect.x + 10, info_y))
            stats_text = self.small_font.render(f"DMG: {settings['damage']} RNG: {settings['range']}", True, WHITE)
            self.screen.blit(stats_text, (button.rect.x + 10, info_y + 20))
        
        # Highlight selected tower
        for button, tower_type in self.tower_buttons:
            if tower_type == self.selected_tower_type:
                pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
        
        # Draw action buttons
        self.pause_button.draw(self.screen)
        
        # Draw instructions
        instructions = [
            "1/2/3: Select Tower",
            "Click: Place/Upgrade",
            "C: Change Path",
            "P: Pause",
            "↑/↓: Change Speed",
            "+/-: Change Difficulty",
            "ESC: Exit"
        ]
        
        inst_y = 800
        for inst in instructions:
            inst_text = self.small_font.render(inst, True, WHITE)
            self.screen.blit(inst_text, (GAME_FIELD_WIDTH + 20, inst_y))
            inst_y += 25
        
        # Draw wave info panel
        if self.game_state == "playing":
            wave_info_rect = pygame.Rect(GAME_FIELD_WIDTH - 250, 100, 230, 120)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), wave_info_rect)
            pygame.draw.rect(self.screen, GOLD, wave_info_rect, 2)
            
            # Title
            info_title = self.small_font.render("Wave Information", True, GOLD)
            self.screen.blit(info_title, (GAME_FIELD_WIDTH - 240, 110))
            
            # Current wave enemies
            current_enemies = self.get_enemies_in_wave(self.wave)
            current_text = self.small_font.render(f"Current: {current_enemies} enemies", True, WHITE)
            self.screen.blit(current_text, (GAME_FIELD_WIDTH - 240, 135))
            
            # Enemy composition
            if self.wave < 3:
                comp_text = self.small_font.render("Composition: All Goblins", True, WHITE)
            elif self.wave < 6:
                comp_text = self.small_font.render("Composition: Goblins & Orcs", True, WHITE)
            else:
                troll_pct = min(60, 20 + (self.wave - 5) * 10)
                comp_text = self.small_font.render(f"Composition: {troll_pct}% Trolls", True, WHITE)
            self.screen.blit(comp_text, (GAME_FIELD_WIDTH - 240, 160))
            
            # Next wave preview
            if self.wave < 10:
                next_enemies = self.get_enemies_in_wave(self.wave + 1)
                next_text = self.small_font.render(f"Next wave: {next_enemies} enemies", True, YELLOW)
                self.screen.blit(next_text, (GAME_FIELD_WIDTH - 240, 185))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        # Draw game over panel
        panel_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, DARK_GREEN, panel_rect)
        pygame.draw.rect(self.screen, RED, panel_rect, 5)
        game_over_text = self.title_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        waves_completed_text = self.font.render(f"Waves Completed: {self.wave}/10", True, WHITE)
        waves_rect = waves_completed_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(waves_completed_text, waves_rect)
        # Changed this line to show restart option
        restart_text = self.small_font.render("Press SPACE to restart or ESC to exit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
    # Modify the draw_victory method
    def draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        # Draw victory panel
        panel_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, DARK_GREEN, panel_rect)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 5)
        victory_text = self.title_font.render("VICTORY!", True, GOLD)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70))
        self.screen.blit(victory_text, text_rect)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(score_text, score_rect)
        bonus_text = self.small_font.render(f"Wave Bonus: +{WAVE_BONUS}", True, YELLOW)
        bonus_rect = bonus_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(bonus_text, bonus_rect)
        max_enemies_text = self.font.render(f"Max Enemies in Wave: {self.get_enemies_in_wave(10)}", True, WHITE)
        max_rect = max_enemies_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(max_enemies_text, max_rect)
        # Changed this line to show restart option
        restart_text = self.small_font.render("Press SPACE to restart or ESC to exit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
    async def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            await asyncio.sleep(0) 
        
        pygame.quit()
if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())