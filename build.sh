#!/usr/bin/env bash

# Update system packages
sudo apt-get update

# Install tesseract OCR engine
sudo apt-get install -y tesseract-ocr

# Clean cache to reduce image size
sudo apt-get clean
