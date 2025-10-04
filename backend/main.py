from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import logging

# Logging to see feedback in terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/api/solve")
async def solve_cube(files: List[UploadFile] = File(...)):

    # Receives images, expects 6 images for the cube face
    if len(files) != 6:
        raise HTTPException(status_code=400, detail="Upload exactly 6 images")

    logger.info(f"Received {len(files)} files.")
    for file in files:
        logger.info(f" - Filename: {file.filename}, Content-Type: {file.content_type}")
        # Pass these files to OpenCV processor here later

    # Dummy solution for now
    dummy_solution = ["R", "U", "R'", "U'", "R'", "F", "R2", "U'", "R'", "U'", "R", "U", "R'", "F'"]

    return {"solution": dummy_solution}

@app.get("/")
def read_root():
    return {"message": "Rubik's cube solver backend running"}