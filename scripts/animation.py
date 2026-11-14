from pathlib import Path

import pygame

ROOT_DIR = Path(__file__).resolve().parents[1]


def load_strip(path, frame_width, frame_height, frame_count=None, row=0):
    sheet_path = ROOT_DIR / path
    if frame_width <= 0 or frame_height <= 0 or row < 0:
        raise ValueError(f"Invalid frame dimensions or row for sprite sheet: {sheet_path}")

    sheet = pygame.image.load(str(sheet_path)).convert_alpha()
    columns = sheet.get_width() // frame_width
    rows = sheet.get_height() // frame_height
    if row >= rows:
        raise ValueError(f"Invalid frame dimensions or row for sprite sheet: {sheet_path}")

    count = columns if frame_count is None else frame_count
    if count <= 0 or count > columns:
        raise ValueError(f"Invalid frame count for sprite sheet: {sheet_path}")

    return [
        sheet.subsurface(
            (index * frame_width, row * frame_height, frame_width, frame_height)
        ).copy()
        for index in range(count)
    ]
