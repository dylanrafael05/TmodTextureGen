from PIL import Image
from PIL.Image import Transpose, Resampling
import random
import pathlib as path
import json

def abspath(p: str) -> str:
    return str(path.Path(p).absolute())

def print_divider():
    print('-' * 50)

base_path = 'bases/ore-mono.png'
base_is_tricolor = False
generate_icon = False
darken_factor = 0.3
input_path = 'input.png'

paramspath = path.Path('params.json')

if paramspath.exists():
    params = json.load(open(paramspath))
    if 'tricolor' in params and params['tricolor'] is True:
        base_is_tricolor = True
    if 'generate_icon' in params and params['generate_icon'] is True:
        generate_icon = True
    if 'darken_factor' in params:
        try:
            darken_factor = float(params['darken_factor'])
        except ValueError:
            pass
    if 'input_file' in params and isinstance(params['input_file'], str):
        input_path = params['input_file']
    if 'base_file' in params and isinstance(params['base_file'], str):
        base_path = params['base_file']

if base_is_tricolor:
    count = 3
    rotations = []
else:
    count = int(input('Frames: '))
    rotations = input('Transformations permitted (fx, fy -> flip, 90 / 180 -> rotate)\nSeperate entries by commas: ').split(', ')

print_divider()
print('Input: ')
print(f'Using input texture from {abspath(input_path)}')
print(f'Using base texture from {abspath(base_path)}')

base = Image.open(base_path)
ipt = Image.open(input_path)

flip_x = 'fx' in rotations
flip_y = 'fy' in rotations
rot_90 = '90' in rotations
rot_180 = '180' in rotations

variants = []

for x in range(count):

    crop = ipt.crop((x * 9, 0, x * 9 + 8, 8))

    variants.append(crop)

    if flip_x:
        variants.append(crop.transpose(Transpose.FLIP_LEFT_RIGHT))
    if flip_y:
        variants.append(crop.transpose(Transpose.FLIP_LEFT_RIGHT))
    if rot_90:
        variants.append(crop.rotate(90))
        variants.append(crop.rotate(270))
    if rot_180:
        variants.append(crop.rotate(180))

out = base.copy()

def darken(c):
    return int(c[0] * darken_factor), int(c[1] * darken_factor), int(c[2] * darken_factor), 255

for i in range(out.width):
    for j in range(out.height):

        pos = (i, j)
        subpos = (i % 9, j % 9)
        cenpos = (i - subpos[0] + 4, j - subpos[1] + 4)

        if base_is_tricolor:
            match out.getpixel(cenpos):
                case (255, 0, 0, 255): variant = variants[0]
                case (0, 255, 0, 255): variant = variants[1]
                case _:                variant = variants[2]
        else:
            variant = random.choice(variants)

        SUBSTITUTION_COLORS = [
            (255, 255, 255, 255),
            (255, 0, 0, 255),
            (0, 255, 0, 255),
            (0, 0, 255, 255)
        ]

        match out.getpixel(pos):
            case x if x in SUBSTITUTION_COLORS: out.putpixel(pos, variant.getpixel(subpos))
            case (0, 0, 0, 255): out.putpixel(pos, darken(variant.getpixel(subpos)))

out.resize((out.width * 2, out.height * 2), Resampling.NEAREST).save('output/output.png')

print_divider()
print('Output: ')
print(f'Saved output to {abspath("output/output.png")}')

if generate_icon:

    min_icon_x, min_icon_y = (out.width, out.height)
    max_icon_x, max_icon_y = (0, 0)

    ICON_BORDER_COLOR = (255, 255, 0, 255)

    for x in range(out.width):
        for y in range(out.height):
            if out.getpixel((x, y)) == ICON_BORDER_COLOR:

                min_icon_x = min(min_icon_x, x)
                min_icon_y = min(min_icon_y, y)

                max_icon_x = max(max_icon_x, x)
                max_icon_y = max(max_icon_y, y)

    icon = out.crop((min_icon_x + 1, min_icon_y + 1, max_icon_x, max_icon_y))
    icon.resize((icon.width * 2, icon.height * 2), Resampling.NEAREST).save('output/output_item.png')
    print(f'Saved output item to {abspath("output/output_item.png")}')

print_divider()