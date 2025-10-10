import kociemba
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Mapping from full color names to the single-letter representation, for example white is up
COLOR_TO_FACE_MAP = {
    'white': 'U',
    'red': 'R',
    'green': 'F',
    'yellow': 'D',
    'orange': 'L',
    'blue': 'B'
}

def to_solver_string(cube_state: Dict[str, List[str]]) -> str:
    # Converts the detected cube state dictionary into a 54-character string which is required by the kociemba solver.
    face_order = ['U', 'R', 'F', 'D', 'L', 'B']
    
    # Map each physical face to its logical face based on its centre sticker
    # The centre never changes, so we can use it to determine what side is which
    face_map = {}
    for face_name, colors in cube_state.items():
        center_color = colors[4]
        if center_color in COLOR_TO_FACE_MAP:
            logical_face = COLOR_TO_FACE_MAP[center_color]
            face_map[logical_face] = colors
        else:
            raise ValueError(f"Invalid center color '{center_color}' on {face_name}. Cannot determine orientation.")

    # Build the final string
    solver_string = ""
    for face_char in face_order:
        if face_char not in face_map:
            raise ValueError(f"Could not find the {face_char} face (center color). Please ensure all 6 faces are uploaded correctly.")
        
        # For each colour on the face you add its corresponding letter
        face_colors = face_map[face_char]
        for color in face_colors:
            solver_string += COLOR_TO_FACE_MAP.get(color, 'X')

    return solver_string

def solve_with_kociemba(cube_state: Dict[str, List[str]]) -> str:
    solver_string = to_solver_string(cube_state)
    logger.info(f"Generated solver string: {solver_string}")
    return kociemba.solve(solver_string)
