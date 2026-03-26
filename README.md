# Face-Basec Cursor Control

A Python application that enables hands-free cursor control using facial movements captured from a webcam. The system tracks face position to move the cursor and detects mouth gestures for mouse clicks.

## Features

* Real-time face tracking (OpenCV)
* Cursor control based on face position
* Grid-based directional movement
* Gesture-based left click (teeth detection)
* Adjustable sensitivity via GUI slider
* Simple GUI built with CustomTkinter
* Live camera preview with visual feedback

## Tech Stack

* Python
* OpenCV
* MediaPipe
* PyAutoGUI
* CustomTkinter
* PIL

## How It Works

1. Capture video from webcam
2. Detect face position in frame
3. Map face position to screen movement (grid-based directions)
4. Track mouth landmarks using MediaPipe FaceMesh
5. Detect “teeth exposure” using mouth aspect ratio
6. Trigger mouse click based on gesture
7. Continuously update cursor position in real time

## Controls

* **Cursor movement** – moves toward the grid region where the face is detected
* **Mouse click** – left button is pressed when teeth are exposed and released when the mouth closes
* **Start** – activates cursor control
* **Pause** – temporarily stops cursor movement
* **Quit** – closes the application
* **Sensitivity slider** – adjusts the threshold for teeth detection to match user preference/facial expressions

## Notes

* Designed as a prototype for accessibility (hands-free control)
* Detection may be affected by lighting and occlusions (e.g. glasses)
* Sensitivity can be adjusted via slider
* Can be extended with additional gestures (e.g. right-click)
