import kociemba
import logging
from typing import Dict, List, Tuple

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

def validate_cube_state(cube_state: Dict[str, List[str]]):
    color_counts = {color: 0 for color in COLOR_TO_FACE_MAP.keys()}
    
    for face_colors in cube_state.values():
        for color in face_colors:
            if color in color_counts:
                color_counts[color] += 1

    for color, count in color_counts.items():
        if count != 9:
            raise ValueError(f"Invalid cube state: Expected 9 '{color}' stickers, but found {count}. A color was likely misidentified due to lighting. Please rescan the cube.")

def get_face_map(cube_state: Dict[str, List[str]]) -> Dict[str, List[str]]:
    # Maps each face's colors to its logical face based on the middle sticker
    # Fifth sticker never changes (index 4)
    face_map = {}
    for face_name, colors in cube_state.items():
        if len(colors) != 9:
            raise ValueError(f"Face {face_name} does not have 9 stickers...")
        center_color = colors[4]
        if center_color in COLOR_TO_FACE_MAP:
            logical_face = COLOR_TO_FACE_MAP[center_color]
            face_map[logical_face] = colors
        else:
            raise ValueError(f"Invalid center color '{center_color}' on {face_name}. Cannot determine face identity...")
    if len(face_map) != 6:
        raise ValueError("Did not receive 6 unique faces. Please check uploaded images for duplicate or invalid faces...")
    return face_map

def orient_and_build_solver_string(cube_state: Dict[str, List[str]]) -> str:
    """
    Orients the cube faces automatically by establishing a chain of references,
    allowing the user to scan faces in any rotation.
    """
    face_map = get_face_map(cube_state)
    oriented_faces = {}

    # Create a reverse map from face character to colour name
    face_char_to_color_map = {v: k for k, v in COLOR_TO_FACE_MAP.items()}

    # This map defines the standard neighbors for each face, 
    # in the order of Top, Right, Bottom, Left from the perspective of looking at that face
    NEIGHBOR_MAP = {
        'U': ['B', 'R', 'F', 'L'],
        'D': ['F', 'R', 'B', 'L'],
        'F': ['U', 'R', 'D', 'L'],
        'B': ['U', 'L', 'D', 'R'],
        'R': ['U', 'B', 'D', 'F'],
        'L': ['U', 'F', 'D', 'B'],
    }

    # Map of opposite faces. An edge piece cannot have the colour of the opposite face
    OPPOSITE_FACE_MAP = {
        'U': 'D', 'D': 'U',
        'F': 'B', 'B': 'F',
        'R': 'L', 'L': 'R',
    }

    for face_char, colors in face_map.items():
        # Get the list of expected neighbor faces for the current face
        expected_neighbors = NEIGHBOR_MAP[face_char]

        # Find which of the expected neighbors we can see on the current face's edges.
        # Edge positions: 0=Top, 1=Right, 2=Bottom, 3=Left
        # Sticker indices: Top=1, Right=5, Bottom=7, Left=3
        edges = [(colors[1], 0), (colors[5], 1), (colors[7], 2), (colors[3], 3)]
        
        rotation_votes = []

        for color, current_pos in edges:
            # Find which face this color belongs to (e.g., 'white' -> 'U')
            face_of_color = COLOR_TO_FACE_MAP.get(color)

            if face_of_color == face_char or face_of_color == OPPOSITE_FACE_MAP.get(face_char):
                continue
            # Check if this face is one of the expected neighbors
            if face_of_color in expected_neighbors:
                target_pos = expected_neighbors.index(face_of_color)
                # Calculate rotations needed if this edge is our reference
                rotations = (current_pos - target_pos + 4) % 4
                rotation_votes.append(rotations)
        
        if not rotation_votes:
            raise ValueError(
                f"Cannot determine orientation for {face_char} face. "
                f"Could not find any valid neighbor colors ({[face_char_to_color_map.get(c) for c in expected_neighbors]}) on its edges."
            )

        # Determine the most likely rotation by finding the mode of the votes, making orientation robust to a single misidentified edge piece
        try:
            from statistics import mode
            rotations = mode(rotation_votes)
        except ImportError:
            rotations = max(set(rotation_votes), key=rotation_votes.count)
        except Exception:
            rotations = rotation_votes[0]


        # Apply the rotations to the list of colors
        rotated_colors = colors
        for _ in range(rotations):
            # This re-orders the list to simulate a 90-degree clockwise rotation of the face.
            rotated_colors = [rotated_colors[i] for i in [6, 3, 0, 7, 4, 1, 8, 5, 2]]
        
        oriented_faces[face_char] = rotated_colors

    # Create final string in the correct U-R-F-D-L-B order
    solver_string = ""
    face_order = ['U', 'R', 'F', 'D', 'L', 'B']
    for face_char in face_order:
        face_colors = oriented_faces[face_char]

        # Iterate through new colours
        for color in face_colors:
            solver_string += COLOR_TO_FACE_MAP.get(color, 'X')

    return solver_string

def solve_with_kociemba(cube_state: Dict[str, List[str]]) -> str:
    validate_cube_state(cube_state)

    solver_string = orient_and_build_solver_string(cube_state)
    logger.info(f"Generated solver string: {solver_string}")
    return kociemba.solve(solver_string)
