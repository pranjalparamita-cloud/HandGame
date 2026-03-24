# Neon Void Hunter 🖐️✨

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange)
![Pygame](https://img.shields.io/badge/Pygame-Game%20Engine-red)

**Neon Void Hunter** is an experimental arcade shooter that replaces the mouse and keyboard with computer vision. Using **OpenCV** and **MediaPipe**, the game tracks your hand in real-time, allowing you to aim with your index finger and shoot targets by pinching your fingers.

> **Project Goal:** To demonstrate how Computer Vision and Human-Computer Interaction (HCI) concepts can be applied to create immersive, controller-free gaming experiences.

---

## 🎮 Game Preview

<!-- OPTIONAL: Add a screenshot or GIF here later -->
<!-- ![Game Demo](screenshots/gameplay.gif) -->

*   **Aim:** Move your index finger to control the neon crosshair.
*   **Shoot:** Pinch your **Thumb** and **Index Finger** together to fire.
*   **Goal:** Destroy the expanding circles before they disappear. Score as high as you can in 60 seconds!

---

## ✨ Features

*   **Real-Time Hand Tracking:** Uses MediaPipe to detect 21 hand landmarks with high precision.
*   **Gesture Recognition:** Implements a custom "Pinch" detection algorithm based on Euclidean distance between finger tips.
*   **Smooth Cursor Movement:** Uses Linear Interpolation (Lerp) to smooth out camera jitter for a fluid gaming experience.
*   **Visual Polish:**
    *   Neon aesthetic with glowing effects.
    *   Custom particle system for explosions.
    *   On-screen scoring and timer.
*   **Physics:** Simple collision detection and particle velocity calculations.

---

## 🛠️ Tech Stack

*   **Language:** Python 3.x
*   **Libraries:**
    *   `opencv-python` (Camera input & image processing)
    *   `mediapipe` (Hand landmark detection)
    *   `pygame` (Game loop, graphics, and window management)
    *   `numpy` (Math calculations)

---

## 🚀 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/handgame.git
    cd handgame
    ```

2.  **Install Dependencies**
    Ensure you have Python installed, then run:
    ```bash
    pip install opencv-python mediapipe pygame numpy
    ```

3.  **Run the Game**
    ```bash
    python hand_game.py
    ```

---

## 🧠 How It Works

1.  **Capture:** OpenCV captures the video feed from your webcam.
2.  **Process:** MediaPipe analyzes the frame to find the hand. It returns coordinates for the **Index Finger Tip (ID 8)** and **Thumb Tip (ID 4)**.
3.  **Map:** The coordinates are mapped from the webcam resolution (e.g., 640x480) to the game window resolution (1280x720).
4.  **Interact:**
    *   The **Index Tip** updates the cursor position.
    *   The distance between the **Thumb** and **Index** is calculated. If `distance < 30 pixels`, the game registers a "Click".
5.  **Render:** Pygame draws the targets, particles, and UI based on the game state.

---

## ⚠️ Troubleshooting

*   **Camera not opening?** Ensure no other app (Zoom/Discord) is using the webcam.
*   **Laggy movement?** Good lighting is essential for MediaPipe to track hands smoothly.
*   **"No module named..." errors?** Make sure you ran the `pip install` command in step 2.

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---

Made with ❤️ and Python.
