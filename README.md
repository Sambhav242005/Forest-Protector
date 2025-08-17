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
---
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

### Archer Tower
- **Cost**: $50
- **Damage**: 15
- **Range**: 150
- **Fire Rate**: 1.5 shots/second
- **Accuracy**: 80%
- **Max Level**: 5
- **Best For**: Long-range coverage with moderate damage

### Cannon Tower
- **Cost**: $75
- **Damage**: 40
- **Range**: 100
- **Fire Rate**: 0.5 shots/second
- **Accuracy**: 65%
- **Max Level**: 4
- **Best For**: High damage against strong enemies at short range

### Magic Tower
- **Cost**: $100
- **Damage**: 25
- **Range**: 120
- **Fire Rate**: 1.0 shots/second
- **Accuracy**: 95%
- **Max Level**: 6
- **Special Ability**: Predicts enemy movement for better accuracy
- **Best For**: High precision targeting with good range

---
## Enemy Types

### Goblin
- **Health**: 50
- **Speed**: 2.5 (fastest)
- **Reward**: $10
- **Appearance**: Small, red enemy
- **Threat Level**: Low

### Orc
- **Health**: 75
- **Speed**: 2.0 (medium)
- **Reward**: $12
- **Appearance**: Medium-sized, dark red enemy
- **Threat Level**: Medium

### Troll
- **Health**: 100
- **Speed**: 1.0 (slowest)
- **Reward**: $15
- **Appearance**: Large, dark brown enemy
- **Threat Level**: High

---
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
