# OniPlayer

<p align="center">
  <img src="icon/icon.ico" alt="OniPlayer Android Icon" width="140" height="140" style="border-radius: 22%; margin: 10px;" />
</p>
<p align="center">
  <strong>OniPlayer Logo</strong>
</p>

<p align="center">
  <strong>A premium, high-performance, dark-themed media player suite built for native Android & desktop Windows, powered by VideoLAN's LibVLC core.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Android%20%7C%20Windows%20%7C%20Linux-blue?style=for-the-badge&logo=platform&logoColor=white" alt="Platforms Badge" />
  <img src="https://img.shields.io/badge/Engines-LibVLC%203.7-orange?style=for-the-badge&logo=vlc&logoColor=white" alt="VLC Badge" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License Badge" />
</p>

---

## Welcome to OniPlayer

**OniPlayer** is a highly polished, distraction-free media playback ecosystem tailored for both mobile (Android) and desktop (Windows) platforms. Unified by a curated deep dark interface, vibrant sky-blue accents, and intuitive control schemes, OniPlayer ensures butter-smooth hardware-accelerated playback of practically any video or audio format.

Rather than compromising with generic wrapper players, OniPlayer has been engineered natively from the ground up:
*   **OniPlayer Android:** Built natively in Kotlin, emphasizing elegant touch gestures (volume/brightness swipes, pinch-to-zoom, slow scrubbing overlay), gorgeous grid layouts, resume-playback memory, and strict edge-swipe protection.
*   **OniPlayer Desktop:** Built in Python using PyQt6, focusing on a fully keyboard-and-mouse-centric experience (including unique multi-key combinations and mouse scroll controls), distraction-free default fullscreen, auto-hiding OS cursor, and built-in standalone packaging.

---

## Repository Structure

This repository is organized as a multi-project monorepo containing both codebases in clean, isolated workspaces:

```
OniPlayer (Root)
├── OniPlayer Android      <- Kotlin Native App (Android 15+ Target API 36)
│   ├── app/                  <- Source code & layout assets (colors.xml, constraint layouts)
│   ├── gradle/               <- Build configuration
│   ├── build.gradle.kts      <- Root build script
│   ├── settings.gradle.kts   <- Project settings
│   ├── gradle.properties     <- Gradle properties
│   ├── gradlew / gradlew.bat <- Gradle wrapper scripts
│   ├── icon.png              <- Android application icon
│   ├── .gitignore            <- Android-specific Gradle & build ignore rules
│   └── README.md             <- Mobile-specific guides & instructions
│
├── OniPlayer Desktop      <- Python 3.10+ & PyQt6 App (Windows x64)
│   ├── plugins/              <- VLC plugins directory
│   ├── libvlc.dll            <- Core VLC engine library
│   ├── libvlccore.dll        <- Core VLC engine library
│   ├── icon.ico              <- Desktop application icon
│   ├── main.py               <- Desktop controller, GUI thread & VLC bindings
│   ├── setup.iss             <- Inno Setup script for executable installer
│   ├── file_version_info.txt <- Application version resource for PyInstaller
│   ├── requirements.txt      <- Desktop dependencies
│   ├── .gitignore            <- Desktop-specific Python, PyQt & PyInstaller ignore rules
│   └── README.md             <- Desktop-specific controls & shortcuts
│
├── .gitattributes            <- Line-ending normalization & binary integrity configs
├── .gitignore                <- Base global system & root workspace ignore rules
└── LICENSE                   <- MIT License
```

---

## Side-by-Side Comparison

| Feature | OniPlayer Android | OniPlayer Desktop |
| :--- | :--- | :--- |
| **Language & Platform** | Kotlin / Native Android 15+ (API 35/36) | Python 3.10+ / PyQt6 on Windows x64 |
| **Core Media Engine** | LibVLC for Android (`3.7.0`) | LibVLC Binding (`python-vlc`) |
| **User Interface** | Sleek Dark Mode (Sky-Blue & Netflix-Red Accent) | Minimalist Deep Dark, Fullscreen by Default |
| **Touch Swipes & Gestures**| Brightness, Volume, 2-Finger Zoom, Slow Scrubbing | Volume Wheel, Hold + Wheel Seek / Track Swap |
| **Keyboard Controls** | N/A | High-fidelity Hotkeys (Arrows, Space, PageUp/Dn, M, A, S) |
| **Subtitles** | SRT/ASS/SSA auto-detection, track BottomSheet | SRT/ASS auto-detection, sync delay shortcuts |
| **State Retention** | Resume watcher progress, Watched badge indicator | Playlists queue, automatic video auto-advance |
| **Distribution / Build** | Gradle APK (Android Studio Jellyfish+) | PyInstaller standalone EXE & Inno Setup Installer |

---

## OniPlayer Android

The mobile client delivers a beautiful library experience alongside an interactive, gesture-rich player interface.

### Highlights
*   **Library Browsing:** Group local videos instantly by immediate folder trees. Long-press to activate Batch Selection mode for secure deletion using elegant confirm dialogs.
*   **Intuitive Gesture Control:** Swipe up/down on the left side for brightness, on the right side for volume. Swipe horizontally for precise seek scrubbing with a clean overlay showing time differences (e.g., `+0:12` or `-1:05`).
*   **Screen Lock:** Long-press to lock screen controls, hiding all icons to prevent accidental navigation or touch inputs during playback.
*   **Thumbnail Optimization:** Leverages Glide v4 for rapid caching and display of local media thumbnails.

**Ready to build?** Follow the detailed setup instructions in the [OniPlayer Android README](OniPlayer%20Android/README.md).

---

## OniPlayer Desktop

The desktop client provides a powerful, distraction-free environment that hides all desktop clutter, allowing you to control everything seamlessly through your mouse and keyboard.

### Highlights
*   **Keyboard & Mouse-Centric Navigation:** Instantly swap audio tracks with `Hold Right-Click + Scroll`, rewind/forward with `Hold Left-Click + Scroll`, or skip files with combined clicks.
*   **Curator Control:** Double-click for Play/Pause, middle-click for Fullscreen, and hold middle-click to toggle subtitles.
*   **Cursor Management:** Auto-hides the mouse cursor over video, reappearing smoothly when hovering over control bars or menus. Features stuck-cursor prevention for a flawless Windows experience.
*   **Auto-Advance Playlists:** Drop a directory in and let it automatically advance sequentially through all candidate videos.

**Ready to run?** Follow the keyboard layout guides and build instructions in the [OniPlayer Desktop README](OniPlayer%20Desktop/README.md).

---

## Quick Setup Reference

### To Run the Desktop Version
Make sure you have Python 3.10+ installed on Windows.
```powershell
# Navigate into the desktop folder
cd "OniPlayer Desktop"

# Install requirements (PyQt6, python-vlc)
pip install -r requirements.txt

# Launch OniPlayer
python main.py
```

### To Build the Android Version
Open Android Studio, point it to the `OniPlayer Android` directory, let Gradle sync complete, and build the APK:
```bash
cd "OniPlayer Android"
./gradlew installDebug
```

---

## License & Attribution

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*   **VLC Core Engine:** LibVLC is distributed under the GNU Lesser General Public License (LGPL v2.1 or later).
*   **Glide (Android):** Licensed under the BSD, MIT, and Apache 2.0 licenses.
*   **PyQt6 (Desktop):** PyQt6 is licensed under the GPL v3 license or a commercial license.

---
