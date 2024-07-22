import pygame as pg
from pygame import Color, Rect, Surface, Mask, Vector2 as Vec2, surfarray, gfxdraw
import numpy as np
from numpy import array as arr
from dataclasses import dataclass
import colorsys
from tkinter import filedialog

pg.init()


class WINDOW:
    x = None
    y = None
    # width, height = 1280, 720
    width, height = 1920, 1080
    size = (width, height)
    fps = 360


pg.display.set_icon(pg.image.load("misc/icon.ico"))
SCREEN = pg.display.set_mode(WINDOW.size, flags=pg.DOUBLEBUF)
SCREEN.set_alpha(None)
CLOCK = pg.time.Clock()
mouse = pg.mouse
pg.mouse.set_visible(False)
DT = 0

fonts = {
    'default': "bahnschrift"
}

DRAG_COLOR = Color(219, 55, 172)
COLORKEY = Color(1, 127, 255)
BLACK = Color('BLACK')
WHITE = Color('WHITE')
RED = Color('RED')
GREEN = Color('GREEN')
BLUE = Color('BLUE')

actions = {
    'delete': 1,
    'rectangle': 100,
    'circle': 101,
    'triangle': 102,
    'regular_pentagon': 103,
    'pentagram': 104,
    'regular_hexagon': 105
}
tools = []
shapes = []
for type_id in actions.values():
    if type_id < 100:
        tools.append(type_id)
    elif type_id > 99:
        shapes.append(type_id)
list_types = shapes + tools


def save_surface_with_filedialog(surface):
    filepath = filedialog.asksaveasfilename(
        title="Save Canvas",
        filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpeg"),
                   ("BMP Files", "*.bmp"), ("TGA Files", "*.tga")],
        defaultextension=".png"
    )
    pg.image.save(surface, filepath)


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


def round_numbers_to_nearest(values, round_to):
    res = []
    for value in values:
        value = round(value)
        try:
            n = value % round_to
            if n >= round_to / 2:
                res.append(value + (round_to - n))
            else:
                res.append(value - n)
        except ZeroDivisionError:
            res.append(value)
    return Vec2(res)


def hsv_to_rgb(H, S, V):
    return arr((colorsys.hsv_to_rgb(H / 360, S / 100, V / 100))) * 255


def masks_collide(object1, object2, offset=(0, 0)):
    return bool(object1.mask.overlap(object2.mask, (
        object2.rect.x - object1.rect.x - offset[0], object2.rect.y - object1.rect.y - offset[1])))


def any_of(lefthand, *righthands) -> bool:
    """
    Compares the lefthand value to each righthand and returns if there are any matches

    Parameters:
      lefthand (Any): value to compare to each righthand.
      righthands (Any): values to compare to the lefthand.

    Returns:
      bool: Whether or not the lefthand matches any of the righthands
    """
    return any(lefthand == s for s in righthands)


########################################################################################################################
###############  CONSTANTS   #################################################################################
########################################################################################################################
@dataclass
class POLYGONS:
    def __init__(self, action, size=None):
        self.size = arr(size)
        if action == actions['rectangle']:
            self.shape, self.ratio = self._RECTANGLE(), 1
        elif action == actions['circle']:
            self.shape, self.ratio = self._CIRCLE(), 1
        elif action == actions['triangle']:
            self.shape, self.ratio = self._TRIANGLE(), 1.33333333333
        elif action == actions['regular_pentagon']:
            self.shape, self.ratio = self._REGULAR_PENTAGON(), 1.05146222424
        elif action == actions['pentagram']:
            self.shape, self.ratio = self._STAR(), 1.05146222424
        elif action == actions['regular_hexagon']:
            self.shape, self.ratio = self._REGULAR_HEXAGON(), 0.86602543256
        else:
            self.shape = arr((0, 0) for _ in range(3))
            self.ratio = 1 / 1
        try:
            self.shape *= self.size
        except:
            pass

    def _RECTANGLE(self):
        vertices = arr((
            (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)
        ))
        return vertices

    def _CIRCLE(self):
        vertices = arr((
            [1.0, 0.5],
            [0.999923825263977, 0.508726179599762],
            [0.9996954202651978, 0.5174497365951538],
            [0.9993147850036621, 0.5261679887771606],
            [0.9987820386886597, 0.5348782539367676],
            [0.9980973601341248, 0.5435778498649597],
            [0.9972609281539917, 0.5522642135620117],
            [0.9962730407714844, 0.5609346628189087],
            [0.9951339960098267, 0.5695865750312805],
            [0.9938441514968872, 0.5782172083854675],
            [0.9924038648605347, 0.5868240594863892],
            [0.9908136129379272, 0.5954045057296753],
            [0.9890738129615784, 0.603955864906311],
            [0.987185001373291, 0.6124755144119263],
            [0.9851478338241577, 0.6209609508514404],
            [0.9829629063606262, 0.6294095516204834],
            [0.9806308746337891, 0.6378186941146851],
            [0.9781523942947388, 0.6461858749389648],
            [0.9755282402038574, 0.6545084714889526],
            [0.9727592468261719, 0.6627840995788574],
            [0.9698463082313538, 0.6710100769996643],
            [0.9667901992797852, 0.6791839599609375],
            [0.9635919332504272, 0.6873033046722412],
            [0.9602524042129517, 0.6953655481338501],
            [0.9567726850509644, 0.7033683061599731],
            [0.9531539082527161, 0.7113091349601746],
            [0.9493970274925232, 0.7191855907440186],
            [0.9455032348632812, 0.7269952297210693],
            [0.9414737820625305, 0.7347357869148254],
            [0.9373098611831665, 0.7424048185348511],
            [0.9330127239227295, 0.75],
            [0.9285836219787598, 0.757519006729126],
            [0.9240240454673767, 0.7649596333503723],
            [0.9193352460861206, 0.7723195552825928],
            [0.9145187735557556, 0.7795964479446411],
            [0.9095760583877563, 0.7867882251739502],
            [0.9045084714889526, 0.7938926219940186],
            [0.899317741394043, 0.8009074926376343],
            [0.8940054178237915, 0.8078307509422302],
            [0.8885729908943176, 0.8146601915359497],
            [0.8830221891403198, 0.8213938474655151],
            [0.8773548007011414, 0.8280295133590698],
            [0.8715723752975464, 0.834565281867981],
            [0.8656768798828125, 0.840999186038971],
            [0.8596699237823486, 0.8473291993141174],
            [0.8535534143447876, 0.8535534143447876],
            [0.8473291993141174, 0.8596699237823486],
            [0.840999186038971, 0.8656768798828125],
            [0.834565281867981, 0.8715723752975464],
            [0.8280295133590698, 0.8773548007011414],
            [0.8213938474655151, 0.8830221891403198],
            [0.8146601915359497, 0.8885729908943176],
            [0.8078307509422302, 0.8940054178237915],
            [0.8009074926376343, 0.899317741394043],
            [0.7938926219940186, 0.9045084714889526],
            [0.7867882251739502, 0.9095760583877563],
            [0.7795964479446411, 0.9145187735557556],
            [0.7723195552825928, 0.9193352460861206],
            [0.7649596333503723, 0.9240240454673767],
            [0.757519006729126, 0.9285836219787598],
            [0.75, 0.9330127239227295],
            [0.7424048185348511, 0.9373098611831665],
            [0.7347357869148254, 0.9414737820625305],
            [0.7269952297210693, 0.9455032348632812],
            [0.7191855907440186, 0.9493970274925232],
            [0.7113091349601746, 0.9531539082527161],
            [0.7033683061599731, 0.9567726850509644],
            [0.6953655481338501, 0.9602524042129517],
            [0.6873033046722412, 0.9635919332504272],
            [0.6791839599609375, 0.9667901992797852],
            [0.6710100769996643, 0.9698463082313538],
            [0.6627840995788574, 0.9727592468261719],
            [0.6545084714889526, 0.9755282402038574],
            [0.6461858749389648, 0.9781523942947388],
            [0.6378186941146851, 0.9806308746337891],
            [0.6294095516204834, 0.9829629063606262],
            [0.6209609508514404, 0.9851478338241577],
            [0.6124755144119263, 0.987185001373291],
            [0.603955864906311, 0.9890738129615784],
            [0.5954045057296753, 0.9908136129379272],
            [0.5868240594863892, 0.9924038648605347],
            [0.5782172083854675, 0.9938441514968872],
            [0.5695865750312805, 0.9951339960098267],
            [0.5609346628189087, 0.9962730407714844],
            [0.5522642135620117, 0.9972609281539917],
            [0.5435778498649597, 0.9980973601341248],
            [0.5348782539367676, 0.9987820386886597],
            [0.5261679887771606, 0.9993147850036621],
            [0.5174497365951538, 0.9996954202651978],
            [0.508726179599762, 0.999923825263977],
            [0.5, 1.0],
            [0.49127379059791565, 0.999923825263977],
            [0.4825502634048462, 0.9996954202651978],
            [0.47383201122283936, 0.9993147850036621],
            [0.4651217758655548, 0.9987820386886597],
            [0.4564221203327179, 0.9980973601341248],
            [0.4477357566356659, 0.9972609281539917],
            [0.4390653371810913, 0.9962730407714844],
            [0.43041345477104187, 0.9951339960098267],
            [0.4217827618122101, 0.9938441514968872],
            [0.41317591071128845, 0.9924038648605347],
            [0.4045954942703247, 0.9908136129379272],
            [0.39604416489601135, 0.9890738129615784],
            [0.38752448558807373, 0.987185001373291],
            [0.37903904914855957, 0.9851478338241577],
            [0.370590478181839, 0.9829629063606262],
            [0.36218130588531494, 0.9806308746337891],
            [0.35381415486335754, 0.9781523942947388],
            [0.345491498708725, 0.9755282402038574],
            [0.3372159004211426, 0.9727592468261719],
            [0.3289899230003357, 0.9698463082313538],
            [0.3208160400390625, 0.9667901992797852],
            [0.3126966953277588, 0.9635919332504272],
            [0.3046344518661499, 0.9602524042129517],
            [0.29663169384002686, 0.9567726850509644],
            [0.28869086503982544, 0.9531539082527161],
            [0.28081440925598145, 0.9493970274925232],
            [0.27300477027893066, 0.9455032348632812],
            [0.26526421308517456, 0.9414737820625305],
            [0.2575951814651489, 0.9373098611831665],
            [0.25, 0.9330127239227295],
            [0.24248096346855164, 0.9285836219787598],
            [0.23504036664962769, 0.9240240454673767],
            [0.22768047451972961, 0.9193352460861206],
            [0.2204035520553589, 0.9145187735557556],
            [0.2132117748260498, 0.9095760583877563],
            [0.20610737800598145, 0.9045084714889526],
            [0.19909247756004333, 0.899317741394043],
            [0.19216924905776978, 0.8940054178237915],
            [0.1853398084640503, 0.8885729908943176],
            [0.17860618233680725, 0.8830221891403198],
            [0.17197048664093018, 0.8773548007011414],
            [0.16543468832969666, 0.8715723752975464],
            [0.15900081396102905, 0.8656768798828125],
            [0.15267080068588257, 0.8596699237823486],
            [0.1464466154575348, 0.8535534143447876],
            [0.14033010601997375, 0.8473291993141174],
            [0.1343231499195099, 0.840999186038971],
            [0.12842759490013123, 0.834565281867981],
            [0.12264519929885864, 0.8280295133590698],
            [0.11697778105735779, 0.8213938474655151],
            [0.11142700910568237, 0.8146601915359497],
            [0.10599461197853088, 0.8078307509422302],
            [0.10068225860595703, 0.8009074926376343],
            [0.09549149870872498, 0.7938926219940186],
            [0.09042397141456604, 0.7867882251739502],
            [0.08548122644424438, 0.7795964479446411],
            [0.080664724111557, 0.7723195552825928],
            [0.07597595453262329, 0.7649596333503723],
            [0.07141634821891785, 0.757519006729126],
            [0.0669873058795929, 0.75],
            [0.0626901388168335, 0.7424048185348511],
            [0.05852621793746948, 0.7347357869148254],
            [0.05449673533439636, 0.7269952297210693],
            [0.05060297250747681, 0.7191855907440186],
            [0.046846091747283936, 0.7113091349601746],
            [0.04322728514671326, 0.7033683061599731],
            [0.03974756598472595, 0.6953655481338501],
            [0.036408066749572754, 0.6873033046722412],
            [0.033209800720214844, 0.6791839599609375],
            [0.03015369176864624, 0.6710100769996643],
            [0.027240723371505737, 0.6627840995788574],
            [0.02447172999382019, 0.6545084714889526],
            [0.021847635507583618, 0.6461858749389648],
            [0.019369155168533325, 0.6378186941146851],
            [0.01703709363937378, 0.6294095516204834],
            [0.014852136373519897, 0.6209609508514404],
            [0.012814968824386597, 0.6124755144119263],
            [0.01092618703842163, 0.603955864906311],
            [0.009186416864395142, 0.5954045057296753],
            [0.007596135139465332, 0.5868240594863892],
            [0.006155818700790405, 0.5782172083854675],
            [0.004865974187850952, 0.5695865750312805],
            [0.0037269294261932373, 0.5609346628189087],
            [0.002739042043685913, 0.5522642135620117],
            [0.0019026398658752441, 0.5435778498649597],
            [0.001217961311340332, 0.5348782539367676],
            [0.0006852447986602783, 0.5261679887771606],
            [0.0003045797348022461, 0.5174497365951538],
            [7.614493370056152e-05, 0.508726179599762],
            [0.0, 0.5],
            [7.614493370056152e-05, 0.49127379059791565],
            [0.0003045797348022461, 0.4825502634048462],
            [0.0006852447986602783, 0.47383201122283936],
            [0.001217961311340332, 0.4651217758655548],
            [0.0019026398658752441, 0.4564221203327179],
            [0.002739042043685913, 0.4477357566356659],
            [0.0037269294261932373, 0.4390653371810913],
            [0.004865974187850952, 0.43041345477104187],
            [0.006155818700790405, 0.4217827618122101],
            [0.007596135139465332, 0.41317591071128845],
            [0.009186416864395142, 0.4045954942703247],
            [0.01092618703842163, 0.39604416489601135],
            [0.012814968824386597, 0.38752448558807373],
            [0.014852136373519897, 0.37903904914855957],
            [0.01703709363937378, 0.370590478181839],
            [0.019369155168533325, 0.36218130588531494],
            [0.021847635507583618, 0.35381415486335754],
            [0.02447172999382019, 0.345491498708725],
            [0.027240723371505737, 0.3372159004211426],
            [0.03015369176864624, 0.3289899230003357],
            [0.033209800720214844, 0.3208160400390625],
            [0.036408066749572754, 0.3126966953277588],
            [0.03974756598472595, 0.3046344518661499],
            [0.04322728514671326, 0.29663169384002686],
            [0.046846091747283936, 0.28869086503982544],
            [0.05060297250747681, 0.28081440925598145],
            [0.05449673533439636, 0.27300477027893066],
            [0.05852621793746948, 0.26526421308517456],
            [0.0626901388168335, 0.2575951814651489],
            [0.0669873058795929, 0.25],
            [0.07141634821891785, 0.24248096346855164],
            [0.07597595453262329, 0.23504036664962769],
            [0.080664724111557, 0.22768047451972961],
            [0.08548122644424438, 0.2204035520553589],
            [0.09042397141456604, 0.2132117748260498],
            [0.09549149870872498, 0.20610737800598145],
            [0.10068225860595703, 0.19909247756004333],
            [0.10599461197853088, 0.19216924905776978],
            [0.11142700910568237, 0.1853398084640503],
            [0.11697778105735779, 0.17860618233680725],
            [0.12264519929885864, 0.17197048664093018],
            [0.12842759490013123, 0.16543468832969666],
            [0.1343231499195099, 0.15900081396102905],
            [0.14033010601997375, 0.15267080068588257],
            [0.1464466154575348, 0.1464466154575348],
            [0.15267080068588257, 0.14033010601997375],
            [0.15900081396102905, 0.1343231499195099],
            [0.16543468832969666, 0.12842759490013123],
            [0.17197048664093018, 0.12264519929885864],
            [0.17860618233680725, 0.11697778105735779],
            [0.1853398084640503, 0.11142700910568237],
            [0.19216924905776978, 0.10599461197853088],
            [0.19909247756004333, 0.10068225860595703],
            [0.20610737800598145, 0.09549149870872498],
            [0.2132117748260498, 0.09042397141456604],
            [0.2204035520553589, 0.08548122644424438],
            [0.22768047451972961, 0.080664724111557],
            [0.23504036664962769, 0.07597595453262329],
            [0.24248096346855164, 0.07141634821891785],
            [0.25, 0.0669873058795929],
            [0.2575951814651489, 0.0626901388168335],
            [0.26526421308517456, 0.05852621793746948],
            [0.27300477027893066, 0.05449673533439636],
            [0.28081440925598145, 0.05060297250747681],
            [0.28869086503982544, 0.046846091747283936],
            [0.29663169384002686, 0.04322728514671326],
            [0.3046344518661499, 0.03974756598472595],
            [0.3126966953277588, 0.036408066749572754],
            [0.3208160400390625, 0.033209800720214844],
            [0.3289899230003357, 0.03015369176864624],
            [0.3372159004211426, 0.027240723371505737],
            [0.345491498708725, 0.02447172999382019],
            [0.35381415486335754, 0.021847635507583618],
            [0.36218130588531494, 0.019369155168533325],
            [0.370590478181839, 0.01703709363937378],
            [0.37903904914855957, 0.014852136373519897],
            [0.38752448558807373, 0.012814968824386597],
            [0.39604416489601135, 0.01092618703842163],
            [0.4045954942703247, 0.009186416864395142],
            [0.41317591071128845, 0.007596135139465332],
            [0.4217827618122101, 0.006155818700790405],
            [0.43041345477104187, 0.004865974187850952],
            [0.4390653371810913, 0.0037269294261932373],
            [0.4477357566356659, 0.002739042043685913],
            [0.4564221203327179, 0.0019026398658752441],
            [0.4651217758655548, 0.001217961311340332],
            [0.47383201122283936, 0.0006852447986602783],
            [0.4825502634048462, 0.0003045797348022461],
            [0.49127379059791565, 7.614493370056152e-05],
            [0.5, 0.0],
            [0.508726179599762, 7.614493370056152e-05],
            [0.5174497365951538, 0.0003045797348022461],
            [0.5261679887771606, 0.0006852447986602783],
            [0.5348782539367676, 0.001217961311340332],
            [0.5435778498649597, 0.0019026398658752441],
            [0.5522642135620117, 0.002739042043685913],
            [0.5609346628189087, 0.0037269294261932373],
            [0.5695865750312805, 0.004865974187850952],
            [0.5782172083854675, 0.006155818700790405],
            [0.5868240594863892, 0.007596135139465332],
            [0.5954045057296753, 0.009186416864395142],
            [0.603955864906311, 0.01092618703842163],
            [0.6124755144119263, 0.012814968824386597],
            [0.6209609508514404, 0.014852136373519897],
            [0.6294095516204834, 0.01703709363937378],
            [0.6378186941146851, 0.019369155168533325],
            [0.6461858749389648, 0.021847635507583618],
            [0.6545084714889526, 0.02447172999382019],
            [0.6627840995788574, 0.027240723371505737],
            [0.6710100769996643, 0.03015369176864624],
            [0.6791839599609375, 0.033209800720214844],
            [0.6873033046722412, 0.036408066749572754],
            [0.6953655481338501, 0.03974756598472595],
            [0.7033683061599731, 0.04322728514671326],
            [0.7113091349601746, 0.046846091747283936],
            [0.7191855907440186, 0.05060297250747681],
            [0.7269952297210693, 0.05449673533439636],
            [0.7347357869148254, 0.05852621793746948],
            [0.7424048185348511, 0.0626901388168335],
            [0.75, 0.0669873058795929],
            [0.757519006729126, 0.07141634821891785],
            [0.7649596333503723, 0.07597595453262329],
            [0.7723195552825928, 0.080664724111557],
            [0.7795964479446411, 0.08548122644424438],
            [0.7867882251739502, 0.09042397141456604],
            [0.7938926219940186, 0.09549149870872498],
            [0.8009074926376343, 0.10068225860595703],
            [0.8078307509422302, 0.10599461197853088],
            [0.8146601915359497, 0.11142700910568237],
            [0.8213938474655151, 0.11697778105735779],
            [0.8280295133590698, 0.12264519929885864],
            [0.834565281867981, 0.12842759490013123],
            [0.840999186038971, 0.1343231499195099],
            [0.8473291993141174, 0.14033010601997375],
            [0.8535534143447876, 0.1464466154575348],
            [0.8596699237823486, 0.15267080068588257],
            [0.8656768798828125, 0.15900081396102905],
            [0.8715723752975464, 0.16543468832969666],
            [0.8773548007011414, 0.17197048664093018],
            [0.8830221891403198, 0.17860618233680725],
            [0.8885729908943176, 0.1853398084640503],
            [0.8940054178237915, 0.19216924905776978],
            [0.899317741394043, 0.19909247756004333],
            [0.9045084714889526, 0.20610737800598145],
            [0.9095760583877563, 0.2132117748260498],
            [0.9145187735557556, 0.2204035520553589],
            [0.9193352460861206, 0.22768047451972961],
            [0.9240240454673767, 0.23504036664962769],
            [0.9285836219787598, 0.24248096346855164],
            [0.9330127239227295, 0.25],
            [0.9373098611831665, 0.2575951814651489],
            [0.9414737820625305, 0.26526421308517456],
            [0.9455032348632812, 0.27300477027893066],
            [0.9493970274925232, 0.28081440925598145],
            [0.9531539082527161, 0.28869086503982544],
            [0.9567726850509644, 0.29663169384002686],
            [0.9602524042129517, 0.3046344518661499],
            [0.9635919332504272, 0.3126966953277588],
            [0.9667901992797852, 0.3208160400390625],
            [0.9698463082313538, 0.3289899230003357],
            [0.9727592468261719, 0.3372159004211426],
            [0.9755282402038574, 0.345491498708725],
            [0.9781523942947388, 0.35381415486335754],
            [0.9806308746337891, 0.36218130588531494],
            [0.9829629063606262, 0.370590478181839],
            [0.9851478338241577, 0.37903904914855957],
            [0.987185001373291, 0.38752448558807373],
            [0.9890738129615784, 0.39604416489601135],
            [0.9908136129379272, 0.4045954942703247],
            [0.9924038648605347, 0.41317591071128845],
            [0.9938441514968872, 0.4217827618122101],
            [0.9951339960098267, 0.43041345477104187],
            [0.9962730407714844, 0.4390653371810913],
            [0.9972609281539917, 0.4477357566356659],
            [0.9980973601341248, 0.4564221203327179],
            [0.9987820386886597, 0.4651217758655548],
            [0.9993147850036621, 0.47383201122283936],
            [0.9996954202651978, 0.4825502634048462],
            [0.999923825263977, 0.49127379059791565],
        ))

        return vertices

    def _TRIANGLE(self):
        return arr(((0, 1),
                    (0.5, 0),
                    (1, 1)))

    def _REGULAR_PENTAGON(self):
        vertices = arr((
            (0.5, 0),
            (0, 0.37918),
            (0.190984, 1),
            (0.809016, 1),
            (1, 0.37918)
        ))
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
        return vertices

    def _REGULAR_HEXAGON(self):
        vertices = arr((
            (0.5, 1.0), (0.0, 0.75), (0.0, 0.25), (0.5, 0.0), (1.0, 0.25), (1.0, 0.75)
        ))
        return vertices


mouse_idle = 'idle'
mouse_dragging = 'dragging'
holding_shift_key = False


########################################################################################################################
###############  GLOBALS   #################################################################################
########################################################################################################################
class current:  # Temporary Shape Data
    object = None
    start_xy = (0, 0)
    end_xy = (0, 0)
    width = 0
    height = 0
    size = (0, 0)
    action = actions['triangle']
    mouse_state = mouse_idle


def creating_shape():
    return any(current.action == action for action in shapes)


def deleting():
    return current.action == actions['delete']


class FpsCounter:
    def __init__(self, text_height, color):
        self.text = 'NULL'
        self.color = Color(color)
        self.font = pg.font.SysFont(fonts['default'], text_height)
        self.surf = self.font.render(self.text, True, self.color)

    def draw(self, display):
        self.text = str(int(CLOCK.get_fps()))
        self.surf = self.font.render(self.text, True, self.color)
        display.blit(self.surf, self.surf.get_rect(bottomright=WINDOW.size))


class Grid():
    def __init__(self, step_x, step_y, color=Color(64, 64, 64), width=1):
        self.surf = Surface(WINDOW.size)
        self.surf.set_colorkey(COLORKEY)
        self.surf.fill(self.surf.get_colorkey())
        if step_x > 0:
            for x in range(0, WINDOW.width + 1, step_x):
                pg.draw.line(self.surf, color, (x, 0), (x, WINDOW.height), width=width)
        if step_y > 0:
            for y in range(0, WINDOW.height + 1, step_y):
                pg.draw.line(self.surf, color, (0, y), (WINDOW.width, y), width=width)

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
        self.color = Color(128, 128, 128)
        self.image = Surface(size)
        self.image.set_colorkey(Color(COLORKEY))
        self.image.fill(self.image.get_colorkey())
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

    def draw(self, display):
        display.blit(self.image, self.rect)
        self.mask = pg.mask.from_surface(self.image)
        return self

    def mouse_hovers(self):
        return masks_collide(self, cursor)

    def change_color(self, color):
        self.color = color
        return self

    def resize_data(self, flip_x=False, flip_y=False):
        self.image = pg.transform.scale(self.image, self.rect.size)
        self.image.fill(self.image.get_colorkey())
        pg.gfxdraw.filled_polygon(self.image, POLYGONS(current.action, self.rect.size).shape, self.color)

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


class DeleteBox(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.color = Color(30, 31, 82)
        self.image = Surface(size)
        self.image.set_colorkey(Color(COLORKEY))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        self.grid = Grid(20, 20, Color(255, 255, 255))
        self.resize_data(False, False)

    def resize_data(self, flip_x=False, flip_y=False):
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
        self.grid.draw(self.image, special_flags=pg.BLEND_MIN)
        return self

    def draw(self, display):
        display.blit(self.image, self.rect, special_flags=pg.BLEND_ADD)


def start_drag():
    C = current
    if creating_shape():
        C.mouse_state = mouse_dragging
        C.start_xy = round_numbers_to_nearest(cursor.rect.topleft, grid_size)
        C.object = Shape(C.start_xy, [0, 0], C.action).change_color(DRAG_COLOR)
    if deleting():
        C.mouse_state = mouse_dragging
        C.start_xy = Vec2(cursor.rect.topleft)
        C.object = DeleteBox(C.start_xy, [0, 0])


def draw_current():
    C = current

    def apply_ratio():
        if creating_shape():
            return grid_size
        return 0

    # update start and end points of drag
    C.object.rect.topleft = C.start_xy
    C.end_xy = round_numbers_to_nearest(cursor.rect.topleft, apply_ratio())
    # update width and height
    C.width = C.end_xy.x - C.start_xy.x
    C.height = C.end_xy.y - C.start_xy.y
    if holding_shift_key:
        # (if holding shift) make sides of shape equal
        if C.width > C.height:
            C.object.rect.size = arr([C.height, C.height])
        else:
            C.object.rect.size = arr([C.width, C.width])
        C.object.rect.size = np.abs(C.object.rect.size)
        C.object.rect.size[0] *= POLYGONS(C.action).ratio
    else:
        C.object.rect.size = np.abs([C.width, C.height])
    if C.width < 0 and C.height < 0:
        C.object.resize_data(True, True)
    elif C.width < 0:
        C.object.resize_data(True, False)
    elif C.height < 0:
        C.object.resize_data(False, True)
    else:
        C.object.resize_data()


def end_drag(color):
    C = current
    if C.mouse_state == mouse_dragging:
        if creating_shape():
            C.object.color = color
            canvas_group.add(C.object)
            draw_current()
        if deleting():
            for shape in canvas_group:
                if masks_collide(shape, C.object) or masks_collide(shape, cursor):
                    canvas_group.remove(shape)
        C.mouse_state = mouse_idle
        C.start_xy = C.end_xy = C.object.rect.size = (0, 0)
        C.width = C.height = 0
    C.object = None
    redraw_canvas()


def cancel_drag():
    C = current
    if not paused:
        if C.mouse_state == mouse_dragging:
            C.mouse_state = mouse_idle
            canvas_group.remove(C.object)
    C.object = None


def apply_ratio():
    C = current
    if creating_shape():
        draw_current()
    elif deleting():
        draw_current()


class ShapeButton():
    def __init__(self, rect, action, bg_color, border_color, border_thickness, shape_color, shape_scale):
        self.rect = Rect(rect)
        self.surf = Surface(self.rect.size)
        self.bg_color = bg_color
        self.surf.fill(self.bg_color)

        self.border_color = border_color
        self.border_thickness = border_thickness

        self.action = action
        self.shape_color = shape_color
        self.shape_scale = shape_scale
        self.shape_image = pg.transform.scale_by(self.surf, self.shape_scale)
        self.shape_image.set_colorkey((COLORKEY));
        self.shape_image.fill(self.shape_image.get_colorkey())
        self.shape_rect = self.shape_image.get_rect(center=Vec2(self.rect.size) / 2)
        self.shape_info = POLYGONS(self.action, Vec2(self.rect.size) * self.shape_scale)
        self.create_shape()

        self.mask = pg.mask.from_surface(self.surf)

    def create_shape(self):
        self.shape_image.fill(self.shape_image.get_colorkey())
        pg.gfxdraw.filled_polygon(self.shape_image,
                                  (self.shape_info.shape) * arr([1 - self.border_thickness * 2 / self.rect.w,
                                                                 1 - self.border_thickness * 2 / self.rect.h]) + self.border_thickness,
                                  self.shape_color)
        return self

    def change_color(self, color):
        self.shape_color = color
        self.create_shape()
        return self

    def mouse_hovers(self, offset=(0, 0)):
        return masks_collide(self, cursor, offset)

    def draw(self, display, special_flags=0):
        self.surf.blit(self.shape_image, self.shape_rect)
        pg.draw.rect(self.surf, self.border_color, self.surf.get_rect(), width=self.border_thickness)
        display.blit(self.surf, self.rect, special_flags=special_flags)
        return self


class TextButton():
    def __init__(self, rect, action, text, text_height, bg_color, border_color, border_thickness):
        self.action = action
        self.bg_color = bg_color
        self.rect = Rect(rect)
        self.surf = Surface(self.rect.size)
        self.surf.fill(self.bg_color)

        font = pg.font.SysFont(fonts['default'], text_height)
        self.text_surf = font.render(text, True, Color('WHITE'))
        self.text_rect = self.text_surf.get_rect(center=Vec2(self.rect.size) / 2)

        self.border_color = border_color
        self.border_thickness = border_thickness

        self.mask = pg.mask.from_surface(self.surf)

    def mouse_hovers(self, offset=(0, 0)):
        return masks_collide(self, cursor, offset)

    def draw(self, display):
        self.surf.blit(self.text_surf, self.text_rect)
        pg.draw.rect(self.surf, self.border_color, self.rect, width=self.border_thickness)
        display.blit(self.surf, self.rect)
        return self


class Hotbar:
    def __init__(self, x, y, button_size, padding, background_color, border_color, border_thickness, icon_scale):
        self.button_bg_color = Color(background_color)
        self.button_bd_color = Color(border_color)
        self.border_thickness = border_thickness

        num_buttons = 7
        self.surf = Surface((num_buttons * button_size[0] + num_buttons * padding, button_size[1]))
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.surf.set_colorkey((COLORKEY));
        self.surf.fill(self.surf.get_colorkey())

        self.button_poses = [(x + off * padding, 0) for off, x in
                             enumerate(range(0, button_size[0] * num_buttons, button_size[0]))]
        self.buttons = []

        for pos, (action, text) in zip([*self.button_poses[0:1]], {actions['delete']: 'DEL'}.items()):
            self.buttons.append(
                TextButton((pos, button_size), action, text, 16,
                           self.button_bg_color, self.button_bd_color, self.border_thickness))
        for pos, action in zip(self.button_poses[len(self.buttons):num_buttons], shapes):
            self.buttons.append(
                ShapeButton((pos, button_size), action, self.button_bg_color,
                            self.button_bd_color, self.border_thickness, RED,
                            icon_scale))
        self.changeAction()
        self.mask = pg.mask.from_surface(self.surf)

    def draw(self, display):
        display.blit(self.surf, self.rect)
        self.mask = pg.mask.from_surface(self.surf)
        return self

    def changeColors(self, color):
        for button in self.buttons:
            if type(button) == ShapeButton:
                button.change_color(color)
        self.update()

    def changeAction(self, event=None):
        try:
            match event.type:
                case pg.KEYDOWN | pg.KEYUP:
                    if current.mouse_state == mouse_dragging:
                        cancel_drag()
                    match event.key:
                        case pg.K_1:
                            current.action = self.buttons[0].action
                        case pg.K_2:
                            current.action = self.buttons[1].action
                        case pg.K_3:
                            current.action = self.buttons[2].action
                        case pg.K_4:
                            current.action = self.buttons[3].action
                        case pg.K_5:
                            current.action = self.buttons[4].action
                        case pg.K_6:
                            current.action = self.buttons[5].action
                        case pg.K_7:
                            current.action = self.buttons[6].action
                case pg.MOUSEBUTTONDOWN | pg.MOUSEBUTTONUP:
                    if not masks_collide(cursor, self):
                        return
                    for button in self.buttons:
                        if not masks_collide(button, cursor, (10, 10)):
                            continue
                        current.action = button.action
                        break
                case pg.MOUSEWHEEL:
                    if current.mouse_state == mouse_dragging:
                        cancel_drag()
                    increment = 1 if e.precise_y < 0 else -1
                    index = list_types.index(current.action) + increment
                    try:
                        current.action = list_types[index]
                    except IndexError:
                        current.action = list_types[0]
        except AttributeError:
            pass
        self.update()

        return self

    def update(self):
        for button in self.buttons:
            if not current.action == button.action:
                bg_color = button.bg_color
            else:
                bg_color = button.bg_color + Color(30, 30, 60)
            button.surf.fill(bg_color)
            button.draw(self.surf)
        return self


class Slider():
    class PD:
        idle = {'bg': Color('WHITE'), 'bd': Color('WHITE')}
        active = {'bg': Color('BLACK'), 'bd': Color('WHITE')}
        current = {'bg': idle['bg'], 'bd': idle['bd']}

    def __init__(self, min, max, initial, rect, texture: Surface,
                 pick_size=(20, 20), border_color=Color(64, 64, 64), border_thickness=5, pick_border_thickness=5):
        self.cursor_dragging = False
        self.min = min
        self.max = max
        self.value = initial
        self.fraction = self.value / self.max

        self.rect = Rect(rect)
        self.surf = Surface(self.rect.size)

        self.pick = Surface((pick_size[0], pick_size[1]))
        self.pick.set_colorkey(Color(COLORKEY));
        self.pick.fill(self.pick.get_colorkey())
        self.pick_rect = self.pick.get_rect(center=(self.rect.w * self.fraction + pick_size[0] / 2, self.rect.h))
        self.pick_border_thickness = pick_border_thickness
        self.triangle_vertices = POLYGONS(actions['triangle'], self.pick_rect.size).shape
        pg.draw.polygon(self.pick, self.PD.current['bg'], self.triangle_vertices)
        pg.draw.polygon(self.pick, self.PD.current['bg'], self.triangle_vertices + arr((0, -1)),
                        width=self.pick_border_thickness)

        # Create bar
        self.texture = texture
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.border_rect = Rect(self.pick_rect.w / 2, 0, *self.rect.size).inflate(self.border_thickness * 2, 0)
        self.bar_rect = Rect(rect)
        self.bar = Surface(self.bar_rect.size)
        self.bar.set_colorkey(Color(COLORKEY));
        self.bar.fill(self.bar.get_colorkey())
        self.bar.blit(pg.transform.scale(texture, self.bar_rect.size), (0, 0))

        self.rect = Rect((self.bar_rect.topleft),
                         (self.bar_rect.w + self.pick_rect.w,
                          self.bar_rect.h + self.border_thickness / 2 + self.pick.get_height() / 3))
        self.surf = Surface(self.rect.size)
        self.surf.set_colorkey(Color(COLORKEY));
        self.surf.fill(self.surf.get_colorkey())

        self.update()

    def draw(self, display, mask_offset=(0, 0)):
        if self.mouse_hovers(mask_offset) or self.cursor_dragging:
            self.PD.current['bg'] = self.PD.active['bg']
            self.PD.current['bd'] = self.PD.active['bd']
        else:
            self.PD.current['bg'] = self.PD.idle['bg']
            self.PD.current['bd'] = self.PD.idle['bd']

        self.update(mask_offset)
        self.surf.fill(self.surf.get_colorkey())
        self.surf.blit(self.bar, (self.pick_rect.w / 2, 0))
        pg.draw.rect(self.surf, self.border_color, self.border_rect, width=self.border_thickness)
        self.surf.blit(self.pick, self.pick_rect.topleft)
        display.blit(self.surf, self.rect)
        return self

    def startDragging(self):
        self.cursor_dragging = True
        cursor.hide()

    def stopDragging(self):
        self.cursor_dragging = False
        cursor.show()

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
        return self

    def scroll(self, event, increment):
        if event.precise_y > 0:
            increment *= -1
        else:
            pass
        self.value += increment

        if self.value <= self.min:
            self.fraction = 0
            self.value = self.min
        if self.value >= self.max:
            self.fraction = 1
            self.value = self.max

        half_pick_width = self.pick_rect.w / 2
        self.fraction = self.value / self.max
        self.pick_rect.centerx = half_pick_width + self.fraction * (self.rect.w - self.pick_rect.w)

    def drag(self, mask_offset):
        if self.cursor_dragging:
            half_pick_width = self.pick_rect.w / 2
            if cursor.rect.x - mask_offset[0] < + self.rect.x + half_pick_width:
                self.fraction = 0
                self.pick_rect.centerx = half_pick_width
            elif cursor.rect.x - mask_offset[0] > + self.rect.x + self.bar_rect.width + half_pick_width:
                self.fraction = 1
                self.pick_rect.centerx = self.rect.width - half_pick_width
            else:
                self.fraction = ((cursor.rect.x - mask_offset[0]) - self.rect.x - half_pick_width) / (
                    self.bar_rect.width)
                self.pick_rect.centerx = cursor.get_pos_in_rect(self.rect)[0] - mask_offset[0]
            self.value = self.fraction * (self.max - self.min) + self.min

            self.PD.current['bg'] = self.PD.active['bg']
            self.PD.current['bd'] = self.PD.active['bd']

    def mouse_hovers(self, offset=(0, 0)):
        return masks_collide(self, cursor, offset)

    def update(self, mask_offset=(0, 0)):
        if self.cursor_dragging:
            if cursor.visible and self.mouse_hovers(mask_offset):
                cursor.hide()
            elif not cursor.visible and not self.mouse_hovers(mask_offset):
                cursor.show()

        self.drag(mask_offset)

        self.pick.fill(self.pick.get_colorkey())
        pg.draw.polygon(self.pick, self.PD.current['bd'], self.triangle_vertices)
        pick_border_ratio_width = (self.pick_rect.w - 2 * self.pick_border_thickness) / self.pick_rect.w
        pick_border_ratio_height = (self.pick_rect.h - 2 * self.pick_border_thickness) / self.pick_rect.h
        pg.draw.polygon(self.pick, self.PD.current['bg'],  # self.triangle
                        self.triangle_vertices * arr((pick_border_ratio_width, pick_border_ratio_height)) +
                        arr((self.pick_rect.w, self.pick_rect.h)) / 2 -
                        arr((self.pick_rect.w, self.pick_rect.h)) *
                        arr((pick_border_ratio_width, pick_border_ratio_height)) / 2)

        self.bar.blit(pg.transform.scale(self.texture, self.bar_rect.size), (0, 0))
        self.mask = pg.mask.from_surface(self.surf)


class TEXTURES:
    def hue_gradient(width, height, s, v, step):
        surf = Surface((width, height))
        pixels = surfarray.pixels3d(surf)
        for x in range(0, surf.get_width(), step):
            pixels[x:x + step, :] = hsv_to_rgb(360 * (x / surf.get_width()), s, v)
        del pixels
        return surf

    def saturation_gradient(width, height, h, v, step):
        surf = Surface((width, height))
        pixels = surfarray.pixels3d(surf)
        for x in range(0, surf.get_width(), step):
            pixels[x:x + step, :] = hsv_to_rgb(h, 100 * x / surf.get_width(), v)
        del pixels
        return surf

    def value_gradient(width, height, h, s, step):
        surf = Surface((width, height))
        pixels = surfarray.pixels3d(surf)
        for x in range(0, surf.get_width(), step):
            pixels[x:x + step, :] = hsv_to_rgb(h, s, 100 * x / surf.get_width())
        del pixels
        return surf


class colorpicker:
    def __init__(self, x, y, width, slider_height, padding=10, pick_size=(20, 20)):
        self.slider_height = slider_height
        self.slider_positions = tuple(
            (0, y + offset * padding) for offset, y in enumerate(range(0, 3 * slider_height, self.slider_height)))
        self.rect = Rect(x, y, width, 3 * slider_height + 3 * padding + pick_size[1])
        self.surf = Surface(self.rect.size)
        self.surf.set_colorkey(Color(COLORKEY))
        self.hue_slider = Slider(min=0, max=360, initial=0,
                                 rect=(*self.slider_positions[0], self.rect.w, slider_height),
                                 texture=TEXTURES.hue_gradient(self.rect.w, self.slider_height, s=100, v=100, step=2),
                                 border_color=Color(64, 64, 64), pick_size=pick_size, pick_border_thickness=3)
        self.saturation_slider = Slider(min=0, max=100, initial=100,
                                        rect=(*self.slider_positions[1], self.rect.w, slider_height),
                                        texture=TEXTURES.saturation_gradient(self.rect.w, self.slider_height, h=0,
                                                                             v=100, step=5),
                                        border_color=Color(64, 64, 64), pick_size=pick_size, pick_border_thickness=3)
        self.value_slider = Slider(min=0, max=100, initial=100,
                                   rect=(*self.slider_positions[2], self.rect.w, slider_height),
                                   texture=TEXTURES.value_gradient(self.rect.w, self.slider_height, h=0, s=100, step=4),
                                   border_color=Color(64, 64, 64), pick_size=pick_size, pick_border_thickness=3)
        self.sliders = (self.hue_slider, self.saturation_slider, self.value_slider)
        for slider in self.sliders:
            slider.bar_rect.inflate(-1, 0)
        self.hue = self.saturation_slider.get()
        self.saturation = self.saturation_slider.get()
        self.value = self.value_slider.get()

        self.rect = self.rect.inflate(pick_size[0] + 1, 0)
        self.surf = pg.transform.scale(self.surf, self.rect.size)
        self.mask = pg.mask.from_surface(self.surf)

    def draw(self, display):
        for slider in self.sliders:
            slider.draw(self.surf, self.rect.topleft)
        display.blit(self.surf, self.rect)
        self.mask = pg.mask.from_surface(self.surf)

    def mouse_hovers(self):
        return masks_collide(self, cursor)

    def startDraggingSelectors(self):
        for slider in self.sliders:
            if slider.mouse_hovers(self.rect.topleft):
                slider.startDragging()

    def stopDraggingSelectors(self):
        for slider in self.sliders:
            slider.stopDragging()

    def scroll(self, hue_incr=0, sat_incr=0, val_incr=0):
        colorpicker.hue_slider.scroll(e, 18)
        self.change_texture()

    def get(self):
        return Color(hsv_to_rgb(self.hue, self.saturation, self.value))

    def set(self, hue, saturation, value):
        for slider in self.sliders:
            if not self.slider.min < hue < self.slider.max:
                raise Exception("colorpicker.set() must be within slider range")

        self.hue_slider.set(hue)
        self.saturation_slider.set(saturation)
        self.value_slider.set(value)
        return self

    def update(self):
        self.hue = self.hue_slider.get()
        self.saturation = self.saturation_slider.get()
        self.value = self.value_slider.get()

        if self.mouse_hovers():
            self.change_texture()

        self.surf.fill(self.surf.get_colorkey())

    def change_texture(self):
        self.hue_slider.texture = TEXTURES.hue_gradient(self.rect.w, self.slider_height, s=self.saturation,
                                                        v=self.value, step=2)
        self.saturation_slider.texture = TEXTURES.saturation_gradient(self.rect.w, self.slider_height, h=self.hue,
                                                                      v=self.value, step=5)
        self.value_slider.texture = TEXTURES.value_gradient(self.rect.w, self.slider_height, h=self.hue,
                                                            s=self.saturation, step=4)


class Cursor:
    def __init__(self):
        self.visible: bool = True
        self.rect: Rect = Rect(*mouse.get_pos(), 1, 1)
        self.mask: Mask = pg.mask.from_surface(Surface(self.rect.size))
        self.color: Color = GREEN
        self.surf: Surface = Surface((6, 6))
        self.surf.set_colorkey(Color(COLORKEY))
        self.update()

    def hide(self):
        self.visible = False
        return self

    def show(self):
        self.visible = True
        return self

    def get_pos_in_rect(self, rect):
        return (arr(self.rect.center) - arr(rect.topleft))

    def update(self):
        self.surf.fill(self.surf.get_colorkey())
        pg.draw.rect(self.surf, self.color, ((2, 0), (2, 6)))
        pg.draw.rect(self.surf, self.color, ((0, 2), (6, 2)))
        self.rect.topleft = mouse.get_pos()
        return self

    def draw(self, display):
        self.rect.topleft = mouse.get_pos()
        if self.visible:
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
        font = pg.font.SysFont(fonts['default'], text_height)
        self.text_surf = font.render(text, True, Color(text_color))
        self.text_rect = self.text_surf.get_rect(center=Vec2(self.rect.size) / 2)

    def mouse_hovers(self, offset=(0, 0)):
        return masks_collide(self, cursor, offset)

    def update(self):
        if self.mouse_hovers():
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
        self.surf = Surface(WINDOW.size)
        self.screen_rect = self.surf.get_rect()
        self.surf.set_alpha(128)

        self.background = Surface(self.surf.get_size())
        self.background.fill(Color(64, 64, 64))
        num_buttons = 4
        self.button_size = (300, 100)
        self.button_positions = ((self.screen_rect.centerx, y + offset * 10) for
                                 offset, y in
                                 enumerate(range(75, self.button_size[1] * num_buttons, self.button_size[1])))
        self.buttons = {}
        for pos, (key, text) in zip(self.button_positions, {'res': 'Resume', 'clear': 'Clear', 'exit': 'Exit',
                                                            'save': 'Save to file'}.items()):
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

    def check_input_for_buttons(self):
        global paused
        global run
        if self.buttons['res'].mouse_hovers():
            paused = False
        if self.buttons['clear'].mouse_hovers():
            clear_canvas()
            paused = False
            redraw_canvas()
        if self.buttons['exit'].mouse_hovers():
            run = False
        if self.buttons['save'].mouse_hovers():
            surface = pg.Surface(WINDOW.size)
            canvas_group.draw(surface)
            save_surface_with_filedialog(surface=surface)

grid_size = 0
paused = False
cursor = Cursor()

hotbar = Hotbar(x=10, y=10,
                button_size=(50, 50),
                padding=5,
                background_color=Color(70, 70, 70),
                border_color=Color(40, 40, 40),
                border_thickness=3,
                icon_scale=0.75)

colorpicker = colorpicker(x=WINDOW.width - 200 - 25,
                          y=15,
                          width=200,
                          slider_height=30,
                          padding=10,
                          pick_size=(16, 16)
                          )

fps_counter = FpsCounter(text_height=22,
                         color=WHITE)

canvas = pg.Surface(WINDOW.size)
canvas_group = pg.sprite.Group()

def redraw_canvas():
    canvas.fill("BLACK")
    grid.draw(SCREEN)
    canvas_group.draw(canvas)

def clear_canvas():
    canvas_group.empty()
    redraw_canvas()

grid_active = False
grid = Grid(grid_size, grid_size)

pause_screen = PauseScreen()

ui_group = [hotbar, colorpicker]

run = True
while run:
    SCREEN.fill(BLACK)
    ####################################################################################################################
    #         POLL FOR EVENTS        #
    ####################################################################################################################
    keys = pg.key.get_pressed()
    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False
        if any_of(e.type, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.KEYDOWN, pg.KEYUP):
            redraw_canvas()
        #######################################################
        #   KEYBOARD   #
        #######################################################
        if e.type == pg.KEYDOWN:
            if not paused:
                hotbar.changeAction(e)
            if e.key == pg.K_ESCAPE:
                paused = not paused
                cancel_drag()

            if e.key == pg.K_r:
                clear_canvas()

            if e.key == pg.K_LSHIFT:
                holding_shift_key = True
            if e.key == pg.K_TAB:
                grid_active = not grid_active
        if e.type == pg.KEYUP:
            if e.key == pg.K_LSHIFT:
                holding_shift_key = False
        #######################################################
        # MOUSE BUTTON #
        #######################################################
        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1:
                if not paused:
                    if not any(masks_collide(cursor, object) for object in
                               ui_group):
                        start_drag()

                    colorpicker.startDraggingSelectors()

                    hotbar.changeAction(e)
                if paused:
                    pause_screen.check_input_for_buttons()
            if e.button == 3:
                if not paused:
                    cancel_drag()
        #######################################################
        if e.type == pg.MOUSEBUTTONUP:
            if e.button == 1:
                if not paused:
                    end_drag(colorpicker.get())
                    current.object
                    colorpicker.stopDraggingSelectors()

        #######################################################
        # SCROLL WHEEL #
        #######################################################
        if e.type == pg.MOUSEWHEEL:
            if not holding_shift_key:
                hotbar.changeAction(e)
            if holding_shift_key:
                colorpicker.scroll(hue_incr=18)
    ####################################################################################################################
    #        Rend_xyER GAME HERE        #
    ####################################################################################################################

    SCREEN.blit(canvas, (0, 0))
    # canvas_group.draw(SCREEN)
    if current.object:
        current.object.draw(SCREEN)
    for shape in canvas_group:
        if masks_collide(cursor, shape):
            cursor.color = (GREEN)
        else:
            cursor.color = (GREEN)

    if not paused:
        colorpicker.draw(SCREEN)
        if current.mouse_state == mouse_dragging:
            draw_current()

        hotbar.changeColors(colorpicker.get())
        for object in ui_group:
            object.draw(SCREEN)
        colorpicker.update()
    elif paused:
        pause_screen.draw(SCREEN)

    cursor.draw(SCREEN)
    fps_counter.draw(SCREEN)

    ####################################################################################################################
    #        Rend_xyER GAME HERE        #
    ####################################################################################################################
    pg.display.update()
    DT = CLOCK.tick(WINDOW.fps)

pg.quit()
