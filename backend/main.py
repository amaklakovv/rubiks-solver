from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from typing import Dict, Any
import io
import logging
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import pillow_heif
from .image_processing import process_face, get_color_name
from .solver import solve_with_kociemba

# Logging to see feedback in terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Directory for debug images to see where the script is looking
DEBUG_DIR = Path("debug_images")
DEBUG_DIR.mkdir(exist_ok=True)

def detect_cube_state(images: List[np.ndarray]) -> Dict[str, Any]:

    # Detects the colour of each sticker on each face of the Rubik's cube, and returns the cube state.
    cube_state = {}
    for i, img in enumerate(images):
        # process_face now also returns an image with debug drawings
        face_colors, debug_image = process_face(img)
        logger.info(f"Detected colours for face {i+1}: {face_colors}")
        
        # Save the debug image to see where the algorithm is sampling
        debug_image_path = DEBUG_DIR / f"face_{i+1}_debug.png"
        cv2.imwrite(debug_image_path, debug_image)
        logger.info(f"Saved debug image to {debug_image_path}")

        # Storing colours in a list
        cube_state[f'face_{i+1}'] = face_colors
    return cube_state

@app.post("/api/solve")
async def solve_cube(files: List[UploadFile] = File(...)):
    # Receives images, expects 6 images for the cube face
    if len(files) != 6:
        raise HTTPException(status_code=400, detail="Upload exactly 6 images")

    logger.info(f"Received {len(files)} files.")
    images = []
    for i, file in enumerate(files):
        logger.info(f" - Filename: {file.filename}, Content-Type: {file.content_type}")
        image_data = await file.read()
        img = None

        # Try to decode as HEIC/HEIF first (as i upload the images from my iPhone)
        try:
            heif_file = pillow_heif.read_heif(io.BytesIO(image_data))
            image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")

            # Convert to BGR for OpenCV
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            logger.info(f"Successfully decoded HEIC image: {file.filename}")
        except pillow_heif.HeifError:
            
            # If it's not HEIC, try decoding with OpenCV
            logger.info(f"Not a HEIC file, trying standard decoding for: {file.filename}")
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        if img is None:
            logger.error(f"Failed to decode image: {file.filename}")
            raise HTTPException(status_code=400, detail=f"Could not decode image: {file.filename}. It may be corrupted or in an unsupported format.")
        
        # If image has an alpha channel, convert it to BGR
        if len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        images.append(img)

    cube_state = detect_cube_state(images)
    logger.info(f"Detected cube state: {cube_state}")

    try:
        # Pass cube_state to solver algorithm
        solution = solve_with_kociemba(cube_state)
        # The solver returns a single string and splits it into a list of moves
        solution_moves = solution.split()
        return {"solution": solution_moves}
    except Exception as e:
        logger.error(f"Error during solving: {e}")
        raise HTTPException(status_code=400, detail=f"Could not solve the cube. Error: {e}. Please check if all faces are scanned correctly...")

@app.get("/")
def read_root():
    return {"message": "Rubik's cube solver backend running"}