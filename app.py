from flask import Flask, request, jsonify
import cv2
import pytesseract
import numpy as np
import os
import re
app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def extract_plate(results):
    # 1. Combine text
    combined = " ".join([r[2] for r in results])

    # 2. Normalize
    clean = re.sub(r'[^A-Z0-9]', '', combined.upper())

    # 3. OCR fixes
    clean = clean.replace('O', '0')

    # 4. Regex extraction
    pattern = r'[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}'
    match = re.search(pattern, clean)

    return match.group() if match else None


@app.route("/ocr", methods=["POST"])
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    # ----------- 1. Read image -----------
    img_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"detected_text": None})

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ----------- 2. Preprocess image -----------
    thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    thresh = cv2.medianBlur(thresh, 3)

    # ----------- 3. Detect text regions using contours -----------
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    results = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Same filter as your notebook
        if w < 20 or h < 20:
            continue

        roi = image[y:y+h, x:x+w]

        # OCR (same config)
        text = pytesseract.image_to_string(
            roi, config="--psm 7"
        )

        if text.strip():
            results.append((x, y, text.strip()))

    # ----------- 4. Sort results -----------
    results = sorted(results, key=lambda r: (r[1], r[0]))
    print(results)
    # Combine text
    final_text = extract_plate(results)

    return jsonify({"detected_text": final_text or None})


@app.route("/")
def home():
    return jsonify({"status": "OCR Flask API running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
