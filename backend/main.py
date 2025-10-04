from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from typing import Dict, Any
import logging

import cv2
import numpy as np

# Logging to see feedback in terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def detect_cube_state(images: List[np.ndarray]) -> Dict[str, Any]:
    
    # Detects the color of each sticker on each face of the Rubik's cube, and returns the cube state.
    cube_state = {}
    for i, img in enumerate(images):
        logger.info(f"Processing image {i+1} with shape {img.shape}")
        # I need to implement color detection for each sticker on the face
        #Just has a placeholder showing images are received
        cube_state[f'face_{i+1}'] = "detected_colors_placeholder"
    return cube_state

@app.post("/api/solve")
async def solve_cube(files: List[UploadFile] = File(...)):
    # Receives images, expects 6 images for the cube face
    if len(files) != 6:
        raise HTTPException(status_code=400, detail="Upload exactly 6 images")

    logger.info(f"Received {len(files)} files.")
    images = []
    for file in files:
        logger.info(f" - Filename: {file.filename}, Content-Type: {file.content_type}")
        image_data = await file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        images.append(cv2.imdecode(nparr, cv2.IMREAD_COLOR))

    cube_state = detect_cube_state(images)
    logger.info(f"Detected cube state: {cube_state}")

    # TODO: Pass the cube_state to a solver algorithm.
    dummy_solution = ["R", "U", "R'", "U'", "R'", "F", "R2", "U'", "R'", "U'", "R", "U", "R'", "F'"]

    return {"solution": dummy_solution}

@app.get("/")
def read_root():
    return {"message": "Rubik's cube solver backend running"}