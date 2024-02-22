"""
DT-Box
Pavel Chigirev, pavelchigirev.com, 2023-2024
See LICENSE.txt for details
"""

def validate_int(input):
    if input == "":
        return True
    try:
        int(input)
        return True
    except ValueError:
        return False

def validate_float(input):
    if input == "":
        return True
    try:
        float(input)
        return True
    except ValueError:
        return False

def str_to_color(color_str):
    rgb = []
    cs = color_str.split('-')
    for c in cs:
        rgb.append(int(c))
    return tuple(rgb)

def color_to_str(color):
    color_string = '-'.join(str(x) for x in color)
    return color_string

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))