# Forest Protector - Tower Defense Game
## Installation

1. **Prerequisites**

   * Ensure you have **Python 3.7 or higher** installed on your system.
   * Verify installation by running:

     ```bash
     python --version
     ```

2. **Clone the Repository**
   Open a terminal or command prompt and run:

   ```bash
   git clone https://github.com/Sambhav242005/Forest-Protector.git
   cd Forest-Protector
   ```

3. **Install Dependencies**
   Install all required Python packages using:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Game**
   Start the game with:

   ```bash
   python forest_protector.py
   ```

---
## Game Summary

Forest Protector is a strategic tower defense game where players defend against waves of enemies by placing and upgrading towers along a path. The goal is to prevent enemies from reaching the end of the path within a 5-minute time limit. As you progress through 10 waves of increasing difficulty, you'll face more enemies with stronger compositions. The game features 50 unique path combinations that change after each wave, requiring players to adapt their strategies dynamically.


## Basic Mechanics

- **Objective**: Prevent enemies from reaching the end of the path by strategically placing towers.
- **Lives**: Start with 3 lives. Lose a life each time an enemy reaches the end. Game ends when all lives are lost.
- **Time Limit**: Complete all 10 waves within 5 minutes.
- **Economy**: Start with $150. Earn money by defeating enemies. Spend money to place and upgrade towers.
- **Wave Progression**: Each wave brings more enemies with stronger compositions:
  - Wave 1: 5 enemies (all goblins)
  - Wave 10: 23 enemies (60% trolls, 30% orcs, 10% goblins)
- **Victory**: Complete all 10 waves to win the game.
- **Tower Upgrades**: Each tower type has a maximum upgrade level. Upgrades improve damage, range, fire rate, and accuracy.

## Tower Types
| Tower Type   | Cost  | Damage | Range | Fire Rate (shots/s) | Accuracy | Projectile Speed | Max Level | Color        |
| ------------ | ----- | ------ | ----- | ------------------- | -------- | ---------------- | --------- | ------------ |
| Archer Tower | \$50  | 20     | 150   | 2.5                 | 80%      | 8                | 5         | Archer Green |
| Cannon Tower | \$75  | 40     | 100   | 1.0                 | 65%      | 5                | 3         | Cannon Gray  |
| Magic Tower  | \$100 | 30     | 120   | 2.0                 | 95%      | 10               | 2         | Magic Purple |


## Enemy Types

| Enemy  | Health | Speed | Reward | Size | Color (RGB)   |
| ------ | ------ | ----- | ------ | ---- | ------------- |
| Goblin | 50     | 3.0   | \$25   | 20   | (200, 50, 50) |
| Orc    | 75     | 2.5   | \$35   | 30   | (100, 50, 50) |
| Troll  | 100    | 2.0   | \$50   | 25   | (50, 25, 25)  |

## Path System

The game features a dynamic path system with 50 unique combinations:

1. **Path Variety**: Five main path types:
   - Circular: Enemies follow a circular route
   - Straight: Enemies follow a mostly straight path with curves
   - Zigzag: Enemies follow a zigzag pattern
   - Spiral: Enemies follow a spiral route
   - Wave: Enemies follow a wave-like pattern
   - Random: 45 procedurally generated paths

2. **Path Changes**: Paths automatically change after each wave, forcing players to adapt their strategies.

3. **Refund System**: When the path changes, all towers are removed and players receive a 75% refund of their total tower costs.

4. **Visual Indicators**: The current path number is displayed in the UI (e.g., "Path: 5/50").

5. **Strategic Impact**: Different path layouts require different tower placement strategies, adding depth and replayability to the game.
