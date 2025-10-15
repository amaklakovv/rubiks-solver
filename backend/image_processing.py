import cv2
import numpy as np
import logging
from typing import List, Tuple, NamedTuple

logger = logging.getLogger(__name__)

class ColorRange(NamedTuple):
    name: str
    hsv_lower: np.ndarray
    hsv_upper: np.ndarray

# Rubik's Cube colours in HSV format (H: 0-179, S: 0-255, V: 0-255)
# Using a list of objects is cleaner for colours like red that wrap around the hue circle
COLOR_RANGES = [
    # Red wraps around 0/179 in HSV
    ColorRange("red", np.array([0, 120, 70]), np.array([10, 255, 255])),
    ColorRange("red", np.array([170, 120, 70]), np.array([179, 255, 255])),
    ColorRange("orange", np.array([11, 120, 70]), np.array([20, 255, 255])),
    ColorRange("yellow", np.array([21, 120, 70]), np.array([34, 255, 255])),
    ColorRange("green", np.array([35, 120, 70]), np.array([85, 255, 255])),
    ColorRange("blue", np.array([86, 120, 70]), np.array([128, 255, 255])),
    
    # White has low saturation and high value
    ColorRange("white", np.array([0, 0, 180]), np.array([179, 80, 255])),
    
    # Black or dark can be defined by low value
    # ColorRange("black", np.array([0, 0, 0]), np.array([179, 255, 70])),
]

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

    for color in COLOR_RANGES:
        if (color.hsv_lower[0] <= h <= color.hsv_upper[0] and
            color.hsv_lower[1] <= s <= color.hsv_upper[1] and
            color.hsv_lower[2] <= v <= color.hsv_upper[2]):
            return color.name

    return "unknown"

def process_face(image: np.ndarray) -> Tuple[List[str], np.ndarray]:

    # Processes a single face image to detect the colors of its 9 stickers, returns a list of colour names.
    height, width, _ = image.shape
    debug_image = image.copy()
    sticker_colors = []

    # Improved grid detection here, assuming the cube face is centered
    # Later I will use a different way to find the grid, maybe edge detection
    CUBE_AREA_RATIO = 0.6
    roi_width = int(width * CUBE_AREA_RATIO)
    roi_height = int(height * CUBE_AREA_RATIO)
    roi_x_start = (width - roi_width) // 2
    roi_y_start = (height - roi_height) // 2

    sticker_size = min(roi_width, roi_height) // 6

    for row in range(3):
        for col in range(3):
            # Calculate the center of each cell
            center_x = roi_x_start + int((col + 0.5) * roi_width / 3)
            center_y = roi_y_start + int((row + 0.5) * roi_height / 3)

            # Define small region of interest around center
            y1 = max(0, center_y - sticker_size // 2)
            y2 = min(height, center_y + sticker_size // 2)
            x1 = max(0, center_x - sticker_size // 2)
            x2 = min(width, center_x + sticker_size // 2)

            roi = image[y1:y2, x1:x2]
            dominant_color = get_dominant_color(roi)
            color_name = get_color_name(dominant_color)
            sticker_colors.append(color_name)

            # Draw a rectangle on the debug image to show where we looked
            cv2.rectangle(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Put the detected color name on the image
            cv2.putText(debug_image, color_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return sticker_colors, debug_image
