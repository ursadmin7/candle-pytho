import os
import sys
import time
import math
import random
import shutil
import argparse

# ============================================================
# CANDLE v2.0 | PROCEDURAL ASCII LIGHT ENGINE
# Created by Syed Yusuf
# Python Standard Library Only
# ============================================================

VERSION = "2.0.0"

RESET = "\033[0m"
BOLD = "\033[1m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
HOME = "\033[H"
CLEAR = "\033[2J"

CHARS = "  .,:;irsXA253hMHGS#9B&@"
WIDTH = 88
HEIGHT = 34

USE_COLOR = True

# ------------------------------------------------------------
# TERMINAL
# ------------------------------------------------------------

def setup_terminal():
    os.system("")
    sys.stdout.write(HIDE_CURSOR + CLEAR)
    sys.stdout.flush()


def restore_terminal():
    sys.stdout.write(RESET + SHOW_CURSOR + "\n")
    sys.stdout.flush()


def terminal_size():
    size = shutil.get_terminal_size((WIDTH, HEIGHT + 5))
    return min(size.columns, 120), min(size.lines - 3, 48)


# ------------------------------------------------------------
# MATH UTILITIES
# ------------------------------------------------------------

def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smoothstep(a, b, x):
    if abs(b - a) < 1e-9:
        return float(x >= b)

    t = clamp((x - a) / (b - a))
    return t * t * (3.0 - 2.0 * t)


def mix(a, b, t):
    return a + (b - a) * t


def ellipse_sdf(x, y, cx, cy, rx, ry):
    """
    Approximate signed distance to an ellipse.
    Negative = inside, positive = outside.
    """
    px = (x - cx) / max(rx, 1e-6)
    py = (y - cy) / max(ry, 1e-6)

    k0 = math.sqrt(px * px + py * py)
    k1 = math.sqrt(
        (x - cx) ** 2 / max(rx, 1e-6) ** 2
        + (y - cy) ** 2 / max(ry, 1e-6) ** 2
    )

    return (k0 - 1.0) * min(rx, ry) / max(k0, 1e-6)


def box_sdf(x, y, cx, cy, hx, hy):
    """
    Signed distance to an axis-aligned rectangle.
    """
    qx = abs(x - cx) - hx
    qy = abs(y - cy) - hy

    outside = math.sqrt(
        max(qx, 0.0) ** 2 + max(qy, 0.0) ** 2
    )

    inside = min(max(qx, qy), 0.0)

    return outside + inside


def union_sdf(a, b):
    return min(a, b)


# ------------------------------------------------------------
# PROCEDURAL FLAME
# ------------------------------------------------------------

def flame_distance(x, y, t):
    """
    A tapered, animated flame built from a moving centerline
    and a varying radius.
    """

    flicker = (
        0.035 * math.sin(t * 7.0)
        + 0.018 * math.sin(t * 13.7)
        + 0.012 * math.sin(t * 21.0)
    )

    height = 1.0 + flicker

    base_y = 0.0
    tip_y = 1.85 * height

    if y < base_y - 0.1 or y > tip_y + 0.1:
        vertical_distance = min(
            abs(y - base_y),
            abs(y - tip_y)
        )
    else:
        vertical_distance = 0.0

    u = clamp((y - base_y) / max(tip_y - base_y, 1e-6))

    radius = (
        0.31
        * math.sin(math.pi * u) ** 0.85
        * (1.0 - 0.30 * u)
    )

    center_x = (
        0.055 * math.sin(t * 3.8 + y * 2.2)
        + 0.025 * math.sin(t * 8.0 - y * 4.0)
    )

    radial_distance = abs(x - center_x) - radius

    # Smooth tapered end at the flame tip.
    return max(radial_distance, vertical_distance - 0.08)


# ------------------------------------------------------------
# CANDLE GEOMETRY
# ------------------------------------------------------------

def candle_distance(x, y, t):
    """
    Candle body, wax rim and rounded base.
    Coordinates are normalized around the center.
    """

    body = box_sdf(
        x, y,
        0.0, -1.12,
        0.43, 0.95
    )

    top = ellipse_sdf(
        x, y,
        0.0, -0.17,
        0.43, 0.095
    )

    bottom = ellipse_sdf(
        x, y,
        0.0, -2.04,
        0.44, 0.12
    )

    distance = union_sdf(body, bottom)

    # Slightly uneven melted wax along the upper edge.
    for index in range(5):
        drip_x = -0.32 + index * 0.16

        drip_length = (
            0.12
            + 0.08 * math.sin(index * 2.1)
            + 0.035 * math.sin(t * 1.5 + index)
        )

        drip = box_sdf(
            x, y,
            drip_x,
            -0.26 - drip_length / 2.0,
            0.035,
            drip_length / 2.0
        )

        distance = union_sdf(distance, drip)

    return union_sdf(distance, top)


# ------------------------------------------------------------
# LIGHTING
# ------------------------------------------------------------

def scene(x, y, t):
    """
    Returns RGB color and intensity for one sample point.
    """

    flame = flame_distance(x, y, t)
    candle = candle_distance(x, y, t)

    # Flame emission and surrounding light.
    flame_glow = math.exp(-max(flame, 0.0) * 5.0)
    broad_glow = math.exp(
        -((x / 1.15) ** 2 + ((y - 0.25) / 2.0) ** 2)
    )

    # Candle surface glow.
    candle_glow = math.exp(-abs(candle) * 8.0)

    # Soft background illumination.
    ambient = 0.025 + 0.025 * broad_glow

    # Background: subtle warm light around the candle.
    red = 0.025 + 0.45 * broad_glow
    green = 0.015 + 0.13 * broad_glow
    blue = 0.025 + 0.025 * broad_glow

    intensity = ambient + 0.85 * flame_glow

    red += 0.95 * flame_glow
    green += 0.55 * flame_glow
    blue += 0.08 * flame_glow

    # Hot core of the flame.
    core = math.exp(
        -((x / 0.12) ** 2 + ((y - 0.65) / 0.48) ** 2)
    )

    red += 0.35 * core
    green += 0.38 * core
    blue += 0.16 * core

    # Candle wax material.
    candle_mask = 1.0 - smoothstep(-0.04, 0.06, candle)

    if candle_mask > 0.0:
        wax_light = (
            0.50
            + 0.18 * math.sin(x * 12.0 + t * 0.3)
            + 0.10 * math.sin(y * 8.0)
        )

        red = mix(red, 0.92 * wax_light, candle_mask)
        green = mix(green, 0.78 * wax_light, candle_mask)
        blue = mix(blue, 0.51 * wax_light, candle_mask)

        # Warm reflection near the flame.
        reflection = clamp(
            math.exp(-((x / 0.38) ** 2 + ((y + 0.25) / 0.38) ** 2))
        )

        red += 0.07 * reflection * candle_mask
        green += 0.04 * reflection * candle_mask

    # Wick.
    wick = box_sdf(
        x, y,
        0.0, -0.035,
        0.025, 0.14
    )

    if wick < 0:
        red, green, blue = 0.16, 0.07, 0.025

    # Ground reflection.
    ground = math.exp(
        -(x / 1.5) ** 2
        - ((y + 2.23) / 0.11) ** 2
    )

    red += 0.28 * ground
    green += 0.075 * ground

    return (
        clamp(red),
        clamp(green),
        clamp(blue),
        clamp(intensity + candle_glow * 0.18)
    )


# ------------------------------------------------------------
# ASCII RENDERER
# ------------------------------------------------------------

def rgb_escape(red, green, blue):
    r = int(clamp(red) * 255)
    g = int(clamp(green) * 255)
    b = int(clamp(blue) * 255)

    return f"\033[38;2;{r};{g};{b}m"


def render_frame(width, height, t):
    """
    Render the candle using ASCII density and RGB color.
    """

    aspect = 2.0
    image = []

    for row in range(height):
        line = []

        for column in range(width):
            x = (column / max(width - 1, 1) - 0.5) * 4.0
            y = (0.5 - row / max(height - 1, 1)) * (
                4.0 * height / max(width * aspect, 1)
            )

            # Scale scene to keep candle vertically centered.
            y *= 2.0

            red, green, blue, intensity = scene(x, y, t)

            # Sparse cinematic sparks.
            spark_seed = (
                math.sin(column * 127.1 + row * 311.7 + t * 2.0)
                * 43758.5453
            )
            spark_value = spark_seed - math.floor(spark_seed)

            spark_zone = (
                abs(x) < 1.0
                and -1.8 < y < 1.8
                and y > -1.8
            )

            if spark_zone and spark_value > 0.997:
                red = 1.0
                green = random.uniform(0.35, 0.85)
                blue = 0.03
                intensity = max(intensity, 0.85)

            index = int(
                clamp(intensity) * (len(CHARS) - 1)
            )

            char = CHARS[index]

            if USE_COLOR:
                color = rgb_escape(red, green, blue)
                line_color = color + char + RESET
            else:
                line_color = char

            line.append(line_color)

        image.append("".join(line))

    return "\n".join(image)


# ------------------------------------------------------------
# APPLICATION
# ------------------------------------------------------------

def run_animation(fps=18):
    width, height = terminal_size()

    if width < 40 or height < 15:
        print("Please enlarge your terminal window.")
        return

    frame_duration = 1.0 / max(fps, 1)
    start = time.perf_counter()
    frame_number = 0

    setup_terminal()

    try:
        while True:
            current_time = time.perf_counter() - start

            frame = render_frame(
                width=min(width, 100),
                height=min(height - 2, 36),
                t=current_time
            )

            sys.stdout.write(HOME + frame)

            footer = (
                f"\n\033[38;2;255;170;50m"
                f"  CANDLE v{VERSION}"
                f"  |  A PROCEDURAL ASCII EXPERIENCE"
                f"  |  CTRL+C TO EXIT"
                f"{RESET}"
            )

            sys.stdout.write(footer)
            sys.stdout.flush()

            frame_number += 1

            elapsed = time.perf_counter() - start
            target = frame_number * frame_duration
            delay = target - elapsed

            if delay > 0:
                time.sleep(delay)

    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal()


def main():
    parser = argparse.ArgumentParser(
        description="CANDLE - Procedural ASCII Flame Renderer"
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=18,
        help="Animation frame rate (default: 18)"
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Render monochrome ASCII"
    )

    args = parser.parse_args()

    global USE_COLOR
    USE_COLOR = not args.no_color

    try:
        run_animation(args.fps)
    except (OSError, ValueError) as error:
        restore_terminal()
        print(f"Renderer error: {error}")


if __name__ == "__main__":
    main()