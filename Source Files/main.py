import pygame as pg
from pygame import Color as Color, Vector2 as Vec2
import numpy as np
from dataclasses import dataclass

pg.init()
WIN_W = 1280
WIN_H = 720
SCREEN = pg.display.set_mode((WIN_W, WIN_H), flags=pg.DOUBLEBUF)
SCREEN.set_alpha(None)
CLOCK = pg.time.Clock()
mouse = pg.mouse
pg.mouse.set_visible(False)
mousepos = (0, 0)
DT = 0


def roundNumToNearest(value, round_to):
    value = round(value)
    try:
        n = value % round_to
        if n >= round_to / 2:
            return value + (round_to - n)
        else:
            return value - n
    except ZeroDivisionError:
        return value


def roundNumsToNearest(values, round_to):
    for value in values:
        value = round(value)
        try:
            n = value % round_to
            if n >= round_to / 2:
                yield value + (round_to - n)
            else:
                yield value - n
        except ZeroDivisionError:
            yield value


@dataclass
class POLYGONS:
    def __init__(self, size, action_type=None):
        self.size = size
        self.action_type = action_type
        # match action_type:
        #     case ACTION_TYPES.TRIANGLE:
        self.triangle = self._ISOCELES_TRIANGLE()
            # case ACTION_TYPES.PENTAGON:
        self.regular_pentagon = self._REGULAR_PENTAGON()
            # case ACTION_TYPES.STAR:
        self.star = self._STAR()
            # case ACTION_TYPES.HEXAGON:
        self.hexagon = self._HEXAGON()
    def _ISOCELES_TRIANGLE(self):
        return np.array(((0, self.size[1]),
                         (self.size[0] / 2, 0),
                         (self.size[0], self.size[1]),
                         (0, self.size[1])))

    def _REGULAR_PENTAGON(self):
        vertices = np.array((
            (0.5, 0),
            (0, 0.37918),
            (0.190984, 1),
            (0.809016, 1),
            (1, 0.37918)
        ))
        vertices *= np.array((self.size[0], self.size[1]))
        return vertices

    def _STAR(self):
        vertices = np.array((
            (0.5, 0),
            (0.349342, 0.337536),
            (0, 0.384753),
            (0.25623, 0.638855),
            (0.190987, 1),
            (0.5, 0.825081),
            (0.809014, 1),
            (0.74377, 0.638855),
            (1, 0.384753),
            (0.650659, 0.337536),
        ))
        vertices *= np.array((self.size[0], self.size[1]))
        return vertices

    def _HEXAGON(self):
        vertices = np.array((
            (0.5, 0),
            (0, 0.25),
            (0, 0.75),
            (0.5, 1.00),
            (1, 0.75),
            (1, 0.25)
        ))
        vertices *= np.array((self.size[0], self.size[1]))
        return vertices


@dataclass
class FONTS:
    default = "bahnschrift"


@dataclass
class COLOR:
    BLACK = Color("BLACK")
    WHITE = Color("WHITE")
    COLORKEY = Color(1, 1, 1)
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)


@dataclass
class GLOBALS:
    pass


class FpsCounter:
    def __init__(self, color, text_height):
        self.text = 'NULL'
        self.color = Color(color)
        self.font = pg.font.SysFont(FONTS.default, text_height)
        self.surf = self.font.render(self.text, True, self.color)

    def draw(self, display):
        self.text = str(int(CLOCK.get_fps()))
        self.surf = self.font.render(self.text, True, self.color)
        display.blit(self.surf, self.surf.get_rect(topright=(WIN_W, 0)))


FpsCounter = FpsCounter(COLOR.WHITE, 22)


class Grid():
    def __init__(self, step_x, step_y, color=Color(64, 64, 64), width=1):
        self.surf = pg.Surface((WIN_W, WIN_H))
        self.surf.set_colorkey(COLOR.COLORKEY)
        self.surf.fill(self.surf.get_colorkey())
        if step_x > 0:
            for x in range(0, WIN_W + 1, step_x):
                pg.draw.line(self.surf, color, (x, 0), (x, WIN_H), width=width)
        if step_y > 0:
            for y in range(0, WIN_H + 1, step_y):
                pg.draw.line(self.surf, color, (0, y), (WIN_W, y), width=width)

    def draw(self, display, special_flags=0):
        display.blit(self.surf, (0, 0), special_flags=special_flags)


GLOBALS.GRID_SIZE = 0
grid = Grid(GLOBALS.GRID_SIZE, GLOBALS.GRID_SIZE)


class Shape(pg.sprite.Sprite):
    def __init__(self, pos, size, shape):
        pg.sprite.Sprite.__init__(self)
        self.polygons = None
        self.shape = shape
        self.shape_color = pg.Color(128, 128, 128)
        self.image = pg.Surface(size)
        self.image.set_colorkey(Color(1, 1, 1))
        self.image.fill(self.image.get_colorkey())
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        self.resize_data(False, False)

    def resize_data(self, flip_x, flip_y):
        self.image = pg.transform.scale(self.image, self.rect.size)
        self.polygons = POLYGONS(self.rect.size, self.shape)
        self.image.fill(self.image.get_colorkey())
        match self.shape:
            case ACTION_TYPES.RECTANGLE:
                pg.draw.rect(self.image, self.shape_color, ((0, 0), (self.rect.size)))
            case ACTION_TYPES.CIRCLE:
                pg.draw.ellipse(self.image, self.shape_color, ((0, 0), (self.rect.size)))
            case ACTION_TYPES.TRIANGLE:
                pg.draw.polygon(self.image, self.shape_color, (self.polygons.triangle))
            case ACTION_TYPES.PENTAGON:
                pg.draw.polygon(self.image, self.shape_color, (self.polygons.regular_pentagon))
            case ACTION_TYPES.STAR:
                pg.draw.polygon(self.image, self.shape_color, (self.polygons.star))
            case ACTION_TYPES.HEXAGON:
                pg.draw.polygon(self.image, self.shape_color, (self.polygons.hexagon))
        if flip_x and flip_y:
            self.rect = self.image.get_rect(bottomright=self.rect.topleft)
        elif flip_x:
            self.rect = self.image.get_rect(topright=self.rect.topleft)
        elif flip_y:
            self.rect = self.image.get_rect(bottomleft=self.rect.topleft)
        else:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)

        self.image = pg.transform.flip(self.image, flip_x, flip_y)
        self.mask = pg.mask.from_surface(self.image)
        return self

    def draw(self, display):
        display.blit(self.image, self.rect)
        return self


class DeleteBox(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.color = pg.Color(30, 31, 82)
        self.image = pg.Surface(size)
        self.image.set_colorkey(Color(1, 1, 1))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        self.grid = Grid(20, 20, Color(32, 32, 32))
        self.resize_data(False, False)

    def resize_data(self, flip_x, flip_y):
        self.image = pg.transform.scale(self.image, self.rect.size)
        self.image.fill(self.color)
        if flip_x and flip_y:
            self.rect = self.image.get_rect(bottomright=self.rect.topleft)
        elif flip_x:
            self.rect = self.image.get_rect(topright=self.rect.topleft)
        elif flip_y:
            self.rect = self.image.get_rect(bottomleft=self.rect.topleft)
        else:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)

        self.image = pg.transform.flip(self.image, flip_x, flip_y)
        self.mask = pg.mask.from_surface(self.image)
        self.grid.draw(self.image, special_flags=pg.BLEND_ADD)
        return self

    def draw(self, display):
        display.blit(self.image, self.rect, special_flags=pg.BLEND_ADD)


class ACTION_TYPES:
    RECTANGLE = 'RECTANGLE'
    CIRCLE = 'CIRCLE'
    TRIANGLE = 'TRIANGLE'
    PENTAGON = 'PENTAGON'
    STAR = 'STAR'
    HEXAGON = 'HEXAGON'
    DELETE = 'DELETE'
    SHAPES = [RECTANGLE, CIRCLE, TRIANGLE, PENTAGON, STAR, HEXAGON]
    ACTION_TYPES = [*SHAPES, DELETE]


class MOUSE_ACTION_STATES:
    IDLE = 'NOT_DRAGGING'
    DRAGGING = 'DRAGGING'
    SHIFT = False


GLOBALS.MOUSE_ACTION = MOUSE_ACTION_STATES.IDLE
GLOBALS.ACTION_TYPE = ACTION_TYPES.RECTANGLE


class TSD:
    CURRENT_SHAPE = None
    START = (0, 0)
    END = (0, 0)
    WIDTH = 0
    HEIGHT = 0
    SIZE = (0, 0)


def dragNewShape(shape, color=COLOR.WHITE, step_size=0, shift_ratio=1 / 1):
    shape.rect.topleft = TSD.START
    TSD.END = np.array(tuple(roundNumsToNearest(mousepos, step_size)))
    TSD.WIDTH = (TSD.END[0] - TSD.START[0])
    TSD.HEIGHT = (TSD.END[1] - TSD.START[1])
    if not MOUSE_ACTION_STATES.SHIFT:
        TSD.SIZE = np.absolute(np.array([TSD.WIDTH, TSD.HEIGHT]))
    else:
        # Method 1
        # temp_shape_norm_half = roundNumToNearest(
        #     np.linalg.norm(np.array([TSD.WIDTH, TSD.HEIGHT])) / 2, step_size)
        # TSD.SIZE = np.absolute(
        #     np.array([roundNumToNearest(temp_shape_norm_half, step_size), temp_shape_norm_half]))

        # Method 2
        if TSD.WIDTH > TSD.HEIGHT:
            TSD.SIZE = np.array((TSD.HEIGHT, TSD.HEIGHT))
        else:
            TSD.SIZE = np.array((TSD.WIDTH, TSD.WIDTH))

        TSD.SIZE[0] *= shift_ratio
        np.abs(TSD.SIZE, TSD.SIZE)
    shape.rect.size = TSD.SIZE
    shape.shape_color = color
    if TSD.WIDTH < 0 and TSD.HEIGHT < 0:
        shape.resize_data(True, True)
    elif TSD.WIDTH < 0:
        shape.resize_data(True, False)
    elif TSD.HEIGHT < 0:
        shape.resize_data(False, True)
    else:
        shape.resize_data(False, False)


def changeActionTypeWithEvent(hotbar, event):
    match event.key:
        case pg.K_1:
            GLOBALS.ACTION_TYPE = ACTION_TYPES.RECTANGLE
            hotbar.switch_button()
        case pg.K_2:
            GLOBALS.ACTION_TYPE = ACTION_TYPES.CIRCLE
            hotbar.switch_button()
        case pg.K_3:
            GLOBALS.ACTION_TYPE = ACTION_TYPES.TRIANGLE
            hotbar.switch_button()
        case pg.K_4:
            GLOBALS.ACTION_TYPE = ACTION_TYPES.PENTAGON
            hotbar.switch_button()
        case pg.K_5:
            GLOBALS.ACTION_TYPE = ACTION_TYPES.STAR
            hotbar.switch_button()
        case pg.K_6:
            GLOBALS.ACTION_TYPE = ACTION_TYPES.HEXAGON
            hotbar.switch_button()
        case pg.K_d:
            GLOBALS.ACTION_TYPE = ACTION_TYPES.DELETE
            hotbar.switch_button()


shapes_group = pg.sprite.Group()


class ShapeButton():
    def __init__(self, rect, action_type, bg_color, border_color, shape_color, shape_scale):
        self.rect = pg.Rect(rect)
        self.surf = pg.Surface(self.rect.size)
        self.bg_color = bg_color
        self.surf.fill(self.bg_color)
        self.border_color = border_color
        self.shape_color = shape_color

        self.action_type = action_type
        self.shape_scale = shape_scale
        self.shape_image = pg.transform.scale_by(self.surf, self.shape_scale)
        self.shape_image.set_colorkey((1, 1, 1)); self.shape_image.fill(self.shape_image.get_colorkey())
        self.shape_rect = self.shape_image.get_rect(center=Vec2(self.rect.size) / 2)
        self.polygons = POLYGONS(Vec2(self.rect.size) * self.shape_scale, self.action_type)
        self.create_shape()


    def create_shape(self):
        match self.action_type:
            case ACTION_TYPES.RECTANGLE:
                pg.draw.rect(self.shape_image, self.shape_color, ((0, 0), self.shape_rect.size))
            case ACTION_TYPES.CIRCLE:
                pg.draw.ellipse(self.shape_image, self.shape_color, ((0, 0), self.shape_rect.size))
            case ACTION_TYPES.TRIANGLE:
                pg.draw.polygon(self.shape_image, self.shape_color, (self.polygons.triangle))
            case ACTION_TYPES.PENTAGON:
                pg.draw.polygon(self.shape_image, self.shape_color, (self.polygons.regular_pentagon))
            case ACTION_TYPES.STAR:
                pg.draw.polygon(self.shape_image, self.shape_color, (self.polygons.star))
            case ACTION_TYPES.HEXAGON:
                pg.draw.polygon(self.shape_image, self.shape_color, self.polygons.hexagon)
        return self

    def draw(self, display, special_flags=0):
        self.surf.blit(self.shape_image, self.shape_rect)
        pg.draw.rect(self.surf, self.border_color, self.surf.get_rect(), width=5)
        display.blit(self.surf, self.rect, special_flags=special_flags)
        return self
class TextButton():
    def __init__(self, rect, action_type, text, text_height, bg_color, border_color):
        self.rect = pg.Rect(rect)
        self.surf = pg.Surface(self.rect.size)
        self.bg_color = bg_color
        self.surf.fill(self.bg_color)
        self.border_color = border_color
        self.action_type = action_type
        font = pg.font.SysFont(FONTS.default, text_height)
        self.text_surf = font.render(text, True, Color('WHITE'))
        self.text_rect = self.text_surf.get_rect(center=Vec2(self.rect.size) / 2)

    def draw(self, display):
        self.surf.blit(self.text_surf, self.text_rect)
        pg.draw.rect(self.surf, self.border_color, self.surf.get_rect(), width=5)
        display.blit(self.surf, self.rect)
        return self
class HotBar:
    def __init__(self, num_buttons, button_size, padding, background_color, border_color):
        self.surf = pg.Surface((num_buttons * button_size[0] + num_buttons * padding, button_size[1]))
        self.surf.set_colorkey((1, 1, 1))
        self.surf.fill(self.surf.get_colorkey())
        self.rect = self.surf.get_rect(topleft=(10, 10))

        self.button_poses = [(x + off * padding, 0) for off, x in
                             enumerate(range(0, button_size[0] * num_buttons, button_size[0]))]
        self.button_bg_color = Color(background_color)
        self.button_bd_color = Color(border_color)
        self.buttons = []
        for pos, action_type in zip(self.button_poses[0:num_buttons - 1], ACTION_TYPES.SHAPES):
            self.buttons.append(
                ShapeButton((pos, button_size), action_type, self.button_bg_color, self.button_bd_color, COLOR.BLUE,
                            0.6))
        for pos, (action_type, text) in zip([self.button_poses[num_buttons - 1]], {ACTION_TYPES.DELETE: 'DEL'}.items()):
            self.buttons.append(
                TextButton((pos, button_size), action_type, text, 16, self.button_bg_color, self.button_bd_color))
        self.switch_button()

    def switch_button(self):
        for button in self.buttons:
            if not GLOBALS.ACTION_TYPE == button.action_type:
                bg_color = button.bg_color
            else:
                bg_color = button.bg_color - Color(50, 50, 50)
            button.surf.fill(bg_color)

    def draw(self, display):
        for button in self.buttons:
            button.draw(self.surf)
        display.blit(self.surf, self.rect)
        return self
HotBar = HotBar(7, (50, 50), 5, Color(100,100,100), Color(50,50,50))

class ColorSlider():
    def __init__(self, mininum, maximum, rect, text, background: pg.Surface, border_color):
        # Create bar
        self.bar_rect = pg.Rect(rect)
        self.bar = pg.Surface(self.bar_rect.size)
        self.bar.set_colorkey(Color(1,1,1)); self.bar.fill(self.bar.get_colorkey())
        self.bar.blit(pg.transform.scale(background, self.bar_rect.size), (0,0))
        pg.draw.rect(self.bar, border_color, self.bar.get_rect(), width=3)

        # text_ratio = 1/1
        # text_height = self.bar_rect.h

        norm = np.linalg.norm((self.bar_rect.w, self.bar_rect.h))
        ratio = self.bar_rect.w / self.bar_rect.h
        self.slide = pg.Surface(np.array((norm, norm * 3/4)) / 10)
        self.slide.set_colorkey(Color(1, 1, 1)); self.slide.fill(self.slide.get_colorkey())
        pg.draw.polygon(self.slide, Color('WHITE'), POLYGONS(self.slide.get_size()).triangle)
        self.slide_rect = self.slide.get_rect(midbottom=(self.bar_rect.w / 2, self.bar_rect.h + self.slide.get_height()/3))

        self.rect = pg.Rect((self.bar_rect.topleft),
                            (self.bar_rect.w + self.slide.get_width(), self.bar_rect.h + self.slide.get_height()/3))
        self.surf = pg.Surface(self.rect.size)
        self.surf.set_colorkey(Color(1,1,1)); self.surf.fill(self.surf.get_colorkey())

        self.being_dragged = False
        self.value = 0
    def hovered(self):
        return self.rect.y < mousepos[1] < self.rect.y + self.bar_rect.h and \
            self.rect.x + self.slide.get_width() / 2 < mousepos[0] < self.rect.x + self.bar_rect.w
    def update(self):
        if self.being_dragged:
            if mousepos[0] <= self.rect.x:
                self.value = 0
            elif mousepos[0] >= self.rect.x + self.bar_rect.w:
                self.value = 1
            else:
                  self.value = (mousepos[0] - self.rect.x) / self.bar_rect.w
            pg.draw.polygon(self.slide, Color('WHITE'), POLYGONS(self.slide.get_size()).triangle)
        self.slide_rect.centerx = self.bar_rect.w * self.value + (self.slide.get_width() / 2)
    def draw(self, display):
        self.update()
        self.surf.fill(self.surf.get_colorkey())
        self.surf.blit(self.bar, (self.slide.get_width() / 2, 0))
        self.surf.blit(self.slide, self.slide_rect)
        display.blit(self.surf, self.rect)
slider1_bg = pg.image.load(r'Images/slider_backgrounds/rainbow_strip.png').convert_alpha()
slider1 = ColorSlider(22, 150, (1065, 50, 200, 25), 'RGB', slider1_bg, Color(64,64,64))
class Cursor:
    def __init__(self):
        self.rect = None
        self.mask = None
        self.color = COLOR.GREEN
        self.surf = pg.Surface((6, 6))
        self.surf.set_colorkey(Color(1, 1, 1))
        self.update()

    def update(self):
        self.surf.fill(self.surf.get_colorkey())
        pg.draw.rect(self.surf, self.color, ((2, 0), (2, 6)))
        pg.draw.rect(self.surf, self.color, ((0, 2), (6, 2)))
        self.mask = pg.mask.from_surface(self.surf)

    def draw(self, display):
        self.rect = self.surf.get_rect(center=(mousepos))
        display.blit(self.surf, self.rect)


Cursor = Cursor()


class ClickTextButton():
    def __init__(self, rect, text, text_height, text_color, bg_color, border_color):
        self.button_rect = pg.Rect(rect)
        self.button_surf = pg.Surface(self.button_rect.size)
        self.bg_color = Color(bg_color)
        self.button_surf.fill(self.bg_color)
        self.border_color = border_color

        self.text_color = text_color
        font = pg.font.SysFont(FONTS.default, text_height)
        self.text_surf = font.render(text, True, Color(text_color))
        self.text_rect = self.text_surf.get_rect(center=Vec2(self.button_rect.size) / 2)

        self.hovered = False

    def update(self):
        if self.button_rect.collidepoint(mousepos):
            self.hovered = True
            bg_color = self.bg_color - Color(50, 50, 50)
        else:
            self.hovered = False
            bg_color = self.bg_color
        self.button_surf.fill(bg_color)

    def draw(self, display, special_flags=0):
        self.button_surf.blit(self.text_surf, self.text_rect)
        pg.draw.rect(self.button_surf, self.border_color, self.button_surf.get_rect(), width=5)
        display.blit(self.button_surf, self.button_rect, special_flags=special_flags)


class PauseScreen:
    def __init__(self):
        self.surf = pg.Surface((WIN_W, WIN_H))
        self.screen_rect = self.surf.get_rect()
        self.surf.set_colorkey(Color(1, 1, 1))
        self.surf.fill(self.surf.get_colorkey())

        self.background = pg.Surface(self.surf.get_size())
        self.background.fill(Color(64, 64, 64))

        num_buttons = 3
        self.button_size = (300, 100)
        self.button_positions = ((self.screen_rect.centerx, y + offset * 10) for
                                 offset, y in
                                 enumerate(range(75, self.button_size[1] * num_buttons, self.button_size[1])))
        self.buttons = {}
        for pos, (key, text) in zip(self.button_positions, {'res': 'Resume', 'clear': 'Clear', 'exit': 'Exit'}.items()):
            self.buttons[key] = (
                ClickTextButton((pos, self.button_size), text, 32, Color('BLACK'), Color(170, 170, 170),
                                Color(120, 120, 120)))
            self.buttons[key].button_rect = self.buttons[key].button_surf.get_rect(
                center=self.buttons[key].button_rect.topleft)

    def draw(self, display, special_flags=0):
        self.surf.blit(self.background, self.screen_rect, special_flags=0)
        for button in self.buttons.values():
            button.update()
            button.draw(self.surf)
        display.blit(self.surf, (0, 0), special_flags=special_flags)


Pause_Screen = PauseScreen()
paused = False

run = True
while run:
    SCREEN.fill(COLOR.BLACK)
    keys = pg.key.get_pressed()
    mousepos = np.array(mouse.get_pos())
    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                if not paused:
                    paused = True
                else:
                    paused = False
            if not paused:
                changeActionTypeWithEvent(HotBar, e)
            if e.key == pg.K_r:
                shapes_group.empty()
            if e.key == pg.K_LSHIFT:
                MOUSE_ACTION_STATES.SHIFT = True
        if e.type == pg.KEYUP:
            if e.key == pg.K_LSHIFT:
                MOUSE_ACTION_STATES.SHIFT = False
        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1:
                if not paused:
                    if any(GLOBALS.ACTION_TYPE == action_type for action_type in ACTION_TYPES.SHAPES):
                        GLOBALS.MOUSE_ACTION = MOUSE_ACTION_STATES.DRAGGING
                        TSD.START = np.array(tuple(roundNumsToNearest(mousepos, GLOBALS.GRID_SIZE)))
                        TSD.CURRENT_SHAPE = Shape(TSD.START, TSD.SIZE, GLOBALS.ACTION_TYPE)
                        shapes_group.add(TSD.CURRENT_SHAPE)
                    if GLOBALS.ACTION_TYPE == ACTION_TYPES.DELETE:
                        GLOBALS.MOUSE_ACTION = MOUSE_ACTION_STATES.DRAGGING
                        TSD.START = np.array(tuple(mousepos))
                        TSD.CURRENT_SHAPE = DeleteBox(TSD.START, TSD.SIZE)
                        shapes_group.add(TSD.CURRENT_SHAPE)
                    if slider1.hovered():
                        slider1.being_dragged = True
                if paused:
                    if Pause_Screen.buttons['res'].hovered:
                        paused = False
                    if Pause_Screen.buttons['clear'].hovered:
                        shapes_group.empty()
                        paused = False
                    if Pause_Screen.buttons['exit'].hovered:
                        run = False
            if e.button == 3:
                if not paused:
                    if GLOBALS.MOUSE_ACTION == MOUSE_ACTION_STATES.DRAGGING:
                        GLOBALS.MOUSE_ACTION = MOUSE_ACTION_STATES.IDLE
                        shapes_group.remove(TSD.CURRENT_SHAPE)
        if e.type == pg.MOUSEBUTTONUP:
            if e.button == 1:
                if not paused:
                    if GLOBALS.MOUSE_ACTION == MOUSE_ACTION_STATES.DRAGGING:
                        if any(GLOBALS.ACTION_TYPE == action_type for action_type in ACTION_TYPES.SHAPES):
                            dragNewShape(TSD.CURRENT_SHAPE, Color(128, 128, 128), GLOBALS.GRID_SIZE,
                                         TSD.SHIFT_RATIO)
                        if GLOBALS.ACTION_TYPE == ACTION_TYPES.DELETE:
                            for shape in shapes_group:
                                if shape != TSD.CURRENT_SHAPE:
                                    if shape.mask.overlap(TSD.CURRENT_SHAPE.mask, (
                                            TSD.CURRENT_SHAPE.rect.x - shape.rect.x,
                                            TSD.CURRENT_SHAPE.rect.y - shape.rect.y)) \
                                            or shape.mask.overlap(Cursor.mask, (
                                            mousepos[0] - shape.rect.x, mousepos[1] - shape.rect.y)):
                                        shapes_group.remove(shape)
                            shapes_group.remove(TSD.CURRENT_SHAPE)
                        GLOBALS.MOUSE_ACTION = MOUSE_ACTION_STATES.IDLE
                        TSD.START = TSD.END = TSD.SIZE = (0, 0)
                        TSD.WIDTH = TSD.HEIGHT = 0

                    slider1.being_dragged = False
    if not paused:
        grid.draw(SCREEN)
        if GLOBALS.MOUSE_ACTION == MOUSE_ACTION_STATES.DRAGGING:
            if any(GLOBALS.ACTION_TYPE == action_type for action_type in ACTION_TYPES.SHAPES):
                if GLOBALS.ACTION_TYPE == ACTION_TYPES.TRIANGLE:
                    TSD.SHIFT_RATIO = 4 / 3
                elif GLOBALS.ACTION_TYPE == ACTION_TYPES.PENTAGON or GLOBALS.ACTION_TYPE == ACTION_TYPES.STAR:
                    TSD.SHIFT_RATIO = 0.951056516295 / 0.904508497185
                else:
                    TSD.SHIFT_RATIO = 1 / 1
                dragNewShape(TSD.CURRENT_SHAPE, Color(219, 55, 172, a=100), GLOBALS.GRID_SIZE,
                             TSD.SHIFT_RATIO)
            elif GLOBALS.ACTION_TYPE == ACTION_TYPES.DELETE:
                dragNewShape(TSD.CURRENT_SHAPE)
        for shape in shapes_group:
            shape.draw(SCREEN)
            if shape.mask.overlap(Cursor.mask, (mousepos[0] - shape.rect.x, mousepos[1] - shape.rect.y)):
                Cursor.color = (COLOR.GREEN)
            else:
                Cursor.color = (COLOR.GREEN)

        HotBar.draw(SCREEN)
        slider1.draw(SCREEN)
    elif paused:
        Pause_Screen.draw(SCREEN)

    Cursor.draw(SCREEN)
    FpsCounter.draw(SCREEN)
    pg.display.update()

    DT = CLOCK.tick(120)

pg.quit()
