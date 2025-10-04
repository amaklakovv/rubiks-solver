import cv2
import numpy as np
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Define the standard Rubik's Cube colors in bgr format and names, values might need tuning based on lighting...
COLOR_MAP = {
    "white": ([180, 180, 180], [255, 255, 255]),
    "yellow": ([0, 180, 180], [80, 255, 255]),
    "blue": ([180, 0, 0], [255, 100, 100]),
    "green": ([0, 180, 0], [100, 255, 100]),
    "red": ([0, 0, 180], [100, 100, 255]),
    "orange": ([0, 100, 200], [100, 180, 255]),
}

def get_dominant_color(image_roi: np.ndarray) -> Tuple[int, int, int]:

    # Finds the dominant colour in a small image region by averaging the colour, returns as average BGR colour
    # Calculate the median colour for each channel, using median to reduce the effect of outliers
    b_median = np.median(image_roi[:, :, 0])
    g_median = np.median(image_roi[:, :, 1])
    r_median = np.median(image_roi[:, :, 2])
    return int(b_median), int(g_median), int(r_median)

def get_color_name(bgr_color: Tuple[int, int, int]) -> str:
    # Finds the closest colour name for a given BGR colour, returns the closest colour as a string
    min_dist = float('inf')
    closest_color = "unknown"

    # Using a simple Euclidean distance in BGR space. I think I might consider converting to a different colour space?
    for name, (lower, upper) in COLOR_MAP.items():
        # Use the center of the range for distance calculation
        color_center = np.array([(l+u)/2 for l, u in zip(lower, upper)])
        dist = np.linalg.norm(np.array(bgr_color) - color_center)

        if dist < min_dist:
            min_dist = dist
            closest_color = name

    return closest_color

def process_face(image: np.ndarray) -> List[str]:

    # Processes a single face image to detect the colors of its 9 stickers, returns a list of colour names.
    height, width, _ = image.shape
    sticker_colors = []

    # Simplified grid detection. Assumes the cube face is centred for now
    # Also assumes it takes up most of the image... 
    # Later I will use a different way to find the grid, maybe edge detection

    # 3x3 grid and sample the center of each cell
    sticker_size_h = height // 5
    sticker_size_w = width // 5

    for row in range(3):
        for col in range(3):
            # Centre of grid cells
            center_y = int((row * 2 + 1.5) * height / 6)
            center_x = int((col * 2 + 1.5) * width / 6)

            # Define small region of interest around center
            y1 = max(0, center_y - sticker_size_h // 2)
            y2 = min(height, center_y + sticker_size_h // 2)
            x1 = max(0, center_x - sticker_size_w // 2)
            x2 = min(width, center_x + sticker_size_w // 2)

            roi = image[y1:y2, x1:x2]
            dominant_color = get_dominant_color(roi)
            color_name = get_color_name(dominant_color)
            sticker_colors.append(color_name)

    return sticker_colors
