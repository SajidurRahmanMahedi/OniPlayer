# OniPlayer Linux

<p align="center">
  <strong>A minimal, keyboard-and-mouse-centric desktop media player built using PyQt6 and Qt6 Multimedia.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License Badge" />
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=for-the-badge&logo=linux&logoColor=white" alt="Platform Badge" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge" />
  <img src="https://img.shields.io/badge/GUI-PyQt6-darkgreen?style=for-the-badge" alt="GUI Badge" />
</p>


OniPlayer Linux is a minimal, keyboard-and-mouse-centric desktop media player built using **PyQt6** and **Qt6 Multimedia**. Engineered for high-performance and a distraction-free viewing experience, it boots directly into an immersive fullscreen, auto-hides the mouse cursor over video playback, and packs incredibly powerful mouse gestures and keyboard shortcuts.

---

## Features

### Media Playback
* **Universal Format Support:** Decodes all major formats (MP4, MKV, AVI, MOV, WMV, WebM) natively using Qt6 Multimedia with GStreamer backend.
* **Smart Playlists:** Drop a file or directory into the player to automatically queue up all video files in that directory.
* **Auto-Advance:** Seamlessly moves to the next video when the current one finishes.

### Advanced Audio Control
* **Smart Volume:** Smooth scaling with an elegant translucent on-screen display (OSD). Default volume is set to a comfortable `60`.
* **Quick Mute:** Instantly toggle sound with a simple keyboard shortcut or clicking the volume icon.

### Immersive User Interface
* **Distraction-Free Design:** Modern dark theme with minimalist styling. Fullscreen by default.
* **Ultra-Hidden Cursor:** The mouse cursor vanishes automatically over the video area. It instantly reappears when hovering over the timeline or when opening the context menu.
* **Elegant Overlays:** Cyan-stroked text overlays for volume and title information.

---

## Controls & Gestures Guide

OniPlayer is designed to be fully controlled via keyboard shortcuts and advanced mouse gestures.

### Keyboard Controls
| Key | Action |
|:---|:---|
| `Space` | Play / Pause |
| `Enter` / `F` | Toggle Fullscreen |
| `Esc` | Exit Fullscreen |
| `Left Arrow` | Seek Backward 10 seconds |
| `Right Arrow` | Seek Forward 10 seconds |
| `Up Arrow` | Volume Up |
| `Down Arrow` | Volume Down |
| `M` | Toggle Mute |
| `Page Up` | Next Video in Playlist |
| `Page Down` | Previous Video in Playlist |

### Mouse Gestures & Shortcuts
| Action | Gesture / Input |
|:---|:---|
| **Toggle Play/Pause** | Left Double-Click over Video |
| **Toggle Fullscreen** | Middle-Click |
| **Context Menu** | Right-Click |
| **Volume Control** | Scroll Mouse Wheel |
| **Fast Forward / Rewind** | Hold Left-Click + Scroll Mouse Wheel |
| **Next Video** | Hold Left-Click + Single-Click Right-Click |
| **Previous Video** | Hold Right-Click + Single-Click Left-Click |
| **Seek Playback** | Click / Drag Timeline |

---

## Getting Started

### Prerequisites
* Linux OS (tested on Ubuntu/Debian-based systems)
* Python 3.10+
* PyQt6
* GStreamer plugins for multimedia support

### Setting Up Development Environment

1. **Install System Dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-pip gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install PyQt6
   ```

3. **Run OniPlayer:**
   ```bash
   python main.py
   ```

   Or with a video file:
   ```bash
   python main.py /path/to/video.mp4
   ```

---

## Additional Features

### Context Menu (Right-Click)
- Play/Pause
- Toggle Fullscreen
- Open File
- Previous/Next Video
- Seek controls (Back/Forward 10s, 30s)

### Playlist Management
- Automatic playlist creation from directory
- Next/Previous video navigation
- Auto-play next video when current ends

### Drag and Drop
- Drag and drop video files directly onto the player

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
