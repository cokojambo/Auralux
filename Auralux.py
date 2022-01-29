import pygame
import random
from math import radians, sin, cos, atan

# PAWN_SPEED - скорость перемещения точки
PAWN_SPEED = 30
WIDTH, HEIGHT = 600, 400
TICK = 60


class Mapa:
    def __init__(self, screen, size_x, size_y):
        self.screen = screen
        self.size_x = size_x
        self.size_y = size_y
        self.planets = []
        self.pawns = []

    def set_planets(self, planets):
        self.planets = planets

    def spawn(self):
        for planet in self.planets:
            planet.spawn_pawns()

    def move(self):
        for pawn in self.pawns:
            pawn.move()

    def draw(self):
        for planet in self.planets:
            planet.draw()

        for pawn in self.pawns:
            pawn.draw()

    def pick_pawns(self, x1, y1, x2, y2):
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        for pawn in self.pawns:
            if x1 < pawn.x < x2 and y1 < pawn.y < y2:
                pawn.pick()

    def set_go_to(self, x, y):
        for pawn in self.pawns:
            if pawn.is_picked:
                pawn.go_to(x, y)
                pawn.is_picked = False

    def search_planet_with_coordinates(self, x, y):
        x, y = change_coordinates(x, y)
        for planet in self.planets:
            px, py, pr = planet.x, planet.y, planet.r
            if (px - x) ** 2 + (py - y) ** 2 <= pr ** 2:
                return change_coordinates(px, py)
        return False

    def bumps(self):
        for planet in self.planets:
            for pawn in self.pawns:
                if (planet.x, planet.y) == (pawn.x, pawn.y):
                    planet.bump(pawn)
        for pawn in self.pawns:
            for an_pawn in self.pawns:
                if id(pawn) != id(an_pawn) and \
                        (round(pawn.x), round(pawn.y)) == (round(an_pawn.x), round(an_pawn.y)):
                    pawn.bump(an_pawn)
                    break


class Planet:
    def __init__(self, mapa, x, y, lvl, max_lvl, color="gray"):
        self.mapa = mapa
        self.x = x
        self.y = y
        self.color = color
        self.r = max(1, lvl) * 10
        self.lvl = lvl
        self.max_lvl = max_lvl

        self.alive = True if self.lvl else False

        if self.alive:
            self.hp = 100
            self.color = color
            if self.lvl < self.max_lvl:
                self.lvl_up_points = 0
        else:
            self.alive_points = 0

    def spawn_pawns(self):
        if self.alive:
            for _ in range(self.lvl):
                self.spawn_pawn()

    def spawn_pawn(self):
        pawn = Pawn(self.mapa, self.x, self.y, self.color)
        self.mapa.pawns.append(pawn)
        dx = random.randint(-self.r - 2, self.r + 2) * self.lvl
        dy = ((self.r + 2) ** 2 - dx ** 2) ** 0.5
        if random.randint(0, 1):
            dy = -dy
        pawn.go_to(self.x + dx, self.y + dy)

    def born(self, color):
        self.alive = True
        self.lvl = 1
        self.hp = self.lvl * 100
        self.color = color
        if self.lvl < self.max_lvl:
            self.lvl_up_points = 0

    def die(self):
        self.alive = False
        self.alive_points = 0
        self.lvl = 0
        self.r = 10
        self.color = "grey"

    def lvl_up(self):
        self.lvl += 1
        self.lvl_up_points = 0

    def bump(self, pawn):
        if self.alive:
            if pawn.color == self.color:
                if self.hp < 100:
                    self.hp += 1
                    pawn.die()
                elif self.max_lvl > self.lvl:
                    self.lvl_up_points += 1
                    if self.lvl < self.max_lvl and self.lvl_up_points == 100:
                        self.lvl_up()
                    pawn.die()
                else:
                    dx = random.randint(-2 - self.r, 2 + self.r)
                    dy = ((self.r + 2) ** 2 - dx ** 2) ** 0.5
                    if random.randint(0, 1):
                        dy = -dy
                    pawn.go_to(self.x + dx, self.y + dy)
            else:
                self.hp -= 1
                if not self.hp:
                    self.die()
                pawn.die()
        else:
            self.alive_points += 1
            if self.alive_points == 100:
                self.born(pawn.color)
            pawn.die()

    def draw(self):
        pygame.draw.circle(self.mapa.screen, self.color,
                           change_coordinates(self.x, self.y), self.r)
        if self.alive:
            if self.hp < 100:
                draw_bar(self.mapa.screen, self.x, self.y + self.r + 8, self.hp, 100)
            elif self.max_lvl > self.lvl and self.lvl_up_points:
                draw_bar(self.mapa.screen, self.x, self.y + self.r + 8, self.lvl_up_points, 100)
        else:
            if self.alive_points:
                draw_bar(self.mapa.screen, self.x, self.y + self.r + 8, self.alive_points, 100)


class Pawn:
    def __init__(self, mapa, x, y, color):
        self.mapa = mapa
        self.x = x
        self.y = y
        self.color = color
        self.v = PAWN_SPEED
        self.to_x = x
        self.to_y = y
        self.is_picked = False

    def pick(self):
        self.is_picked = True

    def move(self):
        if not(self.x == self.to_x and self.y == self.to_y):
            if type(self.to_y) == complex:
                print(*[self])
            vx, vy = get_projections(self.x, self.y, self.to_x, self.to_y, self.v)
            if abs(vx / 1000 * TICK) >= abs(self.to_x - self.x) and abs(vy / 1000 * TICK) >= abs(self.to_y - self.y):
                self.x = self.to_x
                self.y = self.to_y
            else:
                self.x += vx / 1000 * TICK
                self.y += vy / 1000 * TICK

    def go_to(self, to_x, to_y):
        self.to_x = to_x
        self.to_y = to_y

    def bump(self, pawn):
        if pawn.color != self.color:
            pawn.die()
            self.die()

    def die(self):
        self.mapa.pawns.remove(self)

    def draw(self):
        pygame.draw.circle(self.mapa.screen, self.color, change_coordinates(self.x, self.y), 2)

    def __repr__(self):
        return f"Pawn(color={self.color}, x={self.x}, y={self.y}, " \
               f"to_x={self.to_x}, to_y={self.to_y}, is_picked={self.is_picked})"


def get_projections(x0, y0, to_x, to_y, phy_val):
    alpha = get_alpha(x0, y0, to_x, to_y)
    phy_val_x = phy_val * cos(alpha)
    phy_val_y = phy_val * sin(alpha)
    if to_x < x0:
        phy_val_x = -phy_val_x
    if to_y < y0:
        phy_val_y = -phy_val_y
    return phy_val_x, phy_val_y


def get_alpha(x0, y0, to_x, to_y):
    if not to_x - x0:
        return radians(90)
    return atan(abs(to_y - y0) / abs(to_x - x0))


def change_coordinates(x, y):
    return x, HEIGHT - y


def rect_constructor(x1, y1, x2, y2):
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return x1, y1, x2 - x1, y2 - y1


def draw_bar(screen, x, y, points, max_points, lx=20, ly=6):
    x, y = change_coordinates(x, y)
    pygame.draw.rect(screen, "grey", (x - lx // 2, y - ly // 2, lx, ly), 1)
    pygame.draw.rect(screen, "red",
                     (x - lx // 2 + 1, y - ly // 2 + 1, (lx - 2) * points / max_points, ly - 2), 0)


def main():
    pygame.init()
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    background_color = 'black'
    fps = 60
    running = True

    mapa = Mapa(screen, WIDTH, HEIGHT)
    planets = [Planet(mapa, 175, 150, 1, 2, "blue"), Planet(mapa, 225, 100, 1, 2, "blue"),
               Planet(mapa, 250, 300, 1, 2, "green"), Planet(mapa, 350, 300, 1, 2, "green"),
               Planet(mapa, 375, 100, 1, 2, "orange"), Planet(mapa, 425, 150, 1, 2, "orange"),
               Planet(mapa, 300, 200, 0, 2, "gray")]

    mapa.set_planets(planets)

    SPAWNPAWNS = pygame.USEREVENT + 1
    PAWNSMOVE = pygame.USEREVENT + 2
    pygame.time.set_timer(SPAWNPAWNS, 500)
    pygame.time.set_timer(PAWNSMOVE, TICK)

    lx, ly = -1, -1
    st_x, st_y = -1, -1
    en_x, en_y = -1, -1

    fl_z1 = False
    fl_z2 = False

    while running:
        screen.fill(background_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SPAWNPAWNS:
                mapa.spawn()
            if event.type == PAWNSMOVE:
                mapa.move()
                mapa.bumps()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x == lx and y == ly and not fl_z2:
                    fl_z1 = True
                    st_x = x
                    st_y = y
                if fl_z2:
                    if mapa.search_planet_with_coordinates(x, y):
                        x, y = mapa.search_planet_with_coordinates(x, y)
                    mapa.pick_pawns(*change_coordinates(st_x, st_y),
                                    *change_coordinates(en_x, en_y))
                    mapa.set_go_to(*change_coordinates(x, y))
                    fl_z2 = False
                lx = x
                ly = y
            if event.type == pygame.MOUSEBUTTONUP:
                if fl_z1:
                    fl_z1 = False
                    fl_z2 = True
                    en_x, en_y = event.pos
            if fl_z1:
                pygame.draw.rect(screen, "green", rect_constructor(st_x, st_y, *pygame.mouse.get_pos()), 2)
            if fl_z2:
                pygame.draw.rect(screen, "green", rect_constructor(st_x, st_y, en_x, en_y), 2)

        mapa.draw()
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    main()
