import cv2
import numpy as np
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Rubik's Cube colours in HSV format
# H: 0-179, S: 0-255, V: 0-255
COLOR_MAP = {
    "red": [([0, 120, 70], [10, 255, 255]), ([170, 120, 70], [179, 255, 255])],
    "orange": ([10, 120, 70], [25, 255, 255]),
    "yellow": ([26, 120, 70], [34, 255, 255]),
    "green": ([35, 120, 70], [85, 255, 255]),
    "blue": ([86, 120, 70], [128, 255, 255]),
    "white": ([0, 0, 180], [179, 80, 255]),
}

def get_dominant_color(image_roi: np.ndarray) -> Tuple[int, int, int]:
  
    # Calculates the dominant HSV color in a given image region of interest
    hsv_roi = cv2.cvtColor(image_roi, cv2.COLOR_BGR2HSV)
    h_median = np.median(hsv_roi[:, :, 0])
    s_median = np.median(hsv_roi[:, :, 1])
    v_median = np.median(hsv_roi[:, :, 2])
    return int(h_median), int(s_median), int(v_median)

def get_color_name(hsv_color: Tuple[int, int, int]) -> str:
    """Finds the closest color name for a given HSV color."""
    h, s, v = hsv_color
 
    for name, ranges in COLOR_MAP.items():
        # Ensure ranges is always a list of ranges
        if not isinstance(ranges, list):
            ranges = [ranges]
        
        for lower, upper in ranges:
            # Check if the color is within the current range
            if lower[0] <= h <= upper[0] and lower[1] <= s <= upper[1] and lower[2] <= v <= upper[2]:
                return name

    return "unknown"

def process_face(image: np.ndarray) -> List[str]:

    # Processes a single face image to detect the colors of its 9 stickers, returns a list of colour names.
    height, width, _ = image.shape
    sticker_colors = []

    # Simplified grid detection. Assumes the cube face is centred for now
    # Also assumes it takes up most of the image... 
    # Later I will use a different way to find the grid, maybe edge detection

    # 3x3 grid and sample the center of each cell
    sticker_size_h = height // 6
    sticker_size_w = width // 6

    for row in range(3):
        for col in range(3):
            # Calculate the center of each cell in a 3x3 grid
            center_y = int((row + 0.5) * height / 3)
            center_x = int((col + 0.5) * width / 3)

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
