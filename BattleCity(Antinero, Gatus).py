import pyxel
import random
from stage import Cell

SCREEN_WIDTH = 415
SCREEN_HEIGHT = 250
TANK_SPEED = 2
BULLET_SPEED = 4
TANK_SPRITE_SIZE = 16
CELL_SIZE = 16

UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3

EMPTY, BRICK, STONE, WATER, SEMI_CRACKED_BRICK, CRACKED_BRICK, FOREST, HOME, MIRROR_NE, MIRROR_SE, POWER_UP = range(11)

class Bullet:
    def __init__(self, x, y, direction, is_enemy=False):
        self.x = x
        self.y = y
        self.direction = direction
        self.exists = True
        self.is_enemy = is_enemy

    def update(self):
        if self.direction == UP:
            self.y -= BULLET_SPEED
        elif self.direction == DOWN:
            self.y += BULLET_SPEED
        elif self.direction == LEFT:
            self.x -= BULLET_SPEED
        elif self.direction == RIGHT:
            self.x += BULLET_SPEED

    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT)

class EnemyTank:
    def __init__(self):
        self.x = 21 * CELL_SIZE
        self.y = 1 * CELL_SIZE
        self.direction = DOWN
        self.bullets = []
        self.shoot_interval = 60  
        self.shoot_timer = 0
        self.hits = 0
        self.tank_type = 1

    def update(self, cells):
        if self.shoot_timer <= 0:
            self.shoot_bullet()
            self.shoot_timer = self.shoot_interval
        else:
            self.shoot_timer -= 3

        if random.random() < 0.05: 
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        new_x = self.x
        new_y = self.y

        if self.direction == UP:
            new_y -= TANK_SPEED
        elif self.direction == DOWN:
            new_y += TANK_SPEED
        elif self.direction == LEFT:
            new_x -= TANK_SPEED
        elif self.direction == RIGHT:
            new_x += TANK_SPEED

        if not self.is_collision_with_cells(new_x, new_y, cells):
            self.x = new_x
            self.y = new_y

        self.x = max(0, min(self.x, SCREEN_WIDTH - TANK_SPRITE_SIZE))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - TANK_SPRITE_SIZE))

    def is_collision_with_cells(self, x, y, cells):
        for cell in cells:
            if cell.exists and cell.cell_type in {BRICK, SEMI_CRACKED_BRICK, CRACKED_BRICK, STONE, WATER, HOME, MIRROR_NE, MIRROR_SE}:
                if (x < cell.x + CELL_SIZE and
                    x + TANK_SPRITE_SIZE > cell.x and
                    y < cell.y + CELL_SIZE and
                    y + TANK_SPRITE_SIZE > cell.y):
                    return True
        return False

    def shoot_bullet(self):
        bullet_x = self.x + TANK_SPRITE_SIZE // 2 - 2
        bullet_y = self.y + TANK_SPRITE_SIZE // 2 - 2
        bullet = Bullet(bullet_x, bullet_y, self.direction, is_enemy=True)
        self.bullets.append(bullet)
        pyxel.play(0, 1)

    def draw(self):
        if self.tank_type == 1:
            tank_sprites = [(0, 48), (16, 48), (32, 48), (48, 48)]
        else:
            tank_sprites = [(0, 64), (16, 64), (32, 64), (48, 64)]
        pyxel.blt(self.x, self.y, 0, *tank_sprites[self.direction], TANK_SPRITE_SIZE, TANK_SPRITE_SIZE, 0) 
        for bullet in self.bullets:
            pyxel.rect(bullet.x, bullet.y, 2, 2, 8)

    def is_destroyed(self):
        return self.hits == 1
    
class BattleCity:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Battle City")
        pyxel.load("battlecity.pyxres")
        self.tank_x = 4 * CELL_SIZE
        self.tank_y = 15 * CELL_SIZE
        self.tank_direction = UP
        self.player_bullets = []
        self.enemy_tank = EnemyTank()
        self.enemy_tank.hits = 0
        self.enemy_tank_count = 0  
        self.cells = self.create_cells()
        self.create_corner_mirrors()
        self.game_over = False
        self.game_won = False
        self.player_lives = 2  
        self.shoot_interval = 15  
        self.shoot_timer = 0
        self.power_up_active = False
        self.power_up_duration = 300
        self.power_up_timer = 0
        self.power_up_lifetime = 600  
        self.power_up_placed = False     

        pyxel.sound(0).set("a2", "t", "7", "n", 3)  # Player shooting sound
        pyxel.sound(1).set("c3", "t", "6", "f", 5)  # Enemy shooting
        pyxel.sound(2).set("e2g2c3", "t", "7", "n",2)  # Game over sound
        pyxel.sound(3).set("c2", "t", "7", "n", 3)  # Bullet hitting a target
        pyxel.sound(4).set("f2a2c3f3", "t", "7", "n", 2)  # Game won sound

        pyxel.run(self.update, self.draw)
    
    def create_cells(self):
        cells = []
        home_created = False
        mirror_cells_placed = False 
        
        for y in range(10, SCREEN_HEIGHT, CELL_SIZE):
            for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                cell_type = EMPTY

                if x == 0 and y == SCREEN_HEIGHT - CELL_SIZE:
                    cell_type = EMPTY

                elif x == SCREEN_WIDTH - CELL_SIZE and y == 0:
                    cell_type = EMPTY

                elif not home_created:
                    cell_type = HOME
                    home_created = True

                elif not mirror_cells_placed and (x == CELL_SIZE or x == SCREEN_WIDTH - 2 * CELL_SIZE) and (y == CELL_SIZE or y == SCREEN_HEIGHT - 2 * CELL_SIZE):
                    cell_type = MIRROR_NE if x == CELL_SIZE and y == CELL_SIZE else MIRROR_SE
                    mirror_cells_placed = True 

                elif random.random() < 0.6: 
                    cell_type = EMPTY

                else:
                    cell_type = random.choice([BRICK, STONE, WATER, FOREST, POWER_UP])

                cells.append(Cell(x, y, cell_type))

        return cells

    def create_corner_mirrors(self):
        self.cells.append(Cell(CELL_SIZE, CELL_SIZE, MIRROR_NE))  
        self.cells.append(Cell(SCREEN_WIDTH - 2 * CELL_SIZE, CELL_SIZE, MIRROR_SE))  
        self.cells.append(Cell(CELL_SIZE, SCREEN_HEIGHT - 2 * CELL_SIZE, MIRROR_SE))  
        self.cells.append(Cell(SCREEN_WIDTH - 2 * CELL_SIZE, SCREEN_HEIGHT - 2 * CELL_SIZE, MIRROR_NE))

    def is_position_valid(self, x, y, cells):
        for cell in cells:
            if cell.x == x and cell.y == y:
                return False
        return True

    def update(self):
        new_tank_x = self.tank_x 
        new_tank_y = self.tank_y

        if pyxel.btn(pyxel.KEY_W):
            new_tank_y -= TANK_SPEED * (2 if self.power_up_active else 1)
            self.tank_direction = UP
        elif pyxel.btn(pyxel.KEY_UP):
            new_tank_y -= TANK_SPEED * (2 if self.power_up_active else 1)
            self.tank_direction = UP
        elif pyxel.btn(pyxel.KEY_S):
            new_tank_y += TANK_SPEED * (2 if self.power_up_active else 1)
            self.tank_direction = DOWN
        elif pyxel.btn(pyxel.KEY_DOWN):
            new_tank_y += TANK_SPEED * (2 if self.power_up_active else 1)
            self.tank_direction = DOWN
        elif pyxel.btn(pyxel.KEY_A):
            new_tank_x -= TANK_SPEED * (2 if self.power_up_active else 1)
            self.tank_direction = LEFT
        elif pyxel.btn(pyxel.KEY_LEFT):
            new_tank_x -= TANK_SPEED * (2 if self.power_up_active else 1)
            self.tank_direction = LEFT
        elif pyxel.btn(pyxel.KEY_D):
            new_tank_x += TANK_SPEED * (2 if self.power_up_active else 1)
            self.tank_direction = RIGHT
        elif pyxel.btn(pyxel.KEY_RIGHT):
            new_tank_x += TANK_SPEED * (2 if self.power_up_active else 1)
            self.tank_direction = RIGHT

        if self.power_up_active:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.power_up_active = False
        if self.power_up_placed:
            self.power_up_spawn_timer += 1
            if self.power_up_spawn_timer >= self.power_up_lifetime:
                self.remove_power_up()
                
        if not self.is_collision_with_cells(new_tank_x, new_tank_y):
            self.tank_x = new_tank_x
            self.tank_y = new_tank_y

        if pyxel.btn(pyxel.KEY_SPACE):
            if self.shoot_timer <= 0:
                self.shoot_bullet()
                self.shoot_timer = self.shoot_interval
        if self.shoot_timer > 0:
            self.shoot_timer -= 3

        self.tank_x = max(0, min(self.tank_x, SCREEN_WIDTH - TANK_SPRITE_SIZE))
        self.tank_y = max(0, min(self.tank_y, SCREEN_HEIGHT - TANK_SPRITE_SIZE))

        for bullet in self.player_bullets:
            if (bullet.x + 2 >= self.enemy_tank.x and bullet.x <= self.enemy_tank.x + TANK_SPRITE_SIZE and 
                bullet.y + 2 >= self.enemy_tank.y and bullet.y <= self.enemy_tank.y + TANK_SPRITE_SIZE):
                self.enemy_tank.hits += 1
                bullet.exists = False
                pyxel.play(0, 3)
                if self.enemy_tank.is_destroyed():
                    self.enemy_tank_count += 1
                    if self.enemy_tank_count < 3: 
                        self.enemy_tank = EnemyTank()
                    else:
                        self.game_won = True
                        pyxel.play(0, 4)

        for bullet in self.player_bullets:
            bullet.update()

        self.handle_bullet_collision()

        self.player_bullets = [bullet for bullet in self.player_bullets if bullet.exists and not bullet.is_off_screen()]

        self.enemy_tank.update(self.cells)

        for bullet in self.enemy_tank.bullets:
            bullet.update()

        for bullet in self.enemy_tank.bullets:
            if (bullet.x + 2 >= self.tank_x and bullet.x <= self.tank_x + TANK_SPRITE_SIZE and 
                bullet.y + 2 >= self.tank_y and bullet.y <= self.tank_y + TANK_SPRITE_SIZE):
                self.player_lives -= 1
                if self.player_lives <= 0:
                    self.game_over = True
                    pyxel.play(0, 2)
                else:
                    self.tank_x = 4 * CELL_SIZE
                    self.tank_y = 15 * CELL_SIZE
                    self.tank_direction = UP

        self.enemy_tank.bullets = [bullet for bullet in self.enemy_tank.bullets if bullet.exists and not bullet.is_off_screen()]

        if pyxel.btn(pyxel.KEY_N):
            self.reset_game()

        if self.game_over or self.game_won:
            if pyxel.btn(pyxel.KEY_Q):
                pyxel.quit()
            pyxel.stop()
        else:
            pyxel.playm(0, loop=True)

    def is_collision_with_cells(self, x, y):
        for cell in self.cells:
            if cell.exists and cell.cell_type in {BRICK, STONE, WATER, SEMI_CRACKED_BRICK, CRACKED_BRICK, HOME, MIRROR_NE, MIRROR_SE}:
                if (x < cell.x + CELL_SIZE and
                    x + TANK_SPRITE_SIZE > cell.x and
                    y < cell.y + CELL_SIZE and
                    y + TANK_SPRITE_SIZE > cell.y):
                    if cell.cell_type == POWER_UP:
                        cell.exists = False
                        self.power_up_active = True
                        self.power_up_timer = self.power_up_duration
                        self.power_up_placed = False
                        self.power_up_spawn_timer = 0
                    return True
        return False

    def update_bullets(self):
        for bullet in self.player_bullets:
            bullet.update()
            if bullet.is_off_screen():
                bullet.exists = False

        self.player_bullets = [bullet for bullet in self.player_bullets if bullet.exists]

        for bullet in self.enemy_tank.bullets:
            bullet.update()
            if bullet.is_off_screen():
                bullet.exists = False

        self.enemy_tank.bullets = [bullet for bullet in self.enemy_tank.bullets if bullet.exists]

    def update_enemy_tank(self):
        self.enemy_tank.update(self.cells)

    def check_collisions(self):
        for bullet in self.player_bullets:
            if not bullet.exists:
                continue

            for cell in self.cells:
                if cell.exists and cell.cell_type in {BRICK, SEMI_CRACKED_BRICK, CRACKED_BRICK, STONE, HOME, POWER_UP}:
                    if (bullet.x < cell.x + CELL_SIZE and
                        bullet.x + 2 > cell.x and
                        bullet.y < cell.y + CELL_SIZE and
                        bullet.y + 2 > cell.y):
                        bullet.exists = False
                        cell.hits += 1
                        pyxel.play(0, 3)
                        if cell.cell_type == BRICK and cell.hits == 1:
                            cell.cell_type = SEMI_CRACKED_BRICK
                        elif cell.cell_type == BRICK and cell.hits == 2:
                            cell.cell_type = CRACKED_BRICK
                        elif cell.cell_type == SEMI_CRACKED_BRICK and cell.hits == 1:
                            cell.cell_type = CRACKED_BRICK
                        elif cell.cell_type == CRACKED_BRICK and  cell.hits == 1:
                            cell.exists = False
                        elif cell.cell_type == STONE and cell.hits == 2:
                            cell.exists = False
                        elif cell.cell_type == POWER_UP:
                            cell.exists = False
                            self.power_up_active = True
                            self.power_up_timer = self.power_up_duration
                        elif cell.cell_type == HOME:
                            cell.exists = False
                            self.game_over = True
                        break

            if (bullet.x < self.enemy_tank.x + TANK_SPRITE_SIZE and
                bullet.x + 2 > self.enemy_tank.x and
                bullet.y < self.enemy_tank.y + TANK_SPRITE_SIZE and
                bullet.y + 2 > self.enemy_tank.y):
                bullet.exists = False
                self.enemy_tank.hits += 1
                pyxel.play(0, 3)
                if self.enemy_tank.is_destroyed():
                    self.enemy_tank_count += 1
                    if self.enemy_tank_count == 1:
                        self.enemy_tank = EnemyTank() 
                        self.enemy_tank.tank_type = 2 
                    else:
                        self.game_won = True

        for bullet in self.enemy_tank.bullets:
            if not bullet.exists:
                continue

            if (bullet.x < self.tank_x + TANK_SPRITE_SIZE and
                bullet.x + 2 > self.tank_x and
                bullet.y < self.tank_y + TANK_SPRITE_SIZE and
                bullet.y + 2 > self.tank_y):
                bullet.exists = False
                self.player_lives -= 1
                pyxel.play(0, 3)
                if self.player_lives == 0:
                    self.game_over = True

    def handle_bullet_collision(self):
        for bullet in self.player_bullets:
            for cell in self.cells:
                if cell.exists:
                    if (bullet.x + 2 >= cell.x and bullet.x <= cell.x + CELL_SIZE and 
                        bullet.y + 2 >= cell.y and bullet.y <= cell.y + CELL_SIZE):
                        if cell.cell_type == BRICK:
                            cell.cell_type = SEMI_CRACKED_BRICK
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == SEMI_CRACKED_BRICK:
                            cell.cell_type = CRACKED_BRICK
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == CRACKED_BRICK:
                            cell.exists = False
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == STONE:
                            bullet.exists = False
                        elif cell.cell_type == HOME:
                            cell.exists = False
                            bullet.exists = False
                            self.game_over = True
                            pyxel.play(0, 2)
                        elif cell.cell_type == MIRROR_NE:
                            if bullet.direction == UP:
                                bullet.direction = RIGHT
                            elif bullet.direction == DOWN:
                                bullet.direction = LEFT
                            elif bullet.direction == LEFT:
                                bullet.direction = DOWN
                            elif bullet.direction == RIGHT:
                                bullet.direction = UP
                        elif cell.cell_type == MIRROR_SE:
                            if bullet.direction == UP:
                                bullet.direction = LEFT
                            elif bullet.direction == DOWN:
                                bullet.direction = RIGHT
                            elif bullet.direction == LEFT:
                                bullet.direction = UP
                            elif bullet.direction == RIGHT:
                                bullet.direction = DOWN

        for bullet in self.enemy_tank.bullets:
            for cell in self.cells:
                if cell.exists:
                    if (bullet.x + 2 >= cell.x and bullet.x <= cell.x + CELL_SIZE and 
                        bullet.y + 2 >= cell.y and bullet.y <= cell.y + CELL_SIZE):
                        if cell.cell_type == BRICK:
                            cell.cell_type = SEMI_CRACKED_BRICK
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == SEMI_CRACKED_BRICK:
                            cell.cell_type = CRACKED_BRICK
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == CRACKED_BRICK:
                            cell.exists = False
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == STONE:
                            bullet.exists = False
                        elif cell.cell_type == HOME:
                            cell.exists = False
                            bullet.exists = False
                            self.game_over = True
                            pyxel.play(0, 2)
                        elif cell.cell_type == MIRROR_NE:
                            if bullet.direction == UP:
                                bullet.direction = RIGHT
                            elif bullet.direction == DOWN:
                                bullet.direction = LEFT
                            elif bullet.direction == LEFT:
                                bullet.direction = DOWN
                            elif bullet.direction == RIGHT:
                                bullet.direction = UP
                        elif cell.cell_type == MIRROR_SE:
                            if bullet.direction == UP:
                                bullet.direction = LEFT
                            elif bullet.direction == DOWN:
                                bullet.direction = RIGHT
                            elif bullet.direction == LEFT:
                                bullet.direction = UP
                            elif bullet.direction == RIGHT:
                                bullet.direction = DOWN

    def shoot_bullet(self):
        bullet_x = self.tank_x + TANK_SPRITE_SIZE // 2 - 2
        bullet_y = self.tank_y + TANK_SPRITE_SIZE // 2 - 2
        if self.tank_direction == UP:
            bullet_y = self.tank_y
        elif self.tank_direction == DOWN:
            bullet_y = self.tank_y + TANK_SPRITE_SIZE
        elif self.tank_direction == LEFT:
            bullet_x = self.tank_x
        elif self.tank_direction == RIGHT:
            bullet_x = self.tank_x + TANK_SPRITE_SIZE

        bullet = Bullet(bullet_x, bullet_y, self.tank_direction)
        self.player_bullets.append(bullet)
        pyxel.play(0, 0)

    def draw(self):
        pyxel.cls(0)

        for cell in self.cells:
            cell.draw()

        self.enemy_tank.draw()

        for bullet in self.player_bullets:
            pyxel.circ(bullet.x, bullet.y, 2, 12)

        for bullet in self.enemy_tank.bullets:
            pyxel.circ(bullet.x, bullet.y, 2, 4)

        tank_sprites = [(0, 0), (16, 0), (32, 0), (48, 0)]
        pyxel.blt(self.tank_x, self.tank_y, 0, * tank_sprites[self.tank_direction], TANK_SPRITE_SIZE, TANK_SPRITE_SIZE, 0)
        
        pyxel.text(5, 2, f"LIVES: {self.player_lives}", 8)
        pyxel.text(65, 2, f"KILLS: {self.enemy_tank_count}", 8)

        if self.game_over:
            pyxel.cls(0)
            pyxel.text(185, 95, "GAME OVER", pyxel.frame_count % 16)
            pyxel.text(165, 165, "PRESS 'N' TO RESTART", pyxel.frame_count % 16)
            pyxel.text(170, 180, "PRESS 'Q' TO QUIT", pyxel.frame_count % 16)
            pyxel.play(2, 2)
        elif self.game_won:
            pyxel.cls(0)
            pyxel.text(185, 95, "YOU WON!", pyxel.frame_count % 16)
            pyxel.text(165, 165, "PRESS 'N' TO RESTART", pyxel.frame_count % 16)
            pyxel.text(170, 180, "PRESS 'Q' TO QUIT", pyxel.frame_count % 16)
            pyxel.play(2, 4)

    def reset_game(self):
        self.tank_x = 4 * CELL_SIZE
        self.tank_y = 15 * CELL_SIZE
        self.enemy_tank.x = 21 * CELL_SIZE
        self.enemy_tank.y = 1 * CELL_SIZE
        self.tank_direction = UP
        self.enemy_tank_direction = DOWN
        self.player_bullets = []
        self.enemy_tank = EnemyTank()
        self.enemy_tank.hits = 0
        self.enemy_tank_count = 0

        for cell in self.cells:
            if cell.cell_type != MIRROR_NE and cell.cell_type != MIRROR_SE:
                cell.exists = True
                if cell.cell_type == HOME:
                    cell.hits = 0
                elif cell.cell_type in {SEMI_CRACKED_BRICK, CRACKED_BRICK}:
                    cell.cell_type = BRICK
                    
            self.game_over = False
            self.game_won = False
            self.player_lives = 2
            self.shoot_timer = 0

BattleCity()

