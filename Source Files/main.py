import pygame as pg
from pygame import Color, Rect, Surface, Mask, Vector2 as Vec2, surfarray
import numpy as np
from numpy import array as arr
from dataclasses import dataclass
import colorsys
import pyautogui as pyag

pg.init()
class WINDOW:
    x = None
    y = None
    width = 1280
    height = 720
    w = width
    h = height
    fps = 120
WINDOW.w = 1280
WINDOW.h = 720
SCREEN = pg.display.set_mode((WINDOW.w, WINDOW.h), flags=pg.DOUBLEBUF)
SCREEN.set_alpha(None)
CLOCK = pg.time.Clock()
mouse = pg.mouse
mouse.pos = mouse.get_pos()
pg.mouse.set_visible(False)
mouse.rect = Rect(0, 0, 1, 1)
mouse.mask = pg.Mask(size=mouse.rect.size, fill=True)
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

def hsv_to_rgb(H, S, V):
    return arr((colorsys.hsv_to_rgb(H / 360, S / 100, V / 100))) * 255

def masks_collide(object1, object2, offset=(0, 0)):
    return bool(object1.mask.overlap(object2.mask, (
    object2.rect.x - object1.rect.x + offset[1], object2.rect.y - object1.rect.y + offset[1])))

########################################################################################################################
###############  CONSTANTS   #################################################################################
########################################################################################################################
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
        return arr(((0, self.size[1]),
                    (self.size[0] / 2, 0),
                    (self.size[0], self.size[1]),
                    (0, self.size[1])))

    def _REGULAR_PENTAGON(self):
        vertices = arr((
            (0.5, 0),
            (0, 0.37918),
            (0.190984, 1),
            (0.809016, 1),
            (1, 0.37918)
        ))
        vertices *= arr((self.size[0], self.size[1]))
        return vertices

    def _STAR(self):
        vertices = arr((
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
        vertices *= arr((self.size[0], self.size[1]))
        return vertices

    def _HEXAGON(self):
        vertices = arr((
            (0.5, 0),
            (0, 0.25),
            (0, 0.75),
            (0.5, 1.00),
            (1, 0.75),
            (1, 0.25)
        ))
        vertices *= arr((self.size[0], self.size[1]))
        return vertices

@dataclass
class FONTS:
    default = "bahnschrift"

@dataclass
class COLORS:
    BLACK = Color("BLACK")
    WHITE = Color("WHITE")
    COLORKEY = Color(1, 1, 1)
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)

@dataclass
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

@dataclass
class MOUSE_STATES:
    IDLE = 'NOT_DRAGGING'
    DRAGGING = 'DRAGGING'
    SHIFT = False

########################################################################################################################
###############  GLOBALS   #################################################################################
########################################################################################################################
class TSD: # Temporary Shape Data
    SHAPE = None
    COLOR = Color((100, 100, 100))
    START = (0, 0)
    END = (0, 0)
    WIDTH = 0
    HEIGHT = 0
    SIZE = (0, 0)
    ACTION_TYPE = ACTION_TYPES.RECTANGLE
    MOUSE_ACTION = MOUSE_STATES.IDLE

class GLOBALS:
    GRID_SIZE = 0
    PAUSED = False

class FpsCounter:
    def __init__(self, color, text_height):
        self.text = 'NULL'
        self.color = Color(color)
        self.font = pg.font.SysFont(FONTS.default, text_height)
        self.surf = self.font.render(self.text, True, self.color)

    def draw(self, display):
        self.text = str(int(CLOCK.get_fps()))
        self.surf = self.font.render(self.text, True, self.color)
        display.blit(self.surf, self.surf.get_rect(topright=(WINDOW.w, 0)))

class Grid():
    def __init__(self, step_x, step_y, color=Color(64, 64, 64), width=1):
        self.surf = Surface((WINDOW.w, WINDOW.h))
        self.surf.set_colorkey(COLORS.COLORKEY)
        self.surf.fill(self.surf.get_colorkey())
        if step_x > 0:
            for x in range(0, WINDOW.w + 1, step_x):
                pg.draw.line(self.surf, color, (x, 0), (x, WINDOW.h), width=width)
        if step_y > 0:
            for y in range(0, WINDOW.h + 1, step_y):
                pg.draw.line(self.surf, color, (0, y), (WINDOW.w, y), width=width)

    def draw(self, display, special_flags=0):
        display.blit(self.surf, (0, 0), special_flags=special_flags)

########################################################################################################################
###############  CREATING NEW SHAPES   #################################################################################
########################################################################################################################
class Shape(pg.sprite.Sprite):
    def __init__(self, pos, size, shape):
        pg.sprite.Sprite.__init__(self)
        self.polygons = None
        self.shape = shape
        self.shape_color = Color(128, 128, 128)
        self.image = Surface(size)
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
        self.color = Color(30, 31, 82)
        self.image = Surface(size)
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
def startShape():
    if any(TSD.ACTION_TYPE == action_type for action_type in ACTION_TYPES.SHAPES):
        TSD.MOUSE_ACTION = MOUSE_STATES.DRAGGING
        TSD.START = arr(tuple(roundNumsToNearest(mouse.rect.topleft, GLOBALS.GRID_SIZE)))
        TSD.SHAPE = Shape(TSD.START, TSD.SIZE, TSD.ACTION_TYPE)
        shapes_group.add(TSD.SHAPE)
        TSD.COLOR = Color(219, 55, 172)
    if TSD.ACTION_TYPE == ACTION_TYPES.DELETE:
        TSD.MOUSE_ACTION = MOUSE_STATES.DRAGGING
        TSD.START = arr(tuple(mouse.rect.topleft))
        TSD.SHAPE = DeleteBox(TSD.START, TSD.SIZE)
        shapes_group.add(TSD.SHAPE)
def drawShape(step_size=0, shift_ratio=1 / 1):
    TSD.SHAPE.rect.topleft = TSD.START
    TSD.END = arr(tuple(roundNumsToNearest(mouse.rect.topleft, step_size)))
    TSD.WIDTH = (TSD.END[0] - TSD.START[0])
    TSD.HEIGHT = (TSD.END[1] - TSD.START[1])
    if not MOUSE_STATES.SHIFT:
        TSD.SIZE = np.absolute(arr([TSD.WIDTH, TSD.HEIGHT]))
    else:
        # Method 1
        # temp_shape_norm_half = roundNumToNearest(
        #     np.linalg.norm(arr([TSD.WIDTH, TSD.HEIGHT])) / 2, step_size)
        # TSD.SIZE = np.absolute(
        #     arr([roundNumToNearest(temp_shape_norm_half, step_size), temp_shape_norm_half]))

        # Method 2
        if TSD.WIDTH > TSD.HEIGHT:
            TSD.SIZE = arr((TSD.HEIGHT, TSD.HEIGHT))
        else:
            TSD.SIZE = arr((TSD.WIDTH, TSD.WIDTH))

        TSD.SIZE[0] *= shift_ratio
        np.abs(TSD.SIZE, TSD.SIZE)
    TSD.SHAPE.rect.size = TSD.SIZE
    TSD.SHAPE.shape_color = TSD.COLOR
    if TSD.WIDTH < 0 and TSD.HEIGHT < 0:
        TSD.SHAPE.resize_data(True, True)
    elif TSD.WIDTH < 0:
        TSD.SHAPE.resize_data(True, False)
    elif TSD.HEIGHT < 0:
        TSD.SHAPE.resize_data(False, True)
    else:
        TSD.SHAPE.resize_data(False, False)
def endShape():
    if TSD.MOUSE_ACTION == MOUSE_STATES.DRAGGING:
        if any(TSD.ACTION_TYPE == action_type for action_type in ACTION_TYPES.SHAPES):
            TSD.COLOR = Color(100, 100, 100)
            drawShape(GLOBALS.GRID_SIZE,
                      TSD.SHIFT_RATIO)
        if TSD.ACTION_TYPE == ACTION_TYPES.DELETE:
            for shape in shapes_group:
                if shape != TSD.SHAPE:
                    if masks_collide(shape, TSD.SHAPE) or masks_collide(shape, mouse):
                        shapes_group.remove(shape)
            shapes_group.remove(TSD.SHAPE)
        TSD.MOUSE_ACTION = MOUSE_STATES.IDLE
        TSD.START = TSD.END = TSD.SIZE = (0, 0)
        TSD.WIDTH = TSD.HEIGHT = 0
def cancelShape():
    if not GLOBALS.PAUSED:
        if TSD.MOUSE_ACTION == MOUSE_STATES.DRAGGING:
            TSD.MOUSE_ACTION = MOUSE_STATES.IDLE
            shapes_group.remove(TSD.SHAPE)


def scroll_through_action_types(event):
    inc = 0
    if e.precise_y > 0:
        inc = 1
    if e.precise_y < 0:
        inc = -1
    index = ACTION_TYPES.ACTION_TYPES.index(TSD.ACTION_TYPE) - inc
    try:
        TSD.ACTION_TYPE = ACTION_TYPES.ACTION_TYPES[index]
    except IndexError:
        TSD.ACTION_TYPE = ACTION_TYPES.ACTION_TYPES[0]
    hotbar.changeAction()


class ShapeButton():
    def __init__(self, rect, action_type, bg_color, border_color, border_width, shape_color, shape_scale, ):
        self.rect = Rect(rect)
        self.surf = Surface(self.rect.size)
        self.bg_color = bg_color
        self.surf.fill(self.bg_color)
        self.border_color = border_color
        self.border_width = border_width
        self.shape_color = shape_color

        self.action_type = action_type
        self.shape_scale = shape_scale
        self.shape_image = pg.transform.scale_by(self.surf, self.shape_scale)
        self.shape_image.set_colorkey((1, 1, 1));
        self.shape_image.fill(self.shape_image.get_colorkey())
        self.shape_rect = self.shape_image.get_rect(center=Vec2(self.rect.size) / 2)
        self.polygons = POLYGONS(Vec2(self.rect.size) * self.shape_scale, self.action_type)
        self.create_shape()

        self.mask = pg.mask.from_surface(self.surf)

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

    def mouse_hovering(self):
        return bool(masks_collide(self, mouse))

    def draw(self, display, special_flags=0):
        self.surf.blit(self.shape_image, self.shape_rect)
        pg.draw.rect(self.surf, self.border_color, self.surf.get_rect(), width=self.border_width)
        display.blit(self.surf, self.rect, special_flags=special_flags)
        return self
class TextButton():
    def __init__(self, rect, action_type, text, text_height, bg_color, border_color, border_width):
        self.action_type = action_type
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.rect = Rect(rect)
        self.surf = Surface(self.rect.size)
        self.surf.fill(self.bg_color)
        font = pg.font.SysFont(FONTS.default, text_height)
        self.text_surf = font.render(text, True, Color('WHITE'))
        self.text_rect = self.text_surf.get_rect(center=Vec2(self.rect.size) / 2)

        self.mask = pg.mask.from_surface(self.surf)

    def mouse_hovering(self):
        return bool(masks_collide(self, mouse))

    def draw(self, display):
        self.surf.blit(self.text_surf, self.text_rect)
        pg.draw.rect(self.surf, self.border_color, self.surf.get_rect(), width=self.border_width)
        display.blit(self.surf, self.rect)
        return self
class Hotbar:
    def __init__(self, num_buttons, button_size, padding, background_color, border_color, border_width):
        self.button_bg_color = Color(background_color)
        self.button_bd_color = Color(border_color)
        self.border_width = border_width

        self.surf = Surface((num_buttons * button_size[0] + num_buttons * padding, button_size[1]))
        self.rect = self.surf.get_rect(topleft=(10, 10))
        self.surf.set_colorkey((1, 1, 1));
        self.surf.fill(self.surf.get_colorkey())

        self.button_poses = [(x + off * padding, 0) for off, x in
                             enumerate(range(0, button_size[0] * num_buttons, button_size[0]))]
        self.buttons = []
        for pos, action_type in zip(self.button_poses[0:num_buttons - 1], ACTION_TYPES.SHAPES):
            self.buttons.append(
                ShapeButton((pos, button_size), action_type, self.button_bg_color,
                            self.button_bd_color, self.border_width, COLORS.BLUE,
                            0.6))
        for pos, (action_type, text) in zip([self.button_poses[num_buttons - 1]], {ACTION_TYPES.DELETE: 'DEL'}.items()):
            self.buttons.append(
                TextButton((pos, button_size), action_type, text, 16,
                           self.button_bg_color, self.button_bd_color, self.border_width))

        self.changeAction()

    def draw(self, display):
        display.blit(self.surf, self.rect)
        return self

    def changeAction(self, event=None):
        try:
            match event.type:
                case pg.KEYDOWN | pg.KEYUP:
                    match event.key:
                        case pg.K_1:
                            TSD.ACTION_TYPE = ACTION_TYPES.RECTANGLE
                        case pg.K_2:
                            TSD.ACTION_TYPE = ACTION_TYPES.CIRCLE
                        case pg.K_3:
                            TSD.ACTION_TYPE = ACTION_TYPES.TRIANGLE
                        case pg.K_4:
                            TSD.ACTION_TYPE = ACTION_TYPES.PENTAGON
                        case pg.K_5:
                            TSD.ACTION_TYPE = ACTION_TYPES.STAR
                        case pg.K_6:
                            TSD.ACTION_TYPE = ACTION_TYPES.HEXAGON
                        case pg.K_d:
                            TSD.ACTION_TYPE = ACTION_TYPES.DELETE
                case pg.MOUSEBUTTONDOWN | pg.MOUSEBUTTONUP:
                    if not masks_collide(mouse, self):
                        return
                    for button in self.buttons:
                        if not masks_collide(mouse, button, (10, 10)):
                            continue
                        TSD.ACTION_TYPE = button.action_type
                case pg.MOUSEWHEEL:
                    increment = 1 if e.precise_y > 0 else -1
                    index = ACTION_TYPES.ACTION_TYPES.index(TSD.ACTION_TYPE) - increment
                    TSD.ACTION_TYPE = ACTION_TYPES.ACTION_TYPES[index]
        except:
            pass

        for button in self.buttons:
            if not TSD.ACTION_TYPE == button.action_type:
                bg_color = button.bg_color
            else:
                bg_color = button.bg_color + Color(30, 30, 60)
            button.surf.fill(bg_color)

            button.draw(self.surf)
        self.mask = pg.mask.from_surface(self.surf)

        return self

class Slider():
    class PD:
        idle = {'bg': Color('WHITE'), 'bd': Color('WHITE')}
        active = {'bg': Color('BLACK'), 'bd': Color('WHITE')}
        current = {'bg': idle['bg'], 'bd': idle['bd']}

    def __init__(self, min, max, initial, rect, texture: Surface,
                 pick_size=(20, 20), border_color=Color(64, 64, 64), border_thickness=5, pick_border_thickness=5):
        self.mouse_dragging = False
        self.min = min
        self.max = max
        self.value = initial
        self.fraction = self.value/self.max

        self.rect = Rect(rect)
        self.surf = Surface(self.rect.size)

        self.pick = Surface((pick_size[0], pick_size[1]))
        self.pick.set_colorkey(Color(1, 1, 1));
        self.pick.fill(self.pick.get_colorkey())
        self.pick_rect = self.pick.get_rect(center=(self.rect.w*self.fraction + pick_size[0] / 2, self.rect.h))
        self.pick_border_thickness = pick_border_thickness
        pg.draw.polygon(self.pick, self.PD.current['bg'], POLYGONS(self.pick.get_size()).triangle)
        pg.draw.polygon(self.pick, self.PD.current['bg'], POLYGONS(self.pick.get_size()).triangle + arr((0, -1)),
                        width=self.pick_border_thickness)

        # Create bar
        self.texture = texture
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.border_rect = Rect(self.pick_rect.w / 2, 0, *self.rect.size).inflate(self.border_thickness*2, 0)
        self.bar_rect = Rect(rect)
        self.bar = Surface(self.bar_rect.size)
        self.bar.set_colorkey(Color(1, 1, 1));
        self.bar.fill(self.bar.get_colorkey())
        self.bar.blit(pg.transform.scale(texture, self.bar_rect.size), (0, 0))


        self.rect = Rect((self.bar_rect.topleft),
                            (self.bar_rect.w + self.pick_rect.w,
                             self.bar_rect.h + self.pick.get_height() / 3 + self.border_thickness))
        self.surf = Surface(self.rect.size)
        self.surf.set_colorkey(Color(1, 1, 1));
        self.surf.fill(self.surf.get_colorkey())

        self.update()

    def draw(self, display):
        if self.mouse_hovering() or self.mouse_dragging:
            self.PD.current['bg'] = self.PD.active['bg']
            self.PD.current['bd'] = self.PD.active['bd']
        else:
            self.PD.current['bg'] = self.PD.idle['bg']
            self.PD.current['bd'] = self.PD.idle['bd']

        self.update(cursor)

        self.surf.fill(self.surf.get_colorkey())
        self.surf.blit(self.bar, (self.pick_rect.w / 2, 0))
        pg.draw.rect(self.surf, self.border_color, self.border_rect, width=self.border_thickness)
        self.surf.blit(self.pick, self.pick_rect.topleft)
        display.blit(self.surf, self.rect)
        return self
    def startDragging(self, cursor):
        self.mouse_dragging = True
        cursor.hide()
    def stopDragging(self, cursor):
        self.mouse_dragging = False
        cursor.show()

    def get(self):
        return self.value

    def mouse_hovering(self):
        return masks_collide(self, mouse)

    def update(self, cursor=None):
        if self.mouse_dragging:
            if cursor:
                if cursor.visible and self.mouse_hovering():
                    cursor.hide()
                elif not cursor.visible and not self.mouse_hovering():
                    cursor.show()
            half_pick_width = self.pick_rect.w / 2
            if mouse.rect.x < self.rect.x + half_pick_width:
                self.fraction = 0
                self.pick_rect.centerx = half_pick_width
            elif mouse.rect.x > self.rect.x + self.bar_rect.width + half_pick_width:
                self.fraction = 1
                self.pick_rect.centerx = self.rect.width - half_pick_width
            else:
                self.fraction = ((mouse.rect.x) - self.rect.x - half_pick_width) / (self.bar_rect.width)
                self.pick_rect.centerx = mouse.rect.x - self.rect.x

            self.PD.current['bg'] = self.PD.active['bg']
            self.PD.current['bd'] = self.PD.active['bd']

        self.value = self.fraction * (self.max - self.min) + self.min

        self.pick.fill(self.pick.get_colorkey())
        pg.draw.polygon(self.pick, self.PD.current['bd'], POLYGONS(self.pick_rect.size).triangle)
        pick_border_ratio_width =  (self.pick_rect.w - 2 * self.pick_border_thickness) / self.pick_rect.w
        pick_border_ratio_height =  (self.pick_rect.h - 2 * self.pick_border_thickness) / self.pick_rect.h
        pg.draw.polygon(self.pick, self.PD.current['bg'],
                        POLYGONS((arr(self.pick_rect.size) * arr((pick_border_ratio_width, pick_border_ratio_height)))).triangle +
                        arr((self.pick_rect.w, self.pick_rect.h)) / 2 - arr((self.pick_rect.w, self.pick_rect.h)) *
                        arr((pick_border_ratio_width, pick_border_ratio_height)) / 2)

        self.bar.blit(pg.transform.scale(self.texture, self.bar_rect.size), (0, 0))

        self.mask = pg.mask.from_surface(self.surf)



class TEXTURES:
    def hue_gradient(width, height, s, v):
        surf = Surface((width, height))
        pixels = surfarray.array3d(surf)
        for x in range(surf.get_width()):
            pixels[x, :] = hsv_to_rgb(360 * (x / surf.get_width()), s, v)
        return surfarray.make_surface(pixels)

    def saturation_gradient(width, height, h, v):
        surf = Surface((width, height))
        pixels = surfarray.array3d(surf)
        for x in range(surf.get_width()):
            pixels[x, :] = hsv_to_rgb(h, 100 * x / surf.get_width(), v)
        return surfarray.make_surface(pixels)

    def value_gradient(width, height, h, s):
        surf = Surface((width, height))
        pixels = surfarray.array3d(surf)
        for x in range(surf.get_width()):
            pixels[x, :] = hsv_to_rgb(h, s, 100 * x / surf.get_width())
        return surfarray.make_surface(pixels)
class ColorSelector:
    def __init__(self, rect, slider_height=50, padding=10, pick_size=(20, 20)):
        self.slider_height = slider_height
        self.slider_positions = tuple((0, y + offset * padding) for offset, y in enumerate(range(0, 3*slider_height, self.slider_height)))
        self.rect = Rect(*rect[0:2], rect[2], 3 * slider_height + 3 * padding + pick_size[1])
        self.surf = Surface(self.rect.size)
        self.surf.set_colorkey(Color(1,1,1))
        self.hue_slider = Slider(min=0, max=360, initial=0, rect=(*self.slider_positions[0], self.rect.w, slider_height),
                                 texture=TEXTURES.hue_gradient(self.rect.w, slider_height, s=100, v=100),
                                 border_color=Color(64, 64, 64), pick_size=pick_size, pick_border_thickness=3)
        self.saturation_slider = Slider(min=0, max=100, initial=100, rect=(*self.slider_positions[1], self.rect.w, slider_height),
                                        texture=TEXTURES.saturation_gradient(self.rect.w, slider_height, h=0, v=100),
                                        border_color=Color(64, 64, 64), pick_size=pick_size, pick_border_thickness=3)
        self.value_slider = Slider(min=0, max=100, initial=100, rect=(*self.slider_positions[2], self.rect.w, slider_height),
                                   texture=TEXTURES.value_gradient(self.rect.w, slider_height, h=0, s=100),
                                   border_color=Color(64, 64, 64), pick_size=pick_size, pick_border_thickness=3)
        self.sliders = (self.hue_slider, self.saturation_slider, self.value_slider)
        for slider in self.sliders:
            slider.bar_rect.inflate(-1, 0)
        self.hue = self.saturation_slider.get()
        self.saturation = self.saturation_slider.get()
        self.value = self.value_slider.get()

        self.rect = self.rect.inflate(pick_size[0]+1, 0)
        self.surf = pg.transform.scale(self.surf, self.rect.size)
    def startDraggingSelectors(self, cursor):
        for slider in self.sliders:
            if slider.mouse_hovering():
                slider.startDragging(cursor)

    def stopDraggingSelectors(self, cursor):
        for slider in self.sliders:
            slider.stopDragging(cursor)

    def get(self):
        return Color(hsv_to_rgb(self.hue, self.saturation, self.value))
    def update(self):
        self.hue = self.hue_slider.get()
        self.saturation = self.saturation_slider.get()
        self.value = self.value_slider.get()

        self.hue_slider.texture = TEXTURES.hue_gradient(self.rect.w, self.slider_height, s=self.saturation, v=self.value)
        self.saturation_slider.texture = TEXTURES.saturation_gradient(self.rect.w, self.slider_height, h=self.hue, v=self.value)
        self.value_slider.texture = TEXTURES.value_gradient(self.rect.w, self.slider_height, h=self.hue, s=self.saturation)

        self.surf.fill(self.surf.get_colorkey())
        self.mask = pg.mask.from_surface(self.surf)
    def draw(self, display):
        self.update()
        for slider in self.sliders:
            slider.update(cursor)
            slider.draw(self.surf)
            display.blit(slider.surf, slider.rect)
        display.blit(self.surf, self.rect)
"""
# Hue slider
hue_slider = Slider(0, 360, (1070, 50, 200, 25), TEXTURES.hue_gradient(200, 25, s=100, v=100), Color(64, 64, 64), (20, 20))
hue_slider.rect.x -= hue_slider.pick_rect.w

# Saturation slider
sat_slider = Slider(0, 100, (1070, 85, 200, 25), TEXTURES.saturation_gradient(200, 25, h=0, v=100), Color(64, 64, 64), border_color(20, 20))
sat_slider.rect.x -= sat_slider.pick_rect.w

val_slider = Slider(0, 100, (1070, 120, 200, 25), TEXTURES.value_gradient(200, 25, h=0, s=100), Color(64, 64, 64), (20, 20))
val_slider.rect.x -= val_slider.pick_rect.w
"""
class Cursor:
    def __init__(self):
        self.visible: bool = True
        self.rect: Rect = None
        self.mask: Mask = None
        self.color: Color = COLORS.GREEN
        self.surf: Surface = Surface((6, 6))
        self.surf.set_colorkey(Color(1, 1, 1))
        self.update()

    def hide(self):
        self.visible = False
        return self
    def show(self):
        self.visible = True
        return self
    def update(self):
        self.surf.fill(self.surf.get_colorkey())
        pg.draw.rect(self.surf, self.color, ((2, 0), (2, 6)))
        pg.draw.rect(self.surf, self.color, ((0, 2), (6, 2)))
        self.mask = pg.mask.from_surface(self.surf)
        return self
    def draw(self, display):
        if self.visible:
            self.rect = self.surf.get_rect(center=(mouse.rect.topleft))
            display.blit(self.surf, self.rect)
        return self


class ClickTextButton():
    def __init__(self, rect, text, text_height, text_color, bg_color, border_color):
        self.rect = Rect(rect)
        self.surf = Surface(self.rect.size)
        self.bg_color = Color(bg_color)
        self.surf.fill(self.bg_color)
        self.border_color = border_color
        self.mask = pg.mask.from_surface(self.surf)
        self.text_color = text_color
        font = pg.font.SysFont(FONTS.default, text_height)
        self.text_surf = font.render(text, True, Color(text_color))
        self.text_rect = self.text_surf.get_rect(center=Vec2(self.rect.size) / 2)

    def get_mouse_hovering(self):
        return masks_collide(self, mouse)

    def update(self):
        if self.get_mouse_hovering():
            bg_color = self.bg_color - Color(50, 50, 50)
        else:
            bg_color = self.bg_color
        self.surf.fill(bg_color)

    def draw(self, display, special_flags=0):
        self.surf.blit(self.text_surf, self.text_rect)
        pg.draw.rect(self.surf, self.border_color, self.surf.get_rect(), width=5)
        display.blit(self.surf, self.rect, special_flags=special_flags)


class PauseScreen:
    def __init__(self):
        self.surf = Surface((WINDOW.w, WINDOW.h))
        self.screen_rect = self.surf.get_rect()
        self.surf.set_alpha(128)

        self.background = Surface(self.surf.get_size())
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
            self.buttons[key].rect = self.buttons[key].surf.get_rect(
                center=self.buttons[key].rect.topleft)

        self.mask = pg.mask.from_surface(self.surf)

    def draw(self, display, special_flags=0):
        self.surf.blit(self.background, self.screen_rect, special_flags=0)
        display.blit(self.surf, (0, 0), special_flags=special_flags)
        for button in self.buttons.values():
            button.update()
            button.draw(display)

    def switch(self):
        if not GLOBALS.PAUSED:
            GLOBALS.PAUSED = True
        else:
            GLOBALS.PAUSED = False

    def input(self):
        global run
        if self.buttons['res'].get_mouse_hovering():
            GLOBALS.PAUSED = False
        if self.buttons['clear'].get_mouse_hovering():
            shapes_group.empty()
            GLOBALS.PAUSED = False
        if self.buttons['exit'].get_mouse_hovering():
            run = False

colorselector = ColorSelector((700, 100, 200, None), 20, 10, (16, 16))
fps_counter = FpsCounter(COLORS.WHITE, 22)
grid = Grid(GLOBALS.GRID_SIZE, GLOBALS.GRID_SIZE)
cursor = Cursor()
hotbar = Hotbar(7, (50, 50), 5, Color(70, 70, 70), Color(40, 40, 40), 3)
pause_screen = PauseScreen()

shapes_group = pg.sprite.Group()
ui_group = [hotbar]

GLOBALS.PAUSED = False

run = True
while run:
    mouse.rect.topleft = mouse.pos = mouse.get_pos()
    SCREEN.fill(COLORS.BLACK)
    ####################################################################################################################
    #         POLL FOR EVENTS        #
    ####################################################################################################################
    keys = pg.key.get_pressed()
    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False
        #######################################################
        #   KEYBOARD   #
        #######################################################
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                pause_screen.switch()
                endShape()
            if not GLOBALS.PAUSED:
                hotbar.changeAction(e)
            if e.key == pg.K_r:
                shapes_group.empty()
            if e.key == pg.K_LSHIFT:
                MOUSE_STATES.SHIFT = True
        if e.type == pg.KEYUP:
            if e.key == pg.K_LSHIFT:
                MOUSE_STATES.SHIFT = False
        #######################################################
        # MOUSE BUTTON #
        #######################################################
        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1:
                if not GLOBALS.PAUSED:
                    if not any(masks_collide(mouse, object) for object in
                               ui_group):
                        startShape()

                    colorselector.startDraggingSelectors(cursor)

                    hotbar.changeAction(e)

                if GLOBALS.PAUSED:
                    pause_screen.input()
            if e.button == 3:
                if not GLOBALS.PAUSED:
                    cancelShape()
        #######################################################
        if e.type == pg.MOUSEBUTTONUP:
            if e.button == 1:
                if not GLOBALS.PAUSED:
                    endShape()
                    colorselector.stopDraggingSelectors(cursor)
        #######################################################
        # SCROLL WHEEL #
        #######################################################
        if e.type == pg.MOUSEWHEEL:
            scroll_through_action_types(e)

    ####################################################################################################################
    #        RENDER GAME HERE        #
    ####################################################################################################################
    for shape in shapes_group:
        shape.draw(SCREEN)
        if shape.mask.overlap(mouse.mask, (mouse.rect.x - shape.rect.x, mouse.rect.y - shape.rect.y)):
            cursor.color = (COLORS.GREEN)
        else:
            cursor.color = (COLORS.GREEN)

    if not GLOBALS.PAUSED:
        grid.draw(SCREEN)
        if TSD.MOUSE_ACTION == MOUSE_STATES.DRAGGING:
            TSD.COLOR = Color(219, 55, 172)
            if any(TSD.ACTION_TYPE == action_type for action_type in ACTION_TYPES.SHAPES):
                if TSD.ACTION_TYPE == ACTION_TYPES.TRIANGLE:
                    TSD.SHIFT_RATIO = 4 / 3
                elif TSD.ACTION_TYPE == ACTION_TYPES.PENTAGON or TSD.ACTION_TYPE == ACTION_TYPES.STAR:
                    TSD.SHIFT_RATIO = 0.951056516295 / 0.904508497185
                else:
                    TSD.SHIFT_RATIO = 1 / 1
                drawShape(GLOBALS.GRID_SIZE, TSD.SHIFT_RATIO)
            elif TSD.ACTION_TYPE == ACTION_TYPES.DELETE:
                drawShape()

        for object in ui_group:
            object.draw(SCREEN)

        colorselector.draw(SCREEN)
    elif GLOBALS.PAUSED:
        pause_screen.draw(SCREEN)

    cursor.draw(SCREEN)
    fps_counter.draw(SCREEN)

    ####################################################################################################################
    #        RENDER GAME HERE        #
    ####################################################################################################################
    pg.display.update()
    DT = CLOCK.tick(WINDOW.fps)

pg.quit()
