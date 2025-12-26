#!/usr/bin/env bash

# Update system packages
apt-get update

# Install tesseract OCR engine
apt-get install -y tesseract-ocr

# Clean cache to reduce image size
apt-get clean
