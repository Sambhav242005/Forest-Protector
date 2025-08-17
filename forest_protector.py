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
GRID_COLS = SCREEN_WIDTH // GRID_SIZE
GRID_ROWS = SCREEN_HEIGHT // GRID_SIZE
PATH_WIDTH = 60
# Tower types
class TowerType(Enum):
    ARCHER = 1
    CANNON = 2
    MAGIC = 3
# Tower settings
# Tower settings
TOWER_SETTINGS = {
    TowerType.ARCHER: {
        "cost": 50,
        "damage": 20,
        "range": 150,
        "fire_rate": 2.5,  # Shots per second
        "accuracy": 0.8,
        "color": ARCHER_GREEN,
        "projectile_speed": 8,
        "max_level": 5  # Maximum upgrade level
    },
    TowerType.CANNON: {
        "cost": 75,
        "damage": 40,
        "range": 100,
        "fire_rate": 1,  # Shots per second
        "accuracy": 0.65,
        "color": CANNON_GRAY,
        "projectile_speed": 5,
        "max_level": 3  # Maximum upgrade level
    },
    TowerType.MAGIC: {
        "cost": 100,
        "damage": 30,
        "range": 120,
        "fire_rate": 2.0,  # Shots per second
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
class Projectile:
    def __init__(self, x, y, target, damage, projectile_speed, color):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = projectile_speed
        self.color = color
        self.active = True
        
    def update(self):
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
            self.x += dx * self.speed
            self.y += dy * self.speed
    
    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 4)
class Tower:
    def __init__(self, x, y, tower_type):
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
        
        # Load tower image
        self.use_image = False
        try:
            # Construct image path based on tower type
            image_path = f"assets/{tower_type.name.lower()}.png"
            self.image = pygame.image.load(image_path).convert_alpha()
            # Scale image to appropriate size (40x40 pixels)
            self.image = pygame.transform.scale(self.image, (32, 48))
            self.use_image = True
            print(f"Loaded tower image: {image_path}")
        except pygame.error as e:
            print(f"Could not load tower image {image_path}: {e}")
            self.use_image = False
        except Exception as e:
            print(f"Error loading tower image: {e}")
            self.use_image = False
        
    def update(self, enemies, current_time):
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
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
        if self.target and current_time - self.last_shot > 1 / self.fire_rate:
            self.last_shot = current_time
            
            # Check if shot hits based on accuracy
            if random.random() < self.accuracy:
                # For magic tower, predict enemy position
                if self.type == TowerType.MAGIC:
                    # Calculate time to reach enemy
                    distance = math.sqrt((self.target.x - self.x)**2 + (self.target.y - self.y)**2)
                    time_to_hit = distance / self.projectile_speed
                    
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
                            predicted_x = self.target.x + dx * self.target.speed * time_to_hit
                            predicted_y = self.target.y + dy * self.target.speed * time_to_hit
                    
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
        
        upgrade_cost = TOWER_SETTINGS[self.type]["cost"] // 2
        self.total_cost += upgrade_cost
        self.level += 1
        self.damage += self.settings["damage"] * 0.2
        self.range += self.settings["range"] * 0.1
        self.fire_rate += self.settings["fire_rate"] * 0.1
        self.accuracy = min(1.0, self.accuracy + 0.05)
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
    def __init__(self, path, enemy_type="goblin"):
        self.path = path
        self.path_index = 0
        self.x = path[0][0]
        self.y = path[0][1]
        self.type = enemy_type
        self.properties = ENEMY_TYPES[enemy_type]
        self.health = self.properties["health"]
        self.max_health = self.properties["health"]
        self.speed = self.properties["speed"]
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
        
    def update(self):
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
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.progress += self.speed
        
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
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 3
        
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
        path[-1] = (SCREEN_WIDTH, center_y)
        
        return path
    
    @staticmethod
    def generate_straight_path():
        # Create a straight path with some curves
        path = []
        
        # Start point
        path.append((0, SCREEN_HEIGHT // 2))
        
        # Add some curves
        path.append((SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        path.append((SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3))
        path.append((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        path.append((2 * SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
        path.append((3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        
        # End point
        path.append((SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
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
            x = (i + 1) * SCREEN_WIDTH // segments
            if i % 2 == 0:
                y = SCREEN_HEIGHT // 3
            else:
                y = 2 * SCREEN_HEIGHT // 3
            path.append((x, y))
        
        # End point
        path.append((SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        return path
    
    @staticmethod
    def generate_spiral_path():
        # Create a spiral path
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        path = []
        
        # Start point
        path.append((0, center_y))
        
        # Create spiral
        num_turns = 2
        points_per_turn = 20
        max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 3
        
        for i in range(num_turns * points_per_turn + 1):
            angle = (i / points_per_turn) * math.pi * 2
            radius = (i / (num_turns * points_per_turn)) * max_radius
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            path.append((x, y))
        
        # End point
        path.append((SCREEN_WIDTH, center_y))
        
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
            x = i * SCREEN_WIDTH // segments
            y = SCREEN_HEIGHT // 2 + amplitude * math.sin(i * math.pi / 2)
            path.append((x, y))
        
        # End point
        path.append((SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
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
            x = i * SCREEN_WIDTH // (num_waypoints + 1)
            y = random.randint(SCREEN_HEIGHT // 5, 4 * SCREEN_HEIGHT // 5)
            path.append((x, y))
        
        # End point
        end_y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
        path.append((SCREEN_WIDTH, end_y))
        
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
        self.game_state = "playing"  # playing, game_over, victory
        self.score = 0
        self.money = 150
        self.lives = 3
        self.wave = 0
        self.enemies = []
        self.towers = []
        self.selected_tower = None
        self.last_wave_time = time.time()
        self.game_start_time = time.time()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)
        
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
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_1:
                    self.selected_tower_type = TowerType.ARCHER
                elif event.key == pygame.K_2:
                    self.selected_tower_type = TowerType.CANNON
                elif event.key == pygame.K_3:
                    self.selected_tower_type = TowerType.MAGIC
                elif event.key == pygame.K_p:  # Change path manually
                    self.change_path()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
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
                        self.towers.append(Tower(tower_x, tower_y, self.selected_tower_type))
    
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
        if current_time - self.last_wave_time > WAVE_DELAY and len(self.enemies) == 0:
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
                
                enemy = Enemy(self.path, enemy_type)
                self.enemies.append(enemy)
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy.spawn_delay > 0:
                enemy.spawn_delay -= 1/FPS
                continue
                
            enemy.update()
            
            if not enemy.alive:
                if enemy.path_index >= len(self.path) - 1:
                    # Enemy reached the end
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = "game_over"
                else:
                    # Enemy was killed
                    self.score += enemy.properties["reward"]
                    self.money += enemy.properties["reward"] // 2
                
                self.enemies.remove(enemy)
        
        # Update towers
        for tower in self.towers:
            tower.update(self.enemies, current_time)
        
        # Check victory condition
        if self.wave >= 10 and len(self.enemies) == 0:
            self.game_state = "victory"
            self.score += WAVE_BONUS
        
        # Update hover position
        mouse_x, mouse_y = pygame.mouse.get_pos()
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
    
    def draw(self):
        # Draw background
        self.screen.fill(GREEN)
        
        # Draw grass texture
        for x in range(0, SCREEN_WIDTH, 20):
            for y in range(0, SCREEN_HEIGHT, 20):
                if (x // 20 + y // 20) % 2 == 0:
                    pygame.draw.rect(self.screen, DARK_GREEN, (x, y, 20, 20))
        
        # Draw path with proper connections
        for i in range(len(self.path) - 1):
            start = self.path[i]
            end = self.path[i + 1]
            
            # Draw path border
            pygame.draw.line(self.screen, DARK_BROWN, start, end, PATH_WIDTH + 4)
            # Draw path
            pygame.draw.line(self.screen, BROWN, start, end, PATH_WIDTH)
            
            # Draw path connections (circles at waypoints)
            # pygame.draw.circle(self.screen, DARK_BROWN, (int(start[0]), int(start[1])), PATH_WIDTH // 2 + 2)
            pygame.draw.circle(self.screen, BROWN, (int(start[0]), int(start[1])), PATH_WIDTH // 2)
        
        # Draw end point
        end_point = self.path[-1]
        pygame.draw.circle(self.screen, DARK_BROWN, (int(end_point[0]), int(end_point[1])), PATH_WIDTH // 2 + 2)
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
        
        # Draw game over or victory screen
        if self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "victory":
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Draw UI background with gradient
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), ui_rect)
        
        # Draw decorative border
        pygame.draw.rect(self.screen, GOLD, ui_rect, 3)
        
        # Draw game title
        title_text = self.title_font.render("Forest Protector", True, GOLD)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 5))
        
        # Draw stats background
        stats_rect = pygame.Rect(10, 45, SCREEN_WIDTH - 20, 30)
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
        
        # Draw tower selection panel
        panel_rect = pygame.Rect(10, SCREEN_HEIGHT - 120, SCREEN_WIDTH - 20, 110)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 2)
        
        # Draw tower options
        tower_y = SCREEN_HEIGHT - 100
        for i, (tower_type, settings) in enumerate(TOWER_SETTINGS.items()):
            x_pos = 30 + i * 250
            
            # Highlight selected tower
            if tower_type == self.selected_tower_type:
                highlight_rect = pygame.Rect(x_pos - 10, tower_y - 10, 220, 80)
                pygame.draw.rect(self.screen, (100, 100, 100, 100), highlight_rect, 0, 5)
                pygame.draw.rect(self.screen, GOLD, highlight_rect, 2, 5)
            
            # Draw tower icon
            pygame.draw.circle(self.screen, settings["color"], (x_pos + 20, tower_y + 30), 15)
            
            # Draw tower type indicator
            if tower_type == TowerType.ARCHER:
                pygame.draw.arc(self.screen, WHITE, (x_pos + 10, tower_y + 20, 20, 20), 0, math.pi, 3)
                pygame.draw.line(self.screen, WHITE, (x_pos + 13, tower_y + 30), (x_pos + 27, tower_y + 23), 2)
            elif tower_type == TowerType.CANNON:
                pygame.draw.rect(self.screen, BLACK, (x_pos + 15, tower_y + 15, 10, 20))
                pygame.draw.circle(self.screen, BLACK, (x_pos + 20, tower_y + 15), 8)
            elif tower_type == TowerType.MAGIC:
                pygame.draw.circle(self.screen, WHITE, (x_pos + 20, tower_y + 30), 10, 2)
                pygame.draw.line(self.screen, WHITE, (x_pos + 20, tower_y + 20), (x_pos + 20, tower_y + 40), 2)
                pygame.draw.line(self.screen, WHITE, (x_pos + 10, tower_y + 30), (x_pos + 30, tower_y + 30), 2)
            
            # Draw tower info
            tower_name = tower_type.name.capitalize()
            name_text = self.small_font.render(tower_name, True, WHITE)
            self.screen.blit(name_text, (x_pos + 45, tower_y))
            
            cost_text = self.small_font.render(f"Cost: ${settings['cost']}", True, YELLOW)
            self.screen.blit(cost_text, (x_pos + 45, tower_y + 25))
            
            # Draw tower stats
            stats_text = self.small_font.render(f"DMG: {settings['damage']} RNG: {settings['range']}", True, WHITE)
            self.screen.blit(stats_text, (x_pos + 45, tower_y + 50))
        
        # Draw instructions
        instructions = [
            "1/2/3: Select Tower | Click: Place/Upgrade | P: Change Path | ESC: Exit"
        ]
        inst_text = self.small_font.render(instructions[0], True, WHITE)
        self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, SCREEN_HEIGHT - 20))
        
        # Draw path change notification
        if self.auto_change_path:
            path_text = self.small_font.render("Path changes automatically after each wave", True, YELLOW)
            self.screen.blit(path_text, (SCREEN_WIDTH // 2 - path_text.get_width() // 2, SCREEN_HEIGHT - 45))
        
        # Draw wave info panel
        if self.game_state == "playing":
            wave_info_rect = pygame.Rect(SCREEN_WIDTH - 250, 100, 230, 120)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), wave_info_rect)
            pygame.draw.rect(self.screen, GOLD, wave_info_rect, 2)
            
            # Title
            info_title = self.small_font.render("Wave Information", True, GOLD)
            self.screen.blit(info_title, (SCREEN_WIDTH - 240, 110))
            
            # Current wave enemies
            current_enemies = self.get_enemies_in_wave(self.wave)
            current_text = self.small_font.render(f"Current: {current_enemies} enemies", True, WHITE)
            self.screen.blit(current_text, (SCREEN_WIDTH - 240, 135))
            
            # Enemy composition
            if self.wave < 3:
                comp_text = self.small_font.render("Composition: All Goblins", True, WHITE)
            elif self.wave < 6:
                comp_text = self.small_font.render("Composition: Goblins & Orcs", True, WHITE)
            else:
                troll_pct = min(60, 20 + (self.wave - 5) * 10)
                comp_text = self.small_font.render(f"Composition: {troll_pct}% Trolls", True, WHITE)
            self.screen.blit(comp_text, (SCREEN_WIDTH - 240, 160))
            
            # Next wave preview
            if self.wave < 10:
                next_enemies = self.get_enemies_in_wave(self.wave + 1)
                next_text = self.small_font.render(f"Next wave: {next_enemies} enemies", True, YELLOW)
                self.screen.blit(next_text, (SCREEN_WIDTH - 240, 185))
    
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
        
        restart_text = self.small_font.render("Press ESC to exit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
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
        
        restart_text = self.small_font.render("Press ESC to exit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
if __name__ == "__main__":
    game = Game()
    game.run()