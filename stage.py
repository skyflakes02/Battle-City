import pyxel

CELL_SIZE = 16

EMPTY, BRICK, STONE, WATER, SEMI_CRACKED_BRICK, CRACKED_BRICK, FOREST, HOME, MIRROR_NE, MIRROR_SE, POWER_UP = range(11)

class Cell:
    def __init__(self, x, y, cell_type):
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.hits = 0
        self.exists = True

    def draw(self):
        if not self.exists:
            return
        elif self.cell_type == EMPTY:
            pyxel.blt(self.x, self.y, 0,48, 32, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == BRICK:
            pyxel.blt(self.x, self.y, 0, 0, 16, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == STONE:
            pyxel.blt(self.x, self.y, 0, 48, 16, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == WATER:
            pyxel.blt(self.x, self.y, 0, 0, 32, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == SEMI_CRACKED_BRICK:
            pyxel.blt(self.x, self.y, 0, 16, 16, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == CRACKED_BRICK:
            pyxel.blt(self.x, self.y, 0, 32, 16, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == FOREST:
            pyxel.blt(self.x, self.y, 0, 16, 32, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == HOME:
            pyxel.blt(self.x, self.y, 0, 32, 32, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == MIRROR_NE:
            pyxel.line(self.x + CELL_SIZE, self.y, self.x, self.y + CELL_SIZE, 4)
        elif self.cell_type == MIRROR_SE:
            pyxel.line(self.x, self.y, self.x + CELL_SIZE, self.y + CELL_SIZE, 4)
        elif self.cell_type == POWER_UP:
            pyxel.blt(self.x, self.y, 0, 0, 80, CELL_SIZE, CELL_SIZE, 0)
